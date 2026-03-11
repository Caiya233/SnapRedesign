import copy
import random
import threading
import time
import uuid
from io import BytesIO

import clip
import requests
import torch
from PIL import Image


class ComfyClient:
    _clip_bundle = None
    _clip_lock = threading.Lock()

    def __init__(self, config=None):
        config = config or {}
        self.server = config.get("comfy_url", "http://127.0.0.1:8000").rstrip("/")
        self.request_timeout = int(config.get("request_timeout", 60))
        self.poll_interval = float(config.get("poll_interval", 0.5))
        self.session = requests.Session()

        self.device, self.clip_model, self.clip_preprocess = self._get_clip_bundle()

    @classmethod
    def _get_clip_bundle(cls):
        if cls._clip_bundle is None:
            with cls._clip_lock:
                if cls._clip_bundle is None:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                    clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
                    clip_model.eval()
                    cls._clip_bundle = (device, clip_model, clip_preprocess)
        return cls._clip_bundle

    def close(self):
        self.session.close()

    def _request(self, method, path, **kwargs):
        url = f"{self.server}{path}"
        response = self.session.request(method, url, timeout=self.request_timeout, **kwargs)
        response.raise_for_status()
        return response

    # --------------------------------------------
    # Upload image to ComfyUI
    # --------------------------------------------

    def upload_image(self, image_path):
        with open(image_path, "rb") as image_file:
            files = {"image": image_file}
            data = {"type": "input"}
            response = self._request("post", "/upload/image", files=files, data=data)
        return response.json()["name"]

    # --------------------------------------------
    # Detect workflow nodes automatically
    # --------------------------------------------

    def detect_nodes(self, workflow):
        image_nodes = []
        positive_nodes = []
        negative_nodes = []

        for node_id, node in workflow.items():
            class_type = node.get("class_type", "")

            if class_type == "LoadImage":
                image_nodes.append(node_id)

            if class_type == "CLIPTextEncode":
                text = node.get("inputs", {}).get("text", "").lower()
                if "negative" in text:
                    negative_nodes.append(node_id)
                else:
                    positive_nodes.append(node_id)

        return image_nodes, positive_nodes, negative_nodes

    # --------------------------------------------
    # Inject prompt + image into workflow
    # --------------------------------------------

    def prepare_workflow(self, workflow, image_name, prompt_data):
        workflow = copy.deepcopy(workflow)

        positive = prompt_data["prompt"]
        negative = prompt_data["negative_prompt"]

        img_nodes, pos_nodes, neg_nodes = self.detect_nodes(workflow)

        for node_id in img_nodes:
            workflow[node_id]["inputs"]["image"] = image_name

        for node_id in pos_nodes:
            workflow[node_id]["inputs"]["text"] = positive

        for node_id in neg_nodes:
            workflow[node_id]["inputs"]["text"] = negative

        return workflow

    # --------------------------------------------
    # Inject sampler settings (denoise / seed)
    # --------------------------------------------

    def apply_sampler_settings(self, workflow, denoise, seed_lock, seed_offset=0):
        for node in workflow.values():
            if node.get("class_type") != "KSampler":
                continue

            inputs = node.setdefault("inputs", {})
            inputs["denoise"] = denoise

            base_seed = int(inputs.get("seed", 0))
            if seed_lock:
                inputs["seed"] = base_seed + seed_offset
            else:
                inputs["seed"] = random.randint(1, 2**32 - 1)

        return workflow

    # --------------------------------------------
    # Queue workflow
    # --------------------------------------------

    def queue_prompt(self, workflow):
        client_id = str(uuid.uuid4())
        payload = {
            "prompt": workflow,
            "client_id": client_id,
        }
        response = self._request("post", "/prompt", json=payload)
        return response.json()["prompt_id"]

    # --------------------------------------------
    # Wait for generation to complete
    # --------------------------------------------

    def _extract_output_images(self, history_entry):
        outputs = history_entry.get("outputs", {})
        for node in outputs.values():
            images = node.get("images")
            if images:
                return images
        return []

    def wait_for_completions(self, prompt_ids):
        pending = list(prompt_ids)
        completed = {}

        while pending:
            for prompt_id in pending[:]:
                response = self._request("get", f"/history/{prompt_id}")
                history = response.json()

                if prompt_id not in history:
                    continue

                images = self._extract_output_images(history[prompt_id])
                if not images:
                    continue

                completed[prompt_id] = images
                pending.remove(prompt_id)

            if pending:
                time.sleep(self.poll_interval)

        return [completed[prompt_id] for prompt_id in prompt_ids]

    # --------------------------------------------
    # Download image
    # --------------------------------------------

    def download_image(self, image_info):
        params = {
            "filename": image_info["filename"],
            "subfolder": image_info["subfolder"],
            "type": image_info["type"],
        }
        response = self._request("get", "/view", params=params)
        return Image.open(BytesIO(response.content)).convert("RGB")

    # --------------------------------------------
    # CLIP similarity scoring
    # --------------------------------------------

    def encode_clip_image(self, image):
        clip_ready = self.clip_preprocess(image.convert("RGB")).unsqueeze(0).to(self.device)

        with torch.no_grad():
            features = self.clip_model.encode_image(clip_ready)
            features /= features.norm(dim=-1, keepdim=True)

        return features

    def encode_clip_path(self, image_path):
        with Image.open(image_path) as image:
            return self.encode_clip_image(image)

    def compute_clip_similarity(self, original_features, generated_image):
        generated_features = self.encode_clip_image(generated_image)
        return (original_features @ generated_features.T).item()

    # --------------------------------------------
    # Run workflow (Modified for Batch Generation)
    # --------------------------------------------

    def run_workflow(self, workflow, input_image, prompt, denoise=0.5, seed_lock=False, batch_size=4):
        print("Uploading input image...")
        image_name = self.upload_image(input_image)

        prompt_ids = []
        for index in range(batch_size):
            print(f"Queueing task {index + 1}/{batch_size}...")

            task_workflow = self.prepare_workflow(workflow, image_name, prompt)
            task_workflow = self.apply_sampler_settings(
                task_workflow,
                denoise,
                seed_lock,
                seed_offset=index,
            )
            prompt_ids.append(self.queue_prompt(task_workflow))

        print("Waiting for results...")
        original_features = self.encode_clip_path(input_image)
        results = []

        for outputs in self.wait_for_completions(prompt_ids):
            if not outputs:
                continue

            image = self.download_image(outputs[0])
            score = self.compute_clip_similarity(original_features, image)
            print(f"Identity similarity: {round(score, 3)}")
            results.append(
                {
                    "image": image,
                    "score": score,
                }
            )

        return results
