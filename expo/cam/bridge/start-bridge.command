#!/bin/zsh
# macOS: double-click, or run from Terminal. Downloads go2rtc once, then runs it.
cd "$(dirname "$0")"
VER=v1.9.14
[[ $(uname -m) == arm64 ]] && ARCH=mac_arm64 || ARCH=mac_amd64
if [[ ! -x bin/go2rtc ]]; then
  mkdir -p bin && echo "downloading go2rtc $VER ($ARCH)…"
  curl -fL -o bin/go2rtc.zip "https://github.com/AlexxIT/go2rtc/releases/download/$VER/go2rtc_$ARCH.zip" || exit 1
  unzip -o -q bin/go2rtc.zip -d bin && rm bin/go2rtc.zip && chmod +x bin/go2rtc
fi
[[ -f camera.env ]] || { echo "camera.env is missing — copy camera.env.example and fill it in"; exit 1; }
set -a; source ./camera.env; set +a
echo "bridge on http://127.0.0.1:1984  (open it to see the camera)"
exec bin/go2rtc -config go2rtc.yaml
