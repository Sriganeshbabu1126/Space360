import { render, screen, fireEvent } from '@testing-library/react';
import { PathVideoViewer } from '../PathVideoViewer';
import axios from 'axios';

jest.mock('axios');

describe('PathVideoViewer', () => {
  
  it('renders loading state', () => {
    (axios.get as jest.Mock).mockImplementation(() => new Promise(() => {}));
    
    render(<PathVideoViewer pathId="test-path" />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });
  
  it('displays correlations after loading', async () => {
    (axios.get as jest.Mock).mockImplementation((url) => {
      if (url.includes('/api/correlations/')) {
        return Promise.resolve({
          data: {
            correlations: [
              { id: '1', waypoint_id: 'wp1', frame_id: 'f1', confidence: 0.95, timestamp_offset_ms: 50 }
            ]
          }
        });
      }
      if (url.includes('/api/paths/')) {
        return Promise.resolve({
          data: {
            waypoints: [
              { id: 'wp1', timestamp: '2026-09-01T10:00:00Z', latitude: 1.352, longitude: 103.817 }
            ]
          }
        });
      }
      if (url.includes('/api/video-uploads?path_id')) {
        return Promise.resolve({
          data: [{ id: 'v1' }]
        });
      }
      if (url.includes('/api/video-uploads/')) {
        return Promise.resolve({
          data: {
            frames: [
              { id: 'f1', timestamp_seconds: 10, thumbnail_url: 'http://test/thumb.jpg' }
            ]
          }
        });
      }
      return Promise.resolve({ data: {} });
    });
    
    render(<PathVideoViewer pathId="test-path" />);
    
    await screen.findByText(/confidence/i);
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText(/1\.352000/)).toBeInTheDocument();
  });
});
