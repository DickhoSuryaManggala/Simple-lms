# Simple LMS - Django & Docker Project (Progres 4)

![Django Admin Dashboard](image/Screenshot%202026-04-16%20204855.png)

Proyek **Simple LMS** (Learning Management System) yang dibangun menggunakan Django dan dikemas dengan Docker. Proyek ini mendemonstrasikan desain database yang efisien, optimasi query untuk skala besar, dan integrasi dengan Redis, MongoDB, dan Celery.

---

## 📦 Struktur Proyek

```text
simple-lms/
├── config/                 # Konfigurasi utama Django (settings, urls, wsgi, celery)
│   ├── mongodb.py          # Koneksi dan aggregation queries MongoDB
│   └── celery.py         # Konfigurasi Celery
├── courses/                # App LMS (Models, Admin, Fixtures, API, Tasks)
│   ├── tasks.py           # Celery tasks (email, certificate, update stats, export)
│   └── ...
├── .env.example            # Template variabel lingkungan
├── docker-compose.yml      # Orkestrasi container (Web, DB, Redis, MongoDB, RabbitMQ, Celery, Flower)
├── ARCHITECTURE.md         # Dokumentasi arsitektur proyek
└── ...
```

---

## 🆕 Update Progres 4: Fitur Baru

Pada progres ke-4, kita menambahkan fitur-fitur berikut:

### 1. **Redis Integration**
- **Course List Caching** (5 menit cache)
- **Course Detail Caching** (10 menit cache)
- **Rate Limiting** (60 permintaan/menit per IP)

### 2. **MongoDB Integration**
- **Activity Log Collection**: Log semua aktivitas pengguna (register, login, course viewed, dll.)
- **Learning Analytics Collection**: Statistik course (enrollment count, dll.)
- **Aggregation Queries untuk Reports**

### 3. **Celery Tasks**
- `send_enrollment_email`: Kirim email saat user mendaftar course (async)
- `generate_certificate`: Generate sertifikat (async)
- `update_course_statistics`: Update statistik course (periodic task, setiap jam)
- `export_course_report`: Export laporan course CSV (async)

### 4. **Docker Compose Services**
- `web`: Django app
- `db`: PostgreSQL database
- `redis`: Redis untuk caching dan rate limiting
- `mongodb`: MongoDB untuk activity log dan analytics
- `rabbitmq`: Message broker untuk Celery
- `celery-worker`: Celery worker (menjalankan task async tasks)
- `celery-beat`: Celery Beat (scheduled tasks)
- `flower`: Flower (Celery monitoring UI)

---

## 🎯 Fitur Utama

- **Database Schema**: 
    - **Categories**: Mendukung hirarki kategori (Parent-Child).
    - **Courses & Lessons**: Manajemen konten dengan sistem pengurutan (`ordering`).
    - **Enrollment & Progress**: Tracking pendaftaran siswa dan progres belajar secara real-time.
- **Query Optimization**: 
    - Menggunakan `select_related` untuk efisiensi relasi ForeignKey.
    - Menggunakan `annotate` dengan `Count` dan `Case` untuk perhitungan progres langsung di database (menghindari N+1 problem).
- **Django Admin**: Interface admin yang informatif dengan filter, pencarian, dan inline editing untuk Lesson.
- **REST API**: API lengkap dengan Django Ninja, JWT Authentication, dan Swagger documentation.
- **Redis Caching & Rate Limiting**.
- **MongoDB Activity Log & Analytics**.
- **Celery Async & RabbitMQ** untuk task async dan periodic.
- **Flower monitoring UI** untuk monitoring Celery tasks.

---

## 🚀 Cara Menjalankan Proyek

### 1. Prasyarat
Pastikan Anda sudah menginstal **Docker** dan **Docker Compose**.

### 2. Setup Environment
Salin file `.env.example` menjadi `.env`:
```powershell
Copy-Item .env.example .env
```

### 3. Build dan Jalankan Container
```powershell
docker-compose up -d --build
```

### 4. Inisialisasi Database
Jalankan migrasi:
```powershell
# Migrasi Database
docker-compose exec web python manage.py migrate
```

### 5. Akses Aplikasi
- **API Documentation (Swagger)**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)
- **Flower (Celery Monitoring)**: [http://localhost:5555](http://localhost:5555)
- **RabbitMQ Management UI**: [http://localhost:15672](http://localhost:15672)
  - **Username**: `guest`
  - **Password**: `guest`

---

## 📸 Gallery / Screenshots Progres 4

Berikut adalah screenshot fitur baru di Progres 4:

### 1. Docker Compose Services Running
![Docker Compose](image/Screenshot%202026-06-23%20121039.png)

### 2. API Documentation (Swagger UI)
![API Swagger](image/Screenshot%202026-06-23%20121305.png)

### 3. API Analytics Endpoints
![API Analytics](image/Screenshot%202026-06-23%20121346.png)

### 4. Flower (Celery Monitoring UI)
![Flower](image/Screenshot%202026-06-23%20121710.png)

### 5. Flower Tasks
![Flower Tasks](image/Screenshot%202026-06-23%20121717.png)

### 6. Flower Broker
![Flower Broker](image/Screenshot%202026-06-23%20121726.png)

### 7. RabbitMQ Management UI
![RabbitMQ](image/Screenshot%202026-06-23%20121807.png)

### 8. MongoDB Activity Logs
![MongoDB](image/Screenshot%202026-06-23%20121826.png)

### 9. Redis CLI
![Redis](image/Screenshot%202026-06-23%20121838.png)

### 10. API Test
![API Test](image/Screenshot%202026-06-23%20121849.png)

### 11. API Response
![API Response](image/Screenshot%202026-06-23%20121857.png)

### 12. Terminal Docker Compose
![Docker Compose Terminal](image/Screenshot%202026-06-23%20121904.png)

### 13. MongoDB Compass
![MongoDB Compass](image/Screenshot%202026-06-23%20121912.png)

### 14. Django Admin
![Django Admin](image/Screenshot%202026-06-23%20122754.png)

### 15. Final Check
![Final Check](image/Screenshot%202026-06-23%20122906.png)

---

## 📊 Dokumentasi Arsitektur
Untuk penjelasan lebih lanjut tentang arsitektur dan cara kerja fitur baru di Progres 4, lihat file [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🛠️ Variabel Lingkungan (.env)

| Variabel | Deskripsi | Default |
|----------|-----------|---------|
| `DB_NAME` | Nama database PostgreSQL | `lms_db` |
| `DB_USER` | Username database | `lms_user` |
| `DB_PASSWORD` | Password database | `lms_password` |
| `DEBUG` | Mode debug Django | `True` |
| `SECRET_KEY` | Django Secret Key | (Gunakan key unik) |
| `REDIS_HOST` | Host Redis | `redis` |
| `REDIS_PORT` | Port Redis | `6379` |
| `MONGO_HOST` | Host MongoDB | `mongodb` |
| `MONGO_PORT` | Port MongoDB | `27017` |
| `RABBITMQ_HOST` | Host RabbitMQ | `rabbitmq` |
| `RABBITMQ_PORT` | Port RabbitMQ | `5672` |

---


**Author:**
- Dickho Surya Manggala
- NIM: A11.2023.15323
