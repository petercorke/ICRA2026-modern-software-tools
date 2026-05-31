# Beyond Fragments: A Unified Python Ecosystem for Robotics, Vision, and Control

## Motivation

> ... for any particular problem there is a wide choice of algorithms, and each of
> them may have several implementations. These will be written in a variety of
> languages, with a variety of API styles and conventions, and with variable code
> quality, documentation, support and licence conditions. This is a significant
> challenge for robotics today, and "cobbling together" together disparate pieces of
> software has become an essential skill for roboticists. ... Nevertheless, the software
> side of robotics is still harder and more time-consuming than it should be. This
> unfortunate complexity, and the sheer range of choice, presents a very real barrier to
> somebody new entering the field.
> 
> -- Robotics, Vision & Control: 3rd edition, 2023. Preface.

This part of the tutorial will provide a hands-on introduction to four toolboxes I've built and maintained
for more than 30 years, initially in MATLAB, more recently in Python.  Generations of roboticists have
grown up with these tools.

These tools are unashamedly classical, but the classics still have a lot to offer.

> Why burn thousands of GPU hours teaching a network to approximate 3D geometry when
> classical kinematics solves it exactly, instantly, and with zero data? Use the
> classics to give your models the flawless
> generalization and edge-case guarantees that pure data can only dream of. 
>

The toolboxes that I'll cover in the first half of the tutorial are:

* **Spatial Math**, the foundational ability to describe where things are and how they are moving in 3D space.  Mathematical
constructs like SE(3) matrices, twists, quaternions transformed into concrete Python representations.
* **Machine Vision Toolbox**, essentially OpenCV for humans with a uniform object-oriented interface, and connections to ROS and PyTorch.
* **Robotics Toolbox**, the foundational concepts from every robotics textbook: for mobile robots kinematics, planning, localization; for robotic arms kinematics, Jacobians, and dynamics.

* **Block Diagram Simulation**, the ability to simulate dynamic systems composed using a block-diagram formalism.

## The tutorial

In the limited time I can only highlight the key features and hopefully pique your interest to dive
deeper.  I will be presenting using Jupyter notebooks and these will be available before the tutorial.
The plan is that you can follow along on your own laptop.

[Go here to start following](https://petercorke.github.io/ICRA2026-modern-software-tools/).

The notebooks are all zero-install and work in your browser (Safari, Chrome defintely work).

### References
1. [The Robotics Toolbox: 30 years old and still going strong](https://www.youtube.com/watch?v=U37NMe7anXc&list=PL9Hnb9qlvGkRsNBDR7EATNAkzfEK0musp&index=5&pp=iAQB) video of Keynote talk at ICRA@40, 2024.
2. [Robotics Software: Past, Present, and Future](https://www.annualreviews.org/content/journals/10.1146/annurev-control-061323-095841), , ANNUAL REVIEW OF CONTROL, ROBOTICS, AND AUTONOMOUS SYSTEMS Volume 7, 2024.
3. [Not your grandmother’s toolbox – the Robotics Toolbox reinvented for Python](https://doi.org/10.1109/ICRA48506.2021.9561366), Peter Corke and Jesse Haviland, IEEE International Conference on Robotics and Automation (ICRA) 2021.
4. [Some notes about in browser execution](WASM.md), Peter 2026.
5. [Robotics, Vision and Control Fundamental Algorithms in Python](https://doi.org/10.1007/978-3-031-06469-2), 3rd edition, Springer 2023.