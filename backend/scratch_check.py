import os
from google.cloud import firestore

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'F:/Space360/backend/firebase-service-account.json'
db = firestore.Client(project='space360-114433')

job_id = '049eab84-a345-4776-be4b-8f3ec79f3bcc'
doc = db.collection('jobs').document(job_id).get()

if doc.exists:
    print(doc.to_dict())
else:
    print('Job not found.')
