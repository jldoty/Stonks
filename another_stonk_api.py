from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from IPython.display import display
import requests
import time

import requests
import pandas as pd
import time

# Yahoo Finance API endpoint and headers
yahoo_url = "https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/v2/get-quotes"
yahoo_headers = {
    "x-rapidapi-key": "1e2b2dc5f7emshe1fd4861fb4c1d0p1716fejsnb82cd7419bd1",
    "x-rapidapi-host": "apidojo-yahoo-finance-v1.p.rapidapi.com"
}

# Fidelity API endpoint and headers
fidelity_url = "https://fidelity-investments.p.rapidapi.com/auto-complete"
fidelity_headers = {
    "x-rapidapi-key": "1e2b2dc5f7emshe1fd4861fb4c1d0p1716fejsnb82cd7419bd1",
    "x-rapidapi-host": "fidelity-investments.p.rapidapi.com"
}

# Example stock tickers
tickers = ["TSM", "NVDA", "T", "HUBS", "HALO", "CBOE", "ANET", "AMAT", "SYM", "SNPS"]

def fetch_yahoo_data(ticker):
    try:
        response = requests.get(yahoo_url, headers=yahoo_headers, params={"symbols": ticker})
        if response.status_code == 429:  # Too Many Requests
            print(f"Rate limit exceeded for Yahoo Finance API. Waiting for 60 seconds...")
            time.sleep(60)
            return fetch_yahoo_data(ticker)
        response.raise_for_status()
        data = response.json()
        quote = data['quoteResponse']['result'][0]
        return {
            'Ticker': ticker,
            'Current Price': quote.get('regularMarketPrice', 0),
            'PE Ratio': quote.get('forwardPE', 0),
            'Dividend Yield': quote.get('dividendYield', 0),
            'EPS Recent': quote.get('epsTrailingTwelveMonths', 0),
            'Target Price': quote.get('targetMeanPrice', 0)
        }
    except Exception as e:
        print(f"Error fetching data for ticker {ticker} from Yahoo Finance: {e}")
        return {
            'Ticker': ticker,
            'Current Price': 0,
            'PE Ratio': 0,
            'Dividend Yield': 0,
            'EPS Recent': 0,
            'Target Price': 0
        }

def fetch_fidelity_data(ticker):
    try:
        response = requests.get(fidelity_url, headers=fidelity_headers, params={"query": ticker})
        if response.status_code == 429:  # Too Many Requests
            print(f"Rate limit exceeded for Fidelity API. Waiting for 60 seconds...")
            time.sleep(60)
            return fetch_fidelity_data(ticker)
        response.raise_for_status()
        data = response.json()
        # Assuming 'valuation', 'quality', and 'equityScore' are keys in the response data
        return {
            'Ticker': ticker,
            'Valuation': data.get('valuation', 0),
            'Quality': data.get('quality', 0),
            'Equity Score': data.get('equityScore', 0)
        }
    except Exception as e:
        print(f"Error fetching data for ticker {ticker} from Fidelity: {e}")
        return {
            'Ticker': ticker,
            'Valuation': 0,
            'Quality': 0,
            'Equity Score': 0
        }

# Define scoring functions based on the provided formula
def score_eps_change(eps_recent, eps_prior):
    if eps_recent > eps_prior:
        return 1
    elif eps_recent == eps_prior:
        return 0
    else:
        return -1

def score_revenue_change(revenue_recent, revenue_prior):
    if revenue_recent > revenue_prior:
        return 1
    elif revenue_recent == revenue_prior:
        return 0
    else:
        return -1

def score_target_value(current_price, target_price):
    if current_price > target_price:
        if current_price > target_price * 1.15:
            return -1
        return 0
    elif current_price >= target_price * 0.85:
        return 1
    elif current_price >= target_price * 0.50:
        return 2
    else:
        return 3

def score_valuation(valuation):
    if 1 <= valuation <= 19:
        return -2
    elif 20 <= valuation <= 39:
        return -1
    elif 40 <= valuation <= 60:
        return 0
    elif 61 <= valuation <= 80:
        return 1
    elif 81 <= valuation <= 99:
        return 2

def score_quality(quality):
    return score_valuation(quality)  # Same scoring as valuation

def score_equity_score(equity_score):
    if equity_score < 3.0:
        return -1
    elif 3.0 <= equity_score <= 7.0:
        return 0
    elif equity_score > 7.0:
        return 1

def score_pe(pe):
    if pe < 10:
        return 2
    elif 10 <= pe <= 20:
        return 1
    else:
        return 0

def score_dividend(dividend):
    if dividend < 1:
        return 0
    elif 1 <= dividend <= 10:
        return 2
    else:
        return 3

# Collect data from Yahoo Finance
yahoo_data = []
for ticker in tickers:
    data = fetch_yahoo_data(ticker)
    if data:
        yahoo_data.append(data)
    time.sleep(2)  # Add delay between requests to avoid rate limits

# Collect data from Fidelity
fidelity_data = []
for ticker in tickers:
    data = fetch_fidelity_data(ticker)
    if data:
        fidelity_data.append(data)
    time.sleep(2)  # Add delay between requests to avoid rate limits

# Merge Yahoo Finance and Fidelity data
combined_data = []
for y_data in yahoo_data:
    for f_data in fidelity_data:
        if y_data['Ticker'] == f_data['Ticker']:
            combined_data.append({**y_data, **f_data})

# Create a DataFrame from the combined data
df = pd.DataFrame(combined_data)

# Calculate buy rating
df['EPS Score'] = df.apply(lambda row: score_eps_change(row['EPS Recent'], row['EPS Recent']), axis=1)  # Mock data for EPS Prior
df['Revenue Score'] = df.apply(lambda row: score_revenue_change(row['Current Price'], row['Current Price']), axis=1)  # Mock data for Revenue
df['Target Value Score'] = df.apply(lambda row: score_target_value(row['Current Price'], row['Target Price']), axis=1)
df['Valuation Score'] = df.apply(lambda row: score_valuation(row['Valuation']), axis=1)
df['Quality Score'] = df.apply(lambda row: score_quality(row['Quality']), axis=1)
df['Equity Score'] = df.apply(lambda row: score_equity_score(row['Equity Score']), axis=1)
df['PE Score'] = df.apply(lambda row: score_pe(row['PE Ratio']), axis=1)
df['Dividend Score'] = df.apply(lambda row: score_dividend(row['Dividend Yield']), axis=1)

df['Buy Rating'] = df['EPS Score'] + df['Revenue Score'] + df['Target Value Score'] + df['Valuation Score'] + df['Quality Score'] + df['Equity Score'] + df['PE Score'] + df['Dividend Score']

# Save the DataFrame to an Excel file
output_file = 'stock_data_combined.xlsx'
df.to_excel(output_file, index=False)

print(f"Data has been written to {output_file}")
 