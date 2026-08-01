import axios from 'axios';

const CAMERA_URL = 'http://192.168.0.1:6624';

export interface CameraInfo {
  manufacturer: string;
  model: string;
  firmwareVersion: string;
  serialNumber: string;
}

export interface CameraFile {
  fileUrl: string;
  thumbnail?: string;
  dateTimeZone?: string;
  width?: number;
  height?: number;
  fileSize?: number;
}

export const checkCameraConnection = async (): Promise<boolean> => {
  try {
    const res = await axios.get(`${CAMERA_URL}/osc/info`, { timeout: 3000 });
    return res.status === 200;
  } catch (error) {
    return false;
  }
};

export const getCameraInfo = async (): Promise<CameraInfo> => {
  const res = await axios.get(`${CAMERA_URL}/osc/info`);
  return res.data;
};

const pollStatus = async (commandId: string): Promise<any> => {
  while (true) {
    const res = await axios.post(`${CAMERA_URL}/osc/commands/status`, {
      id: commandId
    });
    const { state, results, error } = res.data;
    if (state === 'done') {
      return results;
    }
    if (state === 'error') {
      throw new Error(error?.message || 'Command failed');
    }
    // Wait 500ms before polling again
    await new Promise(resolve => setTimeout(resolve, 500));
  }
};

export const takePicture = async (): Promise<string> => {
  const res = await axios.post(`${CAMERA_URL}/osc/commands/execute`, {
    name: 'camera.takePicture'
  });
  
  const state = res.data.state;
  if (state === 'done') {
    return res.data.results.fileUrl;
  } else if (state === 'inProgress') {
    const results = await pollStatus(res.data.id);
    return results.fileUrl;
  }
  
  throw new Error('Failed to take picture');
};

export const listFiles = async (): Promise<CameraFile[]> => {
  const res = await axios.post(`${CAMERA_URL}/osc/commands/execute`, {
    name: 'camera.listFiles',
    parameters: {
      fileType: 'image',
      entryCount: 10,
      maxThumbSize: 100
    }
  });
  
  if (res.data.state === 'done') {
    return res.data.results.entries;
  } else {
    const results = await pollStatus(res.data.id);
    return results.entries;
  }
};

export const downloadFile = async (fileUrl: string): Promise<Blob> => {
  const res = await axios.get(fileUrl, {
    responseType: 'blob'
  });
  return res.data;
};

export const takeAndDownload = async (): Promise<File> => {
  const fileUrl = await takePicture();
  const blob = await downloadFile(fileUrl);
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  return new File([blob], `space360_${timestamp}.jpg`, { type: 'image/jpeg' });
};
