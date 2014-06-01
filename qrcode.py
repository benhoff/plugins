# Plugin by https://github.com/Mu5tank05
from cloudbot import hook, web, http


@hook.command('qr')
@hook.command
def qrcode(text):
    """qrcode [link] returns a link for a QR code."""

    args = {
        "cht": "qr",  # chart type (QR)
        "chs": "200x200",  # dimensions
        "chl": text  # data
    }

    link = http.prepare_url("http://chart.googleapis.com/chart", args)

    return web.try_shorten(link)
