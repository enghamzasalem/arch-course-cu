# Assignment Submission: Lecture 10

**Student Name**: Arda Arslan  
**Student ID**: 30008610  
**Submission Date**: 23/04/2026  

## Overview

This submission analyzes how CityBite handles increasing workload and scales under peak conditions. It covers workload dimensions, scaling decisions, data flow design, architecture differences between steady and peak load, and the use of common scalability patterns.

## Files Included

- `part1_workload_and_bottlenecks.md` - Workload dimensions, bottlenecks, and hero scenario
- `part1_scale_decisions.md` - Scale up vs scale out decisions for key subsystems
- `part2_data_scaling.md` - Data plane design including read/write paths, caching, and async processing
- `part2_architecture_steady_vs_peak.drawio` - Architecture diagram for steady vs peak load (draw.io)
- `part2_architecture_steady_vs_peak.png` - Architecture diagram for steady vs peak load (image)
- `part3_patterns.md` - Scalability pattern mapping for CityBite
- `part3_autoscaling_and_limits.md` - HPA rule, backpressure strategy, and failure analysis
- `README.md` - This file

## Key Highlights

- Identified main bottlenecks such as database load and connection limits during peak traffic
- Designed a scalable data plane using caching, read replicas, and async workers
- Compared steady vs peak architecture with clear differences in components and scaling behavior

## How to View

1. Open `.drawio` files in draw.io to see editable diagrams  
2. View `.png` files for quick reference  
3. Read `.md` files for documentation  