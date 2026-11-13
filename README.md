# rosbot-dual-slam

REU project for cooperative multi-robot mapping using ROS 2 and dual SLAM.

## Current Status

Completed single-robot testing for both robots:

- SSH connection verified
- Keyboard teleoperation verified
- LiDAR verified
- Camera verified
- RViz visualization verified
- Single-robot SLAM verified
- Maps saved for both robots
- RViz configurations saved for both robots

## Robots

Robot A:
- IP: 192.168.0.224
- Map: `/home/wheeltec/robotA_map.yaml`
- RViz config: `/home/jetson/.rviz2/robotA.rviz`

Robot B:
- IP: 192.168.0.138
- Map: `/home/wheeltec/robotB_map.yaml`
- RViz config: `/home/jetson/.rviz2/robotB.rviz`

## ROS Environment

- ROS 2 Humble
- NVIDIA Jetson used for RViz visualization
- WheelTec robot platform
- SLAM package: `wheeltec_slam_toolbox`

## Current Milestone

Single-robot SLAM is working on both robots.

Next milestone:
- ROS 2 networking
- ROS_DOMAIN_ID testing
- Communication between machines
- Running both robots together
- Multi-robot SLAM / map fusion

See `commands.md` for startup and troubleshooting commands.

See `lab_notes.md` for test results and issues encountered.
---

## Robot A — Verified Mapping Setup (November 11, 2026)

Robot A's mapping pipeline was successfully restarted using a single ROS 2 launch command. The system published an occupancy-grid map on `/map`, and the map was exported successfully.

### Hardware and Software

- Platform: WheelTec ROSbot with NVIDIA Jetson
- ROS distribution: ROS 2 Humble
- LiDAR: LSLiDAR M10_P
- Localization: robot_localization EKF
- Mapping: SLAM Toolbox (asynchronous mode)
- LiDAR preprocessing: custom Python scan normalizer

### Startup

Connect to Robot A:

```bash
ssh wheeltec@192.168.0.224
```

```
ros2 launch ~/robot_a_all.launch.py
```

The master launcher starts the base driver, static transforms, EKF, LiDAR, scan normalizer, and SLAM Toolbox.

### Verify Mapping

In a second SSH terminal:

```
ros2 topic echo /map --once --field info
```

Save a map:

```
ros2 run nav2_map_server map_saver_cli -f ~/robot_a_map_verified -t /map --ros-args -p save_map_timeout:=10.0
```

### Verified Results

- Map resolution: 0.05 meters per cell
- Map dimensions: 146 x 181 cells
- Physical map coverage: approximately 7.30 x 9.05 meters
- Saved outputs: `robot_a/robot_a_map_verified.pgm` and `robot_a/robot_a_map_verified.yaml`
- Scan normalizer output: 1440 readings per scan

### Remaining Work

- Verify startup after a complete Jetson reboot
- Improve portability of configuration paths
- Resolve LiDAR minimum-range warning
- Revalidate Robot B mapping
- Configure ROS 2 networking between both robots
- Implement cooperative mapping and map fusion

---

## Cooperative Dual-SLAM Mapping and Fusion (November 13, 2026)

### Overview

Robot A and Robot B successfully performed independent SLAM mapping of overlapping areas of the TWIST Lab.

Both robots explored the same environment from different directions. Robot A received Robot B's occupancy-grid data over the ROS 2 network.

An offline map-registration and fusion pipeline was developed to align the independently generated occupancy grids and produce a preliminary combined map.

### ROS 2 Communication

- Robot A (leader): `192.168.0.224`
- Robot B (follower): `192.168.0.138`
- ROS distribution: ROS 2 Humble
- Robot A map topic: `/map`
- Robot B map topic: `/robot_b/map`
- Both occupancy grids were received on Robot A.
- Both robots maintained independent SLAM pipelines.

### Saved Maps

| Property | Robot A | Robot B |
|---|---|---|
| Dimensions | 170 x 193 | 193 x 247 |
| Resolution | 0.05 m/cell | 0.05 m/cell |
| Map format | PGM + YAML | PGM + YAML |
| Frame | `robot_a/map` | `robot_b/map` |

The maps are stored in the `maps/` directory.

### Map Registration

Because the two robots use independent SLAM coordinate frames, their occupancy grids cannot be directly combined without estimating a relative transformation.

The offline registration pipeline:

1. Loads the saved occupancy grids and YAML metadata.
2. Converts both maps into a shared processing canvas.
3. Searches candidate rotations and translations.
4. Evaluates obstacle proximity, occupied/free conflicts, and overlapping known cells.
5. Refines the best candidate transformation.
6. Generates an alignment visualization.

The registration uses a coarse-to-fine search with OpenCV and SciPy.

### Experimental Registration Results

| Metric | Result |
|---|---|
| Estimated rotation (B to A) | 29.50 degrees |
| Estimated translation X | 0.900 m |
| Estimated translation Y | -2.250 m |
| Obstacle proximity score | 0.7784 |
| Occupied/free conflict ratio | 0.0817 |
| Known overlapping cells | 7,884 |
| Registration score | 1.6159 |

These are algorithm-specific diagnostic values, not independent accuracy measurements.

The transformation has not been validated against ground-truth robot poses or surveyed landmarks.

### Experimental Map Fusion

After registration, the two occupancy grids are combined using a conservative occupancy policy:

- Cells observed by only one robot retain that robot's occupancy value.
- Cells where both robots agree are preserved.
- Conflicting occupied/free observations are marked unknown.

Generated outputs are stored in `results/`:

- `dual_slam_final_alignment.png`
- `dual_slam_fused_preview.png`
- `dual_slam_fused_map.pgm`
- `dual_slam_fused_map.yaml`
- Version 2 alignment, preview, and fused-map files

The fused occupancy grid uses a resolution of 0.05 meters per cell and includes ROS-compatible YAML metadata.

### Version 2 Improvements

Version 2 adds a limited morphological cleanup step to reduce small rasterization gaps while preserving occupied cells.

The registration search remains unchanged, producing the same estimated transformation and diagnostic metrics.

Diagonal rasterization artifacts remain visible in the fused map and require additional investigation.

### Repository Organization

- `scripts/dual_slam_fusion.py` — original offline registration and fusion
- `scripts/dual_slam_fusion_v2.py` — experimental raster cleanup
- `maps/` — original saved occupancy grids and metadata
- `results/` — alignment visualizations and experimental fused maps
- `commands.md` — ROS 2 commands and startup procedures
- `lab_notes.md` — laboratory notes and troubleshooting

### Running Offline Fusion

The scripts currently use `/home/wheeltec` as the input and output directory.

On Robot A, with the saved map files present:

```bash
python3 ~/dual_slam_fusion.py
```

For Version 2:

```bash
python3 ~/dual_slam_fusion_v2.py
```

Dependencies include Python 3, NumPy, OpenCV, SciPy, and PyYAML.

### Remaining Research Tasks

- Eliminate diagonal rasterization artifacts.
- Validate registration against shared physical landmarks.
- Investigate changing TF heading estimates while robots are stationary.
- Visualize the experimental fused map in RViz.
- Evaluate map fusion quality quantitatively.
- Investigate live or periodically updated cooperative map fusion.

**Research status:** Independent SLAM and inter-robot map sharing demonstrated. Offline map registration and experimental fusion implemented. Accuracy validation and robust fusion remain in progress.

**Safety note:** Experimental fused maps are not validated for autonomous navigation.

