
#!/usr/bin/env python3
"""
TWIST Lab - Cooperative Multi-Robot Mapping
Dual-SLAM Offline Registration and Map Fusion

Robot A: Leader
Robot B: Follower

Inputs:
    robot_a_final_map.pgm / .yaml
    robot_b_final_map.pgm / .yaml

Outputs:
    dual_slam_final_alignment.png
    dual_slam_fused_preview.png
    dual_slam_fused_map.pgm
    dual_slam_fused_map.yaml

The output is experimental until alignment is validated.
No ROS topics, TF, or running SLAM nodes are modified.
"""

import os
import math
import cv2
import yaml
import numpy as np
from scipy.ndimage import distance_transform_edt

HOME = "/home/wheeltec"
SCALE = 0.05

# Previous physical estimate. Used only to rank ambiguous matches.
INITIAL_ANGLE = -77.42
INITIAL_TRANSLATION = (-0.428, -0.436)

# Robot separation gives an approximate constraint, not ground truth.
MAX_TRANSLATION_DEVIATION = 4.0

# Search canvas: 24 x 24 meters.
SIZE = 480
CENTER = SIZE // 2

MIN_OVERLAP = 1500
MIN_OBSTACLES = 80


def load_map(name):
    path = os.path.join(HOME, name)

    with open(path + ".yaml", "r") as f:
        meta = yaml.safe_load(f)

    image = cv2.imread(
        path + ".pgm", cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise RuntimeError("Cannot read " + path + ".pgm")

    resolution = float(meta["resolution"])
    ox, oy, yaw = map(float, meta["origin"])

    # ROS occupancy grids have positive Y upward.
    # Image files have positive Y downward.
    image = np.flipud(image)

    grid = np.full(image.shape, -1, np.int16)

    grid[image >= 205] = 0
    grid[image <= 100] = 100

    return {
        "grid": grid,
        "resolution": resolution,
        "origin": (ox, oy),
        "yaw": yaw,
    }


def rasterize(data):
    grid = data["grid"]
    h, w = grid.shape

    yy, xx = np.indices((h, w))
    known = grid >= 0

    x = (xx[known] + 0.5) * data["resolution"]
    y = (yy[known] + 0.5) * data["resolution"]

    yaw = data["yaw"]
    c, s = math.cos(yaw), math.sin(yaw)

    wx = data["origin"][0] + c*x - s*y
    wy = data["origin"][1] + s*x + c*y

    px = np.rint(wx / SCALE + CENTER).astype(int)
    py = np.rint(CENTER - wy / SCALE).astype(int)

    valid = (
        (px >= 0) & (px < SIZE) &
        (py >= 0) & (py < SIZE)
    )

    out = np.full((SIZE, SIZE), -1, np.int16)

    values = grid[known][valid]
    px, py = px[valid], py[valid]

    out[py[values == 0], px[values == 0]] = 0
    out[py[values == 100], px[values == 100]] = 100

    return out


def warp_grid(grid, angle, tx, ty):
    # Transform Robot B world coordinates into Robot A coordinates.
    # Image coordinates have Y inverted.
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)

    matrix = np.array([
        [c, s, CENTER*(1-c-s) + tx/SCALE],
        [-s, c, CENTER*(1+s-c) - ty/SCALE],
    ], dtype=np.float32)

    # Nearest-neighbor warp preserves occupancy categories.
    return cv2.warpAffine(
        grid.astype(np.int16),
        matrix,
        (SIZE, SIZE),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=-1,
    )


def angle_difference(a, b):
    return abs((a - b + 180) % 360 - 180)


def evaluate(a, b, dist_a, near_a):
    known_a = a >= 0
    known_b = b >= 0

    overlap = known_a & known_b
    overlap_n = int(np.count_nonzero(overlap))

    if overlap_n < MIN_OVERLAP:
        return -1e6, 0, 0, overlap_n

    occupied_b = b == 100
    occupied_a = a == 100

    n_a = int(np.count_nonzero(occupied_a & known_b))
    n_b = int(np.count_nonzero(occupied_b & known_a))

    if n_a < MIN_OBSTACLES or n_b < MIN_OBSTACLES:
        return -1e6, 0, 0, overlap_n

    # Distance to nearest A obstacle, in cells.
    distances = dist_a[occupied_b & known_a]

    # Reward B obstacles close to A obstacles.
    proximity = np.exp(
        -np.minimum(distances, 20.0) / 2.0
    ).mean()

    # Penalize B obstacles in confidently free A space.
    conflict_b = (
        occupied_b & (a == 0) & (~near_a)
    )

    # Penalize A obstacles in confidently free B space.
    near_b = cv2.dilate(
        occupied_b.astype(np.uint8),
        np.ones((5, 5), np.uint8)
    ).astype(bool)

    conflict_a = (
        occupied_a & (b == 0) & (~near_b)
    )

    conflicts = (
        np.count_nonzero(conflict_a) +
        np.count_nonzero(conflict_b)
    )

    total = n_a + n_b
    conflict_ratio = conflicts / total

    # Avoid preferring alignments with tiny overlapping regions.
    coverage = min(overlap_n / 8000.0, 1.0)

    score = (
        2.0 * proximity
        - 1.5 * conflict_ratio
        + 0.25 * coverage
    )

    return score, proximity, conflict_ratio, overlap_n


def search(a, b):
    occupied_a = a == 100

    dist_a = distance_transform_edt(~occupied_a)

    near_a = cv2.dilate(
        occupied_a.astype(np.uint8),
        np.ones((5, 5), np.uint8)
    ).astype(bool)

    best = None

    def test(angle, tx, ty):
        warped = warp_grid(b, angle, tx, ty)

        score, proximity, conflict, overlap = evaluate(
            a, warped, dist_a, near_a
        )

        # Weak prior, not a hard constraint.
        angular_penalty = (
            0.0005 *
            angle_difference(angle, INITIAL_ANGLE)
        )

        translation_penalty = 0.005 * math.hypot(
            tx - INITIAL_TRANSLATION[0],
            ty - INITIAL_TRANSLATION[1]
        )

        score -= angular_penalty + translation_penalty

        return {
            "score": score,
            "angle": angle,
            "tx": tx,
            "ty": ty,
            "proximity": proximity,
            "conflict": conflict,
            "overlap": overlap,
        }

    # Coarse search over full rotation and broad translation.
    # Translation is relative to the existing map origins.
    print("Stage 1: coarse registration...", flush=True)

    candidates = []

    for angle in range(-180, 180, 15):
        for tx in np.arange(-3.0, 3.01, 0.5):
            for ty in np.arange(-3.0, 3.01, 0.5):
                result = test(angle, float(tx), float(ty))
                candidates.append(result)

    candidates.sort(
        key=lambda item: item["score"], reverse=True
    )

    # Refine multiple candidates to reduce local-minimum risk.
    print("Stage 2: fine registration...", flush=True)

    refined = []

    for candidate in candidates[:5]:
        for da in range(-10, 11, 2):
            for dx in np.arange(-0.3, 0.31, 0.1):
                for dy in np.arange(-0.3, 0.31, 0.1):
                    result = test(
                        candidate["angle"] + da,
                        candidate["tx"] + float(dx),
                        candidate["ty"] + float(dy)
                    )
                    refined.append(result)

    refined.sort(
        key=lambda item: item["score"], reverse=True
    )

    best = refined[0]

    print("Stage 3: final refinement...", flush=True)

    for da in np.arange(-2.0, 2.01, 0.5):
        for dx in np.arange(-0.10, 0.101, 0.05):
            for dy in np.arange(-0.10, 0.101, 0.05):
                result = test(
                    best["angle"] + float(da),
                    best["tx"] + float(dx),
                    best["ty"] + float(dy)
                )

                if result["score"] > best["score"]:
                    best = result

    return best


def make_overlay(a, b):
    image = np.full(
        (SIZE, SIZE, 3), 125, np.uint8
    )

    occ_a = a == 100
    occ_b = b == 100

    image[(a == 0) | (b == 0)] = (255, 255, 255)

    # Red = A, Blue = B, Purple = both.
    image[occ_a & ~occ_b] = (0, 0, 255)
    image[occ_b & ~occ_a] = (255, 0, 0)
    image[occ_a & occ_b] = (255, 0, 255)

    conflicts = (
        (occ_a & (b == 0)) |
        (occ_b & (a == 0))
    )
    image[conflicts] = (0, 200, 0)

    return image


def fuse(a, b):
    # Conservative policy: contradictory occupied/free
    # observations remain unknown until reviewed.
    merged = np.full(a.shape, -1, np.int16)

    known_a = a >= 0
    known_b = b >= 0

    merged[known_a & ~known_b] = a[known_a & ~known_b]
    merged[known_b & ~known_a] = b[known_b & ~known_a]

    agree_free = (a == 0) & (b == 0)
    agree_occ = (a == 100) & (b == 100)

    merged[agree_free] = 0
    merged[agree_occ] = 100

    # Do not silently resolve conflicts.
    return merged


def save_ros_map(grid):
    path = os.path.join(HOME, "dual_slam_fused_map")

    # ROS map_saver convention:
    # occupied = black, free = white, unknown = gray.
    image = np.full(grid.shape, 205, np.uint8)
    image[grid == 0] = 254
    image[grid == 100] = 0

    # Convert world-up grid back to image-down coordinates.
    image = np.flipud(image)

    if not cv2.imwrite(path + ".pgm", image):
        raise RuntimeError("Failed to save fused PGM")

    metadata = {
        "image": "dual_slam_fused_map.pgm",
        "mode": "trinary",
        "resolution": SCALE,
        "origin": [
            -CENTER * SCALE,
            -CENTER * SCALE,
            0.0
        ],
        "negate": 0,
        "occupied_thresh": 0.65,
        "free_thresh": 0.25,
    }

    with open(path + ".yaml", "w") as f:
        yaml.safe_dump(
            metadata, f, sort_keys=False
        )

    return path


def main():
    print("Loading saved Robot A and Robot B maps...",
          flush=True)

    a_data = load_map("robot_a_final_map")
    b_data = load_map("robot_b_final_map")

    a = rasterize(a_data)
    b = rasterize(b_data)

    print("Searching for matching walls...", flush=True)

    best = search(a, b)

    if best["score"] <= -1e5:
        raise RuntimeError(
            "No usable registration candidate found"
        )

    aligned_b = warp_grid(
        b,
        best["angle"],
        best["tx"],
        best["ty"]
    )

    overlay = make_overlay(a, aligned_b)

    overlay_path = os.path.join(
        HOME, "dual_slam_final_alignment.png"
    )

    if not cv2.imwrite(overlay_path, overlay):
        raise RuntimeError("Failed to save overlay")

    merged = fuse(a, aligned_b)
    map_path = save_ros_map(merged)

    preview = np.full(
        merged.shape, 205, np.uint8
    )
    preview[merged == 0] = 255
    preview[merged == 100] = 0

    preview_path = os.path.join(
        HOME, "dual_slam_fused_preview.png"
    )

    cv2.imwrite(preview_path, preview)

    print("\n========== FINAL RESULTS ==========")
    print(f"Rotation B -> A: {best['angle']:.2f} degrees")
    print(
        f"Translation B -> A: "
        f"({best['tx']:.3f}, {best['ty']:.3f}) m"
    )
    print(f"Obstacle proximity: {best['proximity']:.4f}")
    print(f"Conflict ratio: {best['conflict']:.4f}")
    print(f"Known overlap: {best['overlap']} cells")
    print(f"Registration score: {best['score']:.4f}")
    print("\nFiles:")
    print(overlay_path)
    print(preview_path)
    print(map_path + ".pgm")
    print(map_path + ".yaml")
    print(
        "\nEXPERIMENTAL fusion only. "
        "Inspect alignment before navigation use."
    )


if __name__ == "__main__":
    main()
