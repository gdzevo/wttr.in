"""
global configuration of the project

External environment variables:

    WTTR_MYDIR
    WTTR_GEOLITE
    WTTR_WEGO
    WTTR_LISTEN_HOST
    WTTR_LISTEN_PORT
    WTTR_USER_AGENT

"""
from __future__ import print_function

import logging
import os
import re

MYDIR = os.path.abspath(os.path.dirname(os.path.dirname("__file__")))
DATA_DIR = os.path.join(MYDIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
LOG_DIR = os.path.join(MYDIR, "log")
GEOLITE = os.environ.get("WTTR_GEOLITE", os.path.join(DATA_DIR, "GeoLite2-City.mmdb"))
WEGO = os.environ.get("WTTR_WEGO", os.path.join(MYDIR, "bin/we-lang"))
PYPHOON = "pyphoon-lolcat"

IP2LCACHE = os.path.join(CACHE_DIR, "ip2l")
PNG_CACHE = os.path.join(CACHE_DIR, "png")
LRU_CACHE = os.path.join(CACHE_DIR, "lru")

LOG_FILE = os.path.join(LOG_DIR, "main.log")

PROXY_LOG_ACCESS = os.path.join(LOG_DIR, "proxy-access.log")
PROXY_LOG_ERRORS = os.path.join(LOG_DIR, "proxy-errors.log")

MISSING_TRANSLATION_LOG = os.path.join(LOG_DIR, "missing-translation")

ALIASES = os.path.join(MYDIR, "share/aliases")
ANSI2HTML = os.path.join(MYDIR, "share/ansi2html.sh")
BLACKLIST = os.path.join(MYDIR, "share/blacklist")

HELP_FILE = os.path.join(MYDIR, "share/help.txt")
BASH_FUNCTION_FILE = os.path.join(MYDIR, "share/bash-function.txt")
TRANSLATION_FILE = os.path.join(MYDIR, "share/translation.txt")

IATA_CODES_FILE = os.path.join(MYDIR, "share/list-of-iata-codes.txt")

TEMPLATES = os.path.join(MYDIR, "share/templates")
STATIC = os.path.join(MYDIR, "share/static")

NOT_FOUND_LOCATION = "not found"
DEFAULT_LOCATION = "oymyakon"

MALFORMED_RESPONSE_HTML_PAGE = open(
    os.path.join(STATIC, "malformed-response.html")
).read()

GEOLOCATOR_SERVICE = "http://localhost:8004"

# number of queries from the same IP address is limited
# (minute, hour, day) limitations:
QUERY_LIMITS = (300, 3600, 24 * 3600)

LISTEN_HOST = os.environ.get("WTTR_LISTEN_HOST", "")
try:
    LISTEN_PORT = int(os.environ.get("WTTR_LISTEN_PORT"))
except (TypeError, ValueError):
    LISTEN_PORT = 8002

PROXY_HOST = "127.0.0.1"
PROXY_PORT = 5001
PROXY_CACHEDIR = os.path.join(CACHE_DIR, "proxy-wwo")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PROXY_CACHEDIR, exist_ok=True)

MY_EXTERNAL_IP = "127.0.0.1"

PLAIN_TEXT_AGENTS = [
    "curl",
    "httpie",
    "lwp-request",
    "wget",
    "python-requests",
    "python-httpx",
    "openbsd ftp",
    "powershell",
    "fetch",
    "aiohttp",
    "http_get",
    "xh",
    "nushell",
    "zig",
]

PLAIN_TEXT_PAGES = [":help", ":bash.function", ":translation", ":iterm2"]

TRANSLATION_TABLE = str.maketrans(
    {
        "\u2196": "\u256E",  # '↖' -> '╮'
        "\u2197": "\u256D",  # '↗' -> '╭'
        "\u2198": "\u2570",  # '↘' -> '╰'
        "\u2199": "\u256F",  # '↙' -> '╯'
        "\u26A1": "\u250C\u2518",
    }
)

_IPLOCATION_ORDER = os.environ.get("WTTR_IPLOCATION_ORDER", "geoip,ip2location,ipinfo")
IPLOCATION_ORDER = _IPLOCATION_ORDER.split(",")

_IP2LOCATION_KEY_FILE = os.environ.get(
    "WTTR_IP2LOCATION_KEY_FILE", os.environ["HOME"] + "/.ip2location.key"
)
IP2LOCATION_KEY = None
if os.path.exists(_IP2LOCATION_KEY_FILE):
    IP2LOCATION_KEY = open(_IP2LOCATION_KEY_FILE, "r").read().strip()

_IPINFO_KEY_FILE = os.environ.get(
    "WTTR_IPINFO_KEY_FILE", os.environ["HOME"] + "/.ipinfo.key"
)
IPINFO_TOKEN = None
if os.path.exists(_IPINFO_KEY_FILE):
    IPINFO_TOKEN = open(_IPINFO_KEY_FILE, "r").read().strip()

_WWO_KEY_FILE = os.environ.get("WTTR_WWO_KEY_FILE", os.environ["HOME"] + "/.wwo.key")
WWO_KEY = "key-is-not-specified"
USE_METNO = True
USER_AGENT = os.environ.get("WTTR_USER_AGENT", "")
if os.path.exists(_WWO_KEY_FILE):
    WWO_KEY = open(_WWO_KEY_FILE, "r").read().strip()
    USE_METNO = False


def error(text):
    "log error `text` and raise a RuntimeError exception"

    if not text.startswith("Too many queries"):
        print(text)
    logging.error("ERROR %s", text)
    raise RuntimeError(text)


def log(text):
    "log error `text` and do not raise any exceptions"

    if not text.startswith("Too many queries"):
        print(text)
        logging.info(text)


def debug_log(text):
    """
    Write `text` to the debug log
    """

    with open("/tmp/wttr.in-debug.log", "a") as f_debug:
        f_debug.write(text + "\n")


def get_help_file(lang):
    "Return help file for `lang`"

    help_file = os.path.join(MYDIR, "share/translations/%s-help.txt" % lang)
    if os.path.exists(help_file):
        return help_file
    return HELP_FILE


def remove_ansi(sometext):
    ansi_escape = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    return ansi_escape.sub("", sometext)
