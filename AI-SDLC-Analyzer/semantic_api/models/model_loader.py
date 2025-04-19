# # semantic_api/model_loader.py
# from sentence_transformers import SentenceTransformer
# import torch
# from config import MODEL_NAME
#
# device = 'cuda' if torch.cuda.is_available() else 'cpu'
#
# def load_model():
#     print(f"Loading model on: {device}")
#     return SentenceTransformer(MODEL_NAME).to(device)
