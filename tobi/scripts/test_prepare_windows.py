from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from prepare_windows import prepare_windows


class PrepareWindowsTests(unittest.TestCase):
    def test_converts_bash_block_and_splits_overflow_slide(self) -> None:
        source_text = """Build Your Own ROS / C++ / Python Packages
===

## Create a ROS package

```bash +exec +pty:80:4
ros2 pkg create
```

## Build the package

```bash +exec +pty:80:4
pixi install
```

<!-- pause -->

## Does it work?

```bash +exec +pty:80:4
pixi run ros2 run icra_ros_package icra_node
```
"""

        with TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "source.md"
            destination = Path(tmpdir) / "destination.md"
            source.write_text(source_text, encoding="utf-8")

            prepare_windows(source, destination)

            output = destination.read_text(encoding="utf-8")

        self.assertIn("```bat +exec\nros2 pkg create\n```", output)
        self.assertIn("```bat +exec\npixi install\n```", output)
        self.assertIn("<!-- end_slide -->\n\n## Does it work?", output)
        self.assertNotIn("+pty:80:4", output)


if __name__ == "__main__":
    unittest.main()
