import axios from "axios";
import { auth } from "./firebase";

const BASE_URL = process.env.REACT_APP_API_URL 
                 || "http://localhost:8000";

const api = axios.create({ baseURL: BASE_URL });

// Attach Firebase token to every request
api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const getAuthHeaders = async (): Promise<Record<string, string>> => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    return { Authorization: `Bearer ${token}` };
  }
  return {};
};


// --- Sites ---
export const getSites = () => 
  api.get("/sites/");
export const createSite = (data: object) => 
  api.post("/sites/", data);
export const getSite = (id: string) => 
  api.get(`/sites/${id}`);

// --- Floor Plans ---
export const getAllFloorPlans = () => api.get("/floor-plans/");
export const getFloorPlans = (siteId: string) =>
  api.get(`/floor-plans/site/${siteId}`);
export const uploadFloorPlan = (
  siteId: string, label: string, file: File) => {
  const form = new FormData();
  form.append("label", label);
  form.append("file", file);
  return api.post(`/floor-plans/site/${siteId}`, form);
};
export const deleteFloorPlan = (id: string) =>
  api.delete(`/floor-plans/${id}`);

// --- Locations ---
export const getAllLocations = () => api.get("/locations/");
export const getLocations = (floorPlanId: string) =>
  api.get(`/locations/floor-plan/${floorPlanId}`);
export const createLocation = (
  floorPlanId: string, data: object) =>
  api.post(`/locations/floor-plan/${floorPlanId}`, data);

// --- Sessions ---
export const getAllSessions = (siteId?: string) => 
  api.get(`/sessions/${siteId ? `?site_id=${siteId}` : ''}`);
export const getSessions = (locationId: string) =>
  api.get(`/sessions/location/${locationId}`);
export const uploadSession = (
  locationId: string, file: File, notes?: string, capturedAt?: string) => {
  const form = new FormData();
  form.append("file", file);
  if (notes) form.append("device_model", notes);
  if (capturedAt) form.append("captured_at", capturedAt);
  return api.post(`/sessions/location/${locationId}`, form);
};
export const compareSessions = (
  sessionA: string, sessionB: string) =>
  api.get(`/sessions/compare?session_a=${sessionA}&session_b=${sessionB}`);
export const deleteSession = (id: string) =>
  api.delete(`/sessions/${id}`);

// --- AI Features ---
export const detectChanges = (
  sessionA: string, sessionB: string) =>
  api.post(`/ai/change-detection?session_a_id=${sessionA}&session_b_id=${sessionB}`);
export const estimateProgress = (sessionId: string) =>
  api.post(`/ai/progress-estimation/${sessionId}`);
export const transcribeVoiceNote = (noteId: string) =>
  api.post(`/ai/transcribe/${noteId}`);
export const askSite = (siteId: string, question: string) =>
  api.post(`/ai/ask/${siteId}?question=${encodeURIComponent(question)}`);

// --- Annotations ---
export const getAnnotations = (sessionId: string) =>
  api.get(`/annotations/session/${sessionId}`);
export const createAnnotation = (
  sessionId: string, data: object) =>
  api.post(`/annotations/session/${sessionId}`, data);
export const resolveAnnotation = (annotationId: string) =>
  api.patch(`/annotations/${annotationId}/resolve`);

// --- Contractors ---
export const getContractors = () => api.get('/contractors/');
export const createContractor = (data: any) => api.post('/contractors/', data);
export const updateContractor = (id: string, data: any) => api.put(`/contractors/${id}`, data);
export const deleteContractor = (id: string) => api.delete(`/contractors/${id}`);

// --- Issues ---
export const getIssues = (status?: string, locationId?: string) => {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (locationId) params.append('location_id', locationId);
  const query = params.toString();
  return api.get(`/issues/${query ? `?${query}` : ''}`);
};
export const createIssue = (data: any) => api.post('/issues/', data);
export const getIssue = (id: string) => api.get(`/issues/${id}`);
export const updateIssue = (id: string, data: any) => api.put(`/issues/${id}`, data);
export const deleteIssue = (id: string) => api.delete(`/issues/${id}`);
export const assignContractorToIssue = (id: string, contractorId: string) => api.post(`/issues/${id}/assign`, { contractor_id: contractorId });
export const unassignContractorFromIssue = (id: string, contractorId: string) => api.delete(`/issues/${id}/assignments/${contractorId}`);
export const getIssueComments = (id: string) => api.get(`/issues/${id}/comments`);
export const addIssueComment = (id: string, comment_text: string) => api.post(`/issues/${id}/comments`, { comment_text });
