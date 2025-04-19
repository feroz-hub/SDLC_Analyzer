from sentence_transformers import SentenceTransformer, util
import torch
import os
import json
from .basemodel import BaseSearchModel


def _get_model_key(model_name):
    # Normalize model key from common models
    if "minilm" in model_name.lower():
        return "minilm"
    elif "mpnet" in model_name.lower():
        return "mpnet"
    else:
        return model_name.replace("/", "_").lower()  # fallback, safer for filenames


class CosineSimilarityModel(BaseSearchModel):
    def __init__(self, model_name: str, json_path: str):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name).to('cuda' if torch.cuda.is_available() else 'cpu')

        # Create filename based on model_name
        name_key = _get_model_key(model_name)
        json_file = os.path.join(json_path, f'{name_key}_requirement_embeddings.json')

        if not os.path.exists(json_file):
            raise FileNotFoundError(f"❌ Embedding file not found: {json_file}")

        with open(json_file, 'r') as f:
            data = json.load(f)

        self.texts = data['texts']
        self.vectors = torch.tensor(data['vectors'])

    def encode(self, text: str):
        return self.model.encode(text, convert_to_tensor=True)

    def search(self, query: str, top_k: int = 3):
        query_vec = self.encode(query)
        cos_scores = util.cos_sim(query_vec, self.vectors)[0]
        top_k_results = torch.topk(cos_scores, k=top_k)

        return [
            {"text": self.texts[i.item()], "score": round(cos_scores[i].item(), 4)}
            for i in top_k_results.indices
        ]
