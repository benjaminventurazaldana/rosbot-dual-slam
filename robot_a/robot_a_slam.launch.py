from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess

def generate_launch_description():
    return LaunchDescription([
        ExecuteProcess(
            cmd=['python3', '/home/wheeltec/robot_a_scan_normalizer.py'],
            output='screen'
        ),
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            namespace='robot_a',
            name='slam_toolbox',
            output='screen',
            parameters=['/home/wheeltec/robot_a_slam.yaml'],
            remappings=[
                ('/tf', '/tf'),
                ('/tf_static', '/tf_static'),
                ('/map', '/robot_a/map'),
                ('/map_metadata', '/robot_a/map_metadata'),
            ]
        )
    ])
