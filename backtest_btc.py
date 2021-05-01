import json

import requests

BTC_URL = "https://api.upbit.com/v1/candles/minutes/60?market=KRW-BTC&count=200"
BTC_HEADERS = {"Accept": "application/json"}


def main() -> None:
    candles = json.loads(requests.get(BTC_URL, headers=BTC_HEADERS).text)
    prices = list(reversed(list(int(candle["trade_price"]) for candle in candles)))
    length = len(prices)

    for long in range(2, 25):
        for short in range(1, long):
            krw = 5.0
            btc = 0.0
            buys = 0
            buy_price = 0
            trades = ""

            for index in range(25, length):
                current_price = prices[index]
                current_short_average = sum(prices[index - short + 1:index + 1]) / short
                current_long_average = sum(prices[index - long + 1:index + 1]) / long
                previous_long_average = sum(prices[index - long:index]) / long

                if current_short_average < current_long_average:
                    if btc > 0:
                        krw = btc * current_price
                        btc = 0.0
                        trades += str(int(current_price - buy_price)) + " "
                elif previous_long_average < current_long_average < current_short_average:
                    if krw > 0:
                        btc = krw / current_price
                        krw = 0.0
                        buys += 1
                        buy_price = current_price

            if btc > 0:
                current_price = prices[length - 1]
                krw = btc * current_price
                trades += str(int(current_price - buy_price))

            print("{:.4f}".format(krw) + "\t\t"
                  + "{:0>2d}".format(short) + "-" + "{:0>2d}".format(long) + "\t\t"
                  + str(buys) + ("*" if btc > 0 else "") + "\t\t"
                  + trades)


if __name__ == "__main__":
    main()
