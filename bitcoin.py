from util import http, hook


@hook.command("btc", autohelp=False)
@hook.command(autohelp=False)
def bitcoin(inp):
    "bitcoin <exchange> -- Gets current exchange rate for bitcoins from several exchanges, default is MtGox. Supports MtGox, Bitpay, and BitStamp."
    exchanges = {
        "mtgox": {
            "api_url": "https://mtgox.com/api/1/BTCUSD/ticker",
            "func": lambda data: u"\x02MtGox\x02 // Current: {}, High: {}, Low: {}, Best Ask: {}, Volume: {}".format(data['return']['last']['display'], \
                                   data['return']['high']['display'], data['return']['low']['display'], data['return']['buy']['display'], \
                                   data['return']['vol']['display'])
        },
        "bitpay": {
            "api_url": "https://bitpay.com/api/rates",
            "func": lambda data: u"\x02Bitpay\x02 // Current: ${}".format(data[0]['rate'])
        },
        "bitstamp": {
            "api_url": "https://www.bitstamp.net/api/ticker/",
            "func": lambda data: u"\x02BitStamp\x02 // Current: ${}, High: ${}, Low: ${}, Volume: {:.2f} BTC".format(data['last'], data['high'], data['low'], \
                                   float(data['volume']))
        }
    }

    inp = inp.lower()

    if inp:
        if inp in exchanges:
            exchange = exchanges[inp]
        else:
            return "Invalid Exchange"
    else:
        exchange = exchanges["mtgox"]

    data = http.get_json(exchange["api_url"])
    func = exchange["func"]
    return func(data)


@hook.command(autohelp=False)
def litecoin(inp, message=None):
    """litecoin -- gets current exchange rate for litecoins from BTC-E"""
    data = http.get_json("https://btc-e.com/api/2/ltc_usd/ticker")
    ticker = data['ticker']
    message("Current: \x0307${:.2f}\x0f - High: \x0307${:.2f}\x0f"
        " - Low: \x0307${:.2f}\x0f - Volume: {:.2f}LTC".format(ticker['buy'], ticker['high'], ticker['low'], ticker['vol_cur']))
