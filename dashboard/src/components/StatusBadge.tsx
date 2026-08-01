import React from 'react';

interface StatusBadgeProps {
  status: string;
  type: 'ai_status' | 'severity' | 'significance' | 'stage' | 'category';
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status, type }) => {
  let colorClass = 'bg-gray-100 text-gray-800 border-gray-200';
  const norm = status.toLowerCase();

  if (type === 'ai_status') {
    if (norm === 'pending') colorClass = 'bg-gray-100 text-gray-800 border-gray-200';
    if (norm === 'processing') colorClass = 'bg-blue-100 text-blue-800 border-blue-200';
    if (norm === 'done') colorClass = 'bg-green-100 text-green-800 border-green-200';
    if (norm === 'error') colorClass = 'bg-red-100 text-red-800 border-red-200';
  } else if (type === 'severity' || type === 'significance') {
    if (norm === 'info' || norm === 'low') colorClass = 'bg-gray-100 text-gray-800 border-gray-200';
    if (norm === 'warning' || norm === 'medium') colorClass = 'bg-yellow-100 text-yellow-800 border-yellow-200';
    if (norm === 'critical' || norm === 'high') colorClass = 'bg-red-100 text-red-800 border-red-200';
  } else if (type === 'stage') {
    if (norm === 'foundation') colorClass = 'bg-orange-100 text-orange-800 border-orange-200';
    if (norm === 'structure') colorClass = 'bg-blue-100 text-blue-800 border-blue-200';
    if (norm === 'mep') colorClass = 'bg-purple-100 text-purple-800 border-purple-200';
    if (norm === 'finishing') colorClass = 'bg-green-100 text-green-800 border-green-200';
    if (norm === 'handover') colorClass = 'bg-brand-100 text-brand-800 border-brand-200';
  } else if (type === 'category') {
    if (norm === 'structural') colorClass = 'bg-blue-50 text-blue-700 border-blue-200';
    if (norm === 'mechanical') colorClass = 'bg-orange-50 text-orange-700 border-orange-200';
    if (norm === 'electrical') colorClass = 'bg-yellow-50 text-yellow-700 border-yellow-200';
    if (norm === 'finishing') colorClass = 'bg-pink-50 text-pink-700 border-pink-200';
    if (norm === 'safety') colorClass = 'bg-red-50 text-red-700 border-red-200';
    if (norm === 'other') colorClass = 'bg-gray-50 text-gray-700 border-gray-200';
  }

  return (
    <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-full shadow-sm border ${colorClass}`}>
      {status}
    </span>
  );
};

export default StatusBadge;
