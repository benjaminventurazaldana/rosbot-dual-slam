# Historical README archive (through November 18, 2026)

> This is an archival copy of the README before the November 26 cleanup. It contains historical status statements, old commands, pending lists, and earlier fusion transform estimates that **must not be treated as the current project status**. For current verified work, use [`../README.md`](../README.md) and [`nov26_experiment.md`](nov26_experiment.md).

---

# Cooperative Multi-Robot Mapping — Dual SLAM

Undergraduate research project at the University of Texas at Arlington (UTA), conducted in the TWIST Lab under Dr. Debashri Roy.

**Research Title:** Cooperative Multi-Robot Mapping: A Dual-SLAM Approach via Wireless Edge Computing

**Research Goal:** Develop a cooperative mapping system in which two ROS 2 mobile robots independently collect sensor data, communicate over a wireless network, and eventually combine their maps into a shared environmental representation.

# November 26, 2026 — Final Planned Experimental Dataset and Live Fusion Milestone

**Current authoritative status (supersedes older dated status entries below).** The November 26 laboratory session is the **final planned data-collection and mapping session** for the current experiment. Robot A and Robot B performed independently running SLAM during supervised manual teleoperation. Their sensor recordings, simultaneous combined ROS bag, final exported occupancy maps, offline registration outputs, and live-fusion snapshots are versioned in this repository.

**Research scope:** This is a working **live occupancy-grid fusion prototype**, **not** a ground-truth-validated mapping or autonomous navigation system. Live fusion consumes the two robots' independently generated maps; it does not perform online joint SLAM optimization, publish the missing inter-robot TF transform, or fuse raw scans directly.

## Start here: November 26 dataset

| Resource | Location / description |
|---|---|
| Robot A recorded LiDAR | `datasets/nov26/robot_a_lidar_20261126/` |
| Robot B recorded LiDAR — Noman's data source | `datasets/nov26/robot_b_lidar_20261126/` |
| Combined 12 min 12 sec ROS bag | `datasets/nov26/dual_slam_combined_20261126/` — 81,152 messages, 12 topics, approximately 459.6 MiB |
| Robot A exported map | `datasets/nov26/dual_slam_nov26_maps/robot_a.pgm` and `.yaml` — 208 × 161, 0.05 m/cell |
| Robot B exported map | `datasets/nov26/dual_slam_nov26_maps/robot_b.pgm` and `.yaml` — 206 × 171, 0.05 m/cell |
| Offline registration and fusion | `scripts/dual_slam_fusion_nov26.py` |
| Live occupancy-grid fusion | `scripts/dual_slam_live_fusion_nov26.py` |
| Offline overlay, map and visualizations | `results/nov26/dual_slam_nov26_*` |
| Saved live map before movement | `results/nov26/live_fused_map.pgm` and `.yaml` |
| Saved live map after movement | `results/nov26/live_fused_map_after_movement.pgm` and `.yaml` |
| Detailed reproducibility, results, limitations | [November 26 experiment guide](docs/nov26_experiment.md) |
| Commands, procedures and historic sessions | [commands.md](commands.md) and [lab_notes.md](lab_notes.md) |

**For Noman:** The original Robot B raw LaserScan topic is **`/robot_b/scan`**; the normalized scan is **`/robot_b/scan_fixed`**. The dedicated Robot B bag is in `datasets/nov26/robot_b_lidar_20261126/`. The combined bag also contains Robot B scan topics. Bag `.db3` objects use Git LFS: clone with Git LFS installed and run `git lfs pull` to obtain the actual recordings rather than pointer files.

## Verified November 26 results

- Bidirectional ROS 2 LiDAR topic visibility across the shared Wi-Fi network; each robot continued running its own SLAM instance.
- Both occupancy-grid topics, `/robot_a/map` and `/robot_b/map`, published at approximately 0.2 Hz.
- Offline B-to-A map alignment estimate: **−2.50°**, translation **(0.000, +0.700) m**; obstacle proximity **0.8262**, conflict ratio **0.0418**, known overlap **32,814 cells**, registration score **1.8383**. These are algorithm-defined registration diagnostics, **not physical alignment accuracy or independent ground truth**.
- The live node subscribed to both maps, published a fused 480 × 480 occupancy grid at 0.05 m/cell on `/dual_slam/fused_map_preview` approximately every five seconds, and the output was displayed in RViz with fixed frame `robot_a/map`.
- Following a small, supervised Robot A turn, the live fusion's logged known-cell count changed from **21,278 to 22,344** and occupied-cell count from **1,826 to 1,860**. Before/after PGM+YAML snapshots were saved. This supports that the live output responded during the test; counts alone do not prove exact cellwise agreement, freshness, alignment accuracy, or both robots' contributions.
- Both robots were safely stopped and shut down after maps and recordings were backed up. November 26 raw datasets were merged in PR #2; fusion code and outputs were merged in PR #3 (merge commit `a20533b`).

**Outstanding for the research paper:** Independently evaluate alignment accuracy, reproducibly rerun the offline pipeline on the archived maps, inspect the before/after grid differences, characterize source freshness and TF separation, and accurately report limitations. No additional laboratory mapping session is currently planned. The earlier November 13/18 material below remains as **historical context**; older “pending” lists and older estimated transforms must not be interpreted as current November 26 results.

---

## 1. Historical project status (through November 18)

**Last updated:** November 26, 2026

Both robots have completed standalone SLAM and a simultaneous manually teleoperated mapping session. Cross-robot map-topic sharing and experimental offline map fusion have been demonstrated; accuracy validation and live fusion remain pending.

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
- Validate and improve experimental cooperative map alignment and fusion
- Complete integrated testing and final demonstration

**Current milestone:** Simultaneous independent SLAM and experimental offline fusion completed. Ground-truth alignment validation and robust live fusion are next.

## Current milestone — November 18, 2026

**Status:** Two independent robot mapping sessions and an **experimental offline fused occupancy map** have been saved to GitHub (commit `729aad6`). The fused map is a research candidate; its alignment has **not** been validated against surveyed landmarks or ground truth, and it is **not suitable for autonomous navigation**.

- Robot A (leader; `192.168.0.224`) and Robot B (follower; `192.168.0.138`) ran their individual SLAM pipelines simultaneously on the TWIST Lab wireless network.
- Robot A subscribed to `/robot_a/map` and `/robot_b/map` across the ROS 2 network. This demonstrates map-topic sharing; a fully validated shared TF tree and bidirectional application-level messaging are still separate tasks.
- Both robots were **manually teleoperated** through the laboratory. Autonomous exploration has **not** been implemented.
- Robot A's first November 18 map was distorted (811 × 1122 cells). After restarting its localization/SLAM launcher and repeating the route, its saved retry map became coherent (204 × 162 cells).
- Robot B's saved map was 218 × 221 cells. Both use 0.05 m/cell resolution.
- Offline registration of `robot_a_retry` and `robot_b_final` estimated rotation B→A **−17.50°**, translation **(−0.050, +0.500) m**, obstacle proximity **0.7191**, conflict ratio **0.0898**, known overlap **32,183 cells**, and algorithm score **1.5436**. These are algorithm-specific diagnostics, not calibrated accuracy measurements.
- Starting layout was approximately parallel, Robot B to Robot A's left, with measured 29 in (~0.7366 m) center-to-center separation. This informed a **soft initial registration preference**, not a fixed transform constraint; the best-fit −17.5° rotation needs independent validation.

### November 18 artifacts

| Artifact | Repository path |
|---|---|
| Robot A successful map | `maps/live_session_nov18/robot_a_retry.pgm` and `.yaml` |
| Robot B map | `maps/live_session_nov18/robot_b_final.pgm` and `.yaml` |
| Robot A failed first attempt (retained for diagnosis) | `maps/live_session_nov18/robot_a_final.pgm` and `.yaml` |
| Fusion overlay and preview | `maps/live_session_nov18/fusion/dual_slam_nov18_alignment.png`, `dual_slam_nov18_fused_preview.png` |
| Experimental ROS-compatible fused grid | `maps/live_session_nov18/fusion/dual_slam_nov18_fused_map.pgm` and `.yaml` |
| Reproduction script | `scripts/dual_slam_fusion_nov18.py` |

### Reproduce November 18 offline fusion

On a ROS robot/Ubuntu system with Python 3, NumPy, OpenCV, SciPy, and PyYAML, and with this repository cloned at `/home/wheeltec/rosbot-dual-slam`:

```bash
cd /home/wheeltec
python3 -u ~/rosbot-dual-slam/scripts/dual_slam_fusion_nov18.py
```

The script uses fixed absolute paths and writes `dual_slam_nov18_*.png`, `.pgm`, and `.yaml` to `/home/wheeltec/`. Running it from other systems requires adapting the `HOME` constant and map paths. The committed copies in `maps/live_session_nov18/fusion/` preserve the experiment as performed.

### Next research steps

1. Measure shared landmarks and independently validate/refine the B→A map transform; verify the duplicated/offset boundaries visible in overlays.
2. Investigate Robot A's EKF and odometry divergence during the first run (previously very large X/Y position covariance, EKF update-rate warnings). The cause was **not established**.
3. Make the fusion script portable and report registration quality against ground truth or other quantitative reference measurements.
4. Integrate a validated transform into live/periodic map fusion; do not reuse November 16's hard-coded live-fusion transform for this session.
5. Continue frame/topic isolation, bidirectional communication validation, and (later) autonomous navigation and exploration.

**Historical note:** Older sections below document the state of the project *at the time they were written*. Any older “pending” statements for simultaneous mapping, topic sharing, or initial offline fusion are superseded by the November 18 milestone above. Live validated fusion and autonomous exploration remain pending.

---

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

Historically, a legacy transform from `robot_b/base_footprint` to `gyro_link` was added. Later testing corrected Robot B's IMU frame to the namespaced `robot_b/gyro_link` and removed the legacy transform; confirm the active files when deploying.

After the fix:

- EKF output stabilized near 20 Hz
- SLAM Toolbox generated occupancy-grid maps
- The corrected launch configuration worked after a full reboot

The previously used legacy `gyro_link` frame was addressed in later testing. Continue auditing namespaced TF frames during multi-robot integration.

## 6. ROS 2 Networking and Multi-Robot Integration

Multi-robot integration is **in progress**: simultaneous independent SLAM and cross-robot map-topic sharing have been demonstrated, but a validated shared TF transform and robust live fusion are not completed.

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

Validate the November 18 offline fused-map alignment and investigate Robot A's prior EKF/SLAM failure before advancing live fusion.

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
- Experimental offline cooperative map fusion is implemented; independent validation and live fusion are pending

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

**Current research phase (November 18):** Simultaneous mapping and experimental offline fusion demonstrated; validation, robust live integration, and autonomous exploration remain pending.

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

