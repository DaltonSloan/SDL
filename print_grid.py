from PIL import Image
import sys

def print_grid(image_path, square_size=16):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    pixels = img.load()

    grid_w = width // square_size
    grid_h = height // square_size

    for y in range(grid_h):
        line = ""
        for x in range(grid_w):
            sx = x * square_size + square_size // 2
            sy = y * square_size + square_size // 2
            
            if sx >= width: sx = width - 1
            if sy >= height: sy = height - 1

            r, g, b = pixels[sx, sy]
            
            if g > r and g > b:
                line += "G"
            elif r > g and r > b:
                line += "R"
            elif b > r and b > g:
                line += "B" # Blue or White/Background
            else:
                line += "." # White/Gray
        print(line)

if __name__ == "__main__":
    print_grid("image.png")
