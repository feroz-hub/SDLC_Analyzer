import os
import platform
from pathlib import Path
import logging
from sentence_transformers import SentenceTransformer
import torch

logger = logging.getLogger(__name__)


# Model name mappings
MODEL_SHORT_NAMES = {
    "all-MiniLM-L6-v2": "minilm",
    "all-mpnet-base-v2": "mpnet",
    "distilbert-base-nli-mean-tokens": "distilbert"
    # Add more mappings as needed
}

MODEL_NAME_TO_REMOTE = {
    "all-MiniLM-L6-v2": "all-MiniLM-L6-v2",
    "all-mpnet-base-v2": "all-mpnet-base-v2",
    "distilbert-base-nli-mean-tokens": "distilbert-base-nli-mean-tokens"
    # Add more mappings as needed
}

class ModelLoader:
    """Utility class for loading and managing Sentence Transformer models."""
    _models = {}  # Cache for loaded models

    def __init__(self, model_name: str):
        self.model_name = model_name.strip().lower()
        self.short_name = self._get_short_name()
        self.device = self._select_device()
        self._model = None

    @staticmethod
    def _select_device() -> str:
        """Select the appropriate device (CUDA, MPS, or CPU)."""
        if torch.cuda.is_available():
            return 'cuda'
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return 'mps'
        return 'cpu'

    def _get_short_name(self) -> str:
        """Get the short name for the model."""
        #return MODEL_SHORT_NAMES.get(self.model_name, self.model_name.replace("/", "_").lower())
        # Case-insensitive lookup in MODEL_SHORT_NAMES
        model_name_lower = self.model_name.lower()
        for key in MODEL_SHORT_NAMES:
            if key.lower() == model_name_lower:
                return MODEL_SHORT_NAMES[key]
        # Fallback: sanitize model_name
        return self.model_name.replace("/", "_").lower()

    @staticmethod
    def _is_local_model_available(model_path: str) -> bool:
        """Check if the local model directory exists and contains required files."""
        if not os.path.exists(model_path):
            return False
        required_files = ["config.json"]
        return all(os.path.exists(os.path.join(model_path, f)) for f in required_files)

    def _get_model_identifier(self) -> str:
        """Determine whether to use local path or remote model name based on OS and availability."""
        # Construct local model path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        model_dir_path = os.path.join(current_dir, "models")
        model_path = os.path.join(model_dir_path, self.model_name)

        os_type = platform.system()
        remote_model_name = MODEL_NAME_TO_REMOTE.get(self.model_name, self.model_name)

        if os_type == "Darwin":  # macOS
            logger.info(f"Running on macOS, using remote model: {remote_model_name}")
            return remote_model_name
        elif os_type == "Windows":
            if self._is_local_model_available(model_path):
                logger.info(f"Local model found, using: {model_path}")
                return model_path
            else:
                logger.info(f"Local model not found at {model_path}, falling back to remote: {remote_model_name}")
                return remote_model_name
        else:  # Other OS (e.g., Linux)
            if self._is_local_model_available(model_path):
                logger.info(f"Local model found, using: {model_path}")
                return model_path
            else:
                logger.info(f"Local model not found at {model_path}, falling back to remote: {remote_model_name}")
                return remote_model_name

    @property
    def model(self) -> SentenceTransformer:
        """Load or retrieve the cached model."""
        if self.model_name not in self._models:
            try:
                model_identifier = self._get_model_identifier()
                logger.info(f"Loading model {model_identifier} on {self.device}")
                model = SentenceTransformer(model_identifier).to(self.device)
                self._models[self.model_name] = model
                logger.info(f"Model {model_identifier} loaded successfully on {self.device}")
            except Exception as e:
                logger.error(f"Error loading model {self.model_name}: {e}")
                raise
        return self._models[self.model_name]

    def cleanup(self):
        """Release the model and clear device cache."""
        if self.model_name in self._models:
            logger.info(f"Releasing model: {self.model_name}")
            del self._models[self.model_name]
            if self.device == 'cuda':
                torch.cuda.empty_cache()
            elif self.device == 'mps' and hasattr(torch.backends.mps, 'empty_cache'):
                torch.backends.mps.empty_cache()
            logger.debug(f"Cleanup completed for model: {self.model_name}")

    @classmethod
    def clear_all_models(cls):
        """Clear all cached models and device caches."""
        for model_name in list(cls._models.keys()):
            model = cls._models.pop(model_name)
            del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        elif hasattr(torch.backends.mps, 'empty_cache') and torch.backends.mps.is_available():
            torch.backends.mps.empty_cache()
        logger.debug("All models cleared from cache")