import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Wellness Insights",
    page_icon=None,
    layout="wide"
)


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
@st.cache_data
def load_data():
    file_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "fitbit_daily_cleaned.csv"
    )

    df = pd.read_csv(file_path)

    # Convert date column if available
    date_columns = [
        "ActivityDate",
        "Date",
        "date",
        "activity_date"
    ]

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            break

    return df


df = load_data()


# ---------------------------------------------------------
# HELPER FUNCTION
# ---------------------------------------------------------
def find_column(possible_names):
    """
    Returns the first matching column from the dataset.
    Matching is case-insensitive.
    """

    column_map = {
        col.lower(): col
        for col in df.columns
    }

    for name in possible_names:
        if name.lower() in column_map:
            return column_map[name.lower()]

    return None


# ---------------------------------------------------------
# IDENTIFY IMPORTANT COLUMNS
# ---------------------------------------------------------
steps_col = find_column([
    "TotalSteps",
    "Steps",
    "total_steps"
])

calories_col = find_column([
    "Calories",
    "calories",
    "TotalCalories"
])

distance_col = find_column([
    "TotalDistance",
    "Distance",
    "total_distance"
])

sleep_col = find_column([
    "TotalMinutesAsleep",
    "MinutesAsleep",
    "SleepMinutes",
    "total_minutes_asleep"
])

time_bed_col = find_column([
    "TotalTimeInBed",
    "TimeInBed",
    "total_time_in_bed"
])

resting_hr_col = find_column([
    "RestingHeartRate",
    "RestingHR",
    "resting_heart_rate"
])

active_minutes_col = find_column([
    "VeryActiveMinutes",
    "ActiveMinutes",
    "FairlyActiveMinutes"
])


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------
st.title("Wellness Insights")
st.caption(
    "Integrated analysis of activity, sleep, heart rate, and calorie patterns"
)


# ---------------------------------------------------------
# DATA VALIDATION
# ---------------------------------------------------------
if df.empty:
    st.error("The dataset is empty.")
    st.stop()


# ---------------------------------------------------------
# CALCULATE METRICS
# ---------------------------------------------------------
def safe_mean(column):
    if column and column in df.columns:
        return pd.to_numeric(
            df[column],
            errors="coerce"
        ).mean()
    return np.nan


avg_steps = safe_mean(steps_col)
avg_calories = safe_mean(calories_col)
avg_distance = safe_mean(distance_col)
avg_sleep = safe_mean(sleep_col)
avg_time_bed = safe_mean(time_bed_col)
avg_resting_hr = safe_mean(resting_hr_col)
avg_active_minutes = safe_mean(active_minutes_col)


# ---------------------------------------------------------
# TOP KPI CARDS
# ---------------------------------------------------------
st.subheader("Overall Wellness Snapshot")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    if not np.isnan(avg_steps):
        st.metric(
            "Average Daily Steps",
            f"{avg_steps:,.0f}"
        )
    else:
        st.metric("Average Daily Steps", "N/A")

with kpi2:
    if not np.isnan(avg_sleep):
        sleep_hours = avg_sleep / 60
        st.metric(
            "Average Sleep",
            f"{sleep_hours:.1f} hrs"
        )
    else:
        st.metric("Average Sleep", "N/A")

with kpi3:
    if not np.isnan(avg_resting_hr):
        st.metric(
            "Average Resting HR",
            f"{avg_resting_hr:.0f} bpm"
        )
    else:
        st.metric("Average Resting HR", "N/A")

with kpi4:
    if not np.isnan(avg_calories):
        st.metric(
            "Average Calories",
            f"{avg_calories:,.0f}"
        )
    else:
        st.metric("Average Calories", "N/A")


st.divider()


# ---------------------------------------------------------
# WELLNESS SCORE
# ---------------------------------------------------------
st.subheader("Wellness Score")

score_components = []
score_explanations = []


# Activity score
if not np.isnan(avg_steps):

    if avg_steps >= 10000:
        activity_score = 100
    elif avg_steps >= 7500:
        activity_score = 85
    elif avg_steps >= 5000:
        activity_score = 70
    else:
        activity_score = 50

    score_components.append(activity_score)

    score_explanations.append(
        f"Activity level: {activity_score}/100"
    )


# Sleep score
if not np.isnan(avg_sleep):

    sleep_hours = avg_sleep / 60

    if 7 <= sleep_hours <= 9:
        sleep_score = 100
    elif 6 <= sleep_hours < 7 or 9 < sleep_hours <= 10:
        sleep_score = 80
    elif 5 <= sleep_hours < 6:
        sleep_score = 60
    else:
        sleep_score = 45

    score_components.append(sleep_score)

    score_explanations.append(
        f"Sleep level: {sleep_score}/100"
    )


# Heart-rate score
if not np.isnan(avg_resting_hr):

    if 60 <= avg_resting_hr <= 70:
        hr_score = 100
    elif 55 <= avg_resting_hr < 60 or 70 < avg_resting_hr <= 80:
        hr_score = 85
    elif 50 <= avg_resting_hr < 55 or 80 < avg_resting_hr <= 90:
        hr_score = 70
    else:
        hr_score = 55

    score_components.append(hr_score)

    score_explanations.append(
        f"Resting heart-rate level: {hr_score}/100"
    )


# Calculate final score
if score_components:
    wellness_score = np.mean(score_components)

    st.metric(
        "Overall Wellness Score",
        f"{wellness_score:.0f}/100"
    )

    st.progress(
        int(wellness_score) / 100
    )

    for explanation in score_explanations:
        st.write(explanation)

else:
    st.warning(
        "There are not enough measurable wellness fields "
        "to calculate a score."
    )


st.divider()


# ---------------------------------------------------------
# ACTIVITY INSIGHTS
# ---------------------------------------------------------
st.subheader("Activity Insights")

activity_col1, activity_col2 = st.columns(2)

with activity_col1:

    if not np.isnan(avg_steps):

        st.write("### Activity Performance")

        if avg_steps >= 10000:
            st.success(
                "Daily activity is relatively high based on average step count."
            )

        elif avg_steps >= 7500:
            st.info(
                "Daily activity is moderate to strong, with room for additional movement."
            )

        elif avg_steps >= 5000:
            st.warning(
                "Daily movement is moderate. Increasing walking or active time could improve activity levels."
            )

        else:
            st.warning(
                "Average daily steps are relatively low. More regular movement may be beneficial."
            )

with activity_col2:

    if not np.isnan(avg_distance):

        st.write("### Distance Performance")

        st.metric(
            "Average Daily Distance",
            f"{avg_distance:.2f}"
        )

        st.write(
            "Distance can be used as an additional indicator "
            "of daily mobility and physical activity."
        )


# ---------------------------------------------------------
# SLEEP INSIGHTS
# ---------------------------------------------------------
st.divider()

st.subheader("Sleep Insights")

if not np.isnan(avg_sleep):

    sleep_hours = avg_sleep / 60

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average Sleep Duration",
            f"{sleep_hours:.1f} hours"
        )

    with col2:

        if 7 <= sleep_hours <= 9:
            st.success(
                "Average sleep duration falls within a commonly recommended adult range."
            )

        elif sleep_hours < 7:
            st.warning(
                "Average sleep duration is below 7 hours."
            )

        else:
            st.info(
                "Average sleep duration is above 9 hours."
            )

else:
    st.info(
        "Sleep information is not available in the dataset."
    )


# ---------------------------------------------------------
# HEART RATE INSIGHTS
# ---------------------------------------------------------
st.divider()

st.subheader("Heart Rate Insights")

if not np.isnan(avg_resting_hr):

    st.metric(
        "Average Resting Heart Rate",
        f"{avg_resting_hr:.0f} bpm"
    )

    st.write(
        "Resting heart rate provides a useful descriptive indicator "
        "for monitoring changes in cardiovascular activity over time."
    )

    if avg_resting_hr < 60:
        st.info(
            "The observed average resting heart rate is below 60 bpm. "
            "Individual interpretation depends on factors such as fitness, age, "
            "medications, and measurement conditions."
        )

    elif avg_resting_hr <= 70:
        st.success(
            "The observed average resting heart rate is within a commonly observed range."
        )

    elif avg_resting_hr <= 80:
        st.warning(
            "The observed average resting heart rate is above 70 bpm."
        )

    else:
        st.warning(
            "The observed average resting heart rate is relatively high. "
            "Trends and individual context should be considered."
        )

else:
    st.info(
        "Resting heart-rate information is not available."
    )


# ---------------------------------------------------------
# CALORIE INSIGHTS
# ---------------------------------------------------------
st.divider()

st.subheader("Calorie Insights")

if not np.isnan(avg_calories):

    st.metric(
        "Average Daily Calories",
        f"{avg_calories:,.0f}"
    )

    st.write(
        "Calorie expenditure can be examined together with activity "
        "levels to understand overall energy expenditure patterns."
    )

    if not np.isnan(avg_steps):

        calories_per_step = avg_calories / avg_steps

        st.write(
            f"Average calories per recorded step: "
            f"{calories_per_step:.3f}"
        )

else:
    st.info(
        "Calorie information is not available."
    )


# ---------------------------------------------------------
# CORRELATION ANALYSIS
# ---------------------------------------------------------
st.divider()

st.subheader("Wellness Relationships")

numeric_columns = []

for col in [
    steps_col,
    calories_col,
    distance_col,
    sleep_col,
    time_bed_col,
    resting_hr_col,
    active_minutes_col
]:

    if col and col in df.columns:
        numeric_columns.append(col)


if len(numeric_columns) >= 2:

    numeric_df = df[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce"
    )

    correlation = numeric_df.corr()

    st.dataframe(
        correlation.round(2),
        use_container_width=True
    )

    st.caption(
        "Correlation indicates statistical association between variables; "
        "it does not establish causation."
    )

else:

    st.info(
        "Not enough numeric wellness variables are available for correlation analysis."
    )


# ---------------------------------------------------------
# BUSINESS INSIGHTS
# ---------------------------------------------------------
st.divider()

st.subheader("Business Insights")

business_col1, business_col2 = st.columns(2)

with business_col1:

    st.write("### Workforce Wellness")

    st.write(
        "Organizations can use aggregated wearable-data insights "
        "to understand general employee activity and wellness trends. "
        "The analysis can support wellness-program planning, "
        "activity challenges, and engagement strategies."
    )

    st.write("### Fitness & Health Platforms")

    st.write(
        "Fitness applications can combine activity, sleep, heart-rate, "
        "and calorie metrics to provide users with a unified wellness dashboard."
    )

with business_col2:

    st.write("### Personalized Engagement")

    st.write(
        "Users with lower activity or inconsistent sleep patterns "
        "can receive targeted educational suggestions and activity reminders."
    )

    st.write("### Program Performance")

    st.write(
        "Organizations can compare aggregated wellness metrics over time "
        "to understand whether wellness initiatives are associated with "
        "changes in engagement and activity."
    )


# ---------------------------------------------------------
# RECOMMENDATIONS
# ---------------------------------------------------------
st.divider()

st.subheader("Recommendations")

recommendations = []


if not np.isnan(avg_steps):

    if avg_steps < 7500:
        recommendations.append(
            "Encourage more daily movement through walking goals, activity breaks, or fitness challenges."
        )
    else:
        recommendations.append(
            "Maintain consistent daily activity and monitor changes over time."
        )


if not np.isnan(avg_sleep):

    sleep_hours = avg_sleep / 60

    if sleep_hours < 7:
        recommendations.append(
            "Encourage consistent sleep schedules and better sleep-hygiene practices."
        )
    elif sleep_hours > 9:
        recommendations.append(
            "Review sleep consistency and overall wellness context rather than relying only on duration."
        )
    else:
        recommendations.append(
            "Maintain consistent sleep duration and monitor sleep trends."
        )


if not np.isnan(avg_resting_hr):

    recommendations.append(
        "Monitor resting heart-rate trends over time instead of relying on a single average."
    )


if not np.isnan(avg_calories):

    recommendations.append(
        "Combine calorie expenditure with activity metrics for a broader view of energy expenditure."
    )


if recommendations:

    for recommendation in recommendations:
        st.write(f"- {recommendation}")


# ---------------------------------------------------------
# IMPORTANT DISCLAIMER
# ---------------------------------------------------------
st.divider()

st.caption(
    "Note: These insights are analytical observations from wearable-device data "
    "and are not medical diagnoses or medical advice. Individual health decisions "
    "should be based on appropriate professional guidance."
)
