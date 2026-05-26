import pandas as pd
from config import DB_URL
# Добавлен импорт get_realtime_cny_kzt_rate
from extract import fetch_kaspi_price, get_realtime_cny_kzt_rate 
from transform import clean_1688_csv, apply_unit_economics
from load import load_to_postgres
from ai_mapper import get_clean_sku

def run_pipeline():
    print("0. Получение актуальных валютных курсов...")
    current_cny_rate = get_realtime_cny_kzt_rate(fallback_rate=70.0)
    print(f"[OK] Текущий курс CNY -> KZT: {current_cny_rate}")

    print("1. Извлечение и очистка данных 1688...")
    # Передаем курс в функцию трансформации
    df_1688 = clean_1688_csv("data/1688_parser (8).csv", current_cny_rate)
    
    # ... остальной код main.py остается без изменений
    
    print("2. AI-нормализация названий (Семантическая экстракция)...")
    # Создаем новую колонку с чистым названием для каждого товара
    df_1688['sku_core'] = df_1688['name'].apply(get_clean_sku)
    
    print("3. Получение розничных цен Kaspi...")
    # Теперь mapping.csv должен содержать колонки: sku_core, kaspi_id
    df_mapping = pd.read_csv("data/mapping.csv")
    
    # Объединяем базу 1688 и базу Kaspi по очищенному ядру модели
    df_merged = pd.merge(df_1688, df_mapping, on='sku_core', how='inner')
    
    df_merged['retail_price_kzt'] = df_merged['kaspi_id'].apply(
        lambda x: fetch_kaspi_price(str(x))
    )
    
    print("4. Расчет юнит-экономики...")
    df_final = apply_unit_economics(df_merged)
    
    print("5. Загрузка в хранилище (PostgreSQL)...")
    load_to_postgres(df_final, DB_URL)
    
    print("\nETL Конвейер успешно завершен.")

if __name__ == "__main__":
    run_pipeline()