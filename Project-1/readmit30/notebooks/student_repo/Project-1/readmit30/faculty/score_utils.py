import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

def score_predictions(hidden_labels_csv: str, predictions_csv: str):
    y = pd.read_csv(hidden_labels_csv)          # row_id, readmit30
    p = pd.read_csv(predictions_csv)            # row_id, prob_readmit30

    merged = y.merge(p, on="row_id", how="inner")
    if len(merged) != len(y):
        raise ValueError("Predictions missing row_ids or duplicated row_ids.")

    y_true = merged["readmit30"].astype(int).values
    y_prob = merged["prob_readmit30"].astype(float).values

    return {
        "auroc": float(roc_auc_score(y_true, y_prob)),
        "auprc": float(average_precision_score(y_true, y_prob)),
        "brier": float(brier_score_loss(y_true, y_prob)),
        "n": int(len(y_true)),
    }
