---
title: "**From Research Code to Running Systems**"
sub_title: "Cross-Platform Robotics and ML Workflows"
authors:
  - Tobias Fischer
  - Peter Corke
theme:
  name: tokyonight-storm
  override:
    footer:
      style: template
      left: '**Tobias Fischer & Peter Corke**: <span class="noice">From Research Code to Running Systems</span>'
      center: ''
      right: "{current_slide} / {total_slides}"
      height: 1
    palette:
      classes:
        noice:
          foreground: red
---

# Robotics is Powered by Software

- Software controls the pace of robotics innovation
- Modern robotics requires integrating many ecosystems
- The bottleneck is often *not algorithms*, but environments

<!-- pause -->

## Goal today

Move from:

- messy research repositories
- fragile installation instructions
- machine-specific setups

to:

- executable workflows
- cross-platform environments
- portable + reproducible robotics systems

<!-- end_slide -->

# The Reality of Many Research Repositories

```text
git clone https://github.com/some_repo/project

# Ubuntu 20.04 only
sudo apt install ...

pip install torch==1.12
pip install some_package

# Compile custom OpenCV

# Download model manually:
https://drive.google.com/...

# Tested on my machine :)
```

<!-- pause -->

# We can do better.

<!-- end_slide -->

# Pixi

Pixi provides:

- declarative environments
- lockfiles
- executable tasks
- cross-platform workflows

<!-- end_slide -->

# Start a Project

```bash +exec
/// python -c "from pathlib import Path; import shutil; [p.unlink() if p.is_file() else shutil.rmtree(p, ignore_errors=True) for p in [Path('pixi.toml'), Path('pixi.lock'), Path('data')]]"
pixi init
```


<!-- pause -->

# Add PyTorch

```bash +exec +pty:80:3
pixi add pytorch torchvision
```

<!-- end_slide -->

# train.py

```file +exec:pixi
path: train.py
language: python
```

<!-- end_slide -->

# Tasks Turn Commands into Workflows

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Define the workflow

```bash +exec
/// python helper.py remove start download-mnist
pixi task add start "python train.py" --depends-on download-mnist
/// python helper.py add download-mnist
```

<!-- pause -->

```toml {1-2|4-5|6-7|1-8}
[tasks]
start = { cmd = "python train.py", depends-on = ["download-mnist"] }

download-mnist = { 
  cmd = "python -c 'from torchvision.datasets import MNIST; MNIST(\"data\", download=True)'", 
  outputs = ["data/MNIST"]
}
```

<!-- pause -->

<!-- column: 1 -->

## Run it
```bash +exec +pty:80:8
pixi run start
```

<!-- pause -->

## Run it again
```bash +exec +pty:80:4
pixi run start
```

<!-- reset_layout -->

<!-- end_slide -->

# Mixing Ecosystems

Modern robotics often needs:

- robotics frameworks
- machine learning frameworks
- system dependencies
- Python-first tooling

<!-- pause -->

# Conda + PyPI Together

```toml
[dependencies]
python = "3.11"
pytorch = "*"

[pypi-dependencies]
transformers = "*"
```

<!-- pause -->

# No boundary between ecosystems

<!-- end_slide -->

# Robotics Meets ML: RoboStack

RoboStack enables ROS on:

- Linux
- macOS
- Windows

using the conda-forge ecosystem.

<!-- pause -->

```bash +exec +pty:80:3
pixi workspace channel add https://prefix.dev/robostack-rolling
pixi add ros-rolling-desktop
```

<!-- end_slide -->

# ROS2 101: TurtleSim demo
```bash +exec
pixi run ros2 run turtlesim turtlesim_node
```
<!-- pause -->

```bash +exec +pty:80:2
pixi run ros2 topic pub /turtle1/cmd_vel geometry_msgs/msg/Twist "{linear: {x: 2.0}, angular: {z: 1.8}}"
```


<!-- end_slide -->

# One Environment

```text
ROS + PyTorch + OpenCV + Transformers + ... + Custom research code
```

<!-- pause -->

# One lockfile.

<!-- pause -->

# One Machine, Multiple ROS Distros

```bash
# Add another ROS distro
pixi workspace channel add https://prefix.dev/robostack-humble
pixi add --feature humble ros-humble-desktop

# Run different environments
pixi run -e humble   ros2 run turtlesim turtlesim_node
pixi run -e rolling  ros2 run rviz2 rviz2

# We still support ROS1 Noetic
```

<!-- pause -->

> Different ROS distributions become environments, not separate machines.

<!-- end_slide -->

# Build Your Own ROS / C++ / Python Packages

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Create a ROS package

```bash +exec +pty:80:2
/// python -c "from pathlib import Path; import shutil; [p.unlink() if p.is_file() else shutil.rmtree(p, ignore_errors=True) for p in [Path('icra_ros_package')]]"
ros2 pkg create \
  --build-type ament_cmake \
  --node-name icra_node \
  icra_ros_package
```

<!-- pause -->

## Add it to Pixi

```toml
[workspace]
preview = ["pixi-build"]

[dependencies]
ros-rolling-icra-ros-package = { path = "icra_ros_package/package.xml" }
```
<!-- pause -->

<!-- column: 1 -->

## Build the package

```bash +exec +pty:80:4
/// python helper.py add pixi-build-preview icra-ros-package
pixi install
```

<!-- pause -->

## Does it work?

```bash +exec +pty:80:4
pixi run ros2 run icra_ros_package icra_node
```

<!-- pause -->

<!-- reset_layout -->

## Beyond ROS

- pure CMake projects
- Python packages
- Rust crates
- git repositories

> Research code becomes installable, shareable infrastructure.

<!-- end_slide -->

# Cross Platform Reproducibility

- Same repository
- Same lockfile
- Same command
- Different machine
- Different OS

<!-- pause -->

# macOS → Linux → HPC

```bash +exec
/// ssh zeus "rm -rf ~/robotics-demo"
# Add other platforms
pixi workspace platform add linux-64 win-64
```
<!-- pause -->

```bash +exec
# Zeus is a Linux machine, so far everything ran on MacOS
ssh zeus "mkdir -p ~/robotics-demo"
scp pixi.toml pixi.lock train.py zeus:~/robotics-demo/
/// ssh zeus "cd ~/robotics-demo && printf '\n[system-requirements]\ncuda = \"12\"\n' >> pixi.toml"
```
<!-- end_slide -->

```bash +exec
/// ssh zeus "cd ~/robotics-demo && pixi add pytorch-gpu -p linux-64" > /dev/null 2>&1
ssh zeus "cd ~/robotics-demo && pixi run start"
```

<!-- end_slide -->

# From Scripts to Infrastructure

```text
        README.md + shell scripts
                  ↓
         Executable workflows
                  ↓
       Composable research systems
```

<!-- pause -->

> Better tooling changes how research is shared, reused, and extended.

<!-- end_slide -->
# Case Study: VSLAM-Lab

Large-scale visual SLAM framework for benchmarking, composability, reproducibility, and easy onboarding.

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Before

```text
README.md

1. Install ROS
2. Build OpenCV
3. Download models
4. Download datasets
5. Configure CUDA
6. Build dependencies
7. Pray
```

<!-- column: 1 -->

## After

```bash +exec +pty:80:6
git clone https://github.com/VSLAM-LAB/VSLAM-LAB.git > /dev/null 2>&1
cd VSLAM-LAB && gh pr checkout 49 > /dev/null 2>&1 && \
pixi run demo orbslam2 eth table_3 mono
```

<!-- reset_layout -->

<!-- pause -->

> Multi-page setup instructions become executable workflows.
> Tooling stopped being a convenience and became research infrastructure!

<!-- end_slide -->

# Why Pixi for Robotics?
| Built-in core feature | Pixi | Conda | Pip | Poetry | uv |
|---|---:|---:|---:|---:|---:|
| Installs Python | ✅ | ✅ | ❌ | ❌ | ✅ |
| Multi-language packages | ✅ | ✅ | ❌ | ❌ | ❌ |
| Lockfiles | ✅ | ❌ | ❌ | ✅ | ✅ |
| Task runner | ✅ | ❌ | ❌ | ❌ | ❌ |
| Workspace management | ✅ | ❌ | ❌ | ✅ | ✅ |

<!-- pause -->

> The point is not one feature.
> 
> The point is having the right combination for robotics.

<!-- end_slide -->

# Why Not Docker?

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Containers are excellent for

- deployment
- cloud workflows
- CI/CD
- reproducible services
- production isolation

```text
Dockerfile
apt-get
pip install
CUDA setup
X11 forwarding
volume mounts
```
<!-- pause -->

<!-- column: 1 -->

## But robotics research often needs

- native GUI applications
- low-friction hardware access
- ROS + ML composability
- rapid iteration across repositories
- cross-platform desktop workflows

```text
pixi.toml
pixi.lock
pixi run start
```

<!-- reset_layout -->

<!-- pause -->

## Our goal

Native, reproducible workflows with minimal setup friction.

<!-- end_slide -->

# Limitations and Trade-offs

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Cross-platform is not magic

- Linux software may still require patches on Windows or macOS
- Native libraries and build systems can behave differently across platforms
- Some robotics packages assume Ubuntu-specific tooling

<!-- pause -->

## Ecosystem integration takes work

- Older scientific software may require compatibility fixes
- Packaging complex robotics stacks is still engineering effort
- Reproducibility reduces friction, not complexity

<!-- pause -->

<!-- column: 1 -->

## Pixi is not universal

- Large organisations often have bespoke infrastructure
- Proprietary toolchains may not integrate cleanly
- Real-time and embedded workflows can require specialised environments

<!-- pause -->

## But the ecosystem is improving rapidly

- Strong community support through conda-forge
- Unified CUDA support via conda-forge and NVIDIA collaboration
- Increasing convergence between robotics and ML tooling

<!-- reset_layout -->

<!-- pause -->

> The goal is not perfect portability.  
> The goal is to reduce friction.

<!-- end_slide -->

# Teasers

- Browser-native ROS via [ROS2WASM](https://ros2wasm.dev/)

- [Cross-platform CI in GitHub](https://github.com/ruben-arts/ros-example)

```yaml
jobs:
  strategy:
    matrix:
      os: [ubuntu-latest, windows-latest, macos-latest]
  steps:
    - name: Setup Pixi and install environment
      uses: prefix-dev/setup-pixi@v0.9.3

    - name: Test
      run: pixi run ros2 pkg list
```

<!-- end_slide -->

# Key Insights

- Robotics is increasingly limited by software infrastructure.

<!-- pause -->

- Tasks turn research code into executable workflows.

<!-- pause -->

- Composable environments unify robotics and machine learning.

<!-- pause -->

- Better packaging enables reuse, benchmarking, and collaboration.

---

# The Bigger Shift

<!-- pause -->

Dependency management is becoming core research infrastructure.

<!-- pause -->

Modern robotics needs:
- reproducible environments
- composable software ecosystems
- portable workflows across platforms

<!-- pause -->

> Build systems that others can run, extend, and build upon.

<!-- pause -->

<!-- new_lines: 3 -->

# Questions?

Tobias Fischer `tobias.fischer@qut.edu.au` & Peter Corke `peter.corke@qut.edu.au`

Queensland University of Technology

<!-- new_lines: 3 -->

# Thank you!

To the **prefix.dev** team for their incredible work on Pixi, to **Silvio Traversaro** for the many hours of work on RoboStack, to my **co-authors**, and to the many, many **open-source contributors** to the many presented projects! Also thanks to the QUT Centre for Robotics and Australian Research Council for their support.