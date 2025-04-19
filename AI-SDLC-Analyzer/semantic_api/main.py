from fastapi import FastAPI
from pydantic import BaseModel
from models.faiss_model import FaissSearchModel
from models.cosine_model import CosineSimilarityModel
from config import EMBEDDING_DIR, MODEL_SHORT_NAMES
import os
app = FastAPI(title="Semantic Search API")

# Request body schema
class QueryRequest(BaseModel):
    user_query: str
    model_name: str = "all-MiniLM-L6-v2"
    method: str = "cosine"  # Options: 'cosine', 'faiss'
    top_k: int = 3

# API route
@app.post("/search/")
async def search(req: QueryRequest):
    if req.method == "faiss":
        short_name = MODEL_SHORT_NAMES.get(req.model_name, req.model_name.split("/")[-1].lower())
        output_dir = os.path.join(EMBEDDING_DIR, short_name, "faiss")
        vec_dir = os.path.normpath(output_dir)
        model = FaissSearchModel(req.model_name, vec_dir)
    elif req.method == "cosine":
        short_name = MODEL_SHORT_NAMES.get(req.model_name, req.model_name.split("/")[-1].lower())
        output_dir = os.path.join(EMBEDDING_DIR, short_name, "cosine")
        vec_dir = os.path.normpath(output_dir)

        model = CosineSimilarityModel(req.model_name, vec_dir)
    else:
        return {"error": f"Unsupported method: {req.method}"}

    results = model.search(req.user_query, top_k=req.top_k)
    return {
        "query": req.user_query,
        "method": req.method,
        "model_name": req.model_name,
        "top_k": req.top_k,
        "results": results
    }
