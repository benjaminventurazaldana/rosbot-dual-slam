from launch import LaunchDescription
from launch_ros.actions import LifecycleNode

def generate_launch_description():
    return LaunchDescription([
        LifecycleNode(
            package='lslidar_driver',
            executable='lslidar_driver_node',
            name='lslidar_driver_node',
            namespace='robot_a',
            output='screen',
            emulate_tty=True,
            parameters=['/home/wheeltec/lsm10_p_robot_a.yaml'],
        )
    ])
