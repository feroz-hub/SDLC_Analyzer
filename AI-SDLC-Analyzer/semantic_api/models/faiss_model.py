from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import torch
from .basemodel import BaseSearchModel


def _get_model_key(model_name):
    # Normalize model key from common models
    if "minilm" in model_name.lower():
        return "minilm"
    elif "mpnet" in model_name.lower():
        return "mpnet"
    else:
        return model_name.replace("/", "_").lower()  # fallback, safer for filenames


class FaissSearchModel(BaseSearchModel):
    def __init__(self, model_name: str, index_dir: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name).to('cuda' if torch.cuda.is_available() else 'cpu')

        # Create filename based on model_name
        name_key = _get_model_key(model_name)
        # Load FAISS index and associated texts
        index_file = os.path.join(index_dir, f"{name_key}_faiss_index.index")
        self.index = faiss.read_index(index_file)

        texts_path = os.path.join(index_dir, f"{name_key}_texts.txt")
        with open(texts_path, 'r') as f:
            self.texts = f.read().splitlines()

    def encode(self, text: str):
        vec = self.model.encode(text)
        return np.array([vec]).astype("float32")

    def search(self, query: str, top_k: int = 3):
        vec = self.encode(query)
        D, I = self.index.search(vec, top_k)

        return [
            {"text": self.texts[i], "score": round(float(D[0][k]), 4)}
            for k, i in enumerate(I[0])
        ]
