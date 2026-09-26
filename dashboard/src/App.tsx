import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import { SiteProvider } from './context/SiteContext';
import LoginPage from './pages/LoginPage';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ProjectDashboard from './pages/ProjectDashboard';
import CapturesPage from './pages/CapturesPage';
import IssuesPage from './pages/IssuesPage';
import ProjectMembersPage from './pages/ProjectMembersPage';
import VideoJobStatusPage from './pages/VideoJobStatusPage';
import ComparePage from './pages/ComparePage';
import AIDetectPage from './pages/AIDetectPage';
import ReportGenerationPage from './pages/ReportGenerationPage';
import NavigatePage from './pages/NavigatePage';
import AuditLogsPage from './pages/AuditLogsPage';

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
      {/* Global Pages */}
      <Route index element={<HomePage />} />
      <Route path="audit-logs" element={<AuditLogsPage />} />
      
      {/* Project Context Pages */}
      <Route path="projects/:projectId" element={<ProjectDashboard />}>
        {/* Default route inside project redirects to navigate */}
        <Route index element={<Navigate to="navigate" replace />} />
        
        <Route path="navigate" element={<NavigatePage />} />
        <Route path="captures" element={<CapturesPage />} />
        <Route path="compare" element={<ComparePage />} />
        <Route path="issues" element={<IssuesPage />} />
        <Route path="ai-detect" element={<AIDetectPage />} />
        <Route path="reports" element={<ReportGenerationPage />} />
        <Route path="members" element={<ProjectMembersPage />} />
        <Route path="videos/:jobId/status" element={<VideoJobStatusPage />} />
      </Route>
      
      {/* Catch-all redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Route>
  </Routes>
);

const App: React.FC = () => {
  return (
    <AuthProvider>
      <SiteProvider>
        <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <Toaster position="top-right" />
          <AppRoutes />
        </BrowserRouter>
      </SiteProvider>
    </AuthProvider>
  );
};

export default App;
