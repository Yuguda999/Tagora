#!/usr/bin/env python3
import sys
import os
import argparse
import json

import numpy as np
import faiss
import mlflow

# ensure project root is on PYTHONPATH
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT)

from mlflow_utils.mlflow_config import init_mlflow, log_run
from data_loader import (
    load_all_product_images_local,
    load_all_product_images_s3,
    load_images_from_urls,
)
from core.visual_search import get_image_embedding, build_faiss_index

def parse_args():
    p = argparse.ArgumentParser(
        description="Train & index Visual Search embeddings"
    )
    p.add_argument(
        "--source", choices=["local", "s3", "urls"], default="local",
        help="Where to load images from"
    )
    p.add_argument(
        "--image-dir", type=str,
        help="(local) path to images, named <product_id>.<ext>"
    )
    p.add_argument(
        "--s3-bucket", type=str, help="(s3) bucket name"
    )
    p.add_argument(
        "--s3-prefix", type=str, default="", help="(s3) key prefix"
    )
    p.add_argument(
        "--urls-file", type=str,
        help="(urls) path to JSON list of {url,product_id} dicts"
    )
    p.add_argument(
        "--output-index", type=str, default="data/faiss_index.bin",
        help="where to write the Faiss index"
    )
    p.add_argument(
        "--output-ids", type=str, default="data/product_ids.json",
        help="where to write the product‑ID list"
    )
    p.add_argument(
        "--tracking-uri", type=str, default=f"file://{os.getcwd()}/mlruns",
        help="MLflow tracking URI"
    )
    p.add_argument(
        "--experiment", type=str, default="visual_search",
        help="MLflow experiment name"
    )
    return p.parse_args()

def load_images(args):
    if args.source == "local":
        if not args.image_dir:
            raise ValueError("--image-dir is required for local source")
        return load_all_product_images_local(args.image_dir)
    elif args.source == "s3":
        if not args.s3_bucket:
            raise ValueError("--s3-bucket is required for s3 source")
        return load_all_product_images_s3(args.s3_bucket, prefix=args.s3_prefix)
    else:  
        if not args.urls_file:
            raise ValueError("--urls-file is required for urls source")
        with open(args.urls_file, "r") as f:
            url_list = json.load(f)
        # url_list should be [{"url": "...", "product_id": "123"}, ...]
        urls = [(entry["url"], entry["product_id"]) for entry in url_list]
        return load_images_from_urls(urls)

def main():
    args = parse_args()

    init_mlflow()
    mlflow.set_tracking_uri(args.tracking_uri)
    mlflow.set_experiment(args.experiment)

    print(f"Loading images from {args.source}…")
    images = load_images(args)
    product_ids = [pid for _, pid in images]
    num_images = len(images)
    print(f"Loaded {num_images} images.")

    print("Computing embeddings…")
    embeddings = []
    for img_bytes, _ in images:
        emb = get_image_embedding(img_bytes)  # returns shape (1,512)
        embeddings.append(emb.astype(np.float32))
    embeddings = np.vstack(embeddings)      # shape (N,512)
    emb_dim = embeddings.shape[1]

    print("Building Faiss HNSW index…")
    index = build_faiss_index(embeddings)

    # ensure output dir exists
    os.makedirs(os.path.dirname(args.output_index), exist_ok=True)
    print(f"Writing index to {args.output_index}…")
    faiss.write_index(index, args.output_index)
    with open(args.output_ids, "w") as f:
        json.dump(product_ids, f)
    print(f"Wrote product IDs to {args.output_ids}.")

    print("Logging to MLflow…")
    run_params = {
        "source": args.source,
        "num_images": num_images,
        "embed_dim": emb_dim
    }
    run_metrics = {
        "num_images": num_images
    }
    run_artifacts = {
        "faiss_index": args.output_index,
        "product_ids": args.output_ids
    }
    log_run(params=run_params, metrics=run_metrics, artifacts=run_artifacts)
    print("Done.")

if __name__ == "__main__":
    main()
