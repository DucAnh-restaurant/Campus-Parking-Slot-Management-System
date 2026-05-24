#!/bin/bash

set -e

echo "[*] ==============================================="
echo "[*] Campus Parking Slot Management System - SETUP"
echo "[*] ==============================================="

if [ -f "/opt/parking/.setup_done" ]; then
    echo "[!] Hệ thống đã được cài đặt trước đó."
    echo "[!] Vui lòng reboot và hệ thống sẽ tự chạy."
    exit 1
fi

echo "[*] Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "[*] Installing Redis Server..."
sudo apt install -y redis-server

echo "[*] Configuring Redis..."
sudo systemctl enable redis-server
sudo systemctl start redis-server

echo "[*] Creating virtual environment..."
python3 -m venv venv

echo "[*] Activating virtual environment..."
source venv/bin/activate

echo "[*] Upgrading pip..."
pip install --upgrade pip

echo "[*] Installing requirements..."
pip install -r requirements.txt

echo "[*] Initializing database..."
python init_db.py

# Đánh dấu đã setup
sudo mkdir -p /opt/parking
sudo touch /opt/parking/.setup_done
sudo chown -R $USER:$USER /opt/parking 2>/dev/null || true

echo "[*] ==============================================="
echo "[*] SETUP HOÀN TẤT!"
echo "[*] Hãy reboot server để hệ thống tự động chạy."
echo "[*] ==============================================="