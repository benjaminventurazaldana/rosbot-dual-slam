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
