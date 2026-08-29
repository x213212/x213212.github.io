---
title: "bitcoin auto trade"
date: "2024-06-10T04:02:00.002+08:00"
updated: "2024-06-10T04:02:25.263+08:00"
permalink: "/2024/06/bitcoin-auto-trade.html"
original_url: "https://x8795278.blogspot.com/2024/06/bitcoin-auto-trade.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-642590887483562883"
tags: ["bitcoin"]
layout: post
---

![](https://hackmd.io/_uploads/rkFi_tXHA.png)

# bitcoin auto trade
![image](https://hackmd.io/_uploads/rJG2zFXB0.png)
最近無聊將交易策略從股票移動到幣安上，來看看24小時不斷交易放著一個月如何
功能大概實現有
每分鐘監控前一百檔成交量高的貨幣
![image](https://hackmd.io/_uploads/HkerXK7BR.png)
支持現貨/合約開單，可以指定任意槓桿倍數
支持一鍵快速逃命出清合約和現貨
交易資料都記錄在DB,使用chart.js可以標記合約和現貨買賣點
下面湊一湊應該都可以自己寫出自動交易程式
額外提供一個回測框架可以快速驗證策略是否在合適的買賣點
如果要實戰的話就用可以用和合約現貨的API直接呼叫，記得要開啟幣安API
![image](https://hackmd.io/_uploads/HyFbPYQHR.png)
因為自動交易，所以架設在GCP,改良了一下策略在第8天運算量和網路終於減小到一天2NT，用最破的機器，硬碟20G，大概一個月7U
![image](https://hackmd.io/_uploads/H10CLKmBC.png)
![image](https://hackmd.io/_uploads/rkFi_tXHA.png)
現在晚上終於可以好好睡一覺不會被雷了，只公開部分程式碼，策略參數沒提供，切勿實戰
```python
import ccxt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

initial_fixed_amount = 1000
initial_contract_fixed_amount = 150

def calculate_obv(data):
    obv = (np.sign(data['close'].diff()) * data['volume']).fillna(0).cumsum()
    return obv

def calculate_obv_slope(data, window):
    obv_slope = data['obv'].rolling(window=window).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
    return obv_slope

def fetch_15min_data(symbol, since=None, limit=3000):
    binance = ccxt.binance()
    ohlcv = binance.fetch_ohlcv(symbol, timeframe='1m', since=since, limit=limit)
    return ohlcv

def calculate_rsi(data, window):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_signals(data):
    volume_threshold = data['volume'].rolling(window=20).mean() * 1.5
    buy_condition = (
 
        (data['macd'] > data['signal_line']) & 

    )

    sell_condition = (

        (data['macd'] < data['signal_line']) & 
   
    )
    data['signal'] = 0.0
    data.loc[buy_condition, 'signal'] = 1.0
    data.loc[sell_condition, 'signal'] = -1.0
    data['position'] = data['signal'].diff()

    return data

def preprocess_data(data):
    latest_df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    latest_df['timestamp'] = pd.to_datetime(latest_df['timestamp'], unit='ms')

    data = latest_df

    data.set_index('timestamp', inplace=True)
    data_15min = data.resample('15min').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna().reset_index()

    data_15min[['open', 'high', 'low', 'close', 'volume']] = data_15min[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return data_15min

def mark_volatile_periods(data):
    threshold = 0.5 
    data['volatile'] = (data['close'].pct_change().abs() > threshold).astype(int)
    return data

def backtest_strategy(data):
    initial_capital = 1000
    capital = initial_capital
    num_coins = 0
    buy_signals = []
    sell_signals = []

    print(len(data))
    data = generate_signals(data)
    data = mark_volatile_periods(data)
    for i in range(len(data)):
        if data['position'].iloc[i] == 1:
            buy_price = data['close'].iloc[i]
            num_coins = capital / buy_price
            capital -= num_coins * buy_price
            buy_signals.append((data['timestamp'].iloc[i], buy_price))
        elif data['position'].iloc[i] == -1:
            sell_price = data['close'].iloc[i]
            capital += num_coins * sell_price
            num_coins = 0
            sell_signals.append((data['timestamp'].iloc[i], sell_price))

    final_capital = capital + (num_coins * data['close'].iloc[-1])
    roi = (final_capital - initial_capital) / initial_capital

    return data, initial_capital, final_capital, roi, buy_signals, sell_signals

def plot_and_save(data, window, buy_signals, sell_signals):
    data = generate_signals(data)
    data = mark_volatile_periods(data)

    plt.figure(figsize=(14, 10))

    plt.subplot(4, 1, 1)
    plt.plot(data['timestamp'], data['close'], label='Close Price')
    plt.title(f'Close Price')
    plt.legend()

    plt.subplot(4, 1, 2)
    plt.plot(data['timestamp'], data['obv'], label='OBV', color='orange')
    plt.title('On-Balance Volume (OBV)')
    plt.legend()

    plt.subplot(4, 1, 3)
    plt.plot(data['timestamp'], data['obv_slope'], label='OBV Slope', color='green')
    plt.title('OBV Slope')
    plt.legend()

    plt.subplot(4, 1, 4)
    plt.plot(data['timestamp'], data['close'], label='Close Price')
    plt.scatter(data['timestamp'][data['volatile'] == 1], data['close'][data['volatile'] == 1], color='red', label='Volatile')
    plt.title('Volatile Periods')
    plt.legend()

    for signal in buy_signals:
        plt.subplot(4, 1, 1)
        plt.plot(signal[0], signal[1], 'g^', markersize=10)

    for signal in sell_signals:
        plt.subplot(4, 1, 1)
        plt.plot(signal[0], signal[1], 'rv', markersize=10)

    plt.tight_layout()
    plt.savefig('obv_slope_chart.png')

symbol = 'CHZ/USDT'
data = fetch_15min_data(symbol)
data = preprocess_data(data)
print(len(data))
data, initial_capital, final_capital, roi, buy_signals, sell_signals = backtest_strategy(data)

print(f'初始資本: {initial_capital}')
print(f'最終資本: {final_capital}')
print(f'投資回報率 (ROI): {roi}')

plot_and_save(data, 14, buy_signals, sell_signals)
```
# 市場
```python
import ccxt
import pandas as pd
import datetime as dt

# 初始化幣安API
binance = ccxt.binance({
    'apiKey': 'api',
    'secret': 'api',
    'timeout': 30000,  # 增加超時時間到30秒
    'enableRateLimit': True,
    'adjustForTimeDifference': True
    # ,  # 启用时间同步
    # 'proxies': {
    #     'http': 'http://213:124/',
    #     'https': 'http://124:124/',
    # }
})

def fetch_ohlcv(symbol, timeframe='1m', since=None, limit=1000):
    all_ohlcv = []
    while True:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe, since, limit)
        if len(ohlcv) == 0:
            break
        all_ohlcv.extend(ohlcv)
        since = ohlcv[-1][0] + 1  # 更新 since 為上次數據的最後一個時間點
        if len(ohlcv) < limit:
            break
    return pd.DataFrame(all_ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# 計算六個月前的時間戳
now = dt.datetime.now()
six_months_ago = now - dt.timedelta(days=360)
since_timestamp = int(six_months_ago.timestamp() * 1000)

# 前五十大加密貨幣對USDT
# top_50_coins = [
#     'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT', 'SOL/USDT', 'DOT/USDT', 'DOGE/USDT', 'AVAX/USDT', 'LINK/USDT', 
#     'LUNA/USDT', 'UNI/USDT', 'MATIC/USDT', 'ICP/USDT', 'SXP/USDT', 'FIL/USDT', 'LTC/USDT', 'ALGO/USDT', 'ATOM/USDT', 'CHZ/USDT', 
#     'ETC/USDT', 'VET/USDT', 'TRX/USDT', 'THETA/USDT', 'XMR/USDT', 'AAVE/USDT', 'EGLD/USDT', 'EOS/USDT', 'NEO/USDT', 'XTZ/USDT', 
#     'CAKE/USDT', 'WAVES/USDT', 'NEAR/USDT', 'HBAR/USDT', 'MKR/USDT', 'GRT/USDT', 'ONT/USDT', 'BCH/USDT', 'SUSHI/USDT', 'COMP/USDT', 
#     'TFUEL/USDT', 'ICX/USDT', 'RUNE/USDT', 'DASH/USDT', 'ZEC/USDT', 'MANA/USDT', 'HOT/USDT', 'SC/USDT', 'QTUM/USDT', 'IOST/USDT'
# ]
top_50_coins =  ['BTC/USDT', 'ETH/USDT', '1000PEPE/USDT', 'LUNA/USDT', 'ZEC/USDT', 'SOL/USDT', 'NOT/USDT', 'PEOPLE/USDT', 'USDC/USDT', 'JASMY/USDT', 'ORDI/USDT', 'PEPE/USDT', 'WIF/USDT', 'DOGE/USDT', '1000SHIB/USDT', 'ALICE/USDT', 'TURBO/USDT', '1000BONK/USDT', 'BEAMX/USDT', 'FDUSD/USDT', '1000FLOKI/USDT', 'XRP/USDT', 'BB/USDT', 'WLD/USDT', 'LINK/USDT', 'BNB/USDT', 'UNI/USDT', 'BOME/USDT', 'ENA/USDT', 'ETHFI/USDT', 'STG/USDT', 'HIGH/USDT', 'ONDO/USDT', 'NEAR/USDT', 'LDO/USDT', 'ARB/USDT', 'AVAX/USDT', 'AUCTION/USDT', 'ENS/USDT', 'ETC/USDT', 'AR/USDT', 'BONK/USDT', 'FLOKI/USDT', 'FIL/USDT', 'MATIC/USDT', 'BCH/USDT', 'OMNI/USDT', 'ADA/USDT', 'FRONT/USDT', 'DOT/USDT', 'TIA/USDT', 'FTM/USDT', 'SHIB/USDT', '1000SATS/USDT', 'ARKM/USDT', 'LTC/USDT', 'OP/USDT', 'ENJ/USDT', 'FET/USDT', 'GALA/USDT', 'RNDR/USDT', 'LUNA2/USDT', '1INCH/USDT', 'TRB/USDT', 'AEVO/USDT', 'STX/USDT', 'W/USDT', 'CHZ/USDT', 'INJ/USDT', 'XAI/USDT', 'JTO/USDT', '1000RATS/USDT', 'EOS/USDT', 'SUI/USDT', 'TNSR/USDT', 'SAGA/USDT', 'APT/USDT', 'ATOM/USDT', 'OM/USDT', 'STRAX/USDT', 'SPELL/USDT', 'PENDLE/USDT', 'BIGTIME/USDT', 'PYTH/USDT', 'MEME/USDT', 'LPT/USDT', 'RUNE/USDT', 'TRU/USDT', 'REZ/USDT', 'MTL/USDT', 'ROSE/USDT', '1000LUNC/USDT', 'DGB/USDT', 'AGIX/USDT', 'PIXEL/USDT', 'BLUR/USDT', 'DYDX/USDT', 'GMX/USDT', 'TON/USDT', 'CRV/USDT', 'GMT/USDT', 'MKR/USDT', 'THETA/USDT', 'MYRO/USDT', 'SAND/USDT', 'VGX/USDT', 'GRT/USDT', 'AAVE/USDT', 'JUP/USDT', 'SNT/USDT', 'MANTA/USDT', 'ICP/USDT', 'SEI/USDT', 'AXS/USDT', 'BEL/USDT', 'EDU/USDT', 'DUSK/USDT']
for coin in top_50_coins:
    coin_data = fetch_ohlcv(coin, '1m', since=since_timestamp)
    coin_data['timestamp'] = pd.to_datetime(coin_data['timestamp'], unit='ms')
    coin_symbol = coin.replace('/USDT', '')
    coin_data.to_csv(f'./data/{coin_symbol}_ohlcv_last_6_months.csv', index=False)

print("抓取完成")

```

# 現貨
```python
import ccxt
import pandas as pd

# 初始化幣安API
binance = ccxt.binance({
    'apiKey': 'api',
    'secret': 'api',
    'timeout': 30000,  # 增加超時時間到30秒
    'enableRateLimit': True,
    'adjustForTimeDifference': True
})

def fetch_current_price(symbol):
    ticker = binance.fetch_ticker(symbol)
    return ticker['last']

def fetch_min_notional(symbol):
    markets = binance.load_markets()
    market = markets[symbol]
    return market['limits']['cost']['min']

def place_market_order(symbol, side, amount):
    return binance.create_market_order(symbol, side, amount)

# 抓取當前ADA價格
symbol = 'ADA/USDT'
current_price = fetch_current_price(symbol)
print(f"當前ADA價格: {current_price}")

# 抓取ADA/USDT的最小交易金額
min_notional = fetch_min_notional(symbol)
print(f"ADA/USDT 最小交易金額: {min_notional} USDT")

# 确保10 USDT 大于最小交易金额
usdt_amount = 10
if usdt_amount < min_notional:
    raise ValueError(f"交易金額低於最小限制：{min_notional} USDT")

# 計算10 USDT可以購買多少ADA
ada_amount = usdt_amount / current_price
print(f"10 USDT 可以購買 {ada_amount} ADA")

# 進行市場訂單購買ADA
order = place_market_order(symbol, 'buy', ada_amount)
print(order)
print("抓取完成並已下單")
# #print(order)
# sell_order = place_market_order(symbol, 'sell', ada_amount)
# print("賣出完成")
# print(sell_order)

```
# 合約
```python
import ccxt
import pandas as pd
import datetime as dt
import time
import hmac 
import hashlib
import requests
import logging
import pytz

# 初始化日誌記錄
logging.basicConfig(filename='contract_trading.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 初始化幣安API
binance = ccxt.binance({
    'apiKey': 'api',
    'secret': 'api',
    'timeout': 30000,  # 增加超時時間到30秒
    'enableRateLimit': True,
    'adjustForTimeDifference': True,
    'options': {
        'defaultType': 'future',  # 確保使用期貨 API
    },
})

# 載入市場資料
binance.load_markets()

# 查詢所有可用的槓桿
def get_all_leverage(symbol):
    market = binance.market(symbol)
    response = binance.fapiPrivateGetLeverageBracket({'symbol': market['id']})
    leverages = [bracket['initialLeverage'] for bracket in response[0]['brackets']]
    return leverages

# 獲取最新期貨價格
def get_latest_future_price(symbol):
    ticker = binance.fapiPublicGetTickerPrice({'symbol': binance.market_id(symbol)})
    return float(ticker['price'])

# 獲取台灣時間
def get_taiwan_time():
    utc_now = dt.datetime.now(dt.timezone.utc)
    taiwan_tz = pytz.timezone('Asia/Taipei')
    return utc_now.astimezone(taiwan_tz).strftime('%Y-%m-%d %H:%M:%S')

# 開倉
# def open_contract(symbol, side, amount, leverage, stop_loss_price=None):
#     market = binance.market(symbol)
#     binance.fapiPrivatePostLeverage({'symbol': market['id'], 'leverage': leverage})
#     order = binance.create_order(symbol, 'market', side, amount)
#     logging.info(f"{get_taiwan_time()} - 開倉成功: {side} {symbol} {amount} @ {order['price']}, 槓桿: {leverage}")
    
#     if stop_loss_price:
#         stop_loss_side = 'sell' if side == 'buy' else 'buy'
#         stop_loss_order = binance.create_order(symbol, 'stop_market', stop_loss_side, amount, None, {'stopPrice': stop_loss_price})
#         logging.info(f"{get_taiwan_time()} - 設置止損: {stop_loss_side} {symbol} {amount} @ {stop_loss_price}")
    
#     return order
def open_contract(symbol, side, amount, leverage, margin_type='ISOLATED'):
    market = binance.market(symbol)
    
    try:
        # 設置槓桿
        binance.fapiPrivatePostLeverage({'symbol': market['id'], 'leverage': leverage})
    except ccxt.BaseError as e:
        logging.error(f"Error setting leverage: {str(e)}")
  
    try:
        # 創建訂單
        order = binance.create_order(symbol, 'market', side, amount)
        logging.info(f"{get_taiwan_time()} - 開倉成功: {side} {symbol} {amount} @ {order['price']}, 槓桿: {leverage}, 保證金模式: {margin_type}")
        return order
    except ccxt.BaseError as e:
        logging.error(f"Error creating order: {str(e)}")
        return None

# 關倉
def close_contract(symbol, amount=None):
    positions = binance.fapiPrivateV2GetPositionRisk()
    for position in positions:
        if position['symbol'] == binance.market(symbol)['id'] and float(position['positionAmt']) != 0:
            side = 'sell' if float(position['positionAmt']) > 0 else 'buy'
            print(side)
            current_amount = abs(float(position['positionAmt']))
            amount_to_close = current_amount if amount is None else min(amount, current_amount)
            order = binance.create_order(symbol, 'market', side, amount_to_close)
            logging.info(f"{get_taiwan_time()} - 關倉成功: {side} {symbol} {amount_to_close} @ {order['price']}")
            print(f"Closed {side} position of {amount_to_close} {symbol}")

# 設置止損單
def set_stop_loss(symbol, side, amount, stop_loss_price):
    stop_loss_side = 'sell' if side == 'buy' else 'buy'
    stop_loss_order = binance.create_order(symbol, 'STOP_MARKET', stop_loss_side, amount, None, {'stopPrice': stop_loss_price})
    logging.info(f"{get_taiwan_time()} - 設置止損: {stop_loss_side} {symbol} {amount} @ {stop_loss_price}")

# 取消所有止損單
def cancel_all_stop_orders(symbol):
    open_orders = binance.fetch_open_orders(symbol)
    for order in open_orders:
        if order['type'] == 'stop_market':
            binance.cancel_order(order['id'], symbol)
            logging.info(f"{get_taiwan_time()} - 取消止損單: {order['side']} {symbol} {order['amount']} @ {order['price']}")

# 重新設置止損單
def reset_stop_loss(symbol, side, amount, new_stop_loss_price):
    cancel_all_stop_orders(symbol)
    set_stop_loss(symbol, side, amount, new_stop_loss_price)

# 計算強平價格
def get_liquidation_prices(symbol, entry_price, amount, leverage):
    entry_price = float(entry_price)
    leverage = float(leverage)
    initial_margin = amount / leverage  # 初始保證金，以USDT計算
    maintenance_margin = initial_margin * 0.005  # 維持保證金，假設為初始保證金的0.5%
    
    # 多倉強平價格
    liquidation_price_long = entry_price * (1 - (initial_margin + maintenance_margin) / amount)

    # 空倉強平價格
    liquidation_price_short = entry_price * (1 + (initial_margin + maintenance_margin) / amount)

    return liquidation_price_long, liquidation_price_short, initial_margin

# 計算特定symbol的未實現盈虧
def calculate_unrealized_pnl(symbol):
    positions = binance.fapiPrivateV2GetPositionRisk()
    for position in positions:
        if position['symbol'] == binance.market(symbol)['id'] and float(position['positionAmt']) != 0:
            entry_price = float(position['entryPrice'])
            current_price = get_latest_future_price(symbol)
            amount = float(position['positionAmt'])
            # 計算未實現盈虧
            if amount > 0:
                pnl = (current_price - entry_price) * amount
            else:
                pnl = (entry_price - current_price) * abs(amount)
            pnl_percentage = (pnl / (entry_price * abs(amount))) * 100
            print(f"Symbol: {symbol}, Position: {amount}, Entry Price: {entry_price}, Current Price: {current_price}, PnL: {pnl}, PnL Percentage: {pnl_percentage}%")
            logging.info(f"{get_taiwan_time()} - Symbol: {symbol}, Position: {amount}, Entry Price: {entry_price}, Current Price: {current_price}, PnL: {pnl}, PnL Percentage: {pnl_percentage}%")
def calculate_unrealized_pnl(symbol):
    positions = binance.fapiPrivateV2GetPositionRisk()
    for position in positions:
        if position['symbol'] == binance.market(symbol)['id'] and float(position['positionAmt']) != 0:
            print(position)
            entry_price = float(position['entryPrice'])
            current_price = get_latest_future_price(symbol)
            amount = float(position['positionAmt'])
            # 計算未實現盈虧
            if amount > 0:
                pnl = (current_price - entry_price) * amount
            else:
                pnl = (entry_price - current_price) * abs(amount)
            pnl_percentage = (pnl / (entry_price * abs(amount))) * 100
            print(f"Symbol: {symbol}, Position: {amount}, Entry Price: {entry_price}, Current Price: {current_price}, PnL: {pnl}, PnL Percentage: {pnl_percentage}%")
            logging.info(f"{get_taiwan_time()} - Symbol: {symbol}, Position: {amount}, Entry Price: {entry_price}, Current Price: {current_price}, PnL: {pnl}, PnL Percentage: {pnl_percentage}%")
            return pnl, pnl_percentage
    return 0, 0
# 示例使用
symbol = 'ORDI/USDT'
leverages = get_all_leverage(symbol)
max_leverage = max(leverages)
print(f"可用槓桿: {leverages}")
print(f"最大槓桿: {max_leverage}")

# 獲取最新期貨價格
entry_price = get_latest_future_price(symbol)
print(f"最新期貨價格: {entry_price}")

# 假設入倉資金量
capital =0.240  # 以USDT計算

# 計算多倉和空倉的強平價格及初始保證金
for get_leverage in leverages:
    print(f"槓桿: {get_leverage}")
    liquidation_price_long, liquidation_price_short, initial_margin = get_liquidation_prices(symbol, entry_price, capital, get_leverage)
    print(f"初始保證金: {initial_margin}")
    print(f"多倉強平價格: {liquidation_price_long}")
    print(f"空倉強平價格: {liquidation_price_short}")

# 設置初始止損價格
stop_loss_price = entry_price * 0.95  # 例如：止損設置為買入價格的95%

# 開啟合約並設置止損
max_leverage = 5
# order = open_contract(symbol, 'buy', capital / entry_price, max_leverage, stop_loss_price)
# order = open_contract(symbol, 'sell', capital , max_leverage)
# print(order['info']['status'])

# # 假設部分平倉一半的倉位
# amount_to_close = capital / entry_price / 2
close_contract(symbol)
# 
# # 查詢並打印特定symbol的未實現盈虧
# symbol = 'ADA/USDT'
# contract_pnl, contract_pnl_percentage = calculate_unrealized_pnl(symbol)
# print(contract_pnl)
# print(contract_pnl_percentage)
# # close_contract(symbol)
# # # 重新設置止損單
# # new_stop_loss_price = entry_price * 0.80  # 新的止損價格，例如設置為買入價格的90%
# # reset_stop_loss(symbol, 'buy', capital / entry_price, new_stop_loss_price)

# def fetch_contract_balance():
#     # with app.app_context():
#     balance = binance.fapiPrivateV2GetBalance()
#     usdt_balance = next(item for item in balance if item['asset'] == 'USDT')
#     return usdt_balance['balance']
# print(fetch_contract_balance())
# def calculate_unrealized_pnl(symbol):
#     try:
#         positions = binance.fapiPrivateGetV2PositionRisk()
#         for position in positions:
#             if position['symbol'] == binance.market(symbol)['id'] and float(position['positionAmt']) != 0:
#                 entry_price = float(position['entryPrice'])
#                 current_price = get_latest_future_price(symbol)
#                 amount = float(position['positionAmt'])
#                 position_type = "Long" if amount > 0 else "Short"
#                 # Calculate unrealized PnL
#                 if amount > 0:
#                     pnl = (current_price - entry_price) * amount
#                 else:
#                     pnl = (entry_price - current_price) * abs(amount)
#                 pnl_percentage = (pnl / (entry_price * abs(amount))) * 100
#                 logging.info(f"{get_taiwan_time()} - Symbol: {symbol}, Position: {amount} ({position_type}), Entry Price: {entry_price}, Current Price: {current_price}, PnL: {pnl}, PnL Percentage: {pnl_percentage}%")
#                 return pnl, pnl_percentage, position_type
#         return 0, 0, "No position"
#     except ccxt.NetworkError as e:
#         logging.error(f"Network error: {str(e)}")
#         return 0, 0, "Network error"
#     except ccxt.ExchangeError as e:
#         logging.error(f"Exchange error: {str(e)}")
#         return 0, 0, "Exchange error"
#     except Exception as e:
#         logging.error(f"An unexpected error occurred: {str(e)}")
#         return 0, 0, "Unknown error"

# pnl, pnl_percentage = calculate_unrealized_pnl('MYROUSDT')
# print(f"PnL: {pnl}, PnL Percentage: {pnl_percentage}%, Position Type: ")
        # if position_amt > 0:
        #     contract_holdings[symbol] = f"開多單 ({position_amt})"
        # elif position_amt < 0:
        #     contract_holdings[symbol] = f"開空單 ({abs(position_amt)})"
        # else:
        #     contract_holdings[symbol] = "0"
    #     return contract_holdings
    # except Exception as e:
    #     logging.error(f"Error fetching contract holdings: {str(e)}")
    #     return {}
# print(get_contract_holdings())
```
# colab
本來要訓練一個小型風控dqn機器人不過colab 一直斷線，超難訓練出來好像成果不太行，開最好的機器訓練速度又拉不上去，可能我寫的怪怪的，不過長期訓練應該有料，這邊有幫你寫模型自動備份
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
import sys
import torch
import random
from torch import nn
from torch.utils.data import Dataset, DataLoader
import pytorch_lightning as pl
from collections import deque
from pytorch_lightning import Trainer
import warnings
import os
import shutil

# 禁用特定警告类型
warnings.filterwarnings("ignore", category=UserWarning)

# 定義計算布林帶的函數
def calculate_bollinger_bands(data, window, no_of_std):
    rolling_mean = data.rolling(window=window).mean()
    rolling_std = data.rolling(window=window).std()
    upper_band = rolling_mean + (rolling_std * no_of_std)
    lower_band = rolling_mean - (rolling_std * no_of_std)
    return upper_band, lower_band

# 定義計算歷史波動率的函數
def calculate_historical_volatility(data, window):
    log_returns = np.log(data['close'] / data['close'].shift(1))
    historical_volatility = log_returns.rolling(window=window).std() * np.sqrt(252)  # 年化波動率
    return historical_volatility

# 計算 RSI
def calculate_rsi(data, window):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def create_dataloader(data, batch_size=32):
    dataset = TradingDataset(data)
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)

# 計算 ADX
def calculate_adx(data, window):
    tr = pd.DataFrame()
    tr['tr0'] = data['high'] - data['low']
    tr['tr1'] = abs(data['high'] - data['close'].shift())
    tr['tr2'] = abs(data['low'] - data['close'].shift())
    tr['tr'] = tr.max(axis=1)

    plus_dm = data['high'] - data['high'].shift()
    minus_dm = data['low'].shift() - data['low']
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    plus_dm[data['high'] - data['high'].shift() <= data['low'].shift() - data['low']] = 0
    minus_dm[data['low'].shift() - data['close'] <= data['high'] - data['high'].shift()] = 0

    tr14 = tr['tr'].rolling(window=window).sum()
    plus_di14 = 100 * (plus_dm.rolling(window=window).sum() / tr14)
    minus_di14 = 100 * (minus_dm.rolling(window=window).sum() / tr14)
    dx = 100 * abs((plus_di14 - minus_di14) / (plus_di14 + minus_di14))
    adx = dx.rolling(window=window).mean()
    return adx

# 自定義計算 Aroon 指標
def calculate_aroon(data, window):
    aroon_up = []
    aroon_down = []
    for i in range(window, len(data)):
        high_idx = data['high'].iloc[i-window:i+1].idxmax()
        low_idx = data['low'].iloc[i-window:i+1].idxmin()
        aroon_up.append((window - (i - high_idx)) / window * 100)
        aroon_down.append((window - (i - low_idx)) / window * 100)
    return np.array(aroon_up), np.array(aroon_down)

# 判斷市場連續下跌或上漲
def detect_trend(data, window, threshold=0.5):
    trend_up = data['close'].rolling(window=window).apply(lambda x: (x > x.shift()).mean(), raw=False)
    trend_down = data['close'].rolling(window=window).apply(lambda x: (x < x.shift()).mean(), raw=False)
    return trend_up, trend_down

# 生成信號
def generate_signals(data):
    data['signal'] = 0.0
    buy_condition =  (data['macd'])
    sell_condition = ( data['macd'] )

    data.loc[buy_condition, 'signal'] = 1.0
    data.loc[sell_condition, 'signal'] = -1.0
    data['position'] = data['signal'].diff()
    return data

# 動態調整買入和賣出比例
def adjust_buy_fraction(rsi, macd, signal_line):
    if rsi < 30 and macd > signal_line:
        return 1.0  # 強烈的超賣信號，買入100%
    elif rsi < 30:
        return 0.75  # 超賣信號，買入75%
    elif rsi < 50:
        return 0.5  # 較低的RSI，買入50%
    elif rsi < 70:
        return 0.25  # RSI處於中間位置，買入25%
    else:
        return 0.1  # RSI較高，買入10%

def adjust_sell_fraction(rsi, macd, signal_line):
    if rsi > 70 and macd < signal_line:
        return 1.0  # 強烈的超買信號，賣出100%
    elif rsi > 70:
        return 0.75  # 超買信號，賣出75%
    elif rsi > 50:
        return 0.5  # 較高的RSI，賣出50%
    elif rsi > 30:
        return 0.25  # RSI處於中間位置，賣出25%
    else:
        return 0.1  # RSI較低，賣出10%

class DQNLitModel(pl.LightningModule):
    def __init__(self, state_size, action_size):
        super(DQNLitModel, self).__init__()
        self.state_size = state_size
        self.action_size = action_size
        self.model = nn.Sequential(
            nn.Linear(state_size, 24),
            nn.ReLU(),
            nn.Linear(24, 24),
            nn.ReLU(),
            nn.Linear(24, action_size)
        )
        self.memory = deque(maxlen=20000)
        self.gamma = 0.95    # 折扣率
        self.epsilon = 1.0  # 探索率
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.criterion = nn.MSELoss()
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)

    def forward(self, x):
        return self.model(x)

    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = torch.FloatTensor(state)
        act_values = self(state)
        return torch.argmax(act_values).item()  # 返回動作

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            state = torch.FloatTensor(state).unsqueeze(0)  # 添加批量維度
            next_state = torch.FloatTensor(next_state).unsqueeze(0)  # 添加批量維度
            reward = torch.FloatTensor([reward])
            target = reward
            if not done:
                target = reward + self.gamma * torch.max(self(next_state))
            target_f = self(state).detach()
            target_f[0][action] = target
            self.optimizer.zero_grad()
            loss = self.criterion(self(state)[0][action], target)
            loss.backward()
            self.optimizer.step()
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def training_step(self, batch, batch_idx):
        state, action, reward, next_state, done = batch
        state = state.float()
        next_state = next_state.float()
        action = action.long()
        reward = reward.float()
        done = done.bool()

        # 獲取當前狀態的動作價值
        current_q_values = self(state).gather(1, action.unsqueeze(-1)).squeeze(-1)
        # 計算下一狀態的最大預期Q值
        next_q_values = self(next_state).max(1)[0]
        next_q_values[done] = 0.0
        expected_q_values = reward + self.gamma * next_q_values

        loss = self.criterion(current_q_values, expected_q_values.detach())
        self.log('train_loss', loss)
        return loss

    def configure_optimizers(self):
        return torch.optim.Adam(self.parameters(), lr=self.learning_rate)

def calculate_macd(data, short_window, long_window, signal_window):
    exp1 = data['close'].ewm(span=short_window, adjust=False).mean()
    exp2 = data['close'].ewm(span=long_window, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def preprocess_data(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    for col in data.columns:
        if col != 'timestamp':
            data[col] = pd.to_numeric(data[col], errors='coerce')
    data = data.dropna()  # 移除任何包含NaN的行
    return data

def load_and_preprocess_data(file_path):
    data = pd.read_csv(file_path)
    data = preprocess_data(data)
    return data

class TradingDataset(Dataset):
    def __init__(self, data):
        self.data = data.astype(float).dropna()  # 確保所有數據都是浮點數並且去掉任何NaN值

    def __len__(self):
        return len(self.data) - 1

    def __getitem__(self, idx):
        columns = ['open', 'high', 'low', 'close', 'volume', 'historical_volatility', 'aroon_up', 'aroon_down', 'macd', 'signal_line', 'upper_band', 'lower_band', 'rsi', 'adx', 'trend_up', 'trend_down']
        state = torch.tensor(self.data.iloc[idx][columns].values, dtype=torch.float32)
        next_state = torch.tensor(self.data.iloc[idx + 1][columns].values, dtype=torch.float32)
        reward = torch.tensor([self.data['close'].iloc[idx + 1] - self.data['close'].iloc[idx]], dtype=torch.float32)
        action = torch.tensor(random.choice([0, 1, 2]), dtype=torch.int64)
        done = torch.tensor(idx == len(self.data) - 2, dtype=torch.bool)
        return state, action, reward, next_state, done

def train_dqn(data, model, episodes, batch_size, num_workers=4):
    columns = ['open', 'high', 'low', 'close', 'volume', 'historical_volatility', 'aroon_up', 'aroon_down', 'macd', 'signal_line', 'upper_band', 'lower_band', 'rsi', 'adx', 'trend_up', 'trend_down']
    trainer = Trainer(max_epochs=episodes, devices="auto", accelerator="auto")
    dataloader = create_dataloader(data[columns], batch_size=batch_size)  # 只選擇需要的列
    trainer.fit(model, dataloader)
    return model

def prepare_data_for_training(file_path):
    data = load_and_preprocess_data(file_path)

    # 轉換timestamp為datetime
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # 將數據重新採樣為15分鐘線
    data.set_index('timestamp', inplace=True)
    data_15min = data.resample('15min').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna().reset_index()

    # 轉換所有數值列為float類型
    data_15min[['open', 'high', 'low', 'close', 'volume']] = data_15min[['open', 'high', 'low', 'close', 'volume']].astype(float)

    # 計算歷史波動率
    hv_window = 14
    data_15min['historical_volatility'] = calculate_historical_volatility(data_15min, hv_window)

    # 計算 Aroon 指標
    aroon_window = 14
    aroon_up, aroon_down = calculate_aroon(data_15min, aroon_window)

    # 補全Aroon指標，使其長度與原數據匹配
    data_15min['aroon_up'] = np.nan
    data_15min['aroon_down'] = np.nan
    data_15min.loc[aroon_window:, 'aroon_up'] = aroon_up
    data_15min.loc[aroon_window:, 'aroon_down'] = aroon_down

    short_window = 12
    long_window = 26
    signal_window = 9
    data_15min['macd'], data_15min['signal_line'], data_15min['histogram'] = calculate_macd(data_15min, short_window, long_window, signal_window)

    # 計算布林帶
    bollinger_window = 20
    no_of_std = 2
    data_15min['upper_band'], data_15min['lower_band'] = calculate_bollinger_bands(data_15min['close'], bollinger_window, no_of_std)

    # 計算 RSI
    rsi_window = 14
    data_15min['rsi'] = calculate_rsi(data_15min['close'], rsi_window)

    # 計算 ADX
    adx_window = 14
    data_15min['adx'] = calculate_adx(data_15min, adx_window)

    # 判斷市場連續下跌或上漲
    trend_window = 20
    trend_up, trend_down = detect_trend(data_15min, trend_window)
    data_15min['trend_up'] = trend_up
    data_15min['trend_down'] = trend_down

    return data_15min
# 繼續訓練的函數
def continue_training(model, checkpoint_path):
    # 檢查檢查點文件是否存在
    if os.path.isfile(checkpoint_path):
        # 載入檢查點
        checkpoint = torch.load(checkpoint_path)
        model.load_state_dict(checkpoint['state_dict'])
        print(f"已成功載入檢查點：{checkpoint_path}")
        return model
    else:
        print(f"檢查點文件不存在：{checkpoint_path}")
        return model

def backtest_strategy(file_path, data, model):
    try:
        # 計算信號
        data = generate_signals(data)

        # 初始化資金和持倉
        initial_capital = 50.0
        capital = initial_capital
        num_ada = 0  # 持有的ADA數量

        # 回測邏輯
        trades = []  # 保存交易記錄
        buy_signals = []
        sell_signals = []

        for i in range(1, len(data)):
            state = data.iloc[i].drop('timestamp').values.reshape(1, -1)
            action = model.act(state)
            if action == 1:  # 買入信號
                buy_price = data['close'].iloc[i]
                buy_fraction = adjust_buy_fraction(data['rsi'].iloc[i], data['macd'].iloc[i], data['signal_line'].iloc[i])
                num_ada_to_buy = capital * buy_fraction / buy_price
                total_cost = buy_price * num_ada_to_buy
                if capital >= total_cost and num_ada_to_buy > 0:
                    capital -= total_cost
                    num_ada += num_ada_to_buy
                    trades.append({'timestamp': data['timestamp'].iloc[i], 'type': 'buy', 'price': buy_price, 'num_ada': num_ada_to_buy})
                    buy_signals.append((data['timestamp'].iloc[i], buy_price))
                    # print(f"買入: {data['timestamp'].iloc[i]} 價格: {buy_price} 數量: {num_ada_to_buy}")
            elif action == 2:  # 賣出信號
                sell_price = data['close'].iloc[i]
                sell_fraction = adjust_sell_fraction(data['rsi'].iloc[i], data['macd'].iloc[i], data['signal_line'].iloc[i])
                num_ada_to_sell = num_ada * sell_fraction
                total_profit = sell_price * num_ada_to_sell
                if num_ada_to_sell > 0:
                    capital += total_profit
                    num_ada -= num_ada_to_sell
                    trades.append({'timestamp': data['timestamp'].iloc[i], 'type': 'sell', 'price': sell_price, 'profit': total_profit, 'num_ada': num_ada_to_sell})
                    sell_signals.append((data['timestamp'].iloc[i], sell_price))
                    # print(f"賣出: {data['timestamp'].iloc[i]} 價格: {sell_price} 數量: {num_ada_to_sell} 利潤: {total_profit}")

        # 計算最終資金
        final_capital = capital + (data['close'].iloc[-1] * num_ada)
        roi = (final_capital - initial_capital) / initial_capital
        print(f"初始資金: {initial_capital} 最終資金: {final_capital} 淨利潤: {final_capital - initial_capital} 投資回報率: {roi}")

        return {
            'file': os.path.basename(file_path),
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'net_profit': final_capital - initial_capital,
            'roi': roi
        }
    except Exception as e:
        print(f"處理文件時發生錯誤: {e}")
        return None

def main():
    torch.set_float32_matmul_precision('high')

    checkpoint_path = '/content/lightning_logs/checkpoints/epoch=9-step=10950.ckpt'  # 假設檢查點保存的路徑

    # 繼續訓練
    global_model = continue_training(global_model, checkpoint_path)
    if len(sys.argv) > 1:
        # 如果提供了CSV文件路徑，則僅回測該文件
        file_path = sys.argv[1]
        data = prepare_data_for_training(file_path)
        global_model = train_dqn(data, global_model, episodes=10, batch_size=32)
        result = backtest_strategy(data, global_model)
        if result:
            print(result)
    else:
        # 否則，回測當前目錄下的所有CSV文件
        csv_files = glob.glob("./data3/*.csv")
        csv_files2 = glob.glob("./data2/*.csv")

        results = []
        data= []
        data_count = 0

        f1 = 'dqn_model.pth'    # 欲複製的檔案
        f2 = './lightning_logs/dqn_model.pth'  # 存檔的位置與檔案名稱
        if os.path.isfile(f1):
          shutil.copyfile(f1,f2)   # 複製檔案
        f1 = 'test.py'    # 欲複製的檔案
        f2 = './lightning_logs/test.py'  # 存檔的位置與檔案名稱
        if os.path.isfile(f2):
          shutil.copyfile(f1,f2)   # 複製檔案

        destination_path = '/content/drive/MyDrive/modelbackup'
        source_path = '/content/lightning_logs'
        if os.path.exists(source_path):
          shutil.copytree(source_path,destination_path, dirs_exist_ok=True)
        checkpoint_path = './lightning_logs/checkpoints/last.ckpt'

        for file_path in csv_files:
          data.append(prepare_data_for_training(file_path))
          global_model = train_dqn(data[data_count], global_model, episodes=10, batch_size=32)
          shutil.copyfile(f1,f2)   # 複製檔案
          shutil.copytree(source_path,destination_path, dirs_exist_ok=True)
          torch.save(global_model, 'dqn_model.pth')

        for file_path in csv_files2:
          data.append(prepare_data_for_training(file_path))
          global_model = train_dqn(data[data_count], global_model, episodes=10, batch_size=32)
          shutil.copytree(source_path,destination_path, dirs_exist_ok=True)
          shutil.copyfile(f1,f2)   # 複製檔案
          torch.save(global_model, 'dqn_model.pth')
        data_count = 0
        for file_path in csv_files:
          result = backtest_strategy(file_path,data[data_count], global_model)
          if result:
            results.append(result)
          data_count+=1

        # 計算總和
        total_initial_capital = sum([r['initial_capital'] for r in results])
        total_final_capital = sum([r['final_capital'] for r in results])
        total_net_profit = sum([r['net_profit'] for r in results])
        total_roi = (total_final_capital - total_initial_capital) / total_initial_capital

        # 添加總和到結果中
        results.append({
            'file': 'Total',
            'initial_capital': total_initial_capital,
            'final_capital': total_final_capital,
            'net_profit': total_net_profit,
            'roi': total_roi
        })

        # 轉換為DataFrame並保存到CSV文件
        results_df = pd.DataFrame(results)
        results_df.to_csv('backtest_results.csv', index=False)

        print("所有回測完成，結果已保存到backtest_results.csv。")

if __name__ == "__main__":
    main()

```

