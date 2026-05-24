#!/bin/bash

echo "[*] ==============================================="
echo "[*] Campus Parking Slot Management System"
echo "[*] ==============================================="

if [ ! -f "/opt/parking/.setup_done" ]; then
    echo "[!] Hệ thống chưa được cài đặt! Chạy ./setup.sh trước."
    exit 1
fi

# Khởi động Redis nếu chưa chạy
if ! systemctl is-active --quiet redis-server; then
    echo "[*] Khởi động Redis..."
    sudo systemctl start redis-server
fi

source venv/bin/activate

# Lấy IP của máy
IP_ADDRESS=$(hostname -I | awk '{print $1}')

echo "[+] IP của máy       : $IP_ADDRESS"
# echo "[+] Truy cập Web     : http://$IP_ADDRESS:5000"
echo "[+] Local Domain     : http://parking.local:5000"
echo "[*] ==============================================="
echo "[*] Ứng dụng đang chạy... (Nhấn Ctrl + C để dừng)"
echo ""

python app.py