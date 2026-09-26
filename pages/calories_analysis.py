from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.title("Calories Analysis")
st.caption(
    "Analyze daily calorie expenditure and its relationship with activity, steps, distance, and sedentary behavior."
)


# ---------------------------------------------------------
# Load Data
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
        "Please make sure the file exists at "
        "`data/fitbit_daily_cleaned.csv`."
    )
    st.stop()


# ---------------------------------------------------------
# Required Columns
# ---------------------------------------------------------
required_columns = ["Calories"]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "The following calorie-related columns are missing: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ---------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------
st.sidebar.header("Calories Filters")


# User filter
if "Id" in df.columns:

    users = sorted(df["Id"].dropna().unique())

    selected_users = st.sidebar.multiselect(
        "Select Users",
        options=users,
        default=users
    )

    filtered_df = df[
        df["Id"].isin(selected_users)
    ].copy()

else:

    filtered_df = df.copy()


# Date filter
if "Date" in filtered_df.columns:

    min_date = filtered_df["Date"].min()
    max_date = filtered_df["Date"].max()

    if pd.notna(min_date) and pd.notna(max_date):

        selected_dates = st.sidebar.date_input(
            "Select Date Range",
            value=(
                min_date.date(),
                max_date.date()
            ),
            min_value=min_date.date(),
            max_value=max_date.date()
        )

        if (
            isinstance(selected_dates, tuple)
            and len(selected_dates) == 2
        ):

            start_date, end_date = selected_dates

            filtered_df = filtered_df[
                (filtered_df["Date"].dt.date >= start_date)
                & (filtered_df["Date"].dt.date <= end_date)
            ]


# ---------------------------------------------------------
# Empty Data Check
# ---------------------------------------------------------
if filtered_df.empty:

    st.warning(
        "No records match the selected filters."
    )

    st.stop()


# ---------------------------------------------------------
# Derived Activity Columns
# ---------------------------------------------------------
activity_columns = [
    "VeryActiveMinutes",
    "FairlyActiveMinutes",
    "LightlyActiveMinutes"
]

available_activity_columns = [
    column
    for column in activity_columns
    if column in filtered_df.columns
]

if available_activity_columns:

    filtered_df["TotalActiveMinutes"] = (
        filtered_df[available_activity_columns]
        .sum(axis=1)
    )

else:

    filtered_df["TotalActiveMinutes"] = 0


# ---------------------------------------------------------
# KPI Calculations
# ---------------------------------------------------------
average_calories = filtered_df["Calories"].mean()

total_calories = filtered_df["Calories"].sum()

maximum_calories = filtered_df["Calories"].max()

minimum_calories = filtered_df["Calories"].min()


if "Steps" in filtered_df.columns:
    average_steps = filtered_df["Steps"].mean()
else:
    average_steps = 0


if "Distance" in filtered_df.columns:
    average_distance = filtered_df["Distance"].mean()
else:
    average_distance = 0


if "TotalActiveMinutes" in filtered_df.columns:
    average_active_minutes = filtered_df[
        "TotalActiveMinutes"
    ].mean()
else:
    average_active_minutes = 0


# ---------------------------------------------------------
# KPI Cards
# ---------------------------------------------------------
st.subheader("Calorie Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Daily Calories",
        f"{average_calories:,.0f}"
    )

with col2:
    st.metric(
        "Total Calories",
        f"{total_calories:,.0f}"
    )

with col3:
    st.metric(
        "Highest Daily Calories",
        f"{maximum_calories:,.0f}"
    )

with col4:
    st.metric(
        "Average Active Minutes",
        f"{average_active_minutes:,.1f}"
    )


st.divider()


# ---------------------------------------------------------
# Calories Distribution
# ---------------------------------------------------------
st.subheader("Daily Calorie Distribution")

fig_calories_distribution = px.histogram(
    filtered_df,
    x="Calories",
    nbins=30,
    title="Distribution of Daily Calories",
    labels={
        "Calories": "Calories Burned",
        "count": "Number of Records"
    }
)

fig_calories_distribution.update_layout(
    height=450
)

st.plotly_chart(
    fig_calories_distribution,
    use_container_width=True
)


# ---------------------------------------------------------
# Calories Trend
# ---------------------------------------------------------
if "Date" in filtered_df.columns:

    daily_calories = (
        filtered_df
        .groupby("Date", as_index=False)["Calories"]
        .mean()
    )

    st.subheader("Daily Calorie Trend")

    fig_calorie_trend = px.line(
        daily_calories,
        x="Date",
        y="Calories",
        markers=True,
        title="Average Daily Calorie Expenditure",
        labels={
            "Date": "Date",
            "Calories": "Average Calories"
        }
    )

    fig_calorie_trend.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_calorie_trend,
        use_container_width=True
    )


# ---------------------------------------------------------
# Calories vs Steps
# ---------------------------------------------------------
if "Steps" in filtered_df.columns:

    st.subheader("Calories vs Steps")

    fig_steps_calories = px.scatter(
        filtered_df,
        x="Steps",
        y="Calories",
        trendline="ols",
        title="Relationship Between Steps and Calories",
        labels={
            "Steps": "Daily Steps",
            "Calories": "Calories Burned"
        },
        hover_data=["Id", "Date"] if "Id" in filtered_df.columns else None
    )

    fig_steps_calories.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_steps_calories,
        use_container_width=True
    )


# ---------------------------------------------------------
# Calories vs Distance
# ---------------------------------------------------------
if "Distance" in filtered_df.columns:

    st.subheader("Calories vs Distance")

    fig_distance_calories = px.scatter(
        filtered_df,
        x="Distance",
        y="Calories",
        trendline="ols",
        title="Relationship Between Distance and Calories",
        labels={
            "Distance": "Distance",
            "Calories": "Calories Burned"
        },
        hover_data=["Id", "Date"] if "Id" in filtered_df.columns else None
    )

    fig_distance_calories.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_distance_calories,
        use_container_width=True
    )


# ---------------------------------------------------------
# Calories vs Active Minutes
# ---------------------------------------------------------
st.subheader("Calories vs Active Minutes")

fig_active_calories = px.scatter(
    filtered_df,
    x="TotalActiveMinutes",
    y="Calories",
    trendline="ols",
    title="Relationship Between Active Minutes and Calories",
    labels={
        "TotalActiveMinutes": "Total Active Minutes",
        "Calories": "Calories Burned"
    },
    hover_data=["Id", "Date"] if "Id" in filtered_df.columns else None
)

fig_active_calories.update_layout(
    height=450
)

st.plotly_chart(
    fig_active_calories,
    use_container_width=True
)


# ---------------------------------------------------------
# Calories vs Sedentary Minutes
# ---------------------------------------------------------
if "SedentaryMinutes" in filtered_df.columns:

    st.subheader("Calories vs Sedentary Behavior")

    fig_sedentary_calories = px.scatter(
        filtered_df,
        x="SedentaryMinutes",
        y="Calories",
        trendline="ols",
        title="Relationship Between Sedentary Time and Calories",
        labels={
            "SedentaryMinutes": "Sedentary Minutes",
            "Calories": "Calories Burned"
        },
        hover_data=["Id", "Date"] if "Id" in filtered_df.columns else None
    )

    fig_sedentary_calories.update_layout(
        height=450
    )

    st.plotly_chart(
        fig_sedentary_calories,
        use_container_width=True
    )


# ---------------------------------------------------------
# User Comparison
# ---------------------------------------------------------
if "Id" in filtered_df.columns:

    st.subheader("Average Calories by User")

    user_calories = (
        filtered_df
        .groupby("Id", as_index=False)["Calories"]
        .mean()
        .sort_values("Calories", ascending=False)
    )

    fig_user_calories = px.bar(
        user_calories,
        x="Id",
        y="Calories",
        title="Average Daily Calories by User",
        labels={
            "Id": "User ID",
            "Calories": "Average Calories"
        }
    )

    fig_user_calories.update_layout(
        height=500
    )

    st.plotly_chart(
        fig_user_calories,
        use_container_width=True
    )


# ---------------------------------------------------------
# Activity and Calorie Summary
# ---------------------------------------------------------
st.subheader("Activity and Calorie Summary")

summary_columns = [
    column
    for column in [
        "Calories",
        "Steps",
        "Distance",
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "SedentaryMinutes",
        "TotalActiveMinutes"
    ]
    if column in filtered_df.columns
]

summary_table = (
    filtered_df[summary_columns]
    .describe()
    .T
    .round(2)
)

st.dataframe(
    summary_table,
    use_container_width=True
)


# ---------------------------------------------------------
# Business Insights
# ---------------------------------------------------------
st.subheader("Key Analytical Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:

    st.markdown(
        f"""
        **Calorie Activity**

        - Average daily calorie expenditure: **{average_calories:,.0f} calories**
        - Highest recorded daily expenditure: **{maximum_calories:,.0f} calories**
        - Average daily steps: **{average_steps:,.0f}**
        """
    )

with insight_col2:

    st.markdown(
        f"""
        **Movement Patterns**

        - Average daily distance: **{average_distance:,.2f}**
        - Average active time: **{average_active_minutes:,.1f} minutes**
        - The charts above can be used to examine how activity levels relate to calorie expenditure.
        """
    )


# ---------------------------------------------------------
# Download Filtered Data
# ---------------------------------------------------------
st.subheader("Download Filtered Data")

csv_data = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Calories Analysis Data",
    data=csv_data,
    file_name="fitbit_calories_filtered.csv",
    mime="text/csv"
)
