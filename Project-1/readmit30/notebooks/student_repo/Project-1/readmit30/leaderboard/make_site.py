#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\"/>
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
  <title>Readmit30 Leaderboard</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border-bottom: 1px solid #ddd; padding: 0.5rem; text-align: left; }
    th { position: sticky; top: 0; background: #fff; }
    .small { color: #666; font-size: 0.9rem; }
    .ok { color: #0a0; font-weight: 600; }
    .err { color: #a00; font-weight: 600; }
  </style>
</head>
<body>
  <h1>Readmit30 Leaderboard</h1>
  <p class=\"small\">Primary metric: AUROC. Tie-breakers: AUPRC, then Brier (lower is better).</p>
  {table}
  <p class=\"small\">Updated from <code>leaderboard/leaderboard.csv</code>.</p>
</body>
</html>
"""

def main():
    lb_csv = Path("leaderboard/leaderboard.csv")
    out = Path("docs/index.html")
    out.parent.mkdir(parents=True, exist_ok=True)

    if not lb_csv.exists():
        out.write_text(TEMPLATE.format(table="<p>No submissions yet.</p>"), encoding="utf-8")
        print(f"Wrote {out} (empty)")
        return

    df = pd.read_csv(lb_csv)

    # Sort: AUROC desc, AUPRC desc, Brier asc (NaNs go last)
    for col in ["auroc", "auprc", "brier"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values(by=["auroc", "auprc", "brier"], ascending=[False, False, True])

    # Make status nicer
    if "status" in df.columns:
        df["status"] = df["status"].apply(lambda s: f"<span class='ok'>OK</span>" if s == "OK" else f"<span class='err'>{s}</span>")

    table = df.to_html(index=False, escape=False)
    out.write_text(TEMPLATE.format(table=table), encoding="utf-8")
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
