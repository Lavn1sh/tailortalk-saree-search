"""
Embeddings module for generating fashion visual and text representations
using FashionCLIP / CLIP.
"""

import os
import logging

# Suppress verbose transformers and Hugging Face Hub internal startup logs
os.environ["TRANSFORMERS_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import torch
import numpy as np
from PIL import Image
from typing import Union, List
import transformers
from transformers import CLIPProcessor, CLIPModel
from transformers.utils import logging as hf_logging

hf_logging.set_verbosity_error()
hf_logging.disable_progress_bar()
logging.getLogger("transformers").setLevel(logging.ERROR)

# Primary model: FashionCLIP (fine-tuned on 800k+ fashion items for fine-grained garment details)
DEFAULT_MODEL_NAME = "patrickjohncyh/fashion-clip"
FALLBACK_MODEL_NAME = "openai/clip-vit-base-patch32"

class FashionEmbeddingModel:
    _instance = None

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self._load_model()

    def _load_model(self):
        print(f"Loading visual embedding model: {self.model_name} on {self.device}...")
        try:
            # First attempt loading from local cache directly to avoid remote HF Hub HEAD requests
            self.processor = CLIPProcessor.from_pretrained(self.model_name, local_files_only=True)
            self.model = CLIPModel.from_pretrained(self.model_name, local_files_only=True).to(self.device)
        except Exception:
            try:
                self.processor = CLIPProcessor.from_pretrained(self.model_name)
                self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
            except Exception as e:
                print(f"Warning: Failed to load {self.model_name}: {e}. Falling back to {FALLBACK_MODEL_NAME}")
                self.model_name = FALLBACK_MODEL_NAME
                try:
                    self.processor = CLIPProcessor.from_pretrained(self.model_name, local_files_only=True)
                    self.model = CLIPModel.from_pretrained(self.model_name, local_files_only=True).to(self.device)
                except Exception:
                    self.processor = CLIPProcessor.from_pretrained(self.model_name)
                    self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)

        self.model.eval()
        print(f"Visual embedding model successfully initialized.")

    @classmethod
    def get_instance(cls, model_name: str = DEFAULT_MODEL_NAME):
        if cls._instance is None:
            cls._instance = cls(model_name)
        return cls._instance

    def _extract_tensor_features(self, output) -> torch.Tensor:
        """Extract tensor from CLIP output across transformers versions."""
        if isinstance(output, torch.Tensor):
            return output
        if hasattr(output, "image_embeds") and output.image_embeds is not None:
            return output.image_embeds
        if hasattr(output, "text_embeds") and output.text_embeds is not None:
            return output.text_embeds
        if hasattr(output, "pooler_output") and output.pooler_output is not None:
            return output.pooler_output
        if hasattr(output, "last_hidden_state") and output.last_hidden_state is not None:
            return output.last_hidden_state[:, 0]
        if isinstance(output, (tuple, list)):
            return output[0]
        raise ValueError(f"Unable to extract tensor features from {type(output)}")

    def encode_image(self, image: Image.Image) -> np.ndarray:
        """
        Encode a single PIL image into a normalized 512-dim embedding vector.
        """
        if image.mode != "RGB":
            image = image.convert("RGB")

        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.inference_mode():
            raw_features = self.model.get_image_features(**inputs)
            features = self._extract_tensor_features(raw_features)
            # L2 Normalize
            features = features / features.norm(p=2, dim=-1, keepdim=True)

        return features.cpu().numpy()[0].astype(np.float32)

    def encode_images_batch(self, images: List[Image.Image], batch_size: int = 32) -> np.ndarray:
        """
        Encode a batch of PIL images into normalized embedding vectors.
        """
        all_embeddings = []
        for i in range(0, len(images), batch_size):
            batch = images[i : i + batch_size]
            rgb_batch = [img.convert("RGB") if img.mode != "RGB" else img for img in batch]
            inputs = self.processor(images=rgb_batch, return_tensors="pt", padding=True).to(self.device)
            with torch.inference_mode():
                raw_features = self.model.get_image_features(**inputs)
                features = self._extract_tensor_features(raw_features)
                features = features / features.norm(p=2, dim=-1, keepdim=True)
            all_embeddings.append(features.cpu().numpy().astype(np.float32))

        return np.vstack(all_embeddings)

    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text query into normalized embedding vector.
        """
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.inference_mode():
            raw_features = self.model.get_text_features(**inputs)
            features = self._extract_tensor_features(raw_features)
            features = features / features.norm(p=2, dim=-1, keepdim=True)
        return features.cpu().numpy()[0].astype(np.float32)
