
import numpy as np
from config import GRID_SIZE

def get_neighbors(x, y):
    return [(x + dx, y + dy) for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]
            if 0 <= x + dx < GRID_SIZE and 0 <= y + dy < GRID_SIZE]

def get_frontier_cells(ownership, civ_id):
    civ_cells = np.argwhere(ownership == civ_id)
    return [(y, x) for y, x in civ_cells if any(ownership[ny, nx] != civ_id and ownership[ny, nx] != 0
            for nx, ny in get_neighbors(x, y))]
