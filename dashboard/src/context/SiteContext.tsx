import React, { createContext, useContext, useEffect, useState } from 'react';
import { getSites, getContractors } from '../services/api';
import { useAuth } from './AuthContext';

export interface Site {
  id: string;
  name: string;
  address?: string;
  status?: string;
  tenant_id?: string;
}

export interface FloorPlan {
  id: string;
  name: string;
  site_id: string;
}

interface SiteContextType {
  sites: Site[];
  selectedSiteId: string | null;
  setSelectedSiteId: (id: string | null) => void;
  selectedFloorPlanId: string | null;
  setSelectedFloorPlanId: (id: string | null) => void;
  tenantId: string | null;
  loading: boolean;
}

const SiteContext = createContext<SiteContextType>({} as SiteContextType);

// Keeping useSite alias
export const useSiteContext = () => useContext(SiteContext);
export const useSite = () => useContext(SiteContext);

export const SiteProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAdmin } = useAuth();
  const [sites, setSites] = useState<Site[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string | null>(() => localStorage.getItem('selectedSiteId'));
  const [selectedFloorPlanId, setSelectedFloorPlanId] = useState<string | null>(() => localStorage.getItem('selectedFloorPlanId'));
  const [loading, setLoading] = useState(true);

  // Determine tenantId based on current selected site, if available
  const currentSite = sites.find(s => s.id === selectedSiteId);
  const tenantId = currentSite?.tenant_id || null;

  useEffect(() => {
    if (selectedSiteId) {
      localStorage.setItem('selectedSiteId', selectedSiteId);
    } else {
      localStorage.removeItem('selectedSiteId');
    }
  }, [selectedSiteId]);

  useEffect(() => {
    if (selectedFloorPlanId) {
      localStorage.setItem('selectedFloorPlanId', selectedFloorPlanId);
    } else {
      localStorage.removeItem('selectedFloorPlanId');
    }
  }, [selectedFloorPlanId]);

  // If site changes, clear floor plan to ensure we don't carry over an old context
  useEffect(() => {
    setSelectedFloorPlanId(null);
  }, [selectedSiteId]);

  useEffect(() => {
    const fetchSites = async () => {
      if (!user) {
        setSites([]);
        setSelectedSiteId(null);
        setSelectedFloorPlanId(null);
        return;
      }
      
      try {
        setLoading(true);
        if (isAdmin) {
          const res = await getSites();
          setSites(res.data);
        } else {
          // Contractor: fetch their profile
          const res = await getContractors();
          const me = res.data.find((c: any) => c.contact === user.email);
          if (me && me.sites) {
            setSites(me.sites);
          } else {
            setSites([]);
          }
        }
      } catch (err) {
        console.error('Error fetching sites', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSites();
  }, [user, isAdmin]);

  const value = {
    sites,
    selectedSiteId,
    setSelectedSiteId,
    selectedFloorPlanId,
    setSelectedFloorPlanId,
    tenantId,
    loading
  };

  return (
    <SiteContext.Provider value={value}>
      {children}
    </SiteContext.Provider>
  );
};
