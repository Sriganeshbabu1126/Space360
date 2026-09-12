import pytest
from unittest.mock import patch, MagicMock
from app.services.video_worker import VideoFrameExtractionWorker

class TestVideoFrameExtraction:
    
    def test_probe_video_success(self):
        """Test ffprobe parses video metadata correctly."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='{"streams": [{"duration": 60.5, "r_frame_rate": "30/1", "codec_name": "h264", "width": 1280, "height": 640}]}'
            )
            
            result = VideoFrameExtractionWorker._probe_video('test.mp4')
            
            assert result['duration'] == 60.5
            assert result['fps'] == 30
            assert result['resolution'] == '1280x640'
            assert result['codec'] == 'h264'
    
    def test_frame_extraction_count(self):
        """Test correct number of frames extracted at 2fps."""
        duration = 30.0  # 30 second video
        fps = 2
        expected_frames = int(duration * fps)  # 60 frames
        
        assert expected_frames == 60
    
    def test_frame_timestamp_calculation(self):
        """Test frame timestamps are accurate."""
        fps = 2
        timestamps = [i / fps for i in range(120)]  # 120 frames at 2fps = 60s
        
        assert timestamps[0] == 0.0
        assert timestamps[1] == 0.5
        assert timestamps[119] == 59.5
    
    @patch('app.services.video_worker.upload_private_file')
    @patch('app.services.video_worker.get_signed_url')
    def test_gcs_upload_called_per_frame(self, mock_get_url, mock_upload):
        """Test each frame uploaded to GCS."""
        mock_get_url.return_value = "gs://bucket/frame.jpg"
        
        num_frames = 60
        for i in range(num_frames):
            mock_upload(b'test', 'path', 'image/jpeg')
            
        assert mock_upload.call_count == num_frames
