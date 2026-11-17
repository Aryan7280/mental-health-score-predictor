"""
Training and evaluation protocol for the Mental Health Score Predictor.

Design (every number on the website is produced by this script):

1. Clean data (dedupe, clip impossible negative activity hours) and make ONE
   stratification-free 80/20 train/test split with a fixed seed.
2. All learned preprocessing (StandardScaler, OneHotEncoder) lives inside a
   scikit-learn Pipeline, so it is re-fit on each training fold only.
3. Hyper-parameters are tuned with 5-fold CV on the TRAINING set only.
4. The final model is selected by mean CV RMSE (never by test RMSE).
5. The held-out test set is used once, to report final metrics, bootstrap
   confidence intervals and paired bootstrap comparisons against baselines.
6. Secondary analyses (country hold-out, Stress_Level ablation, feature-group
   ablation) use cross-validation on the training set, so the test set is not
   reused for any decision.
7. Error analysis (subgroups, score bands, worst cases, permutation importance)
   is computed on the test predictions for interpretation only.
"""
import os
import sys
import json
import warnings

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, GroupKFold, KFold, cross_validate, learning_curve
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.preprocessing import (
    CATEGORICAL_FEATURES,
    LEAKAGE_COLUMN,
    NUMERICAL_FEATURES,
    TARGET_COLUMN,
    get_preprocessor,
    load_and_clean_data,
    split_data,
)

warnings.filterwarnings("ignore")

SEED = 42
N_BOOT = 1000
FEATURES = NUMERICAL_FEATURES + CATEGORICAL_FEATURES


# ----------------------------------------------------------------------------
# Metric helpers
# ----------------------------------------------------------------------------
def compute_metrics(y_true, y_pred):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    return {
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "R2": float(r2_score(y_true, y_pred)),
    }


def bootstrap_ci(y_true, y_pred, n_bootstraps=N_BOOT, ci=0.95, random_state=SEED):
    """Percentile bootstrap CI for RMSE, MAE and R2 on the test set."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    rng = np.random.RandomState(random_state)
    n = len(y_true)
    rmses, maes, r2s = [], [], []
    for _ in range(n_bootstraps):
        idx = rng.randint(0, n, n)
        rmses.append(np.sqrt(mean_squared_error(y_true[idx], y_pred[idx])))
        maes.append(mean_absolute_error(y_true[idx], y_pred[idx]))
        r2s.append(r2_score(y_true[idx], y_pred[idx]))
    lo, hi = (1 - ci) / 2 * 100, (1 - (1 - ci) / 2) * 100
    return {
        "RMSE_CI": (float(np.percentile(rmses, lo)), float(np.percentile(rmses, hi))),
        "MAE_CI": (float(np.percentile(maes, lo)), float(np.percentile(maes, hi))),
        "R2_CI": (float(np.percentile(r2s, lo)), float(np.percentile(r2s, hi))),
    }


def paired_bootstrap_rmse_diff(y_true, pred_a, pred_b, n_bootstraps=N_BOOT, random_state=SEED):
    """
    Paired bootstrap of RMSE(b) - RMSE(a) resampling the SAME test rows for both
    models. Positive values mean model a is better. Returns mean, 95% CI and the
    share of resamples in which a beats b.
    """
    y_true, pred_a, pred_b = map(np.asarray, (y_true, pred_a, pred_b))
    rng = np.random.RandomState(random_state)
    n = len(y_true)
    diffs = []
    for _ in range(n_bootstraps):
        idx = rng.randint(0, n, n)
        ra = np.sqrt(np.mean((y_true[idx] - pred_a[idx]) ** 2))
        rb = np.sqrt(np.mean((y_true[idx] - pred_b[idx]) ** 2))
        diffs.append(rb - ra)
    diffs = np.array(diffs)
    return {
        "mean": float(diffs.mean()),
        "ci_low": float(np.percentile(diffs, 2.5)),
        "ci_high": float(np.percentile(diffs, 97.5)),
        "p_a_better": float((diffs > 0).mean()),
    }


def make_pipeline(regressor, scale=True, num=None, cat=None):
    num = NUMERICAL_FEATURES if num is None else num
    cat = CATEGORICAL_FEATURES if cat is None else cat
    transformers = []
    if num:
        transformers.append(("num", StandardScaler() if scale else "passthrough", num))
    if cat:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat))
    return Pipeline([
        ("preprocessor", ColumnTransformer(transformers, remainder="drop")),
        ("regressor", regressor),
    ])


def cv_rmse(pipeline, X, y, cv, groups=None):
    scores = cross_validate(pipeline, X, y, cv=cv, groups=groups,
                            scoring=["neg_root_mean_squared_error", "neg_mean_absolute_error", "r2"],
                            n_jobs=-1)
    rmse = -scores["test_neg_root_mean_squared_error"]
    return {
        "RMSE_mean": float(rmse.mean()),
        "RMSE_std": float(rmse.std(ddof=1)),
        "MAE_mean": float(-scores["test_neg_mean_absolute_error"].mean()),
        "R2_mean": float(scores["test_r2"].mean()),
        "fold_rmse": [float(v) for v in rmse],
    }


# ----------------------------------------------------------------------------
# Candidate models
# ----------------------------------------------------------------------------
def model_configs():
    return {
        "Baseline: Mean (Dummy)": {
            "pipeline": Pipeline([("preprocessor", get_preprocessor(False)),
                                  ("regressor", DummyRegressor(strategy="mean"))]),
            "grid": {}, "role": "baseline",
            "why": "Predicts the training mean for everyone. Any useful model must beat it.",
        },
        "Baseline: Linear (usage hours only)": {
            "pipeline": make_pipeline(LinearRegression(), num=["Avg_Daily_Usage_Hours"], cat=[]),
            "grid": {}, "role": "baseline",
            "why": "One-feature rule of thumb: 'more social media, lower score'. Tests whether the other features add anything.",
        },
        "Linear Regression": {
            "pipeline": make_pipeline(LinearRegression()),
            "grid": {}, "role": "baseline",
            "why": "Interpretable additive model on all features; the main learned baseline.",
        },
        "Ridge Regression": {
            "pipeline": make_pipeline(Ridge(random_state=SEED)),
            "grid": {"regressor__alpha": [0.01, 0.1, 1.0, 10.0, 50.0, 100.0]}, "role": "candidate",
            "why": "L2 penalty stabilises coefficients of correlated inputs (usage hours vs. unlocks, r = 0.96).",
        },
        "Lasso Regression": {
            "pipeline": make_pipeline(Lasso(random_state=SEED, max_iter=5000)),
            "grid": {"regressor__alpha": [0.001, 0.005, 0.01, 0.05, 0.1]}, "role": "candidate",
            "why": "L1 penalty tests whether the 100+ one-hot country/platform columns can be dropped.",
        },
        "K-Nearest Neighbors": {
            "pipeline": make_pipeline(KNeighborsRegressor()),
            "grid": {"regressor__n_neighbors": [3, 5, 7, 9, 11, 15],
                     "regressor__weights": ["uniform", "distance"]}, "role": "candidate",
            "why": "Local, non-parametric: predicts from the most similar students. Needs scaled inputs.",
        },
        "Random Forest": {
            "pipeline": make_pipeline(RandomForestRegressor(random_state=SEED, n_jobs=-1), scale=False),
            "grid": {"regressor__n_estimators": [200],
                     "regressor__max_depth": [8, 12, 16, None],
                     "regressor__min_samples_leaf": [1, 3]}, "role": "candidate",
            "why": "Captures non-linear thresholds and interactions without scaling; robust default for tabular data.",
        },
        "Gradient Boosting": {
            "pipeline": make_pipeline(GradientBoostingRegressor(random_state=SEED), scale=False),
            "grid": {"regressor__n_estimators": [100, 200],
                     "regressor__learning_rate": [0.05, 0.1],
                     "regressor__max_depth": [3, 5]}, "role": "candidate",
            "why": "Sequential trees fit residuals; strong on tabular data but easier to overfit.",
        },
    }


def score_band(y):
    return pd.cut(y, bins=[0, 5.1, 6.0, 7.0, 8.0, 10.1],
                  labels=["< 5.1 (bottom 25%)", "5.1 - 6.0", "6.0 - 7.0", "7.0 - 8.0", ">= 8.0"],
                  right=False)


def subgroup_table(frame, col, min_n=20):
    rows = []
    for key, g in frame.groupby(col, observed=True):
        if len(g) < min_n:
            continue
        m = compute_metrics(g["actual"], g["pred"])
        rows.append({"group": col, "value": str(key), "n": int(len(g)),
                     "RMSE": round(m["RMSE"], 4), "MAE": round(m["MAE"], 4),
                     "bias": round(float((g["pred"] - g["actual"]).mean()), 4)})
    return rows


# ----------------------------------------------------------------------------
# Main protocol
# ----------------------------------------------------------------------------
def train_and_compare_models(csv_path="data/dataset.csv"):
    os.makedirs("models", exist_ok=True)
    os.makedirs("reports", exist_ok=True)

    print("1. Loading, cleaning and splitting data ...")
    raw = pd.read_csv(csv_path)
    df = load_and_clean_data(csv_path)
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=SEED)
    threshold_25th = float(np.percentile(y_train, 25))
    print(f"   rows={len(df)}  train={len(X_train)}  test={len(X_test)}  25th pct (train)={threshold_25th:.2f}")

    data_quality = {
        "raw_rows": int(len(raw)),
        "exact_duplicates_removed": int(raw.duplicated().sum()),
        "rows_after_cleaning": int(len(df)),
        "missing_values": int(raw.isna().sum().sum()),
        "negative_activity_clipped": int((raw["Physical_Activity_Hours"] < 0).sum()),
        "max_daily_hours_sum": float((df["Avg_Daily_Usage_Hours"] + df["Study_Hours"]
                                      + df["Sleep_Hours_Per_Night"] + df["Physical_Activity_Hours"]).max()),
        "n_countries": int(df["Country"].nunique()),
        "share_country_other": float((df["Country"] == "Other").mean()),
        "target_unique_values": int(df[TARGET_COLUMN].nunique()),
        "test_rows_with_identical_features_in_train": int(
            X_test.merge(X_train.drop_duplicates(), how="inner", on=FEATURES).shape[0]),
    }

    cv = KFold(n_splits=5, shuffle=True, random_state=SEED)
    configs = model_configs()

    print("\n2. Tuning on training folds (5-fold CV) ...")
    fitted, cv_info, params, searches = {}, {}, {}, {}
    for name, cfg in configs.items():
        pipe = cfg["pipeline"]
        if cfg["grid"]:
            search = GridSearchCV(pipe, cfg["grid"], cv=cv, scoring="neg_root_mean_squared_error",
                                  n_jobs=-1, refit=True)
            search.fit(X_train, y_train)
            searches[name] = search
            i = search.best_index_
            folds = [-search.cv_results_[f"split{k}_test_score"][i] for k in range(5)]
            cv_info[name] = {"RMSE_mean": float(np.mean(folds)), "RMSE_std": float(np.std(folds, ddof=1))}
            params[name] = {k.replace("regressor__", ""): v for k, v in search.best_params_.items()}
            fitted[name] = search.best_estimator_
        else:
            info = cv_rmse(pipe, X_train, y_train, cv)
            cv_info[name] = {"RMSE_mean": info["RMSE_mean"], "RMSE_std": info["RMSE_std"]}
            params[name] = {}
            fitted[name] = clone(pipe).fit(X_train, y_train)
        print(f"   {name:38s} CV RMSE = {cv_info[name]['RMSE_mean']:.4f} +/- {cv_info[name]['RMSE_std']:.4f}  {params[name]}")

    # ---- Validation curve (KNN grid) and learning curves, training set only ----
    knn_res = pd.DataFrame(searches["K-Nearest Neighbors"].cv_results_)
    pd.DataFrame({
        "k": knn_res["param_regressor__n_neighbors"].astype(int),
        "weights": knn_res["param_regressor__weights"].astype(str),
        "CV_RMSE": (-knn_res["mean_test_score"]).round(4),
        "CV_RMSE_Std": knn_res["std_test_score"].round(4),
    }).sort_values(["weights", "k"]).to_csv("reports/knn_validation_curve.csv", index=False)

    lc_rows = []
    for name in ["K-Nearest Neighbors", "Random Forest", "Linear Regression"]:
        sizes, tr_s, va_s = learning_curve(clone(fitted[name]), X_train, y_train, cv=cv,
                                           train_sizes=np.linspace(0.1, 1.0, 6),
                                           scoring="neg_root_mean_squared_error", n_jobs=-1)
        for n, t, v in zip(sizes, tr_s, va_s):
            lc_rows.append({"Model": name, "Train_Size": int(n),
                            "Train_RMSE": round(float(-t.mean()), 4), "CV_RMSE": round(float(-v.mean()), 4)})
    pd.DataFrame(lc_rows).to_csv("reports/learning_curves.csv", index=False)

    # ---- Model selection uses CV only ------------------------------------
    best_name = min(cv_info, key=lambda n: cv_info[n]["RMSE_mean"])
    best_model = fitted[best_name]
    print(f"\n   Selected by CV RMSE: {best_name}")
    joblib.dump(best_model, "models/best_model.joblib")

    # ---- Single use of the test set --------------------------------------
    print("\n3. Final evaluation on the held-out test set ...")
    preds = {n: m.predict(X_test) for n, m in fitted.items()}
    rows = []
    for name in configs:
        m = compute_metrics(y_test, preds[name])
        ci = bootstrap_ci(y_test, preds[name])
        diff = paired_bootstrap_rmse_diff(y_test, preds[best_name], preds[name]) if name != best_name else None
        rows.append({
            "Model": name,
            "Role": "selected" if name == best_name else configs[name]["role"],
            "CV_RMSE": round(cv_info[name]["RMSE_mean"], 4),
            "CV_RMSE_Std": round(cv_info[name]["RMSE_std"], 4),
            "Test_RMSE": round(m["RMSE"], 4),
            "Test_MAE": round(m["MAE"], 4),
            "Test_R2": round(m["R2"], 4),
            "Test_RMSE_CI_Low": round(ci["RMSE_CI"][0], 4),
            "Test_RMSE_CI_High": round(ci["RMSE_CI"][1], 4),
            "Delta_RMSE_vs_Selected": None if diff is None else round(diff["mean"], 4),
            "Delta_CI_Low": None if diff is None else round(diff["ci_low"], 4),
            "Delta_CI_High": None if diff is None else round(diff["ci_high"], 4),
            "P_Selected_Better": None if diff is None else round(diff["p_a_better"], 4),
            "Best_Params": json.dumps(params[name]) if params[name] else "default",
            "Why": configs[name]["why"],
        })
    results_df = pd.DataFrame(rows).sort_values("CV_RMSE").reset_index(drop=True)
    results_df.to_csv("reports/model_comparison.csv", index=False)
    print(results_df[["Model", "CV_RMSE", "Test_RMSE", "Test_MAE", "Test_R2", "Delta_RMSE_vs_Selected"]].to_string(index=False))

    # ---- 4. Country hold-out (training set only) ---------------------------
    print("\n4. Leave-countries-out GroupKFold on the training set ...")
    gkf = GroupKFold(n_splits=5)
    groups = X_train["Country"]
    country_rows = []
    for name in ["Baseline: Mean (Dummy)", "Linear Regression", "K-Nearest Neighbors", "Random Forest"]:
        rnd = cv_rmse(clone(fitted[name]), X_train, y_train, cv)
        grp = cv_rmse(clone(fitted[name]), X_train, y_train, gkf, groups=groups)
        country_rows.append({
            "Model": name,
            "Random_KFold_RMSE": round(rnd["RMSE_mean"], 4),
            "Country_GroupKFold_RMSE": round(grp["RMSE_mean"], 4),
            "Country_GroupKFold_RMSE_Std": round(grp["RMSE_std"], 4),
            "Country_GroupKFold_R2": round(grp["R2_mean"], 4),
        })
        print(f"   {name:28s} random={rnd['RMSE_mean']:.3f}  unseen-country={grp['RMSE_mean']:.3f}")
    pd.DataFrame(country_rows).to_csv("reports/country_generalization.csv", index=False)

    # ---- 5. Stress_Level ablation (training CV, same model families) -------
    print("\n5. Stress_Level ablation (5-fold CV on training set) ...")
    X_train_s = df.loc[X_train.index, FEATURES + [LEAKAGE_COLUMN]]
    best_reg = best_model.named_steps["regressor"]
    ablation_rows = []
    for fam, reg, scale in [(best_name, best_reg, True), ("Ridge Regression", Ridge(alpha=1.0), True)]:
        without = cv_rmse(make_pipeline(clone(reg), scale), X_train, y_train, cv)
        with_s = cv_rmse(make_pipeline(clone(reg), scale, cat=CATEGORICAL_FEATURES + [LEAKAGE_COLUMN]),
                         X_train_s, y_train, cv)
        for cond, r in [("Without Stress_Level (used)", without), ("With Stress_Level (excluded)", with_s)]:
            ablation_rows.append({"Model": fam, "Condition": cond,
                                  "CV_RMSE": round(r["RMSE_mean"], 4), "CV_R2": round(r["R2_mean"], 4)})
        print(f"   {fam:22s} without={without['RMSE_mean']:.3f}  with={with_s['RMSE_mean']:.3f}")
    pd.DataFrame(ablation_rows).to_csv("reports/ablation_study.csv", index=False)

    # ---- 6. Feature group ablation (training CV) ---------------------------
    print("\n6. Feature-group ablation (5-fold CV on training set) ...")
    groups_dict = {
        "Demographics only (age, gender, country, level)": (["Age"], ["Gender", "Country", "Academic_Level"]),
        "Lifestyle only (sleep, study, exercise)": (["Study_Hours", "Physical_Activity_Hours", "Sleep_Hours_Per_Night"], []),
        "Digital use only (hours, unlocks, platform, purpose)": (["Avg_Daily_Usage_Hours", "Daily_Unlocks"], ["Most_Used_Platform", "Purpose_Of_Use"]),
        "Everything except country": (NUMERICAL_FEATURES, [c for c in CATEGORICAL_FEATURES if c != "Country"]),
        "All features": (NUMERICAL_FEATURES, CATEGORICAL_FEATURES),
    }
    fg_rows = []
    for g_name, (nums, cats) in groups_dict.items():
        row = {"Feature_Group": g_name}
        for fam, reg in [("KNN", best_reg), ("Ridge", Ridge(alpha=1.0))]:
            r = cv_rmse(make_pipeline(clone(reg), True, nums, cats), X_train[nums + cats], y_train, cv)
            row[f"{fam}_CV_RMSE"] = round(r["RMSE_mean"], 4)
            row[f"{fam}_CV_R2"] = round(r["R2_mean"], 4)
        fg_rows.append(row)
        print(f"   {g_name:52s} KNN={row['KNN_CV_RMSE']:.3f}  Ridge={row['Ridge_CV_RMSE']:.3f}")
    pd.DataFrame(fg_rows).to_csv("reports/feature_group_ablation.csv", index=False)

    # ---- 7. Error analysis on the test predictions -------------------------
    print("\n7. Error analysis ...")
    err = X_test.copy()
    err["actual"] = y_test.values
    err["pred"] = preds[best_name]
    err["residual"] = err["actual"] - err["pred"]
    err["band"] = score_band(err["actual"])
    top_countries = df["Country"].value_counts().head(6).index
    err["country_group"] = err["Country"].where(err["Country"].isin(top_countries), "Smaller countries")
    subgroups = (subgroup_table(err, "Gender") + subgroup_table(err, "Academic_Level")
                 + subgroup_table(err, "country_group") + subgroup_table(err, "band", min_n=1))
    pd.DataFrame(subgroups).to_csv("reports/subgroup_errors.csv", index=False)

    worst = err.reindex(err["residual"].abs().sort_values(ascending=False).index).head(8)
    worst.drop(columns=["band"]).to_csv("reports/worst_errors.csv", index=False)

    perm = permutation_importance(best_model, X_test, y_test, n_repeats=10, random_state=SEED,
                                  scoring="neg_root_mean_squared_error", n_jobs=-1)
    perm_df = pd.DataFrame({"Feature": FEATURES,
                            "RMSE_Increase": perm.importances_mean,
                            "Std": perm.importances_std}).sort_values("RMSE_Increase", ascending=False)
    perm_df.round(4).to_csv("reports/permutation_importance.csv", index=False)

    # ---- 8. Persist predictions & metadata ---------------------------------
    test_eval_df = X_test.copy()
    test_eval_df["Actual_Mental_Health_Score"] = y_test.values
    for n in configs:
        test_eval_df[f"Pred_{n}"] = preds[n]
    test_eval_df.to_csv("reports/test_predictions.csv", index=False)

    best_row = results_df[results_df["Model"] == best_name].iloc[0]
    metadata = {
        "best_model_name": best_name,
        "selection_rule": "lowest mean 5-fold CV RMSE on the training set",
        "best_params": params[best_name],
        "cv_rmse": float(best_row["CV_RMSE"]),
        "test_rmse": float(best_row["Test_RMSE"]),
        "test_mae": float(best_row["Test_MAE"]),
        "test_r2": float(best_row["Test_R2"]),
        "threshold_25th": round(threshold_25th, 2),
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "excluded_features": [LEAKAGE_COLUMN],
        "target_column": TARGET_COLUMN,
        "sample_size": int(len(df)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "random_seed": SEED,
        "data_quality": data_quality,
    }
    with open("models/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)
    print("Saved models/best_model.joblib, models/model_metadata.json and reports/*.csv")
    return {"results_df": results_df, "best_model_name": best_name, "metadata": metadata}


if __name__ == "__main__":
    train_and_compare_models()
