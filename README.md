
# Cooperative Multi-Robot Mapping — Dual SLAM

Undergraduate research project at the University of Texas at Arlington (UTA), conducted in the TWIST Lab under Dr. Debashri Roy.

**Research Title:** Cooperative Multi-Robot Mapping: A Dual-SLAM Approach via Wireless Edge Computing

**Research Goal:** Develop a cooperative mapping system in which two ROS 2 mobile robots independently collect sensor data, communicate over a wireless network, and eventually combine their maps into a shared environmental representation.

## 1. Project Status

**Last updated:** November 11, 2026

Both robots have completed standalone SLAM configuration, testing, reboot verification, and GitHub backups.

### Completed

- SSH connectivity to both NVIDIA Jetson computers
- ROS 2 Humble environment verification
- WheelTec base driver configuration
- LiDAR sensor operation
- IMU processing and EKF odometry
- Custom LiDAR scan normalization
- Asynchronous SLAM Toolbox configuration
- Individual occupancy-grid map generation
- Map exports in `.pgm` and `.yaml` formats
- Unified ROS 2 launch files for both robots
- Successful full-reboot testing
- Local backups of working configurations
- GitHub backups for Robot A and Robot B

Previous lab sessions also included keyboard teleoperation, camera testing, and RViz visualization. These features have not all been revalidated as part of the latest unified-launch reboot tests.

### Pending

- Audit and isolate conflicting ROS 2 topics, nodes, and TF frames
- Configure and verify multi-robot ROS 2 networking
- Demonstrate bidirectional robot-to-robot messaging
- Run both robots simultaneously without interference
- Exchange robot positions, sensor data, and maps
- Configure autonomous navigation and obstacle avoidance
- Implement autonomous exploration
- Implement cooperative map alignment and fusion
- Complete integrated testing and final demonstration

**Current milestone:** Standalone SLAM completed for both robots. Multi-robot integration is the next phase.

## 2. Robot Information

| Property | Robot A | Robot B |
|---|---|---|
| Jetson IP | `192.168.0.224` | `192.168.0.138` |
| SSH username | `wheeltec` | `wheeltec` |
| ROS distribution | ROS 2 Humble | ROS 2 Humble |
| Platform | WheelTec | WheelTec |
| LiDAR | LSLiDAR M10_P | LSLiDAR M10_P |
| Localization | robot_localization EKF | robot_localization EKF |
| Mapping | SLAM Toolbox | SLAM Toolbox |
| Launch file | `robot_a_all.launch.py` | `robot_b_all.launch.py` |
| Saved map prefix | `robot_a_map_verified` | `robot_b_map_verified` |
| Reboot verification | Complete | Complete |
| GitHub backup | Complete | Complete |

Both robots use NVIDIA Jetson computers and communicate over the TWIST Lab wireless network.

## 3. Repository Structure

```text
rosbot-dual-slam/
├── README.md
├── commands.md
├── lab_notes.md
├── robot_a/
│   ├── robot_a_all.launch.py
│   ├── robot_a_ekf.yaml
│   ├── robot_a_slam.yaml
│   ├── robot_a_map_verified.pgm
│   ├── robot_a_map_verified.yaml
│   └── additional configuration files
└── robot_b/
    ├── lsm10_p_robot_b.yaml
    ├── robot_b_all.launch.py
    ├── robot_b_ekf.yaml
    ├── robot_b_imu.yaml
    ├── robot_b_map_initial.pgm
    ├── robot_b_map_initial.yaml
    ├── robot_b_map_verified.pgm
    ├── robot_b_map_verified.yaml
    ├── robot_b_scan_normalizer.py
    └── robot_b_slam.yaml
```

The repository contains backed-up configuration files and saved maps. The Jetson home directories contain the active launch files used during testing.

The repository structure shown above summarizes Robot A's main files and lists Robot B's verified backup files.

## 4. Robot A — Verified Standalone SLAM

### Connect to Robot A

```bash
ssh wheeltec@192.168.0.224
```

### Start the mapping system

```bash
ros2 launch ~/robot_a_all.launch.py
```

The unified launcher starts the robot's base driver, required transforms, sensor-processing components, EKF localization, LiDAR, scan normalization, and asynchronous SLAM Toolbox.

Keep the launch terminal running while testing.

### Verify map publication

From a second SSH terminal:

```bash
ros2 topic echo /map --once --field info
```

### Verified mapping results

- Occupancy-grid map successfully published on `/map`
- Resolution: 0.05 meters per cell
- Previously recorded dimensions: 146 × 181 cells
- Approximate mapped area dimensions: 7.30 × 9.05 meters
- Scan normalizer output: 1440 readings per scan
- Map successfully exported
- Full Jetson reboot verification completed

### Saved files

```text
robot_a/robot_a_map_verified.pgm
robot_a/robot_a_map_verified.yaml
```

Map dimensions may change between SLAM sessions as the robot creates a new map.

## 5. Robot B — Verified Standalone SLAM

### Connect to Robot B

```bash
ssh wheeltec@192.168.0.138
```

### Start the mapping system

```bash
ros2 launch ~/robot_b_all.launch.py
```

The unified launcher starts:

- WheelTec base driver
- Madgwick IMU filter
- robot_localization EKF
- Static TF publishers
- LSLiDAR M10_P driver
- Custom Python scan normalizer
- Asynchronous SLAM Toolbox

### Verify odometry

From a second SSH terminal:

```bash
ros2 topic hz /robot_b/odom_combined
```

**Verified after reboot:** Approximately 19.92 Hz.

### Verify mapping

```bash
ros2 topic echo /robot_b/map --once --field info
```

### Verified mapping results

- Occupancy-grid map successfully published on `/robot_b/map`
- Resolution: 0.05 meters per cell
- Post-reboot map dimensions: 144 × 168 cells
- Approximate mapped area dimensions: 7.20 × 8.40 meters
- EKF odometry approximately 20 Hz
- Scan normalizer output: 1440 readings per scan
- Map successfully exported
- Full Jetson reboot verification completed

### Save a map

```bash
ros2 run nav2_map_server map_saver_cli -f ~/robot_b_map_verified --ros-args -p save_map_timeout:=15.0 -r map:=/robot_b/map
```

### Saved files

```text
robot_b/robot_b_map_initial.pgm
robot_b/robot_b_map_initial.yaml
robot_b/robot_b_map_verified.pgm
robot_b/robot_b_map_verified.yaml
```

The verified map files were saved before the final reboot. The post-reboot map publication test confirmed that mapping restarted successfully; it did not replace the previously saved verified map.

### Important IMU/TF Fix

During testing, Robot B's raw IMU messages used the frame ID `gyro_link`, while the initial static transform configuration only published the namespaced `robot_b/gyro_link` frame.

This mismatch prevented the EKF and SLAM pipeline from operating correctly.

A legacy transform from `robot_b/base_footprint` to `gyro_link` was added to the unified launch file.

After the fix:

- EKF output stabilized near 20 Hz
- SLAM Toolbox generated occupancy-grid maps
- The corrected launch configuration worked after a full reboot

This legacy frame must be reviewed during multi-robot TF isolation to prevent naming conflicts.

## 6. ROS 2 Networking and Multi-Robot Integration

Multi-robot integration has not yet been completed.

Robot B was confirmed to use ROS domain ID 0 during standalone testing. Robot A's current domain setting still needs to be verified.

### Namespace and Topic Audit

Before operating both robots simultaneously, review potentially shared topics and frames, including:

```text
/odom
/imu/data_raw
/imu/data
/cmd_vel
/tf
/tf_static
gyro_link
```

The intended architecture uses distinct robot-specific names and TF frames while preserving the ability to exchange messages.

Example intended topic organization:

```text
/robot_a/odom
/robot_a/scan
/robot_a/map

/robot_b/odom
/robot_b/scan
/robot_b/map
```

These names illustrate the intended organization; they are not a claim that every topic has already been remapped.

ROS 2 normally uses shared `/tf` and `/tf_static` topics with uniquely named frames. Their handling must be reviewed during integration.

### Communication Goal

Demonstrate:

1. Robot A publishes a ROS 2 message.
2. Robot B receives the message.
3. Robot B publishes a response.
4. Robot A receives the response.

The demonstration should confirm bidirectional communication over the TWIST Lab network.

Afterward, extend communication to robot poses, mapping information, and other research data.

## 7. Research Milestones

| Milestone | Status |
|---|---|
| Robot A standalone SLAM | Complete |
| Robot B standalone SLAM | Complete |
| Robot A reboot verification | Complete |
| Robot B reboot verification | Complete |
| Local and GitHub backups | Complete |
| Namespace and TF isolation | Pending |
| ROS 2 networking | Pending |
| Bidirectional messaging | Pending |
| Simultaneous SLAM | Pending |
| Sensor and pose sharing | Pending |
| Autonomous navigation | Pending |
| Autonomous exploration | Pending |
| Cooperative map fusion | Pending |
| Final integrated demonstration | Pending |

### Immediate Priority

Complete the multi-robot namespace audit and establish bidirectional ROS 2 communication between Robot A and Robot B.

### Longer-Term Research Goals

- Allow both robots to navigate independently
- Collect environmental data through autonomous exploration
- Exchange sensor and mapping information
- Align independently generated occupancy-grid maps
- Merge maps into a shared environmental representation
- Evaluate cooperative mapping performance
- Demonstrate the integrated system by April 2027

The final architecture for centralized versus decentralized map fusion remains to be determined.

## 8. Known Issues and Future Improvements

- Potential conflicts from shared ROS 2 topic names
- Potential TF frame conflicts when both robots are online
- Legacy `gyro_link` frame used by Robot B
- ROS domain and DDS discovery configuration not finalized
- LiDAR minimum-range configuration warning
- Configuration paths may require portability improvements
- Camera and RViz functionality require revalidation in the integrated setup
- Autonomous navigation and exploration are not yet configured
- Cooperative map fusion has not yet been implemented

These issues do not invalidate the completed standalone SLAM tests.

## 9. Documentation

See `commands.md` for startup, verification, mapping, and troubleshooting commands.

See `lab_notes.md` for test results, observed ROS topics, configurations, and research progress.

The active Jetson launch configurations and their repository backups should be reviewed together before making changes.

## 10. Repository

**GitHub username:** `benjaminventurazaldana`

**Repository:** https://github.com/benjaminventurazaldana/rosbot-dual-slam

Both robots' standalone mapping configurations and verified maps have been committed and pushed.

Robot B's verified configuration was uploaded in commit `d42d79f` on November 11, 2026.

---

**Current research phase:** Transitioning from independently verified SLAM systems to cooperative multi-robot communication, autonomous exploration, and map fusion.

---

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

