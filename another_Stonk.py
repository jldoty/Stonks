import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from IPython.display import display

symbol = ["TSM", "NVDA", "T", "HUBS", "HALO", "CBOE", "ANET", "AMAT", "SYM", "SNPS"]

def get_stock_data(symbol):
    ts = TimeSeries(key='e2b2dc5f7emshe1fd4861fb4c1d0p1716fejsnb82cd7419bd1')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min')
    return data


tickers = ["TSM", "NVDA", "T", "HUBS", "HALO", "CBOE", "ANET", "AMAT", "SYM", "SNPS"]

all_data = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        # Get stock info
        info = stock.info
        # Add ticker symbol to the info dictionary
        info['Ticker'] = ticker
        all_data.append(info)

        # Print all data fields
        print(f"Data for {ticker} added successfully.")

        for key, value in info.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {e}")
#Check if all_data contains the collected data
print("Collected data:", all_data)

# Create a DataFrame from the collected data
df = pd.DataFrame(all_data)

# Save the DataFrame to an Excel file
output_file = 'stock_data_yapi.xlsx'
df.to_excel(output_file, index=False)

print(f"Data has been written to {output_file}")

# Retrieve values using get() method for each key
current_price = info.get('currentPrice', 'N/A')
pe_ratio = info.get('forwardPE', 'N/A')
dividend_yield = info.get('dividendRate', 'N/A')

# Print the stock information
print(f"Ticker: {ticker}, Current Price: {current_price}, PE Ratio: {pe_ratio}, Dividend Yield: {dividend_yield}")

# Get historical market data
hist = stock.history(period="1y")
        
if not hist.empty:
            eps_recent = hist['Close'].iloc[-1]
            eps_prior = hist['Close'].iloc[-2]
            print(f"EPS Recent: {eps_recent}, EPS Prior: {eps_prior}")
else:
            print(f"Ticker: {ticker}, Historical data not available")
    #except Exception as e:
    #    print(f"Error fetching data for ticker {ticker}: {e}")


def write_to_excel(data, filename=r"C:\Users\Dad\Desktop\Python Tests\stonk.xlsx"):
    df = pd.DataFrame(data, columns=["Stock Symbol", "Analysis", "Earnings Data"])
    df.to_excel(filename, index=False)