# Tagora - Visual Search API

Tagora is a visual search system that allows you to find similar images based on visual content. It uses CLIP embeddings and FAISS indexing to provide fast and accurate image similarity search.

## Features

- **Visual Search**: Upload an image and find visually similar images in the database
- **Fast Indexing**: Uses FAISS HNSW indexing for efficient similarity search
- **REST API**: Simple FastAPI-based REST API for easy integration
- **Comprehensive Testing**: Includes unit tests for both core functionality and API endpoints

## Architecture

The system consists of the following components:

1. **CLIP Model**: Extracts visual features from images
2. **FAISS Index**: Stores and searches image embeddings efficiently
3. **FastAPI Server**: Provides a REST API for searching similar images

## Installation

### Prerequisites

- Python 3.8+
- FastAPI
- PyTorch
- FAISS
- Uvicorn (for serving the API)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tagora.git
   cd tagora
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Prepare your image dataset in the `images/` directory. Images should be named with their IDs (e.g., `1_cat.jpeg`).

4. Build the index:
   ```bash
   python scripts/train_and_index.py --source local --image-dir images/
   ```

## Usage

### Starting the API Server

```bash
uvicorn api.app:app --reload
```

The API will be available at http://localhost:8000.

### API Endpoints

#### Visual Search

**Endpoint**: `POST /visual-search/`

**Parameters**:
- `file`: The image file to search for (form data)
- `top_k`: Number of results to return (default: 5)

**Response**:
```json
{
  "results": [
    {
      "id": 2,
      "product_id": "5",
      "name": "person"
    },
    {
      "id": 0,
      "product_id": "4",
      "name": "human"
    }
  ],
  "scores": [0.0, 1.0344889163970947]
}
```

### Example Usage with cURL

```bash
curl -X POST "http://localhost:8000/visual-search/?top_k=3" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/image.jpg"
```

### Example Usage with Python

```python
import requests

url = "http://localhost:8000/visual-search/"
files = {"file": ("image.jpg", open("path/to/image.jpg", "rb"), "image/jpeg")}
params = {"top_k": 3}

response = requests.post(url, files=files, params=params)
results = response.json()
print(results)
```

## Testing

Run the tests with pytest:

```bash
python -m pytest
```

The test suite includes:
- Core functionality tests (embedding generation, indexing, search)
- API endpoint tests
- Edge case handling

## Project Structure

```
tagora/
├── api/
│   └── app.py                # FastAPI application
├── core/
│   └── visual_search.py      # Core search functionality
├── data/
│   ├── faiss_index.bin       # FAISS index (generated)
│   └── product_ids.json      # Product IDs mapping (generated)
├── images/                   # Image dataset
├── models/
│   └── clip_model.py         # CLIP model wrapper
├── scripts/
│   └── train_and_index.py    # Script to build the index
├── tests/
│   ├── test_api.py           # API tests
│   └── test_core.py          # Core functionality tests
├── mlflow_utils/             # MLflow utilities
├── data_loader.py            # Data loading utilities
└── README.md                 # This file
```

## How It Works

1. **Indexing**:
   - Images are loaded from the specified source (local, S3, or URLs)
   - CLIP extracts visual features from each image
   - Features are indexed using FAISS HNSW for efficient similarity search
   - The index and product IDs mapping are saved to disk

2. **Searching**:
   - User uploads an image via the API
   - CLIP extracts features from the uploaded image
   - FAISS searches for similar embeddings in the index
   - The API parses product IDs using regex to separate numeric IDs and descriptive names
   - The API returns the most similar images with their IDs, names, and similarity scores

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.