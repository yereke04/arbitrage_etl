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