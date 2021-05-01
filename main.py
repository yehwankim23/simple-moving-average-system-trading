import datetime
import json
import sys
import time
import traceback

import pyupbit
import requests
import telegram
import telegram.ext

CHAT_ID = int("")
TOKEN = ""
ACCESS = ""
SECRET = ""
X_API_KEY = ""

BOT = telegram.Bot(TOKEN)

pong = True
holding = False

BTC_URL = "https://api.upbit.com/v1/candles/minutes/60?market=KRW-BTC&count=200"
BTC_HEADERS = {"Accept": "application/json"}

UPBIT = pyupbit.Upbit(ACCESS, SECRET)

VOO_URL = "https://yfapi.net/v8/finance/spark"
VOO_PARAMS = {"interval": "1d", "range": "3mo", "symbols": "VOO"}
VOO_HEADERS = {"x-api-key": X_API_KEY}

BTC_SHORT = 5
BTC_LONG = 15

VOO_SHORT = 7
VOO_LONG = 21


def send_message(text: str) -> None:
    BOT.send_message(CHAT_ID, text)


def send_error_message() -> None:
    global pong

    stack_traces = traceback.format_exc().splitlines()
    message = stack_traces[1].strip() + "()\n\n" + stack_traces[2].strip() + "\n\n"

    if len(stack_traces) > 4:
        message += stack_traces[3].strip() + "()\n\n" + stack_traces[4].strip() + "\n\n"

    send_message(message + stack_traces[-1])
    pong = True


def ping(update: telegram.Update, _: telegram.ext.CallbackContext) -> None:
    global pong

    # noinspection PyBroadException
    try:
        if update.effective_chat.id == CHAT_ID:
            pong = True
    except Exception:
        send_error_message()


def buy(update: telegram.Update, _: telegram.ext.CallbackContext) -> None:
    global holding

    # noinspection PyBroadException
    try:
        if update.effective_chat.id == CHAT_ID:
            holding = True
            send_message("holding : " + str(holding))
    except Exception:
        send_error_message()


def sell(update: telegram.Update, _: telegram.ext.CallbackContext) -> None:
    global holding

    # noinspection PyBroadException
    try:
        if update.effective_chat.id == CHAT_ID:
            holding = False
            send_message("holding : " + str(holding))
    except Exception:
        send_error_message()


def main() -> None:
    global holding, pong

    # noinspection PyBroadException
    try:
        check_btc = True
        check_voo = True
        check_running = True

        updater = telegram.ext.Updater(TOKEN)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(telegram.ext.CommandHandler("ping", ping))
        dispatcher.add_handler(telegram.ext.CommandHandler("buy", buy))
        dispatcher.add_handler(telegram.ext.CommandHandler("sell", sell))

        updater.start_polling()
        send_message("Program started")
    except Exception:
        send_error_message()
        send_message("Program stopped")
        sys.exit(-1)

    while True:
        # noinspection PyBroadException
        try:
            today = datetime.datetime.now()

            if today.minute < 30:
                if check_btc:
                    check_btc = False

                    candles = json.loads(requests.get(BTC_URL, headers=BTC_HEADERS).text)
                    prices = list(reversed(list(int(candle["trade_price"]) for candle in candles)))
                    length = len(prices)

                    if length < BTC_LONG + 1:
                        raise ValueError("len(prices) = " + str(length))

                    prices = prices[-BTC_LONG - 1:]

                    current_price = prices[BTC_LONG]
                    current_short_average \
                        = sum(prices[BTC_LONG - BTC_SHORT + 1:BTC_LONG + 1]) / BTC_SHORT
                    current_long_average = sum(prices[1:BTC_LONG + 1]) / BTC_LONG
                    previous_long_average = sum(prices[0:BTC_LONG]) / BTC_LONG

                    if current_short_average < current_long_average:
                        btc = UPBIT.get_balance("BTC")

                        if btc > 0:
                            UPBIT.sell_market_order("KRW-BTC", btc)
                            send_message("Sell: " + "{:,}".format(int(current_price)))
                    elif previous_long_average < current_long_average < current_short_average:
                        krw = UPBIT.get_balance("KRW")

                        if krw > 10000:
                            UPBIT.buy_market_order("KRW-BTC", krw * 0.9995)
                            send_message("Buy: " + "{:,}".format(int(current_price)))
            else:
                check_btc = True

            if today.hour == 0:
                if check_voo:
                    check_voo = False

                    spark = json.loads(requests.get(VOO_URL, VOO_PARAMS, headers=VOO_HEADERS).text)
                    prices = spark["VOO"]["close"]
                    length = len(prices)

                    if length < VOO_LONG + 1:
                        raise ValueError("len(prices) = " + str(length))

                    prices = prices[-VOO_LONG - 1:]

                    current_price = prices[VOO_LONG]
                    current_short_average \
                        = sum(prices[VOO_LONG - VOO_SHORT + 1:VOO_LONG + 1]) / VOO_SHORT
                    current_long_average = sum(prices[1:VOO_LONG + 1]) / VOO_LONG
                    previous_long_average = sum(prices[0:VOO_LONG]) / VOO_LONG

                    if current_short_average < current_long_average:
                        if holding:
                            send_message("/sell : " + "{:.2f}".format(float(current_price)))
                    elif previous_long_average < current_long_average < current_short_average:
                        if not holding:
                            send_message("/buy : " + "{:.2f}".format(float(current_price)))
            else:
                check_voo = True

            if today.hour in [9, 15, 21]:
                if check_running:
                    check_running = False
                    send_message("Program running")
            else:
                check_running = True

            if pong:
                pong = False
                send_message("Pong")
        except Exception:
            send_error_message()
        finally:
            time.sleep(3)


if __name__ == "__main__":
    main()
