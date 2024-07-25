import requests
from bs4 import BeautifulSoup
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from IPython.display import display
import http.client

conn = http.client.HTTPSConnection("yahoo-finance160.p.rapidapi.com")

payload = "{\"messages\":[{\"role\":\"user\",\"content\":\"should i buy tesla\"}],\"stock\":\"TSLA\",\"conversation_id\":\"\",\"period\":\"1mo\"}"

headers = {
    'x-rapidapi-key': "e2b2dc5f7emshe1fd4861fb4c1d0p1716fejsnb82cd7419bd1",
    'x-rapidapi-host': "yahoo-finance160.p.rapidapi.com",
    'Content-Type': "application/json"
}

conn.request("POST", "/finbot", payload, headers)

res = conn.getresponse()
data = res.read()

tickers = ["TSM", "NVDA", "T", "HUBS", "HALO", "CBOE", "ANET", "AMAT", "SYM", "SNPS"]

for ticker in tickers:
   try:
    stock = yf.Ticker(ticker)
    # Get stock info
    info = stock.info
   
   #retrieve values using get() method for each key
    info.get('Ticker', 'Current Price', 'regularMarketPrice', 'PE Ratio', 'forwardPE', 'Dividend Yield', )
    current_price = info.get('regularMarketPrice', 'N/A')
    dividend_yield = info.get('dividendYield', 'N/A')
    pe_ratio = info.get('forwardPE', 'N/A')
    revenue_recent = info.get('current revenue', 'N/A')
 

    #print the stock information       
    print(f"Ticker: {ticker}, Current Price: {info['regularMarketPrice']}, PE Ratio: {info['forwardPE']}, Dividend Yield: {info['dividendYield']}")
    print(f"Ticker: {ticker}, Current Price: Data not available")
    
    # Get historical market data
    hist = stock.history(period="1y")
    
    if not hist.empty:
            eps_recent = hist['Close'].iloc[-1]
            eps_prior = hist['Close'].iloc[-2]
            print(f"EPS Recent: {eps_recent}, EPS Prior: {eps_prior}")
    else:
            print(f"Ticker: {ticker}, Historical data not available")
    
    #except Exception as e:
    print(f"Error fetching data for ticker {ticker}: {e}")
    
    # Access specific data
    eps_recent = hist.iloc[-1]['Close']
    eps_prior = hist.iloc[-2]['Close']
    print(f"EPS Recent: {eps_recent}, EPS Prior: {eps_prior}")
    #else:
    #print(f"Ticker: {ticker}, Historical data not available")

   except Exception as e:
        print(f"Error fetching data for ticker {ticker}: {e}")         

df = pd.DataFrame(data)

# Define scoring functions
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

# Apply scoring functions and calculate buy rating
df['EPS Score'] = df.apply(lambda row: score_eps_change(row['EPS Recent'], row['EPS Prior']), axis=1)
df['Revenue Score'] = df.apply(lambda row: score_revenue_change(row['Revenue Recent'], row['Revenue Prior']), axis=1)
df['Target Value Score'] = df.apply(lambda row: score_target_value(row['Current Price'], row['Target Price']), axis=1)
df['Valuation Score'] = df.apply(lambda row: score_valuation(row['Valuation']), axis=1)
df['Quality Score'] = df.apply(lambda row: score_quality(row['Quality']), axis=1)
df['Equity Score'] = df.apply(lambda row: score_equity_score(row['Equity Score']), axis=1)
df['PE Score'] = df.apply(lambda row: score_pe(row['PE']), axis=1)
df['Dividend Score'] = df.apply(lambda row: score_dividend(row['Dividend']), axis=1)

df['Buy Rating'] = df['EPS Score'] + df['Revenue Score'] + df['Target Value Score'] + df['Valuation Score'] + df['Quality Score'] + df['Equity Score'] + df['PE Score'] + df['Dividend Score']

# Display the data in a table
display(df[['Ticker', 'Current Price', 'Buy Rating', 'EPS Score', 'Revenue Score', 'Target Value Score', 'Valuation Score', 'Quality Score', 'Equity Score', 'PE Score', 'Dividend Score']])

def write_to_excel(data, filename=r"C:\Users\Dad\Desktop\Python Tests\stonk.xlsx"):
    df = pd.DataFrame(data, columns=["Stock Symbol", "Analysis", "Earnings Data"])
    df.to_excel(filename, index=False)

if __name__ == "__main__":
    symbol = "ACA"
    data = scrape_earnings(symbol)
    write_to_excel([data])
    print(f"Analysis for {symbol} completed. Results saved to stonk.xlsx.")
