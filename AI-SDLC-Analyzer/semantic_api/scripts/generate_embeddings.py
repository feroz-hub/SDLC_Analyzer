# import os
# import json
# import numpy as np
# import faiss
# import pandas as pd
# import re
# from sentence_transformers import SentenceTransformer
# from scripts.config import EXCEL_FILE_PATH, MODEL_PATH, MODEL_NAME_MINILM,MODEL_NAME_MPNET, MODEL_SHORT_NAMES, MODEL_NAME_T5
#
#
#
#
#
# # === HELPER FUNCTIONS === #
# def load_model(name):
#     return SentenceTransformer(name)
#
# def clean_text(text):
#
#     return re.sub(r'\s+', ' ', text.strip())
#
#
# def get_texts(excel_path, sheet_name='Unique_Requirements', usecols='C'):
#     df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet_name, skiprows=1, usecols=usecols)
#     return df['Requirement Index'].dropna().tolist()
#
#
# def generate_json_embeddings(model_name):
#     print(f"🔄 Generating JSON Embeddings using {model_name}...")
#     model = load_model(model_name)
#     raw_text = get_texts(EXCEL_FILE_PATH)
#     texts = [clean_text(text) for text in raw_text]
#     embeddings = model.encode(texts)
#
#     short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
#     filename = f"{short_name}_requirement_embeddings.json"
#     # Define the output directory structure
#     output_dir = os.path.join(MODEL_PATH, short_name, "cosine")
#     vec_dir = os.path.normpath(output_dir)
#     os.makedirs(output_dir, exist_ok=True)
#
#     json_path = os.path.join(vec_dir, filename)
#
#     with open(json_path, 'w') as f:
#         json.dump({"texts": texts, "vectors": embeddings.tolist()}, f, indent=4)
#
#     print(f"✅ {filename} saved at {json_path}")
#
# def generate_faiss_index(model_name):
#     print(f"🔄 Generating FAISS Index using {model_name}...")
#     short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
#
#     model = load_model(model_name)
#     raw_text = get_texts(EXCEL_FILE_PATH)
#     texts = [clean_text(text) for text in raw_text]
#     embeddings = model.encode(texts, convert_to_numpy=True)
#     short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
#     output_dir = os.path.join(MODEL_PATH, short_name, "faiss")
#     vec_dir = os.path.normpath(output_dir)
#
#     os.makedirs(output_dir, exist_ok=True)
#     np.save(os.path.join(vec_dir, f'{short_name}_embeddings.npy'), embeddings)
#
#     with open(os.path.join(vec_dir, f'{short_name}_texts.txt'), 'w') as f:
#         for line in texts:
#             f.write(line + "\n")
#
#     dimension = embeddings.shape[1]
#     index = faiss.IndexFlatL2(dimension)
#     index.add(embeddings)
#
#     faiss.write_index(index, os.path.join(vec_dir, f'{short_name}_faiss_index.index'))
#     print("✅ FAISS index and files saved successfully.")
#
# # === MAIN RUN === #
# if __name__ == "__main__":
#     generate_json_embeddings(MODEL_NAME_MPNET)
#     generate_faiss_index(MODEL_NAME_MPNET)

#

import os
import json

import hnswlib
import numpy as np
import faiss
import pandas as pd
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple, Optional

from annoy import AnnoyIndex
from sentence_transformers import SentenceTransformer
from scripts.config import EXCEL_FILE_PATH, MODEL_PATH, MODEL_NAME_MINILM, MODEL_NAME_MPNET, MODEL_SHORT_NAMES,MODEL_DISTILBERT,MODEL_NAME_T5


class TextProcessor:
    """Class responsible for loading and processing text data."""

    def __init__(self, excel_path: str = EXCEL_FILE_PATH):
        self.excel_path = excel_path

    def get_raw_texts(self, sheet_name: str = 'Unique_Requirements', usecols: str = 'C') -> List[str]:
        """Extract texts from Excel file."""
        try:
            df = pd.read_excel(self.excel_path, sheet_name=sheet_name, skiprows=1, usecols=usecols)
            return df['Requirement Index'].dropna().tolist()
        except Exception as e:
            print(f"Error reading Excel file {self.excel_path}: {e}")
            raise

    def clean_texts(self, texts: List[str]) -> List[str]:
        """Clean and normalize a list of texts."""
        return [self._clean_text(text) for text in texts]

    @staticmethod
    def _clean_text(text: str) -> str:
        """Clean and normalize text by removing extra whitespace."""
        return re.sub(r'\s+', ' ', text.strip())

    def get_processed_texts(self) -> List[str]:
        """Get raw texts and clean them in one step."""
        raw_texts = self.get_raw_texts()
        return self.clean_texts(raw_texts)


class ModelManager:
    """Class responsible for handling embedding models."""

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.short_name = self._get_short_name()
        self._model = None

    def _get_short_name(self) -> str:
        """Get consistent short name for a model."""
        return MODEL_SHORT_NAMES.get(self.model_name, self.model_name.split("/")[-1].lower())

    @property
    def model(self):
        """Lazy-load the model only when needed."""
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
                print(f"Model {self.model_name} loaded successfully.")
            except Exception as e:
                print(f"Error loading model {self.model_name}: {e}")
                raise
        return self._model

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts using the model."""
        print(f"🔄 Generating embeddings using {self.model_name}...")
        return self.model.encode(texts, convert_to_numpy=True)


class EmbeddingStorage(ABC):
    """Abstract base class for embedding storage implementations."""

    def __init__(self, model_manager: ModelManager, base_path: str = MODEL_PATH):
        self.model_manager = model_manager
        self.base_path = base_path

    def get_output_directory(self, subdir: str) -> str:
        """Create and return the appropriate output directory."""
        output_dir = os.path.join(self.base_path, self.model_manager.short_name, subdir)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir


    def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Normalize embeddings for cosine similarity."""
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        return embeddings / norms

    @abstractmethod
    def save(self, texts: List[str], embeddings: np.ndarray) -> None:
        """Save embeddings in a specific format."""
        pass


class JsonEmbeddingStorage(EmbeddingStorage):
    """Class for storing embeddings in JSON format."""

    def save(self, texts: List[str], embeddings: np.ndarray) -> None:
        """Save embeddings in JSON format."""
        output_dir = self.get_output_directory("cosine")
        filename = f"{self.model_manager.short_name}_requirement_embeddings.json"
        json_path = os.path.join(output_dir, filename)

        try:
            with open(json_path, 'w') as f:
                json.dump({"texts": texts, "vectors": embeddings.tolist()}, f, indent=4)
            print(f"✅ {filename} saved at {json_path}")
        except Exception as e:
            print(f"Error saving JSON embeddings: {e}")


class FaissEmbeddingStorage(EmbeddingStorage):
    """Class for storing embeddings in FAISS format."""

    def save(self, texts: List[str], embeddings: np.ndarray) -> None:
        """Save texts and embeddings as FAISS index."""
        output_dir = self.get_output_directory("faiss")
        short_name = self.model_manager.short_name

        try:
            # Save numpy embeddings
            np.save(os.path.join(output_dir, f'{short_name}_embeddings.npy'), embeddings)

            # Save texts
            with open(os.path.join(output_dir, f'{short_name}_texts.txt'), 'w') as f:
                for line in texts:
                    f.write(line + "\n")

            # Create and save FAISS index
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            faiss.write_index(index, os.path.join(output_dir, f'{short_name}_faiss_index.index'))

            print(f"✅ FAISS index and files saved successfully at {output_dir}")
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
#
# class HNSWEmbeddingStorage(EmbeddingStorage):
#     """Class for storing embeddings in HNSW format."""
#     def save(self, texts: List[str], embeddings: np.ndarray) -> None:
#         output_dir = self.get_output_directory("hnsw")
#         short_name = self.model_manager.short_name
#         try:
#             embeddings = self.normalize_embeddings(embeddings)  # Normalize for cosine
#             np.save(os.path.join(output_dir, f'{short_name}_embeddings.npy'), embeddings)
#             with open(os.path.join(output_dir, f'{short_name}_texts.txt'), 'w') as f:
#                 for line in texts:
#                     f.write(line + "\n")
#             dimension = embeddings.shape[1]
#             index = hnswlib.Index(space='cosine', dim=dimension)
#             index.init_index(max_elements=len(embeddings), ef_construction=200, M=16)
#             index.add_items(embeddings, np.arange(len(embeddings)))
#             index.save_index(os.path.join(output_dir, f'{short_name}_hnsw_index.bin'))
#             print(f"✅ HNSW index and files saved successfully at {output_dir}")
#         except Exception as e:
#             print(f"Error saving HNSW index: {e}")
#             raise
#
# class AnnoyEmbeddingStorage(EmbeddingStorage):
#     """Class for storing embeddings in Annoy format."""
#     def save(self, texts: List[str], embeddings: np.ndarray) -> None:
#         output_dir = self.get_output_directory("annoy")
#         short_name = self.model_manager.short_name
#         try:
#             embeddings = self.normalize_embeddings(embeddings)  # Normalize for cosine
#             np.save(os.path.join(output_dir, f'{short_name}_embeddings.npy'), embeddings)
#             with open(os.path.join(output_dir, f'{short_name}_texts.txt'), 'w') as f:
#                 for line in texts:
#                     f.write(line + "\n")
#             dimension = embeddings.shape[1]
#             index = AnnoyIndex(dimension, 'dot')  # Use dot for cosine similarity
#             for i, emb in enumerate(embeddings):
#                 index.add_item(i, emb)
#             index.build(10)  # 10 trees
#             index.save(os.path.join(output_dir, f'{short_name}_annoy_index.ann'))
#             print(f"✅ Annoy index and files saved successfully at {output_dir}")
#         except Exception as e:
#             print(f"Error saving Annoy index: {e}")
#             raise
#


# class EmbeddingPipeline:
#     """Class that orchestrates the embedding generation and storage process."""
#
#     def __init__(self, model_name: str):
#         self.text_processor = TextProcessor()
#         self.model_manager = ModelManager(model_name)
#         self.storage_handlers = {
#             'json': JsonEmbeddingStorage(self.model_manager),
#             'faiss': FaissEmbeddingStorage(self.model_manager),
#             'hnsw': HNSWEmbeddingStorage(self.model_manager),
#             'annoy': AnnoyEmbeddingStorage(self.model_manager)
#         }
#
#     def run(self, output_formats: Optional[List[str]] = None) -> Tuple[List[str], np.ndarray]:
#         """
#         Run the pipeline to generate and save embeddings.
#
#         Args:
#             output_formats: List of formats to output. Options: ['json', 'faiss']
#
#         Returns:
#             Tuple of (texts, embeddings)
#         """
#         if output_formats is None:
#             output_formats = ['json', 'faiss']
#
#         # Process texts
#         texts = self.text_processor.get_processed_texts()
#
#         # Generate embeddings
#         embeddings = self.model_manager.generate_embeddings(texts)
#
#         # Save in requested formats
#         for format_name in output_formats:
#             if format_name in self.storage_handlers:
#                 self.storage_handlers[format_name].save(texts, embeddings)
#             else:
#                 print(f"Warning: Unsupported format '{format_name}' requested.")
#
#         return texts, embeddings
class EmbeddingPipeline:
    """Class that orchestrates the embedding generation and storage process."""
    def __init__(self, model_name: str, index_type: str = 'faiss'):
        self.text_processor = TextProcessor()
        self.model_manager = ModelManager(model_name)
        self.storage_handlers = {
            'json': JsonEmbeddingStorage(self.model_manager),
            'faiss': FaissEmbeddingStorage(self.model_manager),
            # 'hnsw': HNSWEmbeddingStorage(self.model_manager),
            # 'annoy': AnnoyEmbeddingStorage(self.model_manager)
        }
        self.index_type = index_type

    def run(self, output_formats: Optional[List[str]] = None) -> Tuple[List[str], np.ndarray]:
        if output_formats is None:
            output_formats = ['json', self.index_type]
        texts = self.text_processor.get_processed_texts()
        embeddings = self.model_manager.generate_embeddings(texts)
        for format_name in output_formats:
            try:
                if format_name in self.storage_handlers:
                    self.storage_handlers[format_name].save(texts, embeddings)
                else:
                    print(f"Warning: Unsupported format '{format_name}' requested.")
            except Exception as e:
                print(f"Error processing format '{format_name}': {e}")
        return texts, embeddings


# === USAGE EXAMPLE === ## === MAIN EXECUTION === #
# === USAGE EXAMPLE === #
if __name__ == "__main__":
    # Create and run the pipeline with default settings
    pipeline = EmbeddingPipeline(MODEL_DISTILBERT)
    texts, embeddings = pipeline.run()