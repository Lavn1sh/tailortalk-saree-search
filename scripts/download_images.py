"""
Script to download catalogue saree images concurrently and create a manifest.
Dataset: byrappa_tejas_31july.csv
Target: data/images/
Output: data/image_manifest.json
"""

import os
import csv
import json
import time
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse

CSV_PATH = Path("byrappa_tejas_31july.csv")
IMAGES_DIR = Path("data/images")
MANIFEST_PATH = Path("data/image_manifest.json")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
}

def download_single_image(row_idx: int, item: dict, max_retries: int = 3) -> dict:
    url = item.get("image_url", "").strip()
    sku = item.get("SKU", f"item_{row_idx}").strip()
    clean_sku = "".join(c for c in sku if c.isalnum() or c in ("-", "_"))
    filename = f"{row_idx:04d}_{clean_sku}.webp"
    dest_path = IMAGES_DIR / filename

    result = {
        "id": f"saree_{row_idx:04d}",
        "index": row_idx,
        "sku": item.get("SKU", "").strip(),
        "name": item.get("Name", "").strip(),
        "stock": int(item.get("Stock", 0)) if item.get("Stock", "").isdigit() else 0,
        "retail_price": float(item.get("Retail Price", 0)) if item.get("Retail Price", "").replace(".", "", 1).isdigit() else 0.0,
        "discounted_price": float(item.get("Discounted Price", 0)) if item.get("Discounted Price", "").replace(".", "", 1).isdigit() else 0.0,
        "image_url": url,
        "website_link": item.get("Website Link", "").strip(),
        "local_image_path": str(dest_path),
        "status": "pending",
        "error": None
    }

    if not url:
        result["status"] = "failed"
        result["error"] = "Empty URL"
        return result

    if dest_path.exists() and dest_path.stat().st_size > 500:
        result["status"] = "cached"
        return result

    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12)
            if resp.status_code == 200 and len(resp.content) > 500:
                dest_path.write_bytes(resp.content)
                result["status"] = "downloaded"
                result["size_bytes"] = len(resp.content)
                return result
            else:
                if attempt == max_retries:
                    result["status"] = "failed"
                    result["error"] = f"HTTP {resp.status_code}"
        except Exception as e:
            if attempt == max_retries:
                result["status"] = "failed"
                result["error"] = str(e)
            time.sleep(0.5 * attempt)

    return result

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    if not CSV_PATH.exists():
        print(f"Error: {CSV_PATH} not found!")
        return

    with open(CSV_PATH, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} products from {CSV_PATH}")
    print(f"Downloading images to {IMAGES_DIR} with 20 parallel workers...")

    start_time = time.time()
    manifest = []
    success_count = 0
    failed_count = 0
    cached_count = 0

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(download_single_image, idx, row): idx for idx, row in enumerate(rows)}
        for future in as_completed(futures):
            res = future.result()
            manifest.append(res)
            if res["status"] == "downloaded":
                success_count += 1
            elif res["status"] == "cached":
                cached_count += 1
            else:
                failed_count += 1

            total_done = success_count + cached_count + failed_count
            if total_done % 100 == 0 or total_done == len(rows):
                print(f"Progress: {total_done}/{len(rows)} (Downloaded: {success_count}, Cached: {cached_count}, Failed: {failed_count})")

    # Sort manifest by index
    manifest.sort(key=lambda x: x["index"])

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start_time
    print(f"\nDone in {elapsed:.2f}s!")
    print(f"Manifest written to {MANIFEST_PATH}")
    print(f"Total: {len(manifest)} | Success: {success_count + cached_count} | Failed: {failed_count}")

if __name__ == "__main__":
    main()
