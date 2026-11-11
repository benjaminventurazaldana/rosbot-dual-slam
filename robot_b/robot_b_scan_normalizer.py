
#!/usr/bin/env python3

import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class RobotBScanNormalizer(Node):
    def __init__(self):
        super().__init__('robot_b_scan_normalizer')

        self.publisher = self.create_publisher(
            LaserScan, '/robot_b/scan_fixed', 10
        )

        self.subscription = self.create_subscription(
            LaserScan,
            '/robot_b/scan',
            self.scan_callback,
            10
        )

        self.target_count = 1440
        self.get_logger().info(
            'Robot B scan normalizer started'
        )

    def scan_callback(self, msg):
        if not msg.ranges:
            return

        count = self.target_count
        output = LaserScan()

        output.header = msg.header
        output.angle_min = msg.angle_min
        output.angle_max = msg.angle_max
        output.angle_increment = (
            (msg.angle_max - msg.angle_min) / (count - 1)
        )
        output.time_increment = (
            msg.scan_time / count if msg.scan_time > 0 else 0.0
        )
        output.scan_time = msg.scan_time
        output.range_min = msg.range_min
        output.range_max = msg.range_max

        ranges = []
        intensities = []

        for i in range(count):
            angle = output.angle_min + i * output.angle_increment

            if msg.angle_increment == 0:
                ranges.append(float('inf'))
                intensities.append(0.0)
                continue

            index = round(
                (angle - msg.angle_min) / msg.angle_increment
            )

            if 0 <= index < len(msg.ranges):
                ranges.append(float(msg.ranges[index]))
                if index < len(msg.intensities):
                    intensities.append(float(msg.intensities[index]))
                else:
                    intensities.append(0.0)
            else:
                ranges.append(float('inf'))
                intensities.append(0.0)

        output.ranges = ranges
        output.intensities = intensities

        self.publisher.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = RobotBScanNormalizer()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
