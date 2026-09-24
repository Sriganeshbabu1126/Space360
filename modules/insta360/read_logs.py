from google.cloud import logging

client = logging.Client(project='space360-114433')
entries = client.list_entries(
    filter_='resource.type="cloud_run_revision" AND resource.labels.service_name="insta360-module"',
    order_by=logging.DESCENDING,
    max_results=200
)

for e in entries:
    if isinstance(e.payload, str) and 'stitch' in e.payload.lower():
        print(f"[{e.timestamp}] {e.payload}")
    elif isinstance(e.payload, dict) and 'message' in e.payload:
        msg = e.payload['message']
        if 'stitch' in msg.lower() or 'ffmpeg' in msg.lower():
            print(f"[{e.timestamp}] {msg}")
    elif isinstance(e.payload, str) and 'ffmpeg' in e.payload.lower():
        print(f"[{e.timestamp}] {e.payload}")
