#!/bin/zsh
cd "${0:A:h}" || exit 1
export HF_HUB_DISABLE_TELEMETRY=1
exec .venv/bin/python launch.py "$@"
