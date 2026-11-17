"""
Unit tests for data preprocessing module.
"""
import pytest
import os
import pandas as pd
import numpy as np

from src.preprocessing import (
    load_and_clean_data,
    split_data,
    get_preprocessor,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
    LEAKAGE_COLUMN
)


class TestPreprocessing:

    def test_load_and_clean_data(self):
        csv_path = "data/dataset.csv"
        if not os.path.exists(csv_path):
            pytest.skip("Dataset file not found")

        df = load_and_clean_data(csv_path)

        # Check shape
        assert len(df) == 4998  # Exactly 5000 - 2 duplicate rows
        assert df.duplicated().sum() == 0

        # Check clipping of physical activity
        assert (df["Physical_Activity_Hours"] < 0).sum() == 0
        assert df["Physical_Activity_Hours"].min() >= 0.0

        # Check target column
        assert TARGET_COLUMN in df.columns
        assert not df[TARGET_COLUMN].isnull().any()

    def test_split_proportions_and_reproducibility(self):
        csv_path = "data/dataset.csv"
        if not os.path.exists(csv_path):
            pytest.skip("Dataset file not found")

        df = load_and_clean_data(csv_path)
        X_train, X_test, y_train, y_test = split_data(df, test_size=0.2, random_state=42)

        assert len(X_train) == 3998
        assert len(X_test) == 1000
        assert len(y_train) == 3998
        assert len(y_test) == 1000

        # Verify no target leakage feature present in X
        assert LEAKAGE_COLUMN not in X_train.columns
        assert LEAKAGE_COLUMN not in X_test.columns

    def test_preprocessor_pipeline(self):
        preprocessor = get_preprocessor(scale_numerical=True)
        assert preprocessor is not None

        # Create dummy sample
        dummy_df = pd.DataFrame([{
            "Age": 21,
            "Avg_Daily_Usage_Hours": 4.5,
            "Daily_Unlocks": 150,
            "Study_Hours": 4.0,
            "Physical_Activity_Hours": 1.5,
            "Sleep_Hours_Per_Night": 7.5,
            "Gender": "Male",
            "Country": "India",
            "Academic_Level": "Undergraduate",
            "Most_Used_Platform": "Instagram",
            "Purpose_Of_Use": "Entertainment"
        }])

        transformed = preprocessor.fit_transform(dummy_df)
        assert transformed.shape[0] == 1
        assert transformed.shape[1] > len(NUMERICAL_FEATURES)
