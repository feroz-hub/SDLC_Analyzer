# from sentence_transformers import SentenceTransformer, util
# import torch
# import os
# import json
# from .basemodel import BaseSearchModel
# from .utils import get_model_key
#
#
#
#
# class CosineSimilarityModel(BaseSearchModel):
#     def __init__(self, model_name: str, json_path: str):
#         self.model_name = model_name
#         self.model = SentenceTransformer(model_name).to('cuda' if torch.cuda.is_available() else 'cpu')
#
#         # Create filename based on model_name
#         name_key = get_model_key(model_name)
#         json_file = os.path.join(json_path, f'{name_key}_requirement_embeddings.json')
#
#         if not os.path.exists(json_file):
#             raise FileNotFoundError(f"❌ Embedding file not found: {json_file}")
#
#         with open(json_file, 'r') as f:
#             data = json.load(f)
#
#         self.texts = data['texts']
#         self.vectors = torch.tensor(data['vectors'])
#
#     def encode(self, text: str):
#         return self.model.encode(text, convert_to_tensor=True)
#
#     def search(self, query: str, top_k: int = 3):
#         query_vec = self.encode(query)
#         cos_scores = util.cos_sim(query_vec, self.vectors)[0]
#         top_k_results = torch.topk(cos_scores, k=top_k)
#
#         return [
#             {"text": self.texts[i.item()], "score": round(cos_scores[i].item(), 4)}
#             for i in top_k_results.indices
#         ]


# from sentence_transformers import util
# from .basemodel import BaseSearchModel
# from .embedding_loader import EmbeddingLoader
# import torch
# import os
# import logging
# from typing import List, Dict, Union
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# class CosineSimilarityModel(BaseSearchModel):
#     def __init__(self, model_name: str, json_path: str):
#         super().__init__(model_name)
#         self.json_file = os.path.join(json_path, f'{self.model_key}_requirement_embeddings.json')
#         self.texts = None
#         self.vectors = None
#
#     def _load_embeddings(self):
#         if self.texts is None or self.vectors is None:
#             logger.info(f"Loading embeddings from {self.json_file}")
#             self.texts, self.vectors = EmbeddingLoader.load_cosine_embeddings(self.json_file, self.device)
#             logger.info(f"Loaded {len(self.texts)} texts and vectors")
#
#     def search(self, query: str, top_k: int = 3) -> List[Dict[str, Union[str, float]]]:
#         if top_k <= 0:
#             raise ValueError("❌ top_k must be positive")
#         self._load_embeddings()
#         if top_k > len(self.texts):
#             top_k = len(self.texts)
#         query_vec = self.encode(query)
#         cos_scores = util.cos_sim(query_vec, self.vectors)[0]
#         top_k_results = torch.topk(cos_scores, k=top_k)
#         return [
#             {"text": self.texts[i.item()], "score": cos_scores[i].item()}
#             for i in top_k_results.indices
#         ]

from sentence_transformers import util
from .basemodel import BaseSearchModel
from .embedding_loader import EmbeddingLoader
import torch
import os
import logging
from typing import List, Dict, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CosineSimilarityModel(BaseSearchModel):
    def __init__(self, model_name: str, json_path: str):
        super().__init__(model_name)
        self.json_file = os.path.join(json_path, f'{self.model_key}_requirement_embeddings.json')
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