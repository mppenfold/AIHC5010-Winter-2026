#!/usr/bin/env python3
"""
Create train/dev/public_test/hidden_test splits.

- Uses patient-level grouping if patient_nbr exists.
- Creates a binary label: readmit30 = 1 if readmitted == '<30' else 0.
- Saves:
  data/public/{train,dev,public_test}.csv
  data/private/hidden_test.csv   (faculty only)
"""

import argparse
from pathlib import Path
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

def build_label(df: pd.DataFrame) -> pd.Series:
    # UCI uses 'readmitted' values like '<30', '>30', 'NO'
    return (df["readmitted"].astype(str).str.strip() == "<30").astype(int)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-csv", default="data/raw/diabetic_data.csv",
                    help="Path to the main CSV after extraction.")
    ap.add_argument("--out-public", default="data/public")
    ap.add_argument("--out-private", default="data/private")
    ap.add_argument("--seed", type=int, default=1337)
    ap.add_argument("--test-size", type=float, default=0.20)   # hidden_test
    ap.add_argument("--dev-size", type=float, default=0.20)    # dev out of remaining
    args = ap.parse_args()

    raw_csv = Path(args.raw_csv)
    if not raw_csv.exists():
        raise FileNotFoundError(f"Raw CSV not found: {raw_csv}")

    df = pd.read_csv(raw_csv)

    # Minimal hygiene: ensure we have an id
    if "encounter_id" not in df.columns:
        df.insert(0, "encounter_id", range(len(df)))

    df["row_id"] = df["encounter_id"]
    df["readmit30"] = build_label(df)

    # Features: drop label fields (keep readmitted for sanity? better drop)
    # Keep readmitted only in internal processing.
    feature_df = df.drop(columns=["readmitted"])

    out_public = Path(args.out_public); out_public.mkdir(parents=True, exist_ok=True)
    out_private = Path(args.out_private); out_private.mkdir(parents=True, exist_ok=True)

    # Group split if possible
    groups = feature_df["patient_nbr"] if "patient_nbr" in feature_df.columns else feature_df["row_id"]

    # 1) hidden_test split
    gss1 = GroupShuffleSplit(n_splits=1, test_size=args.test_size, random_state=args.seed)
    train_dev_idx, hidden_idx = next(gss1.split(feature_df, groups=groups))

    train_dev = feature_df.iloc[train_dev_idx].reset_index(drop=True)
    hidden = feature_df.iloc[hidden_idx].reset_index(drop=True)

    # 2) dev split from remaining
    groups_td = train_dev["patient_nbr"] if "patient_nbr" in train_dev.columns else train_dev["row_id"]
    gss2 = GroupShuffleSplit(n_splits=1, test_size=args.dev_size, random_state=args.seed + 1)
    train_idx, dev_idx = next(gss2.split(train_dev, groups=groups_td))

    train = train_dev.iloc[train_idx].reset_index(drop=True)
    dev = train_dev.iloc[dev_idx].reset_index(drop=True)

    # 3) public_test is unlabeled (for format checking) - sample from dev or hidden?
    # We’ll sample from dev to avoid giving away hidden distribution.
    public_test = dev.drop(columns=["readmit30"]).sample(frac=1.0, random_state=args.seed).reset_index(drop=True)

    # Save public
    train.to_csv(out_public / "train.csv", index=False)
    dev.to_csv(out_public / "dev.csv", index=False)
    public_test.to_csv(out_public / "public_test.csv", index=False)

    # Save private
    hidden.to_csv(out_private / "hidden_test.csv", index=False)
    hidden[["row_id", "readmit30"]].to_csv(out_private / "hidden_labels.csv", index=False)

    # Small dictionary
    (out_public / "data_dictionary.md").write_text(
        "# Readmit30 Data\n\n"
        "- `row_id`: unique encounter identifier used for submissions\n"
        "- `readmit30`: label (1 if readmitted within 30 days)\n"
        "\n"
        "All other columns are features.\n"
    )

    print("Wrote:")
    print(f"  {out_public/'train.csv'}")
    print(f"  {out_public/'dev.csv'}")
    print(f"  {out_public/'public_test.csv'}")
    print(f"  {out_private/'hidden_test.csv'} (faculty only)")
    print("Next: distribute data/public/* + notebooks/submission_template.ipynb")

if __name__ == "__main__":
    main()
