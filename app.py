from flask import Flask, render_template
import yfinance as yf
from datetime import datetime
import pytz

app = Flask(__name__)

def get_prices(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")

    try:
        name = stock.info.get('shortName', 'N/A')
    except:
        name = 'N/A'

    if len(hist) >= 2:
        prev_close = hist['Close'][-2]
        current_price = hist['Close'][-1]
        diff = current_price - prev_close
    else:
        prev_close = None
        current_price = None
        diff = None

    return {
        'ticker': ticker,
        'name': name,
        'prev_close': round(prev_close, 2) if prev_close else 'N/A',
        'current_price': round(current_price, 2) if current_price else 'N/A',
        'diff': round(diff, 2) if diff else 'N/A'
    }

@app.route('/')
def index():
    with open('tickers.txt') as f:
        tickers = [line.strip() for line in f if line.strip()]
    
    prices = [get_prices(ticker) for ticker in tickers]

    # 日本時間で現在日時を取得
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst).strftime('%Y/%m/%d %H:%M:%S')

    return render_template('index.html', prices=prices, now=now)

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=10000)
