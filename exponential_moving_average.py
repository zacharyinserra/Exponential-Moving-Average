import datetime as dt
import json
import time

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
from dateutil.relativedelta import relativedelta

'''
Exponential Moving Average

EMA(t) = (V(t) * (s / (1 + d))) + EMA(y) * (1 - (s / (1 + d)))

EMA(t) = EMA today
V(t) = Value today
EMA(y) = EMA yesterday
s = Smoothing
d = Number of days

First EMA is SMA
'''


class AlpacaServiceError(Exception):
    def __init__(self, message):
        super().__init__(message)


def calculate_sma_first_day(days, sym_data, start_ind):
    sum = 0
    for i in range(days):
        d = sym_data[start_ind + 1 - i]
        sum += d['c']
    avg = sum / days
    return avg


def calculate_ema(start_sma, days, sym_data, start_ind):
    dic = {}
    smoothing_constant = 2
    weight = smoothing_constant / (days + 1)
    prev_ema = start_sma

    # start at length of weekdays_list
    # get ema for each day in list
    for i in range(start_ind + 1, len(sym_data)):
        d = sym_data[i]
        val_today = d['c']
        ema = (val_today - prev_ema) * weight + prev_ema
        dic[d['t']] = ema
        prev_ema = ema

    return dic


symbol = 'INTC'


# Get todays date and the date a year ago today
today = dt.date.today()
year_ago = (today - relativedelta(years=1))

# Get all data need to calculate 200 day and 50 day moving averages for last year of market data
url = "https://data.alpaca.markets/v1/bars/day?symbols=" + symbol + \
    "&limit=" + str(500) + "&until=" + \
    str(today) + "T23:59:59Z"
payload = {}
headers = {
    'APCA-API-KEY-ID': '',
    'APCA-API-SECRET-KEY': ''
}

response = requests.request("GET", url, headers=headers, data=payload)

if response.status_code != 200:
    raise AlpacaServiceError(response.reason)

data = json.loads(response.text)

symbol_data = data[symbol]

epochs = []
for i in range(len(symbol_data)):
    epochs.append(symbol_data[i]['t'])


# Find year ago epoch to start calculations with
year_ago = dt.datetime.combine(year_ago, dt.datetime.min.time())
index = epochs.index(year_ago.timestamp())

# Get starting SMA to begin EMA calculations
starting_sma200 = calculate_sma_first_day(200, symbol_data, index)

ema200_dic = calculate_ema(starting_sma200, 200, symbol_data, index + 1)

starting_sma50 = calculate_sma_first_day(50, symbol_data, index)

ema50_dic = calculate_ema(starting_sma50, 50, symbol_data, index + 1)

symbol_close = []
for i in range(len(ema200_dic)):
    symbol_close.append(symbol_data[index + i]['c'])


# Get ready to plot
# Convert epochs to dates for plot
epochs = list(ema200_dic.keys())
dates = []
for e in epochs:
    dates.append(time.strftime('%Y-%m-%d', time.localtime(e)))


ema200 = list(ema200_dic.values())
ema50 = list(ema50_dic.values())

fig = plt.figure(figsize=(12, 10))

# Start plotting
plt.title('Exponential Moving Average - ' + symbol)
plt.xlabel("Time (Days)")
plt.ylabel("Price $")

plt.plot(dates, ema200, "-b", label="200 Day")
plt.plot(dates, ema50, "-r", label="50 Day")
plt.plot(dates, symbol_close, "-g", label="Closing Prices")

plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=25))
plt.gca().set_xlim(dates[0], dates[-1])
plt.gcf().autofmt_xdate()

plt.legend(loc="upper left")
plt.grid()

done = True
plt.show()
