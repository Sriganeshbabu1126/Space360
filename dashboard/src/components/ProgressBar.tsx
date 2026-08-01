import React, { useEffect, useState } from 'react';

interface ProgressBarProps {
  value: number;
  label: string;
  colorClass?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({ value, label, colorClass = 'bg-brand-600' }) => {
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => setWidth(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  return (
    <div className="w-full mb-3">
      <div className="flex justify-between items-center mb-1">
        <span className="text-xs font-semibold text-gray-700">{label}</span>
        <span className="text-xs font-bold text-gray-900">{value}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden shadow-inner">
        <div 
          className={`h-2.5 rounded-full transition-all duration-1000 ease-out ${colorClass}`}
          style={{ width: `${width}%` }}
        ></div>
      </div>
    </div>
  );
};

export default ProgressBar;
