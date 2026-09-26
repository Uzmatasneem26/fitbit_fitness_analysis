import streamlit as st
import pandas as pd
import sqlite3

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title="SQL Analysis | Strava Fitness Analytics",
    page_icon="🗄️",
    layout="wide"
)

# ============================================================
# FILE PATH
# ============================================================
DATA_PATH = "data/fitbit_daily_cleaned.csv"


# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)

    # Convert date to datetime for analysis
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Make sure boolean fields are stored consistently
    boolean_columns = [
        "HasSleepData",
        "HasWeightData",
        "HasHeartRateData",
        "LikelyDeviceNotWorn"
    ]

    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)

    return df


# ============================================================
# CREATE SQLITE DATABASE
# ============================================================
@st.cache_resource
def create_database(df):
    conn = sqlite3.connect(":memory:", check_same_thread=False)

    # SQLite table used by all SQL queries
    df.to_sql(
        "fitness_daily",
        conn,
        index=False,
        if_exists="replace"
    )

    return conn


try:
    df = load_data()
    conn = create_database(df)

except FileNotFoundError:
    st.error(
        f"Dataset not found at: `{DATA_PATH}`\n\n"
        "Make sure your project contains the CSV inside the `data` folder."
    )
    st.stop()

except Exception as e:
    st.error(f"Unable to load the dataset: {e}")
    st.stop()


# ============================================================
# HEADER
# ============================================================
st.title("🗄️ SQL Analysis")
st.markdown(
    """
    Use SQL to analyze daily fitness, activity, sleep, calorie,
    heart-rate, and user-level patterns from the cleaned Fitbit dataset.
    """
)

st.info(
    "The cleaned CSV is loaded into an in-memory SQLite database. "
    "All analysis on this page is performed using SQL queries."
)


# ============================================================
# DATASET INFORMATION
# ============================================================
with st.expander("📋 Dataset & SQL Table Information"):

    info_col1, info_col2, info_col3, info_col4 = st.columns(4)

    info_col1.metric("Rows", f"{len(df):,}")
    info_col2.metric("Columns", f"{len(df.columns):,}")
    info_col3.metric("Unique Users", f"{df['Id'].nunique():,}")
    info_col4.metric("SQL Table", "fitness_daily")

    st.write("### Columns available in SQL")

    columns_df = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes.astype(str).values
    })

    st.dataframe(
        columns_df,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# KPI OVERVIEW
# ============================================================
st.header("📊 SQL KPI Overview")

overview_query = """
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT Id) AS unique_users,
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(TotalDistance), 2) AS avg_distance,
    ROUND(AVG(Calories), 0) AS avg_calories,
    ROUND(AVG(TotalMinutesAsleep), 1) AS avg_sleep_minutes,
    ROUND(AVG(SedentaryMinutes), 1) AS avg_sedentary_minutes,
    ROUND(AVG(AvgHeartRate), 1) AS avg_heart_rate
FROM fitness_daily;
"""

overview = pd.read_sql_query(overview_query, conn)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Records",
    f"{int(overview.loc[0, 'total_records']):,}"
)

c2.metric(
    "Unique Users",
    f"{int(overview.loc[0, 'unique_users']):,}"
)

c3.metric(
    "Average Steps",
    f"{overview.loc[0, 'avg_steps']:,.0f}"
)

c4.metric(
    "Average Calories",
    f"{overview.loc[0, 'avg_calories']:,.0f}"
)

c5, c6, c7, c8 = st.columns(4)

c5.metric(
    "Avg Distance",
    f"{overview.loc[0, 'avg_distance']:.2f} km"
)

c6.metric(
    "Avg Sleep",
    f"{overview.loc[0, 'avg_sleep_minutes']:.1f} min"
)

c7.metric(
    "Avg Sedentary Time",
    f"{overview.loc[0, 'avg_sedentary_minutes']:.1f} min"
)

c8.metric(
    "Avg Heart Rate",
    f"{overview.loc[0, 'avg_heart_rate']:.1f} bpm"
)


# ============================================================
# SQL ACTIVITY LEVEL ANALYSIS
# ============================================================
st.header("🏃 Activity Level Analysis")

activity_query = """
SELECT
    CASE
        WHEN TotalSteps < 5000 THEN 'Sedentary'
        WHEN TotalSteps < 10000 THEN 'Moderately Active'
        ELSE 'Highly Active'
    END AS activity_level,

    COUNT(*) AS days,

    ROUND(AVG(TotalSteps), 0) AS avg_steps,

    ROUND(AVG(TotalDistance), 2) AS avg_distance,

    ROUND(AVG(Calories), 0) AS avg_calories,

    ROUND(AVG(TotalMinutesAsleep), 1) AS avg_sleep

FROM fitness_daily

GROUP BY activity_level

ORDER BY
    CASE activity_level
        WHEN 'Sedentary' THEN 1
        WHEN 'Moderately Active' THEN 2
        WHEN 'Highly Active' THEN 3
    END;
"""

activity_result = pd.read_sql_query(activity_query, conn)

st.dataframe(
    activity_result,
    use_container_width=True,
    hide_index=True
)

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.write("**Average Steps by Activity Level**")
    st.bar_chart(
        activity_result.set_index("activity_level")["avg_steps"]
    )

with chart_col2:
    st.write("**Average Calories by Activity Level**")
    st.bar_chart(
        activity_result.set_index("activity_level")["avg_calories"]
    )


# ============================================================
# USER-LEVEL ANALYSIS
# ============================================================
st.header("👤 User-Level Analysis")

user_query = """
SELECT
    Id,

    COUNT(*) AS tracked_days,

    ROUND(AVG(TotalSteps), 0) AS avg_steps,

    ROUND(AVG(TotalDistance), 2) AS avg_distance,

    ROUND(AVG(Calories), 0) AS avg_calories,

    ROUND(AVG(TotalMinutesAsleep), 1) AS avg_sleep,

    ROUND(AVG(SedentaryMinutes), 1) AS avg_sedentary_minutes

FROM fitness_daily

GROUP BY Id

ORDER BY avg_steps DESC;
"""

user_result = pd.read_sql_query(user_query, conn)

st.dataframe(
    user_result,
    use_container_width=True,
    hide_index=True
)

st.write("**Top 10 Users by Average Steps**")

top_users = user_result.head(10).copy()

st.bar_chart(
    top_users.set_index("Id")["avg_steps"]
)


# ============================================================
# DAY-OF-WEEK ANALYSIS
# ============================================================
st.header("📅 Weekly Activity Pattern")

weekday_query = """
SELECT

    CASE CAST(strftime('%w', Date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_name,

    ROUND(AVG(TotalSteps), 0) AS avg_steps,

    ROUND(AVG(Calories), 0) AS avg_calories,

    ROUND(AVG(TotalDistance), 2) AS avg_distance,

    ROUND(AVG(TotalMinutesAsleep), 1) AS avg_sleep

FROM fitness_daily

GROUP BY strftime('%w', Date)

ORDER BY CAST(strftime('%w', Date) AS INTEGER);
"""

weekday_result = pd.read_sql_query(weekday_query, conn)

st.dataframe(
    weekday_result,
    use_container_width=True,
    hide_index=True
)

weekday_chart_col1, weekday_chart_col2 = st.columns(2)

with weekday_chart_col1:
    st.write("**Average Steps by Day**")
    st.line_chart(
        weekday_result.set_index("day_name")["avg_steps"]
    )

with weekday_chart_col2:
    st.write("**Average Calories by Day**")
    st.line_chart(
        weekday_result.set_index("day_name")["avg_calories"]
    )


# ============================================================
# SLEEP ANALYSIS
# ============================================================
st.header("😴 Sleep Analysis")

sleep_query = """
SELECT

    CASE
        WHEN TotalMinutesAsleep < 360 THEN '<6 hours'
        WHEN TotalMinutesAsleep < 480 THEN '6–8 hours'
        ELSE '8+ hours'
    END AS sleep_group,

    COUNT(*) AS days,

    ROUND(AVG(TotalMinutesAsleep), 1) AS avg_sleep_minutes,

    ROUND(AVG(TotalSteps), 0) AS avg_steps,

    ROUND(AVG(Calories), 0) AS avg_calories,

    ROUND(AVG(TotalTimeInBed), 1) AS avg_time_in_bed

FROM fitness_daily

WHERE HasSleepData = 1

GROUP BY sleep_group

ORDER BY
    CASE sleep_group
        WHEN '<6 hours' THEN 1
        WHEN '6–8 hours' THEN 2
        WHEN '8+ hours' THEN 3
    END;
"""

sleep_result = pd.read_sql_query(sleep_query, conn)

st.dataframe(
    sleep_result,
    use_container_width=True,
    hide_index=True
)

sleep_col1, sleep_col2 = st.columns(2)

with sleep_col1:
    st.write("**Average Steps by Sleep Group**")
    st.bar_chart(
        sleep_result.set_index("sleep_group")["avg_steps"]
    )

with sleep_col2:
    st.write("**Average Calories by Sleep Group**")
    st.bar_chart(
        sleep_result.set_index("sleep_group")["avg_calories"]
    )


# ============================================================
# ACTIVITY INTENSITY ANALYSIS
# ============================================================
st.header("⚡ Activity Intensity Analysis")

intensity_query = """
SELECT

    ROUND(AVG(VeryActiveMinutes), 1)
        AS avg_very_active_minutes,

    ROUND(AVG(FairlyActiveMinutes), 1)
        AS avg_fairly_active_minutes,

    ROUND(AVG(LightlyActiveMinutes), 1)
        AS avg_lightly_active_minutes,

    ROUND(AVG(SedentaryMinutes), 1)
        AS avg_sedentary_minutes

FROM fitness_daily;
"""

intensity_result = pd.read_sql_query(intensity_query, conn)

st.dataframe(
    intensity_result,
    use_container_width=True,
    hide_index=True
)

intensity_chart = pd.DataFrame({
    "Activity Type": [
        "Very Active",
        "Fairly Active",
        "Lightly Active",
        "Sedentary"
    ],
    "Average Minutes": [
        intensity_result.loc[0, "avg_very_active_minutes"],
        intensity_result.loc[0, "avg_fairly_active_minutes"],
        intensity_result.loc[0, "avg_lightly_active_minutes"],
        intensity_result.loc[0, "avg_sedentary_minutes"]
    ]
})

st.bar_chart(
    intensity_chart.set_index("Activity Type")
)


# ============================================================
# HEART RATE ANALYSIS
# ============================================================
st.header("❤️ Heart Rate Analysis")

heart_rate_query = """
SELECT
    ROUND(AVG(AvgHeartRate), 1) AS avg_heart_rate,
    ROUND(AVG(MinHeartRate), 1) AS avg_min_heart_rate,
    ROUND(AVG(MaxHeartRate), 1) AS avg_max_heart_rate,
    COUNT(*) AS records_with_heart_rate
FROM fitness_daily
WHERE HasHeartRateData = 1
AND AvgHeartRate IS NOT NULL;
"""

heart_rate_result = pd.read_sql_query(
    heart_rate_query,
    conn
)

st.dataframe(
    heart_rate_result,
    use_container_width=True,
    hide_index=True
)

st.caption(
    "Heart-rate statistics are calculated only for records where "
    "heart-rate data is available."
)


# ============================================================
# DEVICE USAGE / DATA QUALITY ANALYSIS
# ============================================================
st.header("📱 Device Usage & Data Quality")

device_query = """
SELECT
    COUNT(*) AS total_records,

    SUM(CASE
        WHEN HasSleepData = 1 THEN 1
        ELSE 0
    END) AS records_with_sleep,

    SUM(CASE
        WHEN HasWeightData = 1 THEN 1
        ELSE 0
    END) AS records_with_weight,

    SUM(CASE
        WHEN HasHeartRateData = 1 THEN 1
        ELSE 0
    END) AS records_with_heart_rate,

    SUM(CASE
        WHEN LikelyDeviceNotWorn = 1 THEN 1
        ELSE 0
    END) AS likely_device_not_worn

FROM fitness_daily;
"""

device_result = pd.read_sql_query(
    device_query,
    conn
)

st.dataframe(
    device_result,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# HIGHEST CALORIE DAYS
# ============================================================
st.header("🔥 Highest Calorie-Burn Days")

calorie_query = """
SELECT
    Id,
    Date,
    TotalSteps,
    TotalDistance,
    VeryActiveMinutes,
    FairlyActiveMinutes,
    Calories
FROM fitness_daily
ORDER BY Calories DESC
LIMIT 20;
"""

calorie_result = pd.read_sql_query(
    calorie_query,
    conn
)

calorie_result["Date"] = pd.to_datetime(
    calorie_result["Date"]
).dt.strftime("%Y-%m-%d")

st.dataframe(
    calorie_result,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# MOST ACTIVE DAYS
# ============================================================
st.header("🏆 Most Active Days")

most_active_query = """
SELECT
    Id,
    Date,
    TotalSteps,
    TotalDistance,
    VeryActiveMinutes,
    FairlyActiveMinutes,
    LightlyActiveMinutes,
    Calories
FROM fitness_daily
ORDER BY TotalSteps DESC
LIMIT 20;
"""

most_active_result = pd.read_sql_query(
    most_active_query,
    conn
)

most_active_result["Date"] = pd.to_datetime(
    most_active_result["Date"]
).dt.strftime("%Y-%m-%d")

st.dataframe(
    most_active_result,
    use_container_width=True,
    hide_index=True
)


# ============================================================
# INTERACTIVE SQL QUERY
# ============================================================
st.header("💻 Interactive SQL Query")

st.write(
    "Select a predefined query to view the SQL statement and execute it "
    "against the `fitness_daily` SQLite table."
)

queries = {

    "Daily Activity Summary": """
SELECT
    Date,
    TotalSteps,
    TotalDistance,
    Calories,
    VeryActiveMinutes,
    FairlyActiveMinutes,
    LightlyActiveMinutes,
    SedentaryMinutes
FROM fitness_daily
ORDER BY Date;
""",

    "Top 10 Users by Average Steps": """
SELECT
    Id,
    COUNT(*) AS tracked_days,
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(Calories), 0) AS avg_calories
FROM fitness_daily
GROUP BY Id
ORDER BY avg_steps DESC
LIMIT 10;
""",

    "Highest Calorie Days": """
SELECT
    Id,
    Date,
    TotalSteps,
    TotalDistance,
    Calories
FROM fitness_daily
ORDER BY Calories DESC
LIMIT 20;
""",

    "Most Active Days": """
SELECT
    Id,
    Date,
    TotalSteps,
    VeryActiveMinutes,
    FairlyActiveMinutes,
    Calories
FROM fitness_daily
ORDER BY TotalSteps DESC
LIMIT 20;
""",

    "Sleep Analysis": """
SELECT
    Id,
    Date,
    TotalMinutesAsleep,
    TotalTimeInBed,
    TotalSteps,
    Calories
FROM fitness_daily
WHERE HasSleepData = 1
ORDER BY TotalMinutesAsleep DESC;
""",

    "Average Activity by User": """
SELECT
    Id,
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(TotalDistance), 2) AS avg_distance,
    ROUND(AVG(VeryActiveMinutes), 1) AS avg_very_active_minutes,
    ROUND(AVG(LightlyActiveMinutes), 1) AS avg_lightly_active_minutes,
    ROUND(AVG(SedentaryMinutes), 1) AS avg_sedentary_minutes
FROM fitness_daily
GROUP BY Id
ORDER BY avg_steps DESC;
""",

    "Sleep vs Calories": """
SELECT
    CASE
        WHEN TotalMinutesAsleep < 360 THEN '<6 hours'
        WHEN TotalMinutesAsleep < 480 THEN '6–8 hours'
        ELSE '8+ hours'
    END AS sleep_group,
    COUNT(*) AS records,
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(Calories), 0) AS avg_calories
FROM fitness_daily
WHERE HasSleepData = 1
GROUP BY sleep_group
ORDER BY avg_calories DESC;
""",

    "Heart Rate Summary": """
SELECT
    ROUND(AVG(AvgHeartRate), 1) AS avg_heart_rate,
    ROUND(AVG(MinHeartRate), 1) AS avg_min_heart_rate,
    ROUND(AVG(MaxHeartRate), 1) AS avg_max_heart_rate,
    COUNT(*) AS records
FROM fitness_daily
WHERE HasHeartRateData = 1
AND AvgHeartRate IS NOT NULL;
""",

    "Data Quality Check": """
SELECT
    COUNT(*) AS total_records,

    SUM(CASE
        WHEN HasSleepData = 1 THEN 1
        ELSE 0
    END) AS sleep_records,

    SUM(CASE
        WHEN HasWeightData = 1 THEN 1
        ELSE 0
    END) AS weight_records,

    SUM(CASE
        WHEN HasHeartRateData = 1 THEN 1
        ELSE 0
    END) AS heart_rate_records,

    SUM(CASE
        WHEN LikelyDeviceNotWorn = 1 THEN 1
        ELSE 0
    END) AS likely_device_not_worn

FROM fitness_daily;
"""
}

selected_query = st.selectbox(
    "Choose a SQL analysis",
    list(queries.keys())
)

st.code(
    queries[selected_query],
    language="sql"
)

if st.button("▶ Run SQL Query", type="primary"):

    try:
        result = pd.read_sql_query(
            queries[selected_query],
            conn
        )

        st.success(
            f"Query executed successfully — {len(result):,} rows returned."
        )

        st.dataframe(
            result,
            use_container_width=True,
            hide_index=True
        )

        csv_data = result.to_csv(index=False)

        st.download_button(
            label="⬇️ Download SQL Results as CSV",
            data=csv_data,
            file_name="sql_analysis_result.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"SQL Error: {e}")


# ============================================================
# CUSTOM SQL QUERY
# ============================================================
st.header("⌨️ Custom SQL Query")

st.caption(
    "You can write your own SELECT query using the "
    "`fitness_daily` table."
)

custom_sql = st.text_area(
    "Enter SQL query",
    value="""SELECT
    Id,
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(Calories), 0) AS avg_calories
FROM fitness_daily
GROUP BY Id
ORDER BY avg_steps DESC
LIMIT 10;""",
    height=180
)

if st.button("Run Custom Query"):

    query_upper = custom_sql.strip().upper()

    # Allow read-only queries only
    if not (
        query_upper.startswith("SELECT")
        or query_upper.startswith("WITH")
    ):
        st.error(
            "For safety, only SELECT and WITH queries are allowed."
        )

    else:
        try:
            custom_result = pd.read_sql_query(
                custom_sql,
                conn
            )

            st.success(
                f"Query executed successfully — "
                f"{len(custom_result):,} rows returned."
            )

            st.dataframe(
                custom_result,
                use_container_width=True,
                hide_index=True
            )

            custom_csv = custom_result.to_csv(
                index=False
            )

            st.download_button(
                label="⬇️ Download Custom Query Results",
                data=custom_csv,
                file_name="custom_sql_results.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"SQL Error: {e}")


# ============================================================
# KEY SQL INSIGHTS
# ============================================================
st.header("💡 SQL Analysis Insights")

insight_query = """
SELECT
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(Calories), 0) AS avg_calories,
    ROUND(AVG(TotalMinutesAsleep), 1) AS avg_sleep,
    ROUND(AVG(SedentaryMinutes), 1) AS avg_sedentary,
    ROUND(AVG(VeryActiveMinutes), 1) AS avg_very_active
FROM fitness_daily;
"""

insights = pd.read_sql_query(
    insight_query,
    conn
)

st.markdown(
    f"""
    - **Average daily steps:** {insights.loc[0, 'avg_steps']:,.0f}
    - **Average daily calories:** {insights.loc[0, 'avg_calories']:,.0f}
    - **Average sleep:** {insights.loc[0, 'avg_sleep']:.1f} minutes
    - **Average sedentary time:** {insights.loc[0, 'avg_sedentary']:.1f} minutes
    - **Average very active time:** {insights.loc[0, 'avg_very_active']:.1f} minutes
    """
)

st.caption(
    "These are descriptive observations from the available Fitbit records. "
    "They describe patterns in the dataset and should not be interpreted "
    "as causal relationships."
)


# ============================================================
# FOOTER
# ============================================================
st.divider()

st.caption(
    "STRAVA Fitness Analytics | SQL Analysis | "
    "SQLite + Pandas + Streamlit"
)
