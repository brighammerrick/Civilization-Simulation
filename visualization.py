import numpy as np
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
        [0.65, 0.85, 0.90, 0.5], [0.70, 0.70, 0.70, 0.5],
        [0.30, 0.50, 0.90, 0.5], [0.40, 0.40, 0.40, 0.5],
        [0.25, 0.75, 0.25, 0.5], [0.65, 0.65, 0.20, 0.5],
        [0.70, 0.40, 0.90, 0.5], [0.35, 0.85, 0.75, 0.5]
    ]
    return [water_color, land_color] + civ_colors[:NUM_CIVS]

def generate_colored_map(ownership, cmap_colors, get_neighbors, civ_names=None, name_to_color=None):
    image = np.zeros((GRID_SIZE, GRID_SIZE, 4))
    for y in range(GRID_SIZE):
        for x in range(GRID_SIZE):
            tile = ownership[y, x]

            # Determine base color first
            if tile < 2:
                # Water or neutral, keep as before
                color = cmap_colors[tile] if tile < len(cmap_colors) else [0.8, 0.8, 0.7, 1.0]
            else:
                # Check if civ name has a custom color override
                if civ_names and name_to_color and tile - 2 < len(civ_names):
                    civ_name = civ_names[tile - 2]
                    if civ_name in name_to_color:
                        color = name_to_color[civ_name]
                        # Ensure it has alpha, add 1.0 if only RGB given
                        if len(color) == 3:
                            color = (*color, 1.0)
                    else:
                        color = cmap_colors[tile]
                else:
                    color = cmap_colors[tile]

            # Determine alpha based on border status
            is_border = any(ownership[ny, nx] != tile for nx, ny in get_neighbors(x, y))

            if tile == 0:  # water
                alpha = 0.3 if is_border else 1.0
            else:
                alpha = 1.0 if is_border else 0.5

            # Set RGBA with proper alpha override
            image[y, x] = list(color[:3]) + [alpha]

    return image

