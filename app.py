from flask import Flask, render_template
import yfinance as yf
from datetime import datetime
import pytz
import os

app = Flask(__name__)

def get_prices(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="2d")

    # 企業名（または投資信託名）を取得
    try:
        name = stock.info.get('shortName', 'N/A')
    except:
        name = 'N/A'

    # 株価履歴から前日終値と現在価格を取得
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
        'prev_close': round(prev_close, 2) if prev_close else None,
        'current_price': round(current_price, 2) if current_price else None,
        'diff': round(diff, 2) if diff else None
    }

@app.route('/')
def index():
    # tickers.txtから銘柄コードを読み込み
    with open('tickers.txt', encoding='utf-8') as f:
        tickers = [line.strip() for line in f if line.strip()]

    # 各銘柄の株価情報を取得
    prices = [get_prices(ticker) for ticker in tickers]

    # 差額が大きい順に並び替え（None は最下位）
    prices = sorted(prices, key=lambda x: x['diff'] if isinstance(x['diff'], (int, float)) else -9999, reverse=True)

    # サマリー計算
    total = len(prices)
    up_count = sum(1 for p in prices if isinstance(p['diff'], (int, float)) and p['diff'] > 0)
    down_count = sum(1 for p in prices if isinstance(p['diff'], (int, float)) and p['diff'] < 0)
    valid_diffs = [p['diff'] for p in prices if isinstance(p['diff'], (int, float))]
    avg_diff = round(sum(valid_diffs) / len(valid_diffs), 2) if valid_diffs else None

    # 現在時刻（JST）
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst).strftime('%Y/%m/%d %H:%M:%S')

    return render_template(
        'index.html',
        prices=prices,
        now=now,
        total=total,
        up_count=up_count,
        down_count=down_count,
        avg_diff=avg_diff
    )

if __name__ == '__main__':
    # Renderやローカル両方に対応
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
