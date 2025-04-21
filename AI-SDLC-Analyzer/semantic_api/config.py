import os

# Define a mapping for known model short names
MODEL_SHORT_NAMES = {
    "all-MiniLM-L6-v2": "minilm",
    "all-mpnet-base-v2": "mpnet",
    "distilbert-base-nli-mean-tokens": "distilbert",
    # Add more mappings as needed
}

# Supported models for preloading
SUPPORTED_MODELS = [
     ("all-MiniLM-L6-v2", "cosine"),
    ("all-mpnet-base-v2", "cosine"),
    ("all-MiniLM-L6-v2", "faiss"),
    ("all-mpnet-base-v2", "faiss"),
    ("distilbert-base-nli-mean-tokens", "cosine"),
    ("distilbert-base-nli-mean-tokens", "faiss"),
    # Add more models if needed, e.g., ("all-MiniLM-L6-v2", "faiss")
]

# Base directory of the semantic_api folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current file and its directory
#print(f"Base directory: {BASE_DIR}")

EMBEDDING_DIR=os.path.join(BASE_DIR,"model")
#print(f"Embedding directory:{EMBEDDING_DIR}")
INDEX_DIR=os.path.join(BASE_DIR,"data","indexex")
#print(f"Embedding directory:{INDEX_DIR}")