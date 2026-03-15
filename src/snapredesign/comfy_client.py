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
        self.server = config.get("comfy_url", "http://127.0.0.1:8188")

        # CLIP setup
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.clip_model, self.clip_preprocess = clip.load("ViT-B/32", device=self.device)
        self.clip_model.eval()

    def upload_image(self, image_path):
        url = f"{self.server}/upload/image"

        with open(image_path, "rb") as f:
            files = {"image": f}
            data = {"type": "input"}
            r = requests.post(url, files=files, data=data)

        r.raise_for_status()
        return r.json()["name"]

    def _iter_ksamplers(self, workflow):
        for node in workflow.values():
            if node.get("class_type") == "KSampler":
                yield node


    def _node_ref_id(self, ref):
        if isinstance(ref, (list, tuple)) and ref:
            return str(ref[0])
        return None


    def _next_node_id(self, workflow):
        numeric_ids = [int(node_id) for node_id in workflow if str(node_id).isdigit()]
        return str(max(numeric_ids, default=0) + 1)


    def _resolve_clip_input(self, workflow, node_id, visited=None):
        if node_id is None:
            return None

        visited = visited or set()
        if node_id in visited:
            return None
        visited.add(node_id)

        node = workflow.get(node_id)
        if node is None:
            return None

        if node.get("class_type") == "CLIPTextEncode":
            return node["inputs"].get("clip")

        conditioning_ref = self._node_ref_id(node.get("inputs", {}).get("conditioning"))
        if conditioning_ref is not None:
            return self._resolve_clip_input(workflow, conditioning_ref, visited)

        return None


    def _set_positive_prompt(self, workflow, sampler, text):
        node_id = self._node_ref_id(sampler.get("inputs", {}).get("positive"))
        node = workflow.get(node_id) if node_id is not None else None
        if node is not None and node.get("class_type") == "CLIPTextEncode":
            node["inputs"]["text"] = text
            return True
        return False


    def _set_negative_prompt(self, workflow, sampler, text):
        node_id = self._node_ref_id(sampler.get("inputs", {}).get("negative"))
        node = workflow.get(node_id) if node_id is not None else None

        if node is not None and node.get("class_type") == "CLIPTextEncode":
            node["inputs"]["text"] = text
            return True

        clip_ref = self._resolve_clip_input(workflow, node_id)
        if clip_ref is None:
            return False

        new_node_id = self._next_node_id(workflow)
        workflow[new_node_id] = {
            "inputs": {
                "text": text,
                "clip": clip_ref,
            },
            "class_type": "CLIPTextEncode",
            "_meta": {
                "title": "CLIP Text Encode (Negative Prompt)"
            },
        }
        sampler["inputs"]["negative"] = [new_node_id, 0]
        return True


    def prepare_workflow(self, workflow, image_name, prompt_data):
        workflow = copy.deepcopy(workflow)

        positive = prompt_data["prompt"]
        negative = prompt_data["negative_prompt"]

        for node in workflow.values():
            if node.get("class_type") == "LoadImage":
                node["inputs"]["image"] = image_name

        positive_applied = False
        for sampler in self._iter_ksamplers(workflow):
            positive_applied = self._set_positive_prompt(workflow, sampler, positive) or positive_applied
            self._set_negative_prompt(workflow, sampler, negative)

        if not positive_applied:
            raise ValueError("Workflow is missing a CLIPTextEncode node connected to KSampler.positive.")

        return workflow

    def apply_sampler_settings(self, workflow, denoise, seed_lock):
        applied_seed = None

        for node_id, node in workflow.items():
            if node.get("class_type") == "KSampler":
                node["inputs"]["denoise"] = denoise

                if applied_seed is None:
                    existing_seed = node["inputs"].get("seed")
                    if seed_lock and existing_seed is not None:
                        applied_seed = int(existing_seed)
                    else:
                        applied_seed = random.randint(1, 2**32 - 1)

                node["inputs"]["seed"] = applied_seed

        return workflow, applied_seed

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
                        break

                if images:
                    return images

            time.sleep(1)

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
        return Image.open(BytesIO(r.content)).convert("RGB")

    def encode_image_features(self, image_or_path):
        if isinstance(image_or_path, str):
            image = Image.open(image_or_path).convert("RGB")
        else:
            image = image_or_path.convert("RGB")

        image_tensor = self.clip_preprocess(image).unsqueeze(0).to(self.device)

        with torch.inference_mode():
            features = self.clip_model.encode_image(image_tensor)
            features /= features.norm(dim=-1, keepdim=True)

        return features

    def compute_clip_similarity_from_features(self, original_features, generated_image):
        generated_tensor = self.clip_preprocess(
            generated_image.convert("RGB")
        ).unsqueeze(0).to(self.device)

        with torch.inference_mode():
            gen_features = self.clip_model.encode_image(generated_tensor)
            gen_features /= gen_features.norm(dim=-1, keepdim=True)
            similarity = (original_features @ gen_features.T).item()

        return similarity

    def run_workflow(self, workflow, input_image, prompt, denoise=0.5, seed_lock=False, batch_size=4):
        print("Uploading input image...")
        image_name = self.upload_image(input_image)

        prompt_jobs = []

        # Precompute original CLIP features once
        original_features = self.encode_image_features(input_image)

        # batch processing
        for i in range(batch_size):
            print(f"Queueing task {i+1}/{batch_size}...")

            task_workflow = self.prepare_workflow(
                workflow,
                image_name,
                prompt
            )

            task_workflow, task_seed = self.apply_sampler_settings(
                task_workflow,
                denoise,
                seed_lock
            )

            prompt_id = self.queue_prompt(task_workflow)
            prompt_jobs.append({
                "prompt_id": prompt_id,
                "seed": task_seed,
            })

        print("Waiting for results...")
        results = []

        for job in prompt_jobs:
            outputs = self.wait_for_completion(job["prompt_id"])

            for img_info in outputs:
                img = self.download_image(img_info)
                score = self.compute_clip_similarity_from_features(original_features, img)
                print(f"Identity similarity: {round(score, 3)}")

                results.append({
                    "image": img,
                    "score": score,
                    "seed": job["seed"],
                    "prompt_id": job["prompt_id"],
                })
                break

        return results
