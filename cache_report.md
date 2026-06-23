# Laporan Redis Caching Exercise

## 📸 Hasil Test

### 1. Screenshot Hasil Test (First Call vs Second Call)
![Test Result](image/Screenshot%202026-06-23%20125854.png)

### 2. Screenshot Redis CLI (Menunjukkan Key weather:Jakarta)
![Redis CLI](image/Screenshot%202026-06-23%20125923.png)

---

## 💻 Kode yang Dimodifikasi

### weather_api.py
```python
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
```

---

## 🔧 Redis Commands yang Digunakan

1. **SET dengan Expiry (EX)
   - Digunakan untuk menyimpan data ke cache dengan waktu kadaluarsa
   - Perintah: `redis_client.setex(cache_key, 300, data)
   - Atau perintah dasar Redis CLI: `SETEX weather:Jakarta 300 "{data}

2. **GET**
   - Digunakan untuk mengambil data dari cache
   - Perintah: `redis_client.get(cache_key)
   - Atau perintah dasar Redis CLI: `GET weather:Jakarta

3. **DELETE (Tidak digunakan di kode tapi penting untuk melihat keys)
   - Perintah: `KEYS weather:*` untuk melihat semua key yang terkait dengan weather)

---

## ❓ Jawaban Pertanyaan

### 1. Kenapa response time berbeda?
- **First Call (Cache Miss)**: Membutuhkan waktu sekitar 2 detik karena harus memanggil API eksternal dan `time.sleep(2)` untuk simulasi API lambat.

- **Second Call (Cache Hit)**: Hanya membutuhkan waktu kurang dari 0.1 detik karena data diambil langsung dari Redis yang berada di memori (in-memory storage).

### 2. Apa keuntungan caching?
- **Mempercepat response time**: Menghindari pemanggilan API lambat secara berulang-ulang
- **Mengurangi beban server API eksternal**: Tidak perlu memanggil API setiap kali request
- **Menghemat bandwidth**: Tidak perlu mentransfer data berulang-ulang dari server
- **Meningkatkan skalabilitas**: Aplikasi bisa menangani lebih banyak request

### 3. Kapan sebaiknya tidak menggunakan cache?
- **Data yang selalu berubah**: Misalnya data real-time seperti harga saham yang berubah setiap detik)
- **Data yang sangat kecil dan cepat diambil**: Misalnya data yang tidak membutuhkan waktu lama untuk diambil)
- **Data yang sensitif**: Misalnya data pribadi yang tidak boleh disimpan di cache terlalu lama)
- **Write-heavy application**: Lebih banyak operasi tulis daripada baca)
