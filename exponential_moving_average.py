import datetime as dt
import json

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


def daterange(date1, date2):
    for n in range(int((date2 - date1).days)+1):
        yield date1 + dt.timedelta(n)


def calculate_sma_first_day(days, sym_data):
    sum = 0
    for i in range(days):
        sum += sym_data[i]['c']
    avg = sum / days
    return avg


def calculate_ema(start_sma, days, weekdays_list, sym_data):
    dic = {}
    smoothing_constant = 2
    weight = smoothing_constant / (days + 1)
    prev_ema = start_sma

    # WTF DO ID 
    for i in range(days):
        for j in range(days):
            val_today = sym_data[days + i + j]['c']
            ema = (val_today - prev_ema) * weight + prev_ema
            dic[weekdays_list[i]] = ema
            prev_ema = ema

    return dic


symbol = 'INTC'

# List of holidays to get rid of between today and a year ago
# https://www.marketbeat.com/stock-market-holidays/
holidays_list = [dt.date(2020, 1, 1), dt.date(2020, 1, 20), dt.date(2020, 2, 17), dt.date(2020, 4, 10), dt.date(2020, 5, 25), dt.date(2020, 7, 3), dt.date(2020, 9, 7), dt.date(2020, 11, 26), dt.date(
    2020, 12, 25), dt.date(2021, 1, 1), dt.date(2021, 1, 18), dt.date(2021, 2, 15), dt.date(2021, 4, 2), dt.date(2021, 5, 31), dt.date(2021, 7, 5), dt.date(2021, 9, 6), dt.date(2021, 11, 25), dt.date(2021, 12, 24)]

today = dt.date.today()
year_ago = (today - relativedelta(years=1))
weekdays = []

# Get list of weekday dates
for date in daterange(year_ago, today):
    weekno = date.weekday()
    if weekno < 5:
        weekdays.append(date)

# Remove holidays
for date in holidays_list:
    if date in weekdays:
        weekdays.remove(date)

# Get all data need to calculate 200 day and 50 day moving averages for last year of market data

url = "https://data.alpaca.markets/v1/bars/day?symbols=" + symbol + \
    "&limit=" + str(200 + len(weekdays)) + "&until=" + \
    str(today) + "T23:59:59Z"
payload = {}
headers = {
    'APCA-API-KEY-ID': 'PKQLL80ZK3WGK3GF5S6D',
    'APCA-API-SECRET-KEY': 'EiKYfBhDHhnAtHdRPm3PDZ59sP6Kpvwrdqbx1qX1'
}

response = requests.request("GET", url, headers=headers, data=payload)

if response.status_code != 200:
    raise AlpacaServiceError(response.reason)

data = json.loads(response.text)

symbol_data = data[symbol]
# symbol_data.reverse()

epochs = []
for i in range(len(symbol_data)):
    epochs.append(symbol_data[i]['t'])
    weekdays.append(dt.datetime.fromtimestamp(symbol_data[i]['t']))
weekdays.reverse()
epochs.reverse()

# Get starting SMA to begin EMA calculations
starting_sma200 = calculate_sma_first_day(200, symbol_data)

ema200_dic = calculate_ema(starting_sma200, 200, weekdays, symbol_data)

starting_sma50 = calculate_sma_first_day(50, symbol_data)

ema50_dic = calculate_ema(starting_sma200, 50, weekdays, symbol_data)

symbol_close = []
for i in range(len(weekdays)):
    symbol_close.append(symbol_data[i]['c'])


# Get ready to plot
dates = list(ema200_dic.keys())
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

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=25))
plt.gca().set_xlim(dates[0], dates[-1])
plt.gcf().autofmt_xdate()

plt.legend(loc="upper left")
plt.grid()

done = True
plt.show()
