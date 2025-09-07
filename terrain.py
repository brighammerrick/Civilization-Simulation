import numpy as np
from noise import pnoise2
from config import *

def generate_terrain(seed=None):
    if seed is None:
        seed = np.random.randint(0, 100)
    print("Using seed:", seed)

    x = np.linspace(0, GRID_SIZE / SCALE, GRID_SIZE, endpoint=False)
    y = np.linspace(0, GRID_SIZE / SCALE, GRID_SIZE, endpoint=False)
    xx, yy = np.meshgrid(x, y)

    terrain = np.vectorize(lambda a, b: pnoise2(
        a, b, octaves=OCTAVES, persistence=PERSISTENCE,
        lacunarity=LACUNARITY, repeatx=1024, repeaty=1024, base=seed
    ))(xx, yy)

    terrain_norm = (terrain - terrain.min()) / (terrain.max() - terrain.min())
    return terrain_norm > LAND_THRESHOLD, seed
