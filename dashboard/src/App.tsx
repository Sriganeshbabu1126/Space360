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
// Remaining imports for ai/reports if they are part of the app, but user didn't mention them. I'll keep them unrouted or comment them out if they break.
// import AIFeaturesPage from './pages/AIFeaturesPage';
// import ReportsPage from './pages/ReportsPage';

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
      
      {/* Project Context Pages */}
      <Route path="projects/:projectId" element={<ProjectDashboard />}>
        {/* Default route inside project redirects to captures */}
        <Route index element={<Navigate to="captures" replace />} />
        
        <Route path="captures" element={<CapturesPage />} />
        <Route path="issues" element={<IssuesPage />} />
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
