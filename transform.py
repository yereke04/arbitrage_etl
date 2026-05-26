import pandas as pd
import numpy as np
# Удален импорт CNY_KZT_RATE
from config import CARGO_RATE_KG, KASPI_COMMISSION, LOCAL_DELIVERY

VAT_1688_RATE = 0.138
CARD_PROCESSING_FEE = 0.03
def get_realtime_cny_kzt_rate(fallback_rate: float = 75.0, bank_spread: float = 1.068) -> float:
    """
    Получение актуального курса CNY/KZT с учетом комиссии банка за конвертацию.
    bank_spread = 1.068 (наценка банка/Alipay ~6.8% к биржевому курсу)
    """
    try:
        url = "https://open.er-api.com/v6/latest/CNY"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            pure_rate = data.get("rates", {}).get("KZT")
            if pure_rate:
                # Умножаем чистый биржевой курс на наценку банка
                real_acquiring_rate = float(pure_rate) * bank_spread
                print(f"[Курс Валют] Биржа: {float(pure_rate):.2f} ₸ | Списание с карты (с учетом спреда): {real_acquiring_rate:.2f} ₸")
                return real_acquiring_rate
        else:
            print(f"[Курс Валют] API недоступен (Код {response.status_code}).")
            
    except Exception as e:
        print(f"[Курс Валют] Сетевая ошибка: {e}")
        
    print(f"[Курс Валют] Используется резервный курс: {fallback_rate}")
    return fallback_rate
# Добавлен аргумент current_cny_rate
def clean_1688_csv(filepath: str, current_cny_rate: float) -> pd.DataFrame:
    df = pd.read_csv(filepath)
    
    if 'price_cny' in df.columns:
        df['price_cny'] = df['price_cny'].astype(str).str.extract(r'(\d+\.?\d*)', expand=False).astype(float)
        df = df.dropna(subset=['price_cny'])
        
        total_cny = df['price_cny'] * (1 + VAT_1688_RATE) * (1 + CARD_PROCESSING_FEE)
        # Динамический расчет
        df['sourcing_cost'] = total_cny * current_cny_rate 
        
    return df

# ... функция apply_unit_economics остается без изменений

def apply_unit_economics(df: pd.DataFrame) -> pd.DataFrame:
    df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce').fillna(0.4)
    
    # Минимальный порог веса изменен на 0.4 кг
    def fix_weight(w):
        if w > 10:          
            w = w / 1000    
        if w < 0.4:         
            return 0.4
        return w
        
    df['weight_kg'] = df['weight_kg'].apply(fix_weight)

    df['cargo_cost'] = df['weight_kg'] * CARGO_RATE_KG
    df['local_delivery_cost'] = LOCAL_DELIVERY

    df['retail_price_kzt'] = pd.to_numeric(df['retail_price_kzt'], errors='coerce').fillna(149999.0)
    df['commission_cost'] = df['retail_price_kzt'] * KASPI_COMMISSION
    
    # Налог ИП отключен
    df['tax_cost'] = 0 

    df['sourcing_cost'] = pd.to_numeric(df['sourcing_cost'], errors='coerce').fillna(0)
    
    df['total_fulfill_cost'] = (
        df['sourcing_cost'] + 
        df['cargo_cost'] + 
        df['local_delivery_cost'] +
        df['commission_cost'] + 
        df['tax_cost']
    )
    
    df['net_profit'] = df['retail_price_kzt'] - df['total_fulfill_cost']

    invested_capital = df['sourcing_cost'] + df['cargo_cost'] + df['local_delivery_cost']
    df['roi_percent'] = np.where(
        invested_capital > 0,
        (df['net_profit'] / invested_capital) * 100,
        0
    )

    df['roi_percent'] = df['roi_percent'].round(2)
    df['net_profit'] = df['net_profit'].round(2)
    df['total_fulfill_cost'] = df['total_fulfill_cost'].round(2)
    df['cargo_cost'] = df['cargo_cost'].round(2)
    df['commission_cost'] = df['commission_cost'].round(2)

    return df