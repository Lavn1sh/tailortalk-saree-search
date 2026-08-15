"""
Script to extract structured domain features (fabric, color, motifs, work)
from saree catalogue product names and generate enriched metadata.
"""

import re
import json
from pathlib import Path

MANIFEST_PATH = Path("data/image_manifest.json")
ENRICHED_MANIFEST_PATH = Path("data/enriched_manifest.json")

# Known Indian textile categories and fabrics
FABRICS = [
    "Kanchipuram", "Kancipuram", "Kancheepuram", "Kanchi", "Banarasi", "Banaras", "Organza", "Munga Crape", "Munga Crepe",
    "Pashmina", "Tussar", "Georgette", "Chiffon", "Soft Silk", "Pure Silk",
    "Raw Silk", "Chanderi", "Tissue", "Crape", "Crepe", "Linen", "Cotton",
    "Mysore Silk", "Patola", "Paithani", "Kalamkari", "Bandhani"
]

COLORS = [
    "Rani Pink", "Baby Pink", "Pink",
    "Royal Blue", "Sky Blue", "Navy Blue", "Peacock Blue", "Rama Blue", "Blue",
    "Olive Green", "Bottle Green", "Mint Green", "Parrot Green", "Rama Green", "Pista Green", "Green",
    "Ruby Red", "Maroon", "Wine", "Red",
    "Mustard", "Lemon Yellow", "Gold", "Golden", "Yellow",
    "Off White", "Cream", "Ivory", "White",
    "Rust", "Peach", "Orange",
    "Lavender", "Magenta", "Violet", "Purple",
    "Charcoal", "Silver", "Grey", "Black",
    "Copper", "Beige", "Brown", "Teal", "Turquoise"
]

MOTIFS_WORK = [
    "Gandaberunda", "Gandabherunda", "Aplic Work", "Applique", "Floral",
    "Zari", "Gold Zari", "Silver Zari", "Tissue", "Brocade", "Butta", "Butti",
    "Temple Border", "Contrast Border", "Border", "Meenakari", "Embroidery", "Printed",
    "Checks", "Stripes", "Jaal", "Korvai"
]

def extract_attributes(name: str) -> dict:
    name_clean = name.strip()
    name_lower = name_clean.lower()

    # Detect Fabric
    detected_fabric = "Saree"
    for fab in FABRICS:
        pattern = r"\b" + re.escape(fab.lower()) + r"\b"
        if re.search(pattern, name_lower):
            # Normalize naming
            if fab.lower() in ("kanchipuram", "kancipuram", "kancheepuram", "kanchi"):
                detected_fabric = "Kanchipuram Silk"
            elif fab.lower() in ("munga crape", "munga crepe"):
                detected_fabric = "Munga Crape"
            elif fab.lower() == "organza":
                detected_fabric = "Organza"
            elif fab.lower() == "banarasi":
                detected_fabric = "Banarasi"
            elif fab.lower() == "pashmina":
                detected_fabric = "Pashmina"
            else:
                detected_fabric = fab
            break

    # Detect Colors (may detect primary and secondary)
    detected_colors = []
    for col in COLORS:
        pattern = r"\b" + re.escape(col.lower()) + r"\b"
        if re.search(pattern, name_lower):
            if col not in detected_colors:
                detected_colors.append(col)

    primary_color = detected_colors[0] if detected_colors else "Multicolor/Classic"

    # Detect Motifs / Weaves / Special features
    detected_features = []
    for feat in MOTIFS_WORK:
        pattern = r"\b" + re.escape(feat.lower()) + r"\b"
        if re.search(pattern, name_lower):
            if feat not in detected_features:
                detected_features.append(feat)

    # Price category
    return {
        "fabric": detected_fabric,
        "primary_color": primary_color,
        "all_colors": detected_colors,
        "features": detected_features,
        "clean_title": name_clean
    }

def main():
    if not MANIFEST_PATH.exists():
        print(f"Manifest not found at {MANIFEST_PATH}. Run download_images.py first.")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    enriched = []
    fabric_counts = {}
    color_counts = {}

    for item in manifest:
        attr = extract_attributes(item.get("name", ""))
        enriched_item = {
            **item,
            "fabric": attr["fabric"],
            "primary_color": attr["primary_color"],
            "all_colors": attr["all_colors"],
            "features": attr["features"],
            # Formatted text snippet for hybrid search / BM25 / metadata inspection
            "text_description": f"{item.get('name', '')}. Fabric: {attr['fabric']}. Color: {attr['primary_color']}. Price: Rs. {item.get('discounted_price', item.get('retail_price', 0))}"
        }
        enriched.append(enriched_item)

        fabric_counts[attr["fabric"]] = fabric_counts.get(attr["fabric"], 0) + 1
        color_counts[attr["primary_color"]] = color_counts.get(attr["primary_color"], 0) + 1

    with open(ENRICHED_MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"Enriched {len(enriched)} items -> {ENRICHED_MANIFEST_PATH}")
    print("\nTop Fabrics:", sorted(fabric_counts.items(), key=lambda x: x[1], reverse=True)[:8])
    print("Top Colors:", sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:8])

if __name__ == "__main__":
    main()
