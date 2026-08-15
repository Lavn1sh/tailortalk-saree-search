"""
Automated unit and integration tests for TailorTalk Saree Visual Search.
"""

import os
import sys
import json
import pytest
import numpy as np
from PIL import Image
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.colour_analysis import (
    compute_hsv_histogram,
    compare_color_histograms,
    extract_dominant_colors
)
from scripts.enhance_metadata import extract_attributes
from src.agent import find_similar_sarees, search_sarees_by_text

def test_extract_attributes():
    """Test saree metadata extraction from catalog titles."""
    title1 = "Pure Kancipuram Saree Olive Green With Orange Border AA314608"
    attr1 = extract_attributes(title1)
    assert "Kanchipuram" in attr1["fabric"]
    assert "Green" in attr1["all_colors"] or "Olive Green" in attr1["all_colors"]
    assert "Border" in str(attr1["features"])

    title2 = "Organza Tissue Sarees - White & Gold Colour QA255622"
    attr2 = extract_attributes(title2)
    assert "Organza" in attr2["fabric"]
    assert "White" in attr2["all_colors"] or "Gold" in attr2["all_colors"]

    title3 = "Pashmina - Banarasi Saree - Pink Colour QS204820"
    attr3 = extract_attributes(title3)
    assert "Banarasi" in attr3["fabric"] or "Pashmina" in attr3["fabric"]
    assert "Pink" in attr3["all_colors"]

def test_hsv_histogram_and_comparison():
    """Test colour histogram calculation and comparison metric."""
    # Create synthetic solid color images
    red_img = Image.new("RGB", (200, 200), color=(220, 20, 60))
    similar_red_img = Image.new("RGB", (200, 200), color=(210, 30, 50))
    blue_img = Image.new("RGB", (200, 200), color=(20, 50, 220))

    hist_red = compute_hsv_histogram(red_img)
    hist_sim_red = compute_hsv_histogram(similar_red_img)
    hist_blue = compute_hsv_histogram(blue_img)

    assert isinstance(hist_red, np.ndarray)
    assert len(hist_red) > 0

    # Red vs Similar Red should have high similarity
    sim_red_red = compare_color_histograms(hist_red, hist_sim_red)
    # Red vs Blue should have low similarity
    sim_red_blue = compare_color_histograms(hist_red, hist_blue)

    assert 0.0 <= sim_red_red <= 1.0
    assert 0.0 <= sim_red_blue <= 1.0
    assert sim_red_red > sim_red_blue, f"Expected {sim_red_red} > {sim_red_blue}"

def test_dominant_colors_extraction():
    """Test K-means dominant color extraction."""
    img = Image.new("RGB", (100, 100), color=(201, 168, 76)) # Gold
    dominant = extract_dominant_colors(img, k=2)

    assert isinstance(dominant, list)
    assert len(dominant) > 0
    assert "hex" in dominant[0]
    assert "rgb" in dominant[0]
    assert "percentage" in dominant[0]
    assert dominant[0]["hex"].startswith("#")

def test_tool_schema_execution():
    """Test tool error handling when invalid inputs are passed."""
    res_json = find_similar_sarees.invoke({"image_url": "", "image_base64": ""})
    data = json.loads(res_json)
    assert data["status"] == "error"
