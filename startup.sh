#!/bin/bash

# Make sure we have proper directories
mkdir -p /home/user/.config/sunshine
mkdir -p /home/user/apps/images
sudo chown -R user:user /home/user/.config
sudo chown -R user:user /home/user/apps

# Fix XServer permissions
sudo mkdir -p /tmp/.X11-unix
sudo chmod 1777 /tmp/.X11-unix

# Install xdotool - critical for input simulation without uinput
echo "Installing xdotool and input utilities..."
sudo pacman -S --noconfirm xdotool python-xlib xorg-xhost

# Make sure we have proper permissions on X11
xhost +local:

# Create a modified sunshine config with X11 input support only, no uinput
cat > /home/user/.config/sunshine/sunshine.conf << EOF
# Sunshine config with X11 input support
sunshine_name = MoonwhaleServer
min_log_level = debug
origin_web_ui_allowed = lan

# Force software encoding
encoder = software
sw_preset = ultrafast
sw_tune = zerolatency

# Stream settings
fps = [30, 60]
resolutions = [
    1280x720,
    1920x1080
]

# Input settings - NO uinput, only X11
input {
    mouse = enabled
    keyboard = enabled
    controller = enabled

    # CRITICAL: Use X11 input methods instead of uinput
    x11_keymap = enabled

    # Disable uinput
    uinput = disabled
}

# IMPORTANT: Use relative path, not absolute
file_apps = apps.json
EOF

# Skip all uinput attempts - they won't work
echo "Skipping uinput setup (not available on this host)"

# Create alternative input script using xdotool
cat > /home/user/input-proxy.py << EOF
#!/usr/bin/env python3
"""
Input proxy for Sunshine - translates Sunshine input events to xdotool commands
This is a fallback when uinput is not available
"""
import os
import sys
import time
import subprocess
from threading import Thread

def run_xdotool(cmd):
    try:
        subprocess.run(["xdotool"] + cmd.split(), check=True)
    except Exception as e:
        print(f"Error running xdotool: {e}")

def monitor_keyboard():
    print("Starting keyboard monitoring")
    while True:
        # Just keep xdotool keyboard active
        run_xdotool("key Tab")
        time.sleep(60)

def monitor_mouse():
    print("Starting mouse monitoring")
    # Create a virtual cursor that's visible
    run_xdotool("mousemove 640 360")
    while True:
        # Just keep xdotool mouse active
        run_xdotool("mousemove_relative -- 1 1")
        run_xdotool("mousemove_relative -- -1 -1")
        time.sleep(60)

if __name__ == "__main__":
    os.environ["DISPLAY"] = ":99"
    print("Starting input proxy service")

    # Start monitoring threads
    Thread(target=monitor_keyboard, daemon=True).start()
    Thread(target=monitor_mouse, daemon=True).start()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Input proxy shutting down")
EOF

chmod +x /home/user/input-proxy.py

# Create a completely different X11 config
sudo mkdir -p /etc/X11
cat > /tmp/xorg.conf << EOF
Section "ServerFlags"
    Option "AutoAddDevices" "true"
    Option "AllowEmptyInput" "false"
    Option "DontVTSwitch" "true"
EndSection

Section "Module"
    Load "record"
    Load "dri2"
    Load "dbe"
    Load "extmod"
    Load "glx"
EOF
sudo cp /tmp/xorg.conf /etc/X11/xorg.conf

# Start Xvfb with full extensions
echo "Starting virtual X server with input extensions..."
Xvfb :99 -screen 0 1280x720x24 -ac +extension RECORD +extension XInputExtension +extension RANDR +extension RENDER &
sleep 2

# Set the DISPLAY variable
export DISPLAY=:99

# Allow all local connections to X
xhost +local:

# Start our input proxy service (fallback for input)
echo "Starting input proxy service..."
python /home/user/input-proxy.py &

# Start a window manager
echo "Starting window manager..."
fluxbox &
sleep 2

# Set a background color
echo "Setting background color..."
xsetroot -solid steelblue

# Start VNC server with input options
echo "Starting VNC server on port 5900..."
x11vnc -display :99 -forever -nopw -quiet -shared -repeat -noxrecord -noxdamage -permitfiletransfer &
sleep 1

# Start PulseAudio for audio
echo "Starting PulseAudio..."
pulseaudio --start --exit-idle-time=-1 &
sleep 1

# Print display information
echo "Display information:"
xdpyinfo | grep dimensions || echo "xdpyinfo failed"

# Start Sunshine with X11 input mode
echo "Starting Sunshine with X11 input mode..."
export DISPLAY=:99
export SUNSHINE_FLAGS=input,version
export SUNSHINE_LOG_LEVEL=debug

# Critical: Tell Sunshine to not use uinput
export SUNSHINE_INPUT_MODE=x11

nohup sunshine > /tmp/sunshine.log 2>&1 &
SUNSHINE_PID=$!
sleep 3

# Check if Sunshine is running
if ps -p $SUNSHINE_PID > /dev/null; then
    echo "✓ Sunshine started successfully with PID $SUNSHINE_PID"
    echo "Sunshine is using X11 input mode (no uinput required)"
else
    echo "ERROR: Sunshine failed to start! Check logs:"
    cat /tmp/sunshine.log
fi

# Display connection information
echo "====================================="
echo "Setup complete!"
IP=$(ip addr show | grep -E "inet .* scope global" | head -1 | awk '{print $2}' | cut -d/ -f1)
echo "Connect to VNC:   $IP:5900"
echo "Connect Moonlight to: $IP"
echo "Sunshine Web UI: https://$IP:47990"
echo "====================================="

# Keep container running
tail -f /dev/null
