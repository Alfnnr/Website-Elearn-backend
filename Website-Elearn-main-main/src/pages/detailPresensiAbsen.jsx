import DashboardLayout from "../layouts/dashboardlayout";
import { useState, useEffect } from "react";
import { navigationItems } from "../navigation/navigation";
import { ArrowLeft, UserCheck, Users, BookOpen, Calendar, Download, CheckCircle, XCircle, Clock } from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

export default function DetailPresensiAbsen() {
  const [activeNav, setActiveNav] = useState("presensi");
  const navigate = useNavigate();
  const { kode_mk, tanggal, pertemuan_ke } = useParams(); // Get params from URL

  const [daftarAbsen, setDaftarAbsen] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailPresensi, setDetailPresensi] = useState({
    kelas: "",
    matkul: "",
    kode_mk: "",
    pertemuan: 0,
    tanggal: "",
    waktu_mulai: "",
    waktu_selesai: ""
  });

  // Load data dari backend
  useEffect(() => {
    loadDetailPresensi();
  }, [kode_mk, tanggal, pertemuan_ke]);

  const loadDetailPresensi = async () => {
    try {
      const response = await fetch(`http://localhost:8000/presensi/detail/${kode_mk}/${tanggal}/${pertemuan_ke}`);
      if (response.ok) {
        const data = await response.json();
        
        if (data.length > 0) {
          // Set data absen mahasiswa
          setDaftarAbsen(data);
          
          // Load info mata kuliah dan kelas (dari data pertama)
          loadInfoMatkul(kode_mk);
          loadInfoKelas(data[0].id_mahasiswa);
          
          setDetailPresensi(prev => ({
            ...prev,
            kode_mk: kode_mk,
            pertemuan: parseInt(pertemuan_ke),
            tanggal: tanggal
          }));
        }
      } else {
        alert("Data presensi tidak ditemukan");
        navigate("/presensi");
      }
    } catch (error) {
      console.error("Error loading detail presensi:", error);
      alert("Gagal memuat data presensi");
    } finally {
      setLoading(false);
    }
  };

  const loadInfoMatkul = async (kode_mk) => {
    try {
      const response = await fetch(`http://localhost:8000/mata-kuliah/${kode_mk}`);
      if (response.ok) {
        const data = await response.json();
        setDetailPresensi(prev => ({
          ...prev,
          matkul: data.nama_mk
        }));
      }
    } catch (error) {
      console.error("Error loading mata kuliah:", error);
    }
  };

  const loadInfoKelas = async (id_mahasiswa) => {
    try {
      // Ambil data mahasiswa untuk mendapatkan id_kelas
      const responseMhs = await fetch(`http://localhost:8000/mahasiswa/${id_mahasiswa}`);
      if (responseMhs.ok) {
        const dataMhs = await responseMhs.json();
        
        // Ambil data kelas
        const responseKelas = await fetch(`http://localhost:8000/kelas/${dataMhs.id_kelas}`);
        if (responseKelas.ok) {
          const dataKelas = await responseKelas.json();
          setDetailPresensi(prev => ({
            ...prev,
            kelas: dataKelas.nama_kelas
          }));
        }
      }
    } catch (error) {
      console.error("Error loading kelas:", error);
    }
  };

  const handleKembali = () => {
    navigate("/presensi");
  };

  const handleExport = () => {
    // Export data ke CSV
    const csvContent = generateCSV();
    downloadCSV(csvContent, `Presensi_${detailPresensi.kelas}_${detailPresensi.matkul}_Pertemuan${detailPresensi.pertemuan}_${detailPresensi.tanggal}.csv`);
  };

  const generateCSV = () => {
    // Header info
    let csv = `DAFTAR PRESENSI MAHASISWA\n`;
    csv += `Kelas,${detailPresensi.kelas}\n`;
    csv += `Mata Kuliah,${detailPresensi.matkul} (${detailPresensi.kode_mk})\n`;
    csv += `Pertemuan,${detailPresensi.pertemuan}\n`;
    csv += `Tanggal,${new Date(detailPresensi.tanggal).toLocaleDateString('id-ID', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}\n`;
    csv += `Waktu,${detailPresensi.waktu_mulai || '00:00'} - ${detailPresensi.waktu_selesai || '00:00'}\n`;
    csv += `\n`;
    
    // Statistik
    csv += `Total Mahasiswa,${totalMahasiswa}\n`;
    csv += `Hadir,${hadir}\n`;
    csv += `Alpa,${alpa}\n`;
    csv += `Persentase Kehadiran,${persentaseKehadiran}%\n`;
    csv += `\n`;
    
    // Header tabel
    csv += `No,NIM,Nama Mahasiswa,Status,Waktu Absen\n`;
    
    // Data mahasiswa
    daftarAbsen.forEach((mahasiswa, index) => {
      const waktuAbsen = mahasiswa.waktu_input 
        ? new Date(mahasiswa.waktu_input).toLocaleTimeString('id-ID')
        : '-';
      csv += `${index + 1},${mahasiswa.nim},"${mahasiswa.nama_mahasiswa}",${mahasiswa.status},${waktuAbsen}\n`;
    });
    
    return csv;
  };

  const downloadCSV = (content, filename) => {
    // Add BOM for Excel to recognize UTF-8
    const BOM = '\uFEFF';
    const blob = new Blob([BOM + content], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusBadge = (status) => {
    const badges = {
      Hadir: { 
        color: "bg-green-100 text-green-800 border-green-300", 
        icon: CheckCircle, 
        text: "Hadir" 
      },
      "Belum Absen": {
        color: "bg-yellow-100 text-yellow-800 border-yellow-300",
        icon: Clock,
        text: "Belum Absen"
      },
      Alfa: { 
        color: "bg-red-100 text-red-800 border-red-300", 
        icon: XCircle, 
        text: "Alpa" 
      },
    };
    const badge = badges[status] || badges["Belum Absen"];
    const Icon = badge.icon;
    return (
      <span className={`${badge.color} px-3 py-1.5 rounded-full text-xs font-semibold border flex items-center gap-1.5 justify-center w-fit`}>
        <Icon className="h-3.5 w-3.5" />
        {badge.text}
      </span>
    );
  };

  // Hitung statistik
  const totalMahasiswa = daftarAbsen.length;
  const hadir = daftarAbsen.filter(m => m.status === 'Hadir').length;
  const belumAbsen = daftarAbsen.filter(m => m.status === 'Belum Absen').length;
  const alpa = daftarAbsen.filter(m => m.status === 'Alfa').length;
  const persentaseKehadiran = totalMahasiswa > 0 ? ((hadir / totalMahasiswa) * 100).toFixed(1) : 0;

  if (loading) {
    return (
      <DashboardLayout navigationItems={navigationItems} activeNav={activeNav} setActiveNav={setActiveNav}>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Memuat data...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout navigationItems={navigationItems} activeNav={activeNav} setActiveNav={setActiveNav}>
      <div className="space-y-6">
        
        {/* Header dengan Tombol Kembali */}
        <div className="bg-white/60 backdrop-blur-md rounded-2xl border border-gray-200/50 p-6">
          <button
            onClick={handleKembali}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4 transition"
          >
            <ArrowLeft className="h-5 w-5" />
            <span className="font-semibold">Kembali ke Daftar Presensi</span>
          </button>

          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-3 mb-2">
                <UserCheck className="text-blue-600" /> Detail Absensi Mahasiswa
              </h1>
              <p className="text-gray-600 text-sm">Daftar kehadiran mahasiswa untuk pertemuan ini</p>
            </div>

            <button
              onClick={handleExport}
              className="bg-green-600 text-white px-6 py-2.5 rounded-lg hover:bg-green-700 transition flex items-center gap-2 font-semibold"
            >
              <Download className="h-5 w-5" />
              Export Data
            </button>
          </div>
        </div>

        {/* Info Presensi */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="flex items-center gap-3">
              <div className="bg-blue-100 p-3 rounded-lg">
                <Users className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Kelas</p>
                <p className="font-bold text-gray-900">{detailPresensi.kelas}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="bg-purple-100 p-3 rounded-lg">
                <BookOpen className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Mata Kuliah</p>
                <p className="font-bold text-gray-900">{detailPresensi.matkul}</p>
                <p className="text-xs text-gray-500">{detailPresensi.kode_mk}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="bg-orange-100 p-3 rounded-lg">
                <Calendar className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Pertemuan & Tanggal</p>
                <p className="font-bold text-gray-900">Pertemuan {detailPresensi.pertemuan}</p>
                <p className="text-xs text-gray-500">
                  {new Date(detailPresensi.tanggal).toLocaleDateString('id-ID', { 
                    weekday: 'long', 
                    year: 'numeric', 
                    month: 'long', 
                    day: 'numeric' 
                  })}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-blue-200">
            <div className="flex items-center gap-3">
              <Clock className="h-5 w-5 text-blue-600" />
              <p className="text-sm text-gray-700">
                <span className="font-semibold">Waktu Presensi:</span> {detailPresensi.waktu_mulai || "00:00"} - {detailPresensi.waktu_selesai || "00:00"}
              </p>
            </div>
          </div>
        </div>

        {/* Statistik Ringkasan */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-white border border-gray-200 rounded-xl p-4 text-center">
            <p className="text-3xl font-bold text-gray-900">{totalMahasiswa}</p>
            <p className="text-sm text-gray-600 mt-1">Total</p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
            <p className="text-3xl font-bold text-green-600">{hadir}</p>
            <p className="text-sm text-gray-600 mt-1">Hadir</p>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 text-center">
            <p className="text-3xl font-bold text-yellow-600">{belumAbsen}</p>
            <p className="text-sm text-gray-600 mt-1">Belum Absen</p>
          </div>
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-center">
            <p className="text-3xl font-bold text-red-600">{alpa}</p>
            <p className="text-sm text-gray-600 mt-1">Alpa</p>
          </div>
          <div className="bg-indigo-50 border border-indigo-200 rounded-xl p-4 text-center">
            <p className="text-3xl font-bold text-indigo-600">{persentaseKehadiran}%</p>
            <p className="text-sm text-gray-600 mt-1">Kehadiran</p>
          </div>
        </div>

        {/* Tabel Daftar Absen */}
        <div className="bg-white/60 backdrop-blur-md rounded-2xl border border-gray-200/50 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">No</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">NIM</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Nama Mahasiswa</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Waktu Absen</th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Verifikasi Foto</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200 bg-white">
                {daftarAbsen.map((mahasiswa, index) => (
                  <tr key={mahasiswa.id_presensi} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                      {index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {mahasiswa.nim}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {mahasiswa.nama_mahasiswa}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(mahasiswa.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {mahasiswa.waktu_input ? (
                        <span className="flex items-center gap-1.5">
                          <Clock className="h-4 w-4 text-gray-400" />
                          {new Date(mahasiswa.waktu_input).toLocaleTimeString('id-ID')}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {mahasiswa.status === 'Hadir' ? (
                        <span className="bg-green-100 text-green-800 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 w-fit">
                          ✓ Terverifikasi
                        </span>
                      ) : (
                        <span className="bg-gray-100 text-gray-600 px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1.5 w-fit">
                          ✗ Tidak ada
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Progress Bar Kehadiran */}
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <h3 className="font-semibold text-gray-900 mb-3">Progress Kehadiran</h3>
          <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
            <div className="flex h-full">
              <div 
                className="bg-green-600 flex items-center justify-center text-white text-xs font-bold"
                style={{ width: `${(hadir / totalMahasiswa) * 100}%` }}
              >
                {hadir > 0 && `${hadir}`}
              </div>
              <div 
                className="bg-yellow-500 flex items-center justify-center text-white text-xs font-bold"
                style={{ width: `${(belumAbsen / totalMahasiswa) * 100}%` }}
              >
                {belumAbsen > 0 && `${belumAbsen}`}
              </div>
              <div 
                className="bg-red-600 flex items-center justify-center text-white text-xs font-bold"
                style={{ width: `${(alpa / totalMahasiswa) * 100}%` }}
              >
                {alpa > 0 && `${alpa}`}
              </div>
            </div>
          </div>
          <div className="flex flex-wrap gap-4 mt-3 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-600 rounded"></div>
              <span className="text-gray-600">Hadir ({hadir})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 rounded"></div>
              <span className="text-gray-600">Belum Absen ({belumAbsen})</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-600 rounded"></div>
              <span className="text-gray-600">Alpa ({alpa})</span>
            </div>
          </div>
        </div>

      </div>
    </DashboardLayout>
  );
}
