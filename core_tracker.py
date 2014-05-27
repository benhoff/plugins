# plugin to keep track of bot state

import re

from cloudbot import hook

nick_re = re.compile(":(.+?)!")


@hook.event("KICK")
def on_kick(irc_paramlist, conn, chan):
    """
    :type irc_paramlist: list[str]
    :type conn: cloudbot.core.connection.BotConnection
    :type chan: str
    """
    # if the bot has been kicked, remove from the channel list
    if irc_paramlist[1] == conn.nick:
        conn.channels.remove(chan)
        auto_rejoin = conn.config.get('auto_rejoin', False)
        if auto_rejoin:
            conn.join(irc_paramlist[0])


@hook.event("NICK")
def on_nick(irc_paramlist, bot, conn, raw):
    """
    :type irc_paramlist: list[str]
    :type bot: cloudbot.core.bot.CloudBot
    :type conn: cloudbot.core.connection.BotConnection
    :type raw: str
    """
    old_nick = nick_re.search(raw).group(1)
    new_nick = str(irc_paramlist[0])
    if old_nick == conn.nick:
        conn.nick = new_nick
        bot.logger.info("Bot nick changed from '{}' to '{}'.".format(old_nick, new_nick))
