# Civilization Simulation
![Static Badge](https://img.shields.io/badge/Python-blue?style=for-the-badge&logo=python&logoColor=yellow)

This project is a 2D grid-based simulation of civilizations evolving over time. Watch as civilizations are born, expand their territories, declare war on their neighbors, and vie for dominance on a procedurally generated map. The simulation is visualized in real-time using Matplotlib, showing the map, a live leaderboard, and a graph of territory size over time.

## Features

-   **Procedural Terrain Generation:** Creates unique island and continent formations for each simulation using Perlin noise.
-   **Dynamic Civilization Logic:**
    -   Civilizations expand into neutral land and fight over borders.
    -   Expansion rate is influenced by the current size of the civilization.
    -   Complex warfare system where civilizations can declare war, with war intensity growing over time.
    -   Civilizations can form peace treaties, introducing cooldowns before new conflicts can arise.
    -   Annexation mechanics allow dominant powers to absorb defeated civilizations.
-   **Live Visualization:**
    -   A real-time map displaying civilization territories with distinct colors and highlighted borders.
    -   An auto-updating leaderboard ranking civilizations by the amount of territory they control.
    -   A line graph plotting the history of each civilization's territory size.
-   **Highly Configurable:** Almost every aspect of the simulation, from map generation to civilization behavior, can be tweaked in the `config.py` file.

## Getting Started

### Prerequisites

You need Python 3 and the following libraries:

-   `numpy`
-   `matplotlib`
-   `pnoise`
-   `scipy`

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/brighammerrick/civilization-simulation.git
    cd civilization-simulation
    ```

2.  Install the required packages:
    ```bash
    pip install numpy matplotlib pnoise scipy
    ```

### Running the Simulation

To start the simulation, simply run the `__main__.py` script:

```bash
python .
```

A Matplotlib window will open, displaying the simulation.

## Configuration

You can customize the simulation by modifying the variables in `config.py`.

### Map Initialization
-   `GRID_SIZE`: The width and height of the simulation map.
-   `NUM_CIVS`: The number of civilizations to start with.
-   `SEED`: The seed for the procedural map generation. Set to `None` for a random seed on each run.

### Map Generation
-   `SCALE`: Controls the zoom level of the Perlin noise map.
-   `OCTAVES`: The number of noise layers, affecting complexity.
-   `PERSISTENCE`: The roughness of the terrain.
-   `LACUNARITY`: The level of detail in the terrain.
-   `LAND_THRESHOLD`: The water level. A higher value results in less land.

### Civilization Logic
-   `BASE_EXPANSION_CHANCE`: The base probability for a civilization to expand into an adjacent neutral tile.
-   `EXPANSION_SCALE_FACTOR`: A divisor that scales the expansion chance based on civilization size.
-   `GROUP_PUSH_LIMIT`: The maximum number of tiles a single civilization can expand in one frame.
-   `WAR_INTENSITY_GROWTH`: How quickly war intensity increases each frame, affecting conflict aggression.
-   `SPEED_MULTIPLIER`: The number of simulation ticks to perform per visual update, effectively speeding up the simulation.
-   `WAR_COOLDOWN`: The number of frames a civilization must wait after a war ends before declaring a new one.
-   `PEACE_TREATY_COOLDOWN`: The number of frames a peace treaty lasts between two specific civilizations.
-   `PEACE_CHANCE`: The per-frame probability of an ongoing war ending in a peace treaty.
-   `MAX_WARS`: The maximum number of concurrent wars allowed in the simulation.
-   `ANNEXATION_THRESHOLD`: The percentage of a civilization's border that must be controlled by enemies before it can be annexed.

## Code Structure

-   `__main__.py`: The entry point for the application. Initializes the simulation, sets up the Matplotlib visualization, and contains the main update loop.
-   `civ_logic.py`: Governs the core behaviors of civilizations, including peaceful expansion, warfare mechanics, war declarations, peace treaties, and annexation.
-   `terrain.py`: Responsible for generating the 2D terrain for the simulation using Perlin noise.
-   `config.py`: A centralized file for all tunable simulation parameters, allowing for easy experimentation.
-   `utils.py`: A collection of utility functions, such as finding neighboring tiles and identifying disconnected parts of a civilization's territory.
-   `visualization.py`: Contains functions for generating the colored map image and managing the color palette for civilizations.
