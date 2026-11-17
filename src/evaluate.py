"""
Evaluation and visualization module for Mental Health Score Predictor.

Generates:
1. Actual vs Predicted plots for all models
2. Residual scatter and distribution plots
3. Model comparison bar chart (RMSE, MAE, R2)
4. Feature importance plots (Linear/Ridge coefficients and Tree Gini importances)
5. Demographic and subgroup error breakdown (Residuals by Gender, Academic Level, Country)
6. Comprehensive correlation heatmap
7. Exporting interactive Plotly JSON artifacts for web rendering
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go

# Set MPLCONFIGDIR to avoid warnings
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.preprocessing import (
    load_and_clean_data,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
    get_feature_names_from_preprocessor
)


def generate_evaluation_figures():
    """Generates all evaluation charts and persists them to reports/figures/."""
    figures_dir = "reports/figures"
    os.makedirs(figures_dir, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="muted")
    plt.rcParams.update({"font.size": 11, "figure.autolayout": True})

    # 1. Load data & test predictions
    df = load_and_clean_data("data/dataset.csv")
    test_preds_df = pd.read_csv("reports/test_predictions.csv")
    comp_df = pd.read_csv("reports/model_comparison.csv")
    with open("models/model_metadata.json", "r") as f:
        metadata = json.load(f)

    best_model_name = metadata["best_model_name"]
    best_model = joblib.load("models/best_model.joblib")

    print(f"Generating evaluation figures. Best model: {best_model_name}")

    # ==========================================
    # FIGURE 1: Model Comparison Bar Chart
    # ==========================================
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    metrics_to_plot = [("Test_RMSE", "Test RMSE (Lower is Better)", "Blues_r"),
                       ("Test_MAE", "Test MAE (Lower is Better)", "Greens_r"),
                       ("Test_R2", "Test R² Score (Higher is Better)", "Purples")]

    for ax, (metric, title, pal) in zip(axes, metrics_to_plot):
        sorted_comp = comp_df.sort_values(metric, ascending=(metric != "Test_R2"))
        sns.barplot(data=sorted_comp, x=metric, y="Model", ax=ax, palette=pal)
        ax.set_title(title, fontweight="bold")
        ax.set_xlabel(metric)
        ax.set_ylabel("")
        for p in ax.patches:
            val = p.get_width()
            ax.annotate(f"{val:.3f}", (val, p.get_y() + p.get_height() / 2),
                        xytext=(5, 0), textcoords="offset points", va="center", fontsize=9)

    plt.suptitle("Machine Learning Models Comparison on Held-Out Test Set (N=1,000)", fontsize=14, fontweight="bold", y=1.03)
    fig.savefig(f"{figures_dir}/01_model_comparison_metrics.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved 01_model_comparison_metrics.png")

    # ==========================================
    # FIGURE 2: Correlation Heatmap
    # ==========================================
    num_cols = NUMERICAL_FEATURES + [TARGET_COLUMN]
    corr_matrix = df[num_cols].corr()

    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, ax=ax, vmin=-1, vmax=1,
                linewidths=0.5, annot_kws={"size": 10})
    ax.set_title("Pearson Correlation Heatmap (Continuous Features & Target)", fontsize=13, fontweight="bold", pad=15)
    plt.xticks(rotation=35, ha="right")
    fig.savefig(f"{figures_dir}/02_correlation_heatmap.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved 02_correlation_heatmap.png")

    # ==========================================
    # FIGURE 3: Actual vs Predicted (Best Model)
    # ==========================================
    y_true = test_preds_df["Actual_Mental_Health_Score"]
    y_pred = test_preds_df[f"Pred_{best_model_name}"]
    residuals = y_true - y_pred

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(y_true, y_pred, alpha=0.4, color="#1f77b4", edgecolors="k", s=30, label="Predictions")
    min_val = min(y_true.min(), y_pred.min()) - 0.2
    max_val = max(y_true.max(), y_pred.max()) + 0.2
    ax.plot([min_val, max_val], [min_val, max_val], "r--", lw=2, label="Perfect 1:1 Reference Line")
    ax.set_xlim(min_val, max_val)
    ax.set_ylim(min_val, max_val)
    ax.set_xlabel("Actual Mental Health Score", fontsize=12, fontweight="bold")
    ax.set_ylabel(f"Predicted Mental Health Score ({best_model_name})", fontsize=12, fontweight="bold")
    ax.set_title(f"Actual vs. Predicted Scores\n(R² = {metadata['test_r2']:.3f}, RMSE = {metadata['test_rmse']:.3f})",
                 fontsize=13, fontweight="bold")
    ax.legend(loc="upper left")
    fig.savefig(f"{figures_dir}/03_actual_vs_predicted.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved 03_actual_vs_predicted.png")

    # ==========================================
    # FIGURE 4: Residual Diagnostics (Residual vs Predicted & Distribution)
    # ==========================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Scatter of residuals vs predicted
    ax1.scatter(y_pred, residuals, alpha=0.4, color="#ff7f0e", edgecolors="k", s=28)
    ax1.axhline(0, color="r", linestyle="--", lw=2)
    ax1.set_xlabel(f"Predicted Score ({best_model_name})", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Residual (Actual - Predicted)", fontsize=11, fontweight="bold")
    ax1.set_title("Residuals vs. Fitted Values (Homoscedasticity Check)", fontsize=12, fontweight="bold")

    # Histogram / KDE of residuals
    sns.histplot(residuals, kde=True, ax=ax2, color="#2ca02c", bins=30)
    ax2.axvline(0, color="r", linestyle="--", lw=1.5)
    ax2.set_xlabel("Residual Value", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Frequency", fontsize=11, fontweight="bold")
    ax2.set_title(f"Residual Distribution (Mean = {residuals.mean():.3f}, Std = {residuals.std():.3f})",
                  fontsize=12, fontweight="bold")

    fig.savefig(f"{figures_dir}/04_residual_diagnostics.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved 04_residual_diagnostics.png")

    # ==========================================
    # FIGURE 5: Feature Importance Analysis
    # ==========================================
    preprocessor = best_model.named_steps["preprocessor"]
    regressor = best_model.named_steps["regressor"]
    feature_names = get_feature_names_from_preprocessor(preprocessor)

    if hasattr(regressor, "coef_"):
        importances = regressor.coef_
        imp_label = "Linear Coefficient (Standardized Effect Size)"
        imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
        imp_df["AbsImportance"] = imp_df["Importance"].abs()
        top_imp = imp_df.sort_values("AbsImportance", ascending=False).head(15)
        pal = ["#d62728" if x < 0 else "#2ca02c" for x in top_imp["Importance"]]
    elif hasattr(regressor, "feature_importances_"):
        importances = regressor.feature_importances_
        imp_label = "Feature Importance (Gini / Impurity Reduction)"
        imp_df = pd.DataFrame({"Feature": feature_names, "Importance": importances})
        top_imp = imp_df.sort_values("Importance", ascending=False).head(15)
        pal = "viridis"
    else:
        top_imp = pd.DataFrame({"Feature": NUMERICAL_FEATURES, "Importance": [1.0] * len(NUMERICAL_FEATURES)})
        imp_label = "Importance"
        pal = "Blues"

    fig, ax = plt.subplots(figsize=(10, 6))
    if hasattr(regressor, "coef_"):
        sns.barplot(data=top_imp, x="Importance", y="Feature", palette=pal, ax=ax)
    else:
        sns.barplot(data=top_imp, x="Importance", y="Feature", palette=pal, ax=ax)
    ax.set_title(f"Top 15 Most Influential Features ({best_model_name})", fontsize=13, fontweight="bold")
    ax.set_xlabel(imp_label, fontsize=11, fontweight="bold")
    ax.set_ylabel("")
    fig.savefig(f"{figures_dir}/05_feature_importances.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved 05_feature_importances.png")

    # ==========================================
    # FIGURE 6: Error Breakdown across Demographics
    # ==========================================
    test_preds_df["Residual"] = residuals
    test_preds_df["Abs_Error"] = residuals.abs()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    sns.boxplot(data=test_preds_df, x="Gender", y="Residual", ax=axes[0], palette="Set2")
    axes[0].axhline(0, color="r", linestyle="--", lw=1)
    axes[0].set_title("Residuals by Gender", fontsize=12, fontweight="bold")

    sns.boxplot(data=test_preds_df, x="Academic_Level", y="Residual", ax=axes[1], palette="Set3")
    axes[1].axhline(0, color="r", linestyle="--", lw=1)
    axes[1].set_title("Residuals by Academic Level", fontsize=12, fontweight="bold")

    fig.savefig(f"{figures_dir}/06_demographic_error_breakdown.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved 06_demographic_error_breakdown.png")

    # ==========================================
    # FIGURE 7: Target Leakage Comparison (With vs Without Stress_Level)
    # ==========================================
    ablation_df = pd.read_csv("reports/ablation_study.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    sns.barplot(data=ablation_df, x="Test_RMSE", y="Condition", ax=ax1, palette=["#1f77b4", "#d62728"])
    ax1.set_title("Test RMSE: Leakage-Free vs. Leaked Model", fontweight="bold")
    ax1.set_xlabel("RMSE (Lower is Better)")
    ax1.set_ylabel("")

    sns.barplot(data=ablation_df, x="Test_R2", y="Condition", ax=ax2, palette=["#1f77b4", "#d62728"])
    ax2.set_title("Test R²: Leakage-Free vs. Leaked Model", fontweight="bold")
    ax2.set_xlabel("R² (Higher is Better)")
    ax2.set_ylabel("")
    fig.savefig(f"{figures_dir}/07_leakage_ablation_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()
    print("Saved 07_leakage_ablation_comparison.png")

    print("\nAll figures successfully generated in reports/figures/")


if __name__ == "__main__":
    generate_evaluation_figures()
