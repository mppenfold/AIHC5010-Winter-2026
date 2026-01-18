#!/usr/bin/env python3
"""
make_submission_notebook.py

Extract the portion of a Jupyter notebook between two marker cells and
write it to a new notebook (default: submission.ipynb).

Markers are detected if a cell contains a line that is exactly:
  #MAINSTART
and later:
  #MAINEND

By default, the marker cells themselves are NOT included in the output.
"""

from __future__ import annotations

import argparse
import copy
from pathlib import Path
import nbformat
from nbformat.v4 import new_notebook


def _cell_source_as_text(cell) -> str:
    """Return cell source as a single string (nbformat can store it as list or str)."""
    src = cell.get("source", "")
    if isinstance(src, list):
        return "".join(src)
    return str(src)


def _cell_has_marker_line(cell, marker: str) -> bool:
    """True if the cell contains a line that equals marker (ignoring leading/trailing whitespace)."""
    text = _cell_source_as_text(cell)
    for line in text.splitlines():
        if line.strip() == marker:
            return True
    return False


def _find_marker_indices(nb, start_marker: str, end_marker: str) -> tuple[int, int]:
    """
    Return (start_idx, end_idx) for marker cells.

    start_idx is the index of the cell containing start_marker
    end_idx is the index of the first cell AFTER start_idx containing end_marker
    """
    start_idx = None
    end_idx = None

    for i, cell in enumerate(nb.cells):
        if start_idx is None:
            if _cell_has_marker_line(cell, start_marker):
                start_idx = i
        else:
            if _cell_has_marker_line(cell, end_marker):
                end_idx = i
                break

    if start_idx is None:
        raise ValueError(
            f"Start marker {start_marker!r} not found. "
            f"Add a cell containing a line exactly: {start_marker}"
        )
    if end_idx is None:
        raise ValueError(
            f"End marker {end_marker!r} not found after the start marker. "
            f"Add a cell containing a line exactly: {end_marker} after {start_marker}"
        )
    if end_idx <= start_idx:
        raise ValueError("End marker occurs before start marker (unexpected).")

    # Optional sanity check: warn/raise on multiple markers
    extra_starts = sum(_cell_has_marker_line(c, start_marker) for c in nb.cells)
    extra_ends = sum(_cell_has_marker_line(c, end_marker) for c in nb.cells)
    if extra_starts > 1 or extra_ends > 1:
        raise ValueError(
            f"Expected exactly 1 start and 1 end marker cell, but found "
            f"{extra_starts} start(s) and {extra_ends} end(s). "
            "Remove duplicates or make markers unique."
        )

    return start_idx, end_idx


def extract_submission_notebook(
    input_path: Path,
    output_path: Path,
    start_marker: str = "#MAINSTART",
    end_marker: str = "#MAINEND",
    include_marker_cells: bool = False,
    clear_outputs: bool = True,
    clear_execution_counts: bool = True,
) -> None:
    """
    Create output notebook from the section between marker cells.
    """
    nb = nbformat.read(str(input_path), as_version=4)

    start_idx, end_idx = _find_marker_indices(nb, start_marker, end_marker)

    if include_marker_cells:
        selected_cells = nb.cells[start_idx : end_idx + 1]
    else:
        selected_cells = nb.cells[start_idx + 1 : end_idx]

    # Deep copy so we don't mutate the original notebook structure
    selected_cells = copy.deepcopy(selected_cells)

    # Optionally clear outputs for cleaner submission notebooks
    for cell in selected_cells:
        if cell.get("cell_type") == "code":
            if clear_outputs:
                cell["outputs"] = []
            if clear_execution_counts:
                cell["execution_count"] = None

    out_nb = new_notebook(
        cells=selected_cells,
        metadata=nb.metadata,  # preserve kernelspec/language info if present
    )
    out_nb.nbformat = nb.nbformat
    out_nb.nbformat_minor = nb.nbformat_minor

    output_path.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(out_nb, str(output_path))

    print(
        f"Wrote {output_path} with {len(out_nb.cells)} cells "
        f"(extracted from cells {start_idx}..{end_idx} in {input_path})."
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input", "-i", required=True, help="Path to the full notebook (.ipynb)"
    )
    ap.add_argument(
        "--output",
        "-o",
        default="submission.ipynb",
        help="Output notebook path (default: submission.ipynb)",
    )
    ap.add_argument("--start", default="#MAINSTART", help="Start marker line")
    ap.add_argument("--end", default="#MAINEND", help="End marker line")
    ap.add_argument(
        "--include-markers",
        action="store_true",
        help="Include the marker cells themselves in the output",
    )
    ap.add_argument(
        "--keep-outputs",
        action="store_true",
        help="Keep code cell outputs (default clears outputs)",
    )
    ap.add_argument(
        "--keep-exec-counts",
        action="store_true",
        help="Keep execution counts (default clears execution counts)",
    )
    args = ap.parse_args()

    extract_submission_notebook(
        input_path=Path(args.input),
        output_path=Path(args.output),
        start_marker=args.start,
        end_marker=args.end,
        include_marker_cells=args.include_markers,
        clear_outputs=not args.keep_outputs,
        clear_execution_counts=not args.keep_exec_counts,
    )


if __name__ == "__main__":
    main()
