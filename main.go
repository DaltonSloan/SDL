package main

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
)

// Pixel represents a single pixel with RGB values.
// We assume 8-bit color depth for simplicity, but int is fine too.
type Pixel struct {
	R int
	G int
	B int
}

// CompressedImage represents the grid of squares.
type CompressedImage struct {
	OriginalWidth  int
	OriginalHeight int
	SquareSize     int
	GridWidth      int // Number of squares horizontally
	GridHeight     int // Number of squares vertically
	Squares        [][]Pixel
}

// isGreen checks if a square is considered Green.
func isGreen(p Pixel) bool {
	return p.G > p.R
}

// isRed checks if a square is considered Red.
func isRed(p Pixel) bool {
	return p.R > p.G
}

// Point represents a coordinate in the grid.
type Point struct {
	X, Y int
}

// FindConnectedGreenSquares finds all Green squares that are part of a connected component
// of Green and Red squares, where the component contains at least two Green squares.
func FindConnectedGreenSquares(img CompressedImage) []Point {
	visited := make(map[Point]bool)
	var result []Point

	// Directions for 4-way connectivity: up, down, left, right
	dirs := []Point{{0, 1}, {0, -1}, {1, 0}, {-1, 0}}

	for y := 0; y < img.GridHeight; y++ {
		for x := 0; x < img.GridWidth; x++ {
			start := Point{x, y}
			if visited[start] {
				continue
			}

			// We only care about components starting with Green or Red.
			// Actually, we can just iterate and if we hit a Green or Red that hasn't been visited,
			// we explore the whole component.
			pixel := img.Squares[y][x]
			if !isGreen(pixel) && !isRed(pixel) {
				continue
			}

			// Start BFS/DFS
			component := []Point{}
			greenCount := 0
			queue := []Point{start}
			visited[start] = true

			for len(queue) > 0 {
				curr := queue[0]
				queue = queue[1:]
				component = append(component, curr)

				currPixel := img.Squares[curr.Y][curr.X]
				if isGreen(currPixel) {
					greenCount++
				}

				for _, d := range dirs {
					next := Point{curr.X + d.X, curr.Y + d.Y}

					// Check bounds
					if next.X < 0 || next.X >= img.GridWidth || next.Y < 0 || next.Y >= img.GridHeight {
						continue
					}

					if visited[next] {
						continue
					}

					nextPixel := img.Squares[next.Y][next.X]
					if isGreen(nextPixel) || isRed(nextPixel) {
						visited[next] = true
						queue = append(queue, next)
					}
				}
			}

			// If this component has more than 1 Green square, add all its Green squares to the result.
			// The prompt asks for "what squares (marked as green) are connected to other green squares".
			// So we filter the component for Green squares.
			if greenCount > 1 {
				for _, p := range component {
					if isGreen(img.Squares[p.Y][p.X]) {
						result = append(result, p)
					}
				}
			}
		}
	}

	return result
}

func main() {
	// Test Case 1: 2 Green squares connected by a Red square
	// G - R - G
	img1 := CompressedImage{
		GridWidth:  3,
		GridHeight: 1,
		Squares: [][]Pixel{
			{
				{R: 0, G: 255, B: 0},   // Green
				{R: 255, G: 0, B: 0},   // Red
				{R: 0, G: 255, B: 0},   // Green
			},
		},
	}
	res1 := FindConnectedGreenSquares(img1)
	fmt.Printf("Test 1 (G-R-G): Found %d green squares (expected 2)\n", len(res1))
	for _, p := range res1 {
		fmt.Printf("  (%d, %d)\n", p.X, p.Y)
	}

	// Test Case 2: Isolated Green square
	// G   R
	img2 := CompressedImage{
		GridWidth:  2,
		GridHeight: 1,
		Squares: [][]Pixel{
			{
				{R: 0, G: 255, B: 0},   // Green
				{R: 0, G: 0, B: 255},   // Blue (neither)
			},
		},
	}
	res2 := FindConnectedGreenSquares(img2)
	fmt.Printf("Test 2 (Isolated G): Found %d green squares (expected 0)\n", len(res2))

    // Test Case 3: Green connected to Red, but no other Green
    // G - R
    img3 := CompressedImage{
        GridWidth: 2,
        GridHeight: 1,
        Squares: [][]Pixel{
            {
                {R: 0, G: 255, B: 0}, // Green
                {R: 255, G: 0, B: 0}, // Red
            },
        },
    }
    res3 := FindConnectedGreenSquares(img3)
    fmt.Printf("Test 3 (G-R): Found %d green squares (expected 0)\n", len(res3))

    // Test Case 4: Complex shape
    // G R G
    // R G R
    img4 := CompressedImage{
        GridWidth: 3,
        GridHeight: 2,
        Squares: [][]Pixel{
            {
                {R: 0, G: 255, B: 0}, {R: 255, G: 0, B: 0}, {R: 0, G: 255, B: 0},
            },
            {
                {R: 255, G: 0, B: 0}, {R: 0, G: 255, B: 0}, {R: 255, G: 0, B: 0},
            },
        },
    }
    res4 := FindConnectedGreenSquares(img4)
    fmt.Printf("Test 4 (Complex): Found %d green squares (expected 3)\n", len(res4))

	// Test Case 5: Generated Image
	res5 := FindConnectedGreenSquares(GeneratedImage)
	fmt.Printf("Test 5 (Generated Image): Found %d green squares\n", len(res5))

	// Export results to JSON for visualization
	file, _ := os.Create("connected_squares.json")
	defer file.Close()
	encoder := json.NewEncoder(file)
	encoder.Encode(res5)

	// Generate Connectivity Graph
	GenerateConnectivityGraph(GeneratedImage)
}

// GreenBlock represents a connected component of Green squares.
type GreenBlock struct {
	ID     int     `json:"id"`
	Name   string  `json:"name"`
	Points []Point `json:"-"` // Don't export points to graph JSON to keep it clean
	Center Point   `json:"center"`
}

// GraphNode represents a node in the output graph.
type GraphNode struct {
	Name        string   `json:"name"`
	Connections []string `json:"connections"`
	Center      Point    `json:"center"`
}

// GenerateConnectivityGraph identifies Green Blocks, sorts them, finds connections, and exports to JSON.
func GenerateConnectivityGraph(img CompressedImage) {
	// ... (existing code for identifying blocks) ...
	// 1. Identify distinct Green Blocks
	visited := make(map[Point]bool)
	var blocks []*GreenBlock
	dirs := []Point{{0, 1}, {0, -1}, {1, 0}, {-1, 0}}

	for y := 0; y < img.GridHeight; y++ {
		for x := 0; x < img.GridWidth; x++ {
			p := Point{x, y}
			if visited[p] {
				continue
			}
			if isGreen(img.Squares[y][x]) {
				// Found a new block
				block := &GreenBlock{Points: []Point{}}
				queue := []Point{p}
				visited[p] = true
				
				minX, minY := x, y
				maxX, maxY := x, y

				for len(queue) > 0 {
					curr := queue[0]
					queue = queue[1:]
					block.Points = append(block.Points, curr)

					if curr.X < minX { minX = curr.X }
					if curr.Y < minY { minY = curr.Y }
					if curr.X > maxX { maxX = curr.X }
					if curr.Y > maxY { maxY = curr.Y }

					for _, d := range dirs {
						next := Point{curr.X + d.X, curr.Y + d.Y}
						if next.X < 0 || next.X >= img.GridWidth || next.Y < 0 || next.Y >= img.GridHeight {
							continue
						}
						if visited[next] {
							continue
						}
						if isGreen(img.Squares[next.Y][next.X]) {
							visited[next] = true
							queue = append(queue, next)
						}
					}
				}
				// Calculate approximate center for sorting
				block.Center = Point{(minX + maxX) / 2, (minY + maxY) / 2}
				blocks = append(blocks, block)
			}
		}
	}

	// 2. Sort Green Blocks (Top-Left to Bottom-Right)
	// We sort primarily by Y, then by X.
	sort.Slice(blocks, func(i, j int) bool {
		if blocks[i].Center.Y != blocks[j].Center.Y {
			return blocks[i].Center.Y < blocks[j].Center.Y
		}
		return blocks[i].Center.X < blocks[j].Center.X
	})

	// 3. Assign Names
	for i, block := range blocks {
		block.ID = i
		block.Name = generateName(i)
	}

	// 4. Find Connections via Red Paths
	// Map point to block ID for easy lookup
	pointToBlock := make(map[Point]int)
	for _, b := range blocks {
		for _, p := range b.Points {
			pointToBlock[p] = b.ID
		}
	}

	graph := make([]GraphNode, len(blocks))
	for i, block := range blocks {
		graph[i] = GraphNode{
			Name:        block.Name,
			Connections: []string{},
			Center:      block.Center,
		}
		
		// Find all reachable blocks from this block via Red paths
		reachable := make(map[int]bool)
		
		// Start BFS from all boundary Red squares
		queue := []Point{}
		visitedRed := make(map[Point]bool)

		// Initialize queue with adjacent Red squares
		for _, p := range block.Points {
			for _, d := range dirs {
				next := Point{p.X + d.X, p.Y + d.Y}
				if next.X < 0 || next.X >= img.GridWidth || next.Y < 0 || next.Y >= img.GridHeight {
					continue
				}
				// If it's Red and not visited
				if isRed(img.Squares[next.Y][next.X]) && !visitedRed[next] {
					visitedRed[next] = true
					queue = append(queue, next)
				}
			}
		}

		// BFS through Red squares
		for len(queue) > 0 {
			curr := queue[0]
			queue = queue[1:]

			for _, d := range dirs {
				next := Point{curr.X + d.X, curr.Y + d.Y}
				if next.X < 0 || next.X >= img.GridWidth || next.Y < 0 || next.Y >= img.GridHeight {
					continue
				}

				// If we hit a Green square
				if isGreen(img.Squares[next.Y][next.X]) {
					if targetID, ok := pointToBlock[next]; ok {
						if targetID != block.ID {
							reachable[targetID] = true
						}
					}
					continue // Don't traverse through Green
				}

				// If we hit a Red square
				if isRed(img.Squares[next.Y][next.X]) && !visitedRed[next] {
					visitedRed[next] = true
					queue = append(queue, next)
				}
			}
		}

		// Add connections (One Way: only if Target > Source)
		for targetID := range reachable {
			if targetID > block.ID {
				graph[i].Connections = append(graph[i].Connections, blocks[targetID].Name)
			}
		}
		// Sort connections for deterministic output
		sort.Strings(graph[i].Connections)
	}

	// 5. Output to JSON
	file, _ := os.Create("graph.json")
	defer file.Close()
	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	encoder.Encode(graph)
	fmt.Printf("Generated connectivity graph with %d blocks to graph.json\n", len(blocks))
}

func generateName(n int) string {
	// A, B, ..., Z, AA, AB, ...
	const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	if n < 26 {
		return string(letters[n])
	}
	return string(letters[n/26-1]) + string(letters[n%26])
}
