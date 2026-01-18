#!/usr/bin/env python3
import argparse
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred", required=True, help="Path to predictions.csv")
    ap.add_argument("--test", required=True, help="Path to test.csv used for row_id check")
    args = ap.parse_args()

    pred = pd.read_csv(args.pred)
    test = pd.read_csv(args.test)

    required_cols = ["row_id", "prob_readmit30"]
    for c in required_cols:
        if c not in pred.columns:
            raise SystemExit(f"Missing column in predictions: {c}")

    if len(pred) != len(test):
        raise SystemExit(f"Row count mismatch: pred={len(pred)} test={len(test)}")

    if pred["row_id"].duplicated().any():
        raise SystemExit("Duplicate row_id found in predictions.")

    if not pred["row_id"].isin(test["row_id"]).all():
        raise SystemExit("row_id values in predictions must match test row_id set.")

    if pred["prob_readmit30"].isna().any():
        raise SystemExit("prob_readmit30 has NaNs.")

    if ((pred["prob_readmit30"] < 0) | (pred["prob_readmit30"] > 1)).any():
        raise SystemExit("prob_readmit30 must be in [0, 1].")

    print("OK: predictions.csv format is valid.")

if __name__ == "__main__":
    main()
