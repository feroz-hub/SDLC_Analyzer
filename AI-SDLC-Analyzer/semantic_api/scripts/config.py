import os

MODEL_NAME_MINILM = "all-MiniLM-L6-v2"
MODEL_NAME_MPNET = "all-mpnet-base-v2"
MODEL_NAME_T5 = "sentence-t5-base"
MODEL_SHORT_NAMES = {
    "all-MiniLM-L6-v2": "minilm",
    "all-mpnet-base-v2": "mpnet",
    "sentence-t5-base": "t5_base"
    # Add more mappings as needed
}

short_name = MODEL_SHORT_NAMES.get(MODEL_NAME_T5, MODEL_NAME_T5.split("/")[-1].lower())
print(short_name)

# Base directory of the semantic_api folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Get the absolute path of the current file and its directory
print(f"Base directory: {CURRENT_DIR}")

# Move one t up from the current directory
BASE_DIR_PATH = os.path.join(CURRENT_DIR, "..", "..")  # Append ".." to navigate to the parent directory

# Normalize the path to ensure it is in a standard format
BASE_DIR= os.path.normpath(BASE_DIR_PATH)  # Normalize the path to handle redundant separators or up-level references
print(f"Base directory: {BASE_DIR}")

# Define the path to the Excel file used in the project
EXCEL_FILE_PATH = os.path.join(
    BASE_DIR,
    "src",
    "Infrastructure.Resource",
    "Resources",
    "MLCR_Cybersecurity_Product_Requirements.xlsm"  # The name of the Excel file
)
print(f"Excel file path: {EXCEL_FILE_PATH}")

# Save directory (to model/)
EMBEDDINGS_PATH_DIR = os.path.join(CURRENT_DIR,"..")
EMBEDDINGS_PATH = os.path.normpath(EMBEDDINGS_PATH_DIR)
print(f"Embeddings path: {EMBEDDINGS_PATH}")
MODEL_PATH = os.path.join(EMBEDDINGS_PATH,'model')

COSINE_VECTOR_OUTPUT_DIR = os.path.normpath(MODEL_PATH)
COSINE_VECTOR_OUTPUT = os.path.join(COSINE_VECTOR_OUTPUT_DIR,'minilm')
print(COSINE_VECTOR_OUTPUT)
COSINE_VECTOR_OUTPUT = os.path.normpath(COSINE_VECTOR_OUTPUT)
print(f"Embedding vector output directory: {COSINE_VECTOR_OUTPUT_DIR}")
