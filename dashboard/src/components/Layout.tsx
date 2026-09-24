import React, { useState } from 'react';
import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useSite } from '../context/SiteContext';
import { 
  Menu, LogOut, Camera, AlertCircle, Users, LayoutDashboard, User as UserIcon, Settings, ArrowLeft, FileText, Bot, SplitSquareHorizontal, Map
} from 'lucide-react';
import ProjectHeader from './ProjectHeader';

const Layout: React.FC = () => {
  const { user, isAdmin, signOut } = useAuth();
  const { selectedSiteId, sites } = useSite();
  const location = useLocation();
  const navigate = useNavigate();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // If we are in a project route (or have selectedSiteId active while not on home)
  // Actually, let's rely on the URL path to determine sidebar mode.
  const isProjectView = location.pathname.startsWith('/projects/') && selectedSiteId;
  const currentSite = sites.find(s => s.id === selectedSiteId);

  const globalNavItems = [
    { name: 'Projects Hub', path: '/', icon: LayoutDashboard },
    // { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const projectNavItems = [
    { name: 'Navigate', path: `/projects/${selectedSiteId}/navigate`, icon: Map },
    { name: 'Captures', path: `/projects/${selectedSiteId}/captures`, icon: Camera },
    { name: 'Compare', path: `/projects/${selectedSiteId}/compare`, icon: SplitSquareHorizontal },
    { name: 'Issues', path: `/projects/${selectedSiteId}/issues`, icon: AlertCircle },
    { name: 'Reports', path: `/projects/${selectedSiteId}/reports`, icon: FileText },
    { name: 'AI Detect (Beta)', path: `/projects/${selectedSiteId}/ai-detect`, icon: Bot },
  ];

  if (isAdmin) {
    projectNavItems.push({ name: 'Members', path: `/projects/${selectedSiteId}/members`, icon: Users });
  }

  const displayedNavItems = isProjectView ? projectNavItems : globalNavItems;

  const SidebarContent = () => (
    <>
      <div className="h-16 flex items-center px-6 border-b border-brand-800 shrink-0">
        <Camera className="w-6 h-6 mr-3 text-brand-500" />
        <span className="font-bold text-lg tracking-wide">Space360</span>
      </div>
      
      {isProjectView && currentSite && (
        <div className="px-4 py-4 border-b border-brand-800/50 bg-brand-950">
          <button onClick={() => navigate('/')} className="text-brand-300 hover:text-white flex items-center text-xs font-semibold mb-2 transition-colors">
            <ArrowLeft className="w-3 h-3 mr-1" /> Change Project
          </button>
          <div className="font-bold text-white text-sm line-clamp-2 leading-snug">
            {currentSite.name}
          </div>
        </div>
      )}

      <nav className="flex-1 py-4 space-y-1 overflow-y-auto px-3 custom-scrollbar">
        {displayedNavItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            onClick={() => setIsMobileMenuOpen(false)}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center px-3 py-3 md:py-2.5 text-sm font-medium rounded-lg transition-colors min-h-[44px] ${
                isActive 
                  ? 'bg-brand-800 text-white shadow-sm' 
                  : 'text-brand-100 hover:bg-brand-800 hover:text-white'
              }`
            }
          >
            <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* User profile & Sign out */}
      <div className="p-4 border-t border-brand-800 shrink-0">
        <div className="flex items-center mb-4 px-2">
          {user?.photoURL ? (
            <img src={user.photoURL} alt="Avatar" className="w-8 h-8 rounded-full mr-3 border border-brand-700 object-cover" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center mr-3 shrink-0 shadow-inner">
              <UserIcon className="w-4 h-4 text-brand-100" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.displayName || 'User'}</p>
            <p className="text-xs text-brand-300 truncate">{user?.email}</p>
          </div>
        </div>
        <button 
          onClick={() => {
            setIsMobileMenuOpen(false);
            signOut();
          }}
          className="w-full flex items-center justify-center px-4 py-3 md:py-2 text-sm text-brand-100 hover:text-white hover:bg-brand-800 rounded-lg transition-colors min-h-[44px]"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Sign Out
        </button>
      </div>
    </>
  );

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-64 bg-brand-900 text-white flex-col shrink-0 shadow-xl z-20">
        <SidebarContent />
      </div>

      {/* Mobile drawer backdrop */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-gray-900/50 backdrop-blur-sm z-40 md:hidden transition-opacity"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div 
        className={`fixed inset-y-0 left-0 w-64 bg-brand-900 text-white flex flex-col z-50 transform transition-transform duration-300 ease-in-out md:hidden shadow-2xl ${
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <SidebarContent />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col w-full h-full overflow-hidden">
        {/* Mobile Header */}
        <header className="h-14 md:hidden bg-white shadow-sm border-b border-gray-200 flex items-center px-4 z-10 shrink-0">
          <button 
            onClick={() => setIsMobileMenuOpen(true)}
            className="p-2 -ml-2 text-gray-600 hover:text-gray-900 focus:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center rounded-lg hover:bg-gray-100"
          >
            <Menu className="w-6 h-6" />
          </button>
          <div className="ml-2 font-bold text-lg text-brand-900 leading-tight">Space360</div>
        </header>
        
        {/* Optional old ProjectHeader if you want it (though ProjectDashboard handles context header now) */}
        {!isProjectView && <ProjectHeader />}
        
        {/* Main scrollable area */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
