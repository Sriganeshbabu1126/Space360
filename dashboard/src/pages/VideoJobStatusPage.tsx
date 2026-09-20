import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVideoJobStatus } from '../services/api';
import PannellumViewer from '../components/PannellumViewer';
import { ArrowLeft, XCircle } from 'lucide-react';
import toast from 'react-hot-toast';

const VideoJobStatusPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const [status, setStatus] = useState<string>('queued');
  const [gcsUrl, setGcsUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const checkStatus = async () => {
      if (!jobId) return;
      try {
        const res = await getVideoJobStatus(jobId);
        const data = res.data;
        setStatus(data.status);
        if (data.status === 'completed' && data.summary?.gcs_uris?.length > 0) {
          setGcsUrl(data.summary.gcs_uris[0]);
        }
        if (data.status === 'failed') {
          setError('Video processing failed.');
        }
      } catch (err: any) {
        console.error(err);
        toast.error('Failed to get video status');
      }
    };

    checkStatus();
    interval = setInterval(() => {
      if (status !== 'completed' && status !== 'failed') {
        checkStatus();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [jobId, status]);

  const timelineSteps = [
    { key: 'queued', label: 'Queued', icon: '⏳' },
    { key: 'processing', label: 'Processing', icon: '🔄' },
    { key: 'stitching', label: 'Stitching', icon: '✂️' },
    { key: 'completed', label: 'Completed', icon: '✅' },
  ];

  const getStepIndex = (st: string) => {
    if (st === 'queued') return 0;
    if (st === 'processing') return 1;
    if (st === 'stitching') return 2;
    if (st === 'completed') return 3;
    if (st === 'failed') return -1;
    return 1;
  };

  const currentIndex = getStepIndex(status);

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8">
      <button 
        onClick={() => navigate('/captures')}
        className="flex items-center text-brand-600 hover:text-brand-800 mb-6 font-medium"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Back to Captures
      </button>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden mb-8">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-xl font-bold text-gray-900">Video Processing Status</h2>
          <p className="text-sm text-gray-500 mt-1">Job ID: {jobId}</p>
        </div>

        <div className="p-8 flex justify-between items-center relative">
          <div className="absolute top-1/2 left-10 right-10 h-1 bg-gray-200 -z-10 transform -translate-y-1/2" />
          {currentIndex >= 0 && (
            <div 
              className="absolute top-1/2 left-10 h-1 bg-brand-500 -z-10 transform -translate-y-1/2 transition-all duration-500"
              style={{ width: `${(currentIndex / 3) * 100}%`, maxWidth: 'calc(100% - 5rem)' }}
            />
          )}

          {timelineSteps.map((step, idx) => {
            const isCompleted = currentIndex >= idx;
            const isCurrent = currentIndex === idx;
            
            return (
              <div key={step.key} className="flex flex-col items-center bg-white px-4">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl mb-3 shadow-sm border-2 ${
                  isCompleted ? 'border-brand-500 bg-brand-50' : 'border-gray-200 bg-gray-50 opacity-50'
                } ${isCurrent && status !== 'completed' ? 'animate-pulse' : ''}`}>
                  {step.icon}
                </div>
                <span className={`text-sm font-semibold ${isCompleted ? 'text-gray-900' : 'text-gray-400'}`}>
                  {step.label}
                </span>
              </div>
            );
          })}
        </div>

        {status === 'failed' && (
          <div className="m-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
            <XCircle className="w-6 h-6 mr-3 shrink-0" />
            <div>
              <p className="font-semibold">Processing Failed</p>
              <p className="text-sm mt-1">{error || 'An unknown error occurred during video processing.'}</p>
            </div>
          </div>
        )}
      </div>

      {status === 'completed' && gcsUrl && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">360° Video Preview</h3>
          </div>
          <div className="h-[500px] w-full bg-black">
             <PannellumViewer url={gcsUrl} isVideo={true} />
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoJobStatusPage;
