#!/bin/bash

set -e

echo "[*] ==============================================="
echo "[*] Campus Parking Slot Management System - SETUP"
echo "[*] ==============================================="

# Kiểm tra đã setup chưa
if [ -f "/opt/parking/.setup_done" ]; then
    echo "[!] Hệ thống đã được cài đặt trước đó."
    echo "[!] Vui lòng reboot máy để hệ thống tự chạy."
    exit 1
fi

echo "[*] Installing Redis Server..."
sudo apt install -y redis-server

echo "[*] Configuring Redis to start on boot..."
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

# ==================== TẠO SYSTEMD SERVICE ====================
echo "[*] Creating systemd service for auto-start..."

USERNAME=$(whoami)
PROJECT_PATH=$(pwd)

sudo cat > /etc/systemd/system/parking.service << EOF
[Unit]
Description=Campus Parking Slot Management System
After=network.target redis-server.service
Wants=redis-server.service

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$PROJECT_PATH
ExecStart=/bin/bash $PROJECT_PATH/start.sh
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Kích hoạt service
sudo systemctl daemon-reload
sudo systemctl enable parking.service

# Đánh dấu đã setup xong
sudo mkdir -p /opt/parking
sudo touch /opt/parking/.setup_done
sudo chown -R $USERNAME:$USERNAME /opt/parking 2>/dev/null || true

echo "[*] ==============================================="
echo "[*] SETUP HOÀN TẤT!"
echo "[*] Hệ thống sẽ tự động chạy mỗi khi khởi động máy."
echo "[*] Bạn có thể reboot ngay bây giờ."
echo "[*] ==============================================="