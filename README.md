# Building, running and deploying modern software tools for robotics

* ICRA2026 Keynote Tutorial 4
* When: Wednesday, 3 June
* Where: Strauss 1-2

## Abstract

Robotics is powered by software. The tools we use shape the pace of innovation in research, drive
growth in industry, and underpin the education of future developers. This hands-on tutorial presents
a modern view of robotics software through live coding examples.

We begin with open-source Python toolboxes for robotics, machine vision, and spatial mathematics,
illustrating how they enable clear abstractions and rapid prototyping of complex systems. We then
show how these tools can be executed, shared, and extended across major platforms and even in the
browser using Pixi and the conda-forge ecosystem.

Participants will see how robotics frameworks such as ROS and machine learning frameworks such as
PyTorch can be composed into portable workflows, reducing setup overhead and enabling
reproducible experimentation and large-scale benchmarking, including applications such as SLAM.

This tutorial equips attendees to move from fragmented research code to robust, running systems
that can be deployed across platforms, from phones to high-performance computing environments,
and readily extended by others.

## Format

We have 90 minutes, and we'll take half each.  

* Peter: Beyond Fragments: A Unified Python Ecosystem for Robotics, Vision, and Control

* Tobi: From Research Code to Running Systems: Cross-Platform Robotics and ML Workflows

We will be demonstrating tools: what they do, how to use them, and how to install them.  Lots of terminal time, not so much Powerpoints.



The room we've been allocated seats 470 so it might be a big crowd. We will use [mentimeter](https://www.mentimeter.com) to capture questions from the floor and we'll do our best to answer them.  


## Getting started

1. Install `pixi`:

- On Unix (Linux/MacOS): `curl -fsSL https://pixi.sh/install.sh | sh`
- On Windows:
`powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"`
- Make sure to restart your shell after installation!

2. To follow Tobi's presentation, simply run `pixi run presentation` within this directory in a terminal.

## Presenters

![Cartoon of Peter and Tobi](https://raw.github.com/petercorke/ICRA2026-modern-software-tools/main/figs/peter+tobi.png)

**Peter Corke** is a robotics researcher, educator, and open-source creator. He
is a distinguished professor emeritus at Queensland University of
Technology; a fellow of the IEEE and has held many editorial roles. He wrote
the best selling textbook “Robotics, Vision, and Control”, now in its third
edition; created robotics and vision Toolboxes for Python; and has won
international recognition for teaching, including the 2025 Engelberger
Award for Education.

**Tobias Fischer** is a Senior Lecturer and ARC DECRA Fellow at the Queensland
University of Technology, working on robotic perception and localisation,
including in marine environments. He is a strong advocate for open-source
robotics and reproducible research, developing cross-platform software
workflows that integrate robotics and machine learning. He is a Fellow of
the IET, Senior Member of the IEEE, Associate Editor for the IEEE Robotics
and Automation Letters, and co-chair of the IEEE-RAS Women in Engineering
committee.

## Additional resources
### Repositories
- [Machine Vision Toolbox for Python](https://github.com/petercorke/machinevision-toolbox-python)
- [Robotics Toolbox for Python](https://github.com/petercorke/robotics-toolbox-python)
- [Spatial Maths for Python](https://github.com/rai-opensource/spatialmath-python)
- [bdsim: Block Diagram Simulation for Python](https://github.com/petercorke/bdsim)
- [RoboStack](https://robostack.github.io/) - currently providing ros-noetic, ros2-humble, ros2-jazzy, ros2-kilted and ros2-rolling
- [Pixi](https://pixi.sh)

### Papers and books
- [Robotics, Vision and Control Fundamental Algorithms in Python](https://doi.org/10.1007/978-3-031-06469-2)
- [Not your grandmother’s toolbox – the Robotics Toolbox reinvented for Python](https://doi.org/10.1109/ICRA48506.2021.9561366), IEEE International Conference on Robotics and Automation (ICRA) 2021
- [A RoboStack Tutorial: Using the Robot Operating System Alongside the Conda and Jupyter Data Science Ecosystems
](https://doi.org/10.1109/MRA.2021.3128367), IEEE Robotics & Automation Magazine (Volume: 29, Issue: 2, June 2022)
- [Pixi: Unified Software Development and Distribution for Robotics and AI](https://arxiv.org/abs/2511.04827), arXiv:2511.04827
- [ROS2WASM: Bringing the Robot Operating System to the Web](https://doi.org/10.1109/ICRA55743.2025.11127821), IEEE International Conference on Robotics and Automation (ICRA) 2025

## Acknowledgements
Tobi would like to thank the fantastic team at [prefix.dev](https://prefix.dev/) for the great work on Pixi over the last few years, and the nice and productive collaboration. He also thanks all contributors to [RoboStack](https://robostack.github.io/), and in particular Silvio Traversaro for his never-ending support. Tobi acknowledges partial support from the [QUT Centre for Robotics](https://qcr.ai/) and an ARC DECRA Fellowship DE240100149.