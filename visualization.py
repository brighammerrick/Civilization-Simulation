
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from config import GRID_SIZE, NUM_CIVS

def get_color_map():
    water_color = [0.2, 0.4, 1.0, 1.0]
    land_color = [0.8, 0.8, 0.7, 1.0]
    civ_colors = [
        [0.91, 0.30, 0.24, 0.5], [0.98, 0.77, 0.18, 0.5],
        [0.18, 0.80, 0.44, 0.5], [0.60, 0.40, 0.70, 0.5],
        [0.85, 0.33, 0.55, 0.5], [0.44, 0.62, 0.82, 0.5],
        [0.99, 0.60, 0.40, 0.5], [0.35, 0.70, 0.90, 0.5],
        [0.55, 0.40, 0.15, 0.5], [0.90, 0.85, 0.50, 0.5],
        [0.50, 0.75, 0.25, 0.5], [0.90, 0.45, 0.75, 0.5],
        [0.65, 0.85, 0.90, 0.5], [0.95, 0.95, 0.95, 0.5],
        [0.30, 0.50, 0.90, 0.5], [0.75, 0.25, 0.25, 0.5],
        [0.25, 0.75, 0.25, 0.5], [0.65, 0.65, 0.20, 0.5],
        [0.70, 0.40, 0.90, 0.5], [0.35, 0.85, 0.75, 0.5]
    ]
    return [water_color, land_color] + civ_colors[:NUM_CIVS]

def generate_colored_map(ownership, cmap_colors, get_neighbors):
    image = np.zeros((GRID_SIZE, GRID_SIZE, 4))
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            tile = ownership[y, x]
            color = cmap_colors[tile] if tile < len(cmap_colors) else [0.8, 0.8, 0.7, 1.0]
            is_border = any(ownership[ny, nx] != tile for nx, ny in get_neighbors(x, y))

            if tile == 0:  # water
                alpha = 0.3 if is_border else 1.0
            else:
                alpha = 1.0 if is_border else 0.5

            image[y, x] = color[:3] + [alpha]
    return image
