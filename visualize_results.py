import json
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def visualize_results(image_path, json_path, graph_path, output_path):
    # Load image
    img = Image.open(image_path).convert('RGB')
    
    # Load connected squares (for highlighting)
    with open(json_path, 'r') as f:
        squares = json.load(f)
        
    # Load graph (for labels)
    with open(graph_path, 'r') as f:
        graph = json.load(f)
    
    square_size = 16
    
    # --- 1. Draw Highlights (Same as before) ---
    
    # Create a mask for the highlights
    mask = Image.new('L', img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    
    for sq in squares:
        x = sq['X']
        y = sq['Y']
        px = x * square_size
        py = y * square_size
        draw_mask.rectangle([px, py, px + square_size - 1, py + square_size - 1], fill=255)
    
    edges = mask.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda p: 255 if p > 100 else 0)
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    for sq in squares:
        x = sq['X']
        y = sq['Y']
        px = x * square_size
        py = y * square_size
        draw_overlay.rectangle([px, py, px + square_size, py + square_size], fill=(0, 0, 255, 100))

    solid_blue = Image.new('RGBA', img.size, (0, 0, 255, 255))
    overlay.paste(solid_blue, (0, 0), edges)
    
    img = img.convert('RGBA')
    result = Image.alpha_composite(img, overlay).convert('RGB')
    
    # --- 2. Draw Labels ---
    
    draw = ImageDraw.Draw(result)
    
    # Try to load a font, otherwise use default
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
        
    for node in graph:
        name = node['name']
        center = node['center']
        
        # Calculate pixel center
        cx = center['X'] * square_size + square_size // 2
        cy = center['Y'] * square_size + square_size // 2
        
        # Draw text centered
        # Get text size
        bbox = draw.textbbox((0, 0), name, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        tx = cx - text_w // 2
        ty = cy - text_h // 2
        
        # Draw black outline for text readability
        outline_range = 2
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                 draw.text((tx + ox, ty + oy), name, font=font, fill="black")
        
        # Draw white text
        draw.text((tx, ty), name, font=font, fill="white")

    result.save(output_path)
    print(f"Saved visualization to {output_path}")

if __name__ == "__main__":
    visualize_results("image.png", "connected_squares.json", "graph.json", "output.png")
