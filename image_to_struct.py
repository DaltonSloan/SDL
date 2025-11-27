from PIL import Image
import sys

def convert_image(image_path, square_size=16):
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    pixels = img.load()

    grid_w = width // square_size
    grid_h = height // square_size

    print("package main")
    print()
    print("var GeneratedImage = CompressedImage{")
    print(f"\tOriginalWidth:  {width},")
    print(f"\tOriginalHeight: {height},")
    print(f"\tSquareSize:     {square_size},")
    print(f"\tGridWidth:      {grid_w},")
    print(f"\tGridHeight:     {grid_h},")
    print("\tSquares: [][]Pixel{")

    for y in range(grid_h):
        print("\t\t{")
        for x in range(grid_w):
            # Sample the center of the square
            sx = x * square_size + square_size // 2
            sy = y * square_size + square_size // 2
            
            # Bounds check just in case
            if sx >= width: sx = width - 1
            if sy >= height: sy = height - 1

            r, g, b = pixels[sx, sy]
            print(f"\t\t\t{{R: {r}, G: {g}, B: {b}}},")
        print("\t\t},")
    print("\t},")
    print("}")

if __name__ == "__main__":
    convert_image("image.png")
