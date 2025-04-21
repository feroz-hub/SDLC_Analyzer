import os

# Define a mapping for known model short names
MODEL_SHORT_NAMES = {
    "all-MiniLM-L6-v2": "minilm",
    "all-mpnet-base-v2": "mpnet",
    "distilbert-base-nli-mean-tokens": "distilbert",
    # Add more mappings as needed
}
MODELS = {
    "sentence-transformers/all-MiniLM-L6-v2",
    "sentence-transformers/all-mpnet-base-v2",
    "sentence-transformers/distilbert-base-nli-mean-tokens",
}
# Supported search for preloading
SUPPORTED_MODELS = [
     ("all-MiniLM-L6-v2", "cosine"),
    ("all-mpnet-base-v2", "cosine"),
    ("all-MiniLM-L6-v2", "faiss"),
    ("all-mpnet-base-v2", "faiss"),
    ("distilbert-base-nli-mean-tokens", "cosine"),
    ("distilbert-base-nli-mean-tokens", "faiss"),
    # Add more search if needed, e.g., ("all-MiniLM-L6-v2", "faiss")
]

# Base directory of the semantic_api folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current file and its directory
#print(f"Base directory: {BASE_DIR}")
MODEL_DIR_PATH = os.path.join(BASE_DIR, "models")
MODEL_DIR = os.path.normpath(MODEL_DIR_PATH)
#print(f"Model directory: {MODEL_DIR}")# Append ".." to navigate to the parent directory
EMBEDDING_DIR=os.path.join(BASE_DIR,"model")
#print(f"Embedding directory:{EMBEDDING_DIR}")
INDEX_DIR=os.path.join(BASE_DIR,"data","indexex")
#print(f"Embedding directory:{INDEX_DIR}")