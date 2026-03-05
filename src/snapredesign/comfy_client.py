import requests
import time
import uuid
import copy
from PIL import Image
from io import BytesIO

import torch
import clip
import random


class ComfyClient:

    def __init__(self, config=None):

        config = config or {}
        self.server = config.get("comfy_url", "http://127.0.0.1:8000")

        # CLIP setup
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)

    # --------------------------------------------
    # Upload image to ComfyUI
    # --------------------------------------------

    def upload_image(self, image_path):

        url = f"{self.server}/upload/image"

        with open(image_path, "rb") as f:

            files = {"image": f}
            data = {"type": "input"}

            r = requests.post(url, files=files, data=data)

        r.raise_for_status()

        return r.json()["name"]

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

                text = node["inputs"].get("text", "").lower()

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

    def apply_sampler_settings(self, workflow, denoise, seed_lock):

        for node_id, node in workflow.items():

            if node.get("class_type") == "KSampler":

                node["inputs"]["denoise"] = denoise

                if not seed_lock:
                    node["inputs"]["seed"] = random.randint(1, 2**32)

        return workflow

    # --------------------------------------------
    # Queue workflow
    # --------------------------------------------

    def queue_prompt(self, workflow):

        client_id = str(uuid.uuid4())

        payload = {
            "prompt": workflow,
            "client_id": client_id
        }

        r = requests.post(
            f"{self.server}/prompt",
            json=payload
        )

        r.raise_for_status()

        return r.json()["prompt_id"]

    # --------------------------------------------
    # Wait for generation to complete
    # --------------------------------------------

    def wait_for_completion(self, prompt_id):

        while True:

            r = requests.get(f"{self.server}/history/{prompt_id}")
            r.raise_for_status()

            history = r.json()

            if prompt_id in history:

                outputs = history[prompt_id]["outputs"]

                images = []

                for node in outputs.values():

                    if "images" in node:

                        for img in node["images"]:
                            images.append(img)

                if images:
                    return images

            time.sleep(1)

    # --------------------------------------------
    # Download image
    # --------------------------------------------

    def download_image(self, image_info):

        params = {
            "filename": image_info["filename"],
            "subfolder": image_info["subfolder"],
            "type": image_info["type"]
        }

        r = requests.get(
            f"{self.server}/view",
            params=params
        )

        r.raise_for_status()

        return Image.open(BytesIO(r.content))

    # --------------------------------------------
    # CLIP similarity scoring
    # --------------------------------------------

    def compute_clip_similarity(self, original_path, generated_image):

        original = self.clip_preprocess(Image.open(original_path)).unsqueeze(0).to(self.device)
        generated = self.clip_preprocess(generated_image).unsqueeze(0).to(self.device)

        with torch.no_grad():

            orig_features = self.clip_model.encode_image(original)
            gen_features = self.clip_model.encode_image(generated)

            orig_features /= orig_features.norm(dim=-1, keepdim=True)
            gen_features /= gen_features.norm(dim=-1, keepdim=True)

            similarity = (orig_features @ gen_features.T).item()

        return similarity

    # --------------------------------------------
    # Run workflow
    # --------------------------------------------

    def run_workflow(self, workflow, input_image, prompt, denoise=0.5, seed_lock=False):

        print("Uploading input image...")
        image_name = self.upload_image(input_image)

        print("Preparing workflow...")
        workflow = self.prepare_workflow(
            workflow,
            image_name,
            prompt
        )

        # Apply UI settings to sampler
        workflow = self.apply_sampler_settings(
            workflow,
            denoise,
            seed_lock
        )

        print("Queueing workflow...")
        prompt_id = self.queue_prompt(workflow)

        print("Prompt ID:", prompt_id)

        print("Waiting for results...")
        outputs = self.wait_for_completion(prompt_id)

        print("Downloading images...")

        results = []

        for img_info in outputs:

            img = self.download_image(img_info)

            score = self.compute_clip_similarity(input_image, img)

            print("Identity similarity:", round(score, 3))

            results.append({
                "image": img,
                "score": score
            })

        return results