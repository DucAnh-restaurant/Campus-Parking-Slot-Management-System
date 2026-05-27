#!/bin/bash

echo "[*] Initializing database..."
python init_db.py

echo "[*] ==============================================="
echo "[*] Campus Parking Slot Management System"
echo "[*] ==============================================="

if [ ! -f "/opt/parking/.setup_done" ]; then
    echo "[!] Hệ thống chưa được cài đặt! Chạy ./setup.sh trước."
    exit 1
fi

cd "$(dirname "$0")"

source venv/bin/activate

IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo "[+] IP của máy       : $IP_ADDRESS"
echo "[+] Web Local     : http://127.0.0.1:5000"
echo "[+] Local Domain     : http://parking.local:5000"
echo "[*] ==============================================="
echo "[*] Ứng dụng đang chạy..."
echo ""

exec python app.py