# ROS 2 Commands

## General ROS 2

List nodes:
```bash
ros2 node list
```

List topics:
```bash
ros2 topic list
```

View topic data:
```bash
ros2 topic echo <topic>
```

Check topic frequency:
```bash
ros2 topic hz <topic>
```

View topic publisher/subscriber information:
```bash
ros2 topic info <topic> -v
```

Run a ROS executable:
```bash
ros2 run <package> <executable>
```

Launch a ROS package:
```bash
ros2 launch <package> <launch_file>
```

---

# Robot A

IP:
```text
192.168.0.224
```

SSH:
```bash
ssh wheeltec@192.168.0.224
```

Main robot launch:
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

Keyboard control:
```bash
ros2 run wheeltec_robot_keyboard wheeltec_keyboard
```

LiDAR topic:
```text
/scan
```

Camera topic:
```text
/camera/color/image_raw
```

Check LiDAR:
```bash
ros2 topic hz /scan
```

Check camera:
```bash
ros2 topic hz /camera/color/image_raw
```

Save map:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/robotA_map
```

Verify saved map:
```bash
ls -l ~/robotA_map.*
```

Shutdown:
```bash
sudo shutdown now
```

---

# Robot B

IP:
```text
192.168.0.138
```

SSH:
```bash
ssh wheeltec@192.168.0.138
```

Main robot launch:
```bash
ros2 launch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch.py
```

Sensors:
```bash
ros2 launch turn_on_wheeltec_robot wheeltec_sensors.launch.py
```

Standalone LiDAR:
```bash
ros2 launch turn_on_wheeltec_robot wheeltec_lidar.launch.py
```

SLAM:
```bash
ros2 launch wheeltec_slam_toolbox online_async_launch.py
```

Keyboard control:
```bash
ros2 run wheeltec_robot_keyboard wheeltec_keyboard
```

LiDAR topic:
```text
/scan
```

Camera topic:
```text
/rosbot2_138/color/image_raw
```

Check LiDAR:
```bash
ros2 topic hz /scan
```

Check camera:
```bash
ros2 topic hz /rosbot2_138/color/image_raw
```

Save map:
```bash
ros2 run nav2_map_server map_saver_cli -f ~/robotB_map
```

Verify saved map:
```bash
ls -l ~/robotB_map.*
```

Shutdown:
```bash
sudo shutdown now
```

---

# Jetson / RViz

Source ROS 2 Humble:
```bash
source /opt/ros/humble/setup.bash
```

Launch Robot A RViz config:
```bash
rviz2 -d /home/jetson/.rviz2/robotA.rviz
```

Launch Robot B RViz config:
```bash
rviz2 -d /home/jetson/.rviz2/robotB.rviz
```

Verify both RViz configs:
```bash
ls -l ~/.rviz2/robotA.rviz ~/.rviz2/robotB.rviz
```

Shutdown Jetson:
```bash
sudo shutdown now
```

---

# Demo Startup Order

## Robot A
1. Main robot launch
2. Sensors
3. SLAM
4. RViz on Jetson
5. Keyboard control

## Robot B
1. Main robot launch
2. Sensors
3. Standalone LiDAR if `/scan` is not publishing
4. SLAM
5. RViz on Jetson
6. Keyboard control

---

# Quick Troubleshooting

Check if LiDAR is publishing:
```bash
ros2 topic hz /scan
```

Check `/scan` publisher:
```bash
ros2 topic info /scan -v
```

Check camera publisher:
```bash
ros2 topic info /camera/color/image_raw -v
```

Robot B camera:
```bash
ros2 topic info /rosbot2_138/color/image_raw -v
```

Check SLAM node:
```bash
ros2 node list | grep slam
```

Check map topic:
```bash
ros2 topic echo /map --once
```