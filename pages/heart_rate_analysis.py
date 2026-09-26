from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------
st.title("Heart Rate Analysis")
st.caption(
    "Explore average, minimum, and maximum heart-rate patterns "
    "and their relationship with activity and calories."
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
        df["Date"] = pd.to_datetime(
            df["Date"],
            errors="coerce"
        )

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
# CHECK HEART RATE COLUMNS
# ---------------------------------------------------------
required_columns = [
    "AvgHeartRate",
    "MinHeartRate",
    "MaxHeartRate"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "The following heart-rate columns are missing: "
        + ", ".join(missing_columns)
    )
    st.stop()


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("Heart Rate Filters")


# User filter
if "Id" in df.columns:

    users = sorted(
        df["Id"].dropna().unique()
    )

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
                (
                    filtered_df["Date"].dt.date
                    >= start_date
                )
                &
                (
                    filtered_df["Date"].dt.date
                    <= end_date
                )
            ]


# ---------------------------------------------------------
# EMPTY DATA CHECK
# ---------------------------------------------------------
if filtered_df.empty:
    st.warning(
        "No records match the selected filters."
    )
    st.stop()


# ---------------------------------------------------------
# HEART RATE CALCULATIONS
# ---------------------------------------------------------
avg_heart_rate = (
    filtered_df["AvgHeartRate"].mean()
)

min_heart_rate = (
    filtered_df["MinHeartRate"].mean()
)

max_heart_rate = (
    filtered_df["MaxHeartRate"].mean()
)


heart_rate_range = (
    max_heart_rate - min_heart_rate
)


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Heart Rate",
        f"{avg_heart_rate:.0f} bpm"
    )

with col2:
    st.metric(
        "Average Minimum",
        f"{min_heart_rate:.0f} bpm"
    )

with col3:
    st.metric(
        "Average Maximum",
        f"{max_heart_rate:.0f} bpm"
    )

with col4:
    st.metric(
        "Average HR Range",
        f"{heart_rate_range:.0f} bpm"
    )


# ---------------------------------------------------------
# HEART RATE DISTRIBUTION
# ---------------------------------------------------------
st.markdown("---")

st.header("Heart Rate Distribution")

fig_distribution = px.histogram(
    filtered_df,
    x="AvgHeartRate",
    nbins=30,
    title="Distribution of Average Heart Rate",
    labels={
        "AvgHeartRate": "Average Heart Rate (bpm)"
    }
)

fig_distribution.update_layout(
    yaxis_title="Number of Records"
)

st.plotly_chart(
    fig_distribution,
    use_container_width=True
)


# ---------------------------------------------------------
# MIN / AVG / MAX HEART RATE
# ---------------------------------------------------------
st.markdown("---")

st.header("Heart Rate Range")

heart_rate_summary = pd.DataFrame(
    {
        "Metric": [
            "Average Minimum Heart Rate",
            "Average Heart Rate",
            "Average Maximum Heart Rate"
        ],
        "BPM": [
            min_heart_rate,
            avg_heart_rate,
            max_heart_rate
        ]
    }
)

fig_range = px.bar(
    heart_rate_summary,
    x="Metric",
    y="BPM",
    title="Average Heart Rate Range",
    text_auto=".0f"
)

fig_range.update_layout(
    xaxis_title="Metric",
    yaxis_title="Heart Rate (bpm)",
    showlegend=False
)

st.plotly_chart(
    fig_range,
    use_container_width=True
)


# ---------------------------------------------------------
# HEART RATE TREND
# ---------------------------------------------------------
if "Date" in filtered_df.columns:

    st.markdown("---")

    st.header("Daily Heart Rate Trend")

    daily_hr = (
        filtered_df
        .groupby("Date", as_index=False)
        .agg(
            AverageHeartRate=(
                "AvgHeartRate",
                "mean"
            ),
            MinimumHeartRate=(
                "MinHeartRate",
                "mean"
            ),
            MaximumHeartRate=(
                "MaxHeartRate",
                "mean"
            )
        )
    )

    fig_trend = px.line(
        daily_hr,
        x="Date",
        y=[
            "AverageHeartRate",
            "MinimumHeartRate",
            "MaximumHeartRate"
        ],
        title="Daily Heart Rate Trends",
        labels={
            "value": "Heart Rate (bpm)",
            "variable": "Heart Rate Metric"
        }
    )

    st.plotly_chart(
        fig_trend,
        use_container_width=True
    )


# ---------------------------------------------------------
# HEART RATE VS STEPS
# ---------------------------------------------------------
if "TotalSteps" in filtered_df.columns:

    st.markdown("---")

    st.header("Heart Rate and Activity")

    fig_steps = px.scatter(
        filtered_df,
        x="TotalSteps",
        y="AvgHeartRate",
        title="Daily Steps vs Average Heart Rate",
        labels={
            "TotalSteps": "Daily Steps",
            "AvgHeartRate": "Average Heart Rate (bpm)"
        },
        hover_data=(
            ["Id", "Date"]
            if "Date" in filtered_df.columns
            else ["Id"]
        ),
        trendline="ols"
    )

    st.plotly_chart(
        fig_steps,
        use_container_width=True
    )


# ---------------------------------------------------------
# HEART RATE VS CALORIES
# ---------------------------------------------------------
if "Calories" in filtered_df.columns:

    st.markdown("---")

    st.header("Heart Rate and Calories")

    fig_calories = px.scatter(
        filtered_df,
        x="AvgHeartRate",
        y="Calories",
        title="Average Heart Rate vs Calories Burned",
        labels={
            "AvgHeartRate": "Average Heart Rate (bpm)",
            "Calories": "Calories Burned"
        },
        hover_data=(
            ["Id", "Date"]
            if "Date" in filtered_df.columns
            else ["Id"]
        ),
        trendline="ols"
    )

    st.plotly_chart(
        fig_calories,
        use_container_width=True
    )


# ---------------------------------------------------------
# HEART RATE VS ACTIVE MINUTES
# ---------------------------------------------------------
if "VeryActiveMinutes" in filtered_df.columns:

    active_columns = [
        "VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes"
    ]

    available_active_columns = [
        column
        for column in active_columns
        if column in filtered_df.columns
    ]

    if available_active_columns:

        filtered_df["TotalActiveMinutes"] = (
            filtered_df[
                available_active_columns
            ].sum(axis=1)
        )

        st.markdown("---")

        st.header("Heart Rate and Active Minutes")

        fig_active = px.scatter(
            filtered_df,
            x="TotalActiveMinutes",
            y="AvgHeartRate",
            title="Active Minutes vs Average Heart Rate",
            labels={
                "TotalActiveMinutes": "Total Active Minutes",
                "AvgHeartRate": "Average Heart Rate (bpm)"
            },
            hover_data=(
                ["Id", "Date"]
                if "Date" in filtered_df.columns
                else ["Id"]
            ),
            trendline="ols"
        )

        st.plotly_chart(
            fig_active,
            use_container_width=True
        )


# ---------------------------------------------------------
# USER COMPARISON
# ---------------------------------------------------------
if "Id" in filtered_df.columns:

    st.markdown("---")

    st.header("Heart Rate by User")

    user_hr = (
        filtered_df
        .groupby("Id", as_index=False)
        .agg(
            AverageHeartRate=(
                "AvgHeartRate",
                "mean"
            ),
            MinimumHeartRate=(
                "MinHeartRate",
                "mean"
            ),
            MaximumHeartRate=(
                "MaxHeartRate",
                "mean"
            )
        )
        .sort_values(
            "AverageHeartRate",
            ascending=False
        )
    )

    fig_user_hr = px.bar(
        user_hr,
        x="Id",
        y="AverageHeartRate",
        title="Average Heart Rate by User",
        labels={
            "Id": "User",
            "AverageHeartRate": "Average Heart Rate (bpm)"
        }
    )

    st.plotly_chart(
        fig_user_hr,
        use_container_width=True
    )


# ---------------------------------------------------------
# HEART RATE DATA AVAILABILITY
# ---------------------------------------------------------
if "HasHeartRateData" in filtered_df.columns:

    st.markdown("---")

    st.header("Heart Rate Data Availability")

    availability = (
        filtered_df["HasHeartRateData"]
        .value_counts()
        .reset_index()
    )

    availability.columns = [
        "HasHeartRateData",
        "Records"
    ]

    fig_availability = px.pie(
        availability,
        names="HasHeartRateData",
        values="Records",
        title="Records With and Without Heart Rate Data",
        hole=0.45
    )

    st.plotly_chart(
        fig_availability,
        use_container_width=True
    )


# ---------------------------------------------------------
# HEART RATE SUMMARY
# ---------------------------------------------------------
st.markdown("---")

st.header("Heart Rate Summary")

summary = pd.DataFrame(
    {
        "Metric": [
            "Average Heart Rate",
            "Average Minimum Heart Rate",
            "Average Maximum Heart Rate",
            "Average Heart Rate Range"
        ],
        "Value": [
            f"{avg_heart_rate:.2f} bpm",
            f"{min_heart_rate:.2f} bpm",
            f"{max_heart_rate:.2f} bpm",
            f"{heart_rate_range:.2f} bpm"
        ]
    }
)

st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# DOWNLOAD FILTERED DATA
# ---------------------------------------------------------
st.markdown("---")

st.subheader("Download Filtered Heart Rate Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Heart Rate Data",
    data=csv_data,
    file_name="fitbit_heart_rate_filtered.csv",
    mime="text/csv"
)
