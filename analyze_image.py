from PIL import Image
import sys
from collections import Counter

def detect_grid_size(image_path):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    pixels = img.load()

    # Analyze a few rows and columns to find the most common run length
    row_run_lengths = []
    for y in [height // 4, height // 2, 3 * height // 4]:
        current_run = 1
        for x in range(1, width):
            # Check if pixel matches previous pixel (with some tolerance)
            p1 = pixels[x, y]
            p2 = pixels[x-1, y]
            if abs(p1[0]-p2[0]) < 10 and abs(p1[1]-p2[1]) < 10 and abs(p1[2]-p2[2]) < 10:
                current_run += 1
            else:
                if current_run > 1:
                    row_run_lengths.append(current_run)
                current_run = 1
        if current_run > 1:
            row_run_lengths.append(current_run)

    col_run_lengths = []
    for x in [width // 4, width // 2, 3 * width // 4]:
        current_run = 1
        for y in range(1, height):
            p1 = pixels[x, y]
            p2 = pixels[x, y-1]
            if abs(p1[0]-p2[0]) < 10 and abs(p1[1]-p2[1]) < 10 and abs(p1[2]-p2[2]) < 10:
                current_run += 1
            else:
                if current_run > 1:
                    col_run_lengths.append(current_run)
                current_run = 1
        if current_run > 1:
            col_run_lengths.append(current_run)

    # Find most common run lengths
    common_rows = Counter(row_run_lengths).most_common(5)
    common_cols = Counter(col_run_lengths).most_common(5)
    
    print(f"Image Dimensions: {width}x{height}")
    print(f"Common Row Run Lengths: {common_rows}")
    print(f"Common Col Run Lengths: {common_cols}")

    # Estimate square size (taking the most common significant run length)
    # We filter out very small runs which might be noise or borders
    significant_rows = [k for k, v in common_rows if k > 5]
    significant_cols = [k for k, v in common_cols if k > 5]
    
    est_w = significant_rows[0] if significant_rows else 1
    est_h = significant_cols[0] if significant_cols else 1
    
    print(f"Estimated Square Size: {est_w}x{est_h}")
    
    # Calculate grid dimensions
    grid_w = width // est_w
    grid_h = height // est_h
    print(f"Estimated Grid: {grid_w}x{grid_h}")

if __name__ == "__main__":
    detect_grid_size("image.png")
