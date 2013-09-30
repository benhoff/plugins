from util import hook
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

import os
import base64
import json
import hashlib

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s : s[0:-ord(s[-1])]

db_ready = False

def db_init(db):
    """check to see that our db has the the encryption table and return a connection."""
    db.execute("create table if not exists encryption(encrypted, iv, "
               "primary key(encrypted))")
    db.commit()
    db_ready = True


def get_salt(bot):
	if not bot.config.get("random_salt", False):
		bot.config["random_salt"] = hashlib.md5(os.urandom(16)).hexdigest()
		json.dump(bot.config, open('config', 'w'), sort_keys=True, indent=2)
	return bot.config["random_salt"]


@hook.command
def encrypt(inp, bot=None, db=None):
    """encrypt <pass> <string> -- Encrypts <string> with <pass>."""
    db_init(db)

    password = inp.split(" ")[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt)

    iv = Random.new().read(AES.block_size);
    iv_encoded = base64.b64encode(iv)

    text = " ".join(inp.split(" ")[1:])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(text))
    encoded = base64.b64encode(encrypted)

    db.execute("insert or replace into encryption(encrypted, iv)"
               "values(?,?)", (encoded, iv_encoded))
    db.commit()

    return encoded


@hook.command
def decrypt(inp, bot=None, db=None):
    """decrypt <pass> <string> -- Decrypts <string> with <pass>."""
    db_init(db)

    password = inp.split(" ")[0]
    salt = get_salt(bot)
    key = PBKDF2(password, salt)

    text = " ".join(inp.split(" ")[1:])

    iv_encoded = db.execute("select iv from encryption where"
                           " encrypted=?", (text,)).fetchone()[0]
    iv = base64.b64decode(iv_encoded)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(base64.b64decode(text)))