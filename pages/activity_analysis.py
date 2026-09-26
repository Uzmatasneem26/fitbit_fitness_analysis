
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------
st.title("Activity Analysis")
st.caption(
    "Analyze daily steps, distance, activity intensity, and sedentary behavior."
)


# ---------------------------------------------------------
# LOAD DATA
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
        "Please check that the file exists at "
        "`data/fitbit_daily_cleaned.csv`."
    )
    st.stop()


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("Activity Filters")

# User filter
if "Id" in df.columns:
    users = sorted(df["Id"].dropna().unique())

    selected_users = st.sidebar.multiselect(
        "Select Users",
        options=users,
        default=users
    )

    filtered_df = df[df["Id"].isin(selected_users)].copy()
else:
    filtered_df = df.copy()


# Date filter
if "Date" in filtered_df.columns:

    min_date = filtered_df["Date"].min()
    max_date = filtered_df["Date"].max()

    if pd.notna(min_date) and pd.notna(max_date):

        selected_dates = st.sidebar.date_input(
            "Select Date Range",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )

        if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
            start_date, end_date = selected_dates

            filtered_df = filtered_df[
                (filtered_df["Date"].dt.date >= start_date)
                & (filtered_df["Date"].dt.date <= end_date)
            ]


# ---------------------------------------------------------
# EMPTY DATA CHECK
# ---------------------------------------------------------
if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------
avg_steps = filtered_df["TotalSteps"].mean()

avg_distance = filtered_df["TotalDistance"].mean()

avg_very_active = filtered_df["VeryActiveMinutes"].mean()

avg_fairly_active = filtered_df["FairlyActiveMinutes"].mean()

avg_lightly_active = filtered_df["LightlyActiveMinutes"].mean()

avg_sedentary = filtered_df["SedentaryMinutes"].mean()


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Daily Steps",
        f"{avg_steps:,.0f}"
    )

with col2:
    st.metric(
        "Average Distance",
        f"{avg_distance:.2f}"
    )

with col3:
    st.metric(
        "Average Active Minutes",
        f"{(
            avg_very_active
            + avg_fairly_active
            + avg_lightly_active
        ):,.0f}"
    )

with col4:
    st.metric(
        "Average Sedentary Minutes",
        f"{avg_sedentary:,.0f}"
    )


# ---------------------------------------------------------
# ACTIVITY INTENSITY
# ---------------------------------------------------------
st.markdown("---")

st.header("Activity Intensity")

activity_data = pd.DataFrame(
    {
        "Activity Level": [
            "Very Active",
            "Fairly Active",
            "Lightly Active",
            "Sedentary"
        ],
        "Average Minutes": [
            avg_very_active,
            avg_fairly_active,
            avg_lightly_active,
            avg_sedentary
        ]
    }
)


col1, col2 = st.columns(2)


# ---------------------------------------------------------
# BAR CHART
# ---------------------------------------------------------
with col1:

    fig_activity = px.bar(
        activity_data,
        x="Activity Level",
        y="Average Minutes",
        title="Average Minutes by Activity Level",
        text_auto=".0f"
    )

    fig_activity.update_layout(
        xaxis_title="Activity Level",
        yaxis_title="Minutes",
        showlegend=False
    )

    st.plotly_chart(
        fig_activity,
        use_container_width=True
    )


# ---------------------------------------------------------
# PIE CHART
# ---------------------------------------------------------
with col2:

    fig_pie = px.pie(
        activity_data,
        names="Activity Level",
        values="Average Minutes",
        title="Distribution of Daily Activity Time",
        hole=0.45
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )


# ---------------------------------------------------------
# STEPS DISTRIBUTION
# ---------------------------------------------------------
st.markdown("---")

st.header("Daily Steps Distribution")

fig_steps = px.histogram(
    filtered_df,
    x="TotalSteps",
    nbins=30,
    title="Distribution of Daily Steps",
    labels={
        "TotalSteps": "Daily Steps"
    }
)

fig_steps.update_layout(
    yaxis_title="Number of Records"
)

st.plotly_chart(
    fig_steps,
    use_container_width=True
)


# ---------------------------------------------------------
# STEPS VS CALORIES
# ---------------------------------------------------------
st.markdown("---")

st.header("Steps and Calorie Relationship")

fig_steps_calories = px.scatter(
    filtered_df,
    x="TotalSteps",
    y="Calories",
    title="Daily Steps vs Calories Burned",
    trendline="ols",
    hover_data=["Id", "Date"] if "Date" in filtered_df.columns else ["Id"]
)

fig_steps_calories.update_layout(
    xaxis_title="Daily Steps",
    yaxis_title="Calories Burned"
)

st.plotly_chart(
    fig_steps_calories,
    use_container_width=True
)


# ---------------------------------------------------------
# DISTANCE VS STEPS
# ---------------------------------------------------------
st.markdown("---")

st.header("Distance and Steps")

fig_distance_steps = px.scatter(
    filtered_df,
    x="TotalSteps",
    y="TotalDistance",
    title="Daily Steps vs Total Distance",
    hover_data=["Id", "Date"] if "Date" in filtered_df.columns else ["Id"]
)

fig_distance_steps.update_layout(
    xaxis_title="Daily Steps",
    yaxis_title="Total Distance"
)

st.plotly_chart(
    fig_distance_steps,
    use_container_width=True
)


# ---------------------------------------------------------
# SEDENTARY BEHAVIOR
# ---------------------------------------------------------
st.markdown("---")

st.header("Sedentary Behavior")

avg_sedentary_hours = avg_sedentary / 60

st.write(
    f"On average, the selected records contain "
    f"**{avg_sedentary_hours:.1f} hours of sedentary time per day**."
)


if "Date" in filtered_df.columns:

    daily_sedentary = (
        filtered_df
        .groupby("Date", as_index=False)["SedentaryMinutes"]
        .mean()
    )

    fig_sedentary = px.line(
        daily_sedentary,
        x="Date",
        y="SedentaryMinutes",
        title="Average Daily Sedentary Minutes"
    )

    fig_sedentary.update_layout(
        xaxis_title="Date",
        yaxis_title="Sedentary Minutes"
    )

    st.plotly_chart(
        fig_sedentary,
        use_container_width=True
    )


# ---------------------------------------------------------
# USER ACTIVITY COMPARISON
# ---------------------------------------------------------
if "Id" in filtered_df.columns:

    st.markdown("---")

    st.header("User Activity Comparison")

    user_activity = (
        filtered_df
        .groupby("Id", as_index=False)
        .agg(
            AverageSteps=("TotalSteps", "mean"),
            AverageDistance=("TotalDistance", "mean"),
            AverageCalories=("Calories", "mean"),
            AverageSedentaryMinutes=("SedentaryMinutes", "mean")
        )
        .sort_values(
            "AverageSteps",
            ascending=False
        )
    )

    fig_users = px.bar(
        user_activity,
        x="Id",
        y="AverageSteps",
        title="Average Daily Steps by User",
        labels={
            "Id": "User",
            "AverageSteps": "Average Daily Steps"
        }
    )

    st.plotly_chart(
        fig_users,
        use_container_width=True
    )


# ---------------------------------------------------------
# ACTIVITY SUMMARY TABLE
# ---------------------------------------------------------
st.markdown("---")

st.header("Activity Summary")

summary = pd.DataFrame(
    {
        "Metric": [
            "Average Steps",
            "Average Distance",
            "Very Active Minutes",
            "Fairly Active Minutes",
            "Lightly Active Minutes",
            "Sedentary Minutes"
        ],
        "Value": [
            avg_steps,
            avg_distance,
            avg_very_active,
            avg_fairly_active,
            avg_lightly_active,
            avg_sedentary
        ]
    }
)

summary["Value"] = summary["Value"].round(2)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# DOWNLOAD FILTERED DATA
# ---------------------------------------------------------
st.markdown("---")

st.subheader("Download Filtered Activity Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Activity Data",
    data=csv_data,
    file_name="fitbit_activity_filtered.csv",
    mime="text/csv"
)
