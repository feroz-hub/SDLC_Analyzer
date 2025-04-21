from huggingface_hub import snapshot_download
import os
from config import MODEL_DIR, MODELS

os.makedirs(MODEL_DIR, exist_ok=True)  # Create the model directory if it doesn't exist
for model_name in MODELS:
    print(f"Downloading {model_name}...")
    snapshot_download(repo_id=model_name, local_dir=os.path.join(MODEL_DIR, model_name.split("/")[-1]),
                      cache_dir=MODEL_DIR)
    print(f"✅ {model_name} downloaded to {os.path.join(MODEL_DIR, model_name.split('/')[-1])}")