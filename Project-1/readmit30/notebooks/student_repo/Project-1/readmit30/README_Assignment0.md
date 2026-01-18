# Assignment 0 (Colab) — Git + Reproducible ML Submission Workflow

This is a **starter Colab notebook** that teaches the end-to-end workflow you'll use for the Readmit30 project:

1) authenticate to GitLab (PAT)
2) clone your team repo
3) install requirements
4) enable a commit hook to strip notebook outputs
5) run the submission notebook end-to-end
6) validate the submission file format
7) commit + push
8) tag a submission

> **Security note:** Do **not** print your token, and do not run commands like `git remote -v` after adding a token to the remote URL.
> Colab runtimes are ephemeral; once you disconnect, the token is gone.

## What you do
Open `notebooks/Assignment0_Colab_Workflow.ipynb` in Colab and run it top-to-bottom.

## What you submit
For each milestone, you will push:
- `notebooks/submission.ipynb` (your working submission notebook)
- optional helper code in `src/` or `scripts/`
- a Git tag like `milestone_wk3` or `final_week6`

