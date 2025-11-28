// src/pages/kelolaDosen.jsx
import DashboardLayout from "../layouts/dashboardlayout";
import { useState, useEffect } from "react";
import { navigationItems } from "../navigation/navigation";
import { Users, Edit2, AlertCircle, BookOpen, X, Plus, Trash2 } from "lucide-react";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export default function KelolaDosen() {
  const [activeNav, setActiveNav] = useState("kelola-dosen");
  const [dosenList, setDosenList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [selectedDosen, setSelectedDosen] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [loadingAssignments, setLoadingAssignments] = useState(false);
  
  // Form state for adding new assignment
  const [showAddForm, setShowAddForm] = useState(false);
  const [kelasList, setKelasList] = useState([]);
  const [matkulList, setMatkulList] = useState([]);
  const [formData, setFormData] = useState({
    id_kelas: "",
    kode_mk: "",
    tahun_ajaran: new Date().getFullYear() + "/" + (new Date().getFullYear() + 1),
    semester_aktif: "Ganjil"
  });
  const [notification, setNotification] = useState({ show: false, type: '', message: '' });

  useEffect(() => {
    fetchAllDosen();
    fetchKelasList();
    fetchMatkulList();
  }, []);

  const fetchAllDosen = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_BASE_URL}/dosen`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDosenList(response.data);
    } catch (error) {
      console.error("Error fetching dosen:", error);
      showNotification('error', 'Gagal memuat data dosen');
    } finally {
      setLoading(false);
    }
  };

  const fetchKelasList = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_BASE_URL}/kelas`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setKelasList(response.data);
    } catch (error) {
      console.error("Error fetching kelas:", error);
    }
  };

  const fetchMatkulList = async () => {
    try {
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_BASE_URL}/mata-kuliah`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setMatkulList(response.data);
    } catch (error) {
      console.error("Error fetching mata kuliah:", error);
    }
  };

  const fetchDosenAssignments = async (id_dosen) => {
    try {
      setLoadingAssignments(true);
      const token = localStorage.getItem("token");
      const response = await axios.get(`${API_BASE_URL}/kelas-mata-kuliah/dosen/${id_dosen}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAssignments(response.data);
    } catch (error) {
      console.error("Error fetching assignments:", error);
      showNotification('error', 'Gagal memuat data assignment');
      setAssignments([]);
    } finally {
      setLoadingAssignments(false);
    }
  };

  const handleOpenModal = (dosen) => {
    setSelectedDosen(dosen);
    setShowModal(true);
    setShowAddForm(false);
    fetchDosenAssignments(dosen.id_dosen);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedDosen(null);
    setAssignments([]);
    setShowAddForm(false);
    setFormData({
      id_kelas: "",
      kode_mk: "",
      tahun_ajaran: new Date().getFullYear() + "/" + (new Date().getFullYear() + 1),
      semester_aktif: "Ganjil"
    });
  };

  const handleAddAssignment = async (e) => {
    e.preventDefault();
    
    if (!formData.id_kelas || !formData.kode_mk) {
      showNotification('error', 'Kelas dan Mata Kuliah harus dipilih');
      return;
    }

    try {
      const token = localStorage.getItem("token");
      await axios.post(
        `${API_BASE_URL}/kelas-mata-kuliah`,
        {
          id_dosen: selectedDosen.id_dosen,
          kode_mk: formData.kode_mk,
          id_kelas: parseInt(formData.id_kelas),
          tahun_ajaran: formData.tahun_ajaran,
          semester_aktif: formData.semester_aktif,
          status: "Aktif"
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      showNotification('success', 'Assignment berhasil ditambahkan');
      setShowAddForm(false);
      setFormData({
        id_kelas: "",
        kode_mk: "",
        tahun_ajaran: new Date().getFullYear() + "/" + (new Date().getFullYear() + 1),
        semester_aktif: "Ganjil"
      });
      fetchDosenAssignments(selectedDosen.id_dosen);
    } catch (error) {
      console.error("Error adding assignment:", error);
      showNotification('error', error.response?.data?.detail || 'Gagal menambahkan assignment');
    }
  };

  const handleDeleteAssignment = async (id_kelas_mk) => {
    if (!confirm('Hapus assignment ini? Dosen tidak akan bisa mengakses mata kuliah ini lagi.')) {
      return;
    }

    try {
      const token = localStorage.getItem("token");
      await axios.delete(`${API_BASE_URL}/kelas-mata-kuliah/${id_kelas_mk}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      showNotification('success', 'Assignment berhasil dihapus');
      fetchDosenAssignments(selectedDosen.nip);
    } catch (error) {
      console.error("Error deleting assignment:", error);
      showNotification('error', 'Gagal menghapus assignment');
    }
  };

  const showNotification = (type, message) => {
    setNotification({ show: true, type, message });
    setTimeout(() => {
      setNotification({ show: false, type: '', message: '' });
    }, 3000);
  };

  if (loading) {
    return (
      <DashboardLayout navigationItems={navigationItems} activeNav={activeNav} setActiveNav={setActiveNav}>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Loading dosen...</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout navigationItems={navigationItems} activeNav={activeNav} setActiveNav={setActiveNav}>
      {/* Notification */}
      {notification.show && (
        <div className="fixed top-4 right-4 z-50 animate-slide-in">
          <div className={`px-6 py-4 rounded-xl shadow-lg flex items-center gap-3 ${
            notification.type === 'success' ? 'bg-green-500' : 'bg-red-500'
          } text-white`}>
            {notification.type === 'success' ? '✓' : '✕'} {notification.message}
          </div>
        </div>
      )}

      <div className="bg-white/70 backdrop-blur-sm border border-gray-200 rounded-2xl p-8 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-3">
            <Users className="text-blue-600" /> Kelola Dosen
          </h1>
        </div>

        {/* Dosen Table */}
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 font-semibold text-gray-700">NIP</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Nama</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Email</th>
                <th className="text-left py-3 px-4 font-semibold text-gray-700">Prodi</th>
                <th className="text-center py-3 px-4 font-semibold text-gray-700">Aksi</th>
              </tr>
            </thead>
            <tbody>
              {dosenList.map((dosen) => (
                <tr key={dosen.nip} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 text-sm">{dosen.nip}</td>
                  <td className="py-3 px-4 text-sm font-medium">{dosen.nama}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{dosen.email}</td>
                  <td className="py-3 px-4 text-sm text-gray-600">{dosen.prodi}</td>
                  <td className="py-3 px-4 text-center">
                    <button
                      onClick={() => handleOpenModal(dosen)}
                      className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm flex items-center gap-2 mx-auto transition"
                    >
                      <Edit2 className="h-4 w-4" /> Kelola Akses
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {dosenList.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            <Users className="h-12 w-12 mx-auto mb-3 text-gray-300" />
            <p>Belum ada data dosen</p>
          </div>
        )}
      </div>

      {/* Modal Kelola Assignment */}
      {showModal && selectedDosen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
          <div className="bg-white rounded-2xl p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-xl font-bold text-gray-800">
                  Kelola Akses Dosen
                </h3>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedDosen.nama} ({selectedDosen.nip})
                </p>
              </div>
              <button
                onClick={handleCloseModal}
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            {/* Add Assignment Button */}
            {!showAddForm && (
              <button
                onClick={() => setShowAddForm(true)}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg flex items-center justify-center gap-2 mb-4 transition font-medium"
              >
                <Plus className="h-5 w-5" /> Tambah Assignment Baru
              </button>
            )}

            {/* Add Assignment Form */}
            {showAddForm && (
              <form onSubmit={handleAddAssignment} className="bg-gray-50 rounded-xl p-4 mb-4">
                <h4 className="font-semibold text-gray-800 mb-3">Tambah Assignment Baru</h4>
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Kelas <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.id_kelas}
                      onChange={(e) => setFormData({...formData, id_kelas: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Pilih Kelas</option>
                      {kelasList.map(kelas => (
                        <option key={kelas.id_kelas} value={kelas.id_kelas}>
                          {kelas.nama_kelas} - {kelas.prodi}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Mata Kuliah <span className="text-red-500">*</span>
                    </label>
                    <select
                      value={formData.kode_mk}
                      onChange={(e) => setFormData({...formData, kode_mk: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      required
                    >
                      <option value="">Pilih Mata Kuliah</option>
                      {matkulList.map(mk => (
                        <option key={mk.kode_mk} value={mk.kode_mk}>
                          {mk.nama_mk} ({mk.kode_mk})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Tahun Ajaran
                    </label>
                    <input
                      type="text"
                      value={formData.tahun_ajaran}
                      onChange={(e) => setFormData({...formData, tahun_ajaran: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                      placeholder="2024/2025"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Semester
                    </label>
                    <select
                      value={formData.semester_aktif}
                      onChange={(e) => setFormData({...formData, semester_aktif: e.target.value})}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="Ganjil">Ganjil</option>
                      <option value="Genap">Genap</option>
                    </select>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    type="submit"
                    className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition font-medium"
                  >
                    Simpan
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddForm(false)}
                    className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-lg transition font-medium"
                  >
                    Batal
                  </button>
                </div>
              </form>
            )}

            {/* Current Assignments */}
            <div>
              <h4 className="font-semibold text-gray-800 mb-3">Assignment Saat Ini</h4>
              {loadingAssignments ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                </div>
              ) : assignments.length === 0 ? (
                <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-xl">
                  <BookOpen className="h-10 w-10 mx-auto mb-2 text-gray-300" />
                  <p>Belum ada assignment</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {assignments.map((assignment) => (
                    <div
                      key={assignment.id_kelas_mk}
                      className="border border-gray-200 rounded-lg p-4 flex items-center justify-between hover:shadow-md transition"
                    >
                      <div>
                        <h5 className="font-semibold text-gray-800">
                          {assignment.nama_mk} ({assignment.kode_mk})
                        </h5>
                        <p className="text-sm text-gray-600">
                          {assignment.nama_kelas} • {assignment.prodi} • {assignment.tahun_ajaran} • Semester {assignment.semester_aktif}
                        </p>
                        <span className={`inline-block mt-1 text-xs px-2 py-1 rounded-full ${
                          assignment.status === 'Aktif' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-gray-100 text-gray-700'
                        }`}>
                          {assignment.status}
                        </span>
                      </div>
                      <button
                        onClick={() => handleDeleteAssignment(assignment.id_kelas_mk)}
                        className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-lg transition"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
