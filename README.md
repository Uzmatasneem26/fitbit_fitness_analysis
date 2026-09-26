# STRAVA Fitness Analytics

## 📌 Project Overview

STRAVA Fitness Analytics is a data analytics and Streamlit dashboard project that analyzes fitness and smart-device activity data.

The project uses a cleaned Fitbit daily activity dataset to understand patterns in physical activity, calories, sleep, heart rate, sedentary behavior, and user activity.

The project also includes a dedicated **SQL Analysis** section inside the Streamlit application, where fitness data is loaded into an SQLite database and analyzed using SQL queries.

## 🎯 Business Objective

The objective of this project is to analyze smart-device fitness data and identify useful patterns in how users track and engage with their health and fitness activities.

The analysis focuses on:

* Physical activity and daily steps
* Calories burned
* Distance traveled
* Sleep patterns
* Activity intensity
* Sedentary behavior
* Heart-rate information
* User-level activity patterns
* Device and data availability

These insights can be used to understand user behavior and support data-driven wellness and marketing decisions.

## 💼 Business Problem

Fitness and smart-device companies collect large amounts of activity and health-related data. However, raw fitness data alone does not clearly explain user behavior.

This project analyzes the available data to answer questions such as:

* How active are users on average?
* Which users have higher activity levels?
* How does activity vary across days of the week?
* What patterns exist between sleep and physical activity?
* How much time do users spend sedentary?
* What are the differences between activity intensity levels?
* How frequently are sleep, weight, and heart-rate data available?

## 📊 Dataset

The project uses a cleaned Fitbit daily fitness dataset.

The dataset contains daily-level information including:

* User ID
* Date
* Total steps
* Total distance
* Calories
* Very active minutes
* Fairly active minutes
* Lightly active minutes
* Sedentary minutes
* Sleep duration
* Time in bed
* Average heart rate
* Minimum heart rate
* Maximum heart rate
* Sleep-data availability
* Weight-data availability
* Heart-rate-data availability
* Device-wear indicators

## 🛠️ Technologies Used

### Programming & Analysis

* Python
* Pandas
* NumPy

### Visualization

* Matplotlib
* Seaborn
* Streamlit

### SQL Analysis

* SQL
* SQLite

### Development

* VS Code
* Git
* GitHub

## 📈 Streamlit Dashboard

The Streamlit application provides an interactive dashboard for exploring the fitness dataset.

### Main sections

* 🏠 Home
* 📊 Overview Dashboard
* 🏃 Activity Analysis
* 😴 Sleep Analysis
* 👤 User Analysis
* 🗄️ SQL Analysis
* 📋 Raw Data
* ℹ️ About Project

## 🗄️ SQL Analysis

The SQL Analysis page loads the cleaned CSV dataset into an in-memory SQLite database using Pandas.

The dataset is stored as:

`fitness_daily`

The SQL section includes:

* SQL KPI analysis
* Activity-level analysis
* User-level analysis
* Day-of-week analysis
* Sleep analysis
* Activity intensity analysis
* Heart-rate analysis
* Device and data-quality analysis
* Highest-calorie days
* Most-active days
* Predefined SQL queries
* Custom SQL queries
* CSV download of SQL results

Users can select predefined queries or write their own read-only `SELECT`/`WITH` SQL queries.

## 🔍 Example SQL Questions

The project uses SQL to answer questions such as:

```sql
SELECT
    Id,
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(Calories), 0) AS avg_calories
FROM fitness_daily
GROUP BY Id
ORDER BY avg_steps DESC
LIMIT 10;
```

This identifies users with the highest average daily steps.

Another analysis groups users by sleep duration:

```sql
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
GROUP BY sleep_group;
```

## 💡 Key Analytical Areas

### Activity

The project compares daily steps, distance, active minutes, and calories to understand different activity levels.

### Sleep

Sleep duration and time in bed are analyzed alongside activity and calorie patterns.

### Sedentary Behavior

Sedentary minutes are analyzed to understand how much tracked time is spent inactive.

### Heart Rate

Available heart-rate data is summarized using average, minimum, and maximum heart-rate measures.

### User Analysis

User-level averages are calculated to compare activity patterns across tracked users.

### Weekly Patterns

Activity and calorie averages are compared across days of the week.

## 📁 Project Structure

```text
STRAVA FITNESS APP/
│
├── app.py
│
├── data/
│   └── fitbit_daily_completely_cleaned.csv
│
├── pages/
│   └── SQL Analysis.py
│
├── requirements.txt
├── README.md
└── .gitignore
```

## 🚀 How to Run the Project

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### 2. Open the project

```bash
cd STRAVA-FITNESS-APP
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

Windows:

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run Streamlit

```bash
streamlit run app.py
```

The application will open in your browser.

## 🌐 Streamlit Deployment

The project can be deployed using Streamlit Community Cloud.

Make sure the GitHub repository contains:

```text
app.py
requirements.txt
data/
pages/
```

Select `app.py` as the main application file when deploying.

## 📌 Important Note About SQL

The SQL analysis uses an **in-memory SQLite database**.

The CSV data is loaded into SQLite when the Streamlit application starts. No external database server is required.

The SQL table used by the application is:

```text
fitness_daily
```

## ⚠️ Limitations

* The analysis is based on the available Fitbit records.
* User tracking duration may differ between users.
* Not every record contains sleep, weight, or heart-rate information.
* The analysis describes patterns in the available data and does not establish causal relationships.
* The dataset represents the available tracked users and should not automatically be treated as representative of all fitness-device users.

## 👩‍💻 Project Purpose

This project demonstrates practical skills in:

* Data cleaning
* Exploratory Data Analysis
* SQL analysis
* Data visualization
* Python
* Pandas
* SQLite
* Streamlit dashboard development
* Business insight generation

## 📜 References

The project case study focuses on using smart-device fitness data to understand consumer usage patterns and derive insights that can support wellness and marketing strategy.
