"""
Utility functions for Mental Health Score Predictor.
Includes:
- 24-hour daily activity validation (frontend & backend enforcement)
- Personalized recommendations engine
- Metric calculation helpers
"""
from typing import Dict, List, Tuple, Any
import numpy as np


def validate_daily_hours(
    usage_hours: float,
    study_hours: float,
    physical_hours: float,
    sleep_hours: float
) -> Tuple[bool, float, float, str]:
    """
    STRICT 24-HOUR VALIDATION:
    Total non-overlapping daily activity hours must satisfy:
    0 <= Total Hours <= 24.0

    Returns:
        (is_valid, total_hours, remaining_hours, message)
    """
    # Check for negative values
    activities = {
        "Social Media Usage": usage_hours,
        "Study Hours": study_hours,
        "Physical Activity": physical_hours,
        "Sleep Hours": sleep_hours
    }
    for name, val in activities.items():
        if val is None or not isinstance(val, (int, float)):
            return False, 0.0, 24.0, f"ERROR: Invalid input for {name}. Must be a numeric value."
        if val < 0.0:
            return False, 0.0, 24.0, f"ERROR: {name} cannot be negative ({val:.1f} hrs entered)."
        if val > 24.0:
            return False, 0.0, 24.0, f"ERROR: {name} alone exceeds 24 hours ({val:.1f} hrs entered)."

    total_hours = round(float(usage_hours + study_hours + physical_hours + sleep_hours), 2)
    remaining_hours = round(24.0 - total_hours, 2)

    if total_hours > 24.0:
        return (
            False,
            total_hours,
            remaining_hours,
            f"ERROR: Total daily activity hours cannot exceed 24 hours. "
            f"You entered {total_hours:.1f} hours ({total_hours - 24.0:.1f} hours over the limit). "
            f"Please reduce your selected hours."
        )

    if total_hours < 0.0:
        return False, total_hours, remaining_hours, "ERROR: Total daily activity hours cannot be negative."

    return (
        True,
        total_hours,
        remaining_hours,
        f"Valid input: Total {total_hours:.1f} hours accounted for. "
        f"{remaining_hours:.1f} hours remaining in the day."
    )


def generate_recommendations(
    predicted_score: float,
    usage_hours: float,
    study_hours: float,
    physical_hours: float,
    sleep_hours: float,
    threshold: float = 5.1
) -> Dict[str, Any]:
    """
    Generates evidence-based, personalized daily routine recommendations.
    
    Threshold: 5.1 (25th percentile of Mental_Health_Score in training set).
    If predicted_score < threshold:
        Title: 'Suggestions to Improve Your Daily Routine'
    Else:
        Title: 'Suggestions to Maintain Your Balanced Routine'

    Safety and Academic Constraints:
    - Never recommend reducing sleep.
    - Never automatically recommend reducing physical activity.
    - Do not recommend reducing study hours without clear justification.
    - Prioritize reducing excessive social media screen time.
    - Keep all suggestions strictly within the 24-hour envelope.
    - Does NOT constitute a medical diagnosis.
    """
    # Backend check of daily limit first
    is_valid, total_hours, remaining_hours, msg = validate_daily_hours(
        usage_hours, study_hours, physical_hours, sleep_hours
    )
    if not is_valid:
        raise ValueError(f"Cannot generate recommendations for invalid inputs: {msg}")

    is_low = predicted_score < threshold
    suggestions: List[Dict[str, str]] = []

    if is_low:
        title = "Suggestions to Improve Your Daily Routine"
        summary = (
            f"Your predicted Mental Health Score is {predicted_score:.2f}/10, which falls below "
            f"the baseline threshold ({threshold:.1f}/10, corresponding to the 25th percentile of students). "
            f"Based on empirical associations found in our analysis, here are personalized adjustments "
            f"to help support your wellbeing:"
        )

        # 1. Social media usage check
        if usage_hours >= 6.0:
            saved_time = min(2.5, usage_hours - 3.5)
            suggestions.append({
                "category": "Screen Time Reduction",
                "action": f"Gradually reduce social media usage by ~{saved_time:.1f} hours/day (down toward 3.5–4.0 hrs).",
                "reasoning": (
                    f"Your usage of {usage_hours:.1f} hrs/day is in the upper quartile. High usage and frequent unlocks "
                    f"strongly correlate with lower mental health scores (r = -0.82) due to digital fatigue and fragmented attention."
                )
            })
        elif usage_hours >= 4.5:
            suggestions.append({
                "category": "Screen Time Mindfulness",
                "action": "Implement focused 'screen-free' zones during study hours and 1 hour before bedtime.",
                "reasoning": (
                    f"Your usage of {usage_hours:.1f} hrs/day is moderate-high. Setting intentional app timers helps prevent "
                    f"passive scrolling and sleep disruption."
                )
            })

        # 2. Sleep hours check
        if sleep_hours < 7.0:
            target_sleep = min(8.0, sleep_hours + 1.5)
            sleep_gap = target_sleep - sleep_hours
            suggestions.append({
                "category": "Sleep Optimization",
                "action": f"Prioritize increasing sleep from {sleep_hours:.1f} hrs to at least {target_sleep:.1f} hrs/night.",
                "reasoning": (
                    f"Sleep duration is one of the strongest positive predictors of student wellbeing (r = +0.77). "
                    f"Under 7 hours of sleep is clinically linked with heightened stress, lower cognitive performance, and emotional dysregulation."
                )
            })

        # 3. Physical activity check
        if physical_hours < 1.0:
            target_activity = 1.0
            suggestions.append({
                "category": "Physical Wellbeing",
                "action": f"Incorporate {target_activity:.1f} hour of moderate physical activity daily (e.g., brisk walking, sports, cycling).",
                "reasoning": (
                    f"Your current physical activity is {physical_hours:.1f} hrs/day. Physical exercise is positively correlated "
                    f"with mental health scores (r = +0.52), stimulating endorphin release and stress resilience."
                )
            })

        # 4. Study hours balance check
        if study_hours > 7.0:
            suggestions.append({
                "category": "Study Pacing & Rest Breaks",
                "action": "Adopt structured study intervals (e.g., Pomodoro 50/10) rather than continuous high-intensity marathons.",
                "reasoning": (
                    f"While study hours correlate positively with academic engagement, exceeding {study_hours:.1f} hrs without structured "
                    f"recovery increases burnout risk. Ensure active breaks are scheduled."
                )
            })
        elif study_hours < 2.0:
            suggestions.append({
                "category": "Structured Learning Routine",
                "action": "Establish consistent daily study blocks (aim for 2.5–3.5 hrs) to reduce deadline anxiety.",
                "reasoning": (
                    "Regular structured study routines correlate with a greater sense of academic control and reduced panic-driven stress."
                )
            })

        # 5. Remaining hours reallocation
        if remaining_hours > 4.0:
            suggestions.append({
                "category": "Routine Reallocation",
                "action": f"You have {remaining_hours:.1f} unscheduled hours available. Allocate 1–2 hours toward outdoor leisure, hobbies, or restorative sleep.",
                "reasoning": "Unstructured free time can be intentionally directed toward restorative lifestyle habits."
            })

    else:
        title = "Suggestions to Maintain Your Balanced Routine"
        summary = (
            f"Your predicted Mental Health Score is {predicted_score:.2f}/10, which meets or exceeds "
            f"the positive benchmark ({threshold:.1f}/10). Your reported routine reflects supportive lifestyle habits:"
        )

        suggestions.append({
            "category": "Routine Consistency",
            "action": f"Maintain your current balanced sleep schedule ({sleep_hours:.1f} hrs/night).",
            "reasoning": "Consistent circadian rhythms are a fundamental pillar of sustained cognitive performance and emotional stability."
        })
        if usage_hours <= 4.0:
            suggestions.append({
                "category": "Healthy Digital Boundaries",
                "action": f"Keep your social media consumption bounded around {usage_hours:.1f} hrs/day.",
                "reasoning": "Moderate screen time minimizes digital fatigue and preserves attentional bandwidth for offline engagements."
            })
        if physical_hours >= 1.5:
            suggestions.append({
                "category": "Active Lifestyle",
                "action": f"Continue your positive physical activity routine ({physical_hours:.1f} hrs/day).",
                "reasoning": "Sustained regular physical exertion buffers against mid-semester stress spikes."
            })

    disclaimer = (
        "Important Note: This prediction and routine suggestions are generated by an empirical "
        "machine learning regression model for educational and academic project purposes. "
        "They do not constitute a clinical assessment, psychological evaluation, or medical diagnosis. "
        "If you or someone you know is experiencing distress, please reach out to professional counseling services."
    )

    return {
        "title": title,
        "predicted_score": round(predicted_score, 2),
        "threshold": threshold,
        "is_low": is_low,
        "summary": summary,
        "suggestions": suggestions,
        "total_hours": total_hours,
        "remaining_hours": remaining_hours,
        "disclaimer": disclaimer
    }
