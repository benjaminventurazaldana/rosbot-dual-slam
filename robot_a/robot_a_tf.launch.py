from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='robot_a_gyro_tf',
            arguments=[
                '0', '0', '0',
                '0', '0', '0',
                'robot_a/base_footprint',
                'robot_a/gyro_link'
            ]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='robot_a_base_link_tf',
            arguments=[
                '0', '0', '0',
                '0', '0', '0',
                'robot_a/base_footprint',
                'robot_a/base_link'
            ]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='robot_a_laser_tf',
            arguments=[
                '0.08874', '0.00067', '0.11102',
                '0', '0', '0',
                'robot_a/base_footprint',
                'robot_a/laser'
            ]
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='robot_a_camera_tf',
            arguments=[
                '0.16578', '0.00095', '0.0897',
                '0', '0', '0',
                'robot_a/base_footprint',
                'robot_a/camera_link'
            ]
        )
    ])
