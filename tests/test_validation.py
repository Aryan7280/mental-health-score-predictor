"""
Unit tests for Strict 24-Hour Daily Activity Validation & Recommendations.
Directly implements mandatory TESTS 1 through 7 from the project specification.
"""
import pytest
import numpy as np
from src.utils import validate_daily_hours, generate_recommendations


class TestStrict24HourValidation:
    """Mandatory 24-Hour Activity Budget Tests"""

    def test_1_total_20_hours_allowed(self):
        """TEST 1: Total = 20 hours -> Prediction allowed."""
        usage = 5.0
        study = 6.0
        sleep = 7.0
        physical = 2.0
        is_valid, total, rem, msg = validate_daily_hours(usage, study, physical, sleep)

        assert is_valid is True
        assert total == 20.0
        assert rem == 4.0
        assert "Valid input" in msg

    def test_2_total_24_hours_allowed(self):
        """TEST 2: Total = 24 hours exactly -> Prediction allowed."""
        usage = 6.0
        study = 8.0
        sleep = 8.0
        physical = 2.0
        is_valid, total, rem, msg = validate_daily_hours(usage, study, physical, sleep)

        assert is_valid is True
        assert total == 24.0
        assert rem == 0.0
        assert "Valid input" in msg

    def test_3_total_25_hours_blocked(self):
        """TEST 3: Total = 25 hours -> Prediction blocked immediately."""
        usage = 8.0
        study = 8.0
        sleep = 7.0
        physical = 2.0
        is_valid, total, rem, msg = validate_daily_hours(usage, study, physical, sleep)

        assert is_valid is False
        assert total == 25.0
        assert rem == -1.0
        assert "cannot exceed 24 hours" in msg

    def test_4_negative_activity_hours_invalid(self):
        """TEST 4: Negative activity hours -> Invalid input."""
        # Test negative usage
        is_valid, _, _, msg = validate_daily_hours(-1.0, 5.0, 1.0, 8.0)
        assert is_valid is False
        assert "cannot be negative" in msg

        # Test negative sleep
        is_valid2, _, _, msg2 = validate_daily_hours(4.0, 5.0, 1.0, -2.0)
        assert is_valid2 is False
        assert "cannot be negative" in msg2

    def test_5_direct_backend_request_rejected(self):
        """TEST 5: Direct backend request with total > 24 -> Request rejected with ValueError."""
        usage = 8.0
        study = 8.0
        sleep = 8.0
        physical = 2.0  # Total = 26.0

        # Attempting to generate recommendations on invalid inputs must raise ValueError in backend
        with pytest.raises(ValueError) as excinfo:
            generate_recommendations(
                predicted_score=6.0,
                usage_hours=usage,
                study_hours=study,
                physical_hours=physical,
                sleep_hours=sleep,
                threshold=5.10
            )
        assert "Cannot generate recommendations for invalid inputs" in str(excinfo.value)
        assert "cannot exceed 24 hours" in str(excinfo.value)


class TestPersonalizedRecommendations:
    """Mandatory Recommendation Logic Tests"""

    def test_6_valid_input_low_score_recommendations(self):
        """TEST 6: Valid input with low predicted score -> Improvement suggestions displayed."""
        usage = 6.5
        study = 4.0
        sleep = 6.0
        physical = 0.5  # Total = 17.0 hrs (valid)
        predicted_score = 4.5  # Below threshold of 5.10

        rec = generate_recommendations(
            predicted_score=predicted_score,
            usage_hours=usage,
            study_hours=study,
            physical_hours=physical,
            sleep_hours=sleep,
            threshold=5.10
        )

        assert rec["is_low"] is True
        assert rec["title"] == "Suggestions to Improve Your Daily Routine"
        assert len(rec["suggestions"]) > 0

        # Must include suggestions for high screen time and low sleep
        categories = [s["category"] for s in rec["suggestions"]]
        assert any("Screen Time" in c for c in categories)
        assert any("Sleep" in c for c in categories)

        # Safety rules verification
        for s in rec["suggestions"]:
            assert "reduce sleep" not in s["action"].lower()
            assert "reduce physical activity" not in s["action"].lower()

    def test_7_valid_input_non_low_score_maintenance(self):
        """TEST 7: Valid input with non-low predicted score -> Maintenance suggestions displayed."""
        usage = 3.0
        study = 5.0
        sleep = 8.0
        physical = 1.5  # Total = 17.5 hrs (valid)
        predicted_score = 7.8  # Above threshold of 5.10

        rec = generate_recommendations(
            predicted_score=predicted_score,
            usage_hours=usage,
            study_hours=study,
            physical_hours=physical,
            sleep_hours=sleep,
            threshold=5.10
        )

        assert rec["is_low"] is False
        assert rec["title"] == "Suggestions to Maintain Your Balanced Routine"
        assert len(rec["suggestions"]) > 0
        categories = [s["category"] for s in rec["suggestions"]]
        assert any("Sleep" in c or "Routine" in c for c in categories)
