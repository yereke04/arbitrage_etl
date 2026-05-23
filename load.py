import os
import pandas as pd
from sqlalchemy import create_engine

def load_to_postgres(df: pd.DataFrame, db_url: str):
    # 1. Загрузка в БД
    engine = create_engine(db_url)
    df.to_sql('unit_economics', con=engine, if_exists='replace', index=False)
    print(f"[OK] Загружено {len(df)} строк в таблицу unit_economics.")
    
    # 2. Построение абсолютного пути для CSV
    # Определение папки, в которой находится файл load.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Сборка пути: ../arbitrage_etl/data/tableau_export.csv
    csv_path = os.path.join(base_dir, 'data', 'tableau_export.csv')
    
    # 3. Сохранение файла
    df.to_csv(csv_path, index=False)
    print(f"[OK] Файл для Tableau успешно сохранен: {csv_path}")