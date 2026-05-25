# Настройки PostgreSQL
import os
from dotenv import load_dotenv
load_dotenv()  # reads .env from project root
DB_URL = os.getenv("DB_URL")
if not DB_URL:
  raise ValueError("DB_URL is not set. Add it to .env")

# Экономические константы
CNY_KZT_RATE = 65.0
ALIPAY_FEE = 0.03          # Комиссия эквайринга 3%
CARGO_RATE_KG = 1500.0     # Тариф логистики
KASPI_COMMISSION = 0.109   # Комиссия маркетплейса
IP_TAX_RATE = 0.04         # Налог ИП
LOCAL_DELIVERY = 1300.0    # Локальная доставка