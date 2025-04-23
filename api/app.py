import faiss
from fastapi import FastAPI, File, UploadFile, HTTPException
from core.visual_search import get_image_embedding, search_index
from mlflow_utils import mlflow_config

app = FastAPI(title="Visual Search 2.0")

# On startup: load your FAISS index & MLflow model URI
@app.on_event("startup")
def load_resources():
    global faiss_index
    faiss_index = faiss.read_index("data/faiss_index.bin")

@app.post("/visual-search/")
async def visual_search(file: UploadFile = File(...), top_k: int = 5):
    image_bytes = await file.read()
    try:
        query_emb = get_image_embedding(image_bytes)
        ids, scores = search_index(faiss_index, query_emb, k=top_k)
        return {"product_ids": ids, "scores": scores}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
