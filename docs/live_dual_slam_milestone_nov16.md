# REU Milestone — Live Dual-SLAM Integration
Date: November 16, 2026

## Project
Cooperative Multi-Robot Mapping: A Dual-SLAM Approach via Wireless Edge Computing

TWIST Lab — University of Texas at Arlington

## Milestone Achieved
Established bidirectional ROS 2 map communication between Robot A and Robot B and demonstrated an experimental live occupancy-grid fusion pipeline.

## Robot Configuration
- Robot A (Leader): 192.168.0.224
- Robot B (Follower): 192.168.0.138
- ROS 2 Humble
- ROS_DOMAIN_ID=0
- Both robots publish maps at approximately 0.2 Hz.

## Completed Work
1. Confirmed standalone SLAM operation on both robots.
2. Corrected Robot A's map topic to /robot_a/map.
3. Verified Robot B publishes /robot_b/map.
4. Confirmed bidirectional occupancy-grid communication.
5. Created scripts/dual_slam_live_fusion.py.
6. Published /dual_slam/fused_map_preview at approximately 0.2 Hz.
7. Successfully displayed the experimental fused map in RViz on the Jetson.
8. Saved current-session maps for offline registration experiments.

## Live Fusion Test
- Known cells: 4,525
- Occupied cells: 276
- Publication frequency: approximately 0.2 Hz
- Experimental alignment: 29.5 degrees, (0.900, -2.250) meters

The alignment was inherited from an earlier mapping experiment and has not been validated for the current session.

## Current-Session Registration Experiment
- Rotation B to A: -128.00 degrees
- Translation: (0.900, -0.100) meters
- Conflict ratio: 0.5255
- Known overlap: 6,758 cells
- Registration score: 0.0343

The alignment was rejected for TF publication because of substantial occupancy conflicts.

## Known Limitations
- Both robots remained stationary during this session.
- Current maps may not contain sufficient overlapping geometry.
- Robot A and Robot B have separate TF trees.
- Live fusion uses fixed experimental alignment.
- Continuous automatic registration is not implemented.
- Fused maps are visualization-only, not navigation-ready.
- Robot B previously reported SLAM message-filter queue warnings.

## Next Research Steps
1. Collect fresh, overlapping LiDAR observations through supervised teleoperation.
2. Improve and validate map registration.
3. Estimate a reliable transformation between robot_a/map and robot_b/map.
4. Integrate validated registration into the live fusion pipeline.
5. Evaluate mapping accuracy and processing performance.

## Safety and Reproducibility
Original offline fusion scripts remain unchanged.
Original November 13 maps remain preserved.
No inter-robot TF transform was published.
