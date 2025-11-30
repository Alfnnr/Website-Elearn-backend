// src/navigation/navigation.jsx
import { 
  LayoutDashboard, Calendar, CheckCircle, BookOpen,
  GraduationCap, CalendarDays, User, Users
} from "lucide-react";

export const navigationItems = [
  { id: "Dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "Mata-kuliah", label: "Mata Kuliah", icon: Calendar },
  { id: "jadwal-kuliah", label: "Jadwal Kuliah", icon: CalendarDays },
  { id: "presensi", label: "Input Presensi", icon: CheckCircle },
  { id: "materi", label: "Materi", icon: BookOpen },
  { id: "profil-saya", label: "Profil Saya", icon: User, adminOnly: true },
  { id: "kelola-dosen", label: "Kelola Dosen", icon: Users, superAdminOnly: true },
  { id: "User", label: "User", icon: User, superAdminOnly: true },
];
