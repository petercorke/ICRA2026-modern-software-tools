from pathlib import Path


DEPENDENCY_LINE = (
    'ros-rolling-icra-ros-package = { path = "icra_ros_package/package.xml" }'
)


def main() -> None:
    tobi_dir = Path(__file__).resolve().parents[1]
    package_xml = tobi_dir / "icra_ros_package" / "package.xml"
    manifest = tobi_dir / "pixi.toml"

    if package_xml.exists() or not manifest.exists():
        return

    lines = manifest.read_text().splitlines(keepends=True)
    filtered_lines = [line for line in lines if line.strip() != DEPENDENCY_LINE]

    if filtered_lines != lines:
        manifest.write_text("".join(filtered_lines))


if __name__ == "__main__":
    main()
