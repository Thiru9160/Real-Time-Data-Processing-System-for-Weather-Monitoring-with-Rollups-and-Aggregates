import mysql.connector
from datetime import datetime

# Establish a connection to the MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Thirumalesh9160@',
    database='weather_monitoring'
)

cursor = conn.cursor()

# Function to insert weather data into the weather_data table
def insert_weather_data(city, temperature, feels_like, weather):
    timestamp = datetime.now()
    query = '''
        INSERT INTO weather_data (city, temperature, feels_like, weather, timestamp)
        VALUES (%s, %s, %s, %s, %s)
    '''
    values = (city, temperature, feels_like, weather, timestamp)
    cursor.execute(query, values)
    conn.commit()

# Example usage
insert_weather_data('Delhi', 32.5, 35.0, 'Clear')
def calculate_daily_summary(city):
    query = '''
        SELECT 
            AVG(temperature) AS avg_temp,
            MAX(temperature) AS max_temp,
            MIN(temperature) AS min_temp,
            weather,
            COUNT(weather) AS condition_count
        FROM 
            weather_data
        WHERE 
            city = %s
            AND DATE(timestamp) = CURDATE()
        GROUP BY
            weather
        ORDER BY
            condition_count DESC
    '''
    cursor.execute(query, (city,))
    rows = cursor.fetchall()
    
    if rows:
        avg_temp = rows[0][0]
        max_temp = rows[0][1]
        min_temp = rows[0][2]
        dominant_weather = rows[0][3]  # The most frequent weather condition
        
        print(f"City: {city}")
        print(f"Average Temperature: {avg_temp:.2f}°C")
        print(f"Maximum Temperature: {max_temp:.2f}°C")
        print(f"Minimum Temperature: {min_temp:.2f}°C")
        print(f"Dominant Weather Condition: {dominant_weather}")
        
        # Store the daily summary into the daily_summaries table
        insert_daily_summary(city, avg_temp, max_temp, min_temp, dominant_weather)
    
    else:
        print(f"No data available for {city} today.")

def insert_daily_summary(city, avg_temp, max_temp, min_temp, dominant_weather):
    date_today = datetime.now().date()
    query = '''
        INSERT INTO daily_summaries (city, avg_temp, max_temp, min_temp, dominant_weather, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    values = (city, avg_temp, max_temp, min_temp, dominant_weather, date_today)
    cursor.execute(query, values)
    conn.commit()

# Example usage:
calculate_daily_summary('Delhi')
def insert_user_threshold(user_id, city, max_temp=None, min_temp=None, weather_condition=None, consecutive_updates=1):
    query = '''
        INSERT INTO user_thresholds (user_id, city, max_temp, min_temp, weather_condition, consecutive_updates)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    values = (user_id, city, max_temp, min_temp, weather_condition, consecutive_updates)
    cursor.execute(query, values)
    conn.commit()

# Example: Insert a threshold to alert if Delhi's temperature exceeds 35°C for 2 consecutive updates
insert_user_threshold(1, 'Delhi', max_temp=35.0, consecutive_updates=2)
def get_latest_weather_data(city):
    query = '''
        SELECT temperature, weather, timestamp
        FROM weather_data
        WHERE city = %s
        ORDER BY timestamp DESC
        LIMIT 1
    '''
    cursor.execute(query, (city,))
    return cursor.fetchone()
def check_temperature_alert(city, current_temp):
    # Fetch user-defined thresholds for this city
    query = '''
        SELECT max_temp, min_temp, consecutive_updates
        FROM user_thresholds
        WHERE city = %s
    '''
    cursor.execute(query, (city,))
    thresholds = cursor.fetchone()

    if thresholds:
        max_temp, min_temp, consecutive_updates = thresholds

        # Check if the temperature exceeds the max_temp threshold
        if max_temp and current_temp > max_temp:
            print(f"ALERT: Temperature in {city} exceeded {max_temp}°C!")
            return True

        # Check if the temperature drops below the min_temp threshold
        if min_temp and current_temp < min_temp:
            print(f"ALERT: Temperature in {city} dropped below {min_temp}°C!")
            return True

    return False
def check_weather_condition_alert(city, current_weather):
    # Fetch user-defined weather condition thresholds for this city
    query = '''
        SELECT weather_condition, consecutive_updates
        FROM user_thresholds
        WHERE city = %s
    '''
    cursor.execute(query, (city,))
    thresholds = cursor.fetchone()

    if thresholds:
        weather_condition, consecutive_updates = thresholds

        # Check if the weather condition matches the user's threshold
        if weather_condition and current_weather == weather_condition:
            print(f"ALERT: {weather_condition} detected in {city}!")
            return True

    return False
# A dictionary to store how many consecutive breaches have occurred for each city
consecutive_breaches = {}

def check_consecutive_breaches(city, is_breached):
    if is_breached:
        # Increment the breach count if the condition was breached
        if city in consecutive_breaches:
            consecutive_breaches[city] += 1
        else:
            consecutive_breaches[city] = 1
    else:
        # Reset the counter if the condition was not breached
        consecutive_breaches[city] = 0
    
    # Fetch the required consecutive breaches from the user-defined thresholds
    query = '''
        SELECT consecutive_updates
        FROM user_thresholds
        WHERE city = %s
    '''
    cursor.execute(query, (city,))
    required_breaches = cursor.fetchone()[0]
    
    # Trigger an alert if the consecutive breaches exceed the required threshold
    if consecutive_breaches[city] >= required_breaches:
        print(f"ALERT: {city} has breached the threshold for {required_breaches} consecutive updates!")
        consecutive_breaches[city] = 0  # Reset the counter after alerting
