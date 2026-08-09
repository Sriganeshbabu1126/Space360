import sys
import uuid
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app.models import Issue, LocationPoint, IssueComment

db = SessionLocal()

# Get a location
loc = db.query(LocationPoint).first()
location_id = loc.id if loc else "test-loc-" + str(uuid.uuid4())[:8]

payloads = [
    {
        "title": "Exposed Wiring in Corridor B",
        "description": "Found some exposed electrical wiring near the ceiling panels in corridor B. This is a safety hazard and needs immediate attention before the drywall is closed up.",
        "location_id": location_id,
        "status": "open",
        "created_by": "wincadsg@gmail.com"
    },
    {
        "title": "HVAC Duct Misalignment",
        "description": "The main HVAC ducting in the server room is misaligned with the ceiling grid. Needs to be shifted approximately 4 inches to the left.",
        "location_id": location_id,
        "status": "in_review",
        "created_by": "wincadsg@gmail.com"
    }
]

for p in payloads:
    issue = Issue(id=str(uuid.uuid4()), **p)
    db.add(issue)
    # Add an initial comment
    comment = IssueComment(
        id=str(uuid.uuid4()),
        issue_id=issue.id,
        author="wincadsg@gmail.com",
        comment_text="Initial observation from the field capture."
    )
    db.add(comment)

db.commit()
print("Issues created in DB successfully.")
