# Lab Notes

## Robot Information
Robot 1 IP: 192.168.0.224  
Robot 2 IP: 192.168.0.138  
ROS_DOMAIN_ID: 0  
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

### Robot 1
- Connected to Robot 1 over SSH
- Controlled Robot 1 forward, backward, left, and right
- Accessed Robot 1 camera and LiDAR
- Visualized Robot 1 camera and LiDAR in RViz
- Completed single-robot SLAM for Robot 1
- Saved Robot 1 map
- Saved Robot 1 RViz configuration

### Robot 2
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

All saved files were verified to still exist on October 26, 2026.

## ROS 2 Networking Test

ROS 2 networking was successfully tested between Robot A, Robot B, and the Jetson.

All three machines were using the default ROS domain:

```text
ROS_DOMAIN_ID = 0
```

The environment variable itself printed blank on all three systems, which means ROS 2 was using the default domain ID of 0.

### Robot A Publisher

Robot A published a text message using:

```bash
ros2 topic pub /robotA_demo_message std_msgs/msg/String "{data: 'hello from robot A'}" -r 1
```

The publisher sent the message once per second.

### Jetson Subscriber

On the Jetson:

```bash
source /opt/ros/humble/setup.bash
```

The Robot A topic was discovered with:

```bash
ros2 topic list | grep robotA
```

Result:

```text
/robotA_demo_message
```

The topic type was verified with:

```bash
ros2 topic type /robotA_demo_message
```

Result:

```text
std_msgs/msg/String
```

The Jetson received the Robot A message using:

```bash
ros2 topic echo /robotA_demo_message
```

Received data:

```text
data: hello from robot A
```

### Robot B Subscriber

Robot B also subscribed to the Robot A topic using:

```bash
ros2 topic echo /robotA_demo_message
```

Robot B successfully received:

```text
data: hello from robot A
```

## ROS Networking Result

The networking test confirmed:

- Robot A can publish ROS 2 topics over the lab network
- Jetson can discover Robot A
- Jetson can subscribe to Robot A topics
- Robot B can discover Robot A
- Robot B can subscribe to Robot A topics
- Robot A, Robot B, and Jetson can communicate on the same ROS 2 domain
- ROS 2 network discovery is working
- ROS_DOMAIN_ID default domain 0 is working across all three machines

## Project Checklist Status

### Step 1
Connect to the robot using laptop  
Completed

### Step 2
Move robot forward, backward, and turn  
Completed

### Step 3
Access camera and LiDAR  
Completed

### Step 4
Visualize camera and LiDAR in RViz  
Completed

### Step 5
Start SLAM for a single robot and visualize it in RViz  
Completed

### Step 6
Repeat Steps 1-5 for another robot  
Completed

### Step 7
Study ROS networking and connect using ROS domain  
Completed

### Step 8
Send text message using ROS domain / ROS network  
Completed

### Step 9
Multi-SLAM  
Next step

## Demo Readiness

Current demo capabilities:

### Robot A
1. SSH connection
2. Keyboard teleoperation
3. LiDAR visualization
4. Camera visualization
5. SLAM mapping
6. Saved map
7. Saved RViz configuration

### Robot B
1. SSH connection
2. Keyboard teleoperation
3. LiDAR visualization
4. Camera visualization
5. SLAM mapping
6. Saved map
7. Saved RViz configuration

### ROS Networking
1. Robot A publishes ROS message
2. Jetson receives Robot A message
3. Robot B receives Robot A message
4. All three machines communicate on ROS domain 0

## Current Next Step

Begin Step 9: multi-robot SLAM.

Before running both SLAM systems together, the robot topics and TF frames need to be checked for naming collisions, especially:

- `/scan`
- `/odom`
- `/map`
- `/tf`
- `/tf_static`
- camera topics
- SLAM nodes