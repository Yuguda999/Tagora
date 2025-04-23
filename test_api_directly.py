import json
import traceback
from fastapi.testclient import TestClient
from api.app import app

client = TestClient(app)

def test_api():
    try:
        with open("images/5_person.jpeg", "rb") as f:
            resp = client.post("/visual-search/", files={"file": ("test_image.jpg", f, "image/jpeg")})
        
        print(f"Status code: {resp.status_code}")
        if resp.status_code != 200:
            print(f"Error details: {resp.text}")
        else:
            print(f"Response: {json.dumps(resp.json(), indent=2)}")
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
