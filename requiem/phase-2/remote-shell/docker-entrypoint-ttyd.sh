#!/bin/sh
set -e
exec ttyd \
  -W \
  -w /home/ubuntu \
  -p 7681 \
  ${TTYD_IDLE_TIMEOUT:+--max-idle-time "$TTYD_IDLE_TIMEOUT"} \
  -t fontSize=14 \
  -t "theme={'background':'#000000'}" \
  /opt/remote-shell/venv/bin/python /opt/remote-shell/remote_shell.py
