import numpy as np
import random
from config import *
from utils import *
from scipy.ndimage import label

last_war_frame = {}

def expand_and_fight(ownership, NUM_CIVS, BASE_EXPANSION_CHANCE, wars, war_intensity, frame_counter, last_expansion_frame):
    global last_war_frame
    new_ownership = ownership.copy()
    has_expanded = np.zeros(NUM_CIVS + 2, dtype=bool)

    disconnected_masks = {civ_id: get_disconnected_mask(ownership, civ_id) for civ_id in range(2, NUM_CIVS + 2)}

    for civ_id in range(2, NUM_CIVS + 2):
        civ_size = (ownership == civ_id).sum()
        expansion_chance = BASE_EXPANSION_CHANCE * (1 + civ_size / EXPANSION_SCALE_FACTOR)
        frontier_cells = get_frontier_cells(ownership, civ_id)

        if not frontier_cells:
            continue

        random.shuffle(frontier_cells)
        expansions_done = 0

        for y, x in frontier_cells:
            if expansions_done >= GROUP_PUSH_LIMIT:
                break

            neighbors = random.sample(get_neighbors(x, y), len(get_neighbors(x, y)))
            for nx, ny in neighbors:
                target = ownership[ny, nx]
                border_pair = tuple(sorted((civ_id, target)))

                # ✅ Peaceful expansion into neutral land
                if target == 1 and np.random.rand() < expansion_chance * 1.5:
                    new_ownership[ny, nx] = civ_id
                    has_expanded[civ_id] = True
                    expansions_done += 1
                    break

                # War expansion: smoother but still active
                elif target >= 2 and target != civ_id and border_pair in wars:
                    friendly_neighbors = sum(
                        ownership[ny2, nx2] == civ_id
                        for nx2, ny2 in get_neighbors(nx, ny)
                        if 0 <= ny2 < ownership.shape[0] and 0 <= nx2 < ownership.shape[1]
                    )
                
                    if friendly_neighbors == 0:
                        continue  # Don't allow completely isolated attacks
                    
                    attackers = sum(1 for pair in wars if target in pair and civ_id not in pair)
                    multi_front_penalty = 1 + (attackers * MULTI_FRONT_SCALING)
                
                    # Scale base chance by number of friendly neighbors (smooths borders)
                    neighbor_bias = 0.3 + 0.15 * (friendly_neighbors - 1)
                    base_chance = neighbor_bias * war_intensity.get(border_pair, 1.0) * multi_front_penalty
                
                    if disconnected_masks[target][ny, nx]:
                        base_chance *= 2.0
                
                    if np.random.rand() < base_chance:
                        new_ownership[ny, nx] = civ_id
                        has_expanded[civ_id] = True
                        expansions_done += 1
                
                        last_war_frame[civ_id] = frame_counter
                        last_war_frame[target] = frame_counter
                        break

    return new_ownership, has_expanded


def declare_war_if_idle(current_frame, ownership, wars, war_cooldown, peace_treaties, war_intensity):
    for civ_id in np.unique(ownership):
        if civ_id < 2: continue
        if (current_frame - war_cooldown.get(civ_id, -WAR_COOLDOWN*2)) < WAR_COOLDOWN:
            continue

        neighbors = {ownership[ny, nx] for y, x in np.argwhere(ownership == civ_id)
                     for nx, ny in get_neighbors(x, y) if ownership[ny, nx] >= 2 and ownership[ny, nx] != civ_id}

        for other in neighbors:
            pair = tuple(sorted((civ_id, other)))
            if pair not in wars and (current_frame - peace_treaties.get(pair, -PEACE_TREATY_COOLDOWN*2)) > PEACE_TREATY_COOLDOWN:
                if len(wars) < MAX_WARS:
                    wars.add(pair)
                    war_intensity[pair] = 1.0

def maybe_end_wars(frame_counter, wars, peace_treaties, war_cooldown, war_intensity):
    ended = {pair for pair in wars if np.random.rand() < PEACE_CHANCE}
    for pair in ended:
        peace_treaties[pair] = frame_counter
        war_cooldown[pair[0]] = frame_counter
        war_cooldown[pair[1]] = frame_counter
        war_intensity.pop(pair, None)
    wars.difference_update(ended)

def increase_war_intensity(wars, war_intensity):
    for pair in wars:
        war_intensity[pair] = min(war_intensity.get(pair, 1.0) + WAR_INTENSITY_GROWTH, 3.0)

def are_civs_neighbors(ownership, civ1, civ2):
    mask = (ownership == civ1)
    shifts = [np.roll(ownership, s, axis=i) for i in (1, 0) for s in (-1, 1)]
    return any(((s == civ2) & mask).any() for s in shifts)

def check_for_annexations(ownership, wars, civ_names, frame_counter, peace_treaties, war_intensity, annexation_logs, max_logs=5):
    civs = list(set(np.unique(ownership)) - {0, 1})
    for target in civs:
        total_tiles = (ownership == target).sum()
        if total_tiles == 0:
            continue

        # Count border contribution from aggressors
        occupiers = {}
        for y, x in np.argwhere(ownership == target):
            for nx, ny in get_neighbors(x, y):
                occupier = ownership[ny, nx]
                if occupier >= 2 and occupier != target:
                    occupiers[occupier] = occupiers.get(occupier, 0) + 1

        total_occupied = sum(occupiers.values())
        if total_occupied == 0 or total_occupied / total_tiles < ANNEXATION_THRESHOLD:
            continue

        # Log the annexation event
        annexation_logs.append(
            f"Frame {frame_counter}: Civ {target} annexed by civ(s): {', '.join(map(str, occupiers.keys()))}"
        )
        if len(annexation_logs) > max_logs:
            annexation_logs.pop(0)

        # Proportional land split
        proportions = {civ: count / total_occupied for civ, count in occupiers.items()}
        tiles_to_give = {civ: int(proportions[civ] * total_tiles) for civ in occupiers}
        remainder = total_tiles - sum(tiles_to_give.values())
        keys = list(tiles_to_give.keys())
        for i in range(remainder):
            tiles_to_give[keys[i % len(keys)]] += 1

        # Assign tiles using frontier expansion (no disconnected blobs)
        target_tiles = set(zip(*np.where(ownership == target)))
        available_tiles = set(target_tiles)
        reachable = {civ: set() for civ in tiles_to_give}
        assigned = {civ: 0 for civ in tiles_to_give}

        # Initialize reachable frontiers (tiles bordering the civ)
        for civ in tiles_to_give:
            for y, x in np.argwhere(ownership == civ):
                for nx, ny in get_neighbors(x, y):
                    if (ny, nx) in available_tiles:
                        reachable[civ].add((ny, nx))

        # Spread out until civs reach their tile limits or no tiles left
        while any(tiles_to_give[civ] > assigned[civ] and reachable[civ] for civ in reachable):
            for civ in reachable:
                if assigned[civ] >= tiles_to_give[civ] or not reachable[civ]:
                    continue
                chosen = reachable[civ].pop()
                if chosen not in available_tiles:
                    continue

                y, x = chosen
                ownership[y, x] = civ
                assigned[civ] += 1
                available_tiles.remove(chosen)

                for nx, ny in get_neighbors(x, y):
                    if (ny, nx) in available_tiles:
                        reachable[civ].add((ny, nx))

        # Clean up war state
        wars.difference_update({pair for pair in wars if target in pair})
        war_intensity = {k: v for k, v in war_intensity.items() if target not in k}
        peace_treaties = {k: v for k, v in peace_treaties.items() if target not in k}

        # Stop after one annexation per frame
        break

print(ANNEXATION_THRESHOLD)
