from pathlib import Path

import pandas as pd
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.title("Fitbit Fitness Analytics")
st.caption(
    "Exploring activity, sleep, heart rate, calories, and wellness patterns "
    "from Fitbit daily fitness data."
)


# ---------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------
@st.cache_data
def load_data():
    data_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "fitbit_daily_cleaned.csv"
    )

    df = pd.read_csv(data_path)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    return df


try:
    df = load_data()

except FileNotFoundError:
    st.error(
        "The cleaned dataset could not be found. "
        "Please make sure the file is located at "
        "`data/fitbit_daily_cleaned.csv`."
    )
    st.stop()


# ---------------------------------------------------------
# BASIC DATA CALCULATIONS
# ---------------------------------------------------------
total_records = len(df)

unique_users = (
    df["Id"].nunique()
    if "Id" in df.columns
    else 0
)

avg_steps = (
    df["TotalSteps"].mean()
    if "TotalSteps" in df.columns
    else 0
)

avg_calories = (
    df["Calories"].mean()
    if "Calories" in df.columns
    else 0
)

avg_distance = (
    df["TotalDistance"].mean()
    if "TotalDistance" in df.columns
    else 0
)

avg_sleep = (
    df["TotalMinutesAsleep"].mean() / 60
    if "TotalMinutesAsleep" in df.columns
    else 0
)

avg_heart_rate = (
    df["AvgHeartRate"].mean()
    if "AvgHeartRate" in df.columns
    else 0
)


# ---------------------------------------------------------
# DATASET OVERVIEW
# ---------------------------------------------------------
st.markdown("---")

st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Daily Records",
        f"{total_records:,}"
    )

with col2:
    st.metric(
        "Unique Users",
        f"{unique_users:,}"
    )

with col3:
    st.metric(
        "Average Steps",
        f"{avg_steps:,.0f}"
    )

with col4:
    st.metric(
        "Average Calories",
        f"{avg_calories:,.0f}"
    )


# ---------------------------------------------------------
# ADDITIONAL KPIs
# ---------------------------------------------------------
st.subheader("Wellness Snapshot")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Distance",
        f"{avg_distance:.2f}"
    )

with col2:
    st.metric(
        "Average Sleep",
        f"{avg_sleep:.1f} hrs"
    )

with col3:
    if avg_heart_rate > 0:
        st.metric(
            "Average Heart Rate",
            f"{avg_heart_rate:.0f} bpm"
        )
    else:
        st.metric(
            "Average Heart Rate",
            "N/A"
        )

with col4:
    if "TotalMinutesAsleep" in df.columns:
        sleep_records = int(
            df["TotalMinutesAsleep"].notna().sum()
        )
    else:
        sleep_records = 0

    st.metric(
        "Sleep Records",
        f"{sleep_records:,}"
    )


# ---------------------------------------------------------
# BUSINESS PROBLEM
# ---------------------------------------------------------
st.markdown("---")

st.header("Business Problem")

st.write(
    """
    Fitness and wellness platforms collect large amounts of data from
    smart devices, including physical activity, sleep, heart rate,
    calories, and daily movement.

    The challenge is to transform this raw fitness data into meaningful
    information that can help understand user behavior, engagement,
    wellness patterns, and opportunities for improving digital health
    products and marketing strategies.
    """
)


# ---------------------------------------------------------
# PROJECT OBJECTIVE
# ---------------------------------------------------------
st.header("Project Objective")

st.write(
    """
    This project analyzes Fitbit daily fitness data to identify patterns
    in physical activity, sleep, heart rate, calorie expenditure, and
    overall wellness behavior.

    The analysis is designed to transform fitness-device data into
    understandable insights that can support data-driven business
    decisions and wellness-focused strategies.
    """
)


# ---------------------------------------------------------
# KEY QUESTIONS
# ---------------------------------------------------------
st.header("Key Business Questions")

questions = [
    "How active are users on a typical day?",
    "How much time do users spend in different activity levels?",
    "How much sedentary time is recorded?",
    "What are the typical sleep patterns?",
    "How does physical activity relate to calorie expenditure?",
    "What patterns can be observed in heart-rate data?",
    "How consistently are users recording sleep and health information?",
    "What wellness patterns can be identified from the data?",
]

for question in questions:
    st.markdown(f"- {question}")


# ---------------------------------------------------------
# DATASET INFORMATION
# ---------------------------------------------------------
st.markdown("---")

st.header("Dataset Information")

col1, col2 = st.columns(2)

with col1:
    st.write("**Records:**", f"{len(df):,}")
    st.write("**Columns:**", f"{len(df.columns):,}")
    st.write("**Unique Users:**", f"{unique_users:,}")

    if "Date" in df.columns:
        min_date = df["Date"].min()
        max_date = df["Date"].max()

        if pd.notna(min_date) and pd.notna(max_date):
            st.write(
                "**Date Range:**",
                f"{min_date.strftime('%Y-%m-%d')} "
                f"to {max_date.strftime('%Y-%m-%d')}"
            )

with col2:
    st.write("**Missing Values:**", f"{int(df.isna().sum().sum()):,}")
    st.write("**Duplicate Rows:**", f"{int(df.duplicated().sum()):,}")

    if "Id" in df.columns:
        st.write(
            "**Users Represented:**",
            f"{df['Id'].nunique():,}"
        )


# ---------------------------------------------------------
# ANALYTICAL AREAS
# ---------------------------------------------------------
st.markdown("---")

st.header("Analytical Areas")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Activity")
    st.write(
        "Analyze steps, distance, active minutes, and sedentary behavior."
    )

with col2:
    st.subheader("Sleep")
    st.write(
        "Explore sleep duration, time in bed, and sleep patterns."
    )

with col3:
    st.subheader("Heart Rate")
    st.write(
        "Examine average, minimum, and maximum heart-rate patterns."
    )

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Calories")
    st.write(
        "Analyze calorie expenditure and its relationship with activity."
    )

with col2:
    st.subheader("Wellness")
    st.write(
        "Combine multiple fitness indicators to identify behavioral patterns."
    )

with col3:
    st.subheader("Data Explorer")
    st.write(
        "Filter, inspect, and download the cleaned Fitbit dataset."
    )


# ---------------------------------------------------------
# PROJECT WORKFLOW
# ---------------------------------------------------------
st.markdown("---")

st.header("Project Workflow")

workflow = [
    "Data Cleaning",
    "Exploratory Data Analysis",
    "SQL Analysis",
    "Interactive Visualization",
    "Business Insights",
    "Wellness and Marketing Opportunities",
]

for index, step in enumerate(workflow, start=1):
    st.markdown(f"**{index}.** {step}")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")

st.caption(
    "Fitbit Fitness Analytics | Streamlit Data Analytics Project"
)
