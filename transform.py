import pandas as pd
import numpy as np

def clean_1688_csv(filepath: str) -> pd.DataFrame:
    """Загрузка и жесткая очистка сырого датасета 1688"""
    df = pd.read_csv(filepath)
    
    if 'price_cny' in df.columns:
        # 1. Извлекаем только цифры. Игнорируем иероглифы (¥, 元) и текст
        df['price_cny'] = df['price_cny'].astype(str).str.extract(r'(\d+\.?\d*)').astype(float)
        
        # 2. Удаляем "мусорные" строки, где скрейпер не смог достать цену
        df = df.dropna(subset=['price_cny'])
        
        # 3. Базовый расчет себестоимости в тенге (курс 66.95)
        df['sourcing_cost'] = df['price_cny'] * 66.95
        
    return df

def apply_unit_economics(df: pd.DataFrame) -> pd.DataFrame:
    """Расчет бизнес-метрик с защитой от аномальных выбросов"""
    
    # 1. Умная нормализация веса (Защита от граммов)
    df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce').fillna(0.3)
    
    def fix_weight(w):
        if w > 10:          # Если значение больше 10, это 100% граммы.
            w = w / 1000    # Конвертируем 300 г -> 0.3 кг
        if w < 0.2:         # Применяем порог минимального веса
            return 0.3
        return w
        
    df['weight_kg'] = df['weight_kg'].apply(fix_weight)

    # 2. Карго (3000 ₸ / кг)
    CARGO_RATE_KZT = 3000 
    df['cargo_cost'] = df['weight_kg'] * CARGO_RATE_KZT

    # 3. Комиссии маркетплейса и налоги
    df['retail_price_kzt'] = pd.to_numeric(df['retail_price_kzt'], errors='coerce').fillna(149999.0)
    df['commission_cost'] = df['retail_price_kzt'] * 0.11
    df['tax_cost'] = df['retail_price_kzt'] * 0.04

    # 4. Расчет прибыли
    df['sourcing_cost'] = pd.to_numeric(df['sourcing_cost'], errors='coerce').fillna(0)
    
    df['total_fulfill_cost'] = (
        df['sourcing_cost'] + 
        df['cargo_cost'] + 
        df['commission_cost'] + 
        df['tax_cost']
    )
    df['net_profit'] = df['retail_price_kzt'] - df['total_fulfill_cost']

    # 5. ROI
    invested_capital = df['sourcing_cost'] + df['cargo_cost']
    df['roi_percent'] = np.where(
        invested_capital > 0,
        (df['net_profit'] / invested_capital) * 100,
        0
    )

    # 6. Округление до 2 знаков после запятой
    df['roi_percent'] = df['roi_percent'].round(2)
    df['net_profit'] = df['net_profit'].round(2)
    df['total_fulfill_cost'] = df['total_fulfill_cost'].round(2)
    df['cargo_cost'] = df['cargo_cost'].round(2)

    return df