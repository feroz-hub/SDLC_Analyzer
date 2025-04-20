# from sentence_transformers import SentenceTransformer
# import numpy as np
# import faiss
# import os
# import torch
# from .basemodel import BaseSearchModel
# from .utils import get_model_key
#
#
#
# class FaissSearchModel(BaseSearchModel):
#     def __init__(self, model_name: str, index_dir: str):
#         self.model_name = model_name
#         self.model = SentenceTransformer(model_name).to('cuda' if torch.cuda.is_available() else 'cpu')
#
#         # Create filename based on model_name
#         name_key = get_model_key(model_name)
#         # Load FAISS index and associated texts
#         index_file = os.path.join(index_dir, f"{name_key}_faiss_index.index")
#         self.index = faiss.read_index(index_file)
#
#         texts_path = os.path.join(index_dir, f"{name_key}_texts.txt")
#         with open(texts_path, 'r') as f:
#             self.texts = f.read().splitlines()
#
#     def encode(self, text: str):
#         vec = self.model.encode(text)
#         return np.array([vec]).astype("float32")
#
#     def search(self, query: str, top_k: int = 3):
#         vec = self.encode(query)
#         D, I = self.index.search(vec, top_k)
#
#         return [
#             {"text": self.texts[i], "score": round(float(D[0][k]), 4)}
#             for k, i in enumerate(I[0])
#         ]
#

# import numpy as np
# import faiss
# import os
# from .basemodel import BaseSearchModel
# from .embedding_loader import EmbeddingLoader
# import logging
# from typing import List, Dict, Union
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# class FaissSearchModel(BaseSearchModel):
#     def __init__(self, model_name: str, index_dir: str):
#         super().__init__(model_name)
#         self.index_file = os.path.join(index_dir, f"{self.model_key}_faiss_index.index")
#         self.texts_file = os.path.join(index_dir, f"{self.model_key}_texts.json")
#         self.index = None
#         self.texts = None
#
#     def _load_index(self):
#         if self.index is None or self.texts is None:
#             logger.info(f"Loading FAISS index from {self.index_file} and texts from {self.texts_file}")
#             self.index, self.texts = EmbeddingLoader.load_faiss_index(self.index_file, self.texts_file)
#             logger.info(f"Loaded FAISS index and {len(self.texts)} texts")
#
#     def encode(self, text: str | List[str]) -> np.ndarray:
#         tensor = super().encode(text)
#         return tensor.cpu().numpy().astype("float32")
#
#     def search(self, query: str, top_k: int = 3) -> List[Dict[str, Union[str, float]]]:
#         if top_k <= 0:
#             raise ValueError("❌ top_k must be positive")
#         self._load_index()
#         if top_k > len(self.texts):
#             top_k = len(self.texts)
#         vec = self.encode(query)
#         D, I = self.index.search(vec, top_k)
#         max_dist = max(D[0]) if D[0].size > 0 else 1.0
#         return [
#             {"text": self.texts[i], "score": 1.0 - (float(D[0][k]) / max_dist) if max_dist > 0 else 0.0}
#             for k, i in enumerate(I[0])
#         ]

#
# import numpy as np
# import faiss
# import os
# from .basemodel import BaseSearchModel
# from .embedding_loader import EmbeddingLoader
# import logging
# from typing import List, Dict, Union
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# class FaissSearchModel(BaseSearchModel):
#     """FAISS-based search model for semantic search."""
#     def __init__(self, model_name: str, index_dir: str):
#         super().__init__(model_name)
#         self.index_file = os.path.join(index_dir, f"{self.model_key}_faiss_index.index")
#         self.texts_file = os.path.join(index_dir, f"{self.model_key}_texts.txt")
#         self.index = None
#         self.texts = None
#         #self._load_index()
#
#     def _load_index(self):
#         """Load FAISS index and texts from files."""
#         try:
#             if not os.path.exists(self.index_file):
#                 raise FileNotFoundError(f"❌ FAISS index file not found: {self.index_file}")
#             if not os.path.exists(self.texts_file):
#                 raise FileNotFoundError(f"❌ Texts file not found: {self.texts_file}")
#
#             # Load FAISS index (CPU-based)
#             self.index = faiss.read_index(self.index_file)
#
#             # Load texts from .txt file
#             self.texts = EmbeddingLoader.load_texts_txt(self.texts_file)
#
#             if not self.texts:
#                 raise ValueError("❌ No texts loaded from file")
#             if self.index.ntotal != len(self.texts):
#                 raise ValueError(f"❌ Mismatch between {self.index.ntotal} index entries and {len(self.texts)} texts")
#
#             logger.info(
#                 f"Loaded FAISS index with {self.index.ntotal} entries and {len(self.texts)} texts from {self.index_file}")
#         except Exception as e:
#             logger.error(f"Failed to load FAISS index or texts: {str(e)}")
#             raise
#
#     def encode(self, text: str | List[str]) -> np.ndarray:
#         tensor = super().encode(text)
#         return tensor.cpu().numpy().astype("float32")
#     # def encode(self, text: str | List[str]) -> np.ndarray:
#     #     """Encode text(s) into embeddings."""
#     #     try:
#     #         tensor = super().encode(text)
#     #         return tensor.cpu().numpy().astype("float32")
#     #     except Exception as e:
#     #         logger.error(f"Failed to encode text: {str(e)}")
#     #         raise
#
#     def search(self, query: str, top_k: int = 3) -> List[Dict[str, Union[str, float]]]:
#         """Perform similarity search using FAISS."""
#         if top_k <= 0:
#             raise ValueError("❌ top_k must be positive")
#         self._load_index()  # Ensure index is loaded (supports lazy loading)
#         if top_k > len(self.texts):
#             top_k = len(self.texts)
#
#         try:
#             vec = self.encode(query)
#             D, I = self.index.search(vec, top_k)
#             max_dist = max(D[0]) if D[0].size > 0 else 1.0
#             results = [
#                 {"text": self.texts[i], "score":float(round(1.0 - (float(D[0][k]) / max_dist),4))  if max_dist > 0 else 0.0}
#                 for k, i in enumerate(I[0]) if i < len(self.texts)
#             ]
#             logger.info(f"Search completed for query: {query}, top_k: {top_k}, results: {len(results)}")
#             return results
#         except Exception as e:
#             logger.error(f"Search failed: {str(e)}")
#             raise
#
#     def cleanup(self):
#         """Clean up model, index, and texts."""
#         super().cleanup()
#         if self.index is not None:
#             logger.info("Cleaning up FAISS index")
#             del self.index
#             self.index = None
#         if self.texts is not None:
#             logger.info("Cleaning up texts")
#             self.texts = None

import os
import faiss
import numpy as np
import torch
import logging
from typing import List, Dict, Union
from .basemodel import BaseSearchModel
from .embedding_loader import EmbeddingLoader

logger = logging.getLogger(__name__)


class FaissSearchModel(BaseSearchModel):
    """FAISS-based search model for semantic search.

    Attributes:
        model_name (str): Name of the SentenceTransformer model.
        index_file (str): Path to the FAISS index file.
        texts_file (str): Path to the texts file (.txt).
        index (faiss.Index): FAISS index for similarity search.
        texts (List[str]): List of texts corresponding to index vectors.
    """

    def __init__(self, model_name: str, index_dir: str):
        """Initialize the FAISS model with index and texts.

        Args:
            model_name (str): Name of the SentenceTransformer model (e.g., 'all-MiniLM-L6-v2').
            index_dir (str): Directory containing FAISS index and texts files.

        Raises:
            FileNotFoundError: If index or texts file is missing.
            ValueError: If texts are empty or mismatch with index.
        """
        super().__init__(model_name)
        self.index_file = os.path.join(index_dir, f"{self.model_key}_faiss_index.index")
        self.texts_file = os.path.join(index_dir, f"{self.model_key}_texts.txt")
        self.index = None
        self.texts = None
        self._load_index()

    def _load_index(self):
        """Load FAISS index and texts using EmbeddingLoader.

        Raises:
            FileNotFoundError: If index or texts file is missing.
            ValueError: If texts are empty or mismatch with index.
        """
        try:
            # Load FAISS index using EmbeddingLoader
            self.index = EmbeddingLoader.load_faiss_index(self.index_file)

            # Load texts using EmbeddingLoader
            self.texts = EmbeddingLoader.load_texts_txt(self.texts_file)

            if not self.texts:
                raise ValueError("No texts loaded from file")
            if self.index.ntotal != len(self.texts):
                raise ValueError(f"Mismatch between {self.index.ntotal} index entries and {len(self.texts)} texts")

            logger.info(f"Loaded FAISS index and {len(self.texts)} texts")
        except Exception as e:
            logger.error(f"Failed to load FAISS index or texts: {str(e)}")
            raise

    def encode(self, text: str | List[str]) -> np.ndarray:
        """Encode text(s) into embeddings.

        Args:
            text (str | List[str]): Text or list of texts to encode.

        Returns:
            np.ndarray: Encoded embeddings as NumPy array.

        Raises:
            RuntimeError: If encoding fails.
        """
        try:
            tensor = super().encode(text)
            return tensor.cpu().numpy().astype("float32")
        except Exception as e:
            logger.error(f"Failed to encode text: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Union[str, float]]]:
        """Perform similarity search using FAISS.

        Args:
            query (str): Query text to search for.
            top_k (int): Number of top results to return (default: 3).

        Returns:
            List[Dict[str, Union[str, float]]]: List of results with text and similarity score.

        Raises:
            ValueError: If top_k is invalid or index/texts are not loaded.
            RuntimeError: If search fails.
        """
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.index is None or self.texts is None:
            self._load_index()  # Lazy loading
        top_k = min(top_k, len(self.texts))  # Ensure top_k doesn't exceed available texts

        try:
            vec = self.encode(query)
            D, I = self.index.search(vec, top_k)
            max_dist = max(D[0]) if D[0].size > 0 else 1.0
            results = [
                {"text": self.texts[i], "score": float(round(1.0 - (float(D[0][k]) / max_dist), 4))}
                for k, i in enumerate(I[0]) if i < len(self.texts)
            ]
            logger.info(f"Search completed for query: {query}, top_k: {top_k}, results: {len(results)}")
            return results
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    def cleanup(self):
        """Clean up FAISS index, texts, and model resources."""
        logger.debug("Cleaning up FAISS model resources")
        try:
            super().cleanup()
            if self.index is not None:
                logger.info("Cleaning up FAISS index")
                del self.index
                self.index = None
            if self.texts is not None:
                logger.info("Cleaning up texts")
                self.texts = None
            # Force garbage collection
            import gc
            gc.collect()
        except Exception as e:
            logger.error(f"Failed to clean up FAISS model: {str(e)}")
        logger.debug("FAISS model cleanup completed")