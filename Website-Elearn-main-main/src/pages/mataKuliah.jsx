// import DashboardLayout from "../layouts/dashboardlayout";
// import { useState } from "react";
// import {
//   LayoutDashboard, Info, Calendar, CheckCircle, ClipboardList, GraduationCap, Users, Trophy,
//   BookOpen, Award, TrendingUp, Clock, Bell, FileText
// } from "lucide-react"
// import { navigationItems } from "../navigation/navigation";
// ;

// export default function MataKuliah() {
//   const [activeNav, setActiveNav] = useState("Mata-kuliah");


//   // 🟨 Data dummy untuk tabel mata kuliah
//   const courses = [
//     { kode: "IF101", nama: "Pemrograman Web", dosen: "Dr. Siti Lestari", sks: 3 },
//     { kode: "IF202", nama: "Basis Data", dosen: "Budi Santoso, M.Kom", sks: 2 },
//     { kode: "IF303", nama: "Jaringan Komputer", dosen: "Rina Dewi, M.T", sks: 3 },
//     { kode: "IF404", nama: "Kecerdasan Buatan", dosen: "Dr. Rahmat Hidayat", sks: 3 },
//     { kode: "IF505", nama: "Sistem Informasi", dosen: "Ayu Pratiwi, M.Kom", sks: 2 },
//   ];

//   return (
//     <DashboardLayout
//       navigationItems={navigationItems}
//       activeNav={activeNav}
//       setActiveNav={setActiveNav}
//     >
//       {/* Konten Halaman Mata Kuliah */}
//       <div className="bg-white/60 backdrop-blur-md rounded-2xl border border-gray-200/50 p-8">
//         <h1 className="text-2xl font-bold text-gray-900 mb-6">Daftar Mata Kuliah</h1>
//         <table className="w-full border-collapse rounded-lg overflow-hidden">
//           <thead>
//             <tr className="bg-blue-600 text-white text-left">
//               <th className="p-3">Kode</th>
//               <th className="p-3">Nama Mata Kuliah</th>
//               <th className="p-3">Dosen Pengampu</th>
//               <th className="p-3 text-center">SKS</th>
//             </tr>
//           </thead>
//           <tbody>
//             {courses.map((mk, i) => (
//               <tr
//                 key={i}
//                 className={`border-b hover:bg-blue-50 transition-colors ${
//                   i % 2 === 0 ? "bg-white/70" : "bg-gray-50/70"
//                 }`}
//               >
//                 <td className="p-3">{mk.kode}</td>
//                 <td className="p-3 font-medium text-gray-800">{mk.nama}</td>
//                 <td className="p-3 text-gray-600">{mk.dosen}</td>
//                 <td className="p-3 text-center">{mk.sks}</td>
//               </tr>
//             ))}
//           </tbody>
//         </table>
//       </div>
//     </DashboardLayout>
//   );
// }

import DashboardLayout from "../layouts/dashboardlayout";
import { useState, useEffect } from "react";
import { navigationItems } from "../navigation/navigation";
import { apiGet } from "../utils/apiUtils";

export default function MataKuliah() {
  const [activeNav, setActiveNav] = useState("Mata-kuliah");
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMataKuliah = async () => {
      try {
        setLoading(true);
        // Fetch kelas_mata_kuliah for logged-in dosen
        const data = await apiGet("/kelas-mata-kuliah/me");
        setCourses(data);
        setError(null);
      } catch (error) {
        console.error("Gagal mengambil data mata kuliah:", error);
        setError("Gagal memuat data mata kuliah. Pastikan Anda sudah login.");
      } finally {
        setLoading(false);
      }
    };

    fetchMataKuliah();
  }, []);

  return (
    <DashboardLayout
      navigationItems={navigationItems}
      activeNav={activeNav}
      setActiveNav={setActiveNav}
    >
      {/* Konten Halaman Mata Kuliah */}
      <div className="bg-white/60 backdrop-blur-md rounded-2xl border border-gray-200/50 p-8">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Daftar Mata Kuliah</h1>
        
        {/* Loading State */}
        {loading && (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 mt-2">Memuat data...</p>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
            {error}
          </div>
        )}

        {/* Table - Only show when not loading and no error */}
        {!loading && !error && (
          <table className="w-full border-collapse rounded-lg overflow-hidden">
            <thead>
              <tr className="bg-blue-600 text-white text-left">
                <th className="p-3">Kode MK</th>
                <th className="p-3">Nama Mata Kuliah</th>
                <th className="p-3">Kelas</th>
                <th className="p-3">Tahun Ajaran</th>
                <th className="p-3">Semester</th>
                <th className="p-3 text-center">SKS</th>
                <th className="p-3">Status</th>
              </tr>
            </thead>
            <tbody>
              {courses.length === 0 ? (
                <tr>
                  <td colSpan="7" className="p-8 text-center text-gray-500">
                    Tidak ada mata kuliah yang Anda ampu
                  </td>
                </tr>
              ) : (
                courses.map((mk, i) => (
                  <tr
                    key={mk.id_kelas_mk}
                    className={`border-b hover:bg-blue-50 transition-colors ${
                      i % 2 === 0 ? "bg-white/70" : "bg-gray-50/70"
                    }`}
                  >
                    <td className="p-3 font-mono text-sm">{mk.kode_mk}</td>
                    <td className="p-3 font-medium text-gray-800">{mk.nama_mk}</td>
                    <td className="p-3 text-gray-600">{mk.nama_kelas} ({mk.prodi})</td>
                    <td className="p-3 text-gray-600">{mk.tahun_ajaran}</td>
                    <td className="p-3 text-center">{mk.semester_aktif}</td>
                    <td className="p-3 text-center">{mk.sks}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        mk.status && mk.status.toLowerCase() === 'aktif' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-gray-100 text-gray-600'
                      }`}>
                        {mk.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </DashboardLayout>
  );
}