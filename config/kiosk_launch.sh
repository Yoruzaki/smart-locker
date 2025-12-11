#!/usr/bin/env bash
export DISPLAY=:0
export XAUTHORITY=/home/pi/.Xauthority

# Disable screen blanking
xset s off
xset -dpms
xset s noblank

# Launch Chromium in kiosk mode pointing to local UI
/usr/bin/chromium-browser --noerrdialogs --kiosk http://localhost:5000/ &

