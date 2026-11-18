
# Lab Notes — Cooperative Multi-Robot Mapping

**Research Project:** Cooperative Multi-Robot Mapping: A Dual-SLAM Approach via Wireless Edge Computing  
**Institution:** University of Texas at Arlington (UTA)  
**Laboratory:** TWIST Lab  
**Research Advisor:** Dr. Debashri Roy  
**Last Updated:** November 18, 2026

---

**Latest research status:** November 18 independent mapping and experimental offline fusion completed; see the dated session log at the end of this file. Older “current” or “pending” statements below are preserved as **historical snapshots**, not the current status.

## 1. Project Overview

The goal of this research project is to develop a cooperative multi-robot mapping system using two WheelTec mobile robots equipped with NVIDIA Jetson computers.

Each robot independently performs SLAM using ROS 2 Humble, LiDAR measurements, and odometry.

The long-term objective is to enable both robots to:

1. Communicate over the TWIST Lab wireless network.
2. Exchange messages, robot positions, and sensor information.
3. Navigate and explore their environments autonomously.
4. Generate individual occupancy-grid maps.
5. Share and align their maps.
6. Combine mapping information into a common environmental representation.

The final map-fusion architecture, including centralized versus decentralized processing, remains to be determined.

**Current project phase:** Standalone SLAM is complete for both robots. Multi-robot integration is next.

---

## 2. Robot Information

| Property | Robot A | Robot B |
|---|---|---|
| IP Address | 192.168.0.224 | 192.168.0.138 |
| SSH Username | wheeltec | wheeltec |
| ROS Distribution | ROS 2 Humble | ROS 2 Humble |
| Computer | NVIDIA Jetson | NVIDIA Jetson |
| Platform | WheelTec | WheelTec |
| LiDAR | LSLiDAR M10_P | LSLiDAR M10_P |
| Localization | robot_localization EKF | robot_localization EKF |
| Mapping | SLAM Toolbox | SLAM Toolbox |
| SLAM Mode | Asynchronous | Asynchronous |
| Unified Launch | robot_a_all.launch.py | robot_b_all.launch.py |
| Saved Map Prefix | robot_a_map_verified | robot_b_map_verified |
| Standalone SLAM | Complete | Complete |
| Full Reboot Verification | Complete | Complete |
| GitHub Backup | Complete | Complete |

### Network Information

**Wi-Fi:** TWIST Lab network (TWIST, not TWIST 5G)

Robot B was confirmed to be using ROS domain 0 on November 11, 2026.

Earlier networking tests documented that Robot A, Robot B, and the visualization Jetson used the default ROS domain 0.

Robot A's current domain configuration should be verified again before multi-robot integration.

---

## 3. Robot A — Standalone SLAM

### SSH Connection

```bash
ssh wheeltec@192.168.0.224
```

### Unified Startup

```bash
ros2 launch ~/robot_a_all.launch.py
```

This unified launch starts Robot A's standalone mapping pipeline, including:

- WheelTec base driver
- Required static transforms
- IMU processing
- EKF localization
- LiDAR driver
- Custom Python scan normalizer
- Asynchronous SLAM Toolbox

### Verified Map Topic

```text
/map
```

### Verify Map Publication

```bash
ros2 topic echo /map --once --field info
```

### Verified Results

- Standalone SLAM successfully initialized.
- Occupancy-grid map published.
- Map resolution: 0.05 meters per cell.
- Recorded map dimensions: 146 x 181 cells.
- Approximate map dimensions: 7.30 x 9.05 meters.
- Scan normalizer output: 1440 readings per scan.
- Map successfully saved.
- Unified launch tested successfully after a full Jetson reboot.
- Working configuration backed up locally and uploaded to GitHub.

### Saved Map Files

```text
/home/wheeltec/robot_a_map_verified.pgm
/home/wheeltec/robot_a_map_verified.yaml
```

Repository copies:

```text
robot_a/robot_a_map_verified.pgm
robot_a/robot_a_map_verified.yaml
```

### Historical Robot A Configuration

Earlier testing used:

```text
LiDAR topic: /scan
Camera topic: /camera/color/image_raw
RViz fixed frame: map
SLAM package: wheeltec_slam_toolbox
SLAM launch: online_async_launch.py
```

Historical map files:

```text
/home/wheeltec/robotA_map.pgm
/home/wheeltec/robotA_map.yaml
```

Historical RViz configuration:

```text
/home/jetson/.rviz2/robotA.rviz
```

The historical paths and camera configuration have not been revalidated as part of the latest unified-launch testing.

---

## 4. Robot B — Standalone SLAM

### SSH Connection

```bash
ssh wheeltec@192.168.0.138
```

### Unified Startup

```bash
ros2 launch ~/robot_b_all.launch.py
```

The unified launch starts:

- WheelTec base driver
- Madgwick IMU filter
- robot_localization EKF
- Static transform publishers
- LSLiDAR M10_P driver
- Python scan normalizer
- Asynchronous SLAM Toolbox

### Verified ROS Topics

```text
/robot_b/scan
/robot_b/scan_fixed
/robot_b/odom_combined
/robot_b/map
/robot_b/map_metadata
/imu/data_raw
/odom
/tf
/tf_static
```

The global topics are potential multi-robot integration concerns.

### Verify LiDAR

```bash
ros2 topic hz /robot_b/scan_fixed
```

### Verify EKF Odometry

```bash
ros2 topic hz /robot_b/odom_combined
```

### Verify SLAM Map

```bash
timeout 15 ros2 topic echo /robot_b/map --once --field info
```

### Verified Results

Before reboot:

- EKF reached approximately 20 Hz.
- SLAM Toolbox generated an occupancy-grid map.
- Verified map dimensions: 178 x 168 cells.
- Resolution: 0.05 meters per cell.
- Map exported successfully.

After reboot on November 11, 2026:

- SSH connection restored successfully.
- Unified launch started all 11 configured processes.
- Base driver initialized.
- LiDAR driver initialized.
- IMU processing started.
- EKF odometry stabilized at approximately 19.92 Hz.
- SLAM Toolbox remained operational.
- Map topic published successfully.
- Post-reboot map dimensions: 144 x 168 cells.
- Resolution: 0.05 meters per cell.

The different map dimensions reflect separate mapping sessions.

### Saved Map Files

```text
/home/wheeltec/robot_b_map_initial.pgm
/home/wheeltec/robot_b_map_initial.yaml
/home/wheeltec/robot_b_map_verified.pgm
/home/wheeltec/robot_b_map_verified.yaml
```

The verified map was saved before the final reboot.

The post-reboot map was successfully published but was not separately exported.

### Verified Map-Saving Command

```bash
ros2 run nav2_map_server map_saver_cli -f ~/robot_b_map_verified --ros-args -p save_map_timeout:=15.0 -r map:=/robot_b/map
```

### Local Backup

```text
/home/wheeltec/robot_b_working_backup/
```

Files verified in the backup:

```text
lsm10_p_robot_b.yaml
robot_b_all.launch.py
robot_b_ekf.yaml
robot_b_imu.yaml
robot_b_map_initial.pgm
robot_b_map_initial.yaml
robot_b_map_verified.pgm
robot_b_map_verified.yaml
robot_b_scan_normalizer.py
robot_b_slam.yaml
```

All 10 files were copied into the repository's `robot_b/` directory and pushed to GitHub.

---

## 5. Robot B — IMU and TF Troubleshooting

### Problem

Robot B initially experienced inconsistent EKF performance and SLAM mapping failures.

Observed symptoms included:

- EKF output around 2.46 Hz.
- SLAM Toolbox not publishing a map.
- Scan queue warnings.
- Missing or unavailable transforms for IMU processing.

### Root Cause

The raw IMU topic used:

```text
/imu/data_raw
```

The message header referenced:

```text
gyro_link
```

However, the existing static transform configuration published the namespaced frame:

```text
robot_b/gyro_link
```

The missing legacy frame prevented the localization pipeline from consistently transforming the IMU measurements.

### Solution

Added a static transform:

```text
robot_b/base_footprint -> gyro_link
```

The existing namespaced transform was retained:

```text
robot_b/base_footprint -> robot_b/gyro_link
```

The legacy transform was added permanently to:

```text
/home/wheeltec/robot_b_all.launch.py
```

### Results

After applying the fix:

- EKF reached approximately 20 Hz.
- SLAM generated maps.
- Map saving succeeded.
- The corrected configuration continued working after a full Jetson reboot.

### Future Work

The legacy `gyro_link` frame must be addressed during multi-robot TF isolation.

Any changes must preserve the IMU-to-base transform relationship and be followed by EKF and SLAM verification.

---

## 6. Historical Robot B Troubleshooting

The following problems occurred during earlier lab sessions before the current unified launch configuration.

### LiDAR Problems

Observed:

- LiDAR crashed when launched through `wheeltec_sensors.launch.py`.
- `/scan` initially reported zero publishers.
- `lslidar_driver_node` sometimes exited with code -6.
- Launching the LiDAR separately allowed scan publication.
- LiDAR published at approximately 12 Hz.

Historical standalone LiDAR command:

```bash
ros2 launch turn_on_wheeltec_robot wheeltec_lidar.launch.py
```

The current unified launch initializes the LiDAR successfully.

A minimum-range warning may still appear because the configured minimum range is 0.0 m while the LiDAR's supported minimum is approximately 0.2 m.

This warning did not prevent successful mapping.

### Camera Problems

The generic camera topic:

```text
/camera/color/image_raw
```

previously showed no publisher on Robot B.

The correct camera topic observed during earlier testing was:

```text
/rosbot2_138/color/image_raw
```

The camera stream was not revalidated during the latest unified-launch reboot test.

### SLAM Problems

Earlier SLAM sessions experienced:

- Laser scan reading-count mismatches.
- Delayed map publication.
- RViz warnings.
- Mapping failures before sensor initialization.

The custom scan normalizer and corrected IMU transform resolved the principal issues encountered during the latest standalone mapping configuration.

---

## 7. Historical Teleoperation and RViz Testing

Both robots previously completed the following tests:

- SSH connection.
- Forward movement.
- Backward movement.
- Left turning.
- Right turning.
- LiDAR access.
- Camera access.
- RViz visualization.
- Individual SLAM mapping.
- Map saving.

### Historical Keyboard Command

```bash
ros2 run wheeltec_robot_keyboard wheeltec_keyboard
```

### Historical RViz Configuration Paths

Robot A:

```text
/home/jetson/.rviz2/robotA.rviz
```

Robot B:

```text
/home/jetson/.rviz2/robotB.rviz
```

The original notes recorded these files as present on October 26, 2026.

The paths should be verified again before use in the current integrated system.

### Historical WheelTec Launch Commands

Base driver:

```bash
ros2 launch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch.py
```

Sensors:

```bash
ros2 launch turn_on_wheeltec_robot wheeltec_sensors.launch.py
```

SLAM:

```bash
ros2 launch wheeltec_slam_toolbox online_async_launch.py
```

Standalone LiDAR:

```bash
ros2 launch turn_on_wheeltec_robot wheeltec_lidar.launch.py
```

These commands are preserved as historical references.

**Do not run duplicate drivers or SLAM instances alongside the current unified launch files.**

---

## 8. ROS 2 Networking Experiment — Completed

An earlier networking experiment successfully demonstrated ROS 2 message transmission from Robot A to Robot B and the visualization Jetson.

### Network Configuration

All three machines were documented as using the default ROS domain:

```text
ROS_DOMAIN_ID = 0
```

The `ROS_DOMAIN_ID` environment variable was unset, meaning ROS 2 used the default domain.

### Robot A — Publisher

Robot A published a text message:

```bash
ros2 topic pub /robotA_demo_message std_msgs/msg/String "{data: 'hello from robot A'}" -r 1
```

The publisher transmitted at approximately one message per second.

### Visualization Jetson — Subscriber

The Jetson sourced ROS 2 Humble:

```bash
source /opt/ros/humble/setup.bash
```

The topic was discovered:

```bash
ros2 topic list | grep robotA
```

Result:

```text
/robotA_demo_message
```

The message type was checked:

```bash
ros2 topic type /robotA_demo_message
```

Result:

```text
std_msgs/msg/String
```

The Jetson subscribed:

```bash
ros2 topic echo /robotA_demo_message
```

Received:

```text
data: hello from robot A
```

### Robot B — Subscriber

Robot B subscribed using:

```bash
ros2 topic echo /robotA_demo_message
```

Robot B successfully received:

```text
data: hello from robot A
```

### Verified Networking Results

- Robot A published a ROS 2 message over TWIST Wi-Fi.
- The visualization Jetson discovered Robot A's topic.
- The visualization Jetson received Robot A's message.
- Robot B discovered Robot A's topic.
- Robot B received Robot A's message.
- ROS 2 discovery and one-way message transmission worked across the machines using the default domain.

### Important Limitation

This experiment demonstrated:

```text
Robot A -> Robot B
Robot A -> Visualization Jetson
```

It did not yet demonstrate:

```text
Robot B -> Robot A
```

Bidirectional communication still requires testing.

The experiment also did not establish that both robots could run their complete SLAM pipelines simultaneously without topic or TF conflicts.

---

## 9. Multi-Robot Namespace and TF Audit — Pending

Both robots have completed standalone SLAM, but their configurations have not yet been fully audited for simultaneous operation.

### Topics Requiring Review

```text
/scan
/odom
/imu/data_raw
/imu/data
/cmd_vel
/map
/tf
/tf_static
```

Robot B's verified pipeline already uses several namespaced topics:

```text
/robot_b/scan_fixed
/robot_b/odom_combined
/robot_b/map
```

However, some raw sensor and command topics remain global.

### TF Frames Requiring Review

```text
map
odom
base_link
base_footprint
gyro_link
laser
camera_link
```

### Intended Naming Structure

Examples of the planned topic organization:

```text
/robot_a/odom
/robot_a/scan
/robot_a/map

/robot_b/odom
/robot_b/scan
/robot_b/map
```

These names represent the intended architecture, not a completed configuration.

### Important TF Consideration

ROS 2 commonly uses shared `/tf` and `/tf_static` topics.

The robots must have uniquely identifiable TF frame IDs to prevent collisions.

Robot B's legacy `gyro_link` frame requires particular attention.

### Safety Consideration

The robots must not unintentionally subscribe to each other's velocity commands.

Before simultaneous operation, verify command topics, subscriptions, remappings, and the behavior of each base driver.

---

## 10. GitHub and Repository Backup

**GitHub Username:** `benjaminventurazaldana`

**Repository:**

https://github.com/benjaminventurazaldana/rosbot-dual-slam

### Robot A

- Unified launch configuration saved.
- Working configuration backed up locally.
- Verified map files saved.
- Repository files committed and pushed.
- Latest Robot A commit before Robot B upload: `15b4ad1`.

### Robot B

- Unified launch configuration saved.
- Working configuration backed up locally.
- Verified map files saved.
- All 10 files added to the repository.
- Git commit completed successfully.
- Commit pushed to `main`.

Robot B commit:

```text
d42d79f — Add Robot B verified SLAM configuration and maps
```

### Local Development Environment

The repository was synchronized to the Windows development computer using GitHub Desktop.

Both `robot_a/` and `robot_b/` directories were visible in VS Code.

Documentation changes made after this point must be committed and pushed separately.

---

## 11. Research Progress Checklist

| Task | Robot A | Robot B |
|---|---|---|
| SSH connection | Complete | Complete |
| Manual teleoperation | Complete (historical) | Complete (historical) |
| LiDAR testing | Complete | Complete |
| Camera testing | Complete (historical) | Complete (historical) |
| RViz visualization | Complete (historical) | Complete (historical) |
| IMU and EKF configuration | Complete | Complete |
| Standalone SLAM | Complete | Complete |
| Occupancy-grid map generated | Complete | Complete |
| Map saved | Complete | Complete |
| Unified launch file | Complete | Complete |
| Full reboot verification | Complete | Complete |
| Local backup | Complete | Complete |
| GitHub backup | Complete | Complete |
| Namespace isolation | Pending | Pending |
| Simultaneous SLAM | Pending | Pending |
| Autonomous navigation | Pending | Pending |
| Autonomous exploration | Pending | Pending |
| Cooperative map fusion | Pending | Pending |

### Communication Progress

| Communication Test | Status |
|---|---|
| Robot A -> Visualization Jetson | Completed (historical) |
| Robot A -> Robot B | Completed (historical) |
| Robot B -> Robot A | Pending |
| Bidirectional messaging demonstration | Pending |
| Sensor and pose sharing | Pending |
| Map sharing | Pending |
| Cooperative map fusion | Pending |

---

## 12. Current Demo Readiness

### Robot A

Verified standalone capabilities:

1. SSH connection.
2. Unified ROS 2 launch.
3. LiDAR processing.
4. EKF localization.
5. Occupancy-grid SLAM.
6. Saved map.
7. Successful full reboot test.

Historical capabilities requiring revalidation in the current setup:

- Keyboard teleoperation.
- Camera visualization.
- RViz configuration loading.

### Robot B

Verified standalone capabilities:

1. SSH connection.
2. Unified ROS 2 launch.
3. LiDAR processing.
4. IMU filtering.
5. EKF localization at approximately 20 Hz.
6. Occupancy-grid SLAM.
7. Saved map.
8. Successful full reboot test.

Historical capabilities requiring revalidation in the current setup:

- Keyboard teleoperation.
- Camera visualization.
- RViz configuration loading.

### ROS Networking

Previously demonstrated:

1. Robot A publishes a ROS 2 message.
2. Visualization Jetson receives the message.
3. Robot B receives the message.
4. All machines discover the topic using the default ROS domain.

Still required:

1. Robot B publishes to Robot A.
2. Verify bidirectional communication with both robots online.
3. Confirm there are no conflicting robot-control or TF topics.

---

## 13. Current Research Milestones

### Milestone 1 — Robot A Standalone SLAM

**Status: COMPLETE**

Robot A can initialize its mapping pipeline, generate occupancy-grid maps, save maps, and restart successfully after reboot.

### Milestone 2 — Robot B Standalone SLAM

**Status: COMPLETE**

Robot B can initialize its mapping pipeline, generate occupancy-grid maps, save maps, and restart successfully after reboot.

### Milestone 3 — ROS 2 Communication

**Status: PARTIALLY COMPLETE**

Historical testing demonstrated Robot A publishing to Robot B and the visualization Jetson.

Bidirectional communication and integration with the current standalone launch configurations remain pending.

### Milestone 4 — Namespace and TF Isolation

**Status: PENDING**

Audit and correct conflicting topic names, command channels, node names, and TF frames.

Preserve the working standalone configurations while making changes.

### Milestone 5 — Simultaneous SLAM

**Status: PENDING**

Operate both robots at the same time without sensor, localization, command, or TF interference.

### Milestone 6 — Autonomous Navigation and Exploration

**Status: PENDING**

Configure safe autonomous movement, obstacle avoidance, and autonomous environmental exploration.

### Milestone 7 — Cooperative Map Sharing and Fusion

**Status: PENDING**

Exchange maps, align independently generated maps, and combine them into a shared environmental representation.

### Milestone 8 — Final Research Demonstration

**Status: PENDING**

Target: April 2027.

---

## 14. Immediate Next Steps

1. Audit Robot A's existing topics, remappings, nodes, and TF frames.
2. Audit Robot B's existing topics, remappings, nodes, and TF frames.
3. Identify shared names that could cause interference.
4. Implement safe robot-specific naming and remapping.
5. Verify standalone SLAM still works after changes.
6. Confirm ROS domain and DDS discovery settings.
7. Demonstrate Robot A-to-B and Robot B-to-A messaging.
8. Capture terminal output or screenshots as evidence for Dr. Roy.
9. Run both robots simultaneously.
10. Begin cooperative mapping integration.

**Immediate priority:** Complete bidirectional robot-to-robot messaging and obtain reproducible evidence for Dr. Roy.

---

## 15. Current Stopping Point — November 11, 2026

Robot A and Robot B have both completed:

- Standalone ROS 2 mapping configuration.
- Unified launch setup.
- EKF and SLAM verification.
- Occupancy-grid map generation.
- Map saving.
- Full reboot verification.
- Local configuration backups.
- GitHub uploads.

The next technical task is the multi-robot namespace and TF audit.

**No multi-robot configuration changes have been made as part of this new phase.**

The working standalone configurations should be preserved while multi-robot communication, simultaneous SLAM, autonomous exploration, and map fusion are developed.
---

## November 18, 2026 — Simultaneous mapping, Robot A recovery, and offline fusion

**Operator context:** Two WheelTec robots were parked near the shared laboratory doorway, facing approximately parallel at startup. Robot A was positioned on the right and Robot B on the left, separated by approximately 29 in (0.7366 m) center-to-center. Exploration was through supervised keyboard teleoperation, **not autonomous exploration**.

**Robot endpoints / topics**
- Robot A: `ssh wheeltec@192.168.0.224`, launcher `ros2 launch ~/robot_a_all.launch.py`, map `/robot_a/map`, odometry `/robot_a/odom_combined`, teleop `/robot_a/cmd_vel`.
- Robot B: `ssh wheeltec@192.168.0.138`, launcher `ros2 launch ~/robot_b_all.launch.py`, map `/robot_b/map`, odometry `/robot_b/odom_combined`. The base driver was observed subscribing to global `/cmd_vel`; this needs namespace isolation review.
- Both robots ran independent mapping stacks at the same time and were able to exchange ROS map data through the shared network. This is not proof that the independent TF trees were correctly linked.

### Mapping results and recovery

| Map | Grid dimensions | Resolution | Known cells / observations |
|---|---:|---:|---|
| Robot A first attempt | 811 × 1122 | 0.05 m/cell | 85,940 free; 6,462 occupied; ~10.15% known; badly fragmented geometry |
| Robot A retry | 204 × 162 | 0.05 m/cell | Coherent room boundaries and recognizable obstacles in visual inspection |
| Robot B final | 218 × 221 | 0.05 m/cell | 18,378 free; 1,771 occupied; ~41.82% known; coherent room outline |

Robot A's original saved map showed disconnected scan clusters over very large map bounds. Its EKF `/robot_a/odom_combined` at the end of the first run reported approximately `x=18.29, y=11.31` and unusually high X/Y pose covariance diagonals (~80,520 and ~169,463 m²). Raw wheel odometry at one sample reported `x=0.16, y=-2.83, z=3.81`, which was suspicious for a ground robot; different odometry frames make the positions themselves non-directly-comparable.

The active Robot A EKF YAML was `/home/wheeltec/robot_a_ekf.yaml`, with `two_d_mode: true`, wheel odometry `/robot_a/odom`, and IMU `/robot_a/imu/data_raw`. IMU samples contained orientation and yaw-rate data; sporadic EKF update-rate warnings were observed. **No root cause was proven and no EKF YAML change was made as part of this recovery.**

After stopping the Robot A launcher, manually repositioning Robot A, and restarting `~/robot_a_all.launch.py`, its stationary EKF pose remained zero. Robot A then completed another manual lab route; near its returned starting location, EKF pose read `x=-0.0648, y=-0.0507, z=0`. Returning close to the origin is encouraging but is **not** sufficient proof of odometry accuracy.

The successful retry was saved separately under `robot_a_retry`. The earlier distorted map was deliberately retained, not overwritten.

### Offline map registration (November 18)

Input files:
- `maps/live_session_nov18/robot_a_retry.pgm` and `.yaml`
- `maps/live_session_nov18/robot_b_final.pgm` and `.yaml`

Versioned script: `scripts/dual_slam_fusion_nov18.py`. The search is coarse-to-fine over rotation and translation with a *soft* preference around 0° rotation and (0, +0.7366 m) relative offset, derived from the robots' approximate starting arrangement. Its search can choose values outside that prior.

Actual algorithm result:

```text
Rotation B -> A: -17.50 degrees
Translation B -> A: (-0.050, 0.500) m
Obstacle proximity: 0.7191
Conflict ratio: 0.0898
Known overlap: 32183 cells
Registration score: 1.5436
```

The alignment overlay shows many matching exterior walls and interior obstacles, plus localized wall offsets and raster artifacts. This is **promising but not ground-truth validated**. The fused grid is experimental and must not be used as a navigation or safety map.

Output files:
- `maps/live_session_nov18/fusion/dual_slam_nov18_alignment.png`
- `maps/live_session_nov18/fusion/dual_slam_nov18_fused_preview.png`
- `maps/live_session_nov18/fusion/dual_slam_nov18_fused_map.pgm`
- `maps/live_session_nov18/fusion/dual_slam_nov18_fused_map.yaml`

Original maps, old fusion scripts, and experimental November 16 artifacts remain preserved. The fusion run did **not** publish TF or alter running ROS nodes.

### Reproducibility and backup

With this repo in `/home/wheeltec/rosbot-dual-slam` and required Python packages installed:

```bash
cd /home/wheeltec
python3 -u ~/rosbot-dual-slam/scripts/dual_slam_fusion_nov18.py
```

The script has a hard-coded `/home/wheeltec` base path; adapt for other machines. Original November 18 mapping data and the script were pushed to `main` as **`729aad6`**. Both robots were safely shut down after backups.

### Follow-up tasks
1. Validate B→A transform with measured physical landmarks and overlap/conflict inspection.
2. Diagnose the original Robot A mapping/EKF failure and repeat a short controlled-motion test as necessary.
3. Audit namespaced TF and velocity command topics; avoid reintroducing global frame conflicts.
4. Add a validated transform and robust automatic registration to live fusion.
5. Add quantitative evaluation, repeatable procedures, and eventually autonomous navigation/exploration.

