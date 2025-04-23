import pytest
from core.visual_search import get_image_embedding, build_faiss_index, search_index
import numpy as np

def test_embedding_shape(tmp_path):
    # synthetic 1×1 white image
    img = np.ones((1, 512), dtype=np.float32)
    index = build_faiss_index(img)
    ids, scores = search_index(index, img, k=1)
    assert ids == [0]
    assert scores[0] > 0
