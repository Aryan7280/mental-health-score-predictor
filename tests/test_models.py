"""
Unit tests for model persistence, loading, and inference.
"""
import pytest
import os
import json
import joblib
import pandas as pd
import numpy as np


class TestModelArtifacts:

    def test_model_and_metadata_exist(self):
        assert os.path.exists("models/best_model.joblib"), "best_model.joblib missing"
        assert os.path.exists("models/model_metadata.json"), "model_metadata.json missing"
        assert os.path.exists("reports/model_comparison.csv"), "model_comparison.csv missing"

    def test_metadata_fields(self):
        with open("models/model_metadata.json") as f:
            meta = json.load(f)

        assert "best_model_name" in meta
        assert "test_rmse" in meta
        assert "test_r2" in meta
        assert "threshold_25th" in meta
        assert meta["threshold_25th"] == 5.10
        assert meta["test_r2"] > 0.85, "Expected best model R2 > 0.85"
        assert meta["test_rmse"] < 0.50, "Expected best model RMSE < 0.50"

    def test_model_inference_pipeline(self):
        model = joblib.load("models/best_model.joblib")

        sample_input = pd.DataFrame([{
            "Age": 22,
            "Gender": "Female",
            "Country": "USA",
            "Academic_Level": "Undergraduate",
            "Most_Used_Platform": "YouTube",
            "Purpose_Of_Use": "Education",
            "Avg_Daily_Usage_Hours": 3.5,
            "Daily_Unlocks": 110,
            "Study_Hours": 5.0,
            "Physical_Activity_Hours": 2.0,
            "Sleep_Hours_Per_Night": 8.0
        }])

        pred = model.predict(sample_input)
        assert len(pred) == 1
        score = float(pred[0])
        assert isinstance(score, float)
        assert 1.0 <= score <= 10.0, f"Predicted score {score} out of scale [1, 10]"
