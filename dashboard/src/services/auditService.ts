import { db } from './firebase';
import { collection, addDoc, serverTimestamp } from 'firebase/firestore';

export const logAuditAction = async (
  userId: string,
  action: string,
  resourceType: string,
  resourceId: string,
  resourceName: string,
  projectId: string,
  details?: Record<string, any>
) => {
  try {
    await addDoc(collection(db, 'audit_logs'), {
      timestamp: serverTimestamp(),
      user_id: userId,
      action: action,
      resource_type: resourceType,
      resource_id: resourceId,
      resource_name: resourceName,
      project_id: projectId,
      details: details || {},
      ip_address: 'client-side',
      status: 'SUCCESS',
    });
  } catch (error) {
    console.error('Failed to log audit action:', error);
  }
};
