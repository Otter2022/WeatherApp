from flask import Flask, render_template, request
import os
import requests
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, template_folder='template')
secret_key = os.getenv('SECRET_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    chart_data = {
        'labels': ['day 1', 'day 2', 'day 3', 'day 4', 'day 5'],
        'datasets': [{
            'label': 'Average Temperature (Fahrenheit)',
            'data': [0, 0, 0, 0, 0],
            'backgroundColor': 'rgba(75, 192, 192, 0.2)',
            'borderColor': 'rgba(75, 192, 192, 1)',
            'borderWidth': 1
        }]
    }
    city_info = {
        'name': '',
        'country': '',
        'population': ''
    }
    weather_info = {
        'weather': '',
        'description': '',
        'icon': '',
        'wind_speed': '',
        'wind_deg': ''
    }

    if request.method == 'POST':
        if not secret_key:
            return "Error: SECRET_KEY is not set in the environment variables.", 405

        location = request.form.get('location')
        if location  and location.isdigit():
            url = f"https://api.openweathermap.org/data/2.5/forecast?zip={location},us&appid={secret_key}"
        else:
            url = f"https://api.openweathermap.org/data/2.5/forecast?q={location}&appid={secret_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            return "Error: Location not found", 500

        data = response.json()
        if response.status_code != 200:
            return f"Error fetching data from the weather API: {response.status_code}", 405

        records = [{'dt_txt': item['dt_txt'], 'temp': item['main']['temp']} for item in data['list']]
        df = pd.DataFrame(records)
        df['date'] = df['dt_txt'].str.split(' ').str[0]
        df = df.drop_duplicates(subset='date').reset_index(drop=True)

        temps_list = [(i - 273.15) * 9 / 5 + 32 for i in df['temp'].tolist()]
        dates_list = df['date'].tolist()

        chart_data = {
            'labels': dates_list,
            'datasets': [{
                'label': 'Average Temperature (Fahrenheit)',
                'data': temps_list,
                'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                'borderColor': 'rgba(75, 192, 192, 1)',
                'borderWidth': 1
            }]
        }

        if 'city' in data:
            city_info = {
                'name': data['city']['name'],
                'country': data['city']['country'],
                'population': data['city']['population']
            }

        if 'list' in data and len(data['list']) > 0:
            first_entry = data['list'][0]
            weather_info = {
                'weather': first_entry['weather'][0]['main'],
                'description': first_entry['weather'][0]['description'],
                'icon': first_entry['weather'][0]['icon'],#test icon
                'wind_speed': first_entry['wind']['speed'],
                'wind_deg': first_entry['wind']['deg']
            }

    return render_template('WeatherTemplate.html', data=chart_data, city_info=city_info, weather_info=weather_info)

if __name__ == '__main__':
    app.run(port=8000)

