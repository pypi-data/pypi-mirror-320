import requests
from datetime import datetime
import os
import logging

start_hour = int(os.getenv("TELEGRAM_START_HOUR", 0))
end_hour = int(os.getenv("TELEGRAM_END_HOUR", 24))
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

logging.basicConfig(level=logging.INFO, filename="py_log.log",filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

def send(message: str) -> None:
    """
    Відправляє повідомлення в Telegram в заданий час (від 0 до 24).
    """
    now = datetime.now()
    current_hour = now.hour
    telegram_max_symbol = 4096
    if start_hour <= current_hour and current_hour < end_hour:
        try:
            if len(message) > telegram_max_symbol:
                message = message[:telegram_max_symbol]

            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message
            }
            my_rez=requests.post(url, json=payload, timeout=10)
            print(my_rez)

            if my_rez.status_code == 200:
                logging.info(f"Message sent successfully to chat_id={chat_id}")
            else:
                logging.error(f"Message sent with reason: {my_rez.reason}")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending message: {e}") # помилки, пов’язані з HTTP-запитами
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
    else:
        logging.info(f"Current time ({current_hour}) is outside the allowed range ({start_hour}-{end_hour}).")
