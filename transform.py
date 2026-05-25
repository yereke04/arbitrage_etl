import pandas as pd
import numpy as np

# Импорт единого источника истины из конфигурации
from config import CNY_KZT_RATE, CARGO_RATE_KG, KASPI_COMMISSION

def clean_1688_csv(filepath: str) -> pd.DataFrame:
    """Загрузка и жесткая очистка сырого датасета 1688"""
    df = pd.read_csv(filepath)
    
    if 'price_cny' in df.columns:
        # expand=False гарантирует возврат Series для безопасного присвоения
        df['price_cny'] = df['price_cny'].astype(str).str.extract(r'(\d+\.?\d*)', expand=False).astype(float)
        
        df = df.dropna(subset=['price_cny'])
        
        # Использование курса из config.py
        df['sourcing_cost'] = df['price_cny'] * CNY_KZT_RATE
        
    return df

def apply_unit_economics(df: pd.DataFrame) -> pd.DataFrame:
    """Расчет бизнес-метрик с защитой от аномальных выбросов"""
    
    df['weight_kg'] = pd.to_numeric(df['weight_kg'], errors='coerce').fillna(0.3)
    
    def fix_weight(w):
        if w > 10:          
            w = w / 1000    
        if w < 0.2:         
            return 0.3
        return w
        
    df['weight_kg'] = df['weight_kg'].apply(fix_weight)

    # Использование тарифа из config.py
    df['cargo_cost'] = df['weight_kg'] * CARGO_RATE_KG

    df['retail_price_kzt'] = pd.to_numeric(df['retail_price_kzt'], errors='coerce').fillna(149999.0)
    
    # Применение точной ставки 10.9%
    df['commission_cost'] = df['retail_price_kzt'] * KASPI_COMMISSION
    
    # Фиксированный налог ИП (21 000 KZT/мес) не является прямой затратой на единицу товара.
    # Исключен из юнит-экономики для корректного расчета чистой маржинальности.
    df['tax_cost'] = 0 

    df['sourcing_cost'] = pd.to_numeric(df['sourcing_cost'], errors='coerce').fillna(0)
    
    df['total_fulfill_cost'] = (
        df['sourcing_cost'] + 
        df['cargo_cost'] + 
        df['commission_cost'] + 
        df['tax_cost']
    )
    df['net_profit'] = df['retail_price_kzt'] - df['total_fulfill_cost']

    invested_capital = df['sourcing_cost'] + df['cargo_cost']
    df['roi_percent'] = np.where(
        invested_capital > 0,
        (df['net_profit'] / invested_capital) * 100,
        0
    )

    df['roi_percent'] = df['roi_percent'].round(2)
    df['net_profit'] = df['net_profit'].round(2)
    df['total_fulfill_cost'] = df['total_fulfill_cost'].round(2)
    df['cargo_cost'] = df['cargo_cost'].round(2)

    return df