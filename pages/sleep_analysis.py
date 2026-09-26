from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# PAGE TITLE
# ---------------------------------------------------------
st.title("Sleep Analysis")
st.caption(
    "Explore sleep duration, time in bed, sleep efficiency, and "
    "relationships between sleep and daily activity."
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
        "Please make sure the file exists at "
        "`data/fitbit_daily_cleaned.csv`."
    )
    st.stop()


# ---------------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------------
st.sidebar.header("Sleep Filters")


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
# SLEEP CALCULATIONS
# ---------------------------------------------------------

avg_sleep_minutes = (
    filtered_df["TotalMinutesAsleep"].mean()
)

avg_sleep_hours = avg_sleep_minutes / 60


avg_time_in_bed = (
    filtered_df["TotalTimeInBed"].mean()
)

avg_time_in_bed_hours = avg_time_in_bed / 60


# Sleep efficiency
if (
    "TotalMinutesAsleep" in filtered_df.columns
    and "TotalTimeInBed" in filtered_df.columns
):

    sleep_efficiency = (
        filtered_df["TotalMinutesAsleep"]
        /
        filtered_df["TotalTimeInBed"]
        * 100
    )

    avg_sleep_efficiency = (
        sleep_efficiency.mean()
    )

else:
    avg_sleep_efficiency = 0


# Sleep records
if "TotalSleepRecords" in filtered_df.columns:

    total_sleep_records = int(
        filtered_df["TotalSleepRecords"].sum()
    )

else:
    total_sleep_records = 0


# ---------------------------------------------------------
# KPI CARDS
# ---------------------------------------------------------
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average Sleep",
        f"{avg_sleep_hours:.1f} hrs"
    )

with col2:
    st.metric(
        "Average Time in Bed",
        f"{avg_time_in_bed_hours:.1f} hrs"
    )

with col3:
    st.metric(
        "Sleep Efficiency",
        f"{avg_sleep_efficiency:.1f}%"
    )

with col4:
    st.metric(
        "Sleep Records",
        f"{total_sleep_records:,}"
    )


# ---------------------------------------------------------
# SLEEP SUMMARY
# ---------------------------------------------------------
st.markdown("---")

st.header("Sleep Summary")

col1, col2 = st.columns(2)

with col1:

    st.subheader("Average Sleep Duration")

    st.write(
        f"""
        The selected records show an average sleep duration
        of **{avg_sleep_hours:.1f} hours per day**.
        """
    )

with col2:

    st.subheader("Average Time in Bed")

    st.write(
        f"""
        The average recorded time in bed is
        **{avg_time_in_bed_hours:.1f} hours per day**.
        """
    )


# ---------------------------------------------------------
# SLEEP DISTRIBUTION
# ---------------------------------------------------------
st.markdown("---")

st.header("Sleep Duration Distribution")

fig_sleep_distribution = px.histogram(
    filtered_df,
    x="TotalMinutesAsleep",
    nbins=30,
    title="Distribution of Daily Sleep Duration",
    labels={
        "TotalMinutesAsleep": "Minutes Asleep"
    }
)

fig_sleep_distribution.update_layout(
    yaxis_title="Number of Records"
)

st.plotly_chart(
    fig_sleep_distribution,
    use_container_width=True
)


# ---------------------------------------------------------
# SLEEP VS TIME IN BED
# ---------------------------------------------------------
st.markdown("---")

st.header("Sleep Duration vs Time in Bed")

fig_sleep_bed = px.scatter(
    filtered_df,
    x="TotalTimeInBed",
    y="TotalMinutesAsleep",
    title="Time in Bed vs Actual Sleep",
    labels={
        "TotalTimeInBed": "Time in Bed (Minutes)",
        "TotalMinutesAsleep": "Sleep Duration (Minutes)"
    },
    hover_data=["Id", "Date"]
)

st.plotly_chart(
    fig_sleep_bed,
    use_container_width=True
)


# ---------------------------------------------------------
# SLEEP EFFICIENCY DISTRIBUTION
# ---------------------------------------------------------
st.markdown("---")

st.header("Sleep Efficiency")

efficiency_df = filtered_df.copy()

efficiency_df["SleepEfficiency"] = (
    efficiency_df["TotalMinutesAsleep"]
    /
    efficiency_df["TotalTimeInBed"]
    * 100
)

efficiency_df["SleepEfficiency"] = (
    efficiency_df["SleepEfficiency"]
    .replace([float("inf"), -float("inf")], pd.NA)
)

fig_efficiency = px.histogram(
    efficiency_df,
    x="SleepEfficiency",
    nbins=30,
    title="Sleep Efficiency Distribution",
    labels={
        "SleepEfficiency": "Sleep Efficiency (%)"
    }
)

st.plotly_chart(
    fig_efficiency,
    use_container_width=True
)


# ---------------------------------------------------------
# SLEEP VS STEPS
# ---------------------------------------------------------
st.markdown("---")

st.header("Sleep and Activity Relationship")

if "TotalSteps" in filtered_df.columns:

    fig_sleep_steps = px.scatter(
        filtered_df,
        x="TotalSteps",
        y="TotalMinutesAsleep",
        title="Daily Steps vs Sleep Duration",
        labels={
            "TotalSteps": "Daily Steps",
            "TotalMinutesAsleep": "Sleep Duration (Minutes)"
        },
        hover_data=["Id", "Date"],
        trendline="ols"
    )

    st.plotly_chart(
        fig_sleep_steps,
        use_container_width=True
    )


# ---------------------------------------------------------
# SLEEP VS CALORIES
# ---------------------------------------------------------
if "Calories" in filtered_df.columns:

    st.markdown("---")

    st.header("Sleep and Calories")

    fig_sleep_calories = px.scatter(
        filtered_df,
        x="TotalMinutesAsleep",
        y="Calories",
        title="Sleep Duration vs Calories Burned",
        labels={
            "TotalMinutesAsleep": "Sleep Duration (Minutes)",
            "Calories": "Calories Burned"
        },
        hover_data=["Id", "Date"]
    )

    st.plotly_chart(
        fig_sleep_calories,
        use_container_width=True
    )


# ---------------------------------------------------------
# DAILY SLEEP TREND
# ---------------------------------------------------------
if "Date" in filtered_df.columns:

    st.markdown("---")

    st.header("Daily Sleep Trend")

    daily_sleep = (
        filtered_df
        .groupby("Date", as_index=False)
        ["TotalMinutesAsleep"]
        .mean()
    )

    fig_sleep_trend = px.line(
        daily_sleep,
        x="Date",
        y="TotalMinutesAsleep",
        title="Average Daily Sleep Duration",
        labels={
            "Date": "Date",
            "TotalMinutesAsleep": "Minutes Asleep"
        }
    )

    st.plotly_chart(
        fig_sleep_trend,
        use_container_width=True
    )


# ---------------------------------------------------------
# USER SLEEP COMPARISON
# ---------------------------------------------------------
if "Id" in filtered_df.columns:

    st.markdown("---")

    st.header("User Sleep Comparison")

    user_sleep = (
        filtered_df
        .groupby("Id", as_index=False)
        .agg(
            AverageSleepMinutes=(
                "TotalMinutesAsleep",
                "mean"
            ),
            AverageTimeInBed=(
                "TotalTimeInBed",
                "mean"
            ),
            AverageSteps=(
                "TotalSteps",
                "mean"
            )
        )
    )

    user_sleep["AverageSleepHours"] = (
        user_sleep["AverageSleepMinutes"] / 60
    )

    user_sleep = user_sleep.sort_values(
        "AverageSleepHours",
        ascending=False
    )

    fig_user_sleep = px.bar(
        user_sleep,
        x="Id",
        y="AverageSleepHours",
        title="Average Sleep Duration by User",
        labels={
            "Id": "User",
            "AverageSleepHours": "Average Sleep (Hours)"
        }
    )

    st.plotly_chart(
        fig_user_sleep,
        use_container_width=True
    )


# ---------------------------------------------------------
# SLEEP DATA AVAILABILITY
# ---------------------------------------------------------
st.markdown("---")

st.header("Sleep Data Availability")

if "HasSleepData" in filtered_df.columns:

    sleep_availability = (
        filtered_df["HasSleepData"]
        .value_counts()
        .reset_index()
    )

    sleep_availability.columns = [
        "HasSleepData",
        "Records"
    ]

    fig_availability = px.pie(
        sleep_availability,
        names="HasSleepData",
        values="Records",
        title="Records With and Without Sleep Data",
        hole=0.45
    )

    st.plotly_chart(
        fig_availability,
        use_container_width=True
    )

else:

    st.info(
        "The HasSleepData field is not available "
        "in the selected dataset."
    )


# ---------------------------------------------------------
# SLEEP SUMMARY TABLE
# ---------------------------------------------------------
st.markdown("---")

st.header("Sleep Summary Table")

summary = pd.DataFrame(
    {
        "Metric": [
            "Average Sleep",
            "Average Time in Bed",
            "Average Sleep Efficiency",
            "Total Sleep Records"
        ],
        "Value": [
            f"{avg_sleep_hours:.2f} hours",
            f"{avg_time_in_bed_hours:.2f} hours",
            f"{avg_sleep_efficiency:.2f}%",
            f"{total_sleep_records:,}"
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

st.subheader("Download Filtered Sleep Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Sleep Data",
    data=csv_data,
    file_name="fitbit_sleep_filtered.csv",
    mime="text/csv"
)
