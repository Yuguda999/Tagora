import faiss
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, HTTPException
from core.visual_search import get_image_embedding, search_index

# Global variables to store resources
faiss_index = None
product_ids = None

# Load resources function that can be called both in lifespan and directly
def load_resources():
    global faiss_index, product_ids
    if faiss_index is None:
        faiss_index = faiss.read_index("data/faiss_index.bin")

    if product_ids is None:
        # Load the product IDs that correspond to the FAISS index
        with open("data/product_ids.json", "r") as f:
            product_ids = json.load(f)

@asynccontextmanager
async def lifespan(_: FastAPI):
    # Load resources on startup
    load_resources()

    yield

    # Clean up resources if needed when shutting down
    # (nothing to clean up in this case)

app = FastAPI(title="Visual Search 2.0", lifespan=lifespan)

# Load resources immediately for testing purposes
load_resources()

@app.post("/visual-search/")
async def visual_search(file: UploadFile = File(...), top_k: int = 5):
    image_bytes = await file.read()
    try:
        # Ensure top_k doesn't exceed the number of items in the index
        effective_top_k = min(top_k, len(product_ids))

        query_emb = get_image_embedding(image_bytes)
        faiss_ids, scores = search_index(faiss_index, query_emb, k=effective_top_k)

        # Map FAISS index IDs to actual product IDs and names
        mapped_results = []
        valid_scores = []

        for i, idx in enumerate(faiss_ids):
            if 0 <= idx < len(product_ids):
                product_id = product_ids[idx]
                mapped_results.append({
                    "id": idx,
                    "product_id": product_id,
                    "name": product_id  # Using product_id as name for now
                })
                valid_scores.append(scores[i])

        return {
            "results": mapped_results,
            "scores": valid_scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
