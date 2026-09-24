import React, { useState } from 'react';
import { Upload, X, FileImage, Loader2 } from 'lucide-react';
import { useSite } from '../context/SiteContext';
import { uploadFloorPlan } from '../services/api';
import toast from 'react-hot-toast';

interface FloorPlanUploadProps {
  onUploadSuccess?: () => void;
}

const FloorPlanUpload: React.FC<FloorPlanUploadProps> = ({ onUploadSuccess }) => {
  const { selectedSiteId } = useSite();
  const [file, setFile] = useState<File | null>(null);
  const [label, setLabel] = useState('');
  const [uploading, setUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      setFile(selectedFile);
      if (!label) setLabel(selectedFile.name.split('.')[0]);
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !label || !selectedSiteId) return;

    try {
      setUploading(true);
      await uploadFloorPlan(selectedSiteId, label, file);
      toast.success('Floor plan uploaded successfully!');
      setFile(null);
      setLabel('');
      setPreviewUrl(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (err: any) {
      console.error(err);
      toast.error(err.response?.data?.detail || 'Failed to upload floor plan');
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setPreviewUrl(null);
  };

  if (!selectedSiteId) return null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
      <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
        <Upload className="w-5 h-5 mr-2 text-brand-600" />
        Upload New Floor Plan
      </h3>
      
      <form onSubmit={handleUpload} className="space-y-4">
        {!file ? (
          <div className="border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:bg-gray-50 hover:border-brand-400 transition-all cursor-pointer relative">
            <input 
              type="file" 
              accept="image/jpeg, image/png, application/pdf"
              onChange={handleFileChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
            <FileImage className="w-10 h-10 text-gray-400 mx-auto mb-3" />
            <p className="text-sm font-medium text-gray-700">Click or drag file to upload</p>
            <p className="text-xs text-gray-500 mt-1">Supports JPG, PNG, PDF</p>
          </div>
        ) : (
          <div className="flex flex-col sm:flex-row gap-6">
            <div className="w-full sm:w-1/3 relative">
              {previewUrl && (
                <img src={previewUrl} alt="Preview" className="w-full h-auto rounded-lg shadow-sm border border-gray-200" />
              )}
              <button 
                type="button" 
                onClick={clearFile}
                className="absolute -top-2 -right-2 bg-red-100 text-red-600 p-1 rounded-full hover:bg-red-200 shadow-sm"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
            
            <div className="w-full sm:w-2/3 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Floor Plan Name</label>
                <input 
                  type="text" 
                  value={label}
                  onChange={(e) => setLabel(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none"
                  placeholder="e.g. Level 1 Layout"
                  required
                />
              </div>
              
              <button 
                type="submit" 
                disabled={uploading}
                className="w-full btn-primary flex justify-center items-center py-2.5"
              >
                {uploading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin mr-2" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5 mr-2" />
                    Upload Floor Plan
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </form>
    </div>
  );
};

export default FloorPlanUpload;
