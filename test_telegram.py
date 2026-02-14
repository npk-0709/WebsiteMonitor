#!/usr/bin/env python3
"""
Test Script để kiểm tra kết nối Telegram
"""

import json
import requests
import sys

def test_telegram():
    """Kiểm tra cấu hình Telegram"""
    
    print("🔍 Kiểm tra cấu hình Telegram...\n")
    
    # Đọc config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("❌ Không tìm thấy file config.json")
        return False
    except json.JSONDecodeError:
        print("❌ File config.json không đúng định dạng JSON")
        return False
    
    bot_token = config.get('telegram', {}).get('bot_token', '')
    chat_id = config.get('telegram', {}).get('chat_id', '')
    
    # Kiểm tra thông tin
    if 'YOUR_BOT_TOKEN_HERE' in bot_token:
        print("❌ Bạn chưa điền Bot Token vào config.json")
        print("   Hãy lấy Bot Token từ @BotFather trên Telegram")
        return False
    
    if 'YOUR_CHAT_ID_HERE' in chat_id:
        print("❌ Bạn chưa điền Chat ID vào config.json")
        print("   Hãy lấy Chat ID từ @getmyid_bot trên Telegram")
        return False
    
    print(f"✅ Bot Token: {bot_token[:10]}...{bot_token[-10:]}")
    print(f"✅ Chat ID: {chat_id}\n")
    
    # Test gửi tin nhắn
    print("📤 Đang gửi tin nhắn test...\n")
    
    api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': '🎉 <b>TEST THÀNH CÔNG!</b>\n\nHệ thống giám sát website đã sẵn sàng hoạt động!',
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            print("✅ THÀNH CÔNG! Kiểm tra Telegram để xem tin nhắn test")
            print("✅ Cấu hình Telegram hoạt động tốt!")
            print("\n🚀 Bạn có thể chạy: python website_monitor.py")
            return True
        else:
            print(f"❌ Lỗi gửi tin nhắn: {response.status_code}")
            print(f"   Chi tiết: {response.text}")
            
            if response.status_code == 401:
                print("\n💡 Bot Token không hợp lệ. Hãy kiểm tra lại từ @BotFather")
            elif response.status_code == 400:
                print("\n💡 Chat ID không đúng hoặc bạn chưa start bot")
                print("   Hãy gửi /start cho bot trên Telegram")
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout khi kết nối Telegram API")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối tới Telegram. Kiểm tra internet!")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("     KIỂM TRA CÁC HÌNH TELEGRAM BOT")
    print("=" * 60)
    print()
    
    success = test_telegram()
    
    print()
    print("=" * 60)
    
    sys.exit(0 if success else 1)
