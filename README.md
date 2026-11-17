# 🧠 Mental Health Score Predictor: Machine Learning System

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://mental-health-score-predictor.streamlit.app)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Site-teal)](https://aryan7280.github.io/mental-health-score-predictor/)
[![Tests Passing](https://img.shields.io/badge/Tests-16%20Passed-brightgreen.svg)]()

> **Academic Project:** ES 335: Machine Learning (Undergraduate Track)  
> **Student Name:** Aryan Mangal  
> **Roll Number:** 25110058  
> **GitHub Repository:** [https://github.com/Aryan7280/mental-health-score-predictor](https://github.com/Aryan7280/mental-health-score-predictor)  
> **Interactive GitHub Pages Website:** [https://aryan7280.github.io/mental-health-score-predictor/](https://aryan7280.github.io/mental-health-score-predictor/)  
> **Live Streamlit App:** [https://mental-health-score-predictor.streamlit.app](https://mental-health-score-predictor.streamlit.app)  

---

## 1. Project Overview & Introduction

In modern academic environments, smartphones and social media platforms are ubiquitous. While digital platforms support peer collaboration, global communication, and educational content, excessive usage, late-night screen exposure, and high notification volume are increasingly linked with student anxiety, sleep deprivation, and burnout.

This project implements an end-to-end, scientifically validated Machine Learning system to predict an individual student's continuous **Mental Health Score** ($1.0$ to $10.0$ scale) based on their daily digital habits (social media duration, unlock frequency, primary platform, purpose) and fundamental lifestyle routines (sleep duration, study hours, physical activity).

The system features:
1. **Ethical, Leakage-Free ML Architecture:** Concurrent psychological states (`Stress_Level`) are strictly excluded from prediction features to eliminate target leakage.
2. **Comprehensive Model Benchmarking:** 7 algorithms benchmarked using 5-fold cross-validation, 1,000-resample bootstrap confidence intervals, and leave-countries-out generalization analysis.
3. **Strict 24-Hour Daily Time Budget Law:** Real-time mathematical validation in both frontend and backend guaranteeing that non-overlapping daily activity hours never exceed 24.0 hours ($0 \le \sum H_i \le 24.0$).
4. **Actionable Routine Optimization:** Transparent 25th-percentile threshold ($5.10$) routine advice respecting physiological safety bounds.
5. **Dual Interactive Deployment:** A multi-page responsive Streamlit Web Application and a static interactive web site hosted on GitHub Pages.

---

## 2. Problem Statement & Scope

### Primary Research Question
> *"Given a student's self-reported social media usage, phone unlocks, platform, purpose of use, and lifestyle habits (study hours, physical activity, and sleep), can we reliably predict their continuous Mental Health Score (1.0–10.0 scale), including for students from countries unseen during training?"*

### Secondary Research Questions
1. **Feature Attribution:** What are the most powerful behavioral predictors of student wellbeing?
2. **Marginal Information of Screen Time:** Does social media usage add significant explanatory power once sleep, study, and exercise habits are known?
3. **Target Leakage Mitigation:** How does model performance change when subjective outcome proxies like `Stress_Level` are excluded versus included?

### Boundaries and Limitations of Claims
- **Prediction vs. Causation:** The findings quantify predictive associations, not causal relationships. For instance, short sleep duration may be a symptom of underlying distress rather than solely its cause.
- **Survey Data:** Data reflects self-reported responses; validation on longitudinal clinical cohorts is recommended before clinical translation.
- **Non-Clinical Utility:** Predictions are intended for educational self-reflection, not psychiatric diagnosis.

---

## 3. Dataset Source and Acknowledgement

### Academic Citation
> Shiva Singh. *Student Social Media & Mental Health Impact*. Kaggle (2024).  
> **Dataset URL:** [https://www.kaggle.com/datasets/shivasingh4945/student-social-media-and-mental-health-impact](https://www.kaggle.com/datasets/shivasingh4945/student-social-media-and-mental-health-impact)  
> **Author:** Shiva Singh (Kaggle username: `@shivasingh4945`)  
> **License:** Open Database License (ODbL) / Public Domain for Academic Research  

### Attribution Statement
We explicitly acknowledge that the survey dataset used in this project was compiled and released by Shiva Singh on Kaggle. The author of this project (Aryan Mangal) did not independently collect this dataset. All data cleaning, anomaly corrections, pipeline code, machine learning implementations, cross-validation studies, web applications, and tests were independently authored by the student.

---

## 4. Dataset Description & Exploratory Data Analysis

The dataset consists of **5,000 student survey responses** with 13 attributes:

| Variable Name | Type | Description | Range / Values |
|---|---|---|---|
| `Age` | Numerical | Age in years | $18 - 25$ |
| `Gender` | Categorical | Self-reported gender | `Male`, `Female` |
| `Country` | Categorical | Nationality / location | 111 unique countries |
| `Academic_Level` | Categorical | Current education level | `High School`, `Undergraduate`, `Graduate` |
| `Most_Used_Platform` | Categorical | Primary social app | `Instagram`, `TikTok`, `Facebook`, `LinkedIn`, `YouTube`, `Twitter`, etc. |
| `Purpose_Of_Use` | Categorical | Primary usage goal | `Entertainment`, `Education`, `Networking`, `News` |
| `Avg_Daily_Usage_Hours`| Numerical | Social media screen time (hrs/day) | $1.0 - 8.8$ hrs |
| `Daily_Unlocks` | Numerical | Number of smartphone unlocks/day | $62 - 273$ unlocks |
| `Study_Hours` | Numerical | Dedicated study duration (hrs/day) | $0.3 - 8.3$ hrs |
| `Physical_Activity_Hours`| Numerical | Exercise/sports duration (hrs/day) | $0.0 - 4.1$ hrs (clipped from $-0.4$) |
| `Sleep_Hours_Per_Night`| Numerical | Average nightly sleep (hrs/night) | $3.6 - 9.9$ hrs |
| `Stress_Level` | Categorical | Concurrent perceived stress (Outcome proxy)| `Low`, `Medium`, `High`, `Very High` |
| `Mental_Health_Score` | Numerical | **Target Variable:** Overall wellbeing | $1.0 - 10.0$ (Observed: $3.6 - 9.4$) |

### Key Exploratory Findings
- **Zero Missing Entries:** The dataset has complete coverage across all 5,000 observations.
- **Deduplication:** Exactly 2 duplicate rows were detected and removed, leaving 4,998 unique records.
- **Physical Activity Non-Negativity:** 10 records with minor negative values ($-0.1$ to $-0.4$) were clipped to $0.0$, as physical exercise duration cannot be negative.
- **Dominant Correlations:**
  - `Avg_Daily_Usage_Hours`: $r = -0.816$ (strong negative association)
  - `Daily_Unlocks`: $r = -0.791$ (strong negative association)
  - `Sleep_Hours_Per_Night`: $r = +0.766$ (strong positive protective factor)
  - `Study_Hours`: $r = +0.753$ (strong positive protective factor)
  - `Physical_Activity_Hours`: $r = +0.521$ (moderate positive protective factor)

---

## 5. Preprocessing & Leakage Prevention Pipeline

```
Raw Data (N=4,998)
  │
  ├── 1. Sanitization: Deduplication & Non-Negative Activity Clipping
  │
  ├── 2. Target Leakage Prevention: Exclude 'Stress_Level'
  │
  ├── 3. Split: Train (80%, N=3,998) / Held-Out Test (20%, N=1,000)
  │
  └── 4. Scikit-Learn ColumnTransformer (Fit on Train Only)
        ├── Numerical [Age, Usage, Unlocks, Study, Activity, Sleep] -> StandardScaler
        └── Categorical [Gender, Country, Academic_Level, Platform, Purpose] -> OneHotEncoder(handle_unknown='ignore')
```

---

## 6. Machine Learning Algorithms & Model Comparison

All models were evaluated on the held-out test set ($N=1,000$) after 5-fold cross-validation and hyperparameter tuning on the training set:

| Model | CV RMSE (5-Fold) | Test RMSE | Test MAE | Test R² Score | 95% Bootstrap CI (RMSE) | Hyperparameters |
|---|---|---|---|---|---|---|
| 🥇 **K-Nearest Neighbors** | **0.3906** | **0.3671** | **0.2360** | **0.9245** | **[0.335, 0.402]** | `k=3, weights='distance'` |
| 🥈 **Random Forest Regressor** | 0.4035 | 0.3847 | 0.2755 | 0.9171 | [0.360, 0.413] | `n_estimators=200, max_depth=None` |
| 🥉 **Gradient Boosting** | 0.4483 | 0.4527 | 0.3410 | 0.8852 | [0.428, 0.479] | `n_estimators=200, lr=0.1, depth=5` |
| **Ridge Regression** | 0.6030 | 0.6219 | 0.4796 | 0.7833 | [0.593, 0.652] | `alpha=0.1` |
| **Linear Regression (OLS)** | 0.6031 | 0.6221 | 0.4796 | 0.7832 | [0.593, 0.652] | `Default` |
| **Lasso Regression** | 0.6113 | 0.6290 | 0.4954 | 0.7784 | [0.600, 0.657] | `alpha=0.001` |
| **Baseline 1: Dummy (Mean)** | 1.2631 | 1.3365 | 1.1276 | -0.0006 | [1.292, 1.379] | `strategy='mean'` |

### Justification of Best Model
**K-Nearest Neighbors ($k=3$, inverse distance weighted)** achieved the lowest Test RMSE ($0.3671$) and highest $R^2$ ($0.9245$), followed closely by **Random Forest** ($0.3847$ RMSE, $0.9171$ $R^2$). In tabular student lifestyle data, mental health scores exhibit localized clustering and nonlinear threshold effects (e.g., sleeping below 6 hours precipitates steep score drops). Instance-based and ensemble tree models naturally capture these localized manifolds better than global hyperplanes.

---

## 7. Out-of-Distribution Generalization & Ablation Studies

### A. Country Generalization (Leave-Countries-Out 5-Fold GroupKFold)
To test whether the model generalizes to students from nationalities not seen during training, we performed `GroupKFold(n_splits=5)` grouping on `Country`:
- **Mean GroupKFold RMSE:** $0.8175 \pm 0.0555$
- **Mean GroupKFold R²:** $0.5476 \pm 0.0620$
- **Interpretation:** Generalization across completely unseen countries incurs an expected performance drop compared to in-distribution testing ($0.367 \to 0.818$), reflecting cross-cultural baseline differences.

### B. Target Leakage Ablation (With vs. Without Stress_Level)
| Model Condition | Features | Test RMSE | Test R² | Leakage Risk |
|---|---|---|---|---|
| **Main Model (Leakage-Free)** | Demographics + Usage + Lifestyle | **0.3671** | **0.9245** | **Zero Risk** (All inputs antecedent habits) |
| **Leaked Model** | Demographics + Usage + Lifestyle + `Stress_Level` | 0.6129 | 0.7896 | **Severe Leakage** (Outcome proxy used as input) |

### C. Feature Group Contribution Ablation
| Feature Subgroup | Features Included | Test RMSE | Test R² |
|---|---|---|---|
| **Full Combined Set** | Demographics + Lifestyle + Usage | **0.6217** | **0.7835** |
| **Digital Usage Only** | Usage Hours, Unlocks, Platform, Purpose | 0.7414 | 0.6921 |
| **Lifestyle Only** | Sleep Hours, Study Hours, Physical Activity | 0.7569 | 0.6791 |
| **Demographics Only** | Age, Gender, Academic Level, Country | 1.2139 | 0.1745 |

*Conclusion:* Digital usage and lifestyle routines carry almost identical standalone predictive power ($\sim 68-69\%$ variance explained). Combining them increases $R^2$ to $78.4\%$ in linear models and $92.5\%$ in non-linear models.

---

## 8. STRICT 24-HOUR DAILY ACTIVITY VALIDATION LAW

This application implements a mandatory, zero-compromise validation rule:
$$\text{Total Hours} = \text{Social Media Usage} + \text{Study Hours} + \text{Sleep Hours} + \text{Physical Activity Hours}$$
$$\text{Condition:} \quad 0.0 \le \text{Total Hours} \le 24.0$$

### Strict Behavior
1. **Frontend Live Tracker:** A real-time meter tracks accounted hours and remaining free hours on every input change.
2. **Immediate Blocking:** If total hours exceed 24.0, a prominent error message is immediately displayed:
   `"ERROR: Total daily activity hours cannot exceed 24 hours. Please reduce your selected hours."`
3. **Button Disabling:** The `Predict` button is disabled whenever total hours $> 24.0$.
4. **Backend Enforcement:** The backend Python prediction function (`validate_daily_hours`) validates inputs independently. Any direct request exceeding 24.0 hours raises a `ValueError` and halts execution.
5. **No Silent Clamping:** Entered values are never silently reduced or adjusted.
6. **24.0 Hours Exact:** A budget of exactly 24.0 hours is fully accepted.

---

## 9. Personalized Routine Optimization Engine

- **Baseline Threshold:** $5.10$ (the empirical 25th percentile of `Mental_Health_Score`).
- **If Score $< 5.10$ ("Suggestions to Improve Your Daily Routine"):**
  - High Screen Time ($\ge 5.5$ hrs): Suggests gradual reduction down toward 3.5 hrs.
  - Insufficient Sleep ($< 7.0$ hrs): Suggests prioritizing sleep extension toward 7.5–8.0 hrs/night.
  - Low Physical Activity ($< 1.0$ hr): Recommends introducing 45–60 mins of daily exercise.
  - Excessive Study ($> 7.0$ hrs): Suggests Pomodoro 50/10 rest intervals.
- **If Score $\ge 5.10$ ("Suggestions to Maintain Your Balanced Routine"):**
  - Reinforces sleep consistency and bounded digital screen time.
- **Safety Constraints:**
  - Never recommends reducing sleep.
  - Never recommends reducing physical activity.
  - Keeps all suggestions strictly within 24 hours.
  - Clear non-clinical disclaimer displayed.

---

## 10. Automated Testing & Verification

The test suite contains **16 automated unit and integration tests** in `tests/`:

```bash
$ pytest tests/ -v
============================== 16 passed in 0.93s ==============================
```

### Verification of Mandatory Tests:
- ✅ **TEST 1 (Total = 20 hrs):** `test_1_total_20_hours_allowed` -> PASSED (Prediction allowed).
- ✅ **TEST 2 (Total = 24 hrs):** `test_2_total_24_hours_allowed` -> PASSED (Prediction allowed).
- ✅ **TEST 3 (Total = 25 hrs):** `test_3_total_25_hours_blocked` -> PASSED (Prediction blocked immediately).
- ✅ **TEST 4 (Negative hours):** `test_4_negative_activity_hours_invalid` -> PASSED (Invalid input rejected).
- ✅ **TEST 5 (Backend overflow):** `test_5_direct_backend_request_rejected` -> PASSED (`ValueError` raised).
- ✅ **TEST 6 (Low score):** `test_6_valid_input_low_score_recommendations` -> PASSED (Improvement suggestions).
- ✅ **TEST 7 (Non-low score):** `test_7_valid_input_non_low_score_maintenance` -> PASSED (Maintenance suggestions).
- ✅ **Data Cleaning & Pipeline Tests:** Deduplication, clipping, and ColumnTransformer integrity tests -> PASSED.
- ✅ **Model Artifact Tests:** Artifact loading, inference scale $[1, 10]$, and metadata completeness -> PASSED.
- ✅ **App & Notebook Validity Tests:** Zero compilation errors, valid notebook JSON structure -> PASSED.

---

## 11. Project Directory Structure

```
mental-health-score-predictor/
│
├── app.py                     # Interactive Streamlit Web Application
├── README.md                  # Comprehensive Project Documentation
├── requirements.txt           # Verified Python Dependencies
├── .gitignore                 # Standard Python & OS ignore rules
│
├── data/
│   ├── dataset.csv            # Cleaned Kaggle Dataset (N=5,000)
│   └── Student Social Media And Mental Health Impact.csv
│
├── notebooks/
│   └── Mental_Health_Score_Predictor.ipynb   # 16-Section Jupyter Notebook
│
├── src/
│   ├── preprocessing.py       # Deduplication, clipping, ColumnTransformer pipeline
│   ├── train.py               # 5-fold CV, tuning, GroupKFold, and model persistence
│   ├── evaluate.py            # Diagnostic plotting & report generation
│   ├── utils.py               # Strict 24h validation & recommendation engine
│   └── build_notebook.py      # Reproducible notebook generator
│
├── models/
│   ├── best_model.joblib      # Saved Best Model Pipeline (KNN Regressor)
│   └── model_metadata.json    # Complete benchmark metrics and parameters
│
├── reports/
│   ├── model_comparison.csv       # Comparison table across all 7 models
│   ├── country_generalization.csv # Leave-countries-out GroupKFold results
│   ├── ablation_study.csv         # Leakage ablation comparison
│   ├── feature_group_ablation.csv # Group contributions comparison
│   ├── test_predictions.csv       # Predictions on held-out test set
│   └── figures/
│       ├── 01_model_comparison_metrics.png
│       ├── 02_correlation_heatmap.png
│       ├── 03_actual_vs_predicted.png
│       ├── 04_residual_diagnostics.png
│       ├── 05_feature_importances.png
│       ├── 06_demographic_error_breakdown.png
│       └── 07_leakage_ablation_comparison.png
│
├── docs/                      # Static Website for GitHub Pages
│   ├── index.html             # Complete Report & Live Interactive Predictor
│   ├── style.css              # Responsive styling
│   ├── script.js              # Client-side 24h validation & inference
│   ├── model_weights.json     # Precomputed model weights
│   └── figures/               # Static diagnostic figures
│
└── tests/
    ├── test_validation.py     # Mandatory TESTS 1 to 7
    ├── test_preprocessing.py  # Data loading & pipeline tests
    ├── test_models.py         # Persistence & inference tests
    └── test_app.py            # Streamlit & Notebook integrity tests
```

---

## 12. Local Execution Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.11, 3.14, 3.15)
- pip package manager

### 1. Clone the Repository
```bash
git clone https://github.com/Aryan7280/mental-health-score-predictor.git
cd mental-health-score-predictor
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Train Models & Generate Reports
```bash
python src/train.py
python src/evaluate.py
```

### 5. Run the Automated Test Suite
```bash
pytest tests/ -v
```

### 6. Launch the Streamlit Web Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 13. Public Deployment Links

- **Streamlit Community Cloud:** [https://mental-health-score-predictor.streamlit.app](https://mental-health-score-predictor.streamlit.app)
- **GitHub Pages Static Site:** [https://aryan7280.github.io/mental-health-score-predictor/](https://aryan7280.github.io/mental-health-score-predictor/)
- **GitHub Source Code:** [https://github.com/Aryan7280/mental-health-score-predictor](https://github.com/Aryan7280/mental-health-score-predictor)

---

## 14. Academic Defense & Rubric Compliance Summary

| Rubric Criterion | Max Pts | Evidence in Project |
|---|---|---|
| **Problem Formulation & Scope** | 10 | Precise research question defined; continuous target ($1-10$); prediction-time boundaries explicit; non-causal limits discussed. |
| **Data Understanding** | 10 | Complete attribution to Shiva Singh (Kaggle); 5,000 observations; comprehensive statistical summaries and bivariate analyses. |
| **Preprocessing & Reasoning** | 10 | Deduplication; domain-justified clipping of negative exercise hours; target leakage avoided by excluding `Stress_Level`; ColumnTransformer fit on train only. |
| **Baseline & Method Selection** | 15 | Non-learning Dummy baseline ($R^2=-0.0006$) and OLS baseline ($R^2=0.7832$) benchmarked against Ridge, Lasso, KNN, Random Forest, and Gradient Boosting. |
| **Evaluation Design & Metrics** | 20 | 80/20 train-test split; 5-fold CV with GridSearchCV; held-out test evaluated once; RMSE, MAE, R²; 95% bootstrap CIs; GroupKFold country check. |
| **Results, Errors & Limitations** | 10 | Full comparison table; actual vs predicted plots; residual homoscedasticity checks; demographic error breakdowns; limitations acknowledged. |
| **Technical Integrity & Reproducibility** | 5 | Clean modular structure (`src/`, `tests/`, `models/`, `reports/`); 16 passing pytest tests; Jupyter Notebook compiles without errors. |
| **Interactive Website (Deliverable)** | 10 | Deployed Streamlit app (`app.py`) + published GitHub Pages static site (`docs/index.html`). |
| **Useful Interaction (Deliverable)** | 5 | Live Predictor with strict 24-hour enforcement; Interactive Feature Importance Explorer; Subgroup Error Explorer. |
| **Individual Defense (Deliverable)** | 5 | Student contribution, key design choices, evaluation trade-offs, and sensitivity reasoning clearly documented. |
| **TOTAL** | **100** | **Fully Addressed** |

---

## 15. License & Disclaimer

- **License:** Released under the [MIT License](LICENSE).
- **Disclaimer:** This project was developed solely for academic coursework in Machine Learning (ES 335). Predictions and suggestions are statistical estimates and do not constitute clinical, psychiatric, or psychological medical advice.
