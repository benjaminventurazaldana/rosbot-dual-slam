
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from pathlib import Path

HOME = Path.home()


def static_tf(name, xyz, parent, child):
    return Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name=name,
        arguments=[
            *[str(v) for v in xyz],
            '0', '0', '0',
            parent, child
        ],
        output='screen'
    )


def generate_launch_description():
    return LaunchDescription([
        # WheelTec base driver
        Node(
            package='turn_on_wheeltec_robot',
            executable='wheeltec_robot_node',
            name='robot_b_base_driver',
            parameters=[{
                'usart_port_name': '/dev/wheeltec_controller',
                'serial_baud_rate': 115200,
                'robot_frame_id': 'robot_b/base_footprint',
                'odom_frame_id': 'robot_b/odom_combined',
                'cmd_vel': 'cmd_vel',
                'akm_cmd_vel': 'none',
                'product_number': 0,
                'odom_x_scale': 1.0,
                'odom_y_scale': 1.0,
                'odom_z_scale_positive': 1.0,
                'odom_z_scale_negative': 1.0
            }],
            output='screen'
        ),

        # IMU orientation filter
        Node(
            package='imu_filter_madgwick',
            executable='imu_filter_madgwick_node',
            parameters=[str(HOME / 'robot_b_imu.yaml')],
            output='screen'
        ),

        # EKF odometry
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            parameters=[str(HOME / 'robot_b_ekf.yaml')],
            remappings=[
                ('/odometry/filtered', '/robot_b/odom_combined')
            ],
            output='screen'
        ),

        # Robot B sensor transforms
        static_tf(
            'robot_b_base_to_link',
            [0, 0, 0],
            'robot_b/base_footprint',
            'robot_b/base_link'
        ),
        static_tf(
            'robot_b_base_to_gyro_legacy', [0, 0, 0], 'robot_b/base_footprint', 'gyro_link'),
        static_tf(
            'robot_b_base_to_gyro',
            [0, 0, 0],
            'robot_b/base_footprint',
            'robot_b/gyro_link'
        ),
        static_tf(
            'robot_b_base_to_laser',
            [0.08874, 0.00067, 0.11102],
            'robot_b/base_footprint',
            'robot_b/laser'
        ),
        static_tf(
            'robot_b_base_to_camera',
            [0.16578, 0.00095, 0.0897],
            'robot_b/base_footprint',
            'robot_b/camera_link'
        ),

        # M10_P LiDAR
        Node(
            package='lslidar_driver',
            executable='lslidar_driver_node',
            namespace='robot_b',
            name='lslidar_driver_node',
            parameters=[str(HOME / 'lsm10_p_robot_b.yaml')],
            output='screen'
        ),

        # Normalize LiDAR scans to 1440 readings
        ExecuteProcess(
            cmd=[
                'python3',
                str(HOME / 'robot_b_scan_normalizer.py')
            ],
            output='screen'
        ),

        # Asynchronous SLAM Toolbox
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            namespace='robot_b',
            name='slam_toolbox',
            parameters=[str(HOME / 'robot_b_slam.yaml')],
            remappings=[
                ('/map', '/robot_b/map'),
                ('/map_metadata', '/robot_b/map_metadata')
            ],
            output='screen'
        )
    ])
