// Mental Health Score Predictor - Client-side Interactive Engine
// Provides zero-server inference, strict 24-hour validation, and interactive exploration

// Model weights (Trained Ridge Regressor, alpha=0.1, R2=0.783, RMSE=0.622)
const MODEL_CONFIG = {
  intercept: 6.09309,
  threshold: 5.10,
  numMeans: {
    Age: 20.8218,
    Avg_Daily_Usage_Hours: 5.07846,
    Daily_Unlocks: 171.4526,
    Study_Hours: 3.00842,
    Physical_Activity_Hours: 1.7510,
    Sleep_Hours_Per_Night: 6.63458
  },
  numScales: {
    Age: 1.73662,
    Avg_Daily_Usage_Hours: 1.65391,
    Daily_Unlocks: 42.85825,
    Study_Hours: 1.63702,
    Physical_Activity_Hours: 0.66840,
    Sleep_Hours_Per_Night: 1.22139
  },
  numWeights: {
    Age: 0.0152,
    Avg_Daily_Usage_Hours: -0.4285,
    Daily_Unlocks: -0.1942,
    Study_Hours: 0.3812,
    Physical_Activity_Hours: 0.1654,
    Sleep_Hours_Per_Night: 0.4410
  }
};

// -------------------------------------------------------------
// STRICT 24-HOUR VALIDATION ENGINE
// -------------------------------------------------------------
function checkDailyHours() {
  const usage = parseFloat(document.getElementById("usage_hours").value) || 0;
  const study = parseFloat(document.getElementById("study_hours").value) || 0;
  const sleep = parseFloat(document.getElementById("sleep_hours").value) || 0;
  const physical = parseFloat(document.getElementById("physical_hours").value) || 0;

  const total = Math.round((usage + study + sleep + physical) * 10) / 10;
  const remaining = Math.round((24.0 - total) * 10) / 10;

  const totalDisplay = document.getElementById("total_hours_display");
  const remDisplay = document.getElementById("remaining_hours_display");
  const alertBox = document.getElementById("validation_alert");
  const predictBtn = document.getElementById("predict_btn");

  totalDisplay.innerText = `${total.toFixed(1)} / 24.0 hrs`;
  remDisplay.innerText = `${Math.max(0, remaining).toFixed(1)} hrs`;

  // Validation conditions
  if (usage < 0 || study < 0 || sleep < 0 || physical < 0) {
    alertBox.className = "alert-error";
    alertBox.innerText = "ERROR: Negative hours are physically impossible. Please enter positive numbers.";
    alertBox.style.display = "block";
    predictBtn.disabled = true;
    return false;
  }

  if (total > 24.0) {
    alertBox.className = "alert-error";
    const overage = (total - 24.0).toFixed(1);
    alertBox.innerText = `ERROR: Total daily activity hours cannot exceed 24 hours. You selected ${total.toFixed(1)} hrs (${overage} hrs over the limit). Please reduce your selected hours.`;
    alertBox.style.display = "block";
    predictBtn.disabled = true;
    return false;
  }

  // Valid (<= 24.0)
  alertBox.className = "alert-success";
  alertBox.innerText = `Valid input: ${total.toFixed(1)} hrs accounted for. ${remaining.toFixed(1)} unscheduled hrs remaining.`;
  alertBox.style.display = "block";
  predictBtn.disabled = false;
  return true;
}

// -------------------------------------------------------------
// RUN PREDICTION & RECOMMENDATIONS
// -------------------------------------------------------------
function runPrediction() {
  const isValid = checkDailyHours();
  if (!isValid) {
    alert("Prediction blocked: Total daily hours exceed 24.0 hours!");
    return;
  }

  const age = parseFloat(document.getElementById("age").value) || 21;
  const usage = parseFloat(document.getElementById("usage_hours").value) || 4.5;
  const unlocks = parseFloat(document.getElementById("daily_unlocks").value) || 150;
  const study = parseFloat(document.getElementById("study_hours").value) || 4.0;
  const sleep = parseFloat(document.getElementById("sleep_hours").value) || 7.5;
  const physical = parseFloat(document.getElementById("physical_hours").value) || 1.5;

  // Standardize continuous variables
  const zAge = (age - MODEL_CONFIG.numMeans.Age) / MODEL_CONFIG.numScales.Age;
  const zUsage = (usage - MODEL_CONFIG.numMeans.Avg_Daily_Usage_Hours) / MODEL_CONFIG.numScales.Avg_Daily_Usage_Hours;
  const zUnlocks = (unlocks - MODEL_CONFIG.numMeans.Daily_Unlocks) / MODEL_CONFIG.numScales.Daily_Unlocks;
  const zStudy = (study - MODEL_CONFIG.numMeans.Study_Hours) / MODEL_CONFIG.numScales.Study_Hours;
  const zPhysical = (physical - MODEL_CONFIG.numMeans.Physical_Activity_Hours) / MODEL_CONFIG.numScales.Physical_Activity_Hours;
  const zSleep = (sleep - MODEL_CONFIG.numMeans.Sleep_Hours_Per_Night) / MODEL_CONFIG.numScales.Sleep_Hours_Per_Night;

  // Linear dot product
  let score = MODEL_CONFIG.intercept +
    (zAge * MODEL_CONFIG.numWeights.Age) +
    (zUsage * MODEL_CONFIG.numWeights.Avg_Daily_Usage_Hours) +
    (zUnlocks * MODEL_CONFIG.numWeights.Daily_Unlocks) +
    (zStudy * MODEL_CONFIG.numWeights.Study_Hours) +
    (zPhysical * MODEL_CONFIG.numWeights.Physical_Activity_Hours) +
    (zSleep * MODEL_CONFIG.numWeights.Sleep_Hours_Per_Night);

  // Bound score
  score = Math.max(1.0, Math.min(10.0, score));
  const scoreRounded = score.toFixed(2);

  // Render Result
  const outputContainer = document.getElementById("prediction_results_container");
  outputContainer.style.display = "block";

  document.getElementById("pred_score_display").innerText = `${scoreRounded} / 10.0`;

  const tierText = document.getElementById("pred_tier_text");
  if (score < 5.10) {
    tierText.innerHTML = `<span style="color:#dc2626; font-weight:700;">⚠️ Lower Wellbeing Tier (&lt; 25th percentile threshold of 5.10). Routine improvements are strongly suggested.</span>`;
  } else if (score < 7.50) {
    tierText.innerHTML = `<span style="color:#2563eb; font-weight:700;">ℹ️ Moderate-Healthy Wellbeing Tier. Balanced routine maintained.</span>`;
  } else {
    tierText.innerHTML = `<span style="color:#16a34a; font-weight:700;">🌟 Optimal Wellbeing Tier. Strong protective habits observed.</span>`;
  }

  // Generate Personalized Suggestions
  const recContainer = document.getElementById("recommendations_container");
  recContainer.innerHTML = "";

  const isLow = score < 5.10;
  const recTitle = isLow ? "Suggestions to Improve Your Daily Routine" : "Suggestions to Maintain Your Balanced Routine";
  document.getElementById("rec_title_heading").innerText = recTitle;

  const suggestions = [];

  if (isLow) {
    if (usage >= 5.5) {
      suggestions.push({
        cat: "Screen Time Reduction",
        action: `Gradually decrease daily social media use from ${usage.toFixed(1)} hrs down to ~3.5 hrs.`,
        reason: "Excessive usage (r = -0.82) is strongly linked with digital fatigue, cognitive overload, and passive scrolling anxiety."
      });
    }
    if (sleep < 7.0) {
      suggestions.push({
        cat: "Sleep Prioritization",
        action: `Aim to increase sleep duration from ${sleep.toFixed(1)} hrs to 7.5–8.0 hrs/night.`,
        reason: "Sleep is the single strongest positive lifestyle factor (r = +0.77). Inadequate rest impairs emotional regulation."
      });
    }
    if (physical < 1.0) {
      suggestions.push({
        cat: "Physical Exercise",
        action: "Incorporate at least 45–60 minutes of moderate physical activity daily.",
        reason: "Regular movement (r = +0.52) stimulates neuroprotective endorphin release and stress resiliency."
      });
    }
    if (study > 7.0) {
      suggestions.push({
        cat: "Paced Study Intervals",
        action: "Adopt the 50/10 Pomodoro technique with intentional rest breaks.",
        reason: "Continuous studying without restorative pauses increases exhaustion risk."
      });
    }
  } else {
    suggestions.push({
      cat: "Sleep Consistency",
      action: `Maintain your consistent ${sleep.toFixed(1)} hrs/night sleep schedule.`,
      reason: "Consistent circadian rest supports sustained academic focus and emotional resilience."
    });
    suggestions.push({
      cat: "Digital Boundaries",
      action: `Keep your daily social media consumption capped around ${usage.toFixed(1)} hrs.`,
      reason: "Protects attention spans from digital distraction."
    });
  }

  suggestions.forEach(s => {
    const card = document.createElement("div");
    card.className = "rec-card";
    card.innerHTML = `<strong>🔹 ${s.cat}: ${s.action}</strong><br><small style="color:#4b5563;"><b>Empirical Justification:</b> ${s.reason}</small>`;
    recContainer.appendChild(card);
  });
}

// -------------------------------------------------------------
// INTERACTIVE FEATURE IMPORTANCE TOGGLE
// -------------------------------------------------------------
function toggleFeatureImportance(mode) {
  const container = document.getElementById("feature_importance_display");
  if (mode === "coefficients") {
    container.innerHTML = `
      <table>
        <tr><th>Feature</th><th>Standardized Effect Size (Linear Coef)</th><th>Impact Direction</th></tr>
        <tr><td>Sleep Hours Per Night</td><td>+0.441</td><td><span style="color:#16a34a; font-weight:700;">Strong Positive</span></td></tr>
        <tr><td>Avg Daily Usage Hours</td><td>-0.428</td><td><span style="color:#dc2626; font-weight:700;">Strong Negative</span></td></tr>
        <tr><td>Study Hours</td><td>+0.381</td><td><span style="color:#16a34a; font-weight:700;">Strong Positive</span></td></tr>
        <tr><td>Daily Phone Unlocks</td><td>-0.194</td><td><span style="color:#dc2626; font-weight:700;">Moderate Negative</span></td></tr>
        <tr><td>Physical Activity Hours</td><td>+0.165</td><td><span style="color:#16a34a; font-weight:700;">Moderate Positive</span></td></tr>
        <tr><td>Student Age</td><td>+0.015</td><td><span style="color:#64748b;">Negligible</span></td></tr>
      </table>
    `;
  } else if (mode === "tree") {
    container.innerHTML = `
      <table>
        <tr><th>Feature</th><th>Random Forest Relative Importance (Gini)</th><th>Rank</th></tr>
        <tr><td>Avg Daily Usage Hours</td><td>34.2%</td><td>#1</td></tr>
        <tr><td>Sleep Hours Per Night</td><td>28.5%</td><td>#2</td></tr>
        <tr><td>Study Hours</td><td>21.8%</td><td>#3</td></tr>
        <tr><td>Daily Phone Unlocks</td><td>9.4%</td><td>#4</td></tr>
        <tr><td>Physical Activity Hours</td><td>5.1%</td><td>#5</td></tr>
        <tr><td>Demographics (Country/Age/Gender)</td><td>1.0%</td><td>#6</td></tr>
      </table>
    `;
  } else {
    container.innerHTML = `
      <table>
        <tr><th>Feature Group</th><th>Test RMSE</th><th>Test R²</th><th>Predictive Share</th></tr>
        <tr><td>Full Combined Feature Set</td><td>0.367</td><td>0.925</td><td>100% (Baseline Model)</td></tr>
        <tr><td>Lifestyle Factors Only (Sleep, Study, Exercise)</td><td>0.757</td><td>0.679</td><td>Strong Independent Core</td></tr>
        <tr><td>Digital Usage Only (Hours, Unlocks, Platform)</td><td>0.741</td><td>0.692</td><td>Strong Independent Core</td></tr>
        <tr><td>Demographics Only (Age, Gender, Academic Level)</td><td>1.214</td><td>0.175</td><td>Weak Standalone Value</td></tr>
      </table>
    `;
  }
}

// -------------------------------------------------------------
// INTERACTIVE ERROR EXPLORER
// -------------------------------------------------------------
const SUBGROUP_ERRORS = {
  Gender: {
    Male: { count: 504, mae: 0.234, rmse: 0.365, maxOver: "+0.92", maxUnder: "-0.88" },
    Female: { count: 496, mae: 0.238, rmse: 0.369, maxOver: "+0.95", maxUnder: "-0.85" }
  },
  AcademicLevel: {
    Undergraduate: { count: 728, mae: 0.235, rmse: 0.366, maxOver: "+0.94", maxUnder: "-0.88" },
    Graduate: { count: 182, mae: 0.239, rmse: 0.371, maxOver: "+0.91", maxUnder: "-0.84" },
    HighSchool: { count: 90, mae: 0.241, rmse: 0.368, maxOver: "+0.95", maxUnder: "-0.82" }
  },
  Country: {
    India: { count: 78, mae: 0.231, rmse: 0.358, note: "Well-represented in training" },
    USA: { count: 71, mae: 0.237, rmse: 0.366, note: "Well-represented in training" },
    Canada: { count: 46, mae: 0.233, rmse: 0.361, note: "Moderate sample size" },
    Other: { count: 376, mae: 0.239, rmse: 0.370, note: "Diverse composite group" },
    UnseenCountries: { count: 120, mae: 0.651, rmse: 0.817, note: "Evaluated via GroupKFold leave-out" }
  }
};

function exploreErrors(subgroup) {
  const container = document.getElementById("subgroup_error_display");
  const data = SUBGROUP_ERRORS[subgroup];
  let html = `<table><tr><th>Subgroup</th><th>Test Sample Size</th><th>MAE</th><th>RMSE</th><th>Notes / Max Error</th></tr>`;
  for (const [key, val] of Object.entries(data)) {
    html += `<tr>
      <td><strong>${key}</strong></td>
      <td>${val.count}</td>
      <td>${val.mae.toFixed(3)}</td>
      <td>${val.rmse.toFixed(3)}</td>
      <td>${val.note || `Max +: ${val.maxOver}, Max -: ${val.maxUnder}`}</td>
    </tr>`;
  }
  html += `</table>`;
  container.innerHTML = html;
}

// Initialize on page load
window.addEventListener("DOMContentLoaded", () => {
  // Attach change listeners to activity inputs for real-time 24h validation
  const activityInputs = ["usage_hours", "study_hours", "sleep_hours", "physical_hours"];
  activityInputs.forEach(id => {
    const el = document.getElementById(id);
    if (el) {
      el.addEventListener("input", checkDailyHours);
    }
  });

  checkDailyHours();
  toggleFeatureImportance("coefficients");
  exploreErrors("Gender");
});
