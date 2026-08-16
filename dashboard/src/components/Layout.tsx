import React, { useState } from 'react';
import { Outlet, NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Building2, 
  Map, 
  Camera, 
  GitCompare, 
  Sparkles, 
  FileBarChart,
  LogOut,
  User as UserIcon,
  Users,
  AlertCircle,
  Menu,
  X,
  ChevronDown
} from 'lucide-react';
import { useSite } from '../context/SiteContext';
import { useNavigate } from 'react-router-dom';

const SiteSelector = () => {
  const { sites, selectedSiteId, setSelectedSiteId, loading } = useSite();
  const navigate = useNavigate();
  const location = useLocation();

  if (loading || sites.length === 0) return null;

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newSiteId = e.target.value;
    setSelectedSiteId(newSiteId);
    
    if (location.pathname.startsWith('/projects/')) {
      navigate(`/projects/${newSiteId}`);
    }
  };

  return (
    <div className="relative group">
      <select 
        value={selectedSiteId || ''} 
        onChange={handleChange}
        className="appearance-none bg-brand-50 border border-brand-200 text-brand-800 text-sm font-medium rounded-lg pl-4 pr-10 py-2 focus:outline-none focus:ring-2 focus:ring-brand-500 cursor-pointer shadow-sm transition-shadow"
      >
        <option value="" disabled>Select Site...</option>
        {sites.map(site => (
          <option key={site.id} value={site.id}>{site.name}</option>
        ))}
      </select>
      <ChevronDown className="w-4 h-4 text-brand-600 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
    </div>
  );
};

const navItems = [
  { name: 'Home', path: '/', icon: LayoutDashboard },
  { name: 'Sites / Projects', path: '/sites', icon: Building2 },
  { name: 'Floor Plans', path: '/floor-plans', icon: Map },
  { name: 'Captures', path: '/captures', icon: Camera },
  { name: 'Issues', path: '/issues', icon: AlertCircle },
  { name: 'AI Features', path: '/ai', icon: Sparkles },
  { name: 'Reports', path: '/reports', icon: FileBarChart },
  { name: 'Project Members', path: '/members', icon: Users },
];

const Layout: React.FC = () => {
  const { user, isAdmin, signOut } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const currentNavItem = navItems.find(item => item.path === location.pathname) || { name: 'Dashboard' };

  const displayedNavItems = navItems.filter(item => {
    if (item.name === 'Project Members' && !isAdmin) return false;
    return true;
  });

  const SidebarContent = () => (
    <>
      <div className="h-16 flex items-center px-6 border-b border-brand-800 shrink-0">
        <Camera className="w-6 h-6 mr-3 text-brand-500" />
        <span className="font-bold text-lg tracking-wide">Space360</span>
      </div>
      
      <nav className="flex-1 py-4 space-y-1 overflow-y-auto px-3">
        {displayedNavItems.map((item) => (
          <NavLink
            key={item.name}
            to={item.path}
            onClick={() => setIsMobileMenuOpen(false)}
            className={({ isActive }) =>
              `flex items-center px-3 py-3 md:py-2.5 text-sm font-medium rounded-lg transition-colors min-h-[44px] ${
                isActive 
                  ? 'bg-brand-800 text-white' 
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
            <img src={user.photoURL} alt="Avatar" className="w-8 h-8 rounded-full mr-3 border border-brand-700" />
          ) : (
            <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center mr-3 shrink-0">
              <UserIcon className="w-4 h-4 text-brand-100" />
            </div>
          )}
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">{user?.displayName}</p>
            <p className="text-xs text-brand-300 truncate">{user?.email}</p>
          </div>
        </div>
        <button 
          onClick={() => {
            setIsMobileMenuOpen(false);
            signOut();
          }}
          className="w-full flex items-center justify-center px-4 py-3 md:py-2 text-sm text-brand-100 hover:text-white hover:bg-brand-800 rounded-lg transition-colors mb-2 min-h-[44px]"
        >
          <LogOut className="w-4 h-4 mr-2" />
          Sign Out
        </button>
        <div className="text-center text-xs text-brand-400 mt-4 border-t border-brand-800 pt-4">
          SGB Dev Apps
        </div>
      </div>
    </>
  );

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-64 bg-brand-900 text-white flex-col shrink-0">
        <SidebarContent />
      </div>

      {/* Mobile drawer backdrop */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden transition-opacity"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      {/* Mobile Sidebar */}
      <div 
        className={`fixed inset-y-0 left-0 w-64 bg-brand-900 text-white flex flex-col z-50 transform transition-transform duration-300 ease-in-out md:hidden ${
          isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <SidebarContent />
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col w-full h-full overflow-hidden">
        {/* Top Header */}
        <header className="h-16 bg-white shadow-sm border-b border-gray-200 flex items-center justify-between md:justify-between px-4 md:px-8 z-10 shrink-0">
          <div className="flex items-center md:hidden">
            <button 
              onClick={() => setIsMobileMenuOpen(true)}
              className="p-2 -ml-2 text-gray-600 hover:text-gray-900 focus:outline-none min-h-[44px] min-w-[44px] flex items-center justify-center"
            >
              <Menu className="w-6 h-6" />
            </button>
            <span className="font-bold text-lg text-brand-900 ml-2">Space360</span>
          </div>
          <h1 className="text-xl font-semibold text-gray-800 hidden md:block">{currentNavItem.name}</h1>
          
          <div className="flex items-center gap-4">
            <SiteSelector />
          </div>
        </header>
        
        {/* Main scrollable area */}
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
