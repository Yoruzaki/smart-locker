#!/usr/bin/env bash
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Launch Chromium in kiosk mode pointing to local UI
# On newer Raspberry Pi OS releases the binary is "chromium" (not chromium-browser)
if command -v chromium-browser >/dev/null 2>&1; then
  BROWSER=chromium-browser
else
  BROWSER=chromium
fi

$BROWSER --noerrdialogs --kiosk http://localhost:5000/ &

