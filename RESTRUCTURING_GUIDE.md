# DATABASE RESTRUCTURING GUIDE - OPTION 1
## Users Table Contains All User Data (No Separate Mahasiswa Table)

---

## 📋 OVERVIEW

This guide helps you migrate from a **separated table structure** (users + mahasiswa) to a **consolidated structure** where the `users` table contains ALL user data including student information.

### What Changed?
- ❌ **REMOVED**: `mahasiswa` table
- ✅ **ENHANCED**: `users` table now has all mahasiswa fields
- ✅ **SIMPLIFIED**: Single source of truth for all users
- ✅ **UPDATED**: Backend models, routes, and schemas
- ✅ **UPDATED**: Frontend to handle new fields

---

## 🗄️ DATABASE CHANGES

### Old Structure:
```
users: id_user, nama, username, email, password, role, nip, nim, kelas
mahasiswa: id_mahasiswa, nim, nama_mahasiswa, id_kelas, email
```

### New Structure:
```
users: 
  - id_user, nama, username, email, password, role
  - nip (for admin/super_admin)
  - nim, tempat_lahir, tanggal_lahir, jenis_kelamin, agama, 
    alamat, no_hp, kelas (for mahasiswa)
```

---

## 🚀 STEP-BY-STEP IMPLEMENTATION

### STEP 1: Backup Current Database
```sql
-- In phpMyAdmin, export your current database first!
-- File > Export > Quick Export > Go
```

### STEP 2: Import New Database Structure
1. Open phpMyAdmin
2. Select `e-learn` database
3. Click "SQL" tab
4. Open the file: `Backend_api-main/e-learn_restructured.sql`
5. Copy ALL content and paste into SQL editor
6. Click "Go" to execute

**✅ This will:**
- Drop old tables (including mahasiswa)
- Create new users table with all fields
- Create other tables with proper structure
- Insert sample data
- Create indexes for performance

### STEP 3: Verify Database
Run this query to check:
```sql
-- Check users table structure
DESCRIBE users;

-- Check sample data
SELECT id_user, nama, role, nim, nip, kelas 
FROM users 
ORDER BY role, nama;

-- Verify mahasiswa table is removed
SHOW TABLES;  -- Should NOT show 'mahasiswa'
```

---

## 💻 BACKEND UPDATES (Already Done)

### Files Modified:

#### 1. `app/models/user_model.py`
- Added `Date` import from sqlalchemy
- Added new fields: `tempat_lahir`, `tanggal_lahir`, `jenis_kelamin`, `agama`, `alamat`, `no_hp`
- Made `nip` and `nim` UNIQUE
- Changed `jenis_kelamin` to ENUM('L', 'P')

#### 2. `app/schemas/user_schema.py`
- Added `date` import
- Updated `UserRegister` with all mahasiswa fields
- Updated `UserResponse` with all mahasiswa fields
- All fields properly typed (Optional[str], Optional[date], etc.)

#### 3. `app/routes/user_route.py`
- Added `date` import
- Updated `UserUpdate` schema with all new fields
- Updated `create_user` to save all mahasiswa data
- Updated `update_user` to handle all new fields
- Updated all responses to include complete user data
- Added date serialization (converts Date to string for JSON)

#### 4. `app/routes/dashboard_route.py`
- Changed mahasiswa count from `SELECT COUNT(*) FROM mahasiswa`
- To: `SELECT COUNT(*) FROM users WHERE role = 'mahasiswa'`

---

## 🎨 FRONTEND UPDATES NEEDED

### Current State:
The frontend currently handles these fields:
- nama, username, email, password, role
- nip (for admin/super_admin)
- nim, kelas (for mahasiswa)

### What Needs to be Added:
You need to add these fields to the mahasiswa form section:

```jsx
// In src/pages/user.jsx - currentUser state
const [currentUser, setCurrentUser] = useState({
  id_user: null,
  nama: "",
  username: "",
  email: "",
  role: "mahasiswa",
  nip: "",
  nim: "",
  tempat_lahir: "",        // ADD THIS
  tanggal_lahir: "",       // ADD THIS
  jenis_kelamin: "",       // ADD THIS
  agama: "",               // ADD THIS
  alamat: "",              // ADD THIS
  no_hp: "",               // ADD THIS
  kelas: "",
  password: "",
});
```

### Form Fields to Add (Inside mahasiswa conditional):
```jsx
{currentUser.role === "mahasiswa" && (
  <>
    <div>
      <label className="block text-sm font-medium text-gray-700">
        NIM
      </label>
      <input type="text" value={currentUser.nim} ... />
    </div>
    
    {/* ADD THESE NEW FIELDS */}
    <div>
      <label className="block text-sm font-medium text-gray-700">
        Tempat Lahir
      </label>
      <input 
        type="text" 
        value={currentUser.tempat_lahir}
        onChange={(e) => setCurrentUser({ ...currentUser, tempat_lahir: e.target.value })}
        className="w-full border border-gray-300 rounded-lg p-2 mt-1"
      />
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-700">
        Tanggal Lahir
      </label>
      <input 
        type="date" 
        value={currentUser.tanggal_lahir}
        onChange={(e) => setCurrentUser({ ...currentUser, tanggal_lahir: e.target.value })}
        className="w-full border border-gray-300 rounded-lg p-2 mt-1"
      />
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-700">
        Jenis Kelamin
      </label>
      <select 
        value={currentUser.jenis_kelamin}
        onChange={(e) => setCurrentUser({ ...currentUser, jenis_kelamin: e.target.value })}
        className="w-full border border-gray-300 rounded-lg p-2 mt-1"
      >
        <option value="">Pilih Jenis Kelamin</option>
        <option value="L">Laki-laki</option>
        <option value="P">Perempuan</option>
      </select>
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-700">
        Agama
      </label>
      <select 
        value={currentUser.agama}
        onChange={(e) => setCurrentUser({ ...currentUser, agama: e.target.value })}
        className="w-full border border-gray-300 rounded-lg p-2 mt-1"
      >
        <option value="">Pilih Agama</option>
        <option value="Islam">Islam</option>
        <option value="Kristen">Kristen</option>
        <option value="Katolik">Katolik</option>
        <option value="Hindu">Hindu</option>
        <option value="Buddha">Buddha</option>
        <option value="Konghucu">Konghucu</option>
      </select>
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-700">
        Alamat
      </label>
      <textarea 
        value={currentUser.alamat}
        onChange={(e) => setCurrentUser({ ...currentUser, alamat: e.target.value })}
        className="w-full border border-gray-300 rounded-lg p-2 mt-1"
        rows="2"
      />
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-700">
        No. HP
      </label>
      <input 
        type="tel" 
        value={currentUser.no_hp}
        onChange={(e) => setCurrentUser({ ...currentUser, no_hp: e.target.value })}
        className="w-full border border-gray-300 rounded-lg p-2 mt-1"
        placeholder="08xxxxxxxxxx"
      />
    </div>

    <div>
      <label className="block text-sm font-medium text-gray-700">
        Kelas
      </label>
      <input type="text" value={currentUser.kelas} ... />
    </div>
  </>
)}
```

### Update fetchUsers Function:
```jsx
const fetchUsers = async () => {
  try {
    setIsLoading(true);
    const data = await apiGet("/users/");
    const transformedUsers = data.map((user) => ({
      id_user: user.id_user,
      nama: user.nama || "",
      username: user.username,
      email: user.email,
      role: roleMap.frontend[user.role] || user.role,
      nip: user.nip || "-",
      nim: user.nim || "-",
      tempat_lahir: user.tempat_lahir || "-",      // ADD
      tanggal_lahir: user.tanggal_lahir || "-",    // ADD
      jenis_kelamin: user.jenis_kelamin || "-",    // ADD
      agama: user.agama || "-",                    // ADD
      alamat: user.alamat || "-",                  // ADD
      no_hp: user.no_hp || "-",                    // ADD
      kelas: user.kelas || "-",
    }));
    setUsers(transformedUsers);
  } catch (error) {
    console.error("Error fetching users:", error);
  } finally {
    setIsLoading(false);
  }
};
```

### Update openEditModal Function:
```jsx
const openEditModal = (user) => {
  setFormMode("edit");
  setCurrentUser({
    id_user: user.id_user,
    nama: user.nama,
    username: user.username,
    email: user.email,
    role: roleMap.backend[user.role] || user.role,
    nip: user.nip === "-" ? "" : user.nip,
    nim: user.nim === "-" ? "" : user.nim,
    tempat_lahir: user.tempat_lahir === "-" ? "" : user.tempat_lahir,    // ADD
    tanggal_lahir: user.tanggal_lahir === "-" ? "" : user.tanggal_lahir, // ADD
    jenis_kelamin: user.jenis_kelamin === "-" ? "" : user.jenis_kelamin, // ADD
    agama: user.agama === "-" ? "" : user.agama,                         // ADD
    alamat: user.alamat === "-" ? "" : user.alamat,                      // ADD
    no_hp: user.no_hp === "-" ? "" : user.no_hp,                         // ADD
    kelas: user.kelas === "-" ? "" : user.kelas,
    password: "",
  });
  setIsModalOpen(true);
};
```

---

## ✅ TESTING CHECKLIST

### Database:
- [ ] New users table has all fields (run DESCRIBE users)
- [ ] mahasiswa table is removed (run SHOW TABLES)
- [ ] Sample data inserted successfully
- [ ] Can query mahasiswa users: `SELECT * FROM users WHERE role = 'mahasiswa'`

### Backend API:
- [ ] GET /users/ returns all fields including tempat_lahir, tanggal_lahir, etc.
- [ ] POST /users/ can create mahasiswa with full data
- [ ] PUT /users/{id} can update all mahasiswa fields
- [ ] GET /dashboard/superadmin/summary shows correct mahasiswa count

### Frontend:
- [ ] Can create new mahasiswa with all fields
- [ ] Can edit existing mahasiswa with all fields
- [ ] Form shows/hides fields based on role correctly
- [ ] Table displays key information properly
- [ ] Delete functionality works

---

## 📊 SAMPLE DATA PROVIDED

The SQL file includes:
- 1 Super Admin (superadmin / admin123)
- 2 Admins (admin.ahmad, admin.siti / admin123)
- 5 Mahasiswa with complete profiles (budi.santoso, siti.rahayu, etc. / mahasiswa123)
- 6 Kelas (TI-1A, TI-1B, TI-2A, TI-2B, TI-3A, TI-3B)
- 5 Mata Kuliah
- 5 Materi entries
- 5 Jadwal Kuliah entries
- 5 Presensi entries

All with proper relationships!

---

## 🔐 DEFAULT CREDENTIALS

**Super Admin:**
- Username: `superadmin`
- Password: `admin123`

**Admin:**
- Username: `admin.ahmad` or `admin.siti`
- Password: `admin123`

**Mahasiswa:**
- Username: `budi.santoso` (or other students)
- Password: `mahasiswa123`

---

## ⚠️ IMPORTANT NOTES

1. **Backup First**: Always backup your database before running migrations
2. **Foreign Keys**: The new structure still uses foreign keys where appropriate (materi→mata_kuliah, presensi→mata_kuliah, etc.)
3. **No mahasiswa Table**: References to mahasiswa table should now point to users table with role filter
4. **NIM is Key**: For linking attendance (presensi), we use `nim` field from users table
5. **Optional Fields**: Most mahasiswa fields are optional (nullable) to allow flexible data entry

---

## 🎯 BENEFITS OF THIS APPROACH

✅ **Single Source of Truth**: All user data in one place
✅ **No Data Duplication**: Email, kelas, nim only stored once
✅ **Easier to Maintain**: Update user info in one location
✅ **Better Performance**: Less JOIN operations needed
✅ **Simpler Logic**: No need to sync between users and mahasiswa tables
✅ **Cleaner API**: One endpoint handles all user types

---

## 📞 NEED HELP?

If you encounter issues:
1. Check terminal for backend errors
2. Check browser console for frontend errors
3. Verify database structure with DESCRIBE users
4. Test API endpoints with test scripts or Postman
5. Ensure all passwords are hashed with bcrypt

---

## 🔄 ROLLBACK PLAN

If you need to go back:
1. Re-import your backup SQL file
2. Revert backend changes using git
3. Revert frontend changes using git

---

**Author**: GitHub Copilot  
**Date**: November 27, 2025  
**Version**: 1.0 - Option 1 (Consolidated Users Table)
