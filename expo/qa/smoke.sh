#!/bin/zsh
# Дымовая проба зала: прогоняет кадр во всех точках и печатает итог.
#   qa/smoke.sh            — по локальному серверу на :8777
#   qa/smoke.sh <url>      — по любому адресу
# Ловит то, чего не видит проверка синтаксиса: переменную, которой не стало.
URL=${1:-http://localhost:8777/expo/expo.html}
TMP=$(mktemp -d)
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --no-sandbox \
  --virtual-time-budget=12000 --user-data-dir=$TMP --dump-dom "$URL?smoke=1&rq=1&nc=$RANDOM" 2>/dev/null \
  | grep -o '<title>[^<]*</title>' | sed 's/<[^>]*>//g'
rm -rf $TMP
