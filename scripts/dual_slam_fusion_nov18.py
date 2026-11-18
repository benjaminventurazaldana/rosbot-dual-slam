
#!/usr/bin/env python3
"""
TWIST Lab - Cooperative Multi-Robot Mapping
Dual-SLAM Offline Registration and Map Fusion - Version 2

Robot A: Leader
Robot B: Follower

Changes from Version 1:
- Preserves the original registration algorithm.
- Uses inverse-mapped nearest-neighbor occupancy sampling.
- Closes small free-space raster gaps after alignment.
- Keeps occupied cells from being overwritten by free cells.
- Saves all Version 2 outputs separately.

Experimental map fusion only.
Does not publish TF or modify running ROS 2 SLAM nodes.
"""

import os
import math
import cv2
import yaml
import numpy as np
from scipy.ndimage import distance_transform_edt

HOME = "/home/wheeltec"
SCALE = 0.05
SIZE = 480
CENTER = SIZE // 2

INITIAL_ANGLE = 0.0
INITIAL_TRANSLATION = (0.0, 0.7366)

MIN_OVERLAP = 1500
MIN_OBSTACLES = 80

PREFIX = "dual_slam_nov18"


def load_map(name):
    path = os.path.join(HOME, name)

    with open(path + ".yaml", "r") as f:
        meta = yaml.safe_load(f)

    image = cv2.imread(
        path + ".pgm",
        cv2.IMREAD_GRAYSCALE
    )

    if image is None:
        raise RuntimeError("Cannot read " + path + ".pgm")

    image = np.flipud(image)

    grid = np.full(image.shape, -1, np.int16)
    grid[image >= 205] = 0
    grid[image <= 100] = 100

    return {
        "grid": grid,
        "resolution": float(meta["resolution"]),
        "origin": tuple(map(float, meta["origin"][:2])),
        "yaw": float(meta["origin"][2])
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
    px = px[valid]
    py = py[valid]

    out[py[values == 0], px[values == 0]] = 0
    out[py[values == 100], px[values == 100]] = 100

    return out


def transform_matrix(angle, tx, ty):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)

    return np.array([
        [c, s, CENTER*(1-c-s) + tx/SCALE],
        [-s, c, CENTER*(1+s-c) - ty/SCALE]
    ], dtype=np.float32)


def warp_grid(grid, angle, tx, ty):
    matrix = transform_matrix(angle, tx, ty)

    return cv2.warpAffine(
        grid.astype(np.int16),
        matrix,
        (SIZE, SIZE),
        flags=cv2.INTER_NEAREST,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=-1
    )


def clean_grid(grid):
    """
    Close one-cell gaps in known free space.

    Unknown regions are not globally converted to free.
    Occupied cells always take precedence.

    This is a visualization/fusion cleanup, not a
    substitute for validated map registration.
    """
    occupied = (grid == 100).astype(np.uint8)
    free = (grid == 0).astype(np.uint8)
    known = (grid >= 0).astype(np.uint8)

    kernel = np.ones((3, 3), np.uint8)

    closed_free = cv2.morphologyEx(
        free,
        cv2.MORPH_CLOSE,
        kernel
    )

    # Only fill gaps immediately surrounded by known
    # mapped cells. Preserve larger unknown areas.
    neighborhood = cv2.filter2D(
        known.astype(np.float32),
        -1,
        kernel.astype(np.float32),
        borderType=cv2.BORDER_CONSTANT
    )

    small_gaps = (
        (closed_free > 0) &
        (known == 0) &
        (neighborhood >= 7)
    )

    result = grid.copy()
    result[small_gaps] = 0
    result[occupied > 0] = 100

    return result


def angle_difference(a, b):
    return abs((a - b + 180) % 360 - 180)


def evaluate(a, b, dist_a, near_a):
    known_a = a >= 0
    known_b = b >= 0

    overlap_n = int(np.count_nonzero(
        known_a & known_b
    ))

    if overlap_n < MIN_OVERLAP:
        return -1e6, 0, 0, overlap_n

    occupied_a = a == 100
    occupied_b = b == 100

    n_a = int(np.count_nonzero(
        occupied_a & known_b
    ))

    n_b = int(np.count_nonzero(
        occupied_b & known_a
    ))

    if n_a < MIN_OBSTACLES or n_b < MIN_OBSTACLES:
        return -1e6, 0, 0, overlap_n

    distances = dist_a[occupied_b & known_a]

    proximity = np.exp(
        -np.minimum(distances, 20.0) / 2.0
    ).mean()

    conflict_b = (
        occupied_b & (a == 0) & (~near_a)
    )

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

    conflict_ratio = conflicts / (n_a + n_b)
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

    def test(angle, tx, ty):
        warped = warp_grid(b, angle, tx, ty)

        score, proximity, conflict, overlap = evaluate(
            a, warped, dist_a, near_a
        )

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
            "overlap": overlap
        }

    print("Stage 1: coarse registration...", flush=True)

    candidates = []

    for angle in range(-180, 180, 15):
        for tx in np.arange(-3.0, 3.01, 0.5):
            for ty in np.arange(-3.0, 3.01, 0.5):
                candidates.append(
                    test(angle, float(tx), float(ty))
                )

    candidates.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    print("Stage 2: fine registration...", flush=True)

    refined = []

    for candidate in candidates[:5]:
        for da in range(-10, 11, 2):
            for dx in np.arange(-0.3, 0.31, 0.1):
                for dy in np.arange(-0.3, 0.31, 0.1):
                    refined.append(test(
                        candidate["angle"] + da,
                        candidate["tx"] + float(dx),
                        candidate["ty"] + float(dy)
                    ))

    refined.sort(
        key=lambda item: item["score"],
        reverse=True
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
        (SIZE, SIZE, 3),
        125,
        np.uint8
    )

    occ_a = a == 100
    occ_b = b == 100

    image[(a == 0) | (b == 0)] = (255, 255, 255)

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
    merged = np.full(a.shape, -1, np.int16)

    known_a = a >= 0
    known_b = b >= 0

    only_a = known_a & ~known_b
    only_b = known_b & ~known_a

    merged[only_a] = a[only_a]
    merged[only_b] = b[only_b]

    merged[(a == 0) & (b == 0)] = 0
    merged[(a == 100) & (b == 100)] = 100

    # Conflicting observations remain unknown.
    return merged


def save_ros_map(grid):
    path = os.path.join(
        HOME, PREFIX + "_fused_map"
    )

    image = np.full(grid.shape, 205, np.uint8)
    image[grid == 0] = 254
    image[grid == 100] = 0

    image = np.flipud(image)

    if not cv2.imwrite(path + ".pgm", image):
        raise RuntimeError("Failed to save PGM")

    metadata = {
        "image": PREFIX + "_fused_map.pgm",
        "mode": "trinary",
        "resolution": SCALE,
        "origin": [
            -CENTER * SCALE,
            -CENTER * SCALE,
            0.0
        ],
        "negate": 0,
        "occupied_thresh": 0.65,
        "free_thresh": 0.25
    }

    with open(path + ".yaml", "w") as f:
        yaml.safe_dump(
            metadata,
            f,
            sort_keys=False
        )

    return path


def main():
    print("TWIST Lab - Dual-SLAM Fusion V2")
    print("Loading saved maps...", flush=True)

    a_data = load_map("rosbot-dual-slam/maps/live_session_nov18/robot_a_retry")
    b_data = load_map("rosbot-dual-slam/maps/live_session_nov18/robot_b_final")

    a = rasterize(a_data)
    b = rasterize(b_data)

    print("Searching for matching walls...", flush=True)

    best = search(a, b)

    if best["score"] <= -1e5:
        raise RuntimeError(
            "No usable registration candidate found"
        )

    # Preserve the original search and transform.
    aligned_b = warp_grid(
        b,
        best["angle"],
        best["tx"],
        best["ty"]
    )

    # Clean only after registration has finished.
    clean_a = clean_grid(a)
    clean_b = clean_grid(aligned_b)

    overlay = make_overlay(clean_a, clean_b)

    overlay_path = os.path.join(
        HOME, PREFIX + "_alignment.png"
    )

    if not cv2.imwrite(overlay_path, overlay):
        raise RuntimeError("Failed to save overlay")

    merged = fuse(clean_a, clean_b)

    preview = np.full(
        merged.shape, 205, np.uint8
    )
    preview[merged == 0] = 255
    preview[merged == 100] = 0

    preview_path = os.path.join(
        HOME, PREFIX + "_fused_preview.png"
    )

    if not cv2.imwrite(preview_path, preview):
        raise RuntimeError("Failed to save preview")

    map_path = save_ros_map(merged)

    print("\n========== VERSION 2 RESULTS ==========")
    print(
        f"Rotation B -> A: "
        f"{best['angle']:.2f} degrees"
    )
    print(
        f"Translation B -> A: "
        f"({best['tx']:.3f}, {best['ty']:.3f}) m"
    )
    print(
        f"Obstacle proximity: "
        f"{best['proximity']:.4f}"
    )
    print(
        f"Conflict ratio: "
        f"{best['conflict']:.4f}"
    )
    print(
        f"Known overlap: "
        f"{best['overlap']} cells"
    )
    print(
        f"Registration score: "
        f"{best['score']:.4f}"
    )

    print("\nGenerated files:")
    print(overlay_path)
    print(preview_path)
    print(map_path + ".pgm")
    print(map_path + ".yaml")

    print("\nOriginal maps and Version 1 unchanged.")
    print("Experimental map: validation required.")
    print("No TF published. No ROS nodes modified.")


if __name__ == "__main__":
    main()
