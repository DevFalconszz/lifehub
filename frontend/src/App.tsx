import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './modules/auth/store';
import { useThemeStore } from './modules/theme/store';
import Layout from './modules/ui/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Tasks from './pages/Tasks';
import Notes from './pages/Notes';
import Finances from './pages/Finances';
import Calendar from './pages/Calendar';
import Readings from './pages/Readings';
import AiChat from './pages/AiChat';
import { useEffect } from 'react';
import { api, setToken } from './api/client';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user);
  if (!user) return <Navigate to="/login" replace />;
  return <Layout>{children}</Layout>;
}

export default function App() {
  const setUser = useAuthStore((s) => s.setUser);

  useEffect(() => {
    const t = localStorage.getItem('token');
    if (t) {
      setToken(t);
      api.me().then((u) => setUser(u)).catch(() => setToken(null));
    }
  }, []);

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/projects" element={<ProtectedRoute><Projects /></ProtectedRoute>} />
      <Route path="/tasks" element={<ProtectedRoute><Tasks /></ProtectedRoute>} />
      <Route path="/notes" element={<ProtectedRoute><Notes /></ProtectedRoute>} />
      <Route path="/finances" element={<ProtectedRoute><Finances /></ProtectedRoute>} />
      <Route path="/calendar" element={<ProtectedRoute><Calendar /></ProtectedRoute>} />
      <Route path="/readings" element={<ProtectedRoute><Readings /></ProtectedRoute>} />
      <Route path="/ai" element={<ProtectedRoute><AiChat /></ProtectedRoute>} />
    </Routes>
  );
}
