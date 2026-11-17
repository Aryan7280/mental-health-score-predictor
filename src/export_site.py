"""
Export every number shown on the website (docs/) from the pipeline outputs.

Run after `python src/train.py` (and optionally `python src/evaluate.py`):

    python src/export_site.py

Writes docs/data.js, which defines `window.SITE_DATA`. Using a .js file (not
.json + fetch) means the site also works when index.html is opened directly
from disk. The file contains the fitted KNN's scaler statistics, category
lists and training rows so the browser reproduces the saved model exactly.
"""
import json
import os
import shutil
import sys

import joblib
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sklearn.linear_model import Ridge  # noqa: E402

from src.preprocessing import (  # noqa: E402
    CATEGORICAL_FEATURES, NUMERICAL_FEATURES, TARGET_COLUMN, LEAKAGE_COLUMN,
    load_and_clean_data, split_data,
)
from src.train import make_pipeline  # noqa: E402


def records(df):
    return json.loads(df.to_json(orient="records"))


def main():
    meta = json.load(open("models/model_metadata.json"))
    df = load_and_clean_data("data/dataset.csv")
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=meta["random_seed"])
    model = joblib.load("models/best_model.joblib")
    pre = model.named_steps["preprocessor"]
    reg = model.named_steps["regressor"]

    scaler = pre.named_transformers_["num"]
    ohe = pre.named_transformers_["cat"]
    if hasattr(scaler, "named_steps"):
        scaler = scaler.named_steps["scaler"]
    if hasattr(ohe, "named_steps"):
        ohe = ohe.named_steps["onehot"]
    cats = {f: [str(c) for c in ohe.categories_[i]] for i, f in enumerate(CATEGORICAL_FEATURES)}

    # Compact training set: numeric values + category indices
    train_num = X_train[NUMERICAL_FEATURES].round(3).values.tolist()
    train_cat = [[cats[f].index(str(v)) for f, v in zip(CATEGORICAL_FEATURES, row)]
                 for row in X_train[CATEGORICAL_FEATURES].values]

    # Linear reference model (same split) for side-by-side predictions
    ridge = make_pipeline(Ridge(alpha=0.1)).fit(X_train, y_train)
    r_pre = ridge.named_steps["preprocessor"]
    r_scaler = r_pre.named_transformers_["num"]
    r_ohe = r_pre.named_transformers_["cat"]
    r_coef = ridge.named_steps["regressor"].coef_
    n_num = len(NUMERICAL_FEATURES)
    ridge_cat = {}
    pos = n_num
    for i, f in enumerate(CATEGORICAL_FEATURES):
        k = len(r_ohe.categories_[i])
        ridge_cat[f] = {str(c): float(w) for c, w in zip(r_ohe.categories_[i], r_coef[pos:pos + k])}
        pos += k

    # EDA summaries
    hist_counts, hist_edges = np.histogram(df[TARGET_COLUMN], bins=np.arange(3.5, 10.0, 0.5))
    numeric_summary = []
    for c in NUMERICAL_FEATURES + [TARGET_COLUMN]:
        s = df[c]
        numeric_summary.append({"feature": c, "min": float(s.min()), "mean": round(float(s.mean()), 2),
                                "max": float(s.max()), "std": round(float(s.std()), 2),
                                "r_with_target": round(float(s.corr(df[TARGET_COLUMN])), 3)})
    stress = (df.groupby(LEAKAGE_COLUMN)[TARGET_COLUMN].agg(["count", "mean"]).round(2)
              .reindex(["Low", "Medium", "High", "Very High"]).reset_index())
    platform_purpose = pd.crosstab(df["Most_Used_Platform"], df["Purpose_Of_Use"])
    deterministic_share = float(platform_purpose.max(axis=1).sum() / platform_purpose.values.sum())

    # Binned relationship of each numeric input with the target (for the feature explorer)
    feature_bins = {}
    for c in NUMERICAL_FEATURES:
        q = pd.qcut(df[c], q=10, duplicates="drop") if df[c].nunique() > 12 else df[c]
        g = df.groupby(q, observed=True).agg(x=(c, "mean"), y=(TARGET_COLUMN, "mean"),
                                             sd=(TARGET_COLUMN, "std"), n=(TARGET_COLUMN, "size"))
        feature_bins[c] = records(g.reset_index(drop=True).round(3))
    platform_means = (df.groupby("Most_Used_Platform")[TARGET_COLUMN].agg(["mean", "count"])
                      .sort_values("mean").round(3).reset_index())

    # Test predictions for scatter + sample explorer
    tp = pd.read_csv("reports/test_predictions.csv")
    best = meta["best_model_name"]
    scatter = tp[["Actual_Mental_Health_Score", f"Pred_{best}"]].round(2).values.tolist()
    sample_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + ["Actual_Mental_Health_Score"]
    samples = tp.sample(60, random_state=7)
    sample_rows = []
    for _, r in samples.iterrows():
        row = {c: (r[c] if c in CATEGORICAL_FEATURES else float(r[c])) for c in sample_cols}
        row["pred_best"] = round(float(r[f"Pred_{best}"]), 3)
        row["pred_rf"] = round(float(r["Pred_Random Forest"]), 3)
        row["pred_linear"] = round(float(r["Pred_Linear Regression"]), 3)
        row["pred_dummy"] = round(float(r["Pred_Baseline: Mean (Dummy)"]), 3)
        sample_rows.append(row)

    data = {
        "meta": meta,
        "eda": {
            "target_hist": {"edges": hist_edges.round(2).tolist(), "counts": hist_counts.tolist()},
            "numeric_summary": numeric_summary,
            "stress_vs_target": records(stress),
            "platform_counts": df["Most_Used_Platform"].value_counts().to_dict(),
            "top_countries": df["Country"].value_counts().head(8).to_dict(),
            "platform_purpose_determinism": round(deterministic_share, 3),
            "feature_bins": feature_bins,
            "platform_means": records(platform_means),
            "usage_unlocks_r": round(float(df["Avg_Daily_Usage_Hours"].corr(df["Daily_Unlocks"])), 3),
        },
        "models": records(pd.read_csv("reports/model_comparison.csv")),
        "country": records(pd.read_csv("reports/country_generalization.csv")),
        "stress_ablation": records(pd.read_csv("reports/ablation_study.csv")),
        "feature_groups": records(pd.read_csv("reports/feature_group_ablation.csv")),
        "subgroups": records(pd.read_csv("reports/subgroup_errors.csv")),
        "worst": records(pd.read_csv("reports/worst_errors.csv").round(3)),
        "permutation": records(pd.read_csv("reports/permutation_importance.csv")),
        "scatter": scatter,
        "knn_curve": records(pd.read_csv("reports/knn_validation_curve.csv")),
        "learning_curves": records(pd.read_csv("reports/learning_curves.csv")),
        "samples": sample_rows,
        "knn": {
            "k": int(reg.n_neighbors), "weights": reg.weights,
            "num_features": NUMERICAL_FEATURES, "cat_features": CATEGORICAL_FEATURES,
            "mean": scaler.mean_.round(6).tolist(), "scale": scaler.scale_.round(6).tolist(),
            "categories": cats, "train_num": train_num, "train_cat": train_cat,
            "train_y": y_train.round(2).tolist(),
        },
        "ridge": {
            "intercept": float(ridge.named_steps["regressor"].intercept_),
            "mean": r_scaler.mean_.tolist(), "scale": r_scaler.scale_.tolist(),
            "num_coef": r_coef[:n_num].tolist(), "cat_coef": ridge_cat,
        },
    }

    os.makedirs("docs", exist_ok=True)
    with open("docs/data.js", "w", encoding="utf-8") as f:
        f.write("// Generated by src/export_site.py - do not edit by hand.\n")
        f.write("window.SITE_DATA = ")
        json.dump(data, f, separators=(",", ":"))
        f.write(";\n")

    if os.path.isdir("reports/figures"):
        os.makedirs("docs/figures", exist_ok=True)
        for name in os.listdir("reports/figures"):
            shutil.copy(os.path.join("reports/figures", name), os.path.join("docs/figures", name))
    print(f"Wrote docs/data.js ({os.path.getsize('docs/data.js') / 1024:.0f} KB) and copied figures.")


if __name__ == "__main__":
    main()
