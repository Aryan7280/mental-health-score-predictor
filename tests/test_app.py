"""
Tests for Streamlit application integrity and Jupyter Notebook structure.
"""
import pytest
import os
import json
import py_compile


class TestAppAndNotebookIntegrity:

    def test_app_compiles(self):
        """Ensures app.py has zero syntax errors."""
        assert os.path.exists("app.py"), "app.py not found"
        py_compile.compile("app.py", doraise=True)

    def test_notebook_json_validity(self):
        """Ensures notebooks/Mental_Health_Score_Predictor.ipynb is valid JSON and contains required sections."""
        nb_path = "notebooks/Mental_Health_Score_Predictor.ipynb"
        assert os.path.exists(nb_path), "Notebook file not found"

        with open(nb_path, "r", encoding="utf-8") as f:
            nb = json.load(f)

        assert "cells" in nb
        assert len(nb["cells"]) >= 15, "Expected at least 15 notebook cells"

        # Check for key required sections in markdown
        md_text = " ".join(["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown"])
        assert "Shiva Singh" in md_text, "Kaggle dataset author citation missing in notebook"
        assert "kaggle.com" in md_text, "Kaggle URL missing in notebook"
        assert "Stress_Level" in md_text, "Target leakage discussion missing in notebook"
        assert "25th" in md_text or "Percentile" in md_text, "Percentile threshold discussion missing"

    def test_requirements_file(self):
        """Ensures requirements.txt exists and contains core libraries."""
        assert os.path.exists("requirements.txt"), "requirements.txt missing"
        with open("requirements.txt") as f:
            reqs = f.read()
        for pkg in ["pandas", "numpy", "scikit-learn", "streamlit", "plotly", "joblib"]:
            assert pkg in reqs, f"{pkg} missing from requirements.txt"
