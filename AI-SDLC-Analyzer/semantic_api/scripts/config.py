import os
# Base directory of the semantic_api folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Get the absolute path of the current file and its directory
#print(f"Base directory: {CURRENT_DIR}")
MODEL_DIR_BASE_PATH = os.path.join(CURRENT_DIR,"..")
MODEL_DIR_PATH = os.path.join(MODEL_DIR_BASE_PATH,"models")
MODELS_DIR = os.path.normpath(MODEL_DIR_PATH)

#print(f"Model directory path: {MODELS_DIR}")

MODEL_NAME_MINILM = "all-MiniLM-L6-v2"
MODEL_NAME_MPNET = "all-mpnet-base-v2"

MODEL_DISTILBERT="distilbert-base-nli-mean-tokens"
MODEL_SHORT_NAMES = {
    os.path.join(MODELS_DIR, "all-MiniLM-L6-v2"): "minilm",
    os.path.join(MODELS_DIR, "all-mpnet-base-v2"): "mpnet",
    os.path.join(MODELS_DIR, "distilbert-base-nli-mean-tokens"): "distilbert"
}
# Move one t up from the current directory
BASE_DIR_PATH = os.path.join(CURRENT_DIR, "..", "..")  # Append ".." to navigate to the parent directory

# Normalize the path to ensure it is in a standard format
BASE_DIR= os.path.normpath(BASE_DIR_PATH)  # Normalize the path to handle redundant separators or up-level references

#print(f"Base directory: {BASE_DIR}")

# Define the path to the Excel file used in the project
EXCEL_FILE_PATH = os.path.join(
    BASE_DIR,
    "src",
    "Infrastructure.Resource",
    "Resources",
    "MLCR_Cybersecurity_Product_Requirements.xlsm"  # The name of the Excel file
)
EXCEL_FILE = os.path.normpath(EXCEL_FILE_PATH)
#print(f"Excel file path: {EXCEL_FILE_PATH}")

# Save directory (to model/)
EMBEDDINGS_PATH_DIR = os.path.join(CURRENT_DIR,"..")
EMBEDDINGS_PATH = os.path.normpath(EMBEDDINGS_PATH_DIR)
#print(f"Embeddings path: {EMBEDDINGS_PATH}")
MODEL_PATH = os.path.join(EMBEDDINGS_PATH,'model')
