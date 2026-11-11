from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='turn_on_wheeltec_robot',
            executable='wheeltec_robot_node',
            namespace='robot_a',
            output='screen',
            parameters=[{
                'usart_port_name': '/dev/wheeltec_controller',
                'serial_baud_rate': 115200,
                'robot_frame_id': 'robot_a/base_footprint',
                'gyro_frame_id': 'robot_a/gyro_link',
                'odom_frame_id': 'robot_a/odom',
                'cmd_vel': 'cmd_vel',
                'akm_cmd_vel': 'none',
                'product_number': 0,
                'odom_x_scale': 1.0,
                'odom_y_scale': 1.0,
                'odom_z_scale_positive': 1.0,
                'odom_z_scale_negative': 1.0
            }],
            remappings=[
                ('/odom', '/robot_a/odom'),
                ('/cmd_vel', '/robot_a/cmd_vel')
            ]
        )
    ])
