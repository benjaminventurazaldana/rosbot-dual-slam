# Lab Notes

## Robot Information
Robot 1 IP: 192.168.0.224  
Robot 2 IP: 192.168.0.138  
ROS_DOMAIN_ID: Not configured yet  
ROS 2 version: Humble  

## Robot 1
LiDAR topic: /scan  
Camera topic: /camera/color/image_raw  
Fixed frame: map  
SLAM package: wheeltec_slam_toolbox  
SLAM launch: online_async_launch.py  

Saved map:
- /home/wheeltec/robotA_map.pgm
- /home/wheeltec/robotA_map.yaml

RViz config:
- /home/jetson/.rviz2/robotA.rviz

## Robot 2
LiDAR topic: /scan  
Camera topic: /rosbot2_138/color/image_raw  
Fixed frame: map  
SLAM package: wheeltec_slam_toolbox  
SLAM launch: online_async_launch.py  

Saved map:
- /home/wheeltec/robotB_map.pgm
- /home/wheeltec/robotB_map.yaml

RViz config:
- /home/jetson/.rviz2/robotB.rviz

## Commands That Worked

### Main Robot Launch
```bash
ros2 launch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch.py
```

### Sensors
```bash
ros2 launch turn_on_wheeltec_robot wheeltec_sensors.launch.py
```

### SLAM
```bash
ros2 launch wheeltec_slam_toolbox online_async_launch.py
```

### Keyboard Control
```bash
ros2 run wheeltec_robot_keyboard wheeltec_keyboard
```

### Standalone LiDAR
```bash
ros2 launch turn_on_wheeltec_robot wheeltec_lidar.launch.py
```

### Check LiDAR Rate
```bash
ros2 topic hz /scan
```

### Save Robot A Map
```bash
ros2 run nav2_map_server map_saver_cli -f ~/robotA_map
```

### Save Robot B Map
```bash
ros2 run nav2_map_server map_saver_cli -f ~/robotB_map
```

### Jetson RViz
```bash
source /opt/ros/humble/setup.bash
rviz2 -d /home/jetson/.rviz2/robotA.rviz
rviz2 -d /home/jetson/.rviz2/robotB.rviz
```

## Errors / Problems

### Robot B LiDAR
- LiDAR crashed when started through `wheeltec_sensors.launch.py`
- `/scan` showed Publisher count: 0
- `lslidar_driver_node` exited with code -6
- Launching `wheeltec_lidar.launch.py` separately worked
- LiDAR then published `/scan` at approximately 12 Hz

### Robot B Camera
- `/camera/color/image_raw` had no publisher
- Correct Robot B camera topic:
  `/rosbot2_138/color/image_raw`

### Robot B SLAM
- SLAM initially showed mismatched `LaserRangeScan` reading counts
- Restarting SLAM after the LiDAR was publishing allowed the map to appear in RViz

## Completed Progress
- Connected to Robot 1 over SSH
- Controlled Robot 1 forward, backward, left, and right
- Accessed Robot 1 camera and LiDAR
- Visualized Robot 1 camera and LiDAR in RViz
- Completed single-robot SLAM for Robot 1
- Saved Robot 1 map
- Saved Robot 1 RViz configuration

- Connected to Robot 2 over SSH
- Controlled Robot 2 forward, backward, left, and right
- Accessed Robot 2 camera and LiDAR
- Visualized Robot 2 camera and LiDAR in RViz
- Completed single-robot SLAM for Robot 2
- Saved Robot 2 map
- Saved Robot 2 RViz configuration

## Saved Files Verified

Robot 1:
- `/home/wheeltec/robotA_map.pgm`
- `/home/wheeltec/robotA_map.yaml`

Robot 2:
- `/home/wheeltec/robotB_map.pgm`
- `/home/wheeltec/robotB_map.yaml`

Jetson:
- `/home/jetson/.rviz2/robotA.rviz`
- `/home/jetson/.rviz2/robotB.rviz`

All four saved files were verified to still exist on October 26, 2026.

## Demo Readiness
For each robot, the current demo can show:
1. SSH connection from laptop
2. Robot movement using keyboard teleoperation
3. LiDAR data in RViz
4. Camera feed in RViz
5. SLAM map generation in RViz
6. Previously saved map files
7. Saved RViz configuration

## Next Project Step
- ROS 2 networking / ROS_DOMAIN_ID
- Send a ROS message between machines
- Bring both robots online together
- Prepare for multi-robot SLAM