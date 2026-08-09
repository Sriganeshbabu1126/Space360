import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import Layout from './components/Layout';
import DashboardPage from './pages/DashboardPage';
import SitesPage from './pages/SitesPage';
import ComparePage from './pages/ComparePage';
import CapturesPage from './pages/CapturesPage';
import AIFeaturesPage from './pages/AIFeaturesPage';
import ReportsPage from './pages/ReportsPage';
import FloorPlansPage from './pages/FloorPlansPage';
import ProjectMembersPage from './pages/ProjectMembersPage';
import IssuesPage from './pages/IssuesPage';

const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
      <Route index element={<DashboardPage />} />
      <Route path="sites" element={<SitesPage />} />
      <Route path="floor-plans" element={<FloorPlansPage />} />
      <Route path="captures" element={<CapturesPage />} />
      {/* <Route path="compare" element={<ComparePage />} /> */}
      <Route path="issues" element={<IssuesPage />} />
      <Route path="members" element={<ProjectMembersPage />} />
      <Route path="ai" element={<AIFeaturesPage />} />
      <Route path="reports" element={<ReportsPage />} />
    </Route>
  </Routes>
);

const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Toaster position="top-right" />
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
