# Frontend Migration Guide - Kelas Mata Kuliah Structure

## Perubahan Struktur Database ke Frontend

### 1. **Mata Kuliah Page** (`mataKuliah.jsx`)
#### Sebelum:
- Fetch dari `/mata-kuliah` (mendapat semua mata kuliah)
- Menampilkan: Kode, Nama MK, Dosen, Kelas, SKS

#### Sesudah:
- Fetch dari `/kelas-mata-kuliah/me` (mendapat mata kuliah yang diampu dosen yang login)
- Menampilkan: Kode MK, Nama MK, Kelas (dengan prodi), Tahun Ajaran, Semester, SKS, Status
- **Benefit**: Dosen hanya melihat mata kuliah yang mereka ampu, dengan info kelas lengkap

---

### 2. **Materi Page** (`materi.jsx`)
#### Sebelum:
- Pilih Kelas dahulu
- Kemudian sistem menampilkan mata kuliah untuk kelas tersebut
- Route: `/materi/kelas/:idKelas`

#### Sesudah:
- Langsung pilih dari daftar Mata Kuliah & Kelas yang diampu
- Fetch dari `/kelas-mata-kuliah/me` dengan filter `status = 'aktif'`
- Route baru: `/materi/kelas-mk/:id_kelas_mk`
- **Benefit**: Lebih cepat, tidak perlu 2 langkah pilihan, langsung ke materi yang relevan

---

### 3. **Presensi Page** (`presensi.jsx`)
#### Sebelum:
- Generate Presensi: Pilih Kelas → Pilih Mata Kuliah
- Request body: `{ id_kelas, kode_mk, pertemuan_ke, tanggal, waktu_mulai, waktu_selesai }`
- Filter: Terpisah untuk Kelas dan Mata Kuliah

#### Sesudah:
- Generate Presensi: Pilih Mata Kuliah & Kelas (1 dropdown)
- Request body: `{ id_kelas_mk, pertemuan_ke, tanggal, waktu_mulai, waktu_selesai }`
- Filter: Gabungan Mata Kuliah & Kelas + Pertemuan
- **Benefit**: UI lebih sederhana, konsisten dengan struktur database baru

---

### 4. **Jadwal Kuliah Page** (`jadwalKuliah.jsx`)
#### Sebelum:
- Data hardcoded/dummy

#### Sesudah:
- Fetch dari `/kelas-mata-kuliah/me` dengan filter `status = 'aktif'`
- Menampilkan: Kode MK, Nama MK, Kelas, Prodi, Tahun Ajaran, Semester, Hari, Jam, Ruangan
- **Note**: Hari dan Ruangan masih placeholder - akan diambil dari `jadwal_kuliah` table nanti
- **Benefit**: Data real dari database sesuai yang dosen ampu

---

### 5. **Routing Changes** (`App.jsx`)
#### Perubahan URL Pattern:

| Before | After | Keterangan |
|--------|-------|------------|
| `/materi/kelas/:idKelas` | `/materi/kelas-mk/:id_kelas_mk` | Detail materi per mata kuliah |
| `/presensi/:kodeMatkul` | `/presensi/:id_kelas_mk` | Detail presensi |
| `/presensi/detail/:kode_mk/...` | `/presensi/detail/:id_kelas_mk/...` | Detail absen mahasiswa |
| `/materi/:kodeMk/minggu/view` | `/materi/:id_kelas_mk/minggu/view` | View minggu materi |
| `/materi/:kodeMatkul/minggu/:minggu` | `/materi/:id_kelas_mk/minggu/:minggu` | Detail per minggu |

---

## Keuntungan Struktur Baru

### 1. **Konsistensi Data**
- Satu mata kuliah bisa diajar di beberapa kelas berbeda
- Dosen yang berbeda bisa mengajar mata kuliah yang sama di kelas berbeda
- Data tidak redundant di database

### 2. **Authorization Lebih Baik**
- Endpoint `/kelas-mata-kuliah/me` otomatis filter berdasarkan dosen yang login
- Tidak perlu manual filter di frontend
- Security lebih terjamin

### 3. **UI Lebih Sederhana**
- Tidak perlu pilih kelas dahulu, langsung ke mata kuliah yang relevan
- Dropdown menampilkan info lengkap: [Kode] Nama MK - Kelas (Prodi) | Tahun Ajaran
- User journey lebih pendek

### 4. **Scalability**
- Mudah menambah tahun ajaran baru tanpa duplikasi mata kuliah
- Mudah assign dosen pengganti
- History data terjaga per periode

---

## TODO - Halaman yang Masih Perlu Update

### 1. **DetailMateri.jsx**
- Perlu update untuk fetch materi berdasarkan `id_kelas_mk` bukan `id_kelas`
- Endpoint: `/materi/kelas-mk/{id_kelas_mk}`

### 2. **MingguMateri.jsx**
- Update route params dari `kodeMatkul` ke `id_kelas_mk`
- Update fetch endpoint sesuai

### 3. **DetailPresensi.jsx**
- Update untuk fetch presensi berdasarkan `id_kelas_mk`
- Endpoint: `/presensi/kelas-mk/{id_kelas_mk}`

### 4. **DetailPresensiAbsen.jsx**
- Update params dari `kode_mk` ke `id_kelas_mk`

---

## API Endpoints Baru yang Tersedia

### Kelas Mata Kuliah
```
GET    /kelas-mata-kuliah/                    # List all (with filters)
GET    /kelas-mata-kuliah/me                  # List for logged-in dosen
GET    /kelas-mata-kuliah/dosen/{id_dosen}    # List by specific dosen
GET    /kelas-mata-kuliah/{id_kelas_mk}       # Get detail
POST   /kelas-mata-kuliah/                    # Create (super_admin only)
PUT    /kelas-mata-kuliah/{id_kelas_mk}       # Update (super_admin only)
DELETE /kelas-mata-kuliah/{id_kelas_mk}       # Delete (super_admin only)
```

### Response Example
```json
{
  "id_kelas_mk": 1,
  "kode_mk": "IF101",
  "id_kelas": 1,
  "id_dosen": 2,
  "tahun_ajaran": "2024/2025",
  "semester_aktif": 1,
  "status": "aktif",
  "nama_mk": "Pemrograman Web",
  "nama_kelas": "TIF-A",
  "nama_dosen": "Dr. Siti Lestari",
  "sks": 3,
  "semester": 3,
  "prodi": "TIF",
  "nip": "198501012010011001",
  "email_dosen": "siti.lestari@univ.ac.id"
}
```

---

## Testing Checklist

- [ ] Login sebagai dosen
- [ ] Halaman Mata Kuliah menampilkan daftar yang benar
- [ ] Halaman Materi bisa pilih mata kuliah dan navigasi ke detail
- [ ] Generate Presensi dengan dropdown baru berhasil
- [ ] Filter presensi bekerja dengan benar
- [ ] Jadwal Kuliah menampilkan data yang sesuai
- [ ] Semua route baru berfungsi dengan benar

---

## Notes
- Pastikan backend sudah running di `http://localhost:8000`
- Pastikan sudah login dengan akun dosen (role: admin)
- Token JWT harus valid dan tersimpan di localStorage
- Untuk data jadwal lengkap (hari, ruangan), perlu update model `jadwal_kuliah` di backend
