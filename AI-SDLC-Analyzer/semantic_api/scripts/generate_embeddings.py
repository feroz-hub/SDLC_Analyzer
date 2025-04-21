import os
import json
import numpy as np
import faiss
import pandas as pd
import re
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer
from scripts.config import EXCEL_FILE_PATH, MODELS_DIR,MODEL_PATH, MODEL_SHORT_NAMES

MODEL_NAME_MINILM = os.path.join(MODELS_DIR, "all-MiniLM-L6-v2")
MODEL_NAME_MPNET = os.path.join(MODELS_DIR, "all-mpnet-base-v2")
MODEL_DISTILBERT = os.path.join(MODELS_DIR, "distilbert-base-nli-mean-tokens")

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
    """Class responsible for handling embedding search."""

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


    # def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
    #     """Normalize embeddings for cosine similarity."""
    #     norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    #     norms[norms == 0] = 1  # Avoid division by zero
    #     return embeddings / norms

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

class EmbeddingPipeline:
    """Class that orchestrates the embedding generation and storage process."""
    def __init__(self, model_name: str, index_type: str = 'faiss'):
        self.text_processor = TextProcessor()
        self.model_manager = ModelManager(model_name)
        self.storage_handlers = {
            'json': JsonEmbeddingStorage(self.model_manager),
            'faiss': FaissEmbeddingStorage(self.model_manager),
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



if __name__ == "__main__":
    import sys
    model_path = MODEL_DISTILBERT
    if len(sys.argv) > 1:
        model_choice = sys.argv[1].lower()
        model_map = {
            'minilm': MODEL_NAME_MINILM,
            'mpnet': MODEL_NAME_MPNET,
            'distilbert': MODEL_DISTILBERT
        }
        model_path = model_map.get(model_choice, MODEL_DISTILBERT)

    index_types = ['faiss', 'json']
    try:
        # Run the pipeline once
        pipeline = EmbeddingPipeline(model_path)
        texts, embeddings = pipeline.run(output_formats=index_types)
        print(f"\n✅ Pipeline completed successfully for all index types. Generated {len(texts)} embeddings.")
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        sys.exit(1)