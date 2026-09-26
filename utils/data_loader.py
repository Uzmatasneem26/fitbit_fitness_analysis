"""
Data Explorer — raw data browser + SQL analysis layer.

This page loads fitbit_daily_cleaned.csv into an in-memory SQLite database
(table name: daily_activity) and gives the user three ways to look at it:
  1. Raw Data        - filter / browse / download the table
  2. Cleaning & QA    - the integrity-check SQL queries (nulls, negative
                        values, full-day-sedentary / device-not-worn rows,
                        duplicate id+date rows, per-participant row counts)
  3. SQL Query Runner - a free-form SQL box against the same table
  4. Prebuilt Insights - a handful of canned analysis queries + charts
"""

import sqlite3
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "fitbit_daily_cleaned.csv"
TABLE_NAME = "daily_activity"


# ---------------------------------------------------------
# DATA LOADING
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_dataframe() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["Date"])
    return df


@st.cache_resource(show_spinner=False)
def get_connection() -> sqlite3.Connection:
    """One shared in-memory SQLite DB for the life of the session."""
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    df = load_dataframe()
    # SQLite has no native datetime type - store as ISO text (YYYY-MM-DD),
    # which still sorts/compares correctly and works with strftime().
    df_to_load = df.copy()
    df_to_load["Date"] = df_to_load["Date"].dt.strftime("%Y-%m-%d")
    df_to_load.to_sql(TABLE_NAME, conn, index=False, if_exists="replace")
    return conn


def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql_query(sql, conn)


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------
st.title("Data Explorer")
st.caption(
    "Fitbit daily-activity dataset (33 participants, 2016-04-12 to 2016-05-12) "
    "— browse the raw table or run SQL directly against it."
)

df_full = load_dataframe()

if not DATA_PATH.exists():
    st.error(
        f"Couldn't find the data file at `{DATA_PATH}`. "
        "Make sure `fitbit_daily_cleaned.csv` is in a `data/` folder at the "
        "project root (next to `app.py`)."
    )
    st.stop()

tab_raw, tab_qa, tab_sql, tab_insights = st.tabs(
    ["📋 Raw Data", "🧹 Cleaning & QA", "🔍 SQL Query Runner", "📊 Prebuilt Insights"]
)


# ---------------------------------------------------------
# TAB 1 — RAW DATA
# ---------------------------------------------------------
with tab_raw:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Participants", df_full["Id"].nunique())
    col2.metric("Total records", len(df_full))
    col3.metric("Date range", f"{df_full['Date'].min():%b %d} – {df_full['Date'].max():%b %d}")
    col4.metric("Columns", df_full.shape[1])

    st.divider()

    filt_col1, filt_col2 = st.columns([1, 2])
    with filt_col1:
        ids = sorted(df_full["Id"].unique())
        selected_ids = st.multiselect("Filter by participant Id", ids, default=[])
    with filt_col2:
        date_range = st.date_input(
            "Filter by date range",
            value=(df_full["Date"].min().date(), df_full["Date"].max().date()),
            min_value=df_full["Date"].min().date(),
            max_value=df_full["Date"].max().date(),
        )

    filtered = df_full.copy()
    if selected_ids:
        filtered = filtered[filtered["Id"].isin(selected_ids)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[
            (filtered["Date"].dt.date >= start) & (filtered["Date"].dt.date <= end)
        ]

    st.dataframe(filtered, use_container_width=True, height=420)
    st.download_button(
        "Download filtered data as CSV",
        filtered.to_csv(index=False).encode("utf-8"),
        file_name="fitbit_filtered.csv",
        mime="text/csv",
    )


# ---------------------------------------------------------
# TAB 2 — CLEANING & QA (the SQL from the case-study deck)
# ---------------------------------------------------------
with tab_qa:
    st.markdown(
        "These mirror the integrity checks used to clean the dataset "
        "(null checks, negative-value checks, full-day-sedentary / "
        "device-not-worn detection, duplicates, and per-participant coverage)."
    )

    checks = [
        (
            "Null check on key metrics",
            f"""SELECT
    SUM(CASE WHEN TotalSteps IS NULL THEN 1 ELSE 0 END) AS null_steps,
    SUM(CASE WHEN TotalDistance IS NULL THEN 1 ELSE 0 END) AS null_distance,
    SUM(CASE WHEN Calories IS NULL THEN 1 ELSE 0 END) AS null_calories,
    SUM(CASE WHEN SedentaryMinutes IS NULL THEN 1 ELSE 0 END) AS null_sedentary
FROM {TABLE_NAME};""",
        ),
        (
            "Negative / out-of-range value check",
            f"""SELECT
    MIN(TotalDistance) AS min_distance, MAX(TotalDistance) AS max_distance,
    MIN(TotalSteps) AS min_steps, MAX(TotalSteps) AS max_steps,
    MIN(SedentaryMinutes) AS min_sedentary, MAX(SedentaryMinutes) AS max_sedentary,
    MIN(Calories) AS min_calories, MAX(Calories) AS max_calories
FROM {TABLE_NAME};""",
        ),
        (
            "Full-day sedentary rows (SedentaryMinutes >= 1440 → device likely not worn)",
            f"""SELECT Id, Date, SedentaryMinutes, LikelyDeviceNotWorn
FROM {TABLE_NAME}
WHERE SedentaryMinutes >= 1440
ORDER BY Id, Date;""",
        ),
        (
            "Duplicate Id + Date rows (should be zero)",
            f"""SELECT Id, Date, COUNT(*) AS n
FROM {TABLE_NAME}
GROUP BY Id, Date
HAVING COUNT(*) > 1;""",
        ),
        (
            "Per-participant record coverage (not everyone logged the full period)",
            f"""SELECT Id,
    COUNT(*) AS days_logged,
    SUM(CASE WHEN HasSleepData = 1 THEN 1 ELSE 0 END) AS days_with_sleep,
    SUM(CASE WHEN HasHeartRateData = 1 THEN 1 ELSE 0 END) AS days_with_hr,
    SUM(CASE WHEN HasWeightData = 1 THEN 1 ELSE 0 END) AS days_with_weight,
    SUM(CASE WHEN LikelyDeviceNotWorn = 1 THEN 1 ELSE 0 END) AS days_device_not_worn
FROM {TABLE_NAME}
GROUP BY Id
ORDER BY days_logged DESC;""",
        ),
    ]

    for title, sql in checks:
        with st.expander(title, expanded=False):
            st.code(sql, language="sql")
            result = run_query(sql)
            st.dataframe(result, use_container_width=True)
            if "Duplicate" in title:
                if result.empty:
                    st.success("No duplicate Id + Date rows found.")
                else:
                    st.warning(f"{len(result)} duplicate Id + Date combinations found.")


# ---------------------------------------------------------
# TAB 3 — FREE-FORM SQL QUERY RUNNER
# ---------------------------------------------------------
with tab_sql:
    st.markdown(
        f"Write any `SELECT` statement against the **`{TABLE_NAME}`** table. "
        "Available columns:"
    )
    st.code(", ".join(df_full.columns), language="text")

    example_queries = {
        "— choose an example —": "",
        "Average steps by participant": (
            f"SELECT Id, ROUND(AVG(TotalSteps), 0) AS avg_steps\n"
            f"FROM {TABLE_NAME}\nGROUP BY Id\nORDER BY avg_steps DESC;"
        ),
        "Average steps by day of week": (
            f"SELECT CASE CAST(strftime('%w', Date) AS INTEGER)\n"
            f"    WHEN 0 THEN 'Sunday' WHEN 1 THEN 'Monday' WHEN 2 THEN 'Tuesday'\n"
            f"    WHEN 3 THEN 'Wednesday' WHEN 4 THEN 'Thursday' WHEN 5 THEN 'Friday'\n"
            f"    WHEN 6 THEN 'Saturday' END AS weekday,\n"
            f"    ROUND(AVG(TotalSteps), 0) AS avg_steps\n"
            f"FROM {TABLE_NAME}\nGROUP BY weekday\nORDER BY MIN(strftime('%w', Date));"
        ),
        "Sleep vs. sedentary minutes": (
            f"SELECT Id, Date, TotalMinutesAsleep, SedentaryMinutes\n"
            f"FROM {TABLE_NAME}\nWHERE HasSleepData = 1\nORDER BY Id, Date;"
        ),
        "Rows where device likely wasn't worn": (
            f"SELECT * FROM {TABLE_NAME}\nWHERE LikelyDeviceNotWorn = 1;"
        ),
    }
    choice = st.selectbox("Load an example query (optional)", list(example_queries.keys()))
    default_sql = example_queries[choice] or f"SELECT * FROM {TABLE_NAME} LIMIT 20;"

    sql_input = st.text_area("SQL query", value=default_sql, height=160)

    if st.button("▶ Run query", type="primary"):
        try:
            result = run_query(sql_input)
            st.success(f"{len(result)} row(s) returned.")
            st.dataframe(result, use_container_width=True)
            st.download_button(
                "Download results as CSV",
                result.to_csv(index=False).encode("utf-8"),
                file_name="query_results.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Query failed: {e}")


# ---------------------------------------------------------
# TAB 4 — PREBUILT INSIGHT QUERIES + CHARTS
# ---------------------------------------------------------
with tab_insights:
    st.subheader("Average steps by day of week")
    steps_by_weekday_sql = f"""
        SELECT
            CASE CAST(strftime('%w', Date) AS INTEGER)
                WHEN 0 THEN '0-Sunday' WHEN 1 THEN '1-Monday' WHEN 2 THEN '2-Tuesday'
                WHEN 3 THEN '3-Wednesday' WHEN 4 THEN '4-Thursday' WHEN 5 THEN '5-Friday'
                WHEN 6 THEN '6-Saturday' END AS weekday,
            ROUND(AVG(TotalSteps), 0) AS avg_steps
        FROM {TABLE_NAME}
        GROUP BY weekday
        ORDER BY weekday;
    """
    weekday_df = run_query(steps_by_weekday_sql)
    weekday_df["weekday"] = weekday_df["weekday"].str[2:]
    st.bar_chart(weekday_df.set_index("weekday"))
    with st.expander("Show SQL"):
        st.code(steps_by_weekday_sql, language="sql")

    st.divider()

    st.subheader("Time spent in different activity categories, by weekday")
    activity_categories_sql = f"""
        SELECT
            CASE CAST(strftime('%w', Date) AS INTEGER)
                WHEN 0 THEN '0-Sunday' WHEN 1 THEN '1-Monday' WHEN 2 THEN '2-Tuesday'
                WHEN 3 THEN '3-Wednesday' WHEN 4 THEN '4-Thursday' WHEN 5 THEN '5-Friday'
                WHEN 6 THEN '6-Saturday' END AS weekday,
            ROUND(AVG(LightlyActiveMinutes), 1) AS avg_lightly_active,
            ROUND(AVG(FairlyActiveMinutes), 1) AS avg_fairly_active,
            ROUND(AVG(VeryActiveMinutes), 1) AS avg_very_active
        FROM {TABLE_NAME}
        GROUP BY weekday
        ORDER BY weekday;
    """
    cat_df = run_query(activity_categories_sql)
    cat_df["weekday"] = cat_df["weekday"].str[2:]
    st.bar_chart(
        cat_df.set_index("weekday"),
        y=["avg_lightly_active", "avg_fairly_active", "avg_very_active"],
    )
    overall_avgs = cat_df[["avg_lightly_active", "avg_fairly_active", "avg_very_active"]].mean().round(1)
    st.caption(
        f"Overall averages — Lightly active: {overall_avgs['avg_lightly_active']} min · "
        f"Fairly active: {overall_avgs['avg_fairly_active']} min · "
        f"Very active: {overall_avgs['avg_very_active']} min"
    )
    with st.expander("Show SQL"):
        st.code(activity_categories_sql, language="sql")

    st.divider()

    st.subheader("Calories burnt vs. total active minutes, by weekday")
    calories_active_sql = f"""
        SELECT
            CASE CAST(strftime('%w', Date) AS INTEGER)
                WHEN 0 THEN '0-Sunday' WHEN 1 THEN '1-Monday' WHEN 2 THEN '2-Tuesday'
                WHEN 3 THEN '3-Wednesday' WHEN 4 THEN '4-Thursday' WHEN 5 THEN '5-Friday'
                WHEN 6 THEN '6-Saturday' END AS weekday,
            ROUND(AVG(LightlyActiveMinutes + FairlyActiveMinutes + VeryActiveMinutes), 1) AS avg_total_active_minutes,
            ROUND(AVG(Calories), 0) AS avg_calories
        FROM {TABLE_NAME}
        GROUP BY weekday
        ORDER BY weekday;
    """
    cal_df = run_query(calories_active_sql)
    cal_df["weekday"] = cal_df["weekday"].str[2:]
    col_a, col_b = st.columns(2)
    col_a.bar_chart(cal_df.set_index("weekday")[["avg_total_active_minutes"]])
    col_b.line_chart(cal_df.set_index("weekday")[["avg_calories"]])
    with st.expander("Show SQL"):
        st.code(calories_active_sql, language="sql")

    st.divider()

    st.subheader("Sedentary minutes vs. minutes asleep (daily average per participant)")
    sedentary_sleep_sql = f"""
        SELECT Id,
            ROUND(AVG(SedentaryMinutes), 0) AS avg_sedentary_minutes,
            ROUND(AVG(TotalMinutesAsleep), 0) AS avg_minutes_asleep
        FROM {TABLE_NAME}
        WHERE HasSleepData = 1
        GROUP BY Id
        ORDER BY avg_minutes_asleep DESC;
    """
    sed_sleep_df = run_query(sedentary_sleep_sql)
    st.dataframe(sed_sleep_df, use_container_width=True)
    st.scatter_chart(sed_sleep_df, x="avg_sedentary_minutes", y="avg_minutes_asleep")
    with st.expander("Show SQL"):
        st.code(sedentary_sleep_sql, language="sql")

    st.divider()

    st.subheader("Most / least active participants (by average daily steps)")
    activity_rank_sql = f"""
        SELECT Id,
            ROUND(AVG(TotalSteps), 0) AS avg_steps,
            ROUND(AVG(Calories), 0) AS avg_calories,
            COUNT(*) AS days_logged
        FROM {TABLE_NAME}
        GROUP BY Id
        ORDER BY avg_steps DESC;
    """
    rank_df = run_query(activity_rank_sql)
    col_top, col_bottom = st.columns(2)
    col_top.markdown("**Top 5 most active**")
    col_top.dataframe(rank_df.head(5), use_container_width=True)
    col_bottom.markdown("**Bottom 5 least active**")
    col_bottom.dataframe(rank_df.tail(5), use_container_width=True)
    with st.expander("Show SQL"):
        st.code(activity_rank_sql, language="sql")

    st.divider()

    st.subheader("Device-wear consistency")
    wear_sql = f"""
        SELECT Id,
            COUNT(*) AS total_days,
            SUM(CASE WHEN LikelyDeviceNotWorn = 1 THEN 1 ELSE 0 END) AS days_not_worn,
            ROUND(100.0 * SUM(CASE WHEN LikelyDeviceNotWorn = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_not_worn
        FROM {TABLE_NAME}
        GROUP BY Id
        HAVING days_not_worn > 0
        ORDER BY pct_not_worn DESC;
    """
    wear_df = run_query(wear_sql)
    st.dataframe(wear_df, use_container_width=True)
    with st.expander("Show SQL"):
        st.code(wear_sql, language="sql")