import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './PathVideoViewer.css';

interface Correlation {
  id: string;
  path_id: string;
  waypoint_id: string;
  frame_id: string;
  timestamp_offset_ms: number;
  confidence: number;
  created_at: string;
}

interface CorrelationResponse {
  path_id: string;
  correlation_count: number;
  correlations: Correlation[];
}

interface Waypoint {
  id: string;
  latitude: number;
  longitude: number;
  timestamp: string;  
  altitude?: number;
}

interface VideoFrame {
  id: string;
  timestamp_seconds: number;
  thumbnail_url: string;
}

interface Props {
  pathId: string;
}

export const PathVideoViewer: React.FC<Props> = ({ pathId }) => {
  const [correlations, setCorrelations] = useState<Correlation[]>([]);
  const [waypoints, setWaypoints] = useState<Waypoint[]>([]);
  const [frames, setFrames] = useState<VideoFrame[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // UI State
  const [selectedWaypoint, setSelectedWaypoint] = useState<number>(0);  // index
  const [currentTime, setCurrentTime] = useState(0);  // seconds
  const [sortColumn, setSortColumn] = useState<'time' | 'confidence'>('time');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  
  // Fetch correlations on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch correlations
        const corrRes = await axios.get<CorrelationResponse>(
          `http://localhost:8000/api/correlations/${pathId}`
        );
        setCorrelations(corrRes.data.correlations);
        
        // Fetch path waypoints
        const pathRes = await axios.get(`http://localhost:8000/api/paths/${pathId}`);
        setWaypoints(pathRes.data.waypoints || []);
        
        // Fetch video frames (via video_id lookup)
        const videoRes = await axios.get(`http://localhost:8000/api/video-uploads?path_id=${pathId}`);
        if (videoRes.data.length > 0) {
          const videoId = videoRes.data[0].id;
          const framesRes = await axios.get(`http://localhost:8000/api/video-uploads/${videoId}`);
          setFrames(framesRes.data.frames || []);
        }
        
        setError(null);
      } catch (err) {
        setError(`Failed to load path data`);
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    if (pathId) {
      fetchData();
    }
  }, [pathId]);
  
  // Get current waypoint based on timeline position
  const getCurrentWaypoint = () => {
    const corr = correlations[selectedWaypoint];
    const wp = waypoints[selectedWaypoint];
    const frame = frames.find(f => f.id === corr?.frame_id);
    
    if (!corr || !wp || !frame) return null;
    return { waypoint: wp, correlation: corr, frame };
  };
  
  const getWaypointTime = (timestamp: string): number => {
     if (waypoints.length === 0) return 0;
     const start = new Date(waypoints[0].timestamp).getTime();
     const current = new Date(timestamp).getTime();
     return (current - start) / 1000;
  };

  // Handle timeline scrub
  const handleTimelineChange = (time: number) => {
    setCurrentTime(time);
    
    // Find closest waypoint to this time
    let closestIdx = 0;
    let minDiff = Infinity;
    
    waypoints.forEach((wp, idx) => {
      const wpTime = getWaypointTime(wp.timestamp);
      const diff = Math.abs(wpTime - time);
      if (diff < minDiff) {
        minDiff = diff;
        closestIdx = idx;
      }
    });
    
    setSelectedWaypoint(closestIdx);
  };
  
  // Sort correlations
  const getSortedCorrelations = (): Correlation[] => {
    const sorted = [...correlations];
    sorted.sort((a, b) => {
      let aVal: number;
      let bVal: number;
      
      if (sortColumn === 'time') {
        aVal = a.timestamp_offset_ms;
        bVal = b.timestamp_offset_ms;
      } else {
        aVal = a.confidence;
        bVal = b.confidence;
      }
      
      return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    });
    
    return sorted;
  };
  
  // Render
  if (loading) return <div className="path-video-viewer loading">Loading path data...</div>;
  if (error) return <div className="path-video-viewer error">{error}</div>;
  if (!pathId) return <div className="path-video-viewer error">No path ID provided</div>;
  if (correlations.length === 0) return <div className="path-video-viewer error">No correlations found for this path.</div>;
  
  const current = getCurrentWaypoint();
  const sorted = getSortedCorrelations();
  const videoDuration = frames.length > 0 ? frames[frames.length - 1].timestamp_seconds : 60;
  
  return (
    <div className="path-video-viewer">
      <h2>Path + Video Viewer</h2>
      
      {/* Frame + Location Display */}
      {current && (
        <div className="current-display">
          <div className="frame-display">
            <img src={current.frame.thumbnail_url} alt="Frame" />
            <div className="frame-info">
              <div>Frame at {current.frame.timestamp_seconds.toFixed(1)}s</div>
              <div>Confidence: {(current.correlation.confidence * 100).toFixed(0)}%</div>
              <div>Offset: {current.correlation.timestamp_offset_ms}ms</div>
            </div>
          </div>
          
          <div className="location-display">
            <div>📍 GPS Location</div>
            <div className="coords">
              {current.waypoint.latitude.toFixed(6)}°N<br />
              {current.waypoint.longitude.toFixed(6)}°E
            </div>
            <div>Accuracy: ±5m</div>
            <div className="altitude">
              Alt: {(current.waypoint.altitude || 0).toFixed(1)}m
            </div>
          </div>
        </div>
      )}
      
      {/* Timeline Scrubber */}
      <div className="timeline-section">
        <input
          type="range"
          min="0"
          max={videoDuration}
          step="0.5"
          value={currentTime}
          onChange={(e) => handleTimelineChange(parseFloat(e.target.value))}
          className="timeline-scrubber"
        />
        <div className="timeline-labels">
          <span>0s</span>
          <span>{(videoDuration / 2).toFixed(1)}s</span>
          <span>{videoDuration.toFixed(1)}s</span>
        </div>
      </div>
      
      {/* Waypoint List */}
      <div className="waypoints-table">
        <h3>Waypoints ({correlations.length} total)</h3>
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>Time</th>
              <th>GPS Coords</th>
              <th
                onClick={() => {
                  if (sortColumn === 'confidence') {
                    setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
                  } else {
                    setSortColumn('confidence');
                    setSortDirection('desc');
                  }
                }}
                style={{ cursor: 'pointer' }}
              >
                Confidence {sortColumn === 'confidence' ? (sortDirection === 'asc' ? '↑' : '↓') : ''}
              </th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((corr, idx) => {
              const wpIndex = waypoints.findIndex(w => w.id === corr.waypoint_id);
              const wp = waypoints[wpIndex];
              if (!wp) return null;
              
              const wpTime = getWaypointTime(wp.timestamp);
              
              return (
                <tr key={corr.id} className={selectedWaypoint === wpIndex ? 'active' : ''}>
                  <td>{wpIndex + 1}</td>
                  <td>{wpTime.toFixed(1)}s</td>
                  <td>
                    {wp.latitude.toFixed(4)}°, {wp.longitude.toFixed(4)}°
                  </td>
                  <td>{(corr.confidence * 100).toFixed(0)}%</td>
                  <td>
                    <button
                      onClick={() => {
                        setSelectedWaypoint(wpIndex);
                        setCurrentTime(wpTime);
                      }}
                      className="view-btn"
                    >
                      View
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      
      {/* Summary Stats */}
      <div className="summary-stats">
        <div>Total Waypoints: {correlations.length}</div>
        <div>Avg Confidence: {(correlations.reduce((sum, c) => sum + c.confidence, 0) / correlations.length * 100).toFixed(0)}%</div>
        <div>Max Offset: {Math.max(...correlations.map(c => c.timestamp_offset_ms))}ms</div>
      </div>
    </div>
  );
};
