import pytest
import os
import numpy as np
import faiss
from core.visual_search import get_image_embedding, build_faiss_index, search_index

def test_embedding_shape():
    """Test that embeddings have the expected shape and search works."""
    # Create a synthetic embedding
    img = np.ones((1, 512), dtype=np.float32)
    # Normalize the embedding
    img = img / np.linalg.norm(img)
    index = build_faiss_index(img)
    ids, scores = search_index(index, img, k=1)

    # Basic assertions
    assert ids == [0]
    # In FAISS, smaller scores are better (they're distances)
    assert scores[0] >= 0.0  # Score should be non-negative

def test_get_image_embedding():
    """Test that get_image_embedding returns the expected shape."""
    # Load a real image
    with open("images/5_person.jpeg", "rb") as f:
        image_bytes = f.read()

    # Get embedding
    embedding = get_image_embedding(image_bytes)

    # Check shape and normalization
    assert embedding.shape[0] == 1  # Batch size of 1
    assert embedding.shape[1] > 0   # Feature dimension should be positive

    # Check that the embedding is normalized (L2 norm should be close to 1)
    norm = np.linalg.norm(embedding)
    assert 0.99 <= norm <= 1.01

def test_build_faiss_index_with_multiple_embeddings():
    """Test building a FAISS index with multiple embeddings."""
    # Create multiple synthetic embeddings
    num_embeddings = 5
    dim = 512
    embeddings = np.random.rand(num_embeddings, dim).astype(np.float32)

    # Normalize embeddings (as CLIP would do)
    for i in range(num_embeddings):
        embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])

    # Build index
    index = build_faiss_index(embeddings)

    # Check index properties
    assert index.ntotal == num_embeddings
    assert index.d == dim

def test_search_index_with_k():
    """Test searching with different k values."""
    # Create multiple synthetic embeddings
    num_embeddings = 10
    dim = 512
    embeddings = np.random.rand(num_embeddings, dim).astype(np.float32)

    # Normalize embeddings
    for i in range(num_embeddings):
        embeddings[i] = embeddings[i] / np.linalg.norm(embeddings[i])

    # Build index
    index = build_faiss_index(embeddings)

    # Test with different k values
    for k in [1, 3, 5, num_embeddings]:
        query = embeddings[0].reshape(1, -1)  # Use first embedding as query
        ids, scores = search_index(index, query, k=k)

        # Check results
        assert len(ids) == min(k, num_embeddings)
        assert len(scores) == min(k, num_embeddings)

        # First result should be the query itself with score close to 0 (small distance)
        assert ids[0] == 0
        assert scores[0] < 0.01  # Should be very close to 0

def test_search_index_with_real_images():
    """Test search with real images from the dataset."""
    # Load a few images
    image_files = sorted(os.listdir("images"))[:3]  # Just use first 3 images, sorted for consistency
    embeddings = []

    for image_file in image_files:
        if image_file.endswith((".jpeg", ".jpg", ".png")):
            with open(f"images/{image_file}", "rb") as f:
                image_bytes = f.read()
                embedding = get_image_embedding(image_bytes)
                embeddings.append(embedding[0])  # Remove batch dimension

    # Stack embeddings
    embeddings = np.vstack(embeddings)

    # Build index
    index = build_faiss_index(embeddings)

    # Search with first image as query
    with open(f"images/{image_files[0]}", "rb") as f:
        query_bytes = f.read()
        query_emb = get_image_embedding(query_bytes)

    ids, scores = search_index(index, query_emb, k=3)

    # First result should be the query itself with a small distance
    assert ids[0] == 0
    assert scores[0] < 0.01  # Should be very close to 0

def test_faiss_index_persistence():
    """Test that FAISS indices can be saved and loaded."""
    # Create a simple index
    dim = 512
    embeddings = np.random.rand(5, dim).astype(np.float32)
    index = build_faiss_index(embeddings)

    # Save index to a temporary file
    temp_file = "temp_index.bin"
    faiss.write_index(index, temp_file)

    # Load index
    loaded_index = faiss.read_index(temp_file)

    # Check that loaded index has same properties
    assert loaded_index.ntotal == index.ntotal
    assert loaded_index.d == index.d

    # Clean up
    os.remove(temp_file)
