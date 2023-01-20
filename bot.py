import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.00615316
 

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

#la variable ORDER_TYPE_MARKET c'est constante qu'on pris de la bib enums qu'on a importé de binance
def order(side, quantity, symbol, order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order for buy")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        return False
    return True

def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws,message):
    global closes
    #print('received connection')
    json_message = json.loads(message)
    #pprint.pprint(json_message)

    candle = json_message ['k']
    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = talib.RSI(np_closes, RSI_PERIOD)
            print("all rsis calculated so far")
            print(rsi)
            last_rsi = rsi[-1]
            print("the current rsi is {}".format(last_rsi))


            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print ("Overbough!, SELL SELL SELL")
                    #appele la fonction order pour vendre sur binance
                    #SIDE_SELL c'est une variable constante de enums 
                    order_succeeded = order (SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("IT is overbought, but we don't own any. Nothing to do")
            
            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do")
                else:
                    print("Oversold !, BUY BUY BUY")
                    #appele la fonction order pour acheter sur binance
                    order_succeeded = order (SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True
            


ws = websocket.WebSocketApp(SOCKET, on_open=on_open , on_close=on_close, on_message=on_message)
ws.run_forever()

