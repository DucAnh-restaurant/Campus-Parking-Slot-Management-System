#!/bin/bash

set -e

echo "[*] ==============================================="
echo "[*] Campus Parking Slot Management System - SETUP"
echo "[*] ==============================================="

if [ -f "/opt/parking/.setup_done" ]; then
    echo "[!] Hệ thống đã được cài đặt trước đó."
    echo "[!] Vui lòng reboot máy để hệ thống tự chạy."
    exit 1
fi

echo "[*] Installing Redis Server..."
sudo apt update
sudo apt install -y redis-server python3-venv

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

echo "[*] Creating systemd service..."

USERNAME=$(whoami)
PROJECT_PATH=$(pwd)

chmod +x start.sh

# Tạo file systemd service cho ứng dụng
sudo tee /etc/systemd/system/parking.service > /dev/null << EOF
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

# StandardInput=tty
# StandardOutput=tty
# StandardError=tty
# TTYPath=/dev/tty1

# Thay thế các dòng StandardInput/Output bằng các dòng dưới đây
StandardOutput=journal
StandardError=journal


[Install]
WantedBy=multi-user.target
EOF

# Reload systemd, enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable parking.service

# Restart dịch vụ để áp dụng ngay các thay đổi
sudo systemctl restart parking.service

# Tạo file đánh dấu đã setup xong
sudo mkdir -p /opt/parking
sudo touch /opt/parking/.setup_done
sudo chown -R $USERNAME:$USERNAME /opt/parking

# Tạo local domain parking.local
echo "[*] ==============================================="
echo "[*] SETUP HOÀN TẤT!"
echo "[*] Hệ thống sẽ hiển thị trực tiếp trên console sau reboot."
echo "[*] ==============================================="

# Reboot máy để áp dụng thay đổi và khởi động dịch vụ
sudo reboot