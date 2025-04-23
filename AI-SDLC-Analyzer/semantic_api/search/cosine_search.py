from sentence_transformers import util
from .basemodel import BaseSearchModel
from .embedding_loader import EmbeddingLoader
import torch
import os
import logging
from typing import List, Dict, Union
from utils import MODEL_SHORT_NAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CosineSimilarityModel(BaseSearchModel):
    def __init__(self, model_name: str, json_path: str):
        super().__init__(model_name)
        logger.info(
            f"Initialized CosineSimilarityModel with model_name: {self.model_name}, model_key: {self.model_key}")
        self.json_file = os.path.join(json_path, f'{self.model_key}_requirement_embeddings.json')
        logger.info(f"JSON file path: {self.json_file}")
        if not os.path.exists(self.json_file):
            logger.error(f"JSON file not found: {self.json_file}")
            raise FileNotFoundError(f"❌ JSON file not found: {self.json_file}")
        self.texts = None
        self.vectors = None

    def _load_embeddings(self):
        if self.texts is None or self.vectors is None:
            logger.info(f"Loading embeddings from {self.json_file}")
            self.texts, self.vectors = EmbeddingLoader.load_cosine_embeddings(self.json_file, self.device)
            logger.info(f"Loaded {len(self.texts)} texts and vectors")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Union[str, float]]]:
        if top_k <= 0:
            raise ValueError("❌ top_k must be positive")
        self._load_embeddings()
        if top_k > len(self.texts):
            top_k = len(self.texts)
        query_vec = self.encode(query)
        cos_scores = util.cos_sim(query_vec, self.vectors)[0]
        top_k_results = torch.topk(cos_scores, k=top_k)
        return [
            {"text": self.texts[i.item()], "score": cos_scores[i].item()}
            for i in top_k_results.indices
        ]


    def cleanup(self):
        logger.debug("Cleaning up Cosine model resources")
        try:
            super().cleanup()
            if self.vectors is not None:
                logger.info("Cleaning up vectors")
                del self.vectors
                self.vectors = None
            if self.texts is not None:
                logger.info("Cleaning up texts")
                self.texts = None
            # Force garbage collection
            import gc
            gc.collect()
        except Exception as e:
            logger.error(f"Failed to clean up Cosine model: {str(e)}")
        logger.debug("Cosine model cleanup completed")