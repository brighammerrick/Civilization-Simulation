import numpy as np
from scipy.ndimage import label
from config import GRID_SIZE

def get_neighbors(x, y):
    return [(x + dx, y + dy) for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
            if 0 <= x + dx < GRID_SIZE and 0 <= y + dy < GRID_SIZE]

def get_frontier_cells(ownership, civ_id):
    civ_cells = np.argwhere(ownership == civ_id)
    return [(y, x) for y, x in civ_cells if any(ownership[ny, nx] != civ_id and ownership[ny, nx] != 0
            for nx, ny in get_neighbors(x, y))]

def get_disconnected_mask(ownership, civ_id):
    """Returns a boolean mask where disconnected civ territory is True"""
    civ_mask = (ownership == civ_id)
    labeled, num = label(civ_mask)

    if num <= 1:
        return np.zeros_like(ownership, dtype=bool)

    # Find the largest connected region
    sizes = [(labeled == i).sum() for i in range(1, num + 1)]
    largest_label = np.argmax(sizes) + 1

    # Everything not in the largest region is disconnected
    return (labeled != largest_label) & civ_mask

def count_alive_civs(ownership, num_civs):
    return sum((ownership == (i + 2)).any() for i in range(num_civs))