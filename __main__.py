import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from config import *
from terrain import generate_terrain
from utils import get_neighbors
from civ_logic import *
from visualization import get_color_map, generate_colored_map

def main():
    terrain_bool, seed = generate_terrain(SEED)
    ownership = np.where(terrain_bool, 1, 0)
    cmap_colors = get_color_map()

    land_indices = np.argwhere(terrain_bool)
    np.random.shuffle(land_indices)
    civ_positions = land_indices[:NUM_CIVS]
    for i, (y, x) in enumerate(civ_positions):
        ownership[y, x] = i + 2

    frame_counter = 0
    wars = set()
    war_intensity = {}
    peace_treaties = {}
    war_cooldown = {}
    last_expansion_frame = np.zeros(NUM_CIVS + 2, dtype=int)
    civ_names = [f"Civ {i + 1}" for i in range(NUM_CIVS)]
    territory_history = [[] for _ in range(NUM_CIVS)]
    annexation_logs = []
    MAX_LOGS = 5

    fig, (ax_map, ax_graph) = plt.subplots(1, 2, figsize=(14, 7))
    im = ax_map.imshow(generate_colored_map(ownership, cmap_colors, get_neighbors), animated=True)
    ax_map.axis('off')
    frame_text = ax_map.text(0.02, 0.95, '', color='white', transform=ax_map.transAxes,
                             fontsize=12, bbox=dict(facecolor='black', alpha=0.5))

    ax_graph.set_title("Leaderboard")
    ax_graph.axis('off')

    def update(frame):
        nonlocal ownership, frame_counter

        for _ in range(SPEED_MULTIPLIER):
            increase_war_intensity(wars, war_intensity)
            ownership[:], expanded = expand_and_fight(
                ownership, NUM_CIVS, BASE_EXPANSION_CHANCE,
                wars, war_intensity, frame_counter, last_expansion_frame)
            for civ_id in range(2, NUM_CIVS + 2):
                if expanded[civ_id]:
                    last_expansion_frame[civ_id] = frame_counter
            declare_war_if_idle(frame_counter, ownership, wars, war_cooldown, peace_treaties, war_intensity)
            maybe_end_wars(frame_counter, wars, peace_treaties, war_cooldown, war_intensity)
            check_for_annexations(ownership, wars, civ_names, frame_counter, peace_treaties, war_intensity, annexation_logs, MAX_LOGS)
            frame_counter += 1

        im.set_data(generate_colored_map(ownership, cmap_colors, get_neighbors))
        frame_text.set_text(f"Frame: {frame_counter}")

        # Draw Leaderboard
        ax_graph.clear()
        ax_graph.set_title("Leaderboard")
        ax_graph.axis('off')

        civs = list(set(np.unique(ownership)) - {0, 1})
        civ_sizes = [(civ, (ownership == civ).sum()) for civ in civs]
        civ_sizes.sort(key=lambda x: x[1], reverse=True)

        box_height = 0.08
        for i, (civ, size) in enumerate(civ_sizes):
            y = 1 - (i + 1) * box_height
            color = cmap_colors[civ]
            rect = plt.Rectangle((0, y), 1, box_height * 0.8, color=color)
            ax_graph.add_patch(rect)
            name = civ_names[civ - 2]
            ax_graph.text(0.02, y + box_height * 0.4, f"{name} — Territory: {size}",
                          va='center', ha='left', fontsize=10, color='white', weight='bold')

        # Annexation logs textbox at bottom center
        logs_text = "\n".join(annexation_logs[-MAX_LOGS:])
        # Remove old annex log texts
        fig.texts = [t for t in fig.texts if t.get_gid() != 'annex_log']
        fig.text(0.5, 0.02, logs_text, ha='center', va='bottom', fontsize=9, color='white',
                 bbox=dict(facecolor='black', alpha=0.7, boxstyle='round,pad=0.5'), gid='annex_log')

        # Stop animation if only one civ left
        if len(set(ownership.flatten()) - {0, 1}) <= 1:
            ani.event_source.stop()

        return [im, frame_text]

    ani = animation.FuncAnimation(fig, update, interval=100, blit=False, cache_frame_data=False)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
