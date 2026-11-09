#!/bin/zsh
cd "${0:A:h}" || exit 1
if [[ -x ./uv ]]; then
  ema_uv=./uv
else
  ema_uv=$(command -v uv) || ema_uv=''
  for candidate in "$HOME/.local/bin/uv" /opt/homebrew/bin/uv /usr/local/bin/uv; do
    [[ -n "$ema_uv" ]] && break
    [[ -x "$candidate" ]] && ema_uv="$candidate"
  done
fi
if [[ -z "$ema_uv" ]]; then
  print -u2 "uv bulunamadı. GitHub Releases'tan Mac paketini indir veya https://docs.astral.sh/uv/getting-started/installation/ adresinden uv'yi kur."
  exit 1
fi
exec "$ema_uv" run --locked python -X utf8 launch.py "$@"
