import DashboardLayout from "../layouts/dashboardlayout";
import { useState, useEffect } from "react";
import { navigationItems } from "../navigation/navigation";
import { CalendarDays, Clock, MapPin, Users } from "lucide-react";
import { apiGet } from "../utils/apiUtils";

export default function JadwalKuliah() {
  const [activeNav, setActiveNav] = useState("jadwal-kuliah");
  const [jadwal, setJadwal] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchJadwal();
  }, []);

  const fetchJadwal = async () => {
    try {
      setLoading(true);
      // Fetch kelas_mata_kuliah for logged-in dosen with jadwal details
      const data = await apiGet("/kelas-mata-kuliah/me");
      
      // Transform data to include jadwal information
      const jadwalData = data
        .filter(mk => mk.status && mk.status.toLowerCase() === 'aktif')
        .map(mk => ({
          id_kelas_mk: mk.id_kelas_mk,
          kode: mk.kode_mk,
          nama: mk.nama_mk,
          kelas: mk.nama_kelas,
          prodi: mk.prodi,
          tahun_ajaran: mk.tahun_ajaran,
          semester: mk.semester_aktif,
          // These would come from jadwal_kuliah if available
          hari: "Senin", // Placeholder - should come from jadwal_kuliah
          jam_mulai: "08:00",
          jam_selesai: "09:40",
          ruang: "Lab Komputer 1"
        }));
      
      setJadwal(jadwalData);
      setError(null);
    } catch (error) {
      console.error("Error fetching jadwal:", error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout navigationItems={navigationItems} activeNav={activeNav} setActiveNav={setActiveNav}>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Memuat jadwal...</p>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout navigationItems={navigationItems} activeNav={activeNav} setActiveNav={setActiveNav}>
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <h3 className="font-semibold text-red-800 mb-1">Error Loading Data</h3>
          <p className="text-red-600 text-sm">{error}</p>
          <button 
            onClick={fetchJadwal}
            className="mt-3 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm transition"
          >
            Coba Lagi
          </button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout
      navigationItems={navigationItems}
      activeNav={activeNav}
      setActiveNav={setActiveNav}
    >
      {/* 🧭 Informasi jadwal */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-2xl p-8 mb-8 shadow-md">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="bg-white/20 p-4 rounded-xl">
              <CalendarDays className="h-10 w-10 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">Jadwal Mengajar</h1>
              <p className="text-blue-100 text-sm">
                Jadwal perkuliahan yang Anda ampu<br />
                Tahun Ajaran 2024/2025
              </p>
            </div>
          </div>

          <div className="bg-white/20 rounded-xl p-4 text-sm text-blue-100">
            <ul className="space-y-1">
              <li>📚 Total Mata Kuliah: {jadwal.length}</li>
              <li>✅ Status: Aktif</li>
            </ul>
          </div>
        </div>
      </div>

      {/* 📅 Tabel jadwal kuliah */}
      <div className="bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl p-8 shadow-sm">
        <div className="flex items-center gap-3 mb-6">
          <CalendarDays className="text-blue-600 h-6 w-6" />
          <h2 className="text-2xl font-semibold text-gray-800">Jadwal Kuliah</h2>
        </div>

        {jadwal.length === 0 ? (
          <div className="text-center py-12">
            <CalendarDays className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">Tidak ada jadwal kuliah</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-sm">
              <thead className="bg-blue-600 text-white">
                <tr>
                  <th className="py-3 px-4 text-left rounded-tl-lg">Kode MK</th>
                  <th className="py-3 px-4 text-left">Mata Kuliah</th>
                  <th className="py-3 px-4 text-left">Kelas</th>
                  <th className="py-3 px-4 text-left">Prodi</th>
                  <th className="py-3 px-4 text-left">Tahun Ajaran</th>
                  <th className="py-3 px-4 text-left">Semester</th>
                  <th className="py-3 px-4 text-left">Hari</th>
                  <th className="py-3 px-4 text-left">Jam</th>
                  <th className="py-3 px-4 text-left rounded-tr-lg">Ruangan</th>
                </tr>
              </thead>

              <tbody>
                {jadwal.map((item, index) => (
                  <tr
                    key={item.id_kelas_mk}
                    className={`border-b last:border-0 ${
                      index % 2 === 0 ? "bg-white" : "bg-blue-50/60"
                    } hover:bg-blue-100/40 transition`}
                  >
                    <td className="py-2 px-4 font-mono text-xs text-gray-700">{item.kode}</td>
                    <td className="py-2 px-4 text-gray-800 font-medium">{item.nama}</td>
                    <td className="py-2 px-4 text-gray-600">{item.kelas}</td>
                    <td className="py-2 px-4 text-gray-600">{item.prodi}</td>
                    <td className="py-2 px-4 text-gray-600">{item.tahun_ajaran}</td>
                    <td className="py-2 px-4 text-center">{item.semester}</td>
                    <td className="py-2 px-4 text-gray-700">{item.hari}</td>
                    <td className="py-2 px-4 text-gray-700">
                      <div className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-blue-500" />
                        {item.jam_mulai} - {item.jam_selesai}
                      </div>
                    </td>
                    <td className="py-2 px-4 text-gray-700">
                      <div className="flex items-center gap-2">
                        <MapPin className="h-4 w-4 text-blue-500" />
                        <span>{item.ruang}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
