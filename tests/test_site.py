"""
Integrity tests for the evaluation protocol and the static website data.
"""
import json
import os

import joblib
import numpy as np
import pandas as pd
import pytest

from src.preprocessing import load_and_clean_data, split_data


def load_site_data():
    with open("docs/data.js", encoding="utf-8") as f:
        text = f.read()
    start = text.index("window.SITE_DATA = ") + len("window.SITE_DATA = ")
    return json.loads(text[start:].rstrip().rstrip(";"))


def test_model_selected_by_cv_not_test():
    comp = pd.read_csv("reports/model_comparison.csv")
    meta = json.load(open("models/model_metadata.json"))
    assert comp.loc[comp["CV_RMSE"].idxmin(), "Model"] == meta["best_model_name"]


def test_selected_model_beats_baselines_on_test():
    comp = pd.read_csv("reports/model_comparison.csv").set_index("Model")
    meta = json.load(open("models/model_metadata.json"))
    best = comp.loc[meta["best_model_name"]]
    for baseline in ["Baseline: Mean (Dummy)", "Linear Regression"]:
        assert best["Test_RMSE"] < comp.loc[baseline, "Test_RMSE"]
        # paired bootstrap CI of the gap must exclude zero
        assert comp.loc[baseline, "Delta_CI_Low"] > 0


def test_site_data_matches_reports():
    site = load_site_data()
    comp = pd.read_csv("reports/model_comparison.csv")
    site_models = {m["Model"]: m for m in site["models"]}
    for _, row in comp.iterrows():
        assert site_models[row["Model"]]["Test_RMSE"] == pytest.approx(row["Test_RMSE"])
        assert site_models[row["Model"]]["CV_RMSE"] == pytest.approx(row["CV_RMSE"])


def test_site_knn_reproduces_saved_model():
    """Re-implement the browser KNN in numpy and check it matches the joblib model."""
    site = load_site_data()
    k = site["knn"]
    model = joblib.load("models/best_model.joblib")
    df = load_and_clean_data("data/dataset.csv")
    _, X_test, _, _ = split_data(df)
    X = X_test.head(50)

    train_num = np.array(k["train_num"])
    train_cat = np.array(k["train_cat"])
    mean, scale = np.array(k["mean"]), np.array(k["scale"])
    zt = (train_num - mean) / scale
    y = np.array(k["train_y"])
    preds = []
    for _, r in X.iterrows():
        z = (r[k["num_features"]].astype(float).values - mean) / scale
        ci = np.array([k["categories"][c].index(r[c]) for c in k["cat_features"]])
        d = np.sqrt(((zt - z) ** 2).sum(1) + 2 * (train_cat != ci).sum(1))
        idx = np.argsort(d, kind="stable")[: k["k"]]
        if (d[idx] == 0).any():
            preds.append(y[idx][d[idx] == 0].mean())
        else:
            w = 1 / d[idx]
            preds.append((w * y[idx]).sum() / w.sum())
    np.testing.assert_allclose(preds, model.predict(X), atol=0.01)


def test_ablations_do_not_use_test_set_columns():
    abl = pd.read_csv("reports/ablation_study.csv")
    fg = pd.read_csv("reports/feature_group_ablation.csv")
    assert "CV_RMSE" in abl.columns and "Test_RMSE" not in abl.columns
    assert "KNN_CV_RMSE" in fg.columns

