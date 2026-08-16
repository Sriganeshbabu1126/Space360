import React, { createContext, useContext, useEffect, useState } from 'react';
import { getSites, getContractors } from '../services/api';
import { useAuth } from './AuthContext';

interface Site {
  id: string;
  name: string;
}

interface SiteContextType {
  sites: Site[];
  selectedSiteId: string | null;
  setSelectedSiteId: (id: string | null) => void;
  loading: boolean;
}

const SiteContext = createContext<SiteContextType>({} as SiteContextType);

export const useSite = () => useContext(SiteContext);

export const SiteProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, isAdmin } = useAuth();
  const [sites, setSites] = useState<Site[]>([]);
  const [selectedSiteId, setSelectedSiteId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSites = async () => {
      if (!user) {
        setSites([]);
        setSelectedSiteId(null);
        return;
      }
      
      try {
        setLoading(true);
        if (isAdmin) {
          const res = await getSites();
          setSites(res.data);
          if (res.data.length > 0 && !selectedSiteId) {
            setSelectedSiteId(res.data[0].id);
          }
        } else {
          // Contractor: fetch their profile
          const res = await getContractors();
          const me = res.data.find((c: any) => c.contact === user.email);
          if (me && me.sites) {
            setSites(me.sites);
            if (me.sites.length > 0 && !selectedSiteId) {
              setSelectedSiteId(me.sites[0].id);
            }
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
    loading
  };

  return (
    <SiteContext.Provider value={value}>
      {children}
    </SiteContext.Provider>
  );
};
