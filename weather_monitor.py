import requests
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt  # For visualization


# Function to convert temperature from Kelvin to Celsius
def convert_kelvin_to_celsius(kelvin_temp):
    return kelvin_temp - 273.15



# Function to fetch weather data from the OpenWeatherMap API
def fetch_weather_data(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

        # Extract temperature values and convert them from Kelvin to Celsius
        temp_in_kelvin = data['main']['temp']
        feels_like_in_kelvin = data['main']['feels_like']
        temp_in_celsius = convert_kelvin_to_celsius(temp_in_kelvin)
        feels_like_in_celsius = convert_kelvin_to_celsius(feels_like_in_kelvin)
        
        # Return the converted values along with other relevant data
        return {
            'city': city,
            'temp': temp_in_celsius,
            'feels_like': feels_like_in_celsius,
            'main': data['weather'][0]['main'],
            'timestamp': data['dt']
        }
    else:
        print("Error fetching data:", response.status_code)
        return None



# Create a database and table to store weather data
def create_database():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS weather (
        id INTEGER PRIMARY KEY,
        city TEXT,
        temp REAL,
        feels_like REAL,
        main TEXT,
        timestamp INTEGER
    )''')
    conn.commit()
    conn.close()



# Insert weather data into the database
def insert_weather_data(city, temp, feels_like, main, timestamp):
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO weather (city, temp, feels_like, main, timestamp)
                      VALUES (?, ?, ?, ?, ?)''', (city, temp, feels_like, main, timestamp))
    conn.commit()
    conn.close()



# Calculate daily weather summary
def calculate_daily_summary():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT city, DATE(timestamp, 'unixepoch') AS date, 
               AVG(temp) AS avg_temp, 
               MAX(temp) AS max_temp, 
               MIN(temp) AS min_temp, 
               MAX(main) AS dominant_weather
        FROM weather
        GROUP BY city, date
    ''')

    daily_summaries = cursor.fetchall()
    for summary in daily_summaries:
        city, date, avg_temp, max_temp, min_temp, dominant_weather = summary
        print(f"{date} | {city} | Avg Temp: {avg_temp:.2f}°C | Max Temp: {max_temp:.2f}°C | Min Temp: {min_temp:.2f}°C | Dominant Weather: {dominant_weather}")

    conn.close()



# Check for alerting thresholds
def check_alerts(temp, threshold=35):
    if temp > threshold:
        print(f"Alert: Temperature has exceeded {threshold}°C! Current temperature: {temp}°C")



# Plot temperature trend
def plot_temperature_trend():
    conn = sqlite3.connect('weather_data.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DATE(timestamp, 'unixepoch') AS date, AVG(temp) AS avg_temp
        FROM weather
        GROUP BY date
    ''')

    data = cursor.fetchall()
    dates = [row[0] for row in data]
    avg_temps = [row[1] for row in data]

    plt.plot(dates, avg_temps, marker='o')
    plt.xlabel('Date')
    plt.ylabel('Average Temperature (°C)')
    plt.title('Daily Average Temperature Trend')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    conn.close()



# Example usage
if __name__ == "__main__":
    api_key = "0a9bb997b003e3024debac4c3b5429cd"  # Replace with your actual OpenWeatherMap API key
    city = "Delhi"
    create_database()  # Create the database if it doesn't exist
    weather_data = fetch_weather_data(city, api_key)
    if weather_data:
        insert_weather_data(weather_data['city'], weather_data['temp'], weather_data['feels_like'],
                            weather_data['main'], weather_data['timestamp'])
        print("Weather data successfully stored in the database.")
        check_alerts(weather_data['temp'])  # Check if an alert needs to be triggered
        calculate_daily_summary()  # Calculate and display daily weather summaries
        plot_temperature_trend()  # Visualize the temperature trend
