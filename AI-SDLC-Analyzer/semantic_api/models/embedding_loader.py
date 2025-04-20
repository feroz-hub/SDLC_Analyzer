import os
import json
import torch
import faiss
from typing import Tuple, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class EmbeddingLoader:
    """Utility class to load embeddings, texts, and FAISS indexes from files."""

    @staticmethod
    def load_cosine_embeddings(json_file: str, device: str) -> Tuple[List[str], torch.Tensor]:
        """Load texts and vectors from a JSON file for cosine similarity model."""
        try:
            if not os.path.exists(json_file):
                raise FileNotFoundError(f"❌ Embedding file not found: {json_file}")
            with open(json_file, 'r') as f:
                data = json.load(f)

            if 'texts' not in data or 'vectors' not in data:
                raise ValueError("❌ JSON file missing 'texts' or 'vectors' keys")
            texts = data['texts']
            vectors = data['vectors']

            if not texts or not vectors:
                raise ValueError("❌ Empty texts or vectors in JSON file")
            if len(texts) != len(vectors):
                raise ValueError(f"❌ Mismatch between {len(texts)} texts and {len(vectors)} vectors")

            vectors = torch.tensor(vectors, dtype=torch.float32).to(device)
            logger.info(f"Loaded {len(texts)} texts and vectors from {json_file}")
            return texts, vectors
        except Exception as e:
            logger.error(f"Failed to load cosine embeddings: {str(e)}")
            raise

    @staticmethod
    def load_texts_txt(txt_file: str) -> List[str]:
        """Load texts from a TXT file (one text per line)."""
        try:
            if not os.path.exists(txt_file):
                raise FileNotFoundError(f"❌ Texts file not found: {txt_file}")
            with open(txt_file, 'r', encoding='utf-8') as f:
                texts = [line.strip() for line in f if line.strip()]
            if not texts:
                raise ValueError("❌ No valid texts found in TXT file")
            logger.info(f"Loaded {len(texts)} texts from {txt_file}")
            return texts
        except Exception as e:
            logger.error(f"Failed to load texts from TXT file: {str(e)}")
            raise

    @staticmethod
    def load_faiss_index(index_file: str) -> faiss.Index:
        """Load a FAISS index from a .index file."""
        try:
            if not os.path.exists(index_file):
                raise FileNotFoundError(f"❌ FAISS index file not found: {index_file}")
            index = faiss.read_index(index_file)
            if index is None or index.ntotal == 0:
                raise ValueError("❌ Invalid or empty FAISS index")
            logger.info(f"Loaded FAISS index with {index.ntotal} entries from {index_file}")
            return index
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            raise