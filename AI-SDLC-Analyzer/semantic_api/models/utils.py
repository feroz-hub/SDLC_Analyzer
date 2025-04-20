# utils.py
def get_model_key(model_name: str) -> str:
    if "minilm" in model_name.lower():
        return "minilm"
    elif "mpnet" in model_name.lower():
        return "mpnet"
    return model_name.replace("/", "_").lower()
