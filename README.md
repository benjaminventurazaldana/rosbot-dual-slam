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