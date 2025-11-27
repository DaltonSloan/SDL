import json
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from collections import deque
import os

# --- Configuration ---
SQUARE_SIZE = 16

# --- Data Structures ---

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x}, {self.y})"

class GreenBlock:
    def __init__(self, id, points):
        self.id = id
        self.name = ""
        self.points = points # List of Point
        self.center = self._calculate_center()
        
    def _calculate_center(self):
        if not self.points:
            return Point(0, 0)
        min_x = min(p.x for p in self.points)
        max_x = max(p.x for p in self.points)
        min_y = min(p.y for p in self.points)
        max_y = max(p.y for p in self.points)
        return Point((min_x + max_x) // 2, (min_y + max_y) // 2)

# --- Helper Functions ---

def is_green(r, g, b):
    return g > r and g > b

def is_red(r, g, b):
    return r > g and r > b

def generate_name(n):
    # A, B, ..., Z, AA, AB, ...
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < 26:
        return letters[n]
    return letters[n // 26 - 1] + letters[n % 26]

# --- Main Logic ---

def solve_puzzle(image_path):
    print(f"Loading {image_path}...")
    try:
        img = Image.open(image_path).convert('RGB')
    except FileNotFoundError:
        print(f"Error: {image_path} not found.")
        return

    # Derive output paths based on input image location
    input_dir = os.path.dirname(image_path)
    json_output_path = os.path.join(input_dir, "graph.json")
    image_output_path = os.path.join(input_dir, "output.png")

    width, height = img.size
    pixels = img.load()
    
    grid_w = width // SQUARE_SIZE
    grid_h = height // SQUARE_SIZE
    
    print(f"Grid size: {grid_w}x{grid_h}")
    
    # 1. Parse Grid
    # We store the grid as a list of lists of (r, g, b) tuples
    grid = [[(0,0,0) for _ in range(grid_w)] for _ in range(grid_h)]
    
    for y in range(grid_h):
        for x in range(grid_w):
            sx = x * SQUARE_SIZE + SQUARE_SIZE // 2
            sy = y * SQUARE_SIZE + SQUARE_SIZE // 2
            if sx >= width: sx = width - 1
            if sy >= height: sy = height - 1
            grid[y][x] = pixels[sx, sy]

    # 2. Identify Green Blocks
    visited = set()
    blocks = []
    dirs = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    for y in range(grid_h):
        for x in range(grid_w):
            p = Point(x, y)
            if p in visited:
                continue
            
            r, g, b = grid[y][x]
            if is_green(r, g, b):
                # Found new block
                block_points = []
                queue = deque([p])
                visited.add(p)
                
                while queue:
                    curr = queue.popleft()
                    block_points.append(curr)
                    
                    for dx, dy in dirs:
                        nx, ny = curr.x + dx, curr.y + dy
                        
                        if 0 <= nx < grid_w and 0 <= ny < grid_h:
                            np = Point(nx, ny)
                            if np not in visited:
                                nr, ng, nb = grid[ny][nx]
                                if is_green(nr, ng, nb):
                                    visited.add(np)
                                    queue.append(np)
                
                blocks.append(GreenBlock(len(blocks), block_points))

    print(f"Found {len(blocks)} green blocks.")

    # 3. Sort Blocks (Top-Left to Bottom-Right)
    # Sort by Y then X of center
    blocks.sort(key=lambda b: (b.center.y, b.center.x))
    
    # 4. Assign Names
    for i, block in enumerate(blocks):
        block.id = i
        block.name = generate_name(i)

    # 5. Find Connections
    # Map point to block ID
    point_to_block = {}
    for block in blocks:
        for p in block.points:
            point_to_block[p] = block.id
            
    graph_output = []
    
    for block in blocks:
        connections = set()
        
        # BFS from boundary Red squares
        queue = deque()
        visited_red = set()
        
        # Initialize with adjacent reds
        for p in block.points:
            for dx, dy in dirs:
                nx, ny = p.x + dx, p.y + dy
                if 0 <= nx < grid_w and 0 <= ny < grid_h:
                    np = Point(nx, ny)
                    nr, ng, nb = grid[ny][nx]
                    if is_red(nr, ng, nb) and np not in visited_red:
                        visited_red.add(np)
                        queue.append(np)
        
        while queue:
            curr = queue.popleft()
            
            for dx, dy in dirs:
                nx, ny = curr.x + dx, curr.y + dy
                if 0 <= nx < grid_w and 0 <= ny < grid_h:
                    np = Point(nx, ny)
                    nr, ng, nb = grid[ny][nx]
                    
                    # Hit a Green Square?
                    if is_green(nr, ng, nb):
                        if np in point_to_block:
                            target_id = point_to_block[np]
                            if target_id != block.id:
                                connections.add(target_id)
                        continue # Don't traverse through Green
                    
                    # Hit a Red Square?
                    if is_red(nr, ng, nb) and np not in visited_red:
                        visited_red.add(np)
                        queue.append(np)

        # Filter connections (One Way: Target > Source)
        valid_connections = []
        for target_id in connections:
            if target_id > block.id:
                valid_connections.append(blocks[target_id].name)
        
        valid_connections.sort()
        
        graph_output.append({
            "name": block.name,
            "connections": valid_connections,
            "center": {"X": block.center.x, "Y": block.center.y}
        })

    # 6. Output JSON
    with open(json_output_path, 'w') as f:
        json.dump(graph_output, f, indent=2)
    print(f"Saved graph to {json_output_path}")

    # 7. Visualize
    visualize(img, blocks, graph_output, image_output_path)

def visualize(img, blocks, graph_data, output_path):
    # Create mask for highlights
    mask = Image.new('L', img.size, 0)
    draw_mask = ImageDraw.Draw(mask)
    
    for block in blocks:
        for p in block.points:
            px = p.x * SQUARE_SIZE
            py = p.y * SQUARE_SIZE
            draw_mask.rectangle([px, py, px + SQUARE_SIZE - 1, py + SQUARE_SIZE - 1], fill=255)
            
    edges = mask.filter(ImageFilter.FIND_EDGES)
    edges = edges.point(lambda p: 255 if p > 100 else 0)
    
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    # Fill blocks
    for block in blocks:
        for p in block.points:
            px = p.x * SQUARE_SIZE
            py = p.y * SQUARE_SIZE
            draw_overlay.rectangle([px, py, px + SQUARE_SIZE, py + SQUARE_SIZE], fill=(0, 0, 255, 100))
            
    # Draw edges
    solid_blue = Image.new('RGBA', img.size, (0, 0, 255, 255))
    overlay.paste(solid_blue, (0, 0), edges)
    
    # Composite
    img = img.convert('RGBA')
    result = Image.alpha_composite(img, overlay).convert('RGB')
    
    # Draw Labels
    draw = ImageDraw.Draw(result)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 40)
    except IOError:
        # Fallback to default if custom font not found
        # Load a larger default font if possible, or just default
        try:
             font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
             font = ImageFont.load_default()

    for node in graph_data:
        name = node['name']
        center = node['center']
        
        cx = center['X'] * SQUARE_SIZE + SQUARE_SIZE // 2
        cy = center['Y'] * SQUARE_SIZE + SQUARE_SIZE // 2
        
        bbox = draw.textbbox((0, 0), name, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        tx = cx - text_w // 2
        ty = cy - text_h // 2
        
        # Outline
        outline_range = 2
        for ox in range(-outline_range, outline_range + 1):
            for oy in range(-outline_range, outline_range + 1):
                 draw.text((tx + ox, ty + oy), name, font=font, fill="black")
        
        draw.text((tx, ty), name, font=font, fill="white")
        
    result.save(output_path)
    print(f"Saved visualization to {output_path}")

import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Solve the Green/Red square puzzle.")
    parser.add_argument("image_path", help="Path to the input image")
    args = parser.parse_args()
    
    solve_puzzle(args.image_path)
