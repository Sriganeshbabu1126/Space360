import React from 'react';
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
  User as UserIcon
} from 'lucide-react';

const navItems = [
  { name: 'Home', path: '/', icon: LayoutDashboard },
  { name: 'Sites', path: '/sites', icon: Building2 },
  { name: 'Floor Plans', path: '/floor-plans', icon: Map },
  { name: 'Captures', path: '/captures', icon: Camera },
  { name: 'Compare', path: '/compare', icon: GitCompare },
  { name: 'AI Features', path: '/ai', icon: Sparkles },
  { name: 'Reports', path: '/reports', icon: FileBarChart },
];

const Layout: React.FC = () => {
  const { user, signOut } = useAuth();
  const location = useLocation();

  const currentNavItem = navItems.find(item => item.path === location.pathname) || { name: 'Dashboard' };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-60 bg-brand-900 text-white flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-brand-800">
          <Camera className="w-6 h-6 mr-3 text-brand-500" />
          <span className="font-bold text-lg tracking-wide">Space360</span>
        </div>
        
        <nav className="flex-1 py-4 space-y-1 overflow-y-auto px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors ${
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
        <div className="p-4 border-t border-brand-800">
          <div className="flex items-center mb-4 px-2">
            {user?.photoURL ? (
              <img src={user.photoURL} alt="Avatar" className="w-8 h-8 rounded-full mr-3 border border-brand-700" />
            ) : (
              <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center mr-3">
                <UserIcon className="w-4 h-4 text-brand-100" />
              </div>
            )}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.displayName}</p>
              <p className="text-xs text-brand-300 truncate">{user?.email}</p>
            </div>
          </div>
          <button 
            onClick={() => signOut()}
            className="w-full flex items-center justify-center px-4 py-2 text-sm text-brand-100 hover:text-white hover:bg-brand-800 rounded-lg transition-colors mb-2"
          >
            <LogOut className="w-4 h-4 mr-2" />
            Sign Out
          </button>
          <div className="text-center text-xs text-brand-400 mt-4 border-t border-brand-800 pt-4">
            SGB Dev Apps
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <header className="h-16 bg-white shadow-sm border-b border-gray-200 flex items-center px-8 z-10">
          <h1 className="text-xl font-semibold text-gray-800">{currentNavItem.name}</h1>
        </header>
        
        <main className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
