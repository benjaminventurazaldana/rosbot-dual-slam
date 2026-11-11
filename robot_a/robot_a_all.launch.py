from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from pathlib import Path

HOME = Path('/home/wheeltec')

def include(filename):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(str(HOME / filename))
    )

def generate_launch_description():
    return LaunchDescription([
        include('robot_a_base.launch.py'),
        include('robot_a_tf.launch.py'),
        TimerAction(
            period=3.0,
            actions=[include('robot_a_ekf.launch.py')]
        ),
        TimerAction(
            period=5.0,
            actions=[include('robot_a_lidar.launch.py')]
        ),
        TimerAction(
            period=10.0,
            actions=[include('robot_a_slam.launch.py')]
        )
    ])
