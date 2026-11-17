"""
Data preprocessing module for Mental Health Score Predictor.

Handles:
- Loading raw dataset
- Handling duplicates and negative anomalies (clipping Physical_Activity_Hours to 0)
- Feature categorization: numerical vs. categorical
- Target leakage prevention: explicitly excluding Stress_Level from primary features
- Building reusable scikit-learn ColumnTransformer pipelines
- Train/test split with reproducibility (80/20)
"""
import os
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any, Optional
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline


# Features used for the primary regression model (excluding Stress_Level to avoid leakage)
NUMERICAL_FEATURES: List[str] = [
    "Age",
    "Avg_Daily_Usage_Hours",
    "Daily_Unlocks",
    "Study_Hours",
    "Physical_Activity_Hours",
    "Sleep_Hours_Per_Night"
]

CATEGORICAL_FEATURES: List[str] = [
    "Gender",
    "Country",
    "Academic_Level",
    "Most_Used_Platform",
    "Purpose_Of_Use"
]

TARGET_COLUMN: str = "Mental_Health_Score"
LEAKAGE_COLUMN: str = "Stress_Level"


def load_and_clean_data(csv_path: str = "data/dataset.csv") -> pd.DataFrame:
    """
    Loads dataset from CSV and applies foundational cleaning:
    1. Removes exact duplicate rows.
    2. Clips negative Physical_Activity_Hours to 0.0 (artifact of survey/synthetic generation).
    3. Validates required columns.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    df = pd.read_csv(csv_path)

    # 1. Deduplication
    initial_len = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    dropped_duplicates = initial_len - len(df)

    # 2. Anomaly correction: Physical activity cannot be negative in physical time
    neg_physical = (df["Physical_Activity_Hours"] < 0).sum()
    if neg_physical > 0:
        df["Physical_Activity_Hours"] = df["Physical_Activity_Hours"].clip(lower=0.0)

    # 3. Validation
    required_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN, LEAKAGE_COLUMN]
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in dataset: {missing_cols}")

    return df


def get_preprocessor(scale_numerical: bool = True) -> ColumnTransformer:
    """
    Constructs a ColumnTransformer for preprocessing.
    
    Args:
        scale_numerical: If True, applies StandardScaler to numerical features.
                         If False, passes numerical features through untouched (useful for Tree-based models).
    """
    if scale_numerical:
        num_transformer = Pipeline(steps=[
            ("scaler", StandardScaler())
        ])
    else:
        num_transformer = "passthrough"

    cat_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_transformer, NUMERICAL_FEATURES),
            ("cat", cat_transformer, CATEGORICAL_FEATURES)
        ],
        remainder="drop"
    )
    return preprocessor


def split_data(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Splits the cleaned dataset into training and testing sets (80/20 split).
    The test set is held out and only evaluated once per candidate model.
    """
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state
    )
    return X_train, X_test, y_train, y_test


def get_feature_names_from_preprocessor(preprocessor: ColumnTransformer) -> List[str]:
    """
    Retrieves human-readable transformed feature names from a fitted ColumnTransformer.
    """
    feature_names = []
    # Numerical names
    feature_names.extend(NUMERICAL_FEATURES)
    # Categorical one-hot names
    cat_encoder = preprocessor.named_transformers_["cat"].named_steps["onehot"]
    cat_names = cat_encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    feature_names.extend(cat_names)
    return feature_names
