import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
from sqlalchemy import create_engine

# Function to create a database connection
def create_connection():
    try:
        # SQLAlchemy connection string format: dialect+driver://username:password@host:port/database
        db_url = "postgresql+psycopg2://postgres:Arjun1110@localhost:5432/Sample1" # Replace with your actual database URL
        engine = create_engine(db_url, echo=False)  # echo=True for SQL logs
        return engine # Return the SQLAlchemy engine object
    except Exception as e: # Handle any exceptions that occur during connection
        print(f"❌ Error creating engine: {e}") # Print error message if connection fails
        return None # Return None if connection fails

# Fetch data using pandas and SQLAlchemy

df = pd.read_sql("SELECT * FROM traffic_stops", create_connection()) # Function to fetch data from the database using a SQL query
def fetch_data(query): # Function to fetch data from the database using a SQL query
    engine = create_connection() # Create a database connection
    if engine: # Check if the connection was successful
        try: # Execute the SQL query and fetch the data
            df = pd.read_sql(query, con=engine) # Read SQL query results into a DataFrame
            return df # Return the DataFrame containing the query results
        except Exception as e: # Handle any exceptions that occur during query execution
            print(f"Error executing query: {e}") # Print error message if query execution fails
            return pd.DataFrame() # Return an empty DataFrame if query execution fails
    else:
        return pd.DataFrame()  # Return an empty DataFrame if connection fails

def clean_data(df):
    # Drop columns where all values are NaN
    df = df.dropna(axis=1, how='all')

    # Fill missing string fields with 'Unknown'
    string_cols = ['driver_gender', 'driver_race', 'country_name', 'violation', 'stop_outcome', 'search_type', 'stop_duration']
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].fillna('Unknown')

    # Fill missing boolean fields with False
    bool_cols = ['search_conducted', 'drugs_related_stop', 'is_arrested']
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].fillna(False).astype(bool)

    # Handle missing ages: convert to numeric, fill with median, cast to int
    if 'driver_age' in df.columns:
        df['driver_age'] = pd.to_numeric(df['driver_age'], errors='coerce')
        df['driver_age'] = df['driver_age'].fillna(df['driver_age'].median()).astype(int)

    # Convert 'stop_date' to datetime
    if 'stop_date' in df.columns:
        df['stop_date'] = pd.to_datetime(df['stop_date'], errors='coerce')

    # Convert 'stop_time' to time only
    if 'stop_time' in df.columns:
        df['stop_time'] = pd.to_datetime(df['stop_time'], errors='coerce').dt.time

    return df

#Load data from the database and clean it
raw_df = pd.read_sql("SELECT * FROM traffic_stops", create_connection())
data = clean_data(raw_df)

#stop duration options
durations = data['stop_duration'].dropna().unique().tolist()
durations = sorted(durations) if durations else ["0-15 Min", "16-30 Min", "30+ Min"]



# Page title and layout settings
st.set_page_config(page_title="SecureCheck Dashboard", layout="wide") # Set the page title and layout
st.title(":green[🚨 SecureCheck: Police Traffic Stop Dashboard]") 

st.header("👮‍♂️ Traffic Stop Data Analysis") 
query="SELECT * FROM traffic_stops" # SQL query to fetch all traffic stops data
data = fetch_data(query) # Call the fetch_data function to run the SQL query and load the results into a DataFrame
st.dataframe(data, use_container_width=True) # Display the DataFrame in Streamlit

#Key Metrics
st.header("📊 Key Metrics") 
col1, col2, col3, col4 = st.columns(4) # Create 4 columns for displaying key metrics


# Total Stops
with col1: # Calculate total stops and display it in the first column
    total_stops = data.shape[0] # Get the number of rows in the DataFrame
    st.metric(label="Total Stops", value=total_stops) # Display the total stops metric

# is_arrested
with col2: # Calculate total arrests and display it in the second column
    arrests = data['stop_outcome'].value_counts().get('Arrest', 0) # Count the number of arrests in the 'stop_outcome' column
    st.metric(label="Total Arrests", value=arrests) #

# Search Conducted
with col3: # Calculate total searches conducted and display it in the third column
    search_count = data['search_conducted'].sum() # Count the number of searches conducted in the 'search_conducted' column
    st.metric(label="Total Searches", value=search_count) # Display the total searches metric

# Violations
with col4: # Calculate total unique violations and display it in the fourth column
    violation_count = data['violation'].nunique() # Count the number of unique violations in the 'violation' column
    st.metric(label="Total Violations", value=violation_count) # Display the total violations metric

# Visualizations
st.header("📈 Visualizations")
# 📊 Bar Chart for Key Metrics Summary
st.subheader("📊 Summary of Key Metrics") 

# Prepare data for the bar chart
metrics_data = { # Create a dictionary to hold the metrics data
    "Metric": ["Total Stops", "Total Arrests", "Total Searches", "Violation Types"],
    "Value": [
        data.shape[0], # Total number of stops
        data['stop_outcome'].value_counts().get('Arrest', 0), # Total number of arrests
        data['search_conducted'].sum(), # Total number of searches conducted
        data['violation'].nunique() # Total number of unique violations
    ]
}

metrics_df = pd.DataFrame(metrics_data) # Convert the dictionary to a DataFrame for visualization

# Create the bar chart
fig_metrics_bar = px.bar( # Create a bar chart using Plotly Express
    metrics_df, # Use the metrics DataFrame
    x="Metric", # X-axis will be the metric names
    y="Value", # Y-axis will be the values of the metrics
    color="Metric", # Color bars by metric type
    text="Value", # Display the value on top of each bar
    title="Key Metrics Overview", # Title of the chart
    labels={"Value": "Count"}, # Label for the Y-axis
)

# Show the chart in Streamlit
st.plotly_chart(fig_metrics_bar, use_container_width=True) # Display the bar chart in Streamlit with full container width

# ---------------- PIE CHART ----------------
st.subheader("🚻 Driver Gender Distribution (Pie Chart)")
if 'driver_gender' in data.columns: # Check if
    gender_counts = data['driver_gender'].value_counts().reset_index() # Count occurrences
    gender_counts.columns = ['Gender', 'Count'] # Rename columns for clarity

    fig_pie = px.pie(   # Create a pie chart using Plotly Express
        gender_counts, # DataFrame
        names='Gender', # Names for pie slices
        values='Count', # Values for pie slices
        title="Distribution of Driver Gender", # Title of the pie chart
        color_discrete_sequence=px.colors.sequential.RdBu # Color sequence for the pie chart
    )
    st.plotly_chart(fig_pie, use_container_width=True) # Display the pie chart in Streamlit with full container width
else:
    st.warning("Column 'driver_gender' not found in the data.") # Display a warning if the column is not found

# Medium Queries
st.header("🔍 Medium Queries")
selected_query = st.selectbox("Select a query to run:", # Dropdown to select a query
        ["🚗Vehicle-Based - 1.What are the top 10 vehicle_Number involved in drug-related stops?",
        "🚕Vehicle-Based - 2.Which vehicles were most frequently searched?",
        "🧍 Demographic-Based--3.Which driver age group had the highest arrest rate?",
        "🧍 Demographic-Based--4.What is the gender distribution of drivers stopped in each country?",
        "🧍 Demographic-Based--5.Which race and gender combination has the highest search rate?",
        "🕐Time & Duration Based--6.What time of day sees the most traffic stops?",
        "🕑Time & Duration Based - 7.What is the average stop duration for different violations?",
        "🕒Time & Duration Based 8.Are stops during the night more likely to lead to arrests?",
        "🔫Violation-Based 9. Which violations are most associated with searches or arrests?",
        "🔫Violation-Based 10. Which violations are most common among younger drivers (<25)?",
        "🔫Violation-Based 11.Is there a violation that rarely results in search or arrest?",
        "🌏Location-Based 12.Which countries report the highest rate of drug-related stops?",
        "🌏Location-Based 13.What is the arrest rate by country and violation?",
        "🌏Location-Based 14.Which country has the most stops with search conducted?",
        ])

query_map = {"""🚗Vehicle-Based - 1.What are the top 10 vehicle_Number involved in drug-related stops?""": """
select vehicle_number, count(*) as drug_stops_count -- Get vehicle number and number of drug-related stops
from traffic_stops -- From the traffic stops table
where drugs_related_stop = True -- Only include drug-related stops
group by vehicle_number --Group results by vehicle number
order by drug_stops_count desc -- Sort by number of stops, highest first
limit 10  -- Show only the top 10 vehicles""",
"""🚕Vehicle-Based - 2.Which vehicles were most frequently searched?""":"""
select vehicle_number, count(*) as most_frequently_searched_count -- Get vehicle number and how many times it was searched  
from traffic_stops -- From the traffic stops data 
where search_conducted = true -- Only include records where a search was conducted 
group by vehicle_number -- Group the data by vehicle number
order by most_frequently_searched_count desc -- Sort by search count in descending order
limit 10  -- Show only the top 10 vehicles""",
"""🧍 Demographic-Based--3.Which driver age group had the highest arrest rate?""": 
"""select driver_age, count(*) as total_stops, -- Select driver age and count how many stops happened for each age     
sum(case when is_arrested = true then 1 else 0 end) as total_arrests, --Count how many of those stops led to an arrest    
round(sum(case when is_arrested = true then 1 else 0 end)*1.0 / count(*),2) as arrest_rate -- Calculate arrest rate (arrests divided by total stops)
from traffic_stops
group by driver_age -- Group the data by driver age  
order by arrest_rate desc -- Sort by arrest rate in descending order 
limit 1 -- Show only the top result (age with highest arrest rate)""", 
"""🧍 Demographic-Based--4.What is the gender distribution of drivers stopped in each country?""":
"""select country_name, driver_gender, count(*) as total_stops from traffic_stops
group by country_name, driver_gender
order by country_name, driver_gender""", 
"""🧍 Demographic-Based--5.Which race and gender combination has the highest search rate?""":
"""select driver_race, driver_gender, 
count(*) filter(where search_conducted)*100.0/count(*) as search_rate -- Calculate search rate: (number of searches ÷ total stops) × 100  
from traffic_stops -- From the traffic stops data 
group by driver_race, driver_gender -- Group the data by driver race and gender
order by search_rate desc -- Sort the results by search rate in descending order 
limit 5 -- Show only the top 5 combinations with the highest search rate""", 
"""🕐Time & Duration Based--6.What time of day sees the most traffic stops?""":
"""select extract(hour from stop_time) as Hour_of_the_day, -- Extract the hour from stop time and label it as hour_of_the_day  
count(*) as most_traffic_stops -- Count how many traffic stops happened during that hour 
from traffic_stops                               
group by Hour_of_the_day -- Group the data by the extracted hour only 
order by most_traffic_stops desc -- Sort the results by number of stops in descending order  
limit 5 -- Show only the top 5 hours with the most traffic stops""",
"""🕑Time & Duration Based - 7.What is the average stop duration for different violations?""":
"""select violation, -- Select the type of violation
round(avg(case -- Convert stop duration ranges to estimated minutes and calculate the average
	when stop_duration ='0-5 Min' then 3
	when stop_duration= '6-15 Min' then 10
	when stop_duration ='16-30 Min' then 23
	when stop_duration = '30+ Min' then 35
	end),2)
as average_stop_duration -- Round the average stop duration to 2 decimal places and label it as average_stop_duration  
from traffic_stops where stop_duration is not null -- from traffic stops data - only include records where stop duration is not null
group by violation -- Group the data by violation type 
order by average_stop_duration desc -- Sort the results by average stop duration in descending order""",
"""🕒Time & Duration Based 8.Are stops during the night more likely to lead to arrests?""":"""select 
case 
when extract(hour from stop_time) between 18 and 23 or extract(hour from stop_time) between 0 AND 5 then 'Night'
else 'Day' -- Classify stops as Day or Night 
end as hour_of_the_day,
count(*) as total_stops, -- Count total stops per time period  
round(count(*) filter (where is_arrested) *100.0 /count(*),2) as arrest_rate -- Calculate arrest rate percentage
from traffic_stops
where stop_time is not null -- Use only records with valid stop time 
group by hour_of_the_day -- Group by time period 
order by arrest_rate desc -- Sort by highest arrest rate""",
"""🔫Violation-Based 9. Which violations are most associated with searches or arrests?""":
"""select violation, -- Select type of violation 
count(*) filter (where search_conducted) as most_searches, -- Count how many times a search was conducted for each violation 
count(*) filter (where is_arrested) as most_arrests -- Count how many arrests happened for each violation 
from traffic_stops -- From the traffic stops data 
group by violation -- Group the data by violation type 
order by most_searches desc, most_arrests desc -- Sort first by highest number of searches, then by arrests""",
"""🔫Violation-Based 10. Which violations are most common among younger drivers (<25)?""":
"""select violation, -- Select type of violation  
count(*) as younger_drivers -- Count how many drivers under age 25 were involved  
from traffic_stops where driver_age <25 -- From the traffic stops data (only where age < 25) 
group by violation -- Group the data by violation type
order by younger_drivers desc -- Sort by highest number of younger drivers""",
"""🔫Violation-Based 11.Is there a violation that rarely results in search or arrest?""":"""select 
  violation, -- Select type of violation  
  count(*) as total_stops, -- Count total number of stops for each violation  
  sum(case when search_conducted = true then 1 else 0 end) as total_searches, -- Count how many times a search was conducted 
  sum(case when is_arrested = true then 1 else 0 end) as total_arrests, -- Count how many times an arrest occurred 
  round(100.0 * sum(case when search_conducted = true then 1 else 0 end) / count(*), 2) as search_rate,-- Calculate search rate as a percentage of total stops
  round(100.0 * sum(case when is_arrested = true then 1 else 0 end) / count(*), 2) as arrest_rate -- Calculate arrest rate as a percentage of total stops 
from traffic_stops -- From the traffic stops data
group by violation -- Group the data by violation type  
order by search_rate asc, arrest_rate asc -- Sort by lowest search rate first, then by lowest arrest rate
limit 5; -- Show only the top 5 violation that rarely results in search and arrest  
""",
"""🌏Location-Based 12.Which countries report the highest rate of drug-related stops?""":
"""select country_name, -- Select the country name 
round(count(*) filter(where drugs_related_stop) *100.0 / count(*),2) as highest_rate_of_drugrelated_stops -- Calculate the drug-related stop rate as a percentage 
from traffic_stops -- From the traffic stops data  
group by country_name -- Group the data by country 
order by highest_rate_of_drugrelated_stops desc -- Sort by highest drug-related stop rate""",
"""🌏Location-Based 13.What is the arrest rate by country and violation?""":"""select country_name, violation, -- Select country name and type of violation 
round(count(*) filter(where is_arrested) *100.0 / count(*),2) as arrest_rate -- Calculate arrest rate as a percentage for each combination 
from traffic_stops -- From the traffic stops data  
group by country_name, violation -- Group the data by country and violation 
order by arrest_rate asc -- Sort by lowest arrest rate first""",
"""🌏Location-Based 14.Which country has the most stops with search conducted?""":
"""select country_name, -- Select the country name 
count(*) filter(where search_conducted) as search_count -- Count how many searches were conducted in each country
from traffic_stops -- From the traffic stops data 
group by country_name -- Group the data by country  
order by search_count desc -- Sort by highest number of searches"""}

# Display the selected query and its description
st.subheader("Selected Query") # Display the subheader for selected query
if selected_query: # If a query is selected, display it
    st.write(f"You selected: {selected_query}") # Display the selected query

# Show the query code with syntax highlighting
st.subheader("SQL Query Used") # Display the subheader for SQL query used
st.code(query_map[selected_query], language='sql') # Show the SQL code for the selected query with syntax highlighting

# Button to run the selected query
if st.button("Run Query"): # If the button is clicked, run the selected query
    if selected_query in query_map: # Check if the selected query is in the query map
        query = query_map[selected_query] # Get the SQL code for the selected query
        result_df = fetch_data(query) # Fetch the data using the SQL code
        if not result_df.empty: # If the result DataFrame is not empty, display it
            st.dataframe(result_df, use_container_width=True) # Display the result DataFrame in Streamlit with full container width
        else:   # If the result DataFrame is empty, show a warning message
            st.warning("No data found for the selected query.")
    else: # If the selected query is not valid, show an error message 
        st.error("Invalid query selected.")

# Advanced Query Section
st.header("🔍 Advanced Query Section")  
st.write("You can run predefined queries to analyze traffic stop data. Select a query from the dropdown menu below.")
# Dropdown to select a query
selected_query = st.selectbox("Select a query to run:", ["1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)",
                                                        "2.Driver Violation Trends Based on Age and Race (Join with Subquery)",
                                                        "3.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day",
                                                        "4.Violations with High Search and Arrest Rates (Window Function)",
                                                        "5.Driver Demographics by Country (Age, Gender, and Race)",
                                                        "6.Top 5 Violations with Highest Arrest Rates"])
# Map of queries to their SQL code
query_map = {
    "1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)": """
    select country_name, -- Select country name
year, -- Select year of the stop
total_stops, -- Total stops that year in the country
total_arrests, -- Total arrests that year in the country
round(total_arrests*100.0/total_stops,2) as arrest_rate, -- Arrest rate percentage
sum(total_arrests) over(partition by country_name order by year) as cummulative_arrest -- Window function: cumulative arrests over years by country
from(
select country_name, -- Subquery: select country name
extract(year from stop_date) as year, -- Extract year from stop date
count(*) as total_stops, -- Count total stops
count (*) filter (where is_arrested) as total_arrests -- Count arrests
from traffic_stops
group by country_name, extract(year from stop_date) -- Group by country and year
)as yearly_stats
order by country_name, year  -- Order results by country and year
    """,
    """2.Driver Violation Trends Based on Age and Race (Join with Subquery)""":
      """-- step 1: create a subquery that adds an age_group for each row
with age_group_table as (
select
row_number() over() as row_id, -- Add row number as ID for joining
case							-- Categorize driver_age into age groups
when driver_age <18 then 'under 18'
when driver_age between 18 and 25 then '18-25'
when driver_age between 25 and 40 then '25-40'
when driver_age between 40 and 60 then '40-60'
else '60+'
end as age_group
from traffic_stops where driver_age is not null),

traffic_stops_with_id as   -- step 2: add a row number to original table so we can join
(
select *, row_number() over() as row_id -- Add row number as ID for joining
from traffic_stops where driver_age is not null and violation is not null and driver_race is not null
)
select  -- step 3: join both on row_id to combine original data with age group
traffic_stops_with_id.violation,  -- Violation type
traffic_stops_with_id.driver_race, -- Driver race
age_group_table.age_group,  -- Age group from subquery
count (*) as total_violations -- Count violations per group
from traffic_stops_with_id
join age_group_table on traffic_stops_with_id.row_id = age_group_table.row_id  -- Join both tables on row_id to match each driver with an age group
group by traffic_stops_with_id.driver_race,age_group_table.age_group,traffic_stops_with_id.violation
order by traffic_stops_with_id.driver_race,age_group_table.age_group,total_violations desc
""", 
"""3.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day""": """select 
extract(year from stop_date) as Years_of_traffic_stops, -- Get year from stop_date
extract(month from stop_date) as Month_number_of_Year, -- Get numeric month (1–12)
to_char(stop_date,'month') as Month_of_Year, -- Get full month name
extract(hour from stop_time) as Hour_of_the_day, -- Get hour (0–23) from stop_time
date_trunc('hour',stop_time) as Hour_timestamp_of_the_Day, -- Truncate stop_time to start of hour
count(*) as total_stops -- Count number of stops
from traffic_stops
group by Years_of_traffic_stops,  -- Group by extracted year
Month_number_of_Year, -- Group by month number
Month_of_Year, -- Group by month name
Hour_of_the_day,  -- Group by hour
Hour_timestamp_of_the_Day -- Group by hour timestamp
order by Years_of_traffic_stops, -- Sort by year
Month_number_of_Year,Month_of_Year, -- Then by month
Hour_of_the_day,Hour_timestamp_of_the_Day asc -- Then by time of day""", """4.Violations with High Search and Arrest Rates (Window Function)""": """-- Step 1: Create a subquery to calculate search & arrest counts/rates by violation type
with violation_type as (
select violation, -- Violation type
count(*) as total_stops, -- Total number of stops
count(*) filter (where search_conducted=true) as total_search, -- Number of searches conducted
count(*) filter (where is_arrested=true) as total_arrest, -- Number of arrests made
round(count(*) filter (where search_conducted=true)*100.0/count(*),2) as search_rate, -- % of stops with search
round(count(*) filter (where is_arrested=true)*100.0/count(*),2) as arrest_rate  -- % of stops with arrest
from traffic_stops where violation is not null
group by violation 
),
-- Step 2: Rank violations by search rate and arrest rate
rank_violation as (
select *,
rank() over (order by search_rate desc) as search_rank, -- Rank violations by search rate (highest = 1)
rank() over (order by arrest_rate desc) as arrest_rank -- Rank violations by arrest rate (highest = 1)
from violation_type)
-- Step 3: Select and display all data with ranks
select
violation, --Violation type
total_stops, --total stops
total_search, --total searches
search_rate, --search rate(%)
search_rank, --search rate rank
total_arrest, --toral arrest
arrest_rate, -- arrest rate(%)
arrest_rank --aarrest rate rank
from rank_violation
order by (search_rank+arrest_rank) desc -- Sort by combined rank (higher total rank at bottom)
""", """5.Driver Demographics by Country (Age, Gender, and Race)""": """-- Step 1: Create a subquery that assigns age groups and selects key driver info
with age_group_table as (
select country_name,  -- Country of the driver
case 
when driver_age <18 then 'under 18' -- Categorize driver_age into age groups
when driver_age between 18 and 25 then '18-25'
when driver_age between 25 and 40 then '25-40'
when driver_age between 40 and 60 then '40-60'
else '60+'
end as age_group,
driver_gender, -- Gender of the driver
driver_race from traffic_stops -- Race of the driver
where country_name is not null
and driver_age is not null
and driver_gender is not null
and driver_race is not null
)
-- Step 2: Group the results by country, age group, and race, and count drivers
select country_name,  -- Country of the driver
age_group, -- Age group bucket
driver_race, -- Driver race
count(*) as total_drivers  -- Total drivers in this group
from age_group_table
group by country_name, age_group, driver_race
order by country_name, age_group, driver_race -- Sort by country, then age group""", """6.Top 5 Violations with Highest Arrest Rates""": """select violation, -- Type of violation
count(*) as total_stops, -- Total number of traffic stops for the violation
count(*) filter (where is_arrested=true) as total_arrest, -- Number of arrests for the violation
round (count(*) filter (where is_arrested=true)*100.0/count(*),2) as arrest_rate -- Arrest rate (%) for the violation
from traffic_stops where violation is not null -- Consider only rows with a valid violation
group by violation -- Group data by each violation type
order by arrest_rate desc  -- Sort violations by highest arrest rate
limit 5  -- Return top 5 violations with highest arrest rates
"""}

# Display the selected query and its description
st.subheader("Selected Query")
if selected_query: # If a query is selected, display it
    st.write(f"You selected: {selected_query}")


# Show the query code with syntax highlighting
st.subheader("SQL Query Used")
st.code(query_map[selected_query], language='sql')  # Show the SQL code for the selected query with syntax highlighting

# Button to run the selected query
if st.button("Run Adv Query"): # If the button is clicked, run the selected query
    if selected_query in query_map: # Check if the selected query is in the query map
        query = query_map[selected_query] # Get the SQL code for the selected query
        result_df = fetch_data(query) # Fetch the data using the SQL code
        if not result_df.empty: # If the result DataFrame is not empty, display it
            st.dataframe(result_df, use_container_width=True) # Display the result DataFrame in Streamlit with full container width
        else:
            st.warning("No data found for the selected query.") # Display a warning if the result DataFrame is empty
    else:
        st.error("Invalid query selected.") # Display an error if the selected query is not valid

st.markdown("---") # Footer separator
st.markdown("Made with ❤️ for Law Enforcement by SecureCheck Team") # Footer message
st.header("🎈To Know the details") 

st.markdown("Fill out the form below to know the details:") # Form header

st.header("📋 Add New Police Log and Predict Outcome and Violation") 

# Input fields for new police log
with st.form("new_log_form"): # Create a form for adding a new police log
    st.subheader("Add New Police Log") # Input fields for the new log
    stop_date = st.date_input("Stop Date") # Input for stop date
    stop_time = st.time_input("Stop Time", step=datetime.timedelta(minutes=1)) # Input for stop time with 1-minute step
    country_name = st.text_input("Country Name") # Input for country name
    driver_gender = st.selectbox("Driver Gender", ["M","F"]) # Select box for driver gender
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27) # Input for driver age with a range from 16 to 100 and default value of 27
    driver_race = st.text_input("Driver Race") # Input for driver race
    search_conducted = st.selectbox("Search Conducted", ["Yes", "No"]) # Select box for search conducted
    search_type = st.text_input("Search Type (if applicable)") # Input for search type, if applicable
    drug_related_stop = st.selectbox("Drug Related Stop", ["Yes", "No"]) # Select box for drug-related stop
    stop_duration = st.selectbox("Stop Duration", ["0-5 Min", "6-15 Min", "16-30 Min", "30+ Min"]) # Select box for stop duration with predefined options
    vehicle_number = st.text_input("Vehicle Number") # Input for vehicle number
    timestamp = pd.Timestamp(f"{stop_date} {stop_time}") # Combine date and time into a single timestamp

    submitted = st.form_submit_button("Submit Log") # Submit button for the form

   # Filter Data for Prediction and Submit Log
if submitted:  # If the form is submitted
    filtered_data = data[ # # Create a new DataFrame by filtering the data based on the input values
        (data['driver_gender'] == driver_gender) & # Filter by driver gender
        (data['driver_age'] == driver_age) & # Filter by driver age
        (data['search_conducted'] == (search_conducted == "Yes")) &  # Filter by search conducted
        (data['stop_duration'] == stop_duration) & # Filter by stop duration
        (data['drugs_related_stop'] == (drug_related_stop == "Yes"))  # Filter by drug-related stop
    ]


    # Predict stop_outcome and violation if similar records exist
    if not filtered_data.empty: # Check if the filtered data is not empty
        stop_outcome = filtered_data['stop_outcome'].mode()[0] # Get the most common stop outcome
        violation = filtered_data['violation'].mode()[0] # Get the most common violation
    else: # If no similar records found, set default values
        predicted_outcome = "Warning"
        predicted_violation = "Speeding"

# ✅ Convert gender code to full text
    gender_full = "Male" if driver_gender == "M" else "Female" 
       
# Log confirmation message
    search_text = "A search was conducted" if search_conducted == "Yes" else "No search was conducted" # Determine search text based on user input
    drug_text = "was a drug-related stop" if drug_related_stop == "Yes" else "was not a drug-related stop" # Determine drug-related stop text based on user input

    st.markdown(f""" 
    📝 **Prediction Summary ** 
        
    **Predicted Stop Outcome:** {predicted_outcome} \n 
    **Predicted Violation:** {predicted_violation}

    st.success(
        f"Log submitted successfully!\n A {driver_age}-year old {gender_full} driver in {country_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}
    {search_text}, and {drug_text.lower()}.
    Stop duration: **{stop_duration}**.
    Vehicle Number: **{vehicle_number}**.
    )
    """)

# Footer
st.markdown("---")  # Footer separator
st.markdown("Made with ❤️ by SecureCheck Team") # Footer message




 






