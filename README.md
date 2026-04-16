# Simple LMS - Django & Docker Project

![Django Admin Dashboard](image/Screenshot%202026-04-16%20204855.png)

Proyek **Simple LMS** (Learning Management System) yang dibangun menggunakan Django dan dikemas dengan Docker. Proyek ini mendemonstrasikan desain database yang efisien dan optimasi query untuk skala besar.

## 📦 Struktur Proyek

```text
simple-lms/
├── config/                 # Konfigurasi utama Django (settings, urls, wsgi)
├── courses/                # App LMS (Models, Admin, Fixtures)
│   ├── fixtures/           # Data awal untuk testing
│   ├── migrations/         # Database migrations
│   ├── admin.py            # Kustomisasi Django Admin
│   └── models.py           # Definisi skema database
├── .env.example            # Template variabel lingkungan
├── Dockerfile              # Konfigurasi container Python
├── docker-compose.yml      # Orkestrasi container (Web & DB)
├── manage.py               # Django management script
├── query_demo.py           # Script demonstrasi optimasi query
├── requirements.txt        # Daftar dependensi Python
└── README.md               # Dokumentasi proyek
```

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

## 🚀 Cara Menjalankan Proyek

### 1. Prasyarat
Pastikan Anda sudah menginstal **Docker** dan **Docker Compose**.

### 2. Setup Environment
Salin file `.env.example` menjadi `.env`:
```bash
cp .env.example .env
```

### 3. Build dan Jalankan Container
```bash
docker-compose up -d --build
```

### 4. Inisialisasi Database & Data Awal
Jalankan migrasi dan muat data contoh:
```bash
# Migrasi Database
docker-compose run --rm web python manage.py migrate

# Memuat Data Awal (Users, Courses, Lessons)
docker-compose run --rm web python manage.py loaddata initial_data
```

### 5. Akses Aplikasi
- **Django Admin**: [http://localhost:8000/admin/](http://localhost:8000/admin/)
    - **Username**: `admin`
    - **Password**: `SisiLMS2026!`
- **API Documentation (Swagger)**: [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

## 📊 Demonstrasi Optimasi Query

Kami menyediakan script khusus untuk menunjukkan perbedaan performa antara query standar vs query yang dioptimalkan. Jalankan perintah berikut:

```bash
docker-compose run --rm web python query_demo.py
```

**Hasil yang diharapkan:**
- **N+1 Problem**: Menampilkan bagaimana satu request bisa memicu banyak query ke database.
- **Optimized**: Menampilkan bagaimana `select_related` dan `annotate` mengurangi jumlah query secara drastis.

## �️ Gallery / Screenshots

Berikut adalah beberapa tampilan dari aplikasi Simple LMS:

### 1. Django Admin Login
![Admin Login](image/Screenshot%202026-04-12%20235603.png)

### 2. Dashboard Admin & Management
![Admin Dashboard](image/Screenshot%202026-04-16%20204855.png)

### 3. Konfigurasi Database & Models
![Database Setup](image/Screenshot%202026-04-16%20204643.png)

### 4. Query Optimization Demo
![Query Demo Result](image/Screenshot%202026-04-13%20000318.png)

### 5. API Authorization (Swagger)
![API Authorization](image/Screenshot%202026-04-16%20212219.png)

## 🛠️ Variabel Lingkungan (.env)

| Variabel | Deskripsi | Default |
|----------|-----------|---------|
| `DB_NAME` | Nama database PostgreSQL | `lms_db` |
| `DB_USER` | Username database | `lms_user` |
| `DB_PASSWORD` | Password database | `lms_password` |
| `DEBUG` | Mode debug Django | `True` |
| `SECRET_KEY` | Django Secret Key | (Gunakan key unik) |

---
*Dibuat untuk keperluan pembelajaran containerization dan optimasi Django.*

**Author:**
- Dickho Surya Manggala
- NIM: A11.2023.15323
