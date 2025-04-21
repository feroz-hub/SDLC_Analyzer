# config.py
MODEL_NAME = "all-MiniLM-L6-v2"  # or "all-mpnet-base-v2"
SEARCH_TYPE = "faiss"  # or "cosine"

# File Paths
USER_QUERY_PATH = "UserQuery.csv"
EMBEDDINGS_PATH = f"models/{MODEL_NAME}/{SEARCH_TYPE}/embeddings.npy"
TEXTS_PATH = f"models/{MODEL_NAME}/{SEARCH_TYPE}/texts.txt"
FAISS_INDEX_PATH = f"models/{MODEL_NAME}/{SEARCH_TYPE}/faiss_index.index"
JSON_EMBEDDINGS_PATH = f"models/{MODEL_NAME}/{SEARCH_TYPE}/requirement_embeddings.json"
