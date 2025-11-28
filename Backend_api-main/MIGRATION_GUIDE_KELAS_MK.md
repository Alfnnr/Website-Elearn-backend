# MIGRATION GUIDE - Kelas Mata Kuliah Junction Table

## 📋 Overview

Migration ini mengubah struktur database dari:
- **Before**: 1 mata kuliah = 1 dosen = 1 kelas (one-to-one)
- **After**: 1 mata kuliah bisa diajarkan oleh banyak dosen di banyak kelas (many-to-many)

## 🎯 Tujuan Migration

### Problem Statement
Struktur lama **TIDAK MENDUKUNG**:
- ❌ 1 dosen mengampu mata kuliah yang sama di multiple kelas
- ❌ 1 mata kuliah dibuka di multiple kelas dengan dosen berbeda
- ❌ Isolasi data materi/presensi antar dosen dan kelas
- ❌ Historical tracking per semester/tahun ajaran

### Solution
Menambahkan **junction table `kelas_mata_kuliah`** yang menyimpan:
- Kombinasi: mata_kuliah + kelas + dosen + periode
- Referensi untuk jadwal, materi, dan presensi

## 📊 Perubahan Struktur Database

### Tabel Baru

#### `kelas_mata_kuliah` (Junction Table)
```sql
CREATE TABLE `kelas_mata_kuliah` (
  `id_kelas_mk` INT AUTO_INCREMENT PRIMARY KEY,
  `kode_mk` VARCHAR(20) NOT NULL,           -- FK to mata_kuliah
  `id_kelas` INT NOT NULL,                  -- FK to kelas
  `id_dosen` INT NOT NULL,                  -- FK to dosen
  `tahun_ajaran` VARCHAR(20) NOT NULL,      -- "2024/2025"
  `semester_aktif` ENUM('Ganjil', 'Genap'), 
  `status` ENUM('Aktif', 'Selesai', 'Batal'),
  `created_at` TIMESTAMP,
  `updated_at` TIMESTAMP,
  UNIQUE KEY (`kode_mk`, `id_kelas`, `tahun_ajaran`, `semester_aktif`)
);
```

**Contoh Data:**
| id_kelas_mk | kode_mk | id_kelas | id_dosen | tahun_ajaran | semester_aktif | status |
|-------------|---------|----------|----------|--------------|----------------|--------|
| 1           | IF101   | 1        | 1        | 2024/2025    | Ganjil         | Aktif  |
| 2           | IF101   | 2        | 1        | 2024/2025    | Ganjil         | Aktif  |
| 3           | IF101   | 3        | 2        | 2024/2025    | Ganjil         | Aktif  |

Artinya:
- IF101 (Pemrograman Web) dibuka di 3 kelas
- Dosen 1 mengampu kelas 1 & 2
- Dosen 2 mengampu kelas 3

### Tabel yang Dimodifikasi

#### 1. `mata_kuliah` - Menjadi Course Catalog
**REMOVED:**
- ❌ `id_dosen` (pindah ke kelas_mata_kuliah)
- ❌ `id_kelas` (pindah ke kelas_mata_kuliah)

**ADDED:**
- ✅ `deskripsi` TEXT (course description)

**Before:**
```sql
mata_kuliah (kode_mk, nama_mk, id_dosen, id_kelas, sks, semester)
```

**After:**
```sql
mata_kuliah (kode_mk, nama_mk, sks, semester, deskripsi)
```

#### 2. `jadwal_kuliah` - Reference ke Junction
**REMOVED:**
- ❌ `kode_mk`
- ❌ `id_dosen`
- ❌ `id_kelas`
- ❌ `jam` (VARCHAR)

**ADDED:**
- ✅ `id_kelas_mk` INT (FK to kelas_mata_kuliah)
- ✅ `jam_mulai` TIME
- ✅ `jam_selesai` TIME

**Before:**
```sql
jadwal_kuliah (id_jadwal, kode_mk, id_dosen, id_kelas, hari, jam, ruangan)
```

**After:**
```sql
jadwal_kuliah (id_jadwal, id_kelas_mk, hari, jam_mulai, jam_selesai, ruangan)
```

#### 3. `materi` - Reference ke Junction
**REMOVED:**
- ❌ `kode_mk`

**ADDED:**
- ✅ `id_kelas_mk` INT (FK to kelas_mata_kuliah)

**Before:**
```sql
materi (id_materi, kode_mk, minggu, judul, deskripsi, file_pdf)
```

**After:**
```sql
materi (id_materi, id_kelas_mk, minggu, judul, deskripsi, file_pdf)
```

#### 4. `presensi` - Reference ke Junction
**REMOVED:**
- ❌ `kode_mk`

**ADDED:**
- ✅ `id_kelas_mk` INT (FK to kelas_mata_kuliah)

**Before:**
```sql
presensi (id_presensi, id_mahasiswa, kode_mk, tanggal, pertemuan_ke, status)
UNIQUE (id_mahasiswa, kode_mk, tanggal, pertemuan_ke)
```

**After:**
```sql
presensi (id_presensi, id_mahasiswa, id_kelas_mk, tanggal, pertemuan_ke, status)
UNIQUE (id_mahasiswa, id_kelas_mk, tanggal, pertemuan_ke)
```

## 🚀 Cara Menjalankan Migration

### Prerequisites
1. ✅ Database `e-learn` sudah running
2. ✅ Ada data di `mata_kuliah`, `dosen`, `kelas`
3. ✅ Backup database (WAJIB!)

### Langkah 1: Backup Database
```bash
# Via Command Line
mysqldump -u root -p e-learn > backup_before_kelas_mk_$(date +%Y%m%d_%H%M%S).sql

# Atau via phpMyAdmin: Export → SQL
```

### Langkah 2: Jalankan Migration
```bash
# Via Command Line
mysql -u root -p e-learn < migration_kelas_mata_kuliah.sql

# Atau via phpMyAdmin:
# 1. Pilih database e-learn
# 2. Klik tab "SQL"
# 3. Copy-paste isi file migration_kelas_mata_kuliah.sql
# 4. Klik "Go"
```

### Langkah 3: Verifikasi
Script akan otomatis menampilkan hasil verifikasi:
```
========== VERIFICATION RESULTS ==========
kelas_mata_kuliah: 3 records
jadwal_kuliah: Total=3, With_FK=3, Missing_FK=0
materi: Total=5, With_FK=5, Missing_FK=0
presensi: Total=10, With_FK=10, Missing_FK=0
```

**Jika ada Missing_FK > 0** → Ada data yang tidak berhasil dimigrate (perlu dicek manual)

### Langkah 4 (Opsional): Rollback jika Gagal
```bash
mysql -u root -p e-learn < rollback_migration.sql
```

## 📝 Apa yang Terjadi Saat Migration?

### Automatic Data Migration
1. **Backup otomatis** semua tabel yang dimodifikasi
2. **Create junction table** `kelas_mata_kuliah`
3. **Migrate existing data** dari `mata_kuliah` → `kelas_mata_kuliah`
4. **Update references** di jadwal, materi, presensi → point ke `id_kelas_mk`
5. **Drop old columns** (`kode_mk`, `id_dosen`, `id_kelas` dari dependent tables)
6. **Add new constraints** dan foreign keys

### Data Mapping Logic

#### Jadwal Kuliah
```sql
-- Before
jadwal: kode_mk=IF101, id_dosen=1, id_kelas=1

-- After (find matching id_kelas_mk)
jadwal: id_kelas_mk=5 (where kelas_mk has IF101, dosen=1, kelas=1)
```

#### Materi
```sql
-- Before
materi: kode_mk=IF101

-- After (use first matching kelas_mk)
materi: id_kelas_mk=5
```

#### Presensi
```sql
-- Before
presensi: id_mahasiswa=10, kode_mk=IF101

-- After (match via mahasiswa's kelas)
-- Find kelas_mk where mk=IF101 AND kelas=(mahasiswa's kelas)
presensi: id_mahasiswa=10, id_kelas_mk=5
```

## ⚠️ Potential Issues & Solutions

### Issue 1: Duplicate mata_kuliah per kelas
**Symptom:** 
```
ERROR 1062: Duplicate entry 'IF101-1-2024/2025-Ganjil'
```

**Cause:** Sudah ada kombinasi kode_mk + id_kelas + tahun_ajaran + semester

**Solution:**
- Check data: `SELECT * FROM mata_kuliah WHERE id_kelas = 1`
- Hapus duplikat atau ubah semester/tahun_ajaran

### Issue 2: Missing FK reference
**Symptom:**
```
Missing_FK > 0 in verification
```

**Cause:** Data lama tidak punya id_dosen atau id_kelas

**Solution:**
```sql
-- Check missing data
SELECT * FROM jadwal_kuliah WHERE id_kelas_mk IS NULL;
SELECT * FROM materi WHERE id_kelas_mk IS NULL;
SELECT * FROM presensi WHERE id_kelas_mk IS NULL;

-- Manual fix: set default
UPDATE jadwal_kuliah 
SET id_kelas_mk = 1 
WHERE id_kelas_mk IS NULL;
```

### Issue 3: Rollback needed
**Symptom:** Migration gagal di tengah jalan

**Solution:**
1. Jalankan `rollback_migration.sql`
2. Fix issue yang menyebabkan error
3. Jalankan migration lagi

## 🔍 Query Examples - New Structure

### Get semua kelas yang dosen ampu
```sql
SELECT 
  kmk.id_kelas_mk,
  mk.nama_mk,
  k.nama_kelas,
  kmk.tahun_ajaran,
  kmk.semester_aktif
FROM kelas_mata_kuliah kmk
JOIN mata_kuliah mk ON kmk.kode_mk = mk.kode_mk
JOIN kelas k ON kmk.id_kelas = k.id_kelas
WHERE kmk.id_dosen = <logged_dosen_id>
  AND kmk.status = 'Aktif';
```

### Get materi untuk kelas tertentu
```sql
SELECT m.*
FROM materi m
WHERE m.id_kelas_mk = <selected_id_kelas_mk>
ORDER BY m.minggu;
```

### Get presensi dengan filter dosen
```sql
SELECT 
  p.*,
  mhs.nama,
  mk.nama_mk,
  k.nama_kelas
FROM presensi p
JOIN mahasiswa mhs ON p.id_mahasiswa = mhs.id_mahasiswa
JOIN kelas_mata_kuliah kmk ON p.id_kelas_mk = kmk.id_kelas_mk
JOIN mata_kuliah mk ON kmk.kode_mk = mk.kode_mk
JOIN kelas k ON kmk.id_kelas = k.id_kelas
WHERE kmk.id_dosen = <logged_dosen_id>
  AND p.tanggal = '2024-11-27';
```

### Authorization check
```sql
-- Check if dosen can access materi
SELECT COUNT(*) 
FROM materi m
JOIN kelas_mata_kuliah kmk ON m.id_kelas_mk = kmk.id_kelas_mk
WHERE m.id_materi = <requested_materi_id>
  AND kmk.id_dosen = <logged_dosen_id>;
-- Return > 0 = allowed, 0 = forbidden
```

## 📦 Files in This Migration

1. **migration_kelas_mata_kuliah.sql** - Main migration script
2. **rollback_migration.sql** - Restore to original structure
3. **MIGRATION_GUIDE_KELAS_MK.md** - This documentation

## ✅ Post-Migration Checklist

### Database
- [ ] All verification queries return 0 Missing_FK
- [ ] Sample data looks correct
- [ ] Backup tables exist (mata_kuliah_backup, etc)

### Backend (Next Steps)
- [ ] Update models: KelasMatKuliah model
- [ ] Update routes: Add id_kelas_mk filters
- [ ] Update materi routes: Create/read with id_kelas_mk
- [ ] Update presensi routes: Filter by id_kelas_mk
- [ ] Update jadwal routes: Use id_kelas_mk
- [ ] Add authorization middleware (check dosen access)

### Frontend (Next Steps)
- [ ] Update materi page: Dropdown pilih kelas_mk
- [ ] Update presensi page: Filter by kelas_mk
- [ ] Update jadwal page: Show kelas_mk info
- [ ] Update mata kuliah page: Show list of kelas offerings

## 🎓 Best Practices After Migration

### 1. Always Filter by Dosen
```python
# Backend example
@router.get("/materi/")
def get_materi(current_user: dict = Depends(get_current_user)):
    dosen_id = current_user.get("id_dosen")
    
    query = """
        SELECT m.* FROM materi m
        JOIN kelas_mata_kuliah kmk ON m.id_kelas_mk = kmk.id_kelas_mk
        WHERE kmk.id_dosen = :dosen_id
    """
    return db.execute(query, {"dosen_id": dosen_id})
```

### 2. Use Kelas MK Dropdown
```javascript
// Frontend example
const [kelasMKList, setKelasMKList] = useState([]);

// Load kelas that dosen teaches
const fetchKelasMK = async () => {
  const data = await apiGet('/kelas-mata-kuliah/dosen/me');
  setKelasMKList(data);
};

// Form dropdown
<select value={selectedKelasMK}>
  {kelasMKList.map(kmk => (
    <option value={kmk.id_kelas_mk}>
      {kmk.nama_mk} - {kmk.nama_kelas}
    </option>
  ))}
</select>
```

### 3. Historical Data
```sql
-- Keep old semester data
UPDATE kelas_mata_kuliah 
SET status = 'Selesai'
WHERE semester_aktif = 'Ganjil' 
  AND tahun_ajaran = '2023/2024';

-- Create new semester
INSERT INTO kelas_mata_kuliah 
(kode_mk, id_kelas, id_dosen, tahun_ajaran, semester_aktif)
VALUES ('IF101', 1, 1, '2024/2025', 'Genap');
```

## 🆘 Support & Troubleshooting

Jika ada masalah:
1. Check verification output
2. Check `*_backup` tables
3. Run rollback script
4. Contact database admin

---

**Migration Version:** 1.0  
**Created:** 2024-11-27  
**Author:** Database Migration Team
