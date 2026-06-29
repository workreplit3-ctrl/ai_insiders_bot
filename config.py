import os

BOT_TOKEN="8650547243:AAFtRGnunF0PrJPjw1VJtdSXOel6Esx1CrQ"
_raw_admin_ids = os.getenv("ADMIN_IDS", "")
ADMIN_IDS = [int(x) for x in _raw_admin_ids.split(",") if x.strip().isdigit()]

MASTERCLASS_DATE = "25 июня"
MASTERCLASS_TOPIC = "AI-агенты"
PRICE_AFTER_24H = "79$"