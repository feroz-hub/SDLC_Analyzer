from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from search.faiss_search import FaissSearchModel
from search.cosine_search import CosineSimilarityModel
from config import EMBEDDING_DIR, MODEL_SHORT_NAMES
import os
from preprocess import preprocess_query
from typing import Union
from contextlib import asynccontextmanager
import re
from logging_config import setup_logging,get_logger

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), "logs")
logger = setup_logging(log_dir=log_dir, log_file="semantic_api.log")

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Startup: Loading resources...")
    # e.g., preload search here
    yield
    print("🛑 Shutdown: Cleaning up...")
    # e.g., release memory/resources

app = FastAPI(
    title="Semantic Search API",
    description="API for semantic search using different embedding search.",
    lifespan=lifespan
)

# Model cache to store loaded search
class ModelCache:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelCache, cls).__new__(cls)
            cls._instance.models = {}
        return cls._instance

    def get_model(self, method: str, model_name: str) -> Union[FaissSearchModel, CosineSimilarityModel]:
        key = f"{model_name}:{method}"
        if key not in self.models:
            vec_dir = get_vector_dir(model_name, method)
            logger.info(f"Loading model {model_name} with method {method}")
            try:
                self.models[key] = ModelFactory.create_model(method, model_name, vec_dir)
            except Exception as e:
                logger.error(f"Failed to load model {key}: {str(e)}")
                raise
        return self.models[key]

    def cleanup(self):
        """Clean up all search when application shuts down"""
        logger.debug("Starting model cache cleanup")
        logger.debug(f"Models in cache: {list(self.models.keys())}")
        for key, model in list(self.models.items()):
            logger.info(f"Cleaning up model: {key}")
            try:
                model.cleanup()
                del self.models[key]
            except Exception as e:
                logger.error(f"Failed to clean up model {key}: {str(e)}")
        self.models.clear()
        logger.debug("Model cache cleanup completed")
        # Log memory usage after cleanup
        try:
            import psutil
            logger.debug(f"Memory usage after cleanup: {psutil.virtual_memory().percent}%")
        except ImportError:
            logger.debug("psutil not installed, skipping memory usage logging")

def get_vector_dir(model_name: str, method: str) -> str:
    """Centralized path construction."""
    short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
    subdir = "faiss" if method == "faiss" else "cosine"
    return os.path.normpath(os.path.join(EMBEDDING_DIR, short_name, subdir))

class ModelFactory:
    @staticmethod
    def create_model(method: str, model_name: str, vec_dir: str) -> Union[FaissSearchModel, CosineSimilarityModel]:
        if method == "faiss":
            return FaissSearchModel(model_name, vec_dir)
        elif method == "cosine":
            return CosineSimilarityModel(model_name, vec_dir)
        else:
            raise ValueError(f"Unsupported method: {method}")

# Initialize model cache
model_cache = ModelCache()

# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup: initializing model cache")
    for model_name in MODEL_SHORT_NAMES:
        for method in ["cosine", "faiss"]:
            try:
                model_cache.get_model(method, model_name)
            except Exception as e:
                logger.error(f"Failed to preload model {model_name} ({method}): {str(e)}")
    yield
    logger.info("Application shutdown: cleaning up model cache")
    model_cache.cleanup()

app.lifespan = lifespan

# Request body schema
class QueryRequest(BaseModel):
    user_query: str
    model_name: str = "all-MiniLM-L6-v2"
    method: str = "cosine"  # Options: 'cosine', 'faiss'
    top_k: int = 3

    @field_validator("model_name")
    def validate_model_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\-_/]+$', v):
            raise ValueError("Invalid model_name")
        return v

    @field_validator("method")
    def validate_method(cls, v):
        if v not in ["cosine", "faiss"]:
            raise ValueError("Method must be 'cosine' or 'faiss'")
        return v

    @field_validator("top_k")
    def validate_top_k(cls, v):
        if v <= 0:
            raise ValueError("top_k must be positive")
        return v

# Dependency to get the model cache
def get_model_cache():
    return model_cache

# API route
@app.post("/search/")
async def search(req: QueryRequest, cache: ModelCache = Depends(get_model_cache)):
    try:
        logger.info(f"Processing query: {req.user_query} with {req.model_name} ({req.method})")
        model = cache.get_model(req.method, req.model_name)
        preprocessed_query = preprocess_query(req.user_query)
        logger.info(f"PreProcessed query: {preprocessed_query} with {req.model_name} ({req.method})")
        results = model.search(preprocessed_query, top_k=req.top_k)
        return {
            "query": req.user_query,
            "method": req.method,
            "model_name": req.model_name,
            "top_k": req.top_k,
            "results": results
        }
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


# Note: Run Uvicorn in single-process mode for development to avoid multiprocessing issues:
#   uvicorn main:app --reload  (single-process, auto-reload for development)
# For production with higher throughput, test multiprocessing after verifying cleanup:
#   uvicorn main:app --workers 4  (use number of CPU cores, e.g., 4)
# Ensure cleanup in basemodel.py, faiss_search.py, and cosine_search.py is robust to prevent semaphore leaks.