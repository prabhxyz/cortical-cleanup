**Project: Cortical Cleanup Quality Assessment from Pupil-Segmented Images**  
---

## Overview

This project provides a **fully automated pipeline** to measure how “clean” the lens capsule is after the **irrigation/aspiration (I/A) phase** of cataract surgery, based on images in which only the pupil (or capsular area) is visible against a black background. We assume these images already have everything outside the pupil masked out, so we can focus on the internal capsule region alone.

**Key Steps**  
1. **Input Images**: The user places one or more `.png` files in a folder such as `/input/`. Each image shows the pupil region of a postoperative eye on a black background.  
2. **Residual Lens Material Detection**: We convert each image to grayscale and apply robust thresholding (Otsu’s method) _only within the pupil region_. Any bright or whitish patches in that region are flagged as “leftover” cortical matter, which indicates incomplete cortical cleanup.  
3. **Morphological Filtering**: We apply a small morphological open (or similar operation) to remove small specks or noise, ensuring more reliable leftover detection.  
4. **Cleanup Ratio**: We compute a **leftover ratio** = (number of leftover pixels) / (number of pupil pixels). This ratio quantifies how much potential cortical debris remains.  
5. **CSV Report**: The pipeline writes out a `cleanup_scores.csv` file with one row per image, listing `(filename, leftover_ratio, cleanup_score)`. The score is a qualitative label (e.g. “Excellent,” “Moderate,” “Significant”) based on user-defined thresholds.  
6. **Debug Visualization**: We also generate a single PNG (`debug_summary.png`) showing each image’s pipeline results. This includes the original frame, the leftover overlay (highlighting detected debris), and the computed leftover ratio.

---

## How the System Works

### Input & Processing
1. **Folder Scanning**  
   The system scans a specified input directory (e.g., `/input`) for any `.png` images. Each image represents the eye’s internal view (pupil/capsular area) on a black background.

2. **Bright Region Detection**  
   - We first **convert the image to grayscale**.  
   - We identify the “pupil area” as any region that isn’t pure black (since the rest of the image is typically black).  
   - Next, we apply **Otsu’s threshold** _only_ within the pupil region. Otsu’s method automatically determines an optimal threshold value to isolate bright features from a potentially darker background. This step is crucial because it adapts to various lighting conditions or reflection levels in the surgical footage.

3. **Morphological Open**  
   - Bright thresholding can produce small noisy spots, especially due to specular reflections or sensor noise.  
   - We apply a **morphological open** operation (using a small elliptical kernel) to remove these tiny specks, ensuring that only more substantial patches of leftover are kept.

4. **Leftover Ratio**  
   - After cleaning the thresholded mask, we count how many pixels remain bright (“leftover” pixels).  
   - We also count the total number of pupil-area pixels (anything above a small intensity threshold in the original grayscale).  
   - **Leftover Ratio = (Leftover Pixels) / (Total Pupil Pixels)**. A ratio close to 0 means the pupil region appears largely clear (little debris); a high ratio indicates many bright leftover patches.

5. **Scoring & Output**  
   - Based on this ratio, we derive a qualitative score—for instance, “< 2% leftover → Excellent,” “2–5% → Moderate,” “> 5% → Significant.” These thresholds can be tuned.  
   - We store each image’s results in `cleanup_scores.csv`, a simple CSV containing columns:  
     ```
     filename, leftover_ratio, cleanup_score
     ```

---

## Robust Methodology

- **Black Mask Isolation**: By starting with pupil-segmented images (only the internal area visible on black), we eliminate irrelevant background or surgical instruments.  
- **Otsu Thresholding**: Otsu’s method adapts automatically to images of different brightness levels, reflection intensities, or lighting setups. We do not rely on a fixed threshold that might break under varying conditions.  
- **Morphological Operations**: This “open” step (erode + dilate) is key to filtering spurious reflections or single-pixel noise.  
- **Ratio Computation**: Measuring leftover as a fraction of total pupil area yields a consistent, interpretable metric across different image sizes or zoom levels.  
- **Qualitative Scoring**: Translating the numeric ratio into categories (“Excellent/Moderate/Significant”) provides an immediate sense of urgency or surgical result quality.

---

## Debug Summary Visualization

When the pipeline completes, it produces a **debug mosaic** at `"/output/debug_summary.png"`. Below is an example snippet of how it looks:

![Debug Summary](/output/debug_summary.png)

In this screenshot:

- **Left Column**: A case labeled “clean.png”. The leftover ratio is about 0.090 (9%). The top image is the original frame (dark), and the bottom shows a red overlay highlighting detected leftover. You can see only a few small red spots, so the leftover ratio remains relatively low.  
- **Right Column**: A case labeled “not_clean.png”. The leftover ratio is 0.916 (91.6%). The bright area is quite large, indicating abundant debris. This is visually confirmed by the large red patch at the bottom image, covering most of the pupil region.

From this PNG, one can **visually confirm** if the pipeline’s detected leftover corresponds to actual lens debris or if it’s misidentifying reflection or instrumentation. If the ratio is too high or low, you can adjust threshold or morphological parameters accordingly.

---

## Getting Started

1. **Install Requirements**  
   - Python 3.x  
   - OpenCV (e.g. `pip install opencv-python`)  
   - NumPy (`pip install numpy`)  

2. **Run the Project**  
   - Place your `.png` images in a folder, for example:  
     ```
     /input/frame_000001.png
     /input/frame_000002.png
     ```
   - Invoke:  
     ```
     python main.py --input_dir input --output_dir output
     ```
   - The script will:  
     1. Process each image.  
     2. Write `cleanup_scores.csv` into `/output/cleanup_scores.csv`.  
     3. Generate a `debug_summary.png` side‐by‐side mosaic in `/output/debug_summary.png`.

3. **Interpret the Results**  
   - The CSV’s `leftover_ratio` helps quantify how thorough the cleanup is.  
   - The `cleanup_score` label (e.g. “Excellent,” “Moderate,” or “Significant”) quickly flags whether a case might need re-examination.  
   - The `debug_summary.png` visually verifies or troubleshoots the detection process.

---

## Conclusion

This project **robustly** measures cataract cortical cleanup by leveraging:

- **Pupil-segmented inputs**: to isolate the region of interest.  
- **Dynamic thresholding + morphological filtering**: to reliably detect leftover lens debris across varying lighting/contrast conditions.  
- **Quantitative ratio & CSV logging**: enabling easy data tracking and integration with other surgical analytics.  
- **Debug imagery**: allowing direct visual confirmation of detection quality and facilitating quick parameter tuning.

This synergy of classical image processing techniques provides a **simple yet powerful** way to assess postoperative lens clarity, offering immediate feedback for surgical outcome quality and potential PCO risk considerations.