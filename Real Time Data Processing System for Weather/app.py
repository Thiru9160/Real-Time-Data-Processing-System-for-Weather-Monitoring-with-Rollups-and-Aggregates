from flask import Flask, render_template, request, Response
import mysql.connector
import pandas as pd
import plotly.graph_objs as go
import matplotlib.pyplot as plt
import io

app = Flask(__name__)

# Connect to the MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Thirumalesh9160@',
    database='weather_monitoring'
)

cursor = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather/<city>')
def weather(city):
    query = '''
        SELECT temperature, feels_like, weather, timestamp
        FROM weather_data
        WHERE city = %s
        ORDER BY timestamp DESC
        LIMIT 1
    '''
    cursor.execute(query, (city,))
    data = cursor.fetchone()
    
    if data:
        temperature, feels_like, weather_condition, timestamp = data
        return render_template('weather.html', city=city, temperature=temperature, feels_like=feels_like, weather_condition=weather_condition, timestamp=timestamp)
    else:
        return f"No data available for {city}."

@app.route('/summary/<city>')
def summary(city):
    query = '''
        SELECT avg_temp, max_temp, min_temp, dominant_weather, date
        FROM daily_summaries
        WHERE city = %s
        ORDER BY date DESC
        LIMIT 7
    '''
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    
    return render_template('summary.html', city=city, summaries=data)

@app.route('/alerts/<city>')
def alerts(city):
    query = '''
        SELECT alert_type, message, timestamp
        FROM alerts
        WHERE city = %s
        ORDER BY timestamp DESC
    '''
    cursor.execute(query, (city,))
    alerts = cursor.fetchall()
    
    return render_template('alerts.html', city=city, alerts=alerts)

@app.route('/visualize/<city>')
def visualize(city):
    # Fetch the daily summaries for the past week
    query = '''
        SELECT date, avg_temp, max_temp, min_temp
        FROM daily_summaries
        WHERE city = %s
        ORDER BY date DESC
        LIMIT 7
    '''
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    
    # Convert to a Pandas DataFrame for easier plotting
    df = pd.DataFrame(data, columns=['date', 'avg_temp', 'max_temp', 'min_temp'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Create Plotly graph objects
    fig = go.Figure()
    
    # Average temperature line
    fig.add_trace(go.Scatter(x=df['date'], y=df['avg_temp'], mode='lines', name='Avg Temp'))
    
    # Max temperature line
    fig.add_trace(go.Scatter(x=df['date'], y=df['max_temp'], mode='lines', name='Max Temp'))
    
    # Min temperature line
    fig.add_trace(go.Scatter(x=df['date'], y=df['min_temp'], mode='lines', name='Min Temp'))
    
    # Customize the layout
    fig.update_layout(
        title=f"Temperature Trends for {city}",
        xaxis_title='Date',
        yaxis_title='Temperature (°C)'
    )
    
    # Render the graph in an HTML template
    graph_html = fig.to_html(full_html=False)
    
    return render_template('visualize.html', city=city, graph_html=graph_html)

@app.route('/matplotlib/<city>.png')
def matplotlib_plot(city):
    query = '''
        SELECT date, avg_temp, max_temp, min_temp
        FROM daily_summaries
        WHERE city = %s
        ORDER BY date DESC
        LIMIT 7
    '''
    cursor.execute(query, (city,))
    data = cursor.fetchall()
    
    # Convert data to Pandas DataFrame
    df = pd.DataFrame(data, columns=['date', 'avg_temp', 'max_temp', 'min_temp'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['avg_temp'], label='Avg Temp')
    plt.plot(df['date'], df['max_temp'], label='Max Temp')
    plt.plot(df['date'], df['min_temp'], label='Min Temp')
    
    plt.title(f"Temperature Trends for {city}")
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    
    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    return Response(buffer, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
