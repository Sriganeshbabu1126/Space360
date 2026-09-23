import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getVideoJobStatus } from '../services/api';
import PannellumViewer from '../components/PannellumViewer';
import { ArrowLeft, XCircle, CheckCircle, Clock, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';

interface StepStatus {
  status: 'pending' | 'running' | 'complete' | 'failed';
}

interface JobData {
  status: string;
  current_step: string;
  steps?: Record<string, StepStatus>;
  summary?: { gcs_uris?: string[] };
  error_message?: string;
}

const STEP_ORDER = ["detect", "validate", "transfer", "extract", "stitch", "upload"];
const STEP_LABELS: Record<string, string> = {
  detect: "Detect",
  validate: "Validate",
  transfer: "Transfer",
  extract: "Extract",
  stitch: "Stitch",
  upload: "Upload"
};

const VideoJobStatusPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  
  const [jobData, setJobData] = useState<JobData | null>(null);
  const [gcsUrl, setGcsUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;

    const checkStatus = async () => {
      if (!jobId) return;
      try {
        const res = await getVideoJobStatus(jobId);
        const data = res.data as JobData;
        setJobData(data);
        
        if (data.status === 'completed' && data.summary?.gcs_uris?.length) {
          setGcsUrl(data.summary.gcs_uris[0]);
        }
        if (data.status === 'failed') {
          setError(data.error_message || 'Video processing failed.');
        }
      } catch (err: any) {
        console.error(err);
        toast.error('Failed to get video status');
      }
    };

    checkStatus();
    interval = setInterval(() => {
      setJobData(prev => {
        if (prev?.status !== 'completed' && prev?.status !== 'failed') {
          checkStatus();
        }
        return prev;
      });
    }, 5000);

    return () => clearInterval(interval);
  }, [jobId]);

  const renderStepIcon = (status?: string) => {
    switch (status) {
      case 'complete':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'running':
        return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />;
      case 'failed':
        return <XCircle className="w-6 h-6 text-red-500" />;
      case 'pending':
      default:
        return <Clock className="w-6 h-6 text-gray-300" />;
    }
  };

  const getStepColor = (status?: string) => {
    switch (status) {
      case 'complete': return 'border-green-500 bg-green-50';
      case 'running': return 'border-blue-500 bg-blue-50';
      case 'failed': return 'border-red-500 bg-red-50';
      default: return 'border-gray-200 bg-gray-50';
    }
  };

  const currentStepIndex = jobData ? STEP_ORDER.indexOf(jobData.current_step) : -1;

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
        <div className="p-6 border-b border-gray-100 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Video Processing Status</h2>
            <p className="text-sm text-gray-500 mt-1">Job ID: {jobId}</p>
          </div>
          <div className="px-3 py-1 rounded-full text-sm font-medium capitalize bg-gray-100 text-gray-800">
            {jobData?.status || 'Loading...'}
          </div>
        </div>

        <div className="p-8">
          <div className="flex justify-between items-center relative">
            {/* Background line */}
            <div className="absolute top-1/2 left-8 right-8 h-1 bg-gray-200 -z-10 transform -translate-y-1/2" />
            
            {/* Progress line */}
            {currentStepIndex >= 0 && (
              <div 
                className="absolute top-1/2 left-8 h-1 bg-blue-500 -z-10 transform -translate-y-1/2 transition-all duration-500"
                style={{ 
                  width: `${(Math.max(0, currentStepIndex) / (STEP_ORDER.length - 1)) * 100}%`,
                  maxWidth: 'calc(100% - 4rem)' 
                }}
              />
            )}

            {STEP_ORDER.map((stepKey) => {
              const stepInfo = jobData?.steps?.[stepKey];
              const stepStatus = stepInfo?.status || 'pending';
              const isCurrent = jobData?.current_step === stepKey;
              
              return (
                <div key={stepKey} className="flex flex-col items-center bg-white px-2">
                  <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-3 shadow-sm border-2 ${getStepColor(stepStatus)}`}>
                    {renderStepIcon(stepStatus)}
                  </div>
                  <span className={`text-xs md:text-sm font-semibold ${isCurrent ? 'text-blue-600' : stepStatus === 'complete' ? 'text-gray-900' : 'text-gray-400'}`}>
                    {STEP_LABELS[stepKey]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

        {jobData?.status === 'failed' && (
          <div className="m-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center text-red-700">
            <XCircle className="w-6 h-6 mr-3 shrink-0" />
            <div>
              <p className="font-semibold">Processing Failed</p>
              <p className="text-sm mt-1">{error || 'An unknown error occurred during video processing.'}</p>
            </div>
          </div>
        )}
      </div>

      {jobData?.status === 'completed' && gcsUrl && (
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
