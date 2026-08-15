"""
Colour analysis and histogram matching module for fine-grained saree retrieval.
Extracts HSV colour distributions and computes perceptual colour similarity.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Union, Tuple, Dict, List

# HSV Bins for robust color representation
HUE_BINS = 30       # 0 to 180 in OpenCV
SAT_BINS = 16       # 0 to 256
VAL_BINS = 8        # 0 to 256

def pil_to_cv2(image: Image.Image) -> np.ndarray:
    """Convert PIL image to OpenCV BGR format."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    np_img = np.array(image)
    return cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

def extract_saree_focus_region(cv2_bgr: np.ndarray) -> np.ndarray:
    """
    Center-crop/focus on the core garment area to reduce background influence.
    Typically sarees are displayed prominently in the center-to-lower portion.
    """
    h, w = cv2_bgr.shape[:2]
    # Crop central 80% width and 75% height
    top = int(h * 0.10)
    bottom = int(h * 0.90)
    left = int(w * 0.10)
    right = int(w * 0.90)
    return cv2_bgr[top:bottom, left:right]

def compute_hsv_histogram(image: Union[Image.Image, np.ndarray], focus_crop: bool = True) -> np.ndarray:
    """
    Compute a composite perceptual colour descriptor combining CIE L*a*b* colour moments
    (mean, std) and 2D Hue-Saturation colour distribution.
    Returns a 1D float32 numpy array.
    """
    if isinstance(image, Image.Image):
        cv2_img = pil_to_cv2(image)
    else:
        cv2_img = image

    if focus_crop:
        cv2_img = extract_saree_focus_region(cv2_img)

    # 1. CIE L*a*b* Perceptual Colour Space
    lab = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2LAB).astype(np.float32)
    mean_lab = np.mean(lab, axis=(0, 1))  # 3 values [L, a, b]
    std_lab = np.std(lab, axis=(0, 1))    # 3 values

    # 2. 2D Hue-Saturation Distribution (12 H bins x 8 S bins = 96 bins)
    hsv = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2HSV)
    hist_2d = cv2.calcHist([hsv], [0, 1], None, [12, 8], [0, 180, 0, 256]).flatten()
    total_pix = np.sum(hist_2d)
    if total_pix > 0:
        hist_2d = hist_2d / total_pix

    # Concatenate [mean_lab (3), std_lab (3), hist_2d (96)] -> 102 values
    descriptor = np.concatenate([mean_lab, std_lab, hist_2d]).astype(np.float32)
    return descriptor

def extract_dominant_colors(image: Union[Image.Image, np.ndarray], k: int = 4) -> List[Dict[str, Union[str, float]]]:
    """
    Extract top-k dominant colors using K-Means clustering in Lab / RGB space.
    Useful for explaining color matches to the user.
    """
    if isinstance(image, Image.Image):
        cv2_img = pil_to_cv2(image)
    else:
        cv2_img = image

    cv2_img = extract_saree_focus_region(cv2_img)
    # Downscale for fast clustering
    small = cv2.resize(cv2_img, (100, 100))
    rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB).reshape(-1, 3).astype(np.float32)

    # K-means criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, centers = cv2.kmeans(rgb, k, None, criteria, 3, flags)

    counts = np.bincount(labels.flatten())
    total_pixels = len(labels)

    dominant = []
    for count, center in zip(counts, centers):
        r, g, b = [int(c) for c in center]
        hex_code = f"#{r:02x}{g:02x}{b:02x}"
        pct = float(count / total_pixels)
        dominant.append({"hex": hex_code, "rgb": [r, g, b], "percentage": round(pct, 3)})

    dominant.sort(key=lambda x: x["percentage"], reverse=True)
    return dominant

def compare_color_histograms(query_desc: np.ndarray, candidate_desc: np.ndarray) -> float:
    """
    Compare two colour descriptors using CIE Delta-E perceptual distance and
    Bhattacharyya distribution overlap.
    Returns a normalized similarity score in [0.0, 1.0].
    """
    # 1. Delta-E Perceptual Distance on Lab moments
    mean_q, mean_c = query_desc[:3], candidate_desc[:3]
    std_q, std_c = query_desc[3:6], candidate_desc[3:6]

    delta_e = np.linalg.norm(mean_q - mean_c) + 0.5 * np.linalg.norm(std_q - std_c)
    # Exponential decay mapped to [0, 1]
    lab_similarity = np.exp(-delta_e / 38.0)

    # 2. Bhattacharyya Coefficient on HS histograms
    h_q, h_c = query_desc[6:], candidate_desc[6:]
    bhattacharyya_coeff = np.sum(np.sqrt(np.maximum(0, h_q) * np.maximum(0, h_c)))

    # Composite colour similarity
    similarity = float(0.6 * lab_similarity + 0.4 * bhattacharyya_coeff)
    return float(np.clip(similarity, 0.0, 1.0))
