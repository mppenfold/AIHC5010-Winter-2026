#!/usr/bin/env python3
"""
Download + unpack the UCI Diabetes 130-US hospitals dataset into data/raw/.
Note: UCI may serve the dataset as a zip with a stable URL; if it changes,
download manually and place the zip in data/raw/ then re-run extraction.
"""

import argparse
import os
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

UCI_PAGE = "https://archive.ics.uci.edu/ml/datasets/diabetes+130-us+hospitals+for+years+1999-2008"
# NOTE: The direct file URL can occasionally change. If so, download manually from UCI.
POSSIBLE_ZIP_URLS = [
    # Some mirrors / legacy paths have existed; keep this list editable.
    # If none work, manual download is the fallback.
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip-path", default="", help="If set, use this local zip instead of downloading.")
    ap.add_argument("--outdir", default="data/raw", help="Where to store raw files.")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    zip_path = Path(args.zip_path) if args.zip_path else outdir / "diabetes_130US.zip"

    if args.zip_path:
        if not zip_path.exists():
            raise FileNotFoundError(f"Provided --zip-path does not exist: {zip_path}")
    else:
        downloaded = False
        for url in POSSIBLE_ZIP_URLS:
            try:
                print(f"Trying download: {url}")
                urlretrieve(url, zip_path)
                downloaded = True
                break
            except Exception as e:
                print(f"  failed: {e}")
        if not downloaded:
            raise RuntimeError(
                "Could not download automatically.\n"
                f"Please download the dataset zip manually from:\n  {UCI_PAGE}\n"
                f"Then place it at: {zip_path}\n"
                "and re-run this script with --zip-path."
            )

    print(f"Using zip: {zip_path}")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(outdir)

    print(f"Extracted to: {outdir}")
    print("Next: run scripts/01_make_splits.py")

if __name__ == "__main__":
    main()
