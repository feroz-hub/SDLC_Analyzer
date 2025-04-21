from sentence_transformers import SentenceTransformer
import torch
from abc import ABC, abstractmethod
from typing import List, Dict, Union
from .utils import get_model_key, get_local_model_path
import logging
import gc
logger = logging.getLogger(__name__)


def _select_device() -> str:
    if torch.cuda.is_available():
        return 'cuda'
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return 'mps'
    return 'cpu'


class BaseSearchModel(ABC):
    def __init__(self, model_name: str, clear_cuda_cache: bool = True):
        self.model_name = model_name
        self.model_key = get_model_key(model_name)
        self.clear_cuda_cache = clear_cuda_cache
        self.device = _select_device()
        try:
            logger.info(f"Loading SentenceTransformer model: {model_name} on {self.device}")
            model_path_or_name = get_local_model_path(model_name)
            self.model = SentenceTransformer(model_path_or_name).to(self.device)
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {str(e)}")

            raise RuntimeError(f"❌ Could not load model {model_name}: {str(e)}")

    def encode(self, text: str | List[str]) -> torch.Tensor:
        if isinstance(text, str):
            text = [text]
        return self.model.encode(text, convert_to_tensor=True, show_progress_bar=False)

    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Union[str, float]]]:
        pass

    def cleanup(self):
        logger.debug(f"Cleaning up model: {self.model_name}")
        try:
            if hasattr(self, 'model') and self.model is not None:
                logger.info(f"Releasing model: {self.model_name}")
                del self.model
                self.model = None
            if self.device == 'cuda' and self.clear_cuda_cache:
                logger.info("Clearing CUDA cache")
                torch.cuda.empty_cache()
            elif self.device == 'mps':
                logger.info("Attempting to clear MPS cache")
                try:
                    # Check if empty_cache exists for MPS
                    if hasattr(torch.backends.mps, 'empty_cache'):
                        torch.backends.mps.empty_cache()
                        logger.debug("MPS cache cleared successfully")
                    else:
                        logger.warning("MPS empty_cache not available in this PyTorch version")
                except Exception as e:
                    logger.error(f"Failed to clear MPS cache: {str(e)}")
                # Force garbage collection to release MPS resources
                gc.collect()
        except Exception as e:
            logger.error(f"Failed to clean up model {self.model_name}: {str(e)}")
        logger.debug(f"Cleanup completed for model: {self.model_name}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()