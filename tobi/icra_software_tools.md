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
        accent:
          foreground: "a7f3d0"
        caution:
          foreground: "fb7185"
        highlight:
          foreground: "fbbf24"
---

From Research Code to Running Systems
===

Robotics papers increasingly depend on full software stacks

Bucket list:
  - ROS, Python, C++, CUDA, simulators, ML tooling, and data
  - Cross-platform robotics and ML workflows
    (Linux + Windows + MacOS + ...)
  - Support for many programming languages:
    Python, C++, Rust, R, ...

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

## Hands up if you have lost time to...

- a missing dependency
- a mystery dataset or model download
- "works on my machine"

<!--
speaker_note: |
  This is the bridge from "software matters" to "environment management is research infrastructure".
  Keep it concrete: when a stack cannot be installed, the algorithm effectively cannot be evaluated.
-->

<!-- pause -->

## The thesis

Tooling is part of how research is
<span class="accent">shared, reused, and extended</span>. Developing and sharing should be a single workflow, not separated.

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

<!-- column_layout: [1, 5, 1] -->

<!-- column: 1 -->

# What if the README had one command?

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


## During the talk

- arrows: navigate
- `control` + `e`: run code
- `control` + `r`: reset slide
- `?`: show keybindings
- `esc` or `control` + `c`: exit


## Running it yourself

Use a terminal and raw `git clone`
(avoid GitHub Web or GitHub Desktop):
```bash
git clone https://github.com/petercorke/
          ICRA2026-modern-software-tools.git
cd ICRA2026-modern-software-tools
pixi run presentation
```

<!-- pause -->

Only run executable snippets from presentations you trust!

<!--
speaker_note: |
  This slide establishes trust and agency before code starts executing.
  For Windows users, explicitly say to open PowerShell or Git Bash and paste the `git clone` command.
  Avoid GitHub's web download and GitHub Desktop for the workshop, because the live commands assume a normal Git checkout and a terminal in the repository directory.
  Explain that `cd ICRA2026-modern-software-tools` moves the terminal into the downloaded project folder.
-->

<!-- end_slide -->

Pixi: From Instructions to Artifacts ⚡
===

Pixi is a fast project manager built on the
conda-forge ecosystem.

Think: conda packages, modern project workflow.

<!-- pause -->

<!-- column_layout: [1, 1] -->

<!-- column: 0 -->

## The old way: Instructions

- README.md
- shell scripts
- oral tradition
- "ask the previous student"

<!-- column: 1 -->

## Now: shared artifacts

- `pixi.toml`
- `pixi.lock`
- `pixi run <task>`
- CI-friendly commands

<!-- reset_layout -->

> The shift is from instructions to <span class="accent">runnable artifacts</span>.

<!--
speaker_note: |
  Introduce Pixi as the tool that carries the story, not the story itself.
  The story is: environment, task, lockfile, platform.
  Be precise about the lockfile: it is a fully resolved environment, including exact package versions, hashes, and per-platform solver output.
  That is what lets a project be shared as more than "try these install commands".
  Stress that a README is still useful, but it should point to commands that can be checked by CI and run by collaborators.
  The important shift is that setup knowledge moves out of oral tradition and into files we can version, review, and execute.
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
pixi add python pytorch torchvision
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

Hands up: who has a command in their lab
that nobody wants to type from memory?

<!-- pause -->

<!-- column_layout: [3, 2] -->

<!-- column: 0 -->

## Define the workflow

```bash +exec
/// python scripts/pixi_snippets.py remove start download-mnist
pixi task add start "python train.py" --depends-on download-mnist
/// python scripts/pixi_snippets.py add download-mnist
```

<!-- pause -->

```toml
[tasks]
...
download-mnist = {
  cmd = "python -c 'torchvision.datasets.MNIST("data", download=True)'",
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

<!--
speaker_note: |
  This is the first real "workflow" moment.
  The task name becomes the interface: students, CI, and future you do not need to remember the exact Python command.
  Also stress that a task is not just an alias: `pixi run start` runs inside the resolved environment, so the command and the environment contract travel together.
  The `outputs` entry means Pixi can avoid repeating work once the data is already present; reproducibility does not have to mean rerunning every expensive setup step.
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

Hands up if you have ever installed a VM
or old Ubuntu just to get ROS running.

<!-- pause -->

RoboStack enables ROS on:

- Linux
- macOS
- Windows

through the conda-forge ecosystem.

<!-- pause -->

```bash +exec +pty:80:10
pixi workspace channel add https://prefix.dev/robostack-rolling
pixi add ros-rolling-desktop
```

<!-- end_slide -->

ROS Desktop App from a Locked Environment
===

```bash +exec
pixi run ros2 run turtlesim turtlesim_node
```
<!-- pause -->

```bash +exec +pty:80:2
pixi run ros2 topic pub /turtle1/cmd_vel \
  geometry_msgs/msg/Twist \
  "{linear: {x: 2.0}, angular: {z: 1.8}}"
```
<!-- pause -->

Start with a tiny demo.
Then scale the same idea to real stacks.

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

<!--
speaker_note: |
  A Pixi feature is a building block for an environment.
  That is the key idea here: Humble and Rolling can share a repository, but still resolve into distinct environments with their own dependencies, channels, and tasks.
-->

<!-- end_slide -->

Build Your Own ROS / C++ / Python Packages
===

<!-- column_layout: [3, 2] -->

<!-- column: 0 -->

## Create a ROS package

<!-- // Delete the icra_ros_package in case it already exists -->
```bash +exec +pty:80:2
/// python -c "from pathlib import Path; import shutil; [p.unlink() if p.is_file() else shutil.rmtree(p, ignore_errors=True) for p in [Path('icra_ros_package')]]"
/// python scripts/pixi_snippets.py remove icra-ros-package
pixi run ros2 pkg create \
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
<!-- // See scripts/pixi_snippets.py for these snippets -->

```bash +exec +pty:80:2
/// python scripts/pixi_snippets.py add pixi-build-preview icra-ros-package
# The equivalent to colcon build!
pixi install
```

<!-- pause -->

## Does it work?

```bash +exec +pty:80:4
pixi run ros2 run icra_ros_package icra_node
```

<!-- pause -->

<!--
speaker_note: |
  The important detail is that the dependency is the local `package.xml`.
  Pixi-build uses that metadata to build and install the package, and dependency resolution follows the package.xml declarations instead of a separate hand-written install list.
  In practice, this is what you want for ROS research code: not only install ROS packages, but develop local ROS packages inside the same reproducible environment.
-->

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
- Different OS - note: no root required!

<!-- pause -->

# macOS → Linux → HPC

```bash +exec
# Add other platforms
pixi workspace platform add linux-64 win-64

/// python scripts/remote_demo.py reset
```
<!-- pause -->

```bash +exec
# Copy this demo to Linux/HPC via ssh/scp
# Runs ssh/scp only when ICRA_REMOTE_HOST is set
python scripts/remote_demo.py prepare
```
<!-- end_slide -->

```bash +exec +pty:80:10
# Optional presenter remote: run the same Pixi task on Linux/HPC
# Prints each remote command before executing it
python scripts/remote_demo.py run
```

<!--
speaker_note: |
  This is the real reproducibility test: clone or copy the same repository to a different machine, then run the same task.
  It simulates handing the repository to a colleague on different hardware.
  If something still fails, the remaining problem is usually an explicit system-level issue rather than hidden project setup.
-->

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

1. Install ROS, ...
2. Build OpenCV, ...
3. Download models
4. Download datasets
5. Configure CUDA
6. Build dependencies
7. Pray
```

<!-- pause -->

<!-- column: 1 -->

## After ✨
```bash +exec +pty:80:6
git clone https://github.com/VSLAM-LAB/VSLAM-LAB.git > /dev/null 2>&1
pixi run -m ./VSLAM-LAB/pixi.toml demo orbslam2 eth table_3 mono 
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
- host networking and shared memory behavior
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

<!--
speaker_note: |
  Docker is still the right tool for many deployment jobs.
  Pixi is not anti-container: a Pixi environment can also be installed inside a container when that is the deployment boundary.
  The mismatch here is research iteration: host hardware, GUI tools, ROS networking, local notebooks, and multiple repositories need to move together.
  Containers can also make ROS middleware behavior more surprising: networking isolation, discovery, and shared-memory transport across host/container boundaries are often exactly the kind of friction robotics researchers are trying to avoid.
  Avoid making a size claim unless you have measured it; it is enough to say Pixi often feels faster because it resolves, links, and caches packages differently from pulling full images.
-->

<!-- end_slide -->

Limitations and Trade-offs
===

Reproducible does not mean effortless.
It means the effort is captured instead of rediscovered.

<!-- pause -->

1. Some robotics software is still Linux-first.
   Drivers, GUIs, middleware, and hardware access need testing.

2. Packaging moves work earlier.
   Old libraries and unusual builds likely need patches (our RoboStack builds have 100s!).

3. Pixi is one layer.
   Docker, HPC modules, and embedded toolchains still matter.

4. Lockfiles capture complexity.
   They do not make complex systems simple.

<!-- pause -->

> The win is not zero setup.
> The win is setup you can inspect, share, and rerun.

<!--
speaker_note: |
  Keep this honest and short.
  The point is not "Pixi solves everything"; the point is that captured complexity is better than undocumented complexity.
-->

<!-- end_slide -->

Teasers
===

1. Browser-native ROS via [ROS2WASM](https://ros2wasm.dev/)
<!-- pause -->
2. Pack environments for another machine: `pixi pack`
<!-- pause -->
3. [Cross-platform CI](https://github.com/ruben-arts/ros-example)

```yaml
jobs:
  strategy:
    matrix:
      os: [ubuntu, windows, macos]
  steps:
    - name: Setup Pixi and install environment
      uses: prefix-dev/setup-pixi

    - name: Run ROS node
      run: pixi run ros2 pkg list
```
<!-- pause -->
4. Package missing dependencies (if it blocks your research, it blocks someone else's research, too!):
   `rattler-build generate-recipe pypi some-package`

<!-- pause -->
5. Package AI/ML models as versioned, cached dependencies:
   https://prefix.dev/blog/packaging-ai-ml-models-as-conda-packages

<!--
speaker_note: |
  Treat these as doors the audience can open after the tutorial, not as five more demos.
  The shared theme is that tooling work compounds beyond one repository.
  For the CI teaser, mention that setup-pixi installs Pixi and prepares the environment; cache hits are useful because the lockfile is still in sync.
  The model-packaging teaser is about model files becoming lockable, cacheable, and traceable artifacts rather than side downloads hidden in setup scripts.
-->

<!-- end_slide -->

Key Insights
===

<!-- list_item_newlines: 2 -->

1. Environments are part of the method.

2. Tasks and lockfiles make projects runnable.

3. Packaging turns local code into shared infrastructure.

4. <span class="highlight">Research software</span> is part of the contribution.

<!-- pause -->

> Build systems that others can run, trust, extend, and build upon.

<!-- pause -->

## Thank you

`Tobias.Fischer@qut.edu.au` & `Peter.Corke@qut.edu.au`

QUT Centre for Robotics

Thanks to the **prefix.dev** team for creating Pixi, **Silvio Traversaro**,
**Alejandro Fontan**, **Nicolas Marticorena**, **Margaux Edwards**,
my **co-authors**, open-source contributors,
and the Australian Research Council.

# Questions?

<!--
speaker_note: |
  End by returning to the title.
  "Running systems" means less time recovering setup state and more time evaluating ideas.
-->

<!-- end_slide -->

References and Links
===

<!-- list_item_newlines: 2 -->

- [<span class="highlight">pixi.sh</span>](https://pixi.sh)

- [<span class="highlight">A RoboStack Tutorial: Using the Robot Operating System Alongside the Conda and Jupyter Data Science Ecosystems</span>](https://doi.org/10.1109/MRA.2021.3128367), IEEE Robotics & Automation Magazine, vol. 29, no. 2, June 2022

- [<span class="highlight">Pixi: Unified Software Development and Distribution for Robotics and AI</span>](https://arxiv.org/abs/2511.04827), arXiv:2511.04827

- [<span class="highlight">ROS2WASM: Bringing the Robot Operating System to the Web</span>](https://doi.org/10.1109/ICRA55743.2025.11127821), IEEE International Conference on Robotics and Automation (ICRA) 2025

- [<span class="highlight">VSLAM-LAB: A Comprehensive Framework for Visual SLAM Methods and Datasets</span>](https://arxiv.org/abs/2504.04457), IEEE/RSJ International Conference on Intelligent Robots and Systems (IROS) 2025

- [<span class="highlight">rattler.build</span>](https://rattler.build)
