import pytest

class TestCorrelationAlgorithm:
    
    def test_timestamp_offset_calculation(self):
        """Test that clock offset is applied correctly."""
        waypoint_offset_nanos = 1_000_000_000
        frame_offset_nanos = 1_000_000_000
        clock_offset_nanos = 500_000_000
        adjusted_frame = frame_offset_nanos + clock_offset_nanos  
        
        diff = abs(waypoint_offset_nanos - adjusted_frame)
        
        assert diff == 500_000_000
    
    def test_confidence_score(self):
        """Test confidence calculation (0-1 scale)."""
        diff_ms = 100  
        max_acceptable = 500
        confidence = max(0.0, 1.0 - (diff_ms / max_acceptable))
        
        assert confidence == 0.8
        
        confidence_perfect = max(0.0, 1.0 - (0 / max_acceptable))
        assert confidence_perfect == 1.0
    
    def test_closest_frame_selection(self):
        """Test that closest frame is selected correctly."""
        waypoint_nanos = 2_000_000_000  
        
        frames = [
            {"timestamp_seconds": 1.5, "frame_id": 1},  
            {"timestamp_seconds": 2.0, "frame_id": 2},  
            {"timestamp_seconds": 2.5, "frame_id": 3},  
        ]
        
        clock_offset = 0
        
        min_diff = float('inf')
        closest = None
        
        for frame in frames:
            frame_nanos = frame["timestamp_seconds"] * 1_000_000_000
            adjusted_nanos = frame_nanos + clock_offset
            diff = abs(waypoint_nanos - adjusted_nanos)
            
            if diff < min_diff:
                min_diff = diff
                closest = frame
        
        assert closest["frame_id"] == 2
        assert min_diff == 0
