import json
import os

nb_path = "Assignment1_Colab_Workflow.ipynb"
out_path = "Assignment1_Local.ipynb"

print(f"Reading {nb_path}...")
with open(nb_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

new_cells = []

# Header cell to fix paths and environment
setup_code = [
    "import os\n",
    "import sys\n",
    "# Set paths relative to this notebook (in notebooks/)\n",
    "# We assume structure: .../readmit30/notebooks (cwd)\n",
    "#                      .../readmit30/scripts/data\n",
    "base_dir = os.path.abspath(os.path.join(os.getcwd(), '..'))\n",
    "print(f'Base dir (readmit30): {base_dir}')\n",
    "os.environ['TRAIN_PATH'] = os.path.join(base_dir, 'scripts', 'data', 'public', 'train.csv')\n",
    "os.environ['DEV_PATH']   = os.path.join(base_dir, 'scripts', 'data', 'public', 'dev.csv')\n",
    "os.environ['TEST_PATH']  = os.path.join(base_dir, 'scripts', 'data', 'public', 'public_test.csv')\n",
    "os.environ['OUT_PATH']   = 'predictions.csv'\n",
    "\n",
    "print('Environment variables set for local execution.')\n"
]

setup_cell = {
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": setup_code
}
new_cells.append(setup_cell)

for cell in nb["cells"]:
    source_str = "".join(cell["source"])
    
    # Filter out cells specific to Colab/Workflow setup that don't apply locally
    if "git clone" in source_str:
        print("Skipping git clone cell")
        continue
    if "%cd student_repo" in source_str:
        print("Skipping cd student_repo cell")
        continue
    if "getpass" in source_str and "GitHub PAT" in source_str:
        print("Skipping GitHub authentication cell")
        continue
    if "git push" in source_str:
        print("Skipping git push cell")
        continue
    if "pip install" in source_str and "requirements.txt" in source_str:
        print("Skipping pip install requirements cell")
        continue
    if "pre-commit install" in source_str:
         print("Skipping pre-commit install cell")
         continue

    # Fix paths in python shell commands
    # Original expects running from repo root: Project-1/readmit30/scripts/...
    # We are in: .../readmit30/notebooks
    # So we want: ../scripts/...
    new_source = []
    for line in cell["source"]:
        if "Project-1/readmit30/scripts/" in line:
            # Replace with relative path from notebooks dir
            replaced = line.replace("Project-1/readmit30/scripts/", "../scripts/")
            new_source.append(replaced)
        else:
            new_source.append(line)
    cell["source"] = new_source

    new_cells.append(cell)

nb["cells"] = new_cells

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)

print(f"Created {out_path} with {len(new_cells)} cells.")
