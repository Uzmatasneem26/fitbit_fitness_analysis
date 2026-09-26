import streamlit as st
import pandas as pd
from pathlib import Path


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Data Explorer",
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

    return pd.read_csv(file_path)


df = load_data()


# ---------------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------------
st.title("Data Explorer")

st.caption(
    "Explore, filter, and analyze the cleaned Fitbit fitness dataset."
)


# ---------------------------------------------------------
# DATASET OVERVIEW
# ---------------------------------------------------------
st.subheader("Dataset Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Records",
        f"{len(df):,}"
    )

with col2:
    st.metric(
        "Total Columns",
        f"{len(df.columns):,}"
    )

with col3:
    st.metric(
        "Missing Values",
        f"{df.isna().sum().sum():,}"
    )

with col4:
    st.metric(
        "Duplicate Rows",
        f"{df.duplicated().sum():,}"
    )


st.divider()


# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------
st.subheader("Data Filters")

filtered_df = df.copy()

filter_columns = st.columns(3)

# Date filter
date_columns = [
    "ActivityDate",
    "Date",
    "date",
    "activity_date"
]

date_column = next(
    (col for col in date_columns if col in df.columns),
    None
)

if date_column:

    filtered_df[date_column] = pd.to_datetime(
        filtered_df[date_column],
        errors="coerce"
    )

    min_date = filtered_df[date_column].min()
    max_date = filtered_df[date_column].max()

    with filter_columns[0]:

        if pd.notna(min_date) and pd.notna(max_date):

            selected_dates = st.date_input(
                "Select Date Range",
                value=(min_date.date(), max_date.date()),
                min_value=min_date.date(),
                max_value=max_date.date()
            )

            if isinstance(selected_dates, tuple) and len(selected_dates) == 2:

                start_date, end_date = selected_dates

                filtered_df = filtered_df[
                    (
                        filtered_df[date_column].dt.date >= start_date
                    )
                    &
                    (
                        filtered_df[date_column].dt.date <= end_date
                    )
                ]


# Numeric filters
numeric_columns = df.select_dtypes(
    include="number"
).columns.tolist()


with filter_columns[1]:

    if numeric_columns:

        selected_numeric = st.selectbox(
            "Numeric Column",
            numeric_columns
        )

    else:
        selected_numeric = None


with filter_columns[2]:

    search_text = st.text_input(
        "Search Data",
        placeholder="Enter a value to search..."
    )


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------
if search_text:

    mask = filtered_df.astype(str).apply(
        lambda column: column.str.contains(
            search_text,
            case=False,
            na=False
        )
    ).any(axis=1)

    filtered_df = filtered_df[mask]


# ---------------------------------------------------------
# FILTERED DATA SUMMARY
# ---------------------------------------------------------
st.subheader("Filtered Dataset")

st.write(
    f"Showing **{len(filtered_df):,}** of **{len(df):,} records**"
)


st.dataframe(
    filtered_df,
    use_container_width=True,
    height=500
)


# ---------------------------------------------------------
# NUMERIC SUMMARY
# ---------------------------------------------------------
st.divider()

st.subheader("Statistical Summary")

if numeric_columns:

    summary = filtered_df[numeric_columns].describe().T

    summary = summary.round(2)

    st.dataframe(
        summary,
        use_container_width=True
    )

else:

    st.info(
        "No numeric columns are available for statistical analysis."
    )


# ---------------------------------------------------------
# COLUMN INFORMATION
# ---------------------------------------------------------
st.divider()

st.subheader("Column Information")

column_info = pd.DataFrame({
    "Column": df.columns,
    "Data Type": [
        str(df[col].dtype)
        for col in df.columns
    ],
    "Non-Null Values": [
        df[col].notna().sum()
        for col in df.columns
    ],
    "Missing Values": [
        df[col].isna().sum()
        for col in df.columns
    ],
    "Unique Values": [
        df[col].nunique()
        for col in df.columns
    ]
})


st.dataframe(
    column_info,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# DOWNLOAD FILTERED DATA
# ---------------------------------------------------------
st.divider()

st.subheader("Download Data")

csv_data = filtered_df.to_csv(
    index=False
).encode("utf-8")


st.download_button(
    label="Download Filtered CSV",
    data=csv_data,
    file_name="fitbit_filtered_data.csv",
    mime="text/csv"
)
