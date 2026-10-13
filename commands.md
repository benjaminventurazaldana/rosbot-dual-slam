# ROS 2 Commands

List nodes:
ros2 node list

List topics:
ros2 topic list

View topic data:
ros2 topic echo <topic>

Run a ROS executable:
ros2 run <package> <executable>

Launch ROS:
ros2 launch <package> <launch_file>

SSH into Rosbot:
ssh wheeltec@192.168.0.100

Start robot:
ros2 launch turn_on_wheeltec_robot turn_on_wheeltec_robot.launch

Keyboard control:
ros2 run wheeltec_robot_keyboard wheeltec_keyboard