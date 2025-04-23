import os
import faiss
import numpy as np
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