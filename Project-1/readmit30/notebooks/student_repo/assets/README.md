### Project-1 Set up details

Downloaded dataset from:

```
https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008
```

Ran:

```
python download_data.py --zip-path ~/Downloads/diabetes+130-us+hospitals+for+years+1999-2008.zip
```

Then made splits:

```
python make_splits.py
```

For scoring submissions, go into:

```
/Users/kline.timothy/repos/AIHC-5010-Winter-2026/Project-1/readmit30/faculty
```

Modify the 'submissions.csv' 

And then run:

python batch_score_submissions.py \
  --submissions ./submissions.csv \
  --hidden-test ../scripts/data/private/hidden_test.csv \
  --hidden-labels ../scripts/data/private/hidden_labels.csv \
  --train-path ../scripts/data/public/train.csv \
  --dev-path   ../scripts/data/public/dev.csv \
  --workdir "$(pwd)/faculty_workdir" --make-site

![Leader Board](../Project-1/readmit30/faculty/docs/leaderboard.png)