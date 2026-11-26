# November 26, 2026 — Final Planned Dual-SLAM Experiment

Project: **Cooperative Multi-Robot Mapping: A Dual-SLAM Approach via Wireless Edge Computing**  
Institution: University of Texas at Arlington, TWIST Lab  
Research advisor: Dr. Debashri Roy  
Data collection status: **complete for the currently planned experiment**. This document describes the archived session and reproducible software analysis; it does not request any new robot traversal.

## 1. Scope and architecture

Two WheelTec robots equipped with NVIDIA Jetson computers ran **ROS 2 Humble** and separate SLAM Toolbox pipelines. A manually supervised operator drove them through overlapping regions of the lab, one at a time. Robot A (leader, `192.168.0.224`) and Robot B (follower, `192.168.0.138`) published individual occupancy grids on `/robot_a/map` and `/robot_b/map` and their respective LiDAR topics. Each robot used its own LiDAR/odometry/IMU and EKF/SLAM processing.

The live software on Robot A consumes both `nav_msgs/msg/OccupancyGrid` maps and periodically fuses them into a **preview**. It does **not** merge the raw scans into one optimizer, establish a verified global inter-robot TF link, or support autonomous navigation.

The robots initially faced approximately the same direction with Robot B to Robot A's left, around **29 in = 0.7366 m center-to-center**. This is the approximate setup used for a *soft registration prior*, not a surveyed relative pose.

## 2. Archived final source recordings

The recordings and maps reside in the versioned `datasets/nov26/` folder:

| Directory / file | Description |
|---|---|
| `robot_a_lidar_20261126/` | Robot A standalone LiDAR recording |
| `robot_b_lidar_20261126/` | Robot B standalone LiDAR recording; intended raw sensor source for Noman |
| `dual_slam_combined_20261126/` | One shared ROS 2 recording including Robot A and Robot B topics; ~12 min 12 sec, 81,152 messages, 12 topics, ~459.6 MiB |
| `dual_slam_nov26_maps/robot_a.pgm`, `.yaml` | Robot A final saved occupancy grid, 208 × 161 cells |
| `dual_slam_nov26_maps/robot_b.pgm`, `.yaml` | Robot B final saved occupancy grid, 206 × 171 cells |

Maps use **0.05 m/cell**. Individual LiDAR bags recorded approximately 14,429 messages for Robot A and 33,000 for Robot B in their respective sessions. The combined recording contains original and normalized scans, odometry, Robot A IMU, occupancy maps and TF topics. Its exact topic inventory should be read from its own metadata rather than inferred from this summary.

**Noman's source topics:** Robot B original scan `/robot_b/scan`; normalized scan `/robot_b/scan_fixed`. These are different from the derived fused occupancy grid.

### Acquire Git LFS data on a development machine

```powershell
git lfs install
git clone https://github.com/benjaminventurazaldana/rosbot-dual-slam.git
cd rosbot-dual-slam
git lfs pull
```

If already cloned, run `git lfs pull` from the repo root. The `*.db3` files are tracked by Git LFS. Use `ros2 bag info datasets/nov26/dual_slam_combined_20261126` on a machine with ROS 2 available; similarly inspect the two separate LiDAR bags. Do not replace these recordings with newly collected data.

## 3. November 26 registration and offline fusion

Source: `scripts/dual_slam_fusion_nov26.py`

Input: the archived map pairs in `datasets/nov26/dual_slam_nov26_maps/`. The script loads PGM+YAML metadata, rasterizes the maps into a common **480 × 480** canvas, searches B→A rotation/translation candidates, refines the best score using obstacle proximity/overlap/conflict diagnostics, performs limited raster cleanup, and fuses free/occupied/unknown classifications conservatively. Conflicting occupied/free cells remain unknown.

The script's registration prior is an **initial** 0° direction and **(0, +0.7366 m)** separation; it may return a different result. It uses `HOME = os.getcwd()`, so it must be launched **from the repository root**, and writes outputs in that current directory. Committed outputs are copied to `results/nov26/`.

### Reproduce offline analysis (Windows PowerShell)

With Python installed and the repository locally cloned:

```powershell
cd C:\Users\HP\Documents\rosbot-dual-slam
.\.venv\Scripts\python.exe -m pip install numpy scipy opencv-python PyYAML
.\.venv\Scripts\python.exe .\scripts\dual_slam_fusion_nov26.py
```

If a virtual environment has not been created yet, first run `py -m venv .venv`. These commands write `dual_slam_nov26_*` files to the repo root. They do not modify the archived input maps. Compare with the committed `results/nov26/` outputs instead of blindly overwriting experimental records.

### Observed results

| Metric | November 26 result |
|---|---:|
| Estimated B→A rotation | −2.50° |
| Estimated translation | (0.000, +0.700) m |
| Obstacle proximity metric | 0.8262 |
| Conflict ratio metric | 0.0418 (4.18%) |
| Known overlap | 32,814 cells |
| Registration objective score | 1.8383 |

Files:

- `results/nov26/dual_slam_nov26_alignment.png` — registration overlay
- `results/nov26/dual_slam_nov26_fused_preview.png` — visualization
- `results/nov26/dual_slam_nov26_fused_map.pgm` and `.yaml` — experimental fused map

**Interpretation:** The overlay and numerical scores indicate a promising candidate alignment, but they are **not independently measured pose error**. There is no surveyed-landmark or calibrated ground-truth alignment result. A map registration driven by similarity can appear plausible while maintaining translational/rotational errors.

## 4. Live map-fusion prototype and captured test

Source: `scripts/dual_slam_live_fusion_nov26.py`.

Inputs: `/robot_a/map` and `/robot_b/map` (type `nav_msgs/msg/OccupancyGrid`). Output: `/dual_slam/fused_map_preview` (same message type, header frame `robot_a/map`). Publication occurs on a **5-second timer**, using the latest received source maps, not time-synchronized sensor frames.

Parameters provide a **fixed, experiment-specific B→A transform**:

```text
alignment_angle = -2.5 degrees
alignment_tx = 0.000 meters
alignment_ty = +0.700 meters
```

The source code header still warns about an earlier experimental alignment; the numerical values above were updated from the November 26 offline registration. The *numerical* transform remains **unvalidated against independent ground truth** and should not be carried into a newly restarted SLAM session without re-registration.

### Historical November 26 live launch (not necessary to rerun for archived evaluation)

On Robot A (while both SLAM launchers were operating):

```bash
ssh wheeltec@192.168.0.224
source /opt/ros/humble/setup.bash
python3 ~/dual_slam_live_fusion_nov26.py
```

The script was copied to Robot A's home directory during the experiment. For a future independent reproduction, copy the repository script to the intended machine and confirm ROS 2 Humble Python dependencies and both source topics first. This is not a request for more lab recording.

RViz used fixed frame `robot_a/map` and displayed `/dual_slam/fused_map_preview`, with 480 × 480 cells and 0.05 m/cell. The map preview was displayed and the node published repeatedly without reported errors during the observed test.

### Live-update observation

After a **short, supervised turn by Robot A** (Robot B stationary), the node logged:

| Output metric | Before motion | After motion | Change |
|---|---:|---:|---:|
| Known cells | 21,278 | 22,344 | +1,066 |
| Occupied cells | 1,826 | 1,860 | +34 |

The updated output was saved through ROS 2 map server and backed up under:

- `results/nov26/live_fused_map.pgm` and `.yaml`
- `results/nov26/live_fused_map_after_movement.pgm` and `.yaml`

Both snapshots are 480 × 480 cells at 0.05 m/cell. These count changes are **evidence of a responding output**, not proof of a validated shared map or an independently measured error bound. A stronger verification should compare cellwise contents, inspect source timestamps, and test each robot's contribution with archived topics.

The map saver command used was:

```bash
ros2 run nav2_map_server map_saver_cli \
  -t /dual_slam/fused_map_preview \
  -f ~/dual_slam_nov26_results/live_fused_map_after_movement \
  --ros-args -p save_map_timeout:=15.0 \
  -p map_subscribe_transient_local:=false
```

## 5. Reliability, frame and safety limitations

1. **Disconnected TF trees:** Each robot had internally valid map-to-laser transforms, but a direct `robot_a/map` to `robot_b/laser` lookup failed due to separate transform trees. The fixed fusion transform is applied numerically; the live node does not publish an inter-robot TF.
2. **Transform not ground-truth validated:** The November 26 result is obtained by an image-based search and soft starting-position prior; registered maps are not an independently calibrated global reference.
3. **No online alignment optimization:** The live node uses hard-coded default registration parameters and does not re-estimate alignment as SLAM updates. SLAM restarts could change origin and invalidate the transform.
4. **No freshness or synchronization gate:** The node republishes the most recently received maps every five seconds. It does not validate input age, matching acquisition times or per-source availability after the initial receipt.
5. **Derived map fusion, not raw scan fusion:** The two SLAM systems remain independent, and their occupancy grids are the fusion inputs.
6. **Occupancy policy:** Free/occupied conflicts are marked unknown. Rasterization and 0.05 m grid discretization can leave artifacts; previews are not safe for navigation or obstacle avoidance.
7. **Manual teleoperation only:** Autonomous navigation and exploration were not demonstrated. Robot B's global `/cmd_vel` interface requires a namespace-safety audit before any autonomous commanding.
8. **RF B210 scope:** RF communications hardware and experiments are handled by Noman and Gaurav; this documentation covers the ROS 2/Wi-Fi dual-SLAM experiment and the sensor recordings used by that work.

## 6. Research completion checklist (offline work only)

- [x] Robot A and B independent SLAM and manually supervised overlap coverage
- [x] Dedicated raw LiDAR bags and combined ROS bag recorded and archived with Git LFS
- [x] Individual maps exported and preserved
- [x] Offline registration plus experimental fused map created
- [x] Live periodic occupancy-grid output and RViz preview demonstrated
- [x] Observable live update during controlled Robot A motion
- [x] Before/after live outputs archived
- [x] Both robots safely shut down; datasets and fusion scripts merged to `main`
- [ ] Quantify cellwise difference between archived live snapshots
- [ ] Independently validate B→A registration using landmarks or another external reference (if available in existing recorded material)
- [ ] Reproduce offline fusion from committed inputs and record environment/dependencies
- [ ] Review source map freshness/TF limitations for publication-quality claims
- [ ] Report reproducibility, metrics, limitations and figures in the five-page conference paper (December 6, 2026)

**Versioning:** November 26 dataset was merged through PR #2; live/offline fusion code and maps through PR #3 (merge commit `a20533b`). The historical November 18 maps, scripts and diagnostics remain in the repository and should not be mixed with this final dataset.
