import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from config import *
from terrain import generate_terrain
from utils import get_neighbors
from civ_logic import *
from visualization import get_color_map, generate_colored_map

# --- Global histories ---
territory_history = [[] for _ in range(NUM_CIVS)]
ownership_history = []
leaderboard_history = []

# --- Name generation ---
civ_prefixes = ["Trerthustan", "Jeerbia", "Trauntium", "Mutuastan", "Myrr", "Citan", "Tyrenia", "Nostara", "Yumker", "Branth"]
civ_suffixes = ["Kingdom", "Union", "Empire", "Federation", "Dominion", "Confederacy", "Alliance", "Realm"]
name_to_color = {"The Birmingham Barony": [1.0, 0.2, 0.2, 0.5]}

def generate_civ_name():
    if np.random.rand() < 0.01:
        print("BIRMINGHAM!!!")
        return "The Birmingham Barony"
    return f"The {np.random.choice(civ_prefixes)} {np.random.choice(civ_suffixes)}"

def assign_color(name):
    if name in name_to_color:
        return name_to_color[name]
    color = np.random.rand(3,).tolist()
    name_to_color[name] = color
    return color

def generate_unique_civ_names(num_names):
    civ_names = []
    while len(civ_names) < num_names:
        name = generate_civ_name()
        if name not in civ_names:
            civ_names.append(name)
            assign_color(name)
    return civ_names

# --- Leaderboard drawing ---
def draw_leaderboard(ax, ownership, civ_names, cmap_colors, max_rows=15):
    ax.clear()
    ax.axis("off")
    civ_counts = [(i + 2, (ownership == (i + 2)).sum()) for i in range(NUM_CIVS)]
    civ_counts.sort(key=lambda x: -x[1])
    spacing = 0.93 / 15
    for rank, (civ_id, count) in enumerate(civ_counts[:max_rows]):
        name = civ_names[civ_id - 2] if civ_id - 2 < len(civ_names) else f"Civ {civ_id}"
        if civ_id < len(cmap_colors):
            r, g, b, *_ = cmap_colors[civ_id]
            rgba = (r, g, b, 0.5)
        else:
            rgba = (0.5, 0.5, 0.5, 0.5)
        ax.text(
            0.05, 0.96 - spacing * rank,
            f"#{rank+1} {name}",
            fontsize=11,
            weight='bold',
            color='white',
            bbox=dict(boxstyle="round,pad=0.4", facecolor=rgba, edgecolor='black'),
            transform=ax.transAxes,
            clip_on=True
        )
    return civ_counts

# --- Main Simulation ---
def main():
    global territory_history, ownership_history, leaderboard_history

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
    civ_names = generate_unique_civ_names(NUM_CIVS)

    # --- Setup figure ---
    fig = plt.figure(figsize=(16, 8))
    fig.canvas.manager.set_window_title('Birmingham Simulation')
    gs = fig.add_gridspec(2, 3, height_ratios=[15, 1], width_ratios=[1.5, 4, 2])

    ax_leaderboard = fig.add_subplot(gs[0, 0])
    ax_map = fig.add_subplot(gs[0, 1])
    ax_graph = fig.add_subplot(gs[0, 2])

    im = ax_map.imshow(generate_colored_map(ownership, cmap_colors, get_neighbors), animated=True)
    ax_map.axis('off')
    frame_text = ax_map.text(0.02, 0.95, '', color='white', transform=ax_map.transAxes,
                             fontsize=12, bbox=dict(facecolor='black', alpha=0.5))

    lines = [ax_graph.plot([], [], label=civ_names[i], color=cmap_colors[i + 2])[0] for i in range(NUM_CIVS)]
    ax_graph.set_xlabel("Frame")
    ax_graph.set_ylabel("Territory Size")
    ax_graph.legend(loc='upper left', fontsize=8)

    civ_label_texts = [
        ax_map.text(0, 0, '', color='black', fontsize=10, ha='center', va='center',
                    bbox=dict(facecolor='white', alpha=0.5, edgecolor='black', boxstyle='round,pad=0.3'),
                    visible=False)
        for _ in range(NUM_CIVS)
    ]

    # --- Update function ---
    def update(frame):
        nonlocal ownership, frame_counter
        alive_civs = set(np.unique(ownership)) - {0, 1}

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
            check_for_annexations(ownership, wars, civ_names, frame_counter,
                                  peace_treaties, war_intensity, annexation_logs=[])
            frame_counter += 1

        im.set_data(generate_colored_map(ownership, cmap_colors, get_neighbors))
        frame_text.set_text(f"Frame: {frame_counter}")

        for idx, civ_id in enumerate(range(2, NUM_CIVS + 2)):
            yx = np.argwhere(ownership == civ_id)
            if len(yx) == 0:
                civ_label_texts[idx].set_visible(False)
                continue
            centroid = yx.mean(axis=0)
            civ_label_texts[idx].set_position((centroid[1], centroid[0]))
            civ_label_texts[idx].set_text(civ_names[civ_id - 2])
            civ_label_texts[idx].set_bbox(dict(facecolor=cmap_colors[civ_id], alpha=0.5,
                                               edgecolor='black', boxstyle='round,pad=0.3'))
            civ_label_texts[idx].set_visible(True)

        civ_counts = [(ownership == (i + 2)).sum() for i in range(NUM_CIVS)]
        for i, count in enumerate(civ_counts):
            territory_history[i].append(count)
            lines[i].set_data(range(len(territory_history[i])), territory_history[i])

        ax_graph.set_xlim(0, max(100, frame_counter + 10))
        ax_graph.set_ylim(0, max(100, max(civ_counts) * 1.2))
        ax_graph.set_title("Territory Over Time")

        draw_leaderboard(ax_leaderboard, ownership, civ_names, cmap_colors, max_rows=15)

        # Record history every frame
        ownership_history.append(ownership.copy())

        if len(set(ownership.flatten()) - {0, 1}) <= 1:
            ani.event_source.stop()

        return [im, frame_text] + lines + civ_label_texts

    ani = animation.FuncAnimation(fig, update, interval=1, blit=False)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show(block=True)

if __name__ == "__main__":
    main()