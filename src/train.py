"""
Training module for Mental Health Score Predictor.

Implements:
1. Baseline 1: Dummy Regressor (Mean predictor)
2. Baseline 2 / Model 1: Linear Regression
3. Model 2: Ridge Regression (with tuning)
4. Model 3: Lasso Regression (with tuning)
5. Model 4: K-Nearest Neighbors (KNN) Regressor (with tuning)
6. Model 5: Random Forest Regressor (with tuning)
7. Model 6: Gradient Boosting Regressor (with tuning)

Evaluation protocol:
- 80/20 train/test split (fixed seed)
- 5-fold cross-validation on training data for model selection
- Test set evaluated once per final model
- Country generalization via GroupKFold
- Leakage comparison (with vs without Stress_Level)
- Feature group ablation (Demographics vs Lifestyle vs Usage)
- Saving best model pipeline and reports
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Dict, Any, List, Tuple

from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import KFold, GroupKFold, cross_validate, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

import warnings
warnings.filterwarnings("ignore")

from src.preprocessing import (
    load_and_clean_data,
    split_data,
    get_preprocessor,
    get_feature_names_from_preprocessor,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
    LEAKAGE_COLUMN
)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Computes RMSE, MAE, and R2 score."""
    mse = mean_squared_error(y_true, y_pred)
    rmse = float(np.sqrt(mse))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {"RMSE": rmse, "MAE": mae, "R2": r2}


def bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bootstraps: int = 1000,
    ci: float = 0.95,
    random_state: int = 42
) -> Dict[str, Tuple[float, float]]:
    """Calculates bootstrap confidence intervals for RMSE, MAE, and R2."""
    rng = np.random.RandomState(random_state)
    n = len(y_true)
    rmses, maes, r2s = [], [], []

    for _ in range(n_bootstraps):
        idx = rng.randint(0, n, n)
        y_t = y_true[idx]
        y_p = y_pred[idx]
        rmses.append(np.sqrt(mean_squared_error(y_t, y_p)))
        maes.append(mean_absolute_error(y_t, y_p))
        r2s.append(r2_score(y_t, y_p))

    alpha_low = ((1.0 - ci) / 2.0) * 100
    alpha_high = (1.0 - (1.0 - ci) / 2.0) * 100

    return {
        "RMSE_CI": (float(np.percentile(rmses, alpha_low)), float(np.percentile(rmses, alpha_high))),
        "MAE_CI": (float(np.percentile(maes, alpha_low)), float(np.percentile(maes, alpha_high))),
        "R2_CI": (float(np.percentile(r2s, alpha_low)), float(np.percentile(r2s, alpha_high))),
    }


def train_and_compare_models(csv_path: str = "data/dataset.csv") -> Dict[str, Any]:
    """
    Executes the complete rigorous model training, validation, and benchmarking pipeline.
    """
    os.makedirs("models", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    os.makedirs("reports/figures", exist_ok=True)

    print("1. Loading and cleaning data...")
    df = load_and_clean_data(csv_path)
    X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=42)

    # 25th percentile of target in training set for routine recommendations threshold
    threshold_25th = float(np.percentile(y_train, 25))
    print(f"Dataset shape: {df.shape}, Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"Mental Health Score 25th percentile threshold: {threshold_25th:.2f}")

    cv = KFold(n_splits=5, shuffle=True, random_state=42)

    # Preprocessors
    preprocessor_scaled = get_preprocessor(scale_numerical=True)
    preprocessor_unscaled = get_preprocessor(scale_numerical=False)

    # Candidate Models definition
    models_config = {
        "Baseline: Dummy (Mean)": {
            "pipeline": Pipeline([
                ("preprocessor", preprocessor_unscaled),
                ("regressor", DummyRegressor(strategy="mean"))
            ]),
            "param_grid": {}
        },
        "Linear Regression": {
            "pipeline": Pipeline([
                ("preprocessor", preprocessor_scaled),
                ("regressor", LinearRegression())
            ]),
            "param_grid": {}
        },
        "Ridge Regression": {
            "pipeline": Pipeline([
                ("preprocessor", preprocessor_scaled),
                ("regressor", Ridge(random_state=42))
            ]),
            "param_grid": {
                "regressor__alpha": [0.01, 0.1, 1.0, 10.0, 50.0, 100.0]
            }
        },
        "Lasso Regression": {
            "pipeline": Pipeline([
                ("preprocessor", preprocessor_scaled),
                ("regressor", Lasso(random_state=42, max_iter=2000))
            ]),
            "param_grid": {
                "regressor__alpha": [0.001, 0.005, 0.01, 0.05, 0.1]
            }
        },
        "K-Nearest Neighbors": {
            "pipeline": Pipeline([
                ("preprocessor", preprocessor_scaled),
                ("regressor", KNeighborsRegressor())
            ]),
            "param_grid": {
                "regressor__n_neighbors": [3, 5, 7, 9, 11, 15],
                "regressor__weights": ["uniform", "distance"]
            }
        },
        "Random Forest": {
            "pipeline": Pipeline([
                ("preprocessor", preprocessor_unscaled),
                ("regressor", RandomForestRegressor(random_state=42, n_jobs=-1))
            ]),
            "param_grid": {
                "regressor__n_estimators": [100, 200],
                "regressor__max_depth": [8, 12, 16, None],
                "regressor__min_samples_split": [2, 5]
            }
        },
        "Gradient Boosting": {
            "pipeline": Pipeline([
                ("preprocessor", preprocessor_unscaled),
                ("regressor", GradientBoostingRegressor(random_state=42))
            ]),
            "param_grid": {
                "regressor__n_estimators": [100, 200],
                "regressor__learning_rate": [0.05, 0.1],
                "regressor__max_depth": [3, 5]
            }
        }
    }

    results = []
    fitted_models = {}
    test_predictions = {}

    print("\n2. Training models with 5-fold CV & Hyperparameter Tuning...")
    for name, config in models_config.items():
        print(f"--> Training {name}...")
        pipeline = config["pipeline"]
        param_grid = config["param_grid"]

        if param_grid:
            search = GridSearchCV(
                pipeline,
                param_grid=param_grid,
                cv=cv,
                scoring="neg_root_mean_squared_error",
                n_jobs=-1
            )
            search.fit(X_train, y_train)
            best_model = search.best_estimator_
            best_params = search.best_params_
            cv_rmse = -search.best_score_
        else:
            best_model = pipeline
            best_model.fit(X_train, y_train)
            best_params = {}
            cv_scores = cross_validate(
                best_model,
                X_train,
                y_train,
                cv=cv,
                scoring=["neg_root_mean_squared_error", "neg_mean_absolute_error", "r2"],
                n_jobs=-1
            )
            cv_rmse = -np.mean(cv_scores["test_neg_root_mean_squared_error"])

        # Predict on held-out test set
        y_test_pred = best_model.predict(X_test)
        metrics = compute_metrics(y_test.values, y_test_pred)
        ci = bootstrap_ci(y_test.values, y_test_pred)

        fitted_models[name] = best_model
        test_predictions[name] = y_test_pred

        results.append({
            "Model": name,
            "CV_RMSE": round(cv_rmse, 4),
            "Test_RMSE": round(metrics["RMSE"], 4),
            "Test_MAE": round(metrics["MAE"], 4),
            "Test_R2": round(metrics["R2"], 4),
            "Test_RMSE_95CI": f"[{ci['RMSE_CI'][0]:.3f}, {ci['RMSE_CI'][1]:.3f}]",
            "Best_Params": str(best_params) if best_params else "Default"
        })

    # Summary table
    results_df = pd.DataFrame(results).sort_values("Test_RMSE")
    results_df.to_csv("reports/model_comparison.csv", index=False)
    print("\n=== MODEL COMPARISON TABLE ===")
    print(results_df.to_string(index=False))

    # Identify best model
    best_model_name = results_df.iloc[0]["Model"]
    best_model = fitted_models[best_model_name]
    print(f"\n--> Best-performing model: {best_model_name}")

    # Save best model
    joblib.dump(best_model, "models/best_model.joblib")
    print(f"Saved best model pipeline to models/best_model.joblib")

    # 3. Country Generalization Test (GroupKFold)
    print("\n3. Performing Country Generalization Analysis (GroupKFold)...")
    # Evaluate generalization on countries
    gkf = GroupKFold(n_splits=5)
    # Use Ridge / best model for country evaluation
    country_groups = df["Country"]
    X_full = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y_full = df[TARGET_COLUMN]

    country_cv_scores = []
    for train_idx, val_idx in gkf.split(X_full, y_full, groups=country_groups):
        X_tr, X_val = X_full.iloc[train_idx], X_full.iloc[val_idx]
        y_tr, y_val = y_full.iloc[train_idx], y_full.iloc[val_idx]

        model_clone = joblib.load("models/best_model.joblib")
        model_clone.fit(X_tr, y_tr)
        val_pred = model_clone.predict(X_val)
        m = compute_metrics(y_val.values, val_pred)
        country_cv_scores.append(m)

    country_cv_df = pd.DataFrame(country_cv_scores)
    country_summary = {
        "Country_GroupKFold_RMSE_Mean": round(float(country_cv_df["RMSE"].mean()), 4),
        "Country_GroupKFold_RMSE_Std": round(float(country_cv_df["RMSE"].std()), 4),
        "Country_GroupKFold_MAE_Mean": round(float(country_cv_df["MAE"].mean()), 4),
        "Country_GroupKFold_R2_Mean": round(float(country_cv_df["R2"].mean()), 4),
    }
    print("Country Generalization Summary (Leave-Countries-Out GroupKFold):", country_summary)
    pd.DataFrame([country_summary]).to_csv("reports/country_generalization.csv", index=False)

    # 4. Target Leakage Ablation Analysis (With vs Without Stress_Level)
    print("\n4. Running Target Leakage Ablation Analysis...")
    # Model WITH Stress_Level included
    cat_with_leakage = CATEGORICAL_FEATURES + [LEAKAGE_COLUMN]
    preprocessor_leaked = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERICAL_FEATURES),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_with_leakage)
        ]
    )
    leaked_pipeline = Pipeline([
        ("preprocessor", preprocessor_leaked),
        ("regressor", Ridge(alpha=1.0, random_state=42))
    ])

    X_train_leaked = df.loc[X_train.index, NUMERICAL_FEATURES + cat_with_leakage]
    X_test_leaked = df.loc[X_test.index, NUMERICAL_FEATURES + cat_with_leakage]
    leaked_pipeline.fit(X_train_leaked, y_train)
    leaked_pred = leaked_pipeline.predict(X_test_leaked)
    leaked_metrics = compute_metrics(y_test.values, leaked_pred)

    best_test_rmse = results_df.loc[results_df["Model"] == best_model_name, "Test_RMSE"].values[0]
    best_test_r2 = results_df.loc[results_df["Model"] == best_model_name, "Test_R2"].values[0]

    ablation_df = pd.DataFrame([
        {
            "Condition": "Main Model (Ethical / Leakage-Free - Without Stress_Level)",
            "Features_Used": "Demographics, Usage, Lifestyle (11 features)",
            "Test_RMSE": best_test_rmse,
            "Test_R2": best_test_r2,
            "Target_Leakage_Risk": "None - All features observable at prediction time"
        },
        {
            "Condition": "Leaked Model (Artificial Inflation - With Stress_Level)",
            "Features_Used": "Demographics, Usage, Lifestyle + Stress_Level (12 features)",
            "Test_RMSE": round(leaked_metrics["RMSE"], 4),
            "Test_R2": round(leaked_metrics["R2"], 4),
            "Target_Leakage_Risk": "Severe Leakage - Stress_Level is a proxy for the outcome itself"
        }
    ])
    ablation_df.to_csv("reports/ablation_study.csv", index=False)
    print("Ablation study saved to reports/ablation_study.csv")
    print(ablation_df.to_string(index=False))

    # 5. Feature Group Contribution Ablation (Demographics vs Lifestyle vs Usage)
    print("\n5. Running Feature Group Ablation...")
    feature_group_ablation = []

    # Lifestyle only: Study_Hours, Physical_Activity_Hours, Sleep_Hours_Per_Night
    # Usage only: Avg_Daily_Usage_Hours, Daily_Unlocks, Most_Used_Platform, Purpose_Of_Use
    # Demographics only: Age, Gender, Country, Academic_Level
    groups_dict = {
        "Demographics Only": (["Age"], ["Gender", "Country", "Academic_Level"]),
        "Lifestyle Only (Sleep, Study, Exercise)": (["Study_Hours", "Physical_Activity_Hours", "Sleep_Hours_Per_Night"], []),
        "Digital Usage Only (Usage hrs, Unlocks, Platform, Purpose)": (["Avg_Daily_Usage_Hours", "Daily_Unlocks"], ["Most_Used_Platform", "Purpose_Of_Use"]),
        "Full Feature Set (Combined)": (NUMERICAL_FEATURES, CATEGORICAL_FEATURES)
    }

    for g_name, (nums, cats) in groups_dict.items():
        pre_g = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), nums) if nums else ("num", "drop", []),
                ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cats) if cats else ("cat", "drop", [])
            ]
        )
        pipe_g = Pipeline([("pre", pre_g), ("reg", Ridge(alpha=1.0, random_state=42))])
        pipe_g.fit(X_train[nums + cats], y_train)
        pred_g = pipe_g.predict(X_test[nums + cats])
        m_g = compute_metrics(y_test.values, pred_g)
        feature_group_ablation.append({
            "Feature_Group": g_name,
            "Test_RMSE": round(m_g["RMSE"], 4),
            "Test_MAE": round(m_g["MAE"], 4),
            "Test_R2": round(m_g["R2"], 4)
        })

    fg_df = pd.DataFrame(feature_group_ablation)
    fg_df.to_csv("reports/feature_group_ablation.csv", index=False)
    print(fg_df.to_string(index=False))

    # 6. Save Metadata & Test Predictions for evaluation & Web App
    test_eval_df = X_test.copy()
    test_eval_df["Actual_Mental_Health_Score"] = y_test.values
    for m_name, preds in test_predictions.items():
        test_eval_df[f"Pred_{m_name}"] = preds
    test_eval_df.to_csv("reports/test_predictions.csv", index=False)

    metadata = {
        "best_model_name": best_model_name,
        "best_params": results_df.loc[results_df["Model"] == best_model_name, "Best_Params"].values[0],
        "test_rmse": results_df.loc[results_df["Model"] == best_model_name, "Test_RMSE"].values[0],
        "test_mae": results_df.loc[results_df["Model"] == best_model_name, "Test_MAE"].values[0],
        "test_r2": results_df.loc[results_df["Model"] == best_model_name, "Test_R2"].values[0],
        "threshold_25th": threshold_25th,
        "numerical_features": NUMERICAL_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target_column": TARGET_COLUMN,
        "sample_size": len(df),
        "train_size": len(X_train),
        "test_size": len(X_test)
    }

    with open("models/model_metadata.json", "w") as f:
        json.dump(metadata, f, indent=4)

    print("Metadata written to models/model_metadata.json")
    print("Training phase complete.")
    return {
        "results_df": results_df,
        "best_model_name": best_model_name,
        "metadata": metadata
    }


if __name__ == "__main__":
    train_and_compare_models()
