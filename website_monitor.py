#!/usr/bin/env python3
"""
Website Monitoring System with Telegram Alerts
Hệ thống giám sát website và cảnh báo qua Telegram
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional
import sys
from pathlib import Path

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Quản lý thông báo Telegram"""
    
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    def send_message(self, message: str) -> bool:
        """Gửi tin nhắn qua Telegram"""
        try:
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ Đã gửi thông báo Telegram thành công")
                return True
            else:
                logger.error(f"❌ Lỗi gửi Telegram: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối Telegram: {str(e)}")
            return False
    
    def send_alert(self, website_name: str, url: str, status_code: int, error_msg: str = ""):
        """Gửi cảnh báo máy chủ sập"""
        emoji = "🔴"
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        message = f"{emoji} <b>CẢNH BÁO MÁY CHỦ</b>\n\n"
        message += f"🌐 <b>Website:</b> {website_name}\n"
        message += f"🔗 <b>URL:</b> {url}\n"
        message += f"📊 <b>Status Code:</b> {status_code}\n"
        
        if error_msg:
            message += f"⚠️ <b>Lỗi:</b> {error_msg}\n"
        
        message += f"🕐 <b>Thời gian:</b> {timestamp}\n"
        message += f"\n❗ Máy chủ có thể đã sập!"
        
        self.send_message(message)
    
    def send_recovery(self, website_name: str, url: str):
        """Gửi thông báo máy chủ đã hoạt động trở lại"""
        emoji = "✅"
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        message = f"{emoji} <b>MÁY CHỦ ĐÃ PHỤC HỒI</b>\n\n"
        message += f"🌐 <b>Website:</b> {website_name}\n"
        message += f"🔗 <b>URL:</b> {url}\n"
        message += f"🕐 <b>Thời gian:</b> {timestamp}\n"
        message += f"\n✨ Máy chủ đã hoạt động bình thường!"
        
        self.send_message(message)


class WebsiteMonitor:
    """Quản lý giám sát website"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config = self.load_config(config_path)
        self.telegram = TelegramNotifier(
            self.config['telegram']['bot_token'],
            self.config['telegram']['chat_id']
        )
        self.website_status = {}  # Lưu trạng thái của các website
        
    def load_config(self, config_path: str) -> Dict:
        """Đọc file cấu hình"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info(f"✅ Đã tải cấu hình từ {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"❌ Không tìm thấy file cấu hình: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Lỗi định dạng JSON: {str(e)}")
            sys.exit(1)
    
    def check_website(self, website: Dict) -> Dict:
        """Kiểm tra trạng thái một website"""
        url = website['url']
        name = website['name']
        timeout = self.config['monitoring']['timeout']
        retry_count = self.config['monitoring']['retry_count']
        retry_delay = self.config['monitoring']['retry_delay']
        
        result = {
            'name': name,
            'url': url,
            'status_code': None,
            'is_ok': False,
            'error': None,
            'response_time': None
        }
        
        for attempt in range(retry_count):
            try:
                start_time = time.time()
                response = requests.get(
                    url,
                    timeout=timeout,
                    headers={'User-Agent': 'Mozilla/5.0 Website Monitor'}
                )
                response_time = time.time() - start_time
                
                result['status_code'] = response.status_code
                result['response_time'] = round(response_time, 2)
                
                if response.status_code == 200:
                    result['is_ok'] = True
                    logger.info(f"✅ {name} ({url}): OK - {response.status_code} - {result['response_time']}s")
                    return result
                else:
                    result['error'] = f"HTTP {response.status_code}"
                    logger.warning(f"⚠️ {name} ({url}): {response.status_code} - Thử lại {attempt + 1}/{retry_count}")
                
            except requests.exceptions.Timeout:
                result['error'] = "Timeout"
                logger.warning(f"⚠️ {name} ({url}): Timeout - Thử lại {attempt + 1}/{retry_count}")
                
            except requests.exceptions.ConnectionError:
                result['error'] = "Connection Error"
                logger.warning(f"⚠️ {name} ({url}): Lỗi kết nối - Thử lại {attempt + 1}/{retry_count}")
                
            except Exception as e:
                result['error'] = str(e)
                logger.warning(f"⚠️ {name} ({url}): {str(e)} - Thử lại {attempt + 1}/{retry_count}")
            
            # Đợi trước khi thử lại
            if attempt < retry_count - 1:
                time.sleep(retry_delay)
        
        # Nếu đã thử hết số lần retry
        logger.error(f"❌ {name} ({url}): FAILED - {result['error']}")
        return result
    
    def monitor_all(self):
        """Kiểm tra tất cả website"""
        logger.info("=" * 60)
        logger.info("🔍 Bắt đầu kiểm tra các website...")
        
        websites = [w for w in self.config['websites'] if w.get('enabled', True)]
        
        for website in websites:
            result = self.check_website(website)
            website_key = website['url']
            
            # Lấy trạng thái trước đó
            previous_status = self.website_status.get(website_key, {}).get('is_ok', True)
            current_status = result['is_ok']
            
            # Cập nhật trạng thái mới
            self.website_status[website_key] = result
            
            # Gửi cảnh báo nếu có thay đổi trạng thái
            if not current_status and previous_status:
                # Website vừa bị lỗi
                self.telegram.send_alert(
                    website['name'],
                    website['url'],
                    result['status_code'] or 0,
                    result['error']
                )
            elif current_status and not previous_status:
                # Website đã phục hồi
                self.telegram.send_recovery(
                    website['name'],
                    website['url']
                )
        
        logger.info("✅ Hoàn thành kiểm tra")
        logger.info("=" * 60)
    
    def start(self):
        """Bắt đầu giám sát liên tục"""
        check_interval = self.config['monitoring']['check_interval']
        
        logger.info("🚀 Khởi động hệ thống giám sát website")
        logger.info(f"⏱️  Kiểm tra mỗi {check_interval} giây")
        logger.info(f"🌐 Giám sát {len(self.config['websites'])} website")
        
        # Gửi thông báo khởi động
        startup_msg = "🚀 <b>HỆ THỐNG GIÁM SÁT ĐÃ KHỞI ĐỘNG</b>\n\n"
        startup_msg += f"🌐 Số website: {len(self.config['websites'])}\n"
        startup_msg += f"⏱️ Chu kỳ kiểm tra: {check_interval}s\n"
        startup_msg += f"🕐 Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        self.telegram.send_message(startup_msg)
        
        try:
            while True:
                self.monitor_all()
                logger.info(f"😴 Chờ {check_interval} giây cho lần kiểm tra tiếp theo...\n")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("\n⛔ Dừng hệ thống giám sát")
            shutdown_msg = "⛔ <b>HỆ THỐNG GIÁM SÁT ĐÃ DỪNG</b>\n\n"
            shutdown_msg += f"🕐 Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
            self.telegram.send_message(shutdown_msg)
            sys.exit(0)


def main():
    """Hàm chính"""
    monitor = WebsiteMonitor('config.json')
    monitor.start()


if __name__ == "__main__":
    main()
