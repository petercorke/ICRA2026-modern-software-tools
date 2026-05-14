---
title: "**From Research Code to Running Systems**"
sub_title: "Cross-Platform Robotics and ML Workflows"
authors:
  - Peter Corke
  - Tobias Fischer
theme:
  name: tokyonight-storm
  override:
    footer:
      style: template
      left: '**Peter Corke & Tobias Fischer**: <span class="noice">From Research Code to Running Systems</span>'
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
- reproducible robotics systems

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
/// rm -rf pixi.toml
/// rm -rf data
pixi init
```

```bash +image
/// echo "test" > ./test.txt
magick -size 1x1 xc:transparent png:-
```


<!-- pause -->

# Add PyTorch

```bash +exec +pty:80:3
pixi add pytorch torchvision
```

<!-- end_slide -->

# hello.py

```file +exec:pixi
path: hello.py
language: python
```

<!-- end_slide -->

# Add a Task

```toml {1-2|4-5|6-7|1-8}
[tasks]
train = { cmd = "python train.py", depends-on = ["download-mnist"] }

download-mnist = { 
  cmd = "python -c 'from torchvision.datasets import MNIST; MNIST(\"data\", download=True)'", 
  outputs = ["data/MNIST"]
}
```

```bash +image
/// pixi task add start "python hello.py" > /dev/null 2>&1
magick -size 1x1 xc:transparent png:-
```

<!-- pause -->

# train.py

```python
import torch

print('Train ...')
```

<!-- pause -->

# Run the Workflow

```bash +exec +pty
pixi run start
```

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
pixi workspace platform add linux-64 osx-arm64 win-64
```
<!-- pause -->

```bash +exec
ssh zeus "mkdir -p ~/robotics-demo"
scp pixi.toml pixi.lock hello.py zeus:~/robotics-demo/
/// ssh zeus "cd ~/robotics-demo && printf '\n[system-requirements]\ncuda = \"12\"\n' >> pixi.toml"
```
<!-- end_slide -->

```bash +image
/// ssh zeus "cd ~/robotics-demo && pixi add pytorch-gpu -p linux-64" > /dev/null 2>&1
magick -size 1x1 xc:transparent png:-
```

```bash +exec
ssh zeus "cd ~/robotics-demo && pixi run start"
```

<!-- end_slide -->

# From Scripts to Infrastructure

<!-- pause -->

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
pixi run demo \
orbslam2 eth table_3 mono
```

<!-- reset_layout -->

<!-- pause -->

> Multi-page setup instructions become executable workflows.

<!-- end_slide -->

# Tasks as Workflows

```toml
[tasks]
download-data = "python scripts/download_data.py"
download-models = "python scripts/download_models.py"
benchmark = "python run_benchmark.py"
```

<!-- pause -->

# Research code becomes executable infrastructure

This is where the tooling stopped being a convenience and became research infrastructure!

<!-- end_slide -->

# Why Not Docker?

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Containers are excellent for

- deployment

- isolation

- cloud workflows

- CI/CD pipelines

- *But:* difficult composition across research repositories
```text

Dockerfile

apt-get

pip install

CUDA setup

X11 forwarding

volume mounts

```

<!-- column: 1 -->

## But robotics research often needs

- native hardware acceleration

- GUI applications

- ROS + ML composability

- rapid iteration across repositories

- native network access

```text

pixi.toml

pixi.lock

pixi run start

```

<!-- reset_layout -->

<!-- pause -->

## Our goal

Native, reproducible, cross-platform workflows with minimal setup friction.

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

# Thank You!

Questions?

Peter Corke `peter.corke@qut.edu.au` & Tobias Fischer `tobias.fischer@qut.edu.au`

Queensland University of Technology
