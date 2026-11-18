
# ROS 2 Commands — Dual-SLAM Research

**Project:** Cooperative Multi-Robot Mapping: A Dual-SLAM Approach via Wireless Edge Computing  
**Lab:** UTA TWIST Lab — Dr. Debashri Roy  
**Last Updated:** November 18, 2026

This document contains verified commands for Robot A and Robot B, general ROS 2 utilities, troubleshooting instructions, and legacy commands from earlier lab sessions.

**Important (November 18):** Simultaneous independent SLAM, cross-robot map topic sharing, manually guided lab mapping, and experimental offline fusion were demonstrated. Ground-truth registration validation, robust TF integration, and autonomy remain pending. Older sections are retained for historical procedures; use the newest workflow below for current topic names.

---

## 1. Robot Information

| Property | Robot A | Robot B |
|---|---|---|
| IP Address | `192.168.0.224` | `192.168.0.138` |
| SSH Username | `wheeltec` | `wheeltec` |
| ROS Version | ROS 2 Humble | ROS 2 Humble |
| Unified Launch | `~/robot_a_all.launch.py` | `~/robot_b_all.launch.py` |
| Map Topic | `/robot_a/map` | `/robot_b/map` |
| Saved Map | `robot_a_map_verified` | `robot_b_map_verified` |
| Standalone SLAM | Verified | Verified |
| Reboot Test | Passed | Passed |

Both robots use NVIDIA Jetson computers and WheelTec mobile robot platforms.

---

## 2. General ROS 2 Commands

### Source ROS 2 Humble

```bash
source /opt/ros/humble/setup.bash
```

### List Nodes

```bash
ros2 node list
```

### List Topics

```bash
ros2 topic list
```

### List Topics With Message Types

```bash
ros2 topic list -t
```

### View Topic Data

Replace `<topic>` with the actual topic name.

```bash
ros2 topic echo <topic>
```

### View One Message

```bash
ros2 topic echo <topic> --once
```

### Check Topic Frequency

```bash
ros2 topic hz <topic>
```

Allow several seconds for the average frequency to stabilize. Press Ctrl+C to stop.

### Check Publishers and Subscribers

```bash
ros2 topic info <topic> -v
```

### Check Topic Message Type

```bash
ros2 topic type <topic>
```

### Run a ROS Executable

```bash
ros2 run <package> <executable>
```

### Launch a ROS Package

```bash
ros2 launch <package> <launch_file>
```

### Check ROS Domain

```bash
echo ${ROS_DOMAIN_ID:-0}
```

If `ROS_DOMAIN_ID` is unset, ROS 2 normally uses domain 0.

---

## 3. Robot A — Verified Startup

### Terminal A1 — Connect to Robot A

```bash
ssh wheeltec@192.168.0.224
```

### Terminal A1 — Start Complete Mapping System

```bash
ros2 launch ~/robot_a_all.launch.py
```

This unified launcher starts the components required for Robot A's verified standalone mapping pipeline, including:

- WheelTec base driver
- Required static transforms
- IMU and localization components
- EKF odometry
- LiDAR driver
- Custom scan normalizer
- Asynchronous SLAM Toolbox

Keep this terminal running.

**Do not launch duplicate WheelTec drivers, LiDAR drivers, or SLAM nodes alongside the unified launcher.**

### Terminal A2 — Connect to Robot A

Open a separate terminal:

```bash
ssh wheeltec@192.168.0.224
```

### Verify ROS Nodes

```bash
ros2 node list
```

### Verify Topics

```bash
ros2 topic list -t
```

### Verify Map Publication

```bash
ros2 topic echo /map --once --field info
```

Previously verified results:

- Map resolution: 0.05 meters per cell
- Recorded dimensions: 146 × 181 cells
- Approximate map dimensions: 7.30 × 9.05 meters

Map dimensions can change between SLAM sessions.

### Save Robot A Map

The verified saved map prefix is:

```text
robot_a_map_verified
```

The following command uses an explicit map remapping and extended timeout:

```bash
ros2 run nav2_map_server map_saver_cli -f ~/robot_a_map_verified --ros-args -p save_map_timeout:=15.0 -r map:=/map
```

This is the recommended command form; the exact command used during Robot A's earlier successful export should be cross-checked against the original lab log.

### Verify Saved Map Files

```bash
ls -lh ~/robot_a_map_verified.*
```

Expected files:

```text
robot_a_map_verified.pgm
robot_a_map_verified.yaml
```

### Robot A Reboot Verification

Robot A's unified mapping setup was successfully tested after a full Jetson reboot.

The saved verified map and working launch configuration were backed up locally and pushed to GitHub.

---

## 4. Robot B — Verified Startup

### Terminal B1 — Connect to Robot B

```bash
ssh wheeltec@192.168.0.138
```

### Terminal B1 — Start Complete Mapping System

```bash
ros2 launch ~/robot_b_all.launch.py
```

The verified unified launcher starts:

- WheelTec base driver
- Madgwick IMU filter
- robot_localization EKF
- Static TF publishers
- LSLiDAR M10_P driver
- Python LiDAR scan normalizer
- Asynchronous SLAM Toolbox

Keep this terminal running.

### Terminal B2 — Connect to Robot B

Open a second terminal:

```bash
ssh wheeltec@192.168.0.138
```

### Verify ROS Nodes

```bash
ros2 node list
```

Expected nodes include:

```text
/robot_b_base_driver
/imu_filter_madgwick
/ekf_filter_node
/robot_b/lslidar_driver_node
/robot_b/slam_toolbox
/robot_b_scan_normalizer
```

Additional static transform publishers and transform listener nodes are expected.

### Verify LiDAR

```bash
ros2 topic hz /robot_b/scan_fixed
```

The scan normalizer produces 1440 range readings per scan.

### Verify EKF Odometry

```bash
ros2 topic hz /robot_b/odom_combined
```

**Verified after full reboot:** Approximately 19.92 Hz.

### Verify Map Topic

```bash
ros2 topic list -t
```

Look for:

```text
/robot_b/map [nav_msgs/msg/OccupancyGrid]
```

### Verify Map Publication

```bash
timeout 15 ros2 topic echo /robot_b/map --once --field info
```

Post-reboot verified output:

```text
resolution: 0.05000000074505806
width: 144
height: 168
```

This corresponds to approximately 7.20 × 8.40 meters in map dimensions.

The map may take time to appear after SLAM starts.

### Save Robot B Map

```bash
ros2 run nav2_map_server map_saver_cli -f ~/robot_b_map_verified --ros-args -p save_map_timeout:=15.0 -r map:=/robot_b/map
```

This command successfully saved the verified map during testing.

### Verify Saved Files

```bash
ls -lh ~/robot_b_map_verified.*
```

Expected files:

```text
robot_b_map_verified.pgm
robot_b_map_verified.yaml
```

### Robot B Local Backup

The working configuration was backed up to:

```text
/home/wheeltec/robot_b_working_backup/
```

The backup contains:

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

### Robot B Reboot Verification

Robot B passed a complete Jetson reboot test on November 11, 2026.

After reconnecting over SSH:

1. The unified launch started all 11 configured processes.
2. The base driver and LiDAR initialized successfully.
3. EKF odometry stabilized at approximately 19.92 Hz.
4. SLAM Toolbox remained operational.
5. `/robot_b/map` published a valid occupancy grid.

The post-reboot map was not separately exported; the verified map files were saved before reboot.

---

## 5. Robot B — Important IMU and TF Fix

During standalone testing, Robot B initially had a transform mismatch.

Raw IMU messages used:

```text
gyro_link
```

However, the existing static transform configuration used:

```text
robot_b/gyro_link
```

The EKF could not consistently transform the IMU data, and SLAM failed to generate a map.

The working solution added a legacy static transform:

```text
robot_b/base_footprint -> gyro_link
```

The unified launch file also retains the namespaced transform:

```text
robot_b/base_footprint -> robot_b/gyro_link
```

After adding the missing transform:

- EKF reached approximately 20 Hz.
- SLAM generated occupancy-grid maps.
- The system continued working after reboot.

**Important for multi-robot integration:** The unprefixed `gyro_link` frame is a potential naming conflict and must be reviewed before both robots operate simultaneously.

Do not remove or rename this transform without coordinating the corresponding IMU message frame IDs and verifying the entire localization pipeline.

---

## 6. Camera and RViz — Historical Commands

The following commands and paths come from earlier lab sessions. They are retained for reference but have not all been revalidated with the current unified launch files.

### Robot A — Previously Observed Camera Topic

```text
/camera/color/image_raw
```

Check the topic if present:

```bash
ros2 topic hz /camera/color/image_raw
```

### Robot B — Previously Observed Camera Topic

```text
/rosbot2_138/color/image_raw
```

Check the topic if present:

```bash
ros2 topic hz /rosbot2_138/color/image_raw
```

Camera drivers are not confirmed to be part of the current unified SLAM launch files.

### Launch RViz

```bash
rviz2
```

### Historical RViz Configuration Paths

Robot A:

```bash
rviz2 -d /home/jetson/.rviz2/robotA.rviz
```

Robot B:

```bash
rviz2 -d /home/jetson/.rviz2/robotB.rviz
```

These paths were recorded during earlier lab sessions and must be checked against the current Jetson home directories before reuse.

---

## 7. Keyboard Teleoperation — Historical Command

Previously used WheelTec keyboard control:

```bash
ros2 run wheeltec_robot_keyboard wheeltec_keyboard
```

This command was used during earlier testing.

Before using keyboard control with the unified launch configuration, verify the robot's active command topic and ensure that teleoperation targets only the intended robot.

**Do not operate both robots simultaneously using an unverified shared `/cmd_vel` topic.**

---

## 8. Quick Troubleshooting

### Check ROS Nodes

```bash
ros2 node list
```

### Check Available Topics

```bash
ros2 topic list -t
```

### Check SLAM Nodes

```bash
ros2 node list | grep slam
```

### Check Robot A Map

```bash
timeout 15 ros2 topic echo /map --once --field info
```

### Check Robot B Map

```bash
timeout 15 ros2 topic echo /robot_b/map --once --field info
```

### Check Robot B Scan

```bash
ros2 topic hz /robot_b/scan_fixed
```

### Check Robot B Odometry

```bash
ros2 topic hz /robot_b/odom_combined
```

### Check Robot B Map Publisher

```bash
ros2 topic info /robot_b/map -v
```

### Check Robot B SLAM Node

```bash
ros2 node info /robot_b/slam_toolbox
```

### Check Robot B EKF Diagnostics

```bash
ros2 topic echo /diagnostics
```

### Check Robot B IMU Frame

```bash
ros2 topic echo /imu/data_raw --once --field header
```

### Check ROS Domain

```bash
echo ${ROS_DOMAIN_ID:-0}
```

### If Map Publication Is Delayed

1. Confirm the unified launch is still running.
2. Check `ros2 node list`.
3. Check `ros2 topic list -t`.
4. Verify odometry and scan publication.
5. Retry the map query after SLAM has had time to initialize.

Do not immediately restart the system simply because a map query times out once.

---

## 9. Legacy WheelTec Commands

These commands were used during earlier manual startup sessions.

They are retained for historical reference and component-level troubleshooting.

**Do not run them alongside the unified launch files unless the relevant duplicate components have been deliberately disabled.**

### Base Driver

```bash
ros2 launch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch.py
```

### Sensors

```bash
ros2 launch turn_on_wheeltec_robot wheeltec_sensors.launch.py
```

### Standalone LiDAR

```bash
ros2 launch turn_on_wheeltec_robot wheeltec_lidar.launch.py
```

### Asynchronous SLAM

```bash
ros2 launch wheeltec_slam_toolbox online_async_launch.py
```

### Keyboard Control

```bash
ros2 run wheeltec_robot_keyboard wheeltec_keyboard
```

These commands are not the recommended current startup procedure.

Use the unified Robot A or Robot B launcher instead.

---

## 10. Multi-Robot Networking — Pending

The following work has not yet been completed.

### ROS Domain

Robot B was confirmed to use:

```text
ROS_DOMAIN_ID=0
```

Robot A's current domain configuration still needs verification.

The intended communication architecture is not yet finalized.

A shared ROS domain with isolated robot namespaces is a candidate approach for direct ROS 2 communication.

### Potential Topic Conflicts

Review shared topics including:

```text
/odom
/imu/data_raw
/imu/data
/cmd_vel
/tf
/tf_static
```

Some of these topics are currently global rather than robot-specific.

### Potential TF Frame Conflicts

Review:

```text
gyro_link
base_link
base_footprint
odom
map
laser
```

Robot-specific TF frames must be uniquely identifiable.

The standard shared `/tf` and `/tf_static` topics can remain shared when their frame identifiers and publishers are correctly coordinated.

### Intended Topic Organization

Examples:

```text
/robot_a/odom
/robot_a/scan
/robot_a/map

/robot_b/odom
/robot_b/scan
/robot_b/map
```

These are target naming examples, not confirmation that all remappings have been implemented.

### Bidirectional Communication Demonstration

Planned test:

1. Connect both Jetsons to TWIST Wi-Fi.
2. Verify ROS 2 domain and DDS discovery settings.
3. Publish a test message from Robot A.
4. Receive the message on Robot B.
5. Publish a response from Robot B.
6. Receive the response on Robot A.
7. Record terminal output or screenshots as proof.

This demonstration is a priority for Dr. Roy.

Do not use motor-command topics for the initial communication test.

---

## 11. Safe Shutdown

Stop active ROS 2 launch processes with Ctrl+C before shutting down when practical.

### Shutdown Jetson

```bash
sudo shutdown now
```

### Reboot Jetson

```bash
sudo reboot
```

SSH sessions will disconnect during shutdown or reboot.

Reconnect using the appropriate robot IP address.

---

## 12. GitHub Repository

**GitHub Username:** `benjaminventurazaldana`

**Repository:**

https://github.com/benjaminventurazaldana/rosbot-dual-slam

Both Robot A and Robot B standalone configurations have been backed up to the private repository.

Robot B's verified configuration was committed as:

```text
d42d79f — Add Robot B verified SLAM configuration and maps
```

### Check Local Git Status

```bash
git status
```

### Check Latest Commit

```bash
git log -1 --oneline
```

### Check Remote Repository

```bash
git remote -v
```

Git operations should be performed inside the repository directory.

Do not commit credentials, personal access tokens, SSH private keys, or other secrets.

---

## 13. Next Research Milestones

1. Audit Robot A and Robot B namespaces, topics, nodes, and TF frames.
2. Resolve naming conflicts without breaking standalone SLAM.
3. Configure ROS 2 networking and DDS discovery.
4. Demonstrate bidirectional robot-to-robot messaging.
5. Run both robots simultaneously without interference.
6. Exchange robot poses and mapping information.
7. Configure autonomous navigation and obstacle avoidance.
8. Implement autonomous exploration.
9. Develop cooperative map alignment and fusion.
10. Complete the integrated research demonstration.

**Historical stopping point (November 11):** Both standalone robot configurations were complete, reboot-tested, and backed up. See the November 18 workflow below for the subsequent simultaneous mapping and offline fusion milestone.
---

## November 18, 2026 — Verified dual-SLAM workflow (most recent)

**Use current namespaced topics.** Earlier commands elsewhere in this document may use historical `/map` or legacy TF references. November 18 verified Robot A as `/robot_a/map`, Robot B as `/robot_b/map`. Do not use old November 16 hard-coded alignment numbers for the new mapping session.

### Terminal assignments and startup

On separate SSH terminals (left = Robot A, right = Robot B):

**Robot A — Tab 1**
```bash
ssh wheeltec@192.168.0.224
source /opt/ros/humble/setup.bash
ros2 launch ~/robot_a_all.launch.py
```

**Robot B — Tab 1**
```bash
ssh wheeltec@192.168.0.138
source /opt/ros/humble/setup.bash
ros2 launch ~/robot_b_all.launch.py
```

Launchers must remain active while mapping. Use separate Tab 2 SSH sessions for diagnostic commands and map saving. Movement must be supervised, on clear paths, with the operator able to stop the robots.

### Teleoperation (historically verified during November 18)

**Robot A — Tab 2**
```bash
ssh wheeltec@192.168.0.224
source /opt/ros/humble/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/robot_a/cmd_vel
```

**Robot B — Tab 2**
```bash
ssh wheeltec@192.168.0.138
source /opt/ros/humble/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```

Robot B's global `/cmd_vel` subscription needs future namespace isolation; **do not assume the remapping is safe if the robot topology changes**. In teleop: `i` forward, `,` reverse, `j` left, `l` right, `k` stop, `x` decrease speed, Ctrl+C exit. Stop the robot before leaving its controller.

### Save both maps to Robot A (Tab 2)

The November 18 session demonstrated Robot A could subscribe to both map topics over ROS 2. Saving through Robot A creates a common session folder. If network discovery is unavailable, save each map on its own robot and transfer it afterwards.

```bash
ssh wheeltec@192.168.0.224
source /opt/ros/humble/setup.bash
mkdir -p ~/rosbot-dual-slam/maps/live_session_nov18

# Save a new Robot A mapping session under a unique prefix:
ros2 run nav2_map_server map_saver_cli \
  -t /robot_a/map \
  -f ~/rosbot-dual-slam/maps/live_session_nov18/robot_a_retry \
  --ros-args -p save_map_timeout:=15.0 \
  -p map_subscribe_transient_local:=false

ros2 run nav2_map_server map_saver_cli \
  -t /robot_b/map \
  -f ~/rosbot-dual-slam/maps/live_session_nov18/robot_b_final \
  --ros-args -p save_map_timeout:=15.0 \
  -p map_subscribe_transient_local:=false

ls -lh ~/rosbot-dual-slam/maps/live_session_nov18/
```

**For future sessions, change the directory and file prefixes** so that prior datasets are not overwritten. The exact saved November 18 inputs are already committed; there is no need to regenerate them.

### Inspect map metadata, EKF and topic health

```bash
cat ~/rosbot-dual-slam/maps/live_session_nov18/robot_a_retry.yaml
cat ~/rosbot-dual-slam/maps/live_session_nov18/robot_b_final.yaml
ros2 topic info /robot_a/odom_combined -v
ros2 topic echo /robot_a/odom_combined --once
ros2 topic echo /robot_a/odom --once
ros2 topic echo /robot_a/imu/data_raw --once
ros2 topic echo /robot_a/map --once --field info
ros2 topic echo /robot_b/map --once --field info
```

Only run live topic checks when the corresponding robot launchers are active. Raw wheel odometry and filtered EKF odometry are different coordinate frames, so comparing their XY coordinates directly does not establish drift. During the original Robot A run, anomalously large EKF covariance and a fragmented map were observed; diagnosis remains open.

### Offline fusion using committed November 18 maps

On Robot A or an equivalent Linux environment, with checkout under `/home/wheeltec/rosbot-dual-slam`, NumPy, SciPy, PyYAML, and OpenCV installed:

```bash
cd /home/wheeltec
python3 -u ~/rosbot-dual-slam/scripts/dual_slam_fusion_nov18.py
```

Expected output names under `/home/wheeltec/`:
```text
dual_slam_nov18_alignment.png
dual_slam_nov18_fused_preview.png
dual_slam_nov18_fused_map.pgm
dual_slam_nov18_fused_map.yaml
```

The committed output copies are in `maps/live_session_nov18/fusion/`. The script's absolute `HOME` constant must be adapted to run elsewhere. Registration results from this session: **−17.50°**, **(−0.050, +0.500) m**, **0.0898 conflict**, **32,183 known overlapping cells**. These are experimental diagnostics, not validated transform accuracy.

### Verify Git backup before shutdown

```bash
cd ~/rosbot-dual-slam
git status -sb
git log -1 --oneline
```

November 18 dataset commit: `729aad6`, successfully pushed to `main`. Stop launchers in Tab 1 using Ctrl+C, then shut down each robot through SSH if finished:

```bash
sudo shutdown -h now
```

This workflow does **not** deploy a validated inter-robot TF link and does **not** enable autonomous navigation.

