---
title: "**From Research Code to Running Systems**"
sub_title: "Cross-Platform Robotics and ML Workflows"
authors:
  - Tobias Fischer
  - Peter Corke
theme:
  name: terminal-dark
  override:
    intro_slide:
      subtitle:
        colors:
          foreground: cyan
      location:
        colors:
          foreground: cyan

    execution_output:
      status:
        running:
          foreground: cyan

    layout_grid:
      color: cyan

    footer:
      style: template
      left: '**Tobias Fischer & Peter Corke**: <span class="noice">From Research Code to Running Systems</span>'
      right: "{current_slide} / {total_slides}"
      height: 1
    palette:
      classes:
        noice:
          foreground: "ff0000"
          background: "000000"
        accent:
          foreground: "a7f3d0"
          background: "000000"
        caution:
          foreground: "fb7185"
          background: "000000"
        highlight:
          foreground: "fbbf24"
          background: "000000"
---

From Research Code to Running Systems
===

Cross-platform robotics and ML workflows

<!-- pause -->

# Research software is part of the research contribution.

<!-- pause -->

Today: turn fragile setup instructions into
<span class="accent">executable systems</span>.

<!-- end_slide -->

Robotics is Powered by Software
===

- Software controls the pace of robotics innovation
- Modern robotics requires integrating many ecosystems
- The bottleneck is often *not algorithms*, but environments

<!-- pause -->

## What changes in practice?

Tooling becomes part of how research is
<span class="accent">shared, reused, and extended</span>.

<!-- pause -->

## Goal today

Move from:

- messy research repositories
- fragile installation instructions
- machine-specific setups

to:

- executable workflows
- cross-platform environments
- reproducible robotics systems others can extend

<!-- end_slide -->

The Reality of Many Research Repositories
===

```shell
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

<!-- column_layout: [1, 3, 1] -->

<!-- column: 1 -->

# We can do better!

<!-- end_slide -->

This Talk Is Executable
===

The slides are also the demo environment.

<!-- pause -->

- Navigate with arrow keys
- Run code on a slide with `control` + `e`
- Show keybindings with `?`
- Exit with `esc` or `control` + `c`

<!-- pause -->

Only run executable snippets from presentations you trust!

<!-- end_slide -->

# Pixi ⚡

Pixi is a fast project manager built on the
conda-forge ecosystem.

Think: conda packages, modern project workflow.

<!-- pause -->

It provides:

- declarative environments
- lockfiles
- executable tasks
- cross-platform workflows

<!-- end_slide -->

From Instructions to Artifacts
===

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Instructions

- README.md
- shell scripts
- oral tradition
- "ask the previous student"

<!-- column: 1 -->

## Artifacts

- `pixi.toml`
- `pixi.lock`
- `pixi run <task>`
- CI-friendly commands

<!-- reset_layout -->

<!-- pause -->

> The shift is from instructions to <span class="accent">runnable artifacts</span>.

<!-- end_slide -->

# Start a Project

<!-- // Note: we want to start from scratch every time, so delete any "leftovers" -->
<!-- // Note 2: Lines starting with "///" will run but not be shown -->

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

Fast Environments Change Behavior ⚡
===

If changing environments takes
<span class="caution">minutes</span>,
people avoid changing environments.

<!-- pause -->

If it takes <span class="accent">seconds</span>,
environments become part of iteration.

# Environment Solve Time

```text
microenv
▓▓▓▓                     🟩 Pixi         0.07s
▒▒▒▒▒▒▒▒▒▒               🟦 Micromamba   2.54s
████████████████         🟧 conda        4.08s


stressenv
▓▓▓▓                     🟩 Pixi         4.54s
▒▒▒▒▒▒▒▒▒▒               🟦 Micromamba  12.58s
████████████████████████ 🟧 conda       29.84s
```

<!-- pause -->

> Speed matters because research is exploratory.

<!-- end_slide -->

# train.py

```file +exec:pixi
path: train.py
language: python
```

<!-- end_slide -->

Tasks Turn Commands into Workflows
===

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
  cmd = "python -c 'from torchvision.datasets import MNIST; MNIST(\"data\", download=True)' 2>/dev/null",
  outputs = ["data/MNIST"]
}
```

<!-- pause -->

<!-- column: 1 -->

## Run it
```bash +exec +pty:80:4
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

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Robotics stack

- ROS
- OpenCV
- CUDA
- native libraries

<!-- pause -->

<!-- column: 1 -->

## ML stack

- PyTorch
- Transformers
- experiment tools
- Python packages

<!-- reset_layout -->

<!-- pause -->

# Conda-forge + PyPI Together

```toml
[dependencies]
python = "3.11"
pytorch = "*"

[pypi-dependencies]
transformers = "*"
```

<!-- pause -->

# No boundary between ecosystems ✨

<!-- end_slide -->

Robotics Meets ML: RoboStack
===

RoboStack enables ROS on:

- Linux
- macOS
- Windows

through the conda-forge ecosystem.

<!-- pause -->

```bash +exec +pty:80:3
pixi workspace channel add https://prefix.dev/robostack-rolling
pixi add ros-rolling-desktop
```

<!-- end_slide -->

ROS Desktop App from a Locked Environment
===

Start with a tiny demo.
Then scale the same idea to real stacks.

<!-- pause -->

```bash +exec
pixi run ros2 run turtlesim turtlesim_node
```
<!-- pause -->

```bash +exec +pty:80:2
pixi run ros2 topic pub /turtle1/cmd_vel \
  geometry_msgs/msg/Twist \
  "{linear: {x: 2.0}, angular: {z: 1.8}}"
```


<!-- end_slide -->

# One Environment

```text
ROS + PyTorch + OpenCV
+ Transformers + custom research code
```

<!-- pause -->

# <span class="accent">One lockfile.</span>

<!-- pause -->

# One Machine, Multiple ROS Distros

```bash
# Add another ROS distro
pixi workspace channel add https://prefix.dev/robostack-humble
pixi add --feature humble ros-humble-desktop

# Run different environments
pixi run -e humble   ros2 run turtlesim turtlesim_node
pixi run -e rolling  ros2 run rviz2 rviz2

# We still support ROS1 Noetic :)
```

<!-- pause -->

> Different ROS distributions become environments, not separate machines.

<!-- end_slide -->

From Environment to Infrastructure
===

This is where Pixi stops being only an
environment manager.

<!-- pause -->

It becomes lab infrastructure.

<!-- pause -->

> Research code becomes something others can install.

<!-- end_slide -->

Build Your Own ROS / C++ / Python Packages
===

<!-- pause -->

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Create a ROS package

<!-- // Delete the icra_ros_package in case it already exists -->
```bash +exec +pty:80:4
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

<!-- // The helper script adds small snippets into the pixi.toml that I want to hide for the presentation -->
<!-- // See the top of helper.py for these snippets -->

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

<!-- end_slide -->


Beyond ROS
===

- pure CMake projects
- Python packages
- Rust crates
- git repositories

> Research code becomes installable, shareable infrastructure.

<!-- end_slide -->

Cross Platform Reproducibility
===

- Same repository
- Same lockfile
- Same command
- Different machine
- Different OS

<!-- pause -->

# macOS → Linux → HPC

```bash +exec
# Add other platforms
pixi workspace platform add linux-64 win-64

/// python helper.py remote-demo reset
```
<!-- pause -->

```bash +exec
# Copy this demo to Linux/HPC via ssh/scp
# Runs ssh/scp only when ICRA_REMOTE_HOST is set
python helper.py remote-demo prepare
```
<!-- end_slide -->

```bash +exec
# Optional presenter remote: run the same Pixi task on Linux/HPC
# Prints each remote command before executing it
python helper.py remote-demo run
```

<!-- end_slide -->

From Scripts to Infrastructure
===

```text
        README.md + shell scripts
                  ↓
         Executable workflows
                  ↓
       Composable research systems
```

<!-- pause -->

> Better tooling changes how research is shared,
> reused, and extended.

<!-- end_slide -->

Case Study: VSLAM-Lab
===

Large-scale visual SLAM framework for benchmarking,
composability, reproducibility, and easy onboarding.

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Before 😬

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

## After ✨
```bash +exec +pty:80:6
git clone https://github.com/VSLAM-LAB/VSLAM-LAB.git > /dev/null 2>&1
cd VSLAM-LAB && \
pixi run demo orbslam2 eth table_3 mono
```

<!-- reset_layout -->

<!-- pause -->

> Multi-page setup instructions become executable workflows!

<!-- end_slide -->

Why Pixi for Robotics? ⚙️
===

| Built-in project feature | Pixi | Conda | Pip | Poetry | uv |
|---|---:|---:|---:|---:|---:|
| Installs Python | ✅ | ✅ | ❌ | ❌ | ✅ |
| Native libraries | ✅ | ✅ | ❌ | ❌ | ❌ |
| Lockfiles | ✅ | via tools | ❌ | ✅ | ✅ |
| Task runner | ✅ | ❌ | ❌ | ❌ | ❌ |
| Workspace management | ✅ | ❌ | ❌ | ✅ | ✅ |
| Fast solver | ✅ | slower | n/a | ❌ | ✅ |

<!-- pause -->

> The point is not one feature.

> The point is having the <span class="accent">right combination</span> for robotics.

<!-- end_slide -->

Why Not Docker? 🧱
===

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

<span class="accent">Native, reproducible workflows</span>
with minimal setup friction.

<!-- end_slide -->

Limitations and Trade-offs
===

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
- Reproducibility captures complexity

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

<!-- pause -->

> Reproducible does not mean effortless.
> It means the effort is captured.

<!-- end_slide -->

Teasers
===

- Browser-native ROS via [ROS2WASM](https://ros2wasm.dev/)
<!-- pause -->

- Pack environments for another machine: `pixi pack`

<!-- pause -->

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
<!-- pause -->
- conda-forge is community infrastructure: `rattler-build generate-recipe pypi some-package`

Open a PR in `conda-forge/staged-recipes`.

> If a package blocks your research, packaging it can unblock the community.

<!-- end_slide -->

Key Insights
===

<!-- list_item_newlines: 2 -->


1. Robotics is increasingly limited by software infrastructure.

<!-- pause -->

2. Tasks turn research code into executable workflows.

<!-- pause -->

3. Composable environments unify robotics and machine learning.

<!-- pause -->

4. Better packaging enables reuse, benchmarking, and collaboration.

<!-- pause -->

5. <span class="highlight">Research software</span>
   is part of the contribution.

<!-- end_slide -->


The Bigger Shift
===

Dependency management is becoming core research infrastructure.

Modern robotics needs:
- reproducible environments
- composable software ecosystems
- portable workflows across platforms

<!-- pause -->

> Build systems that others can run, extend, and build upon.

<!-- pause -->

# Questions?

`Tobias.Fischer@qut.edu.au` & `Peter.Corke@qut.edu.au`

Queensland University of Technology

# Thank you!

To the **prefix.dev** team for their incredible work on Pixi,
to **Silvio Traversaro** for the many hours of work on RoboStack,
to **Alejandro Fontan** for his work on VSLAM-LAB,
to my **co-authors**, and to the many **open-source contributors**! Also thanks to the QUT Centre for Robotics
and Australian Research Council for their support.
