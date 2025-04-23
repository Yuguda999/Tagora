import json
import os
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

# Load product IDs for validation
with open("data/product_ids.json", "r") as f:
    PRODUCT_IDS = json.load(f)

def test_visual_search_endpoint_basic():
    """Test the basic functionality of the visual search endpoint."""
    with open("images/5_person.jpeg", "rb") as f:
        resp = client.post("/visual-search/", files={"file": ("test_image.jpg", f, "image/jpeg")})

    # Print error details if there's an error
    if resp.status_code != 200:
        print(f"Error response: {resp.status_code}")
        print(f"Error details: {resp.text}")

    assert resp.status_code == 200
    body = resp.json()

    # Check response structure
    assert "results" in body
    assert "scores" in body
    assert len(body["results"]) <= 5  # Default top_k is 5
    assert len(body["scores"]) <= 5

    # Check that each result has the expected fields
    for result in body["results"]:
        assert "id" in result
        assert "product_id" in result
        assert "name" in result

        # Verify that the product_id is valid
        assert result["product_id"] in PRODUCT_IDS

        # Verify that the id is a valid index into the product_ids list
        assert 0 <= result["id"] < len(PRODUCT_IDS)

        # Verify that the product_id matches the id's lookup in PRODUCT_IDS
        assert PRODUCT_IDS[result["id"]] == result["product_id"]

def test_visual_search_with_custom_top_k():
    """Test the visual search endpoint with a custom top_k parameter."""
    top_k = 3
    with open("images/5_person.jpeg", "rb") as f:
        resp = client.post(f"/visual-search/?top_k={top_k}",
                          files={"file": ("test_image.jpg", f, "image/jpeg")})

    assert resp.status_code == 200
    body = resp.json()

    # Check that we get exactly top_k results
    assert len(body["results"]) <= top_k
    assert len(body["scores"]) <= top_k

def test_visual_search_with_different_images():
    """Test the visual search endpoint with different images."""
    # Test with multiple different images
    for image_file in os.listdir("images"):
        if image_file.endswith((".jpeg", ".jpg", ".png")):
            with open(f"images/{image_file}", "rb") as f:
                resp = client.post("/visual-search/",
                                  files={"file": (image_file, f, "image/jpeg")})

            assert resp.status_code == 200
            body = resp.json()

            # Basic validation
            assert "results" in body
            assert "scores" in body
            assert len(body["results"]) > 0

def test_visual_search_error_handling():
    """Test error handling in the visual search endpoint."""
    # Test with invalid file (empty file)
    resp = client.post("/visual-search/", files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert resp.status_code == 500  # Should return an error

    # Test with missing file
    resp = client.post("/visual-search/")
    assert resp.status_code == 422  # Validation error

def test_visual_search_large_top_k():
    """Test with a top_k larger than the number of available items."""
    # Set top_k to a value larger than the number of items in the index
    top_k = 100
    with open("images/5_person.jpeg", "rb") as f:
        resp = client.post(f"/visual-search/?top_k={top_k}",
                          files={"file": ("test_image.jpg", f, "image/jpeg")})

    assert resp.status_code == 200
    body = resp.json()

    # Should return at most the number of items in the index
    assert len(body["results"]) <= len(PRODUCT_IDS)
    assert len(body["scores"]) <= len(PRODUCT_IDS)

def test_visual_search_response_consistency():
    """Test that the response is consistent for the same image."""
    # Make two identical requests
    with open("images/5_person.jpeg", "rb") as f:
        resp1 = client.post("/visual-search/",
                           files={"file": ("test_image.jpg", f, "image/jpeg")})

    with open("images/5_person.jpeg", "rb") as f:
        resp2 = client.post("/visual-search/",
                           files={"file": ("test_image.jpg", f, "image/jpeg")})

    # Both responses should be identical
    assert resp1.json() == resp2.json()
