import json
import re
import subprocess
import sys
from importlib.util import find_spec

TOOLBOXES = {
    "bdsim": {
        "import_name": "bdsim",
        "pip_name": "bdsim",
        "wheel_prefixes": ["bdsim-"],
    },
    "roboticstoolbox": {
        "import_name": "roboticstoolbox",
        "pip_name": "roboticstoolbox-python",
        "wheel_prefixes": [
            "spatialmath_python-",
            "spatialgeometry-",
            "roboticstoolbox_python-",
        ],
    },
    "machinevisiontoolbox": {
        "import_name": "machinevisiontoolbox",
        "pip_name": "machinevision-toolbox-python",
        "wasm_no_deps": True,
        "wheel_prefixes": [
            "spatialmath_python-",
            "spatialgeometry-",
            "machinevision_toolbox_python-",
        ],
        "optional_wheel_prefixes": ["opencv_python-"],
        "fallback_packages": [
            "ansitable",
            "mvtb-data",
            "pillow",
            "requests",
            "tqdm",
            "opencv-python",
        ],
    },
    "pgraph": {
        "import_name": "pgraph",
        "pip_name": "pgraph-python",
        "wheel_prefixes": ["pgraph_python-"],
    },
    "spatialmath": {
        "import_name": "spatialmath",
        "pip_name": "spatialmath-python",
        "wheel_prefixes": ["spatialmath_python-"],
    },
}

PACKAGES = {
    "numpy": {"import_name": "numpy", "pip_name": "numpy"},
    "scipy": {"import_name": "scipy", "pip_name": "scipy"},
    "matplotlib": {"import_name": "matplotlib", "pip_name": "matplotlib"},
    "opencv": {"import_name": "cv2", "pip_name": "opencv-python", "wasm_no_deps": True},
}

IMPORT_TO_PIP = {
    "cv2": "opencv-python",
    "mvtbdata": "mvtb-data",
    "PIL": "pillow",
    "spatialmath": "spatialmath-python",
    "spatialgeometry": "spatialgeometry",
    "pgraph": "pgraph-python",
}


def _is_wasm() -> bool:
    return "pyodide" in sys.modules or "micropip" in sys.modules


def _is_installed(import_name: str) -> bool:
    return find_spec(import_name) is not None


def _import_missing_dependency(import_name: str):
    try:
        __import__(import_name)
        return None
    except ModuleNotFoundError as exc:
        return str(exc)
    except Exception:
        return None


def _missing_module_name(error_text: str):
    if not error_text:
        return None
    match = re.search(r"No module named '([^']+)'", error_text)
    return match.group(1) if match else None


async def _install_wasm_missing_imports(toolbox, spec, piplite_module):
    attempted = set()
    while True:
        missing_dep = _import_missing_dependency(spec["import_name"])
        if not missing_dep:
            return

        mod = _missing_module_name(missing_dep)
        if not mod:
            return

        pkg = IMPORT_TO_PIP.get(mod, mod)
        if pkg in attempted:
            raise RuntimeError(
                "Unable to resolve transitive dependencies for "
                f"'{toolbox}'. Last missing module: {mod}"
            )

        attempted.add(pkg)
        print(
            "setup_tutorial: "
            f"toolbox '{toolbox}' auto-dependency source=pypi "
            f"name=({pkg})"
        )
        await piplite_module.install([pkg], deps=False)


def _latest_matching(wheels, filename_prefix):
    matches = [w for w in wheels if w.rsplit("/", 1)[-1].startswith(filename_prefix)]
    return matches[-1] if matches else None


def _wheel_names(wheels):
    return [w.rsplit("/", 1)[-1] for w in wheels]


async def _pypi_wheels():
    from js import fetch

    resp = await fetch("/pypi/all.json")
    if not resp.ok:
        return []

    data = json.loads(await resp.text())
    wheels = []
    for pkg_data in data.values():
        for release_files in pkg_data.get("releases", {}).values():
            for item in release_files:
                filename = item.get("filename")
                if filename and filename.endswith(".whl"):
                    wheels.append(f"/pypi/{filename}")
    return sorted(set(wheels))


def _setup_matplotlib_inline():
    try:
        from IPython import get_ipython

        ip = get_ipython()
        if ip is not None:
            ip.run_line_magic("matplotlib", "inline")
    except Exception:
        pass


async def _install_wasm(toolboxes):
    import piplite

    wheels = await _pypi_wheels()

    for toolbox in toolboxes:
        spec = TOOLBOXES[toolbox]
        if _is_installed(spec["import_name"]):
            print(
                f"setup_tutorial: toolbox '{toolbox}' source=already installed in environment"
            )
            missing_dep = _import_missing_dependency(spec["import_name"])
            if missing_dep:
                if spec.get("bundle_only", False):
                    bundle_wheels = []
                    missing_required = []
                    for prefix in spec.get("wheel_prefixes", []):
                        wheel = _latest_matching(wheels, prefix)
                        if wheel:
                            bundle_wheels.append(wheel)
                        else:
                            missing_required.append(prefix)
                    if missing_required:
                        raise RuntimeError(
                            "Bundle-only toolbox has missing required wheel(s): "
                            f"{', '.join(missing_required)}"
                        )
                    print(
                        "setup_tutorial: "
                        f"toolbox '{toolbox}' source=bundle "
                        f"names=({', '.join(_wheel_names(bundle_wheels))})"
                    )
                    await piplite.install(bundle_wheels)
                    await _install_wasm_missing_imports(toolbox, spec, piplite)
                    continue
                print(
                    "setup_tutorial: "
                    f"toolbox '{toolbox}' source=pypi "
                    f"name=({spec['pip_name']})"
                )
                await piplite.install(
                    [spec["pip_name"]], deps=not spec.get("wasm_no_deps", False)
                )
                await _install_wasm_missing_imports(toolbox, spec, piplite)
            continue

        install_list = []
        missing_required = []
        for prefix in spec.get("wheel_prefixes", []):
            wheel = _latest_matching(wheels, prefix)
            if wheel:
                install_list.append(wheel)
            else:
                missing_required.append(prefix)

        for prefix in spec.get("optional_wheel_prefixes", []):
            wheel = _latest_matching(wheels, prefix)
            if wheel:
                install_list.append(wheel)

        if spec.get("bundle_only", False) and missing_required:
            raise RuntimeError(
                "Bundle-only toolbox has missing required wheel(s): "
                f"{', '.join(missing_required)}"
            )

        if install_list and not missing_required:
            deduped = []
            seen = set()
            for wheel in install_list:
                if wheel not in seen:
                    deduped.append(wheel)
                    seen.add(wheel)
            print(
                "setup_tutorial: "
                f"toolbox '{toolbox}' source=bundle "
                f"names=({', '.join(_wheel_names(deduped))})"
            )
            await piplite.install(deduped, deps=not spec.get("wasm_no_deps", False))
            companions = spec.get("fallback_packages", [])
            if companions:
                print(
                    "setup_tutorial: "
                    f"toolbox '{toolbox}' companion source=pypi "
                    f"names=({', '.join(companions)})"
                )
                await piplite.install(companions, deps=False)
            await _install_wasm_missing_imports(toolbox, spec, piplite)
            continue

        print(
            "setup_tutorial: "
            f"toolbox '{toolbox}' source=pypi "
            f"name=({spec['pip_name']})"
        )
        await piplite.install(
            [spec["pip_name"]], deps=not spec.get("wasm_no_deps", False)
        )
        companions = spec.get("fallback_packages", [])
        if companions:
            print(
                "setup_tutorial: "
                f"toolbox '{toolbox}' companion source=pypi "
                f"names=({', '.join(companions)})"
            )
            await piplite.install(companions, deps=False)
        await _install_wasm_missing_imports(toolbox, spec, piplite)


def _install_local(toolboxes):
    for toolbox in toolboxes:
        spec = TOOLBOXES[toolbox]
        if _is_installed(spec["import_name"]):
            print(
                f"setup_tutorial: toolbox '{toolbox}' source=already installed in environment"
            )
            continue
        print(
            "setup_tutorial: "
            f"toolbox '{toolbox}' source=pypi "
            f"name=({spec['pip_name']})"
        )
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", spec["pip_name"]]
        )


async def _install_wasm_packages(packages):
    import piplite

    for package in packages:
        spec = PACKAGES[package]
        if _is_installed(spec["import_name"]):
            continue
        if spec.get("wasm_no_deps"):
            await piplite.install([spec["pip_name"]], deps=False)
        else:
            await piplite.install([spec["pip_name"]])


def _install_local_packages(packages):
    for package in packages:
        spec = PACKAGES[package]
        if _is_installed(spec["import_name"]):
            continue
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", spec["pip_name"]]
        )


async def setup_tutorial(
    required_toolboxes=None,
    required_packages=None,
    install_missing=True,
    verbose=True,
):
    if required_toolboxes is None:
        required_toolboxes = []
    if required_packages is None:
        required_packages = []

    requested = [name.lower() for name in required_toolboxes]
    requested_packages = [name.lower() for name in required_packages]
    unknown = [name for name in requested if name not in TOOLBOXES]
    unknown_packages = [name for name in requested_packages if name not in PACKAGES]
    if unknown:
        supported = ", ".join(sorted(TOOLBOXES.keys()))
        raise ValueError(
            "Unknown toolbox name(s): "
            f"{', '.join(unknown)}. Supported names: {supported}."
        )
    if unknown_packages:
        supported = ", ".join(sorted(PACKAGES.keys()))
        raise ValueError(
            "Unknown package name(s): "
            f"{', '.join(unknown_packages)}. Supported names: {supported}."
        )

    print("Setting up tutorial environment — wait for the \u2705")

    if verbose:
        where = "JupyterLite/WASM" if _is_wasm() else "local Python"
        print(f"setup_tutorial: environment={where}")
        if requested:
            print(f"setup_tutorial: required_toolboxes={requested}")
        if requested_packages:
            print(f"setup_tutorial: required_packages={requested_packages}")

    if install_missing and requested:
        if _is_wasm():
            await _install_wasm(requested)
        else:
            _install_local(requested)
    elif requested:
        for toolbox in requested:
            spec = TOOLBOXES[toolbox]
            if _is_installed(spec["import_name"]):
                print(
                    f"setup_tutorial: toolbox '{toolbox}' source=already installed in environment"
                )
            else:
                print(
                    f"setup_tutorial: toolbox '{toolbox}' source=not installed (install_missing=False)"
                )
    if install_missing and requested_packages:
        if _is_wasm():
            await _install_wasm_packages(requested_packages)
        else:
            _install_local_packages(requested_packages)

    missing = [
        name for name in requested if not _is_installed(TOOLBOXES[name]["import_name"])
    ]
    if missing:
        raise RuntimeError(
            "Missing required toolbox imports after setup: " f"{', '.join(missing)}"
        )

    missing_packages = [
        name
        for name in requested_packages
        if not _is_installed(PACKAGES[name]["import_name"])
    ]
    if missing_packages:
        raise RuntimeError(
            "Missing required package imports after setup: "
            f"{', '.join(missing_packages)}"
        )

    _setup_matplotlib_inline()

    if verbose:
        parts = []
        if requested:
            toolbox_labels = ", ".join(TOOLBOXES[n]["import_name"] for n in requested)
            parts.append(f"toolboxes: {toolbox_labels}")
        if requested_packages:
            pkg_labels = ", ".join(PACKAGES[n]["pip_name"] for n in requested_packages)
            parts.append(f"packages: {pkg_labels}")
        summary = "; ".join(parts)
        print(f"\u2705 Setup complete — {summary}")


def initialize():
    raise RuntimeError(
        "setup_tutorial.initialize() is deprecated. "
        "Use: await setup_tutorial.setup_tutorial(required_toolboxes=[...])."
    )
