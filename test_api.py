
import requests
import json
import datetime

url = 'http://localhost:8000/api/paths/'
headers = {'Content-Type': 'application/json'}
payload = {
    'site_id': 'test-site',
    'user_id': 'test-user',
    'started_at': '2026-09-02T10:45:00.123Z',
    'ended_at': '2026-09-02T10:46:00.123Z',
    'waypoint_count': 0,
    'waypoints': []
}

try:
    response = requests.post(url, json=payload, headers=headers)
    print(response.status_code)
    print(response.text)
except Exception as e:
    print('Error:', e)

