import React from 'react';
import { useSite } from '../context/SiteContext';
import { Building2, ChevronRight } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const ProjectHeader: React.FC = () => {
  const { selectedSiteId, sites } = useSite();
  const location = useLocation();

  if (!selectedSiteId || location.pathname === '/sites' || location.pathname === '/') return null;

  const currentSite = sites.find(s => s.id === selectedSiteId);
  if (!currentSite) return null;

  return (
    <div className="bg-brand-900 text-white px-4 md:px-8 py-3 flex flex-col sm:flex-row sm:items-center justify-between shrink-0 shadow-md z-20">
      <div className="flex items-center gap-3">
        <div className="bg-brand-800 p-2 rounded-lg">
          <Building2 className="w-5 h-5 text-brand-100" />
        </div>
        <div>
          <p className="text-xs text-brand-300 font-medium uppercase tracking-wider">Current Project</p>
          <h2 className="text-base font-bold text-white leading-tight">{currentSite.name}</h2>
        </div>
      </div>
      <Link 
        to="/sites" 
        className="mt-3 sm:mt-0 inline-flex items-center text-sm font-medium text-brand-200 hover:text-white bg-brand-800 hover:bg-brand-700 px-4 py-2 rounded-lg transition-colors border border-brand-700 w-max"
      >
        Change Project <ChevronRight className="w-4 h-4 ml-1" />
      </Link>
    </div>
  );
};

export default ProjectHeader;
