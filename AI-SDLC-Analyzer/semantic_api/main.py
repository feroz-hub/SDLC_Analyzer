# from fastapi import FastAPI
# from pydantic import BaseModel
# from models.faiss_model import FaissSearchModel
# from models.cosine_model import CosineSimilarityModel
# from config import EMBEDDING_DIR, MODEL_SHORT_NAMES
# import os
# app = FastAPI(title="Semantic Search API")
#
# # Request body schema
# class QueryRequest(BaseModel):
#     user_query: str
#     model_name: str = "all-MiniLM-L6-v2"
#     method: str = "cosine"  # Options: 'cosine', 'faiss'
#     top_k: int = 3
#
# # API route
# @app.post("/search/")
# async def search(req: QueryRequest):
#     if req.method == "faiss":
#         short_name = MODEL_SHORT_NAMES.get(req.model_name, req.model_name.split("/")[-1].lower())
#         output_dir = os.path.join(EMBEDDING_DIR, short_name, "faiss")
#         vec_dir = os.path.normpath(output_dir)
#         model = FaissSearchModel(req.model_name, vec_dir)
#     elif req.method == "cosine":
#         short_name = MODEL_SHORT_NAMES.get(req.model_name, req.model_name.split("/")[-1].lower())
#         output_dir = os.path.join(EMBEDDING_DIR, short_name, "cosine")
#         vec_dir = os.path.normpath(output_dir)
#
#         model = CosineSimilarityModel(req.model_name, vec_dir)
#     else:
#         return {"error": f"Unsupported method: {req.method}"}
#
#     results = model.search(req.user_query, top_k=req.top_k)
#     return {
#         "query": req.user_query,
#         "method": req.method,
#         "model_name": req.model_name,
#         "top_k": req.top_k,
#         "results": results
#     }

# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, validator, field_validator
# from models.faiss_model import FaissSearchModel
# from models.cosine_model import CosineSimilarityModel
# from config import EMBEDDING_DIR, MODEL_SHORT_NAMES
# import os
# import logging
# import re
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# app = FastAPI(title="Semantic Search API")
#
# def get_vector_dir(model_name: str, method: str) -> str:
#     """Centralized path construction."""
#     short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
#     subdir = "faiss" if method == "faiss" else "cosine"
#     return os.path.normpath(os.path.join(EMBEDDING_DIR, short_name, subdir))
#
# class ModelFactory:
#     @staticmethod
#     def create_model(method: str, model_name: str, vec_dir: str) -> FaissSearchModel | CosineSimilarityModel:
#         if method == "faiss":
#             return FaissSearchModel(model_name, vec_dir)
#         elif method == "cosine":
#             return CosineSimilarityModel(model_name, vec_dir)
#         else:
#             raise ValueError(f"Unsupported method: {method}")
#
# # Request body schema
# class QueryRequest(BaseModel):
#     user_query: str
#     model_name: str = "all-MiniLM-L6-v2"
#     method: str = "cosine"  # Options: 'cosine', 'faiss'
#     top_k: int = 3
#
#     @field_validator("model_name")
#     def validate_model_name(cls, v):
#         if not re.match(r'^[a-zA-Z0-9\-_/]+$', v):
#             raise ValueError("Invalid model_name")
#         return v
#
#     @field_validator("method")
#     def validate_method(cls, v):
#         if v not in ["cosine", "faiss"]:
#             raise ValueError("Method must be 'cosine' or 'faiss'")
#         return v
#
#     @field_validator("top_k")
#     def validate_top_k(cls, v):
#         if v <= 0:
#             raise ValueError("top_k must be positive")
#         return v
#
# # API route
# @app.post("/search/")
# async def search(req: QueryRequest):
#     vec_dir = get_vector_dir(req.model_name, req.method)
#     try:
#         logger.info(f"Processing query: {req.user_query} with {req.model_name} ({req.method})")
#         with ModelFactory.create_model(req.method, req.model_name, vec_dir) as model:
#             results = model.search(req.user_query, top_k=req.top_k)
#         return {
#             "query": req.user_query,
#             "method": req.method,
#             "model_name": req.model_name,
#             "top_k": req.top_k,
#             "results": results
#         }
#     except Exception as e:
#         logger.error(f"Search failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

#
# from fastapi import FastAPI, HTTPException, Depends
# from pydantic import BaseModel, field_validator
# from models.faiss_model import FaissSearchModel
# from models.cosine_model import CosineSimilarityModel
# from config import EMBEDDING_DIR, MODEL_SHORT_NAMES
# import os
# import logging
# from logging.handlers import RotatingFileHandler
# from typing import Dict, Tuple, Union
# import re
#
# # Configure logging to write to a file and console
# try:
#     log_dir = os.path.join(os.path.dirname(__file__), "logs")
#     os.makedirs(log_dir, exist_ok=True)
#     log_file = os.path.join(log_dir, "semantic_api.log")
#
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#         handlers=[
#             RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5),  # 10MB per file, 5 backups
#             logging.StreamHandler()  # Keep console output
#         ]
#     )
# except Exception as e:
#     print(f"Failed to configure logging: {str(e)}")
#     raise
#
# logger = logging.getLogger(__name__)
# logger.info("Logging initialized")
#
# app = FastAPI(
#     title="Semantic Search API",
#     description="API for semantic search using different embedding models."
# )
#
# # Model cache to store loaded models
# class ModelCache:
#     _instance = None
#
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super(ModelCache, cls).__new__(cls)
#             cls._instance.models = {}
#         return cls._instance
#
#     def get_model(self, method: str, model_name: str) -> Union[FaissSearchModel, CosineSimilarityModel]:
#         key = f"{model_name}:{method}"
#         if key not in self.models:
#             vec_dir = get_vector_dir(model_name, method)
#             logger.info(f"Loading model {model_name} with method {method}")
#             try:
#                 self.models[key] = ModelFactory.create_model(method, model_name, vec_dir)
#             except Exception as e:
#                 logger.error(f"Failed to load model {key}: {str(e)}")
#                 raise
#         return self.models[key]
#
#     def cleanup(self):
#         """Clean up all models when application shuts down"""
#         for key, model in self.models.items():
#             logger.info(f"Cleaning up model: {key}")
#             model.cleanup()
#         self.models = {}
#
# def get_vector_dir(model_name: str, method: str) -> str:
#     """Centralized path construction."""
#     short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
#     subdir = "faiss" if method == "faiss" else "cosine"
#     return os.path.normpath(os.path.join(EMBEDDING_DIR, short_name, subdir))
#
# class ModelFactory:
#     @staticmethod
#     def create_model(method: str, model_name: str, vec_dir: str) -> Union[FaissSearchModel, CosineSimilarityModel]:
#         if method == "faiss":
#             return FaissSearchModel(model_name, vec_dir)
#         elif method == "cosine":
#             return CosineSimilarityModel(model_name, vec_dir)
#         else:
#             raise ValueError(f"Unsupported method: {method}")
#
# # Initialize model cache
# model_cache = ModelCache()
#
# # Request body schema
# class QueryRequest(BaseModel):
#     user_query: str
#     model_name: str = "all-MiniLM-L6-v2"
#     method: str = "cosine"  # Options: 'cosine', 'faiss'
#     top_k: int = 3
#
#     @field_validator("model_name")
#     def validate_model_name(cls, v):
#         if not re.match(r'^[a-zA-Z0-9\-_/]+$', v):
#             raise ValueError("Invalid model_name")
#         return v
#
#     @field_validator("method")
#     def validate_method(cls, v):
#         if v not in ["cosine", "faiss"]:
#             raise ValueError("Method must be 'cosine' or 'faiss'")
#         return v
#
#     @field_validator("top_k")
#     def validate_top_k(cls, v):
#         if v <= 0:
#             raise ValueError("top_k must be positive")
#         return v
#
# # Dependency to get the model cache
# def get_model_cache():
#     return model_cache
#
# # API route
# @app.post("/search/")
# async def search(req: QueryRequest, cache: ModelCache = Depends(get_model_cache)):
#     try:
#         logger.info(f"Processing query: {req.user_query} with {req.model_name} ({req.method})")
#         model = cache.get_model(req.method, req.model_name)
#         results = model.search(req.user_query, top_k=req.top_k)
#         return {
#             "query": req.user_query,
#             "method": req.method,
#             "model_name": req.model_name,
#             "top_k": req.top_k,
#             "results": results
#         }
#     except Exception as e:
#         logger.error(f"Search failed: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
#
# # Add event handlers for startup and shutdown
# @app.on_event("startup")
# def startup_event():
#     logger.info("Application startup: initializing model cache")
#
# @app.on_event("shutdown")
# def shutdown_event():
#     logger.info("Application shutdown: cleaning up models")
#     model_cache.cleanup()

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, field_validator
from models.faiss_model import FaissSearchModel
from models.cosine_model import CosineSimilarityModel
from config import EMBEDDING_DIR, MODEL_SHORT_NAMES
import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Tuple, Union
from contextlib import asynccontextmanager
import re
from logging_config import setup_logging,get_logger

# Configure logging
log_dir = os.path.join(os.path.dirname(__file__), "logs")
logger = setup_logging(log_dir=log_dir, log_file="semantic_api.log")
logger = get_logger(__name__)

app = FastAPI(
    title="Semantic Search API",
    description="API for semantic search using different embedding models."
)

# Model cache to store loaded models
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
        """Clean up all models when application shuts down"""
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
    logger.info("Application shutdown: cleaning up models")
    logger.debug("Starting application shutdown")
    model_cache.cleanup()
    logger.debug("Application shutdown completed")

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
        results = model.search(req.user_query, top_k=req.top_k)
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
# Ensure cleanup in basemodel.py, faiss_model.py, and cosine_model.py is robust to prevent semaphore leaks.