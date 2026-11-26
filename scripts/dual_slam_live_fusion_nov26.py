
#!/usr/bin/env python3
"""
TWIST Lab - Cooperative Multi-Robot Mapping
Live Dual-SLAM Map Fusion - Experimental Version 1

Robot A: Leader
Robot B: Follower

Inputs:
    /robot_a/map
    /robot_b/map

Output:
    /dual_slam/fused_map_preview

This node:
- Receives live occupancy grids from both robots.
- Converts both maps to a common grid.
- Applies an experimental B-to-A alignment.
- Preserves unknown cells and conflicting observations.
- Publishes an updated fusion preview every 5 seconds.

IMPORTANT:
The initial alignment is from an earlier experiment.
It must be validated for the current mapping session.
The output is not navigation-ready.

Does not modify SLAM nodes or publish TF.
"""

import math

import numpy as np
import rclpy

from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from nav_msgs.msg import OccupancyGrid


RESOLUTION = 0.05
SIZE = 480

# Previous experimental alignment (Robot B -> Robot A).
# These values are NOT validated for the current session.
ALIGNMENT_ANGLE = -2.5
ALIGNMENT_TX = 0.000
ALIGNMENT_TY = 0.700


def quaternion_yaw(q):
    return math.atan2(
        2.0 * (q.w * q.z + q.x * q.y),
        1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    )


class LiveFusion(Node):

    def __init__(self):
        super().__init__("dual_slam_live_fusion")

        self.map_a = None
        self.map_b = None

        self.declare_parameter("alignment_angle", ALIGNMENT_ANGLE)
        self.declare_parameter("alignment_tx", ALIGNMENT_TX)
        self.declare_parameter("alignment_ty", ALIGNMENT_TY)

        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.VOLATILE

        self.create_subscription(
            OccupancyGrid,
            "/robot_a/map",
            self.callback_a,
            qos
        )

        self.create_subscription(
            OccupancyGrid,
            "/robot_b/map",
            self.callback_b,
            qos
        )

        self.publisher = self.create_publisher(
            OccupancyGrid,
            "/dual_slam/fused_map_preview",
            10
        )

        self.create_timer(5.0, self.publish_fusion)

        self.get_logger().info(
            "TWIST Lab - Live Dual-SLAM Fusion started"
        )

        self.get_logger().info(
            "Waiting for Robot A and Robot B maps..."
        )

    def callback_a(self, msg):
        self.map_a = msg

    def callback_b(self, msg):
        self.map_b = msg

    def rasterize(self, msg, angle=0.0, tx=0.0, ty=0.0):

        width = msg.info.width
        height = msg.info.height
        resolution = msg.info.resolution

        grid = np.asarray(
            msg.data, dtype=np.int16
        ).reshape((height, width))

        # Trinary occupancy classification.
        values = np.full(grid.shape, -1, dtype=np.int16)
        values[(grid >= 0) & (grid <= 25)] = 0
        values[grid >= 65] = 100

        yy, xx = np.nonzero(values >= 0)

        result = np.full(
            (SIZE, SIZE), -1, dtype=np.int16
        )

        if len(xx) == 0:
            return result

        origin = msg.info.origin.position
        yaw = quaternion_yaw(msg.info.origin.orientation)

        local_x = (xx + 0.5) * resolution
        local_y = (yy + 0.5) * resolution

        c = math.cos(yaw)
        s = math.sin(yaw)

        world_x = origin.x + c * local_x - s * local_y
        world_y = origin.y + s * local_x + c * local_y

        # Additional registration transform for Robot B.
        a = math.radians(angle)
        ca = math.cos(a)
        sa = math.sin(a)

        final_x = ca * world_x - sa * world_y + tx
        final_y = sa * world_x + ca * world_y + ty

        # Common grid covers -12 m to +12 m on both axes.
        px = np.floor(
            (final_x + SIZE * RESOLUTION / 2.0) / RESOLUTION
        ).astype(int)

        py = np.floor(
            (final_y + SIZE * RESOLUTION / 2.0) / RESOLUTION
        ).astype(int)

        valid = (
            (px >= 0) & (px < SIZE) &
            (py >= 0) & (py < SIZE)
        )

        # Occupied cells take priority within each source map.
        np.maximum.at(
            result,
            (py[valid], px[valid]),
            values[yy[valid], xx[valid]]
        )

        return result

    def fuse(self, a, b):

        merged = np.full(
            (SIZE, SIZE), -1, dtype=np.int16
        )

        known_a = a >= 0
        known_b = b >= 0

        only_a = known_a & ~known_b
        only_b = known_b & ~known_a

        merged[only_a] = a[only_a]
        merged[only_b] = b[only_b]

        merged[(a == 0) & (b == 0)] = 0
        merged[(a == 100) & (b == 100)] = 100

        # Conflicting free/occupied observations remain unknown.
        return merged

    def publish_fusion(self):

        if self.map_a is None or self.map_b is None:
            self.get_logger().info(
                "Waiting for both occupancy grids..."
            )
            return

        angle = self.get_parameter(
            "alignment_angle"
        ).value

        tx = self.get_parameter(
            "alignment_tx"
        ).value

        ty = self.get_parameter(
            "alignment_ty"
        ).value

        a = self.rasterize(self.map_a)

        b = self.rasterize(
            self.map_b,
            angle=angle,
            tx=tx,
            ty=ty
        )

        merged = self.fuse(a, b)

        message = OccupancyGrid()

        message.header.stamp = self.get_clock().now().to_msg()
        message.header.frame_id = "robot_a/map"

        message.info.resolution = RESOLUTION
        message.info.width = SIZE
        message.info.height = SIZE

        message.info.origin.position.x = (
            -SIZE * RESOLUTION / 2.0
        )

        message.info.origin.position.y = (
            -SIZE * RESOLUTION / 2.0
        )

        message.info.origin.orientation.w = 1.0

        message.data = merged.flatten().astype(
            np.int8
        ).tolist()

        self.publisher.publish(message)

        known = int(np.count_nonzero(merged >= 0))
        occupied = int(np.count_nonzero(merged == 100))

        self.get_logger().info(
            f"Fusion preview published | "
            f"Known cells: {known} | "
            f"Occupied cells: {occupied}"
        )


def main(args=None):

    rclpy.init(args=args)

    node = LiveFusion()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()

