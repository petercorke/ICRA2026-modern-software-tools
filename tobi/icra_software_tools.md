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

Robotics papers increasingly depend on software systems.

<!-- pause -->

Today: make those systems
<span class="accent">runnable, repeatable, and portable</span>.

<!--
speaker_note: |
  Open with the shared pain, not with Pixi.
  The promise is practical: by the end, setup instructions should look less like folklore and more like executable infrastructure.
-->

<!-- end_slide -->

The Problem: Research Code Becomes Infrastructure
===

- Robots run on software stacks, not isolated algorithms
- Modern robotics mixes ROS, Python, C++, CUDA, simulators, and ML tooling
- The environment often determines whether the result can be reproduced

<!-- pause -->

## The thesis

Tooling becomes part of how research is
<span class="accent">shared, reused, and extended</span>.

<!--
speaker_note: |
  This is the bridge from "software matters" to "environment management is research infrastructure".
  Keep it concrete: when a stack cannot be installed, the algorithm effectively cannot be evaluated.
-->

## Goal today

Move from:

- fragile setup instructions
- machine-specific environments
- commands that only one person remembers

to:

- captured environments
- executable workflows
- reproducible systems others can run and extend

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

<!--
speaker_note: |
  Let the bad README breathe for a moment.
  The point is not to mock old repositories; most of us have written this slide.
  The question is how to make the next repository easier to run.
-->

<!-- end_slide -->

This Talk Is Executable
===

The slides are also the demo environment.

- Navigate with arrow keys
- Run code on a slide with `control` + `e`
- Show keybindings with `?`
- Exit with `esc` or `control` + `c`

<!-- pause -->

Only run executable snippets from presentations you trust!

<!-- speaker_note: This slide establishes trust and agency before code starts executing. -->

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

<!--
speaker_note: |
  Introduce Pixi as the tool that carries the story, not the story itself.
  The story is: environment, task, lockfile, platform.
-->

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

> The shift is from instructions to <span class="accent">runnable artifacts</span>.

<!--
speaker_note: |
  Stress that a README is still useful, but it should point to commands that can be checked by CI and run by collaborators.
-->

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

<!--
speaker_note: |
  Do not oversell benchmark numbers as universal.
  The talking point is behavioral: slow environments make people avoid experiments, fast environments make them part of the loop.
-->

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

<!--
speaker_note: |
  This is the first real "workflow" moment.
  The task name becomes the interface: students, CI, and future you do not need to remember the exact Python command.
-->

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

An environment file becomes infrastructure when it defines
the project contract.

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## Shared interfaces

- laptop: `pixi run start`
- CI: `pixi run test`
- HPC: `pixi run benchmark`
- workshop: `pixi run presentation`

<!-- column: 1 -->

## Captured assumptions

- dependencies are declared
- solver output is locked
- tasks are named
- platform differences are explicit

<!-- reset_layout -->

> Different entry points, one reproducible project.

<!--
speaker_note: |
  This slide should answer "so what?" after the demos.
  Pixi is useful locally, but the bigger value is a shared contract between authors, students, reviewers, CI, and collaborators.
  The commands differ because the jobs differ; the important part is that they are named, versioned, and reproducible.
-->

<!-- end_slide -->

Build Your Own ROS / C++ / Python Packages
===

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

- Linux-first robotics software can still need patches on Windows or macOS
- GUI applications, hardware access, and native builds behave differently
- Some ROS packages still assume Ubuntu-specific tooling

## Packaging moves work earlier

- Old scientific software may need compatibility fixes
- Complex robotics stacks still require engineering effort
- Reproducibility captures complexity; it does not remove it

<!-- column: 1 -->

## Pixi is not universal

- Docker remains excellent for deployment and services
- HPC modules and lab infrastructure may still be the right layer
- Real-time, embedded, and proprietary toolchains can need specialised setups

## The ecosystem is improving

- conda-forge gives robotics access to shared packaging infrastructure
- RoboStack brings ROS into that ecosystem
- CUDA and ML tooling are becoming more composable

<!-- reset_layout -->

> Reproducible does not mean effortless.
> It means the effort is captured instead of rediscovered.

<!--
speaker_note: |
  Keep this honest and short.
  The point is not "Pixi solves everything"; the point is that captured complexity is better than undocumented complexity.
-->

<!-- end_slide -->

Teasers
===

1. Browser-native ROS via [ROS2WASM](https://ros2wasm.dev/)

2. Pack environments for another machine: `pixi pack`

3. [Cross-platform CI in GitHub](https://github.com/ruben-arts/ros-example)

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

4. Package missing dependencies:
   `rattler-build generate-recipe pypi some-package`

> If a package blocks your research, packaging it can unblock the community.

<!--
speaker_note: |
  Treat these as doors the audience can open after the tutorial, not as four more demos.
  The shared theme is that tooling work compounds beyond one repository.
-->

<!-- end_slide -->

Key Insights
===

<!-- list_item_newlines: 2 -->

1. Environments are part of the method.

2. Tasks are the interface to a project.

3. Lockfiles preserve more than dependencies; they preserve context.

4. Packaging turns local code into shared infrastructure.

5. <span class="highlight">Research software</span> is part of the contribution.

<!--
speaker_note: |
  This is the recap slide, not a new-content slide.
  Read it as a ladder: method, interface, context, infrastructure, contribution.
-->

<!-- end_slide -->


Make the Easy Path the Reproducible Path
===

A useful research artifact should answer:

1. What environment do I need?
2. What command should I run?
3. What result should I expect?
4. How do I run it somewhere else?

<!-- pause -->

> Build systems that others can run, trust, extend, and build upon.

<!--
speaker_note: |
  End by returning to the title.
  "Running systems" means less time recovering setup state and more time evaluating ideas.
-->

# Questions?

`Tobias.Fischer@qut.edu.au` & `Peter.Corke@qut.edu.au`

Queensland University of Technology

# Thank you!

Thanks to the **prefix.dev** team, **Silvio Traversaro**,
**Alejandro Fontan**, my **co-authors**, the open-source contributors,
the QUT Centre for Robotics, and the Australian Research Council.
