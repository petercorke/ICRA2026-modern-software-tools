import re
from pathlib import Path

import nbformat
from nbconvert.exporters import PDFExporter
from nbconvert.preprocessors import ExecutePreprocessor

NOTEBOOKS = [
    ("peter/jupyter-lite/content/spatial-math.ipynb", "Spatial Math"),
    ("peter/jupyter-lite/content/robotics.ipynb", "Robotics Toolbox"),
    ("peter/jupyter-lite/content/machine-vision.ipynb", "Machine Vision Toolbox"),
    ("peter/jupyter-lite/content/block-diagram.ipynb", "Block Diagram Simulation"),
]

EXPORT_ONLY_CODE = {
    "spatial-math.ipynb": "if NBCONVERT:\n    from spatialmath import BasePoseMatrix\n    BasePoseMatrix._color = False\n",
    "robotics.ipynb": """if NBCONVERT:
    from spatialmath import BasePoseMatrix
    BasePoseMatrix._color = False

    # Avoid a Matplotlib/Robotics Toolbox colorbar issue in the conda-forge export stack.
    from roboticstoolbox.mobile.PlannerBase import PlannerBase
    _plot_bg = PlannerBase.plot_bg

    def _plot_bg_without_colorbar(self, *args, **kwargs):
        kwargs.setdefault("colorbar", False)
        return _plot_bg(self, *args, **kwargs)

    PlannerBase.plot_bg = _plot_bg_without_colorbar

    import numpy as _np
    from spatialmath import Polygon2
    from roboticstoolbox.mobile.Animations import VehiclePolygon
    _vehicle_polygon_init = VehiclePolygon.__init__

    def _vehicle_polygon_init_compat(self, shape="car", scale=1, **kwargs):
        coords = None
        if isinstance(shape, Polygon2):
            coords = shape.vertices()
        elif isinstance(shape, _np.ndarray) and shape.ndim == 2:
            if shape.shape[0] == 2:
                coords = shape
            elif shape.shape[1] == 2:
                coords = shape.T

        if coords is not None:
            _vehicle_polygon_init(self, "car", scale=1, **kwargs)
            self._coords = coords * scale
            self._args = kwargs
            return None

        return _vehicle_polygon_init(self, shape, scale=scale, **kwargs)

    VehiclePolygon.__init__ = _vehicle_polygon_init_compat
""",
}

MARKDOWN_IMAGE_RE = re.compile(r"!\[[^\]]+\]\(([^)]+)\)")


def strip_markdown_image_alt_text(cell):
    if cell.cell_type == "markdown":
        cell.source = MARKDOWN_IMAGE_RE.sub(r"![](\1)", cell.source)


outdir = Path("_artifacts/part1-pdfs")
outdir.mkdir(parents=True, exist_ok=True)
content_root = Path("peter/jupyter-lite/content")

exporter = PDFExporter()
executor = ExecutePreprocessor(timeout=600, kernel_name="python3")
# Optional if you want to force TeX engine:
# exporter.latex_command = ["xelatex", "{filename}", "-interaction=nonstopmode"]

for nb_path, title in NOTEBOOKS:
    nb_file = Path(nb_path)
    nb_dir = nb_file.parent
    resource_paths = [
        nb_dir,
        nb_dir / "support",
        nb_dir / "support/figs",
        content_root / "support",
        content_root / "support/figs",
    ]
    with nb_file.open("r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Drop the intro markdown + setup cell, regardless of per-cell tags.
    if len(nb.cells) >= 2:
        nb.cells = nb.cells[2:]

    for cell in nb.cells:
        strip_markdown_image_alt_text(cell)

    injected_cells = [
        nbformat.v4.new_code_cell(
            "NBCONVERT = True\n"
            "import warnings\n"
            "warnings.filterwarnings('ignore')\n"
        )
    ]

    export_only_code = EXPORT_ONLY_CODE.get(nb_file.name)
    if export_only_code:
        injected_cells.append(nbformat.v4.new_code_cell(export_only_code))

    nb.cells = injected_cells + nb.cells

    author = "Peter Corke"
    nb.metadata["title"] = title
    nb.metadata["authors"] = [{"name": author}]

    resources = {
        "metadata": {
            "name": title,
            "title": title,
            "authors": [{"name": author}],
            # Helps nbconvert resolve local assets referenced by notebook markdown.
            "path": str(nb_dir),
        },
        "resource_paths": [str(path) for path in resource_paths],
    }

    executor.preprocess(nb, resources)
    nb.cells = nb.cells[len(injected_cells) :]

    body, _ = exporter.from_notebook_node(nb, resources=resources)
    pdf_path = outdir / (Path(nb_path).stem + ".pdf")
    pdf_path.write_bytes(body)
    print("wrote", pdf_path.resolve())
