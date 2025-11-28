# Test Materi Sharing Feature

## Test Scenario: Multiple Dosen Access Same Materials

### Setup
1. Database memiliki:
   - BD001 (Basis Data) assigned ke kelas TIF-2023-A (id_kelas=1)
   - Ahmad.dosen (id_dosen=1) mengajar BD001 di kelas tersebut
   - Siti.dosen (id_dosen=2) juga mengajar BD001 di kelas yang sama
   
2. Materi existing untuk BD001 + kelas 1:
   - Minggu 1: Pengenalan Basis Data (uploaded_by: ahmad.dosen)
   - Minggu 2: Normalisasi Database (uploaded_by: ahmad.dosen)
   - Minggu 3: SQL Lanjutan (uploaded_by: ahmad.dosen)

### Test Cases

#### ✅ TC-01: Get Materi List (Shared Access)
**Endpoint:** GET /materi?kode_mk=BD001&id_kelas=1
**Expected:** Return all 3 materi regardless of uploaded_by
**Status:** PASSED
**Result:** Returns 3 materials with uploaded_by field

#### ✅ TC-02: Get Kelas Mata Kuliah Detail
**Endpoint:** GET /kelas-mata-kuliah/1
**Expected:** Return kode_mk and id_kelas fields
**Status:** PASSED
**Result:** Returns {"kode_mk": "BD001", "id_kelas": 1, ...}

#### ✅ TC-03: Get Materi by Week
**Endpoint:** GET /materi?kode_mk=BD001&id_kelas=1&minggu=1
**Expected:** Return only minggu 1 materials
**Status:** PASSED
**Result:** Returns 1 material for week 1

#### 🔄 TC-04: Frontend - View Materi List
**Page:** /materi → Click "Basis Data"
**Expected:** Navigate to /materi/kelas-mk/1 and display 16-week grid with counts
**Status:** TO TEST
**Steps:**
1. Login as ahmad.dosen
2. Navigate to Materi page
3. Click on "Basis Data" card
4. Verify 16-week grid appears
5. Verify week 1, 2, 3 show "1 materi tersedia" or more

#### 🔄 TC-05: Frontend - View Week Details
**Page:** /materi/1/minggu/1
**Expected:** Display materials for week 1
**Status:** TO TEST
**Steps:**
1. From detail materi page, click "Minggu 1"
2. Verify materials list appears
3. Verify "Pengenalan Basis Data" appears
4. Verify uploaded_by shows ahmad.dosen name

#### 🔄 TC-06: Upload New Material (Ahmad)
**Page:** /materi/1/minggu/4
**Expected:** Ahmad can upload material for week 4
**Status:** TO TEST
**Steps:**
1. Login as ahmad.dosen
2. Navigate to Minggu 4
3. Click "Tambah Materi" button
4. Fill form: judul, deskripsi, upload PDF
5. Submit
6. Verify material appears in list
7. Verify uploaded_by = 1 (ahmad)

#### 🔄 TC-07: Shared Material Access (Siti)
**Page:** /materi → "Basis Data" → Minggu 4
**Expected:** Siti can see Ahmad's material
**Status:** TO TEST (after fixing unique_offering constraint)
**Steps:**
1. Assign siti.dosen to BD001 + kelas 1 (same tahun_ajaran)
2. Login as siti.dosen
3. Navigate to Materi → Basis Data → Minggu 4
4. Verify Ahmad's material from TC-06 appears
5. Verify all 4 materials (week 1,2,3,4) visible

#### 🔄 TC-08: Upload by Second Dosen (Siti)
**Page:** /materi/1/minggu/4
**Expected:** Siti can add additional material to same week
**Status:** TO TEST
**Steps:**
1. As siti.dosen, navigate to Minggu 4
2. Click "Tambah Materi" (should allow multiple materials per week)
3. Fill form with different material
4. Submit
5. Verify both materials (Ahmad's and Siti's) appear
6. Verify uploaded_by shows correct dosen for each

#### 🔄 TC-09: Edit Material Ownership
**Page:** /materi/1/minggu/1
**Expected:** Only uploader can edit their own material
**Status:** TO TEST (if authorization implemented)
**Steps:**
1. As siti.dosen, try to edit Ahmad's material
2. Verify edit is blocked OR successful (depending on business rule)

### Known Issues
1. **Constraint Issue:** `unique_offering` prevents multiple dosen in same kelas+mk+tahun_ajaran
   - **Workaround:** Use different tahun_ajaran for testing
   - **Fix Required:** Migration to change constraint to include id_dosen

2. **Password Issue:** Cannot login with test accounts via curl
   - **Workaround:** Test via browser UI
   - **Status:** Non-blocking for UI testing

### Next Steps
1. ✅ Complete TC-04 to TC-09 via browser testing
2. Fix unique_offering constraint for production
3. Add authorization rules for material editing
4. Add dosen name display in material cards (uploaded_by)
5. Consider adding "Edit" permission check based on uploaded_by

### API Endpoints Changed
- GET /materi?kode_mk={code}&id_kelas={id}&minggu={week} ✅
- POST /materi (body: kode_mk, id_kelas, minggu, judul, deskripsi, uploaded_by, file_pdf) ✅
- PUT /materi/{id} (body: judul, deskripsi, minggu, file_pdf) ✅
- DELETE /materi/{id} ✅

### Database Changes
- materi.id_kelas_mk → REMOVED
- materi.kode_mk → ADDED (FK to mata_kuliah)
- materi.id_kelas → ADDED (FK to kelas)
- materi.uploaded_by → ADDED (FK to dosen, nullable)
