import os
import json
import pandas as pd
from sentence_transformers import SentenceTransformer
from config import EXCEL_FILE_PATH, EMBEDDING_VECTOR_OUTPUT_DIR

# Define a mapping for known model short names
MODEL_SHORT_NAMES = {
    "all-MiniLM-L6-v2": "minilm",
    "all-mpnet-base-v2": "mpnet",
    # Add more mappings as needed
}
# Load model
MODEL_NAME = "all-mpnet-base-v2"  # You can change this as needed
model = SentenceTransformer(MODEL_NAME)

# Extract short name or fallback to model filename
short_name = MODEL_SHORT_NAMES.get(MODEL_NAME, MODEL_NAME.split("/")[-1].lower())

# Load and process Excel data
texts = pd.read_excel(EXCEL_FILE_PATH, sheet_name='Unique_Requirements', skiprows=1, usecols="C")['Requirement Index'].dropna().tolist()

# Generate embeddings
embeddings = model.encode(texts)
# Create output filename dynamically

filename = f"{short_name}_requirement_embeddings.json"
os.makedirs(EMBEDDING_VECTOR_OUTPUT_DIR, exist_ok=True)
json_path = os.path.join(EMBEDDING_VECTOR_OUTPUT_DIR, filename)

# Save to JSON
with open(json_path, 'w') as f:
    json.dump({"texts": texts, "vectors": embeddings.tolist()}, f, indent=4)

print(f"✅ {filename} generated at {json_path}")