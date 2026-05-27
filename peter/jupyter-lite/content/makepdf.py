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
    "robotics.ipynb": "if NBCONVERT:\n    from spatialmath import BasePoseMatrix\n    BasePoseMatrix._color = False\n",
}

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
    with nb_file.open("r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    # Drop the intro markdown + setup cell, regardless of per-cell tags.
    if len(nb.cells) >= 2:
        nb.cells = nb.cells[2:]

    injected_cells = [nbformat.v4.new_code_cell("NBCONVERT = True\n")]

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
        "resource_paths": [
            str(nb_dir),
            str(nb_dir / "support"),
            str(nb_dir / "support/figs"),
            str(content_root / "support"),
            str(content_root / "support/figs"),
        ],
    }

    executor.preprocess(nb, resources)
    nb.cells = nb.cells[len(injected_cells):]

    body, _ = exporter.from_notebook_node(nb, resources=resources)
    pdf_path = outdir / (Path(nb_path).stem + ".pdf")
    pdf_path.write_bytes(body)
    print("wrote", pdf_path.resolve())
