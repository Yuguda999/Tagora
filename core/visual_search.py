from PIL import Image
from io import BytesIO
import torch
import faiss
import numpy as np

# Load CLIP once at import time
from models.clip_model import model as _clip_model, processor as _processor


def get_image_embedding(image_bytes: bytes) -> np.ndarray:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    inputs = _processor(images=image, return_tensors="pt")
    with torch.no_grad():
        feats = _clip_model.get_image_features(**inputs)
    feats = feats / feats.norm(p=2, dim=-1, keepdim=True)
    return feats.cpu().numpy()

def build_faiss_index(embeddings: np.ndarray):
    dim = embeddings.shape[1]
    index = faiss.IndexHNSWFlat(dim, 32)  # HNSW for speed+accuracy
    index.hnsw.efConstruction = 200
    index.add(embeddings)
    return index

def search_index(index: faiss.Index, query_emb: np.ndarray, k: int = 5):
    D, I = index.search(query_emb, k)
    return I.tolist()[0], D.tolist()[0]
