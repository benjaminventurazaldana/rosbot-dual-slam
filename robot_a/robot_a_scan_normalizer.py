#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

class ScanNormalizer(Node):
    def __init__(self):
        super().__init__('robot_a_scan_normalizer')
        self.publisher = self.create_publisher(
            LaserScan, '/robot_a/scan_fixed', qos_profile_sensor_data)
        self.subscription = self.create_subscription(
            LaserScan, '/robot_a/scan',
            self.process_scan, qos_profile_sensor_data)
        self.count = 0
        self.get_logger().info(
            'Normalizing /robot_a/scan -> /robot_a/scan_fixed')

    def process_scan(self, msg):
        bins = 1440
        output = LaserScan()
        output.header = msg.header
        output.angle_min = 0.0
        output.angle_increment = 2.0 * math.pi / bins
        output.angle_max = output.angle_min + (bins - 1) * output.angle_increment
        output.time_increment = msg.time_increment
        output.scan_time = msg.scan_time
        output.range_min = msg.range_min
        output.range_max = msg.range_max
        output.ranges = [float('inf')] * bins
        output.intensities = [0.0] * bins

        for i, distance in enumerate(msg.ranges):
            angle = msg.angle_min + i * msg.angle_increment
            index = round((angle % (2.0 * math.pi)) /
                          output.angle_increment) % bins

            if math.isfinite(distance) and msg.range_min <= distance <= msg.range_max:
                if distance < output.ranges[index]:
                    output.ranges[index] = distance
                    if i < len(msg.intensities):
                        output.intensities[index] = msg.intensities[i]

        self.publisher.publish(output)
        self.count += 1
        if self.count % 120 == 0:
            self.get_logger().info(
                f'Normalized {self.count} scans; '
                f'latest input={len(msg.ranges)}, output={bins}')

def main():
    rclpy.init()
    node = ScanNormalizer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
