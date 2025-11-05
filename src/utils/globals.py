import os
import string
from dotenv import load_dotenv

load_dotenv(os.path.abspath("src/config/.env"))

SPOTIFY = {
    "CLIENT_ID": os.getenv("CLIENT_ID"),
    "CLIENT_SECRET": os.getenv("CLIENT_SECRET"),
    "REDIRECT_URI": os.getenv("REDIRECT_URI"),
    "SCOPE": "playlist-modify-public playlist-modify-private",
    "USER_ID": os.getenv("SPOTIFY_USER_ID"),
}

AMAZONE_EMAIL = os.getenv("EMAIL")
AMAZONE_PASSWORD = os.getenv("PASSWORD")

YOUTUBE_USER_ID = os.getenv("YOUTUBE_USER_ID")

SPECIAL_CHAR_DICT = {
    "!": "Exclamation mark",
    '"': "Double quotation mark",
    "#": "Hash",
    "$": "Dollar sign",
    "%": "Percent sign",
    "&": "Ampersand",
    "'": "Apostrophe",
    "(": "Left parenthesis",
    ")": "Right parenthesis",
    "*": "Asterisk",
    "+": "Plus sign",
    ",": "Comma",
    "-": "Minus sign",
    ".": "Period",
    "/": "Slash",
    ":": "Colon",
    ";": "Semicolon",
    "<": "Less than",
    "=": "Equals sign",
    ">": "Greater than",
    "?": "Question mark",
    "@": "At symbol",
    "[": "Left square bracket",
    "\\": "Backslash",
    "]": "Right square bracket",
    "^": "Caret",
    "_": "Underscore",
    "`": "Grave accent",
    "{": "Left curly brace",
    "|": "Vertical bar",
    "}": "Right curly brace",
    "~": "Tilde",
    " ": "Space",
}

special_char_list = [v for _, v in SPECIAL_CHAR_DICT.items()]
CHAR_STR = string.ascii_lowercase + string.digits
CHAR_STR_SPEC = string.punctuation

CHAR_LIST_TRANS = list(CHAR_STR) + special_char_list

PLATFORMS = ["spotify", "amazon", "youtube"]
