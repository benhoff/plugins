# Written by Scaevolus 2010
from util import hook, http
from util.text import multiword_replace
from util.execute import eval_py
import string
import sqlite3
import re

re_lineends = re.compile(r'[\r\n]*')

# some simple "shortcodes" for formatting purposes
shortcodes = {
'[b]': '\x02',
'[/b]': '\x02',
'[u]': '\x1F',
'[/u]': '\x1F',
'[i]': '\x16',
'[/i]': '\x16'}


def db_init(db):
    db.execute("create table if not exists mem(word, data, nick,"
               " primary key(word))")
    db.commit()


def get_memory(db, word):

    row = db.execute("select data from mem where word=lower(?)",
                     [word]).fetchone()
    if row:
        return row[0]
    else:
        return None


@hook.command("r", adminonly=True)
@hook.command(adminonly=True)
def remember(inp, nick='', db=None, say=None, input=None, notice=None):
    "remember <word> [+]<data> -- Remembers <data> with <word>. Add +"
    " to <data> to append."
    db_init(db)

    append = False

    try:
        head, tail = inp.split(None, 1)
    except ValueError:
        return remember.__doc__

    data = get_memory(db, head)

    if tail[0] == '+':
        append = True
        # ignore + symbol
        new = tail[1:]
        _head, _tail = data.split(None, 1)
        # data is stored with the input so ignore it when re-adding it
        if len(tail) > 1 and tail[1] in (string.punctuation + ' '):
            tail = _tail + new
        else:
            tail = _tail + ' ' + new

    db.execute("replace into mem(word, data, nick) values"
               " (lower(?),?,?)", (head, tail, nick))
    db.commit()

    if data:
        if append:
            notice("Appending \x02%s\x02 to \x02%s\x02" % (new, data))
        else:
            notice('Remembering \x02%s\x02 for \x02%s\x02. Type ?%s to see it.'
                % (tail, head, head))
            notice('Previous data was \x02%s\x02' % data)
    else:
        notice('Remembering \x02%s\x02 for \x02%s\x02. Type ?%s to see it.'
                % (tail, head, head))


@hook.command("f", adminonly=True)
@hook.command(adminonly=True)
def forget(inp, db=None, input=None, notice=None):
    "forget <word> -- Forgets a remembered <word>."

    db_init(db)
    data = get_memory(db, inp)

    if data:
        db.execute("delete from mem where word=lower(?)",
                   [inp])
        db.commit()
        notice('"%s" has been forgotten.' % data.replace('`', "'"))
        return
    else:
        notice("I don't know about that.")
        return


@hook.command
def info(inp, notice=None, db=None):
    "info <factoid> -- Shows the source of a factoid."

    db_init(db)

    # attempt to get the factoid from the database
    data = get_memory(db, inp.strip())

    if data:
        notice(data)
    else:
        notice("Unknown Factoid.")


@hook.regex(r'^\? ?(.+)')
def factoid(inp, say=None, db=None, bot=None, me=None, conn=None, input=None):
    "?<word> -- Shows what data is associated with <word>."
    try:
        prefix_on = bot.config["plugins"]["factoids"].get("prefix", False)
    except KeyError:
        prefix_on = False

    db_init(db)

    # split up the input
    split = inp.group(1).strip().split(" ")
    factoid_id = split[0]

    if len(split) >= 1:
        arguments = " ".join(split[1:])
    else:
        arguments = ""

    data = get_memory(db, factoid_id)

    if data:
        # if the factoid starts with <py>, its a dynamic one
        if data.startswith("<py>"):
            data = data[4:].strip()
            variables = 'input="""%s"""; nick="%s"; chan="%s"; bot_nick="%s";' % (arguments,
                         input.nick, input.chan, input.conn.nick)
            result = eval_py(variables + data)

        else:
            result = data

        result = multiword_replace(result, shortcodes)

        if result.startswith("<act>"):
            result = result[5:].strip()
            me(result)
        else:
            if prefix_on:
                say("\x02[%s]:\x02 %s" % (factoid_id, result))
            else:
                say(result)
