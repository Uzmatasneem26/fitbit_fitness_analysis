-- =========================================================
-- fitness_analysis.sql
--
-- All SQL used by the app, run against the `daily_activity`
-- table (loaded from fitbit_daily_cleaned.csv by
-- utils/data_loader.py).
--
-- Each query is preceded by a "-- name: <key>" marker.
-- data_loader.parse_sql_file() splits this file on those
-- markers so any page can do:
--
--     from utils.data_loader import get_query, run_query
--     df = run_query(get_query("null_check"))
--
-- Keep one query per "-- name:" block, terminated with ";".
-- =========================================================


-- name: null_check
-- Null check on key metrics — should return all zeros.
SELECT
    SUM(CASE WHEN TotalSteps IS NULL THEN 1 ELSE 0 END) AS null_steps,
    SUM(CASE WHEN TotalDistance IS NULL THEN 1 ELSE 0 END) AS null_distance,
    SUM(CASE WHEN Calories IS NULL THEN 1 ELSE 0 END) AS null_calories,
    SUM(CASE WHEN SedentaryMinutes IS NULL THEN 1 ELSE 0 END) AS null_sedentary
FROM daily_activity;


-- name: negative_value_check
-- Min/max range check to catch negative or otherwise
-- out-of-range values.
SELECT
    MIN(TotalDistance) AS min_distance, MAX(TotalDistance) AS max_distance,
    MIN(TotalSteps) AS min_steps, MAX(TotalSteps) AS max_steps,
    MIN(SedentaryMinutes) AS min_sedentary, MAX(SedentaryMinutes) AS max_sedentary,
    MIN(Calories) AS min_calories, MAX(Calories) AS max_calories
FROM daily_activity;


-- name: full_day_sedentary
-- Rows where SedentaryMinutes >= 1440 (a full day) — these
-- indicate the device was likely not worn that day.
SELECT Id, Date, SedentaryMinutes, LikelyDeviceNotWorn
FROM daily_activity
WHERE SedentaryMinutes >= 1440
ORDER BY Id, Date;


-- name: duplicate_rows
-- Duplicate Id + Date combinations — should return zero rows.
SELECT Id, Date, COUNT(*) AS n
FROM daily_activity
GROUP BY Id, Date
HAVING COUNT(*) > 1;


-- name: participant_coverage
-- Per-participant record coverage — not everyone logged the
-- full period, and not every day has sleep/heart-rate/weight data.
SELECT Id,
    COUNT(*) AS days_logged,
    SUM(CASE WHEN HasSleepData = 1 THEN 1 ELSE 0 END) AS days_with_sleep,
    SUM(CASE WHEN HasHeartRateData = 1 THEN 1 ELSE 0 END) AS days_with_hr,
    SUM(CASE WHEN HasWeightData = 1 THEN 1 ELSE 0 END) AS days_with_weight,
    SUM(CASE WHEN LikelyDeviceNotWorn = 1 THEN 1 ELSE 0 END) AS days_device_not_worn
FROM daily_activity
GROUP BY Id
ORDER BY days_logged DESC;


-- name: avg_steps_by_weekday
-- Average total steps by day of week.
SELECT
    CASE CAST(strftime('%w', Date) AS INTEGER)
        WHEN 0 THEN '0-Sunday' WHEN 1 THEN '1-Monday' WHEN 2 THEN '2-Tuesday'
        WHEN 3 THEN '3-Wednesday' WHEN 4 THEN '4-Thursday' WHEN 5 THEN '5-Friday'
        WHEN 6 THEN '6-Saturday' END AS weekday,
    ROUND(AVG(TotalSteps), 0) AS avg_steps
FROM daily_activity
GROUP BY weekday
ORDER BY weekday;


-- name: activity_categories_by_weekday
-- Average lightly/fairly/very active minutes by day of week.
SELECT
    CASE CAST(strftime('%w', Date) AS INTEGER)
        WHEN 0 THEN '0-Sunday' WHEN 1 THEN '1-Monday' WHEN 2 THEN '2-Tuesday'
        WHEN 3 THEN '3-Wednesday' WHEN 4 THEN '4-Thursday' WHEN 5 THEN '5-Friday'
        WHEN 6 THEN '6-Saturday' END AS weekday,
    ROUND(AVG(LightlyActiveMinutes), 1) AS avg_lightly_active,
    ROUND(AVG(FairlyActiveMinutes), 1) AS avg_fairly_active,
    ROUND(AVG(VeryActiveMinutes), 1) AS avg_very_active
FROM daily_activity
GROUP BY weekday
ORDER BY weekday;


-- name: calories_vs_active_minutes_by_weekday
-- Average total active minutes vs. average calories, by weekday.
SELECT
    CASE CAST(strftime('%w', Date) AS INTEGER)
        WHEN 0 THEN '0-Sunday' WHEN 1 THEN '1-Monday' WHEN 2 THEN '2-Tuesday'
        WHEN 3 THEN '3-Wednesday' WHEN 4 THEN '4-Thursday' WHEN 5 THEN '5-Friday'
        WHEN 6 THEN '6-Saturday' END AS weekday,
    ROUND(AVG(LightlyActiveMinutes + FairlyActiveMinutes + VeryActiveMinutes), 1) AS avg_total_active_minutes,
    ROUND(AVG(Calories), 0) AS avg_calories
FROM daily_activity
GROUP BY weekday
ORDER BY weekday;


-- name: sedentary_vs_sleep_by_participant
-- Average sedentary minutes vs. average minutes asleep, per participant.
SELECT Id,
    ROUND(AVG(SedentaryMinutes), 0) AS avg_sedentary_minutes,
    ROUND(AVG(TotalMinutesAsleep), 0) AS avg_minutes_asleep
FROM daily_activity
WHERE HasSleepData = 1
GROUP BY Id
ORDER BY avg_minutes_asleep DESC;


-- name: activity_rank_by_participant
-- Most / least active participants by average daily steps.
SELECT Id,
    ROUND(AVG(TotalSteps), 0) AS avg_steps,
    ROUND(AVG(Calories), 0) AS avg_calories,
    COUNT(*) AS days_logged
FROM daily_activity
GROUP BY Id
ORDER BY avg_steps DESC;


-- name: device_wear_consistency
-- Percentage of days each participant's device was likely not worn.
SELECT Id,
    COUNT(*) AS total_days,
    SUM(CASE WHEN LikelyDeviceNotWorn = 1 THEN 1 ELSE 0 END) AS days_not_worn,
    ROUND(100.0 * SUM(CASE WHEN LikelyDeviceNotWorn = 1 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_not_worn
FROM daily_activity
GROUP BY Id
HAVING days_not_worn > 0
ORDER BY pct_not_worn DESC;