import os
import requests

IMAGE_DIR = "images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Expanded list of product-like images
image_data = {
    "001_shoe.jpg": "https://images.unsplash.com/photo-1519744792095-2f2205e87b6f",
    "002_sandal.jpg": "https://images.unsplash.com/photo-1584467735871-b7fcb7aef5aa",
    "003_hat.jpg": "https://images.unsplash.com/photo-1562157873-818bc0726f83",
    "004_backpack.jpg": "https://images.unsplash.com/photo-1600185365567-15d423d03f06",
    "005_dress.jpg": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2",
    "006_beach_sandal.jpg": "https://images.unsplash.com/photo-1595950658703-663c33f6d2a4",
    "007_tshirt.jpg": "https://images.unsplash.com/photo-1580910051071-24f4f7df0e8b",
    "008_suit.jpg": "https://images.unsplash.com/photo-1600180758890-6f5d502c41ab",
    "009_watch.jpg": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
    "010_glasses.jpg": "https://images.unsplash.com/photo-1589571894960-20bbe2828c84",
    "011_jeans.jpg": "https://images.unsplash.com/photo-1600185365981-e74a41e305e3",
    "012_jacket.jpg": "https://images.unsplash.com/photo-1512436991641-6745cdb1723f",
    "013_handbag.jpg": "https://images.unsplash.com/photo-1571771681367-4e44724e6c5f",
    "014_boots.jpg": "https://images.unsplash.com/photo-1575301976455-00a1f6c57918",
    "015_earrings.jpg": "https://images.unsplash.com/photo-1603349206299-d8aeac9ce53e",
    "016_scarf.jpg": "https://images.unsplash.com/photo-1600185365813-8e00c4e6bb91",
    "017_beanie.jpg": "https://images.unsplash.com/photo-1617049078250-b93a1c1aab4e",
    "018_necklace.jpg": "https://images.unsplash.com/photo-1600185365704-2a4575f04bde",
    "019_bracelet.jpg": "https://images.unsplash.com/photo-1600185365524-c90e90d90a64",
    "020_socks.jpg": "https://images.unsplash.com/photo-1575537302964-1ab05460e91f",
    "021_sneakers.jpg": "https://images.unsplash.com/photo-1596464716122-089d0fbc6f6b",
    "022_heels.jpg": "https://images.unsplash.com/photo-1556909114-ecfc47ffb5f6",
    "023_belt.jpg": "https://images.unsplash.com/photo-1562158070-4b38c8b2b749",
    "024_sweater.jpg": "https://images.unsplash.com/photo-1577041348497-fc74e9a2e89d",
    "025_tote_bag.jpg": "https://images.unsplash.com/photo-1576306467526-b7be64c29961",
    "026_polo.jpg": "https://images.unsplash.com/photo-1578760544098-92ad7e5e7e51",
    "027_hoodie.jpg": "https://images.unsplash.com/photo-1600185366047-1f78e3d905f0",
    "028_tank_top.jpg": "https://images.unsplash.com/photo-1593032457862-8edc6384714e",
    "029_sunglasses.jpg": "https://images.unsplash.com/photo-1519681393784-d120267933ba",
    "030_rings.jpg": "https://images.unsplash.com/photo-1599934827884-09f444d06552"
}

def download_images():
    for filename, url in image_data.items():
        dest_path = os.path.join(IMAGE_DIR, filename)
        if os.path.exists(dest_path):
            print(f"✔️ Already exists: {filename}")
            continue
        print(f"⬇️ Downloading {filename}...")
        try:
            response = requests.get(url, stream=True, timeout=10)
            if response.status_code == 200:
                with open(dest_path, 'wb') as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
                print(f"✅ Saved: {filename}")
            else:
                print(f"❌ Failed to download {filename} (status: {response.status_code})")
        except Exception as e:
            print(f"❌ Error downloading {filename}: {e}")

if __name__ == "__main__":
    download_images()
