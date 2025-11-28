# MIGRATION GUIDE - Database Normalization dengan Tabel Dosen

## Perubahan Database

### Struktur Baru (3 Tabel Terpisah)

Database sekarang menggunakan struktur fully normalized dengan 3 tabel utama:

1. **users** - Authentication only
   - id_user, username, email, password, role, is_active

2. **mahasiswa** - Student profiles
   - id_mahasiswa, user_id (FK), nim, nama, tempat_lahir, tanggal_lahir, jenis_kelamin, agama, alamat, no_hp, id_kelas (FK)

3. **dosen** - Teacher/Lecturer profiles
   - id_dosen, user_id (FK), nip, nama_dosen, email_dosen, tempat_lahir, tanggal_lahir, jenis_kelamin, agama, alamat, no_hp

4. **mata_kuliah** - Courses
   - kode_mk (PK), nama_mk, **id_dosen (FK to dosen)**, sks, semester, id_kelas (FK)

### Foreign Keys
- mahasiswa.user_id → users.id_user (CASCADE)
- mahasiswa.id_kelas → kelas.id_kelas (SET NULL)
- dosen.user_id → users.id_user (CASCADE)
- **mata_kuliah.id_dosen → dosen.id_dosen (SET NULL)**
- jadwal_kuliah.id_dosen → dosen.id_dosen (CASCADE)

## Langkah Implementasi

### 1. Backup Database Lama
```bash
mysqldump -u root -p e-learn > backup_e-learn_before_dosen.sql
```

### 2. Import Database Baru
```bash
mysql -u root -p < e-learn_with_dosen.sql
```

atau via phpMyAdmin:
1. Pilih database `e-learn`
2. Klik tab "Import"
3. Pilih file `e-learn_with_dosen.sql`
4. Klik "Go"

### 3. Verifikasi Database
```sql
-- Cek jumlah data
SELECT 'users' AS tabel, COUNT(*) AS jumlah FROM users
UNION ALL
SELECT 'dosen', COUNT(*) FROM dosen
UNION ALL
SELECT 'mahasiswa', COUNT(*) FROM mahasiswa
UNION ALL
SELECT 'mata_kuliah', COUNT(*) FROM mata_kuliah;

-- Test JOIN query
SELECT 
  u.id_user, u.username, u.role,
  m.nim, m.nama AS nama_mahasiswa,
  d.nip, d.nama_dosen
FROM users u
LEFT JOIN mahasiswa m ON u.id_user = m.user_id
LEFT JOIN dosen d ON u.id_user = d.user_id
ORDER BY u.id_user;

-- Test mata_kuliah with dosen
SELECT 
  mk.kode_mk, mk.nama_mk,
  d.nama_dosen,
  k.nama_kelas
FROM mata_kuliah mk
LEFT JOIN dosen d ON mk.id_dosen = d.id_dosen
LEFT JOIN kelas k ON mk.id_kelas = k.id_kelas;
```

### 4. Test Backend

#### Start Backend
```bash
cd Backend_api-main
.\venv\Scripts\Activate  # Activate venv
uvicorn main:app --reload
```

#### Test Endpoints

**1. Test GET /users/ - Should return all users dengan profile**
```bash
# Via browser
http://localhost:8000/users/

# Via PowerShell
Invoke-RestMethod -Uri "http://localhost:8000/users/" -Method GET | ConvertTo-Json -Depth 5
```

Expected Response:
- Super admin: hanya data user (no profile)
- Admin/Dosen: data user + dosen profile (nip, nama_dosen, dll)
- Mahasiswa: data user + mahasiswa profile (nim, nama, id_kelas, dll)

**2. Test POST /users/dosen - Create new dosen**
```bash
$body = @{
  username = "dosen_baru"
  email = "dosen.baru@elearn.com"
  password = "password123"
  nip = "199001012020121001"
  nama_dosen = "Dr. Budi Santoso, M.Kom"
  email_dosen = "budi.santoso@university.ac.id"
  tempat_lahir = "Jakarta"
  tanggal_lahir = "1990-01-01"
  jenis_kelamin = "L"
  agama = "Islam"
  alamat = "Jl. Pendidikan No. 50"
  no_hp = "081234567890"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/users/dosen" -Method POST -Body $body -ContentType "application/json"
```

**3. Test GET /dosen/ - Get all dosen**
```bash
Invoke-RestMethod -Uri "http://localhost:8000/dosen/" -Method GET
```

**4. Test GET /mata-kuliah/ - Should show nama_dosen from dosen table**
```bash
Invoke-RestMethod -Uri "http://localhost:8000/mata-kuliah/" -Method GET
```

**5. Test Login dengan dosen account**
```bash
$body = @{
  username = "ahmad.dosen"
  password = "password123"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/auth/login" -Method POST -Body $body -ContentType "application/json"
```

Expected Response:
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "user": {
    "id_user": 2,
    "username": "ahmad.dosen",
    "role": "admin",
    "email": "ahmad.wijaya@elearn.com",
    "nama": "Dr. Ahmad Wijaya, M.Kom",
    "nip": "197801011999031001"
  }
}
```

**6. Test Dashboard - Should count from dosen table**
```bash
Invoke-RestMethod -Uri "http://localhost:8000/dashboard/superadmin/summary" -Method GET
```

## Perubahan Backend Code

### Files Created
1. `app/models/dosen_model.py` - Dosen model dengan user_id FK
2. `app/schemas/dosen_schema.py` - Dosen schemas (UserDosenCreate, UserDosenResponse, etc)
3. `app/routes/dosen_route.py` - Dosen endpoints (read-only)

### Files Updated
1. `app/models/mata_kuliah_model.py`
   - Changed: `dosen_pengampu VARCHAR(150)` → `id_dosen INT FK`
   - Added: FK relationship to dosen table

2. `app/routes/user_route.py`
   - Added: POST /users/dosen (create dosen + user)
   - Added: PUT /dosen/{user_id} (update dosen profile)
   - Updated: GET /users/ includes dosen profile for admin users
   - Updated: GET /users/{id} includes dosen profile

3. `app/routes/mata_kuliah_route.py`
   - All queries now LEFT JOIN dosen table
   - Returns `d.nama_dosen` instead of `mk.dosen_pengampu`

4. `app/routes/auth_route.py`
   - Login now queries dosen table for nama when role='admin'

5. `app/routes/dashboard_route.py`
   - total_admin count from dosen table instead of users WHERE role

6. `main.py`
   - Added: dosen_route import and registration

## API Endpoints Baru

### Dosen Endpoints
- `GET /dosen/` - Get all dosen dengan user data
- `GET /dosen/{id_dosen}` - Get dosen by id
- `POST /users/dosen` - Create dosen (user + profile)
- `PUT /users/dosen/{user_id}` - Update dosen profile
- `DELETE /users/{user_id}` - Delete user (cascade to dosen)

### Updated Endpoints
- `GET /users/` - Now includes dosen profile for admin role
- `GET /mata-kuliah/` - Now accepts `?id_dosen=X` filter
- `GET /mata-kuliah/{kode}` - Returns id_dosen and nama_dosen
- `POST /auth/login` - Returns nama and nip for dosen users

## Breaking Changes

⚠️ **Perubahan yang Mempengaruhi Frontend:**

1. **Mata Kuliah Response**
   - Old: `{ dosen_pengampu: "Dr. Ahmad" }`
   - New: `{ id_dosen: 1, nama_dosen: "Dr. Ahmad Wijaya, M.Kom" }`

2. **User Response untuk Admin/Dosen**
   - Old: `{ role: "admin", nip: "xxx", nama: "Dr. Ahmad" }`
   - New: `{ role: "admin", id_dosen: 1, nip: "xxx", nama_dosen: "Dr. Ahmad Wijaya, M.Kom" }`

3. **Login Response untuk Dosen**
   - Returns `nama` (from dosen.nama_dosen) and `nip`

## Sample Data

Database baru sudah include sample data:
- 1 super_admin user (username: `superadmin`)
- 2 dosen users dengan profile lengkap
  - ahmad.dosen (Dr. Ahmad Wijaya, M.Kom)
  - siti.dosen (Siti Nurhaliza, S.Kom, M.T)
- 5 mahasiswa dengan profile lengkap
- 3 mata kuliah dengan id_dosen FK yang valid
- 3 jadwal kuliah dengan id_dosen FK

## Troubleshooting

### Error: Unknown column 'dosen_pengampu'
- Pasti backend belum restart setelah update code
- Solution: Stop dan start ulang `uvicorn main:app --reload`

### Error: Foreign key constraint fails pada mata_kuliah
- id_dosen yang dimasukkan tidak exist di tabel dosen
- Solution: Cek `SELECT * FROM dosen` untuk melihat id_dosen yang valid

### Error: Cannot add or update a child row
- Saat create mata_kuliah dengan id_dosen yang tidak valid
- Solution: Set id_dosen=NULL atau gunakan id_dosen yang exist

## Migration dari Struktur Lama

Jika punya data production yang perlu dimigrate:

```sql
-- 1. Backup dulu
CREATE TABLE users_backup AS SELECT * FROM users;
CREATE TABLE mata_kuliah_backup AS SELECT * FROM mata_kuliah;

-- 2. Create dosen dari users WHERE role='admin' AND nip IS NOT NULL
INSERT INTO dosen (user_id, nip, nama_dosen, email_dosen)
SELECT 
  id_user,
  nip,
  nama,
  email
FROM users
WHERE role = 'admin' AND nip IS NOT NULL;

-- 3. Update mata_kuliah.id_dosen dari nama dosen (manual mapping needed)
-- Contoh jika tahu mapping-nya:
UPDATE mata_kuliah mk
SET mk.id_dosen = (
  SELECT d.id_dosen FROM dosen d
  WHERE d.nama_dosen LIKE CONCAT('%', mk.dosen_pengampu, '%')
  LIMIT 1
)
WHERE mk.dosen_pengampu IS NOT NULL;
```

## Next Steps

1. ✅ Database imported dengan 3 tabel terpisah
2. ✅ Backend code updated untuk handle dosen table
3. ✅ All endpoints tested dan working
4. 🔄 Frontend perlu update untuk:
   - Gunakan id_dosen saat create/update mata_kuliah
   - Tampilkan nama_dosen dari response
   - Handle dosen profile di user management
