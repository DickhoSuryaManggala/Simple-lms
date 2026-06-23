import time
from weather_api import get_weather

# First call - should be slow (2 seconds)
print("=== First Call (Cache Miss) ===")
start = time.time()
result1 = get_weather("Jakarta")
time1 = time.time() - start
print(f"First call: {time1:.2f}s")

print("\n" + "="*50 + "\n")

# Second call - should be fast (< 0.1 second)
print("=== Second Call (Cache Hit) ===")
start = time.time()
result2 = get_weather("Jakarta")
time2 = time.time() - start
print(f"Second call (cached): {time2:.2f}s")

print("\n" + "="*50 + "\n")

print("✅ Test selesai!")
print(f"Perbedaan waktu: {time1 - time2:.2f}s lebih cepat!")
