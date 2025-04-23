from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_visual_search_endpoint():
    with open("tests/fixtures/white.jpg", "rb") as f:
        resp = client.post("/visual-search/", files={"file": ("white.jpg", f, "image/jpeg")})
    assert resp.status_code == 200
    body = resp.json()
    assert "product_ids" in body and len(body["product_ids"]) <= 5
