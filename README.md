# Student Wellbeing Predictor

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Site-teal)](https://aryan7280.github.io/mental-health-score-predictor/)

> **ES 335: Machine Learning** · Aryan Mangal (25110058)
> **Website:** https://aryan7280.github.io/mental-health-score-predictor/
> **Repository:** https://github.com/Aryan7280/mental-health-score-predictor

The website (`docs/`) is the main deliverable. It explains the problem, data, method, evaluation, results, errors and
limitations, and includes an in-browser predictor that reproduces the saved model. Every number on the site is generated
from the pipeline outputs by `src/export_site.py`.

---

## 1. Problem and scope

**Question.** For a student whose country appears in the training data, how accurately can we predict their
`Mental_Health_Score` (1–10 self-rating) from age, gender, country, academic level, main platform, purpose of use,
daily social-media hours, phone unlocks, study hours, exercise hours and sleep hours? And how much of that accuracy
survives for students from countries never seen in training?

| | |
|---|---|
| Unit of analysis | One row = one student's survey response (single time point) |
| Target | `Mental_Health_Score`, continuous, regression (observed 3.6–9.4) |
| Prediction-time inputs | Habits and demographics only. `Stress_Level` is excluded: it is measured with the outcome and would not exist at prediction time |
| Success criterion | Lower RMSE than the mean baseline and a linear model, with a paired-bootstrap CI that excludes 0 |
| Not claimed | Causal effects, clinical validity, or results for populations outside this dataset |

## 2. Data

- **Source:** Shiva Singh, *Student Social Media & Mental Health Impact*, Kaggle (2024),
  https://www.kaggle.com/datasets/shivasingh4945/student-social-media-and-mental-health-impact. Public CSV, no credentials.
  `data/dataset.csv` is byte-identical to the downloaded file.
- **Access limits:** collection method, sampling and scoring instrument are undocumented; the data may be partly simulated.
- **Quality checks:**
  - 5,000 rows, 0 missing values, 2 exact duplicates removed, leaving 4,998 rows.
  - 10 negative exercise values clipped to 0.
  - Social media + study + sleep + exercise never exceeds 22.1 h, so no row is impossible.
  - The target has only 59 distinct values.
  - "Other" covers 38% of the `Country` column.
  - Platform almost determines purpose (95% of rows).
  - Usage hours and unlocks are highly correlated (r = 0.96).
  - Only 3 test rows have an exact feature twin in the training set.

## 3. Preprocessing

- Rule-based cleaning before the split, with nothing learned: deduplication and clipping.
- Learned preprocessing lives inside a scikit-learn `Pipeline`, so it is fit on training folds only:
  - `StandardScaler` on the 6 numeric features, for KNN and the linear models. Tree models get raw values.
  - `OneHotEncoder(handle_unknown="ignore")` on the 5 categorical features.

## 4. Evaluation protocol

- A single 80/20 split with seed 42: 3,998 training rows and 1,000 test rows.
- `GridSearchCV` with 5-fold CV on the **training set** tunes hyper-parameters. The final model is the one with the **lowest
  mean CV RMSE**, so the test set is never used for selection.
- The test set is used once, for the final metrics, 95% bootstrap CIs (1,000 resamples) and **paired** bootstrap
  comparisons against the selected model.
- The KNN validation curve (CV RMSE vs k) and the learning curves come from training-set CV only.
- The unseen-country check (`GroupKFold` by country), the `Stress_Level` ablation and the feature-group ablation all use CV on the
  training set.

## 5. Results (held-out test set, N = 1,000)

| Model | CV RMSE | Test RMSE [95% CI] | MAE | R² | ΔRMSE vs selected [95% CI] |
|---|---|---|---|---|---|
| **K-Nearest Neighbors (k=3, distance)**, selected | 0.391 ± 0.032 | **0.367** [0.335, 0.402] | 0.236 | 0.924 | – |
| Random Forest | 0.404 ± 0.017 | 0.384 [0.359, 0.412] | 0.276 | 0.917 | +0.018 [−0.016, 0.050] |
| Gradient Boosting | 0.448 ± 0.013 | 0.453 [0.428, 0.479] | 0.341 | 0.885 | +0.086 [0.052, 0.120] |
| Ridge (α=0.1) | 0.603 ± 0.024 | 0.622 [0.593, 0.652] | 0.480 | 0.783 | +0.255 [0.214, 0.293] |
| Linear Regression (baseline) | 0.603 ± 0.024 | 0.622 [0.593, 0.652] | 0.480 | 0.783 | +0.255 [0.214, 0.293] |
| Lasso (α=0.001) | 0.611 ± 0.021 | 0.629 [0.600, 0.657] | 0.495 | 0.778 | +0.262 [0.223, 0.300] |
| Linear, usage hours only (baseline) | 0.734 ± 0.029 | 0.756 [0.725, 0.786] | 0.607 | 0.680 | +0.388 [0.347, 0.429] |
| Mean / Dummy (baseline) | 1.263 ± 0.042 | 1.337 [1.292, 1.379] | 1.128 | −0.001 | +0.969 [0.918, 1.016] |

**How to read these results:**

- **KNN clearly beats both baselines.** It is ahead of the mean baseline and of linear regression, which points to local or
  non-linear structure in the data.
- **KNN vs Random Forest is a tie.** The paired CI includes 0, so this test set does not separate them.
- **Unseen countries (`GroupKFold`, CV RMSE):**
  - Mean baseline: 1.217
  - Linear: 0.731
  - KNN: 0.828
  - Random Forest: 0.680

  KNN's accuracy depends heavily on matching students from the same country. For new countries, Random Forest is the
  better choice, and errors are roughly twice as large.
- **`Stress_Level` ablation:** adding it barely changes CV RMSE (KNN 0.391 to 0.392; Ridge 0.604 to 0.599). It is excluded
  for validity, not because of accuracy.
- **Errors:**
  - Extremes are pulled toward the middle: bottom-band bias is +0.14 and top-band bias is −0.20.
  - The mixed "Other" country group is among the hardest to predict.
  - The largest single miss is about 2.3 points.

**Limitations:**

- The data's provenance is unknown.
- The results show association, not causation.
- All values are self-reported at a single time point.
- The model transfers weakly to new countries.
- Extreme scores are shrunk toward the middle.
- Everything rests on one train/test split.

## 6. Reproduce

```bash
git clone https://github.com/Aryan7280/mental-health-score-predictor.git
cd mental-health-score-predictor
pip install -r requirements.txt
python src/train.py        # split, tuning, CV selection, test metrics, ablations, error analysis -> reports/, models/
python src/evaluate.py     # static figures -> reports/figures/
python src/export_site.py  # regenerates docs/data.js and docs/figures/
pytest tests/
```

To view the website locally, open `docs/index.html` in a browser. It needs no server and no build step. GitHub Pages serves
the `docs/` folder.


## Acknowledgement

The dataset was collected and published by Shiva Singh (Kaggle). All cleaning, modelling, evaluation, the website and the tests in this
repository are my own work. This is an educational project and not a diagnostic tool.
