"""Helper script: download DejaVu Sans fonts for local development.

Run once before starting the app if PDF Cyrillic rendering is broken:
    python download_fonts.py
"""
import os
import urllib.request

FONTS = {
    "DejaVuSans.ttf": (
        "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans.ttf"
    ),
    "DejaVuSans-Bold.ttf": (
        "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf"
    ),
}

os.makedirs("fonts", exist_ok=True)

for name, url in FONTS.items():
    dest = os.path.join("fonts", name)
    if os.path.exists(dest):
        print(f"  already exists: {dest}")
        continue
    print(f"  downloading {name}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"  saved to {dest}")
    except Exception as e:
        print(f"  failed: {e}")

print("Done.")
