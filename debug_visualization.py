"""
Create a single mosaic (PNG) showing the pipeline steps for each input.
We'll show:
  1) Original image
  2) leftover mask overlay
  3) leftover ratio text

We stack them horizontally or in a grid for multiple images.
"""

import cv2
import numpy as np


def create_debug_mosaic(debug_images, max_width=1200):
    """
    Creates a single mosaic image that lines up each sample horizontally.

    debug_images: list of tuples => (original_bgr, leftover_mask, leftover_ratio, filename)

    We will produce for each item a small panel with:
      - the original
      - an overlay of leftover in red
      - some text about leftover_ratio

    Then we horizontally concatenate all panels. If it becomes too wide, we might do 2 rows, etc.
    For simplicity, let's do a single horizontal strip, and scale down if needed.
    """
    panels = []
    for (original_bgr, leftover_mask, leftover_ratio, filename) in debug_images:
        panel = create_single_panel(original_bgr, leftover_mask, leftover_ratio, filename)
        panels.append(panel)

    # Concatenate horizontally
    mosaic = np.hstack(panels) if len(panels) > 1 else panels[0]

    # If mosaic is too wide, we can downscale
    height, width = mosaic.shape[:2]
    if width > max_width:
        scale = max_width / float(width)
        new_size = (int(width * scale), int(height * scale))
        mosaic = cv2.resize(mosaic, new_size, interpolation=cv2.INTER_AREA)

    return mosaic


def create_single_panel(original_bgr, leftover_mask, leftover_ratio, filename):
    """
    Build a single panel that includes:
      - The original BGR image (small)
      - Red overlay where leftover_mask=255
      - Text label with leftover_ratio
    We'll stack vertically or side-by-side in the same panel.
    """
    h, w = original_bgr.shape[:2]

    # Make an overlay
    overlay = original_bgr.copy()
    red = (0, 0, 255)
    overlay[leftover_mask == 255] = red

    # We'll place them top: original, bottom: overlay
    # Then we can add text about leftover_ratio
    top_label = put_text_on_image(original_bgr, f"Original: {filename}", (10, 30))
    bottom_label = put_text_on_image(overlay,
                                     f"Leftover: ratio={leftover_ratio:.3f}",
                                     (10, 30))

    # Stack vertically
    panel = np.vstack([top_label, bottom_label])
    return panel


def put_text_on_image(image_bgr, text, coord, font_scale=0.9, color=(255, 255, 255)):
    """
    Return a copy of image_bgr with 'text' drawn at position 'coord'.
    """
    output = image_bgr.copy()
    cv2.putText(output, text, coord, cv2.FONT_HERSHEY_SIMPLEX,
                font_scale, color, 2, cv2.LINE_AA)
    return output