
import streamlit as st


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Fitbit Fitness Analytics",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown(
    """
    <style>

    /* Main application background */
    .stApp {
        background-color: #f5f7f8;
    }

    /* Main content container */
    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Main headings */
    h1 {
        font-size: 40px !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 28px !important;
        font-weight: 650 !important;
        margin-top: 1.5rem !important;
    }

    h3 {
        font-size: 21px !important;
        font-weight: 600 !important;
    }

    /* -------------------------------------------------
       SIDEBAR
       ------------------------------------------------- */
    section[data-testid="stSidebar"] {
        background-color: #173f2c;
    }

    section[data-testid="stSidebar"] * {
        color: white;
    }

    /* Sidebar navigation text */
    section[data-testid="stSidebar"] [data-testid="stNavLink"] {
        color: white !important;
        font-size: 15px;
        border-radius: 8px;
        margin-bottom: 4px;
    }

    /* Active navigation item */
    section[data-testid="stSidebar"] [data-testid="stNavLink"][aria-current="page"] {
        background-color: rgba(255, 255, 255, 0.15);
        font-weight: 600;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: white;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 14px;
    }

    div[data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Dataframes */
    div[data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }

    /* Horizontal divider */
    hr {
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ---------------------------------------------------------
# SIDEBAR HEADER
# ---------------------------------------------------------
with st.sidebar:

    st.title("Fitbit Fitness Analytics")
    


# ---------------------------------------------------------
# PAGE DEFINITIONS
# ---------------------------------------------------------
home_page = st.Page(
    "pages/home.py",
    title="Home",
    default=True
)

activity_page = st.Page(
    "pages/activity_analysis.py",
    title="Activity Analysis"
)

sleep_page = st.Page(
    "pages/sleep_analysis.py",
    title="Sleep Analysis"
)

sql_page = st.Page(
    "pages/sql_analysis.py",
    title="SQL Analysis"
)

heart_rate_page = st.Page(
    "pages/heart_rate_analysis.py",
    title="Heart Rate Analysis"
)

calories_page = st.Page(
    "pages/calories_analysis.py",
    title="Calories Analysis"
)

wellness_page = st.Page(
    "pages/wellness_insights.py",
    title="Wellness Insights"
)

data_page = st.Page(
    "pages/data_explorer.py",
    title="Data Explorer"
)


# ---------------------------------------------------------
# NAVIGATION
# ---------------------------------------------------------
pg = st.navigation(
    [
        home_page,
        activity_page,
        sleep_page,
        sql_page,
        heart_rate_page,
        calories_page,
        wellness_page,
        data_page
    ]
)


# ---------------------------------------------------------
# RUN SELECTED PAGE
# ---------------------------------------------------------
pg.run()