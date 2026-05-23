import os
import json
import time
import pandas as pd
from google import genai
from google.genai import types

# Инициализация клиента
client = genai.Client(api_key="AIzaSyBy5_uUVyq3oX6yBWYenjVW--GY1uDLSx0")

CACHE_FILE = "data/mapping_cache.json"

# Жесткое определение кэша (Чтение из файла временно отключено)
CACHE_DB = {
    "Suitable for Logitech Gprox Superlight 2 Dogpiwang Third-Generation Wireless Gaming Mouse": "Logitech G Pro X Superlight 2",
    "Logitech Mx Master4 High-Performance Business Ergonomic Mouse Wireless Bluetooth Dual": "Logitech MX Master 4",
    "罗技 GPW4 鹰眼GPROX SUPERLIGHT2 DEX 无线游戏鼠标网吧网咖": "Logitech G Pro X Superlight 2",
    "Logitech (g) Gpw4 Generation Wireless Gaming Mouse for Small Hands, Dual-Mode Mechanical": "Logitech G Pro Wireless",
    "Suitable for Logitech Gpw4 Puppy Wireless Mouse Gaming E-Sports Peripherals Gpw4 Mouse Pink": "Logitech G Pro Wireless",
    "Suitable for Logitech Gpw2 King Kong Wireless Mouse, the Second Generation Gaming E-Sports Gpw 2 King Kong Edition - Red": "Logitech G Pro Wireless",
    "Logitech Gpw5 Snow Leopard Wireless Mouse Electromagnetic Micro-Motion Gaming Mouse Gpw5": "Logitech G Pro X Superlight 2",
    "适用罗技无线鼠标gpw5狗屁王五代雪豹": "Logitech G Pro X Superlight 2",
    "适用罗技GPW5雪豹无线鼠标 狗屁王五代8K电磁微动电竞游戏双模": "Logitech G Pro X Superlight 2",
    "Logitech Gpro X Superstrike 5Th Generation Snow Leopard Wireless Gaming Mouse Is Suitable for Use": "Logitech G Pro X Superlight 2",
    "罗技GPW5雪豹无线鼠标 狗屁王五代8K电磁微动电竞游戏双模轻量化": "Logitech G Pro X Superlight 2",
    "Logitech Master Series Mx Master 4 High Performance Wireless Bluetooth Mouse": "Logitech MX Master 4",
    "Suitable for Logitech Gpw4 Puppy Wireless Mouse Gaming E-Sports Peripherals Gpw4 Mouse Black": "Logitech G Pro Wireless"
}

def extract_sku_core_gemini(raw_name: str) -> str:
    prompt = f"""
    Извлеки официальное глобальное название модели устройства из текста.
    Проигнорируй маркетинговые слова (Suitable for, Generation), сленг, иероглифы и цвета.
    Верни ТОЛЬКО чистое название модели без знаков препинания и лишних слов.
    Текст: {raw_name}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0)
        )
        time.sleep(15)
        return response.text.strip()
        
    except Exception as e:
        print(f"[Ошибка AI] {e}")
        time.sleep(15) 
        return raw_name

def get_clean_sku(raw_name: str) -> str:
    # 1. Проверяем наш жесткий кэш
    if raw_name in CACHE_DB:
        print(f"[Кэш] Найдено совпадение для: {raw_name[:30]}...")
        return CACHE_DB[raw_name]
    
    # 2. Если названия нет в кэше — ИГНОРИРУЕМ ИИ (обход лимита 429)
    # Скрипт просто вернет оригинальное длинное название и пойдет дальше
    print(f"[Пропуск AI] Новая строка (лимит исчерпан): {raw_name[:40]}...")
    
    return raw_name