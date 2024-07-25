import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the Stock Information Website!"

if __name__ == '__main__':
    app.run(debug=True)

#need rapidapi item
#fidelity
def get_stock_data(symbol):
    ts = TimeSeries(key='e2b2dc5f7emshe1fd4861fb4c1d0p1716fejsnb82cd7419bd1')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min')
    return data

#yahoo
def get_stock_data(symbol):
    ts = TimeSeries(key='e2b2dc5f7emshe1fd4861fb4c1d0p1716fejsnb82cd7419bd1')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min')
    return data




<!-- templates/index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Stock Information</title>
</head>
<body>
    <h1>Stock Information for {{ symbol }}</h1>
    <pre>{{ stock_data }}</pre>
</body>
</html>

from flask import render_template

@app.route('/stock/<symbol>')
def stock(symbol):
    data = get_stock_data(symbol)
    return render_template('index.html', symbol=symbol, stock_data=data)

# app.py


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

Flask==2.0.1
#this shoyld be the reapid api
alpha_vantage==2.3.1

# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]

docker build -t flask-stock-app .

docker run -p 5000:5000 flask-stock-app
