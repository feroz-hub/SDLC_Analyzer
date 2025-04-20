import os
import json
import numpy as np
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from .config import EXCEL_FILE_PATH, MODEL_PATH, MODEL_NAME_MINILM,MODEL_NAME_MPNET, MODEL_SHORT_NAMES, MODEL_NAME_T5





# === HELPER FUNCTIONS === #
def load_model(name):
    return SentenceTransformer(name)


def get_texts(excel_path, sheet_name='Unique_Requirements', usecols='C'):
    df = pd.read_excel(EXCEL_FILE_PATH, sheet_name=sheet_name, skiprows=1, usecols=usecols)
    return df['Requirement Index'].dropna().tolist()


def generate_json_embeddings(model_name):
    print(f"🔄 Generating JSON Embeddings using {model_name}...")
    model = load_model(model_name)
    texts = get_texts(EXCEL_FILE_PATH)
    embeddings = model.encode(texts)

    short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
    filename = f"{short_name}_requirement_embeddings.json"
    # Define the output directory structure
    output_dir = os.path.join(MODEL_PATH, short_name, "cosine")
    vec_dir = os.path.normpath(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    json_path = os.path.join(vec_dir, filename)

    with open(json_path, 'w') as f:
        json.dump({"texts": texts, "vectors": embeddings.tolist()}, f, indent=4)

    print(f"✅ {filename} saved at {json_path}")

def generate_faiss_index(model_name):
    print(f"🔄 Generating FAISS Index using {model_name}...")
    short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())

    model = load_model(model_name)
    texts = get_texts(EXCEL_FILE_PATH)
    embeddings = model.encode(texts, convert_to_numpy=True)
    short_name = MODEL_SHORT_NAMES.get(model_name, model_name.split("/")[-1].lower())
    output_dir = os.path.join(MODEL_PATH, short_name, "faiss")
    vec_dir = os.path.normpath(output_dir)

    os.makedirs(output_dir, exist_ok=True)
    np.save(os.path.join(vec_dir, f'{short_name}_embeddings.npy'), embeddings)

    with open(os.path.join(vec_dir, f'{short_name}_texts.txt'), 'w') as f:
        for line in texts:
            f.write(line + "\n")

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    faiss.write_index(index, os.path.join(vec_dir, f'{short_name}_faiss_index.index'))
    print("✅ FAISS index and files saved successfully.")

# === MAIN RUN === #
if __name__ == "__main__":
    generate_json_embeddings(MODEL_NAME_T5)
    generate_faiss_index(MODEL_NAME_T5)