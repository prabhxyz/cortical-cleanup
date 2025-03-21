"""
Entry point for the cortical cleanup assessment project.
It scans a folder of pupil-segmented images, applies leftover detection,
computes a cleanup ratio, and generates a CSV plus a debug visualization.
"""

import os
import argparse
import glob
import cv2

from leftover_detection import detect_leftover
from scoring import compute_cleanup_score
from debug_visualization import create_debug_mosaic


def parse_args():
    parser = argparse.ArgumentParser(description="Assess cortical cleanup from pupil-segmented images.")
    parser.add_argument('--input_dir', type=str, default='/input',
                        help="Path to folder with one or more PNG images of the segmented pupil region.")
    parser.add_argument('--output_dir', type=str, default='output_results',
                        help="Output folder for CSV, debug images, etc.")
    return parser.parse_args()


def main():
    args = parse_args()

    # Make sure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)

    # Collect all PNG images from input_dir
    input_pattern = os.path.join(args.input_dir, '*.png')
    image_paths = sorted(glob.glob(input_pattern))

    if len(image_paths) == 0:
        print(f"No PNG images found in {args.input_dir}. Exiting.")
        return

    print(f"Found {len(image_paths)} images in {args.input_dir}.")

    # We'll keep track of results in a list of dicts for CSV writing later
    results = []

    # For debug visualization: store step images
    debug_images = []  # list of (original_bgr, leftover_mask_color, leftover_ratio, filename)

    for img_path in image_paths:
        filename = os.path.basename(img_path)
        print(f"Processing {filename}...")

        # Load the pupil-segmented image
        # It is presumably black outside the pupil region
        original_bgr = cv2.imread(img_path, cv2.IMREAD_COLOR)
        if original_bgr is None:
            print(f"Warning: could not read {img_path}, skipping.")
            continue

        # 1) Detect leftover (bright/hazy) areas
        # leftover_mask = white regions, leftover_ratio = fraction of leftover in pupil
        leftover_mask, leftover_ratio = detect_leftover(original_bgr)

        # 2) Convert ratio to a more interpretable numeric or textual score
        # (Optionally, you could define thresholds like "Clean", "Moderate", "Significant")
        cleanup_score = compute_cleanup_score(leftover_ratio)

        # Save results in our results list
        results.append({
            'filename': filename,
            'leftover_ratio': leftover_ratio,
            'cleanup_score': cleanup_score
        })

        # We'll also store images for debug mosaic
        debug_images.append((original_bgr, leftover_mask, leftover_ratio, filename))

    # Write CSV with leftover info
    csv_path = os.path.join(args.output_dir, 'cleanup_scores.csv')
    write_csv(csv_path, results)
    print(f"Saved CSV results to {csv_path}")

    # Generate a single mosaic image showing each file's pipeline steps
    if len(debug_images) > 0:
        debug_mosaic = create_debug_mosaic(debug_images)
        dbg_out_path = os.path.join(args.output_dir, 'debug_summary.png')
        cv2.imwrite(dbg_out_path, debug_mosaic)
        print(f"Saved debug mosaic to {dbg_out_path}")


def write_csv(csv_path, results):
    """
    Write a CSV with columns: filename, leftover_ratio, cleanup_score
    """
    import csv
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "leftover_ratio", "cleanup_score"])
        for row in results:
            writer.writerow([row['filename'], f"{row['leftover_ratio']:.4f}", row['cleanup_score']])


if __name__ == "__main__":
    main()
