"""
Module for detecting bright/hazy leftover cortical matter inside the pupil area.
We assume the input is a BGR image with black background and a pupil region in the center.
"""

import cv2
import numpy as np


def detect_leftover(image_bgr):
    """
    Detect leftover lens cortex in a pupil-segmented image (black background, pupil in center).

    Steps:
    1) Convert to grayscale.
    2) Identify the pupil region (non-black).
    3) Threshold bright areas in that region (indicating leftover cortex).
    4) Morphological filtering to reduce noise.
    5) Calculate leftover ratio = (# leftover pixels) / (# pupil pixels).

    Returns:
      leftover_mask (uint8): same size as input, with leftover areas marked as 255, else 0
      leftover_ratio (float): fraction of pupil area that is leftover
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    # Identify pupil region = everything that is not black
    # We'll define black as near zero intensity
    # Make a mask of where the pixel is > some small threshold (e.g. 10)
    pupil_mask = (gray > 10).astype(np.uint8)

    # If the pupil is small or doesn't exist, leftover ratio is 0 by definition
    pupil_area = np.count_nonzero(pupil_mask)
    if pupil_area == 0:
        leftover_mask = np.zeros_like(gray, dtype=np.uint8)
        leftover_ratio = 0.0
        return leftover_mask, leftover_ratio

    # Within the pupil region, find bright areas
    # Use Otsu or a fixed threshold. We'll try Otsu for adaptiveness.
    # BUT first let's mask out everything that's not pupil, to avoid background messing up Otsu
    masked_gray = gray.copy()
    masked_gray[pupil_mask == 0] = 0  # so background is definitely black

    # Otsu threshold
    # The second retval '_' is the threshold value found by Otsu
    _, leftover_binary = cv2.threshold(masked_gray, 0, 255,
                                       cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # leftover_binary now has bright leftover areas as 255, plus possibly noise
    # Let's ensure we only consider pixels inside the pupil mask
    leftover_binary[pupil_mask == 0] = 0

    # Morphological filtering to reduce small specks
    # We'll do a small open operation
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    leftover_clean = cv2.morphologyEx(leftover_binary, cv2.MORPH_OPEN, kernel)

    # leftover_clean is now a refined mask of leftover cortical matter
    leftover_area = np.count_nonzero(leftover_clean)
    leftover_ratio = leftover_area / float(pupil_area)

    return leftover_clean, leftover_ratio
