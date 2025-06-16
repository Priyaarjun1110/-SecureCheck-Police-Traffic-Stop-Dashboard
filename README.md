# 🚨 SecureCheck: A Python-SQL Digital Ledger for Police Post Logs

**Domain:** Law Enforcement & Public Safety  
**Tech Stack:** Python · PostgreSQL · Streamlit · Plotly · Pandas

---

## 🔍 Project Overview

**SecureCheck** is a real-time traffic stop analytics and prediction system designed for law enforcement check posts. It replaces traditional manual logs with a centralized, SQL-powered digital dashboard built using Python and Streamlit.

The system tracks vehicle stops, analyzes patterns in violations, searches, arrests, and helps officers predict possible outcomes based on past data.

---

## 🧩 Features

- ✅ Real-time logging of police traffic stops
- 📊 Key metrics: Arrests, Searches, Violations, Driver Demographics
- 📈 Interactive dashboards and visualizations using Plotly
- 🔍 14 medium-level SQL query options via dropdown
- 🧠 6 advanced SQL queries (joins, subqueries, window functions)
- 🧮 Smart prediction engine for likely outcomes & violations
- 💬 Clean, modern Streamlit user interface
- 🔐 Secure PostgreSQL database integration

---

## 📁 Dataset Schema

| Column              | Description                              |
|---------------------|------------------------------------------|
| stop_date           | Date of the stop                         |
| stop_time           | Time of the stop                         |
| country_name        | Country of the stop                      |
| driver_gender       | Gender of the driver (M/F)               |
| driver_age          | Age of the driver                        |
| driver_race         | Race/Ethnicity of the driver             |
| violation           | Violation type (Speeding, DUI, etc.)     |
| stop_outcome        | Result (Warning, Citation, Arrest)       |
| search_conducted    | Was a search conducted? (True/False)     |
| search_type         | Type of search                           |
| is_arrested         | Was the driver arrested? (True/False)    |
| drugs_related_stop  | Was the stop drug-related? (True/False)  |
| stop_duration       | Duration of the stop                     |
| vehicle_number      | Unique vehicle identifier                |

---

## 📊 Visual Dashboards

- **Metric Cards**: Total Stops, Arrests, Searches, Violation Types  
- **Bar Charts**: Key Metrics Summary  
- **Pie Chart**: Driver Gender Distribution  
- **Dropdown Filters**: Select and run medium or advanced SQL queries  
- **Smart Form**: Add new logs and receive predicted outcome & violation  

---

## 🧠 SQL Query Categories

<details>
<summary>🚗 Vehicle-Based Queries</summary>

- Top 10 vehicles in drug-related stops  
- Most frequently searched vehicles  

</details>

<details>
<summary>🧍 Demographics-Based</summary>

- Age groups with highest arrest rate  
- Gender distribution by country  
- Race-gender combinations with high search rates  

</details>

<details>
<summary>🕒 Time-Based Queries</summary>

- Most common hours for stops  
- Night vs Day arrest comparison  
- Avg. stop durations for different violations  

</details>

<details>
<summary>⚖️ Violation-Based</summary>

- Most searched and arrested violations  
- Violations common among drivers under 25  
- Violations rarely leading to search/arrest  

</details>

<details>
<summary>🌍 Location-Based</summary>

- Countries with high drug-related stops  
- Arrest rate by country and violation  
- Country with most search-conducted stops  

</details>

<details>
<summary>🧪 Advanced SQL (Window & Joins)</summary>

- Yearly breakdown of arrests by country  
- Violation trends by age & race  
- Time-period patterns of traffic stops  
- Violations with highest search & arrest rates  
- Driver demographics by country  
- Top 5 violations with highest arrest rates  

</details>

---

## 📦 Project Structure

```bash
SecureCheck/
├── miniproject1.py            # Main Streamlit dashboard app
├── clean_data.py              # Data cleaning logic
├── requirements.txt           # Python dependencies
├── /sql                       # SQL query library (optional)
├── /data                      # Raw or cleaned CSV samples
├── /screenshots               # Dashboard screenshots
├── /docs                      # Project documentation (e.g. Police.docx)
└── README.md                  # This file

