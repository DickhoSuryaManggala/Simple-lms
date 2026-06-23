import requests
import time
import redis
import json

# Connect to Redis
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

def get_weather(city):
    """Simulasi API call yang lambat dengan caching Redis"""
    
    # Cek apakah data ada di cache
    cache_key = f"weather:{city}"
    cached_data = redis_client.get(cache_key)
    
    if cached_data:
        print(f"[Cache Hit] Menggunakan data cache untuk {city}")
        return json.loads(cached_data)
    
    # Jika tidak ada di cache, panggil API
    print(f"[Cache Miss] Memanggil API untuk {city}")
    time.sleep(2)  # Simulate slow API call
    
    # Gunakan API dummy untuk testing (karena example.com tidak real)
    # Atau gunakan Open-Meteo sebagai pengganti
    response = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude=-6.2088&longitude=106.8456&current=temperature_2m")
    weather_data = response.json()
    
    # Simpan ke Redis dengan expiry 5 menit (300 detik)
    redis_client.setex(cache_key, 300, json.dumps(weather_data))
    
    return weather_data

if __name__ == "__main__":
    # Test langsung di weather_api.py
    print(get_weather("Jakarta"))
