# 🔍 Hệ Thống Giám Sát Website với Telegram

Hệ thống tự động theo dõi nhiều website và gửi cảnh báo qua Telegram khi phát hiện lỗi.

## ✨ Tính Năng

- ✅ Theo dõi nhiều website cùng lúc
- 🔔 Cảnh báo qua Telegram khi máy chủ sập (status code khác 200)
- 🔄 Tự động retry khi phát hiện lỗi
- 📊 Logging chi tiết
- ⚡ Thông báo khi máy chủ phục hồi
- 🎯 Cấu hình dễ dàng qua file JSON

## 📋 Yêu Cầu

- Python 3.7+
- Telegram Bot Token
- Chat ID của Telegram

## 🚀 Cài Đặt

### Bước 1: Cài đặt thư viện

```bash
pip install -r requirements.txt
```

### Bước 2: Tạo Telegram Bot

1. Mở Telegram và tìm `@BotFather`
2. Gửi lệnh `/newbot`
3. Đặt tên cho bot
4. Lưu lại **Bot Token** (ví dụ: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Bước 3: Lấy Chat ID

**Cách 1: Dùng bot GetMyId**
1. Tìm bot `@getmyid_bot` trên Telegram
2. Gửi `/start`
3. Bot sẽ trả về Chat ID của bạn

**Cách 2: Dùng API**
1. Gửi tin nhắn cho bot của bạn
2. Truy cập: `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
3. Tìm giá trị `"chat":{"id":123456789}`

### Bước 4: Cấu Hình

Mở file `config.json` và điền thông tin:

```json
{
  "telegram": {
    "bot_token": "YOUR_BOT_TOKEN_HERE",  // ← Thay bằng Bot Token
    "chat_id": "YOUR_CHAT_ID_HERE"       // ← Thay bằng Chat ID
  },
  "monitoring": {
    "check_interval": 300,    // Kiểm tra mỗi 5 phút (300 giây)
    "timeout": 30,            // Timeout 30 giây
    "retry_count": 3,         // Thử lại 3 lần khi có lỗi
    "retry_delay": 5          // Đợi 5 giây giữa các lần retry
  },
  "websites": [
    {
      "name": "Website 1",
      "url": "https://example.com",
      "enabled": true
    }
  ]
}
```

### Bước 5: Thêm Website Cần Giám Sát

Thêm website vào mảng `websites` trong `config.json`:

```json
"websites": [
  {
    "name": "Website Chính",
    "url": "https://mywebsite.com",
    "enabled": true
  },
  {
    "name": "API Server",
    "url": "https://api.mywebsite.com/health",
    "enabled": true
  },
  {
    "name": "Blog",
    "url": "https://blog.mywebsite.com",
    "enabled": false  // ← Tạm tắt giám sát
  }
]
```

## 🎯 Sử Dụng

### Chạy Hệ Thống

```bash
python website_monitor.py
```

### Chạy Nền (Background)

**Trên Linux/Mac:**
```bash
nohup python website_monitor.py > output.log 2>&1 &
```

**Dùng screen:**
```bash
screen -S monitor
python website_monitor.py
# Nhấn Ctrl+A, sau đó D để detach
```

**Dùng systemd (Linux):**

Tạo file `/etc/systemd/system/website-monitor.service`:

```ini
[Unit]
Description=Website Monitor Service
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/script
ExecStart=/usr/bin/python3 /path/to/script/website_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Sau đó:
```bash
sudo systemctl enable website-monitor
sudo systemctl start website-monitor
sudo systemctl status website-monitor
```

## 📊 Ví Dụ Thông Báo

### Khi Phát Hiện Lỗi:
```
🔴 CẢNH BÁO MÁY CHỦ

🌐 Website: Website Chính
🔗 URL: https://mywebsite.com
📊 Status Code: 503
⚠️ Lỗi: HTTP 503
🕐 Thời gian: 14/02/2026 10:30:15

❗ Máy chủ có thể đã sập!
```

### Khi Máy Chủ Phục Hồi:
```
✅ MÁY CHỦ ĐÃ PHỤC HỒI

🌐 Website: Website Chính
🔗 URL: https://mywebsite.com
🕐 Thời gian: 14/02/2026 10:35:20

✨ Máy chủ đã hoạt động bình thường!
```

## 📝 Log File

Tất cả hoạt động được ghi vào file `monitor.log`:

```
2026-02-14 10:30:15,123 - INFO - ✅ Website Chính (https://mywebsite.com): OK - 200 - 0.45s
2026-02-14 10:35:20,456 - ERROR - ❌ API Server (https://api.mywebsite.com): FAILED - Connection Error
```

## ⚙️ Tùy Chỉnh

### Thay Đổi Chu Kỳ Kiểm Tra

```json
"monitoring": {
  "check_interval": 60  // Kiểm tra mỗi 1 phút
}
```

### Tăng Số Lần Retry

```json
"monitoring": {
  "retry_count": 5,      // Thử lại 5 lần
  "retry_delay": 10      // Đợi 10 giây giữa các lần
}
```

### Timeout Dài Hơn

```json
"monitoring": {
  "timeout": 60  // Timeout 60 giây
}
```

## 🐛 Xử Lý Lỗi

### Lỗi "Bot Token Invalid"
- Kiểm tra lại Bot Token từ BotFather
- Đảm bảo không có khoảng trắng thừa

### Lỗi "Chat ID Invalid"
- Kiểm tra lại Chat ID
- Đảm bảo đã gửi `/start` cho bot

### Không Nhận Được Thông Báo
1. Kiểm tra bot có bị block không
2. Gửi tin nhắn cho bot để kích hoạt
3. Kiểm tra log file `monitor.log`

## 📦 Cấu Trúc Thư Mục

```
.
├── website_monitor.py    # Script chính
├── config.json          # File cấu hình
├── requirements.txt     # Thư viện Python
├── monitor.log         # Log file (tự tạo)
└── README.md           # Hướng dẫn
```

## 🔒 Bảo Mật

- **KHÔNG** commit file `config.json` lên Git (chứa Bot Token)
- Thêm vào `.gitignore`:
  ```
  config.json
  *.log
  ```
- Giữ Bot Token an toàn, không chia sẻ

## 💡 Tips

1. **Kiểm tra nhiều endpoint:** Thêm `/health`, `/api/status` vào danh sách
2. **Phân loại website:** Đặt tên rõ ràng để dễ nhận biết
3. **Backup cấu hình:** Lưu template `config.json` riêng
4. **Monitor cả HTTP và HTTPS:** Đảm bảo SSL certificate hợp lệ

## 📞 Hỗ Trợ

Nếu gặp vấn đề:
1. Kiểm tra file `monitor.log`
2. Xem lại cấu hình trong `config.json`
3. Đảm bảo internet kết nối ổn định

## 📄 License

MIT License - Tự do sử dụng và chỉnh sửa.
