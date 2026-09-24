import React, { useState } from 'react';
import { FileText, Download, Calendar, Filter, Loader2 } from 'lucide-react';
import { useSite } from '../context/SiteContext';
import { useSiteContext } from '../context/SiteContext';
import toast from 'react-hot-toast';

const ReportGenerationPage: React.FC = () => {
  const { selectedSiteId } = useSite();
  const { selectedFloorPlanId } = useSiteContext();

  const [reportType, setReportType] = useState('site');
  const [format, setFormat] = useState('pdf');
  const [includeCaptures, setIncludeCaptures] = useState(true);
  const [includeIssues, setIncludeIssues] = useState(true);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [generating, setGenerating] = useState(false);

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedSiteId) return;

    try {
      setGenerating(true);
      
      const payload = {
        report_type: reportType,
        project_id: selectedSiteId,
        floor_plan_id: reportType === 'floor_plan' ? selectedFloorPlanId : undefined,
        date_range: startDate || endDate ? { start: startDate, end: endDate } : undefined,
        include_captures: includeCaptures,
        include_issues: includeIssues,
        format: format
      };

      // Mock API call to backend
      console.log('Sending report generation request:', payload);
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast.success('Report generated successfully! Download starting...');
      
      // Mock download
      const a = document.createElement('a');
      a.href = `data:text/plain;charset=utf-8,Mock Report Content`;
      a.download = `report_${new Date().toISOString()}.${format}`;
      a.click();

    } catch (error) {
      console.error(error);
      toast.error('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  if (!selectedSiteId) return null;

  return (
    <div className="max-w-4xl">
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="p-6 border-b border-gray-100 bg-gray-50/50">
          <h2 className="text-xl font-bold text-gray-900 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-brand-600" />
            Generate Project Report
          </h2>
          <p className="text-gray-500 text-sm mt-1">Export captures, issues, and analytics for external stakeholders.</p>
        </div>

        <form onSubmit={handleGenerate} className="p-6 space-y-8">
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center">
              <Filter className="w-4 h-4 mr-2" /> Report Scope
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <label className={`border rounded-lg p-4 cursor-pointer transition-colors ${reportType === 'site' ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-500' : 'border-gray-200 hover:border-gray-300'}`}>
                <input type="radio" name="reportType" value="site" checked={reportType === 'site'} onChange={(e) => setReportType(e.target.value)} className="sr-only" />
                <div className="font-bold text-gray-900 mb-1">Full Site</div>
                <div className="text-xs text-gray-500">All floor plans & issues in project</div>
              </label>

              <label className={`border rounded-lg p-4 cursor-pointer transition-colors ${reportType === 'floor_plan' ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-500' : 'border-gray-200 hover:border-gray-300'}`}>
                <input type="radio" name="reportType" value="floor_plan" checked={reportType === 'floor_plan'} onChange={(e) => setReportType(e.target.value)} className="sr-only" />
                <div className="font-bold text-gray-900 mb-1">Floor Plan</div>
                <div className="text-xs text-gray-500">Only currently selected floor plan</div>
              </label>

              <label className={`border rounded-lg p-4 cursor-pointer transition-colors ${reportType === 'issues' ? 'border-brand-500 bg-brand-50 ring-1 ring-brand-500' : 'border-gray-200 hover:border-gray-300'}`}>
                <input type="radio" name="reportType" value="issues" checked={reportType === 'issues'} onChange={(e) => setReportType(e.target.value)} className="sr-only" />
                <div className="font-bold text-gray-900 mb-1">Issues Only</div>
                <div className="text-xs text-gray-500">Detailed punch list of open issues</div>
              </label>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider flex items-center">
                <Calendar className="w-4 h-4 mr-2" /> Date Range (Optional)
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Start Date</label>
                  <input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none" />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">End Date</label>
                  <input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-brand-500 focus:border-brand-500 outline-none" />
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="text-sm font-bold text-gray-900 uppercase tracking-wider">Includes</h3>
              <div className="space-y-2">
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" checked={includeCaptures} onChange={(e) => setIncludeCaptures(e.target.checked)} className="form-checkbox h-4 w-4 text-brand-600 rounded border-gray-300 focus:ring-brand-500" />
                  <span className="text-sm text-gray-700">Capture Thumbnails & Metadata</span>
                </label>
                <label className="flex items-center space-x-3 cursor-pointer">
                  <input type="checkbox" checked={includeIssues} onChange={(e) => setIncludeIssues(e.target.checked)} className="form-checkbox h-4 w-4 text-brand-600 rounded border-gray-300 focus:ring-brand-500" />
                  <span className="text-sm text-gray-700">Issue Annotations & Comments</span>
                </label>
              </div>
            </div>
          </div>

          <div className="pt-6 border-t border-gray-100 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">Export Format:</span>
              <select value={format} onChange={(e) => setFormat(e.target.value)} className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-brand-500 focus:border-brand-500 block p-2">
                <option value="pdf">PDF Document (.pdf)</option>
                <option value="pptx">PowerPoint (.pptx)</option>
                <option value="xlsx">Excel Data (.xlsx)</option>
              </select>
            </div>

            <button type="submit" disabled={generating || (reportType === 'floor_plan' && !selectedFloorPlanId)} className="btn-primary flex items-center px-6 py-2.5">
              {generating ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" /> Generating...</>
              ) : (
                <><Download className="w-4 h-4 mr-2" /> Generate Report</>
              )}
            </button>
          </div>
          
          {reportType === 'floor_plan' && !selectedFloorPlanId && (
            <p className="text-red-500 text-xs text-right mt-2">Please select a Floor Plan from the top menu first.</p>
          )}
        </form>
      </div>
    </div>
  );
};

export default ReportGenerationPage;
