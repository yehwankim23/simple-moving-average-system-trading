import json

import requests

X_API_KEY = ""

VOO_URL = "https://yfapi.net/v8/finance/spark"
VOO_PARAMS = {"interval": "1d", "range": "3mo", "symbols": "VOO"}
VOO_HEADERS = {"x-api-key": X_API_KEY}


def main() -> None:
    spark = json.loads(requests.get(VOO_URL, VOO_PARAMS, headers=VOO_HEADERS).text)
    prices = spark["VOO"]["close"]
    length = len(prices)

    for long in range(2, 15):
        for short in range(1, long):
            usd = 5.0
            voo = 0.0
            buys = 0
            buy_price = 0
            trades = ""

            for index in range(15, length):
                current_price = prices[index]
                current_short_average = sum(prices[index - short + 1:index + 1]) / short
                current_long_average = sum(prices[index - long + 1:index + 1]) / long
                previous_long_average = sum(prices[index - long:index]) / long

                if current_short_average < current_long_average:
                    if voo > 0:
                        usd = voo * current_price
                        voo = 0.0
                        trades += "{:.2f}".format(current_price - buy_price) + " "
                elif previous_long_average < current_long_average < current_short_average:
                    if usd > 0:
                        voo = usd / current_price
                        usd = 0.0
                        buys += 1
                        buy_price = current_price

            if voo > 0:
                current_price = prices[length - 1]
                usd = voo * current_price
                trades += "{:.2f}".format(current_price - buy_price)

            print("{:.4f}".format(usd) + "\t\t"
                  + "{:0>2d}".format(short) + "-" + "{:0>2d}".format(long) + "\t\t"
                  + str(buys) + ("*" if voo > 0 else "") + "\t\t"
                  + trades)


if __name__ == "__main__":
    main()
