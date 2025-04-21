# utils.py

MODEL_SHORT_NAMES = {
    "all-MiniLM-L6-v2": "minilm",
    "all-mpnet-base-v2": "mpnet",
    "sentence-t5-base": "t5_base",
    "distilbert-base-nli-mean-tokens": "distilbert"
    # Add more mappings as needed
}


def get_model_key(model_name: str) -> str:
    """
    Returns a short key for the given model name based on predefined mappings.
    Falls back to a sanitized version of the model name.
    """
    model_name_clean = model_name.strip().lower()

    # Try to find exact match in short name dictionary
    for full_name, short_name in MODEL_SHORT_NAMES.items():
        if full_name.lower() == model_name_clean:
            return short_name

    # Fallback: remove slashes and lowercase
    return model_name.replace("/", "_").lower()

def get_local_model_path(model_name: str) -> str:
    from pathlib import Path
    import os
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

    MODEL_DIR_BASE_PATH = os.path.dirname(CURRENT_DIR)

    MODEL_DIR_PATH = os.path.join(MODEL_DIR_BASE_PATH, "models")
    model_path = Path(os.path.join(MODEL_DIR_PATH, model_name))
    return str(model_path) if model_path.exists() else model_name  # fallback to remote





