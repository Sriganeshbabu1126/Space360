import React, { useEffect, useState } from 'react';
import { useSite } from '../context/SiteContext';
import { getFloorPlans } from '../services/api';
import { Map, ChevronDown } from 'lucide-react';
import toast from 'react-hot-toast';

const FloorPlanSelector: React.FC = () => {
  const { selectedSiteId, selectedFloorPlanId, setSelectedFloorPlanId } = useSite();
  const [floorPlans, setFloorPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchFloorPlans = async () => {
      if (!selectedSiteId) {
        setFloorPlans([]);
        return;
      }
      try {
        setLoading(true);
        const res = await getFloorPlans(selectedSiteId);
        setFloorPlans(res.data);
      } catch (err: any) {
        console.error('Error fetching floor plans:', err);
        toast.error('Failed to load floor plans');
      } finally {
        setLoading(false);
      }
    };

    fetchFloorPlans();
  }, [selectedSiteId]);

  if (!selectedSiteId) return null;

  return (
    <div className="relative mb-6">
      <label className="block text-sm font-medium text-gray-700 mb-1 flex items-center">
        <Map className="w-4 h-4 mr-1 text-gray-500" />
        Current Floor Plan Context
      </label>
      <div className="relative">
        <select
          value={selectedFloorPlanId || ''}
          onChange={(e) => setSelectedFloorPlanId(e.target.value || null)}
          disabled={loading}
          className="appearance-none w-full bg-white border border-gray-300 text-gray-900 text-sm rounded-lg pl-4 pr-10 py-2.5 focus:outline-none focus:ring-2 focus:ring-brand-500 shadow-sm transition-shadow disabled:bg-gray-100 disabled:text-gray-500"
        >
          <option value="">
            {loading ? 'Loading floor plans...' : 'All Floor Plans'}
          </option>
          {floorPlans.map((fp) => (
            <option key={fp.id} value={fp.id}>
              {fp.name}
            </option>
          ))}
        </select>
        <ChevronDown className="w-4 h-4 text-gray-500 absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none" />
      </div>
    </div>
  );
};

export default FloorPlanSelector;
