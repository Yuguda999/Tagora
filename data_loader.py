# visual-search/data_loader.py

import os
from io import BytesIO
from typing import List, Tuple

import boto3
from botocore.exceptions import BotoCoreError, ClientError
import requests

def load_all_product_images_local(image_dir: str) -> List[Tuple[bytes, str]]:
    """
    Load all product images from a local directory.
    Filenames must be <product_id>.<ext>, e.g. "1234.jpg".
    Returns a list of (image_bytes, product_id).
    """
    images = []
    for fname in os.listdir(image_dir):
        prod_id, _ = os.path.splitext(fname)
        path = os.path.join(image_dir, fname)
        with open(path, "rb") as f:
            img_bytes = f.read()
        images.append((img_bytes, prod_id))
    return images


def load_all_product_images_s3(bucket_name: str, prefix: str = "") -> List[Tuple[bytes, str]]:
    """
    Load all product images from an S3 bucket.
    Assumes keys under `prefix/` are named <product_id>.<ext>.
    Requires AWS credentials in env or ~/.aws/credentials.
    """
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    images: List[Tuple[bytes, str]] = []

    for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
        for obj in page.get("Contents", []):
            key = obj["Key"]
            prod_id, _ = os.path.splitext(os.path.basename(key))
            try:
                resp = s3.get_object(Bucket=bucket_name, Key=key)
                img_bytes = resp["Body"].read()
                images.append((img_bytes, prod_id))
            except (BotoCoreError, ClientError) as e:
                print(f"Error fetching {key} from S3: {e}")
    return images


def load_images_from_urls(urls: List[Tuple[str, str]]) -> List[Tuple[bytes, str]]:
    """
    Given a list of (url, product_id), fetch via HTTP.
    """
    images = []
    for url, prod_id in urls:
        try:
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            images.append((r.content, prod_id))
        except Exception as e:
            print(f"Error fetching {url}: {e}")
    return images
