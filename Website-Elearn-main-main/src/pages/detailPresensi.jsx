import DashboardLayout from "../layouts/dashboardlayout";
import { useState } from "react";
import { navigationItems } from "../navigation/navigation";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, CheckCircle, XCircle, AlertTriangle, Users } from "lucide-react";

export default function DetailPresensi() {
  const [activeNav, setActiveNav] = useState("presensi");
  const { kodeMatkul } = useParams();
  const navigate = useNavigate();

  // Data mata kuliah
  const matkulInfo = {
    IF101: { nama: "Pemrograman Web", dosen: "Dr. Siti Lestari", jam: "08:00 - 09:40" },
    IF202: { nama: "Basis Data", dosen: "Budi Santoso, M.Kom", jam: "10:00 - 11:40" },
    IF303: { nama: "Sistem Informasi", dosen: "Ayu Pratiwi, M.Kom", jam: "13:00 - 14:40" },
  }[kodeMatkul] || { nama: "Mata Kuliah Tidak Ditemukan" };

  // Data presensi mahasiswa
  const dataMahasiswa = [
    { id: 1, nama: "Andi Saputra", nim: "2101001", status: "Hadir" },
    { id: 2, nama: "Budi Rahman", nim: "2101002", status: "Hadir" },
    { id: 3, nama: "Citra Dewi", nim: "2101003", status: "Terlambat" },
    { id: 4, nama: "Dian Prasetyo", nim: "2101004", status: "Tidak Hadir" },
    { id: 5, nama: "Eka Sari", nim: "2101005", status: "Hadir" },
  ];

  const getStatusStyle = (status) => {
    switch (status) {
      case "Hadir": return "bg-green-100 text-green-800";
      case "Terlambat": return "bg-yellow-100 text-yellow-800";
      case "Tidak Hadir": return "bg-red-100 text-red-800";
      default: return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case "Hadir": return <CheckCircle className="h-5 w-5 text-green-500" />;
      case "Terlambat": return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case "Tidak Hadir": return <XCircle className="h-5 w-5 text-red-500" />;
      default: return null;
    }
  };

  return (
    <DashboardLayout navigationItems={navigationItems} activeNav={activeNav} setActiveNav={setActiveNav}>
      <div className="bg-white/60 backdrop-blur-md rounded-2xl border border-gray-200/50 p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3">
              <Users className="text-blue-600" /> Daftar Presensi Mahasiswa
            </h1>
            <p className="text-gray-600 mt-1">{matkulInfo.nama} — {matkulInfo.dosen}</p>
            <p className="text-gray-500 text-sm">{matkulInfo.jam}</p>
          </div>
          <button
            onClick={() => navigate("/presensi")}
            className="flex items-center gap-2 text-blue-600 hover:text-blue-800 transition"
          >
            <ArrowLeft className="h-4 w-4" /> Kembali
          </button>
        </div>

        <table className="w-full border-collapse rounded-lg overflow-hidden">
          <thead>
            <tr className="bg-blue-600 text-white text-left">
              <th className="p-3">No</th>
              <th className="p-3">Nama Mahasiswa</th>
              <th className="p-3">NIM</th>
              <th className="p-3 text-center">Status</th>
            </tr>
          </thead>
          <tbody>
            {dataMahasiswa.map((mhs, index) => (
              <tr
                key={mhs.id}
                className={`border-b hover:bg-blue-50 transition-colors ${
                  index % 2 === 0 ? "bg-white/70" : "bg-gray-50/70"
                }`}
              >
                <td className="p-3">{index + 1}</td>
                <td className="p-3 font-medium text-gray-800">{mhs.nama}</td>
                <td className="p-3 text-gray-600">{mhs.nim}</td>
                <td className="p-3 text-center">
                  <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusStyle(mhs.status)}`}>
                    {getStatusIcon(mhs.status)}
                    {mhs.status}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </DashboardLayout>
  );
}
