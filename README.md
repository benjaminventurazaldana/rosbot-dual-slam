# Cooperative Multi-Robot Mapping — Dual SLAM

**University of Texas at Arlington (UTA) · TWIST Lab · Dr. Debashri Roy**

**Research title:** Cooperative Multi-Robot Mapping: A Dual-SLAM Approach via Wireless Edge Computing

**Last updated:** November 26, 2026

## Current status

The **November 26, 2026 experiment is the final planned physical data-collection session** for the present study. Two WheelTec robots operated **independent ROS 2 Humble / SLAM Toolbox pipelines** and were manually teleoperated through overlapping lab areas. Individual LiDAR recordings, a combined ROS 2 bag, separate occupancy maps, offline fusion outputs, and before/after live-fusion maps are archived in this repository.

**Implemented and observed:** independent SLAM, cross-robot ROS 2 LiDAR/map topic access over the lab Wi-Fi, offline occupancy-grid registration/fusion, and a live fused-map **preview** that updated following a controlled Robot A turn.

**Not yet validated:** independent ground-truth map alignment accuracy, online registration/refinement, connected inter-robot TF trees, synchronized/fresh input handling, autonomous exploration, or navigation suitability. **This is an experimental live occupancy-grid fusion prototype, not a shared joint-SLAM estimator or navigation-ready map.** These limits must be reported accurately in research outputs.

### Final November 26 datasets and deliverables

| Artifact | Repository path |
|---|---|
| Robot A raw LiDAR recording | `datasets/nov26/robot_a_lidar_20261126/` |
| Robot B raw LiDAR recording | `datasets/nov26/robot_b_lidar_20261126/` |
| Combined dual-robot ROS bag | `datasets/nov26/dual_slam_combined_20261126/` |
| Robot A/B final exported maps | `datasets/nov26/dual_slam_nov26_maps/` |
| Offline registration and fusion script | `scripts/dual_slam_fusion_nov26.py` |
| Live occupancy-grid fusion script | `scripts/dual_slam_live_fusion_nov26.py` |
| Offline and live fusion maps, overlays and snapshots | `results/nov26/` |
| Detailed setup, data, reproduction, measurements and limitations | [November 26 experiment guide](docs/nov26_experiment.md) |
| Commands for archived test procedures | [commands.md](commands.md) |
| Dated experimental observations | [lab_notes.md](lab_notes.md) |
| Earlier test history and old README | [Historical README archive](docs/historical_readme_pre_cleanup.md) |

**Data handoff for Noman:** The Robot B bag is `datasets/nov26/robot_b_lidar_20261126/`; raw LiDAR topic **`/robot_b/scan`**, normalized LiDAR topic **`/robot_b/scan_fixed`**. The combined bag also includes Robot B scan topics. Git LFS is required to retrieve the full `.db3` data (`git lfs pull`).

The combined recording lasted approximately **12 minutes 12 seconds**, with **81,152 messages across 12 topics**, approximately **459.6 MiB**. Exported Robot A and B grids measure **208 × 161** and **206 × 171** cells respectively, both **0.05 m/cell**.

## November 26 results

| Measurement | Recorded outcome |
|---|---:|
| Estimated registration rotation, Robot B → Robot A | **−2.50°** |
| Estimated registration translation, B → A | **(0.000, +0.700) m** |
| Obstacle proximity (algorithm diagnostic) | **0.8262** |
| Occupied/free conflict ratio (algorithm diagnostic) | **0.0418** |
| Known overlapping map cells | **32,814** |
| Registration objective score (algorithm diagnostic) | **1.8383** |
| Live fused grid dimensions / resolution | **480 × 480 / 0.05 m/cell** |
| Fusion publication interval | **approximately 5 seconds** |
| Known cells before → after a controlled Robot A turn | **21,278 → 22,344** |
| Occupied cells before → after the turn | **1,826 → 1,860** |

The registration values are outputs of the offline optimization, **not independent measurements of physical alignment error**. The live cell counts show the fused output changed during the experiment, but do not prove map accuracy, input freshness, or each robot's independent contribution.

### Architecture and relevant topics

| Component | Robot A | Robot B |
|---|---|---|
| Jetson / SSH | `wheeltec@192.168.0.224` | `wheeltec@192.168.0.138` |
| Unified launch | `~/robot_a_all.launch.py` | `~/robot_b_all.launch.py` |
| Original LiDAR scan | `/robot_a/scan` | `/robot_b/scan` |
| Normalized scan | `/robot_a/scan_fixed` | `/robot_b/scan_fixed` |
| Independent occupancy map | `/robot_a/map` | `/robot_b/map` |

The live preview node runs on Robot A and **subscribes to both occupancy maps**. It applies the **fixed experimental** B→A transform estimated from the November 26 saved maps, and publishes `/dual_slam/fused_map_preview` with frame `robot_a/map`. This node does **not** directly merge raw LiDAR scans, compute a live transform, or publish a connecting inter-robot TF. Robot B's motion-command topic was observed as the global `/cmd_vel`; use appropriate safety checks if modifying the system.

## Reproduce offline map fusion without new robot data

The November 26 offline script reads its input maps **relative to the current working directory**, so run it from the **repository root**. Python packages required: `numpy`, `scipy`, `opencv-python`, `PyYAML`.

On Windows PowerShell with Python installed:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install numpy scipy opencv-python PyYAML
.\.venv\Scripts\python.exe .\scripts\dual_slam_fusion_nov26.py
```

It reads from `datasets/nov26/dual_slam_nov26_maps/` and writes generated `dual_slam_nov26_*` outputs to the repository root. Compare those generated files against the **committed reference artifacts** under `results/nov26/`; do not overwrite source data.

To retrieve large ROS bags on a machine with Git LFS:

```bash
git lfs install
git lfs pull
```

Read [the experiment guide](docs/nov26_experiment.md) for complete source-data descriptions, test commands, interpretation and limitations. ROS 2 bag inspection needs a configured ROS 2 environment; ordinary Windows PowerShell alone is insufficient.

## Remaining offline research and publication tasks

1. Reproduce the offline registration using the archived November 26 maps and document software versions and outputs.
2. Quantify cellwise differences between `results/nov26/live_fused_map.pgm` and `results/nov26/live_fused_map_after_movement.pgm`.
3. Evaluate the B→A map transform against an **independent reference, if available**; otherwise explicitly report that ground-truth accuracy is unavailable.
4. Explain disconnected TF trees, fixed alignment, input freshness and synchronization limitations, and why the fused map is not navigation-ready.
5. Include methodology, figures, measurements, limitations and appropriately bounded conclusions in the planned five-page conference paper due **December 6, 2026**.

**No additional physical mapping or recording session is currently planned.** RF B210 communication work is separately handled by Noman and Gaurav.

## Provenance and historical records

The November 26 raw datasets and maps were merged through **PR #2**; the offline/live fusion scripts and saved results through **PR #3**; the initial documentation update through **PR #4**. Prior November 13 and November 18 experiments are preserved in [lab_notes.md](lab_notes.md) and the [historical README archive](docs/historical_readme_pre_cleanup.md). Those records include **older** map dimensions, topic names, transform estimates and incomplete milestone lists. **They are not the current November 26 experiment status.**

**Repository:** https://github.com/benjaminventurazaldana/rosbot-dual-slam
