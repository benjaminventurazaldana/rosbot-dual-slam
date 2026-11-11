from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='robot_localization',
            executable='ekf_node',
            namespace='robot_a',
            name='ekf_filter_node',
            output='screen',
            parameters=['/home/wheeltec/robot_a_ekf.yaml'],
            remappings=[
                ('/odometry/filtered', '/robot_a/odom_combined'),
                ('odometry/filtered', '/robot_a/odom_combined'),
                ('/tf', '/tf'),
                ('/tf_static', '/tf_static')
            ]
        )
    ])
