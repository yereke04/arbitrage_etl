from curl_cffi import requests

def fetch_kaspi_price(product_id: str, city_id: str = "710000000") -> float:
    # URL без параметров в строке
    url = f"https://kaspi.kz/yml/offer-view/offers/{product_id}"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "ru-RU,ru;q=0.9",
        "Referer": f"https://kaspi.kz/shop/p/-{product_id}/",
        "Origin": "https://kaspi.kz",
        "Content-Type": "application/json"
    }
    
    # Параметры передаются в теле POST-запроса
    payload = {
        "cityId": city_id,
        "id": product_id,
        "limit": 10,
        "page": 0
    }
    
    try:
        response = requests.post(
            url, 
            json=payload,
            headers=headers, 
            impersonate="chrome120", 
            timeout=15
        )
        
        print(f"[{product_id}] Статус Kaspi API: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get('offers', [])
            if offers:
                # Находим минимальную цену среди всех продавцов (демпинг)
                return min([offer['price'] for offer in offers])
            else:
                print(f"[{product_id}] Нет активных продавцов.")
        else:
            print(f"[{product_id}] Ошибка ответа: {response.text[:100]}")
            
    except Exception as e:
        print(f"[{product_id}] Сетевая ошибка: {e}")
        
    return 149999.0 # Fallback цена при сбое

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