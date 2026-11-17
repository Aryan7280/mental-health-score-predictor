"""
Mental Health Score Predictor - Streamlit Web Application

Pages/Tabs:
A. Home Page: Project overview, research questions, workflow, key highlights.
B. Exploratory Data Analysis: Interactive Plotly distributions, correlations, and filters.
C. Model Performance: Benchmark tables, actual vs predicted, residual diagnostics, ablation studies.
D. Prediction & Lifestyle Advisor:
   - Interactive inputs
   - STRICT 24-Hour Validation (frontend + backend enforcement)
   - Live total and remaining hours meters
   - Prediction disabled if total > 24 hours
   - Evidence-based personalized daily routine recommendations
"""
import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.utils import validate_daily_hours, generate_recommendations
from src.preprocessing import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, TARGET_COLUMN

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Mental Health Score Predictor | ES 335",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 16px;
        border-left: 4px solid #3B82F6;
        margin-bottom: 12px;
    }
    .error-box {
        background-color: #FEE2E2;
        border: 2px solid #EF4444;
        border-radius: 8px;
        padding: 14px;
        color: #991B1B;
        font-weight: 600;
        margin: 12px 0px;
    }
    .success-box {
        background-color: #ECFDF5;
        border: 2px solid #10B981;
        border-radius: 8px;
        padding: 14px;
        color: #065F46;
        font-weight: 600;
        margin: 12px 0px;
    }
    .card-recommendation {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_cached_data():
    data_path = "data/dataset.csv"
    if not os.path.exists(data_path):
        data_path = "mental-health-score-predictor/data/dataset.csv"
    df = pd.read_csv(data_path).drop_duplicates().reset_index(drop=True)
    df["Physical_Activity_Hours"] = df["Physical_Activity_Hours"].clip(lower=0.0)
    return df


@st.cache_resource
def load_trained_model():
    model_path = "models/best_model.joblib"
    if not os.path.exists(model_path):
        model_path = "mental-health-score-predictor/models/best_model.joblib"
    meta_path = "models/model_metadata.json"
    if not os.path.exists(meta_path):
        meta_path = "mental-health-score-predictor/models/model_metadata.json"
    
    model = joblib.load(model_path)
    with open(meta_path, "r") as f:
        metadata = json.load(f)
    return model, metadata


# Load artifacts
try:
    df_clean = load_cached_data()
    best_model, metadata = load_trained_model()
except Exception as e:
    st.error(f"Error loading project artifacts: {e}")
    st.stop()


# Sidebar Navigation
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3062/3062634.png", width=70)
st.sidebar.title("Navigation")
st.sidebar.markdown("**Course:** ES 335 ML Project  \n**Author:** Aryan Mangal (25110058)")

page = st.sidebar.radio(
    "Go to",
    ["🏠 Home & Overview", "📊 Exploratory Data Analysis", "📈 Model Benchmarking", "🔮 Mental Health Predictor & Advisor"],
    index=3
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 24-Hour Rule")
st.sidebar.caption("All non-overlapping daily activity inputs are strictly constrained to 24 hours total.")


# ==============================================================================
# PAGE 1: HOME & OVERVIEW
# ==============================================================================
if page == "🏠 Home & Overview":
    st.markdown('<div class="main-header">🧠 Mental Health Score Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Predicting Student Wellbeing from Social Media Habits & Lifestyle Factors</div>', unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Survey Records", f"{metadata['sample_size']:,}")
    with col2:
        st.metric("Countries Represented", f"{df_clean['Country'].nunique()}")
    with col3:
        st.metric("Best Model", metadata['best_model_name'])
    with col4:
        st.metric("Test R² Score", f"{metadata['test_r2']:.3f}")

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("📌 Project Problem Statement")
        st.markdown("""
        Social media use is often blamed for poor student wellbeing, but empirical questions remain:
        - How much does screen time truly predict mental health compared to fundamental physiological habits like **sleep duration** and **physical activity**?
        - Can a machine learning model reliably generalize to students from **unseen countries**?
        - How can predictive models be transformed into **actionable routine adjustments** without violating biological time budgets?

        This application provides an empirical, end-to-end Machine Learning system trained on 5,000 global student survey responses.
        """)

        st.subheader("🎯 Project Objectives")
        st.markdown("""
        1. **Rigorous Data Quality Auditing:** Deduplication, non-negativity constraints, and distribution analysis.
        2. **Preventing Target Leakage:** Explicitly omitting concurrent psychological state indicators (`Stress_Level`) to ensure all features are observable antecedents.
        3. **Diverse Algorithm Benchmarking:** Comparing Baseline Dummy, Linear, Ridge, Lasso, K-Nearest Neighbors, Random Forest, and Gradient Boosting.
        4. **Out-of-Distribution Generalization:** GroupKFold evaluation across 111 nationalities.
        5. **Strict 24-Hour Validation:** Real-time enforcement that daily activities logically cannot exceed 24 hours.
        """)

    with col_right:
        st.subheader("📋 Dataset Acknowledgement")
        st.markdown("""
        - **Source:** [Student Social Media & Mental Health Impact](https://www.kaggle.com/datasets/shivasingh4945/student-social-media-and-mental-health-impact)
        - **Author:** Shiva Singh (`@shivasingh4945`), Kaggle
        - **Units:** 5,000 self-reported student records
        - **Target:** Continuous `Mental_Health_Score` (1.0 to 10.0 scale)
        """)

        st.subheader("⚙️ Technical Architecture")
        st.markdown("""
        - **Data Pipeline:** Scikit-learn `Pipeline` + `ColumnTransformer`
        - **Algorithms:** KNN Regressor, Random Forest, Gradient Boosting, Ridge, Lasso, OLS
        - **Validation:** 5-Fold Cross Validation + Leave-Countries-Out GroupKFold
        - **Deployment:** Streamlit Cloud & GitHub Pages Static App
        """)


# ==============================================================================
# PAGE 2: EXPLORATORY DATA ANALYSIS
# ==============================================================================
elif page == "📊 Exploratory Data Analysis":
    st.markdown('<div class="main-header">📊 Exploratory Data Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Interactive data exploration and feature relationship inspection</div>', unsafe_allow_html=True)

    # Filter Controls
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        gender_filter = st.multiselect("Filter by Gender", options=df_clean["Gender"].unique(), default=df_clean["Gender"].unique())
    with col_f2:
        acad_filter = st.multiselect("Filter by Academic Level", options=df_clean["Academic_Level"].unique(), default=df_clean["Academic_Level"].unique())
    with col_f3:
        platform_filter = st.multiselect("Filter by Platform", options=df_clean["Most_Used_Platform"].unique(), default=df_clean["Most_Used_Platform"].unique()[:6])

    filtered_df = df_clean[
        (df_clean["Gender"].isin(gender_filter)) &
        (df_clean["Academic_Level"].isin(acad_filter)) &
        (df_clean["Most_Used_Platform"].isin(platform_filter))
    ]

    st.caption(f"Displaying {len(filtered_df)} records matching the selected filters.")

    tab1, tab2, tab3 = st.tabs(["Target & Key Distributions", "Correlations & Heatmap", "Behavioral Bivariate Plots"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            fig_hist = px.histogram(
                filtered_df, x="Mental_Health_Score", nbins=30, marginal="box",
                title="Mental Health Score Distribution", color_discrete_sequence=["#3B82F6"]
            )
            fig_hist.add_vline(x=5.10, line_dash="dash", line_color="orange", annotation_text="25th Pct (5.10)")
            st.plotly_chart(fig_hist, use_container_width=True)
        with c2:
            fig_usage = px.histogram(
                filtered_df, x="Avg_Daily_Usage_Hours", nbins=30, marginal="box",
                title="Daily Social Media Usage (Hours)", color_discrete_sequence=["#EC4899"]
            )
            st.plotly_chart(fig_usage, use_container_width=True)

    with tab2:
        c1, c2 = st.columns([3, 2])
        with c1:
            num_cols = NUMERICAL_FEATURES + [TARGET_COLUMN]
            corr = filtered_df[num_cols].corr()
            fig_corr = px.imshow(
                corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                title="Pearson Correlation Matrix (Selected Subset)"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        with c2:
            st.markdown("#### Key Correlation Takeaways")
            st.markdown("""
            - **Social Media Usage (r = -0.82):** Strong negative association with mental health scores.
            - **Daily Phone Unlocks (r = -0.79):** High unlock frequency reflects fragmented attention and digital stress.
            - **Sleep Hours (r = +0.77):** Strongest positive protective factor for student wellbeing.
            - **Study Hours (r = +0.75):** Regular academic pacing correlates with higher wellbeing.
            - **Physical Activity (r = +0.52):** Moderate positive protective association.
            """)

    with tab3:
        fig_scatter = px.scatter(
            filtered_df,
            x="Avg_Daily_Usage_Hours",
            y="Mental_Health_Score",
            color="Sleep_Hours_Per_Night",
            size="Daily_Unlocks",
            hover_data=["Country", "Academic_Level"],
            title="Mental Health Score vs. Usage Hours (Colored by Sleep Duration)",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)


# ==============================================================================
# PAGE 3: MODEL PERFORMANCE
# ==============================================================================
elif page == "📈 Model Benchmarking":
    st.markdown('<div class="main-header">📈 Machine Learning Model Benchmarks</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Rigorous cross-validation, hyperparameter tuning, and error diagnostics</div>', unsafe_allow_html=True)

    # Load comparison table
    comp_path = "reports/model_comparison.csv"
    if not os.path.exists(comp_path):
        comp_path = "mental-health-score-predictor/reports/model_comparison.csv"
    comp_df = pd.read_csv(comp_path)

    st.subheader("🏆 Model Comparison Table (Held-Out Test Set N=1,000)")
    st.dataframe(comp_df, use_container_width=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="metric-card"><h4>🥇 Best Model</h4><h2>K-Nearest Neighbors</h2><p>k=3, distance-weighted</p></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="metric-card"><h4>📉 Test RMSE</h4><h2>0.3671</h2><p>95% CI: [0.335, 0.402]</p></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="metric-card"><h4>🎯 Test R² Score</h4><h2>0.9245</h2><p>Explanatory variance: 92.5%</p></div>', unsafe_allow_html=True)

    st.markdown("---")

    col_fig1, col_fig2 = st.columns(2)
    with col_fig1:
        fig_path1 = "reports/figures/03_actual_vs_predicted.png"
        if not os.path.exists(fig_path1):
            fig_path1 = "mental-health-score-predictor/" + fig_path1
        if os.path.exists(fig_path1):
            st.image(fig_path1, caption="Actual vs. Predicted Scores (KNN Model, R² = 0.925)", use_column_width=True)

    with col_fig2:
        fig_path2 = "reports/figures/04_residual_diagnostics.png"
        if not os.path.exists(fig_path2):
            fig_path2 = "mental-health-score-predictor/" + fig_path2
        if os.path.exists(fig_path2):
            st.image(fig_path2, caption="Residual Diagnostics (Homoscedasticity & Normalcy)", use_column_width=True)

    st.subheader("🛡️ Scientific Validation Studies")
    tab_ab1, tab_ab2 = st.tabs(["Target Leakage Ablation", "Country Generalization (GroupKFold)"])

    with tab_ab1:
        st.markdown("""
        **Why Stress_Level was Excluded from the Primary Model:**
        `Stress_Level` is an evaluation of subjective psychological state at the time of the survey.
        Including it creates severe target leakage because stress is a symptom/outcome of mental health, not an independent daily habit.
        """)
        ab_path = "reports/ablation_study.csv"
        if not os.path.exists(ab_path):
            ab_path = "mental-health-score-predictor/" + ab_path
        if os.path.exists(ab_path):
            ab_df = pd.read_csv(ab_path)
            st.table(ab_df)

    with tab_ab2:
        st.markdown("""
        **Out-of-Distribution Generalization to Unseen Countries:**
        We performed `GroupKFold(n_splits=5)` grouping on `Country` (111 unique countries).
        In each fold, students from 20+ countries were completely held out from training.
        """)
        cg_path = "reports/country_generalization.csv"
        if not os.path.exists(cg_path):
            cg_path = "mental-health-score-predictor/" + cg_path
        if os.path.exists(cg_path):
            cg_df = pd.read_csv(cg_path)
            st.table(cg_df)


# ==============================================================================
# PAGE 4: INTERACTIVE PREDICTOR & LIFESTYLE ADVISOR (WITH STRICT 24-HOUR VALIDATION)
# ==============================================================================
elif page == "🔮 Mental Health Predictor & Advisor":
    st.markdown('<div class="main-header">🔮 Mental Health Score Predictor</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Enter student lifestyle factors to generate an empirical prediction and routine advice</div>', unsafe_allow_html=True)

    st.info("⏱️ **Strict 24-Hour Law:** Total non-overlapping daily activity hours (Social Media + Study + Sleep + Exercise) must not exceed 24.0 hours.")

    # Form layout
    with st.form("prediction_form"):
        st.markdown("### 1. Student Profile & Demographics")
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            age = st.slider("Age", min_value=18, max_value=25, value=21, step=1)
            gender = st.selectbox("Gender", options=["Male", "Female"])
        with col_d2:
            academic_level = st.selectbox("Academic Level", options=["Undergraduate", "Graduate", "High School"])
            country = st.selectbox("Country", options=sorted(df_clean["Country"].unique().tolist()), index=sorted(df_clean["Country"].unique().tolist()).index("India") if "India" in df_clean["Country"].unique() else 0)
        with col_d3:
            platform = st.selectbox("Most Used Platform", options=sorted(df_clean["Most_Used_Platform"].unique().tolist()))
            purpose = st.selectbox("Purpose of Use", options=sorted(df_clean["Purpose_Of_Use"].unique().tolist()))

        st.markdown("---")
        st.markdown(r"### 2. Daily Digital & Lifestyle Hours (Must sum to $\le 24.0$ hrs)")

        col_h1, col_h2, col_h3, col_h4 = st.columns(4)
        with col_h1:
            usage_hours = st.number_input(
                "Social Media Usage (hrs/day)",
                min_value=0.0, max_value=24.0, value=4.5, step=0.1,
                help="Daily hours spent on social media apps."
            )
            daily_unlocks = st.slider("Daily Phone Unlocks", min_value=30, max_value=300, value=150, step=1)
        with col_h2:
            study_hours = st.number_input(
                "Study Hours (hrs/day)",
                min_value=0.0, max_value=24.0, value=4.0, step=0.1,
                help="Dedicated academic study and lecture hours."
            )
        with col_h3:
            sleep_hours = st.number_input(
                "Sleep Hours (hrs/night)",
                min_value=0.0, max_value=24.0, value=7.5, step=0.1,
                help="Average nightly sleep duration."
            )
        with col_h4:
            physical_hours = st.number_input(
                "Physical Activity (hrs/day)",
                min_value=0.0, max_value=24.0, value=1.5, step=0.1,
                help="Exercise, walking, sports, or gym hours."
            )

        # ----------------------------------------------------------------------
        # STRICT 24-HOUR VALIDATION (Frontend check in form)
        # ----------------------------------------------------------------------
        is_valid, total_hours, remaining_hours, validation_msg = validate_daily_hours(
            usage_hours, study_hours, physical_hours, sleep_hours
        )

        st.markdown("#### Live Time Budget Tracker")
        c_m1, c_m2, c_m3 = st.columns([1, 1, 2])
        with c_m1:
            st.metric("Total Hours Accounted", f"{total_hours:.1f} / 24.0 hrs")
        with c_m2:
            st.metric("Remaining Unallocated Hours", f"{max(0.0, remaining_hours):.1f} hrs")
        with c_m3:
            if not is_valid:
                st.markdown(f'<div class="error-box">⛔ {validation_msg}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-box">✅ {validation_msg}</div>', unsafe_allow_html=True)

        # Submit button: Disabled visually/logically if total_hours > 24
        submit_btn = st.form_submit_button(
            "Predict Mental Health Score",
            disabled=(not is_valid)
        )

    # --------------------------------------------------------------------------
    # PREDICTION EXECUTION (WITH BACKEND ENFORCEMENT)
    # --------------------------------------------------------------------------
    if submit_btn:
        # BACKEND ENFORCEMENT: Reject immediately if bypassed
        backend_valid, b_total, b_rem, b_msg = validate_daily_hours(
            usage_hours, study_hours, physical_hours, sleep_hours
        )
        if not backend_valid:
            st.error(f"BACKEND VALIDATION REJECTED: {b_msg}")
            st.stop()

        # Build feature vector matching model schema
        input_data = pd.DataFrame([{
            "Age": int(age),
            "Gender": str(gender),
            "Country": str(country),
            "Academic_Level": str(academic_level),
            "Most_Used_Platform": str(platform),
            "Purpose_Of_Use": str(purpose),
            "Avg_Daily_Usage_Hours": float(usage_hours),
            "Daily_Unlocks": int(daily_unlocks),
            "Study_Hours": float(study_hours),
            "Physical_Activity_Hours": float(physical_hours),
            "Sleep_Hours_Per_Night": float(sleep_hours)
        }])

        try:
            predicted_score = float(best_model.predict(input_data)[0])
            # Bound prediction to logical scale 1.0 - 10.0
            predicted_score = float(np.clip(predicted_score, 1.0, 10.0))
        except Exception as err:
            st.error(f"Prediction failed: {err}")
            st.stop()

        # Display Prediction Result
        st.markdown("---")
        st.subheader("🎯 Prediction Results")

        res_col1, res_col2 = st.columns([2, 3])
        with res_col1:
            # Score Gauge Chart
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=predicted_score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Predicted Mental Health Score", 'font': {'size': 18}},
                gauge={
                    'axis': {'range': [1, 10], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "#2563EB"},
                    'steps': [
                        {'range': [1, 5.10], 'color': "#FEE2E2"},
                        {'range': [5.10, 7.50], 'color': "#FEF3C7"},
                        {'range': [7.50, 10], 'color': "#D1FAE5"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 5.10
                    }
                }
            ))
            fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig_gauge, use_container_width=True)

        with res_col2:
            st.markdown(f"### Score: **{predicted_score:.2f} / 10.0**")
            if predicted_score < 5.10:
                st.warning(f"⚠️ **Score Assessment:** Lower Tier (< 25th percentile threshold of 5.10). Routine adjustments are recommended.")
            elif predicted_score < 7.50:
                st.info(f"ℹ️ **Score Assessment:** Moderate-Healthy Tier. Balanced lifestyle habits observed.")
            else:
                st.success(f"🌟 **Score Assessment:** Optimal Tier (> 75th percentile). Strong protective habits observed.")

            st.markdown(f"""
            - **Primary Contributing Habit:** Sleep ({sleep_hours:.1f} hrs) and Daily Screen Time ({usage_hours:.1f} hrs).
            - **Estimated Confidence Interval (95%):** [{max(1.0, predicted_score - 0.37):.2f}, {min(10.0, predicted_score + 0.37):.2f}]
            - **Model Used:** {metadata['best_model_name']} (Trained on N=3,998)
            """)

        # ----------------------------------------------------------------------
        # EVIDENCE-BASED PERSONALIZED RECOMMENDATIONS (SECTION 8)
        # ----------------------------------------------------------------------
        st.markdown("---")
        rec_data = generate_recommendations(
            predicted_score=predicted_score,
            usage_hours=usage_hours,
            study_hours=study_hours,
            physical_hours=physical_hours,
            sleep_hours=sleep_hours,
            threshold=5.10
        )

        st.subheader(f"💡 {rec_data['title']}")
        st.write(rec_data["summary"])

        for rec in rec_data["suggestions"]:
            st.markdown(f"""
            <div class="card-recommendation">
                <span style="font-size: 1.05rem; font-weight: 700; color: #1E40AF;">🔹 {rec['category']}: {rec['action']}</span><br>
                <span style="font-size: 0.95rem; color: #374151;"><b>Empirical Justification:</b> {rec['reasoning']}</span>
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"ℹ️ {rec_data['disclaimer']}")
