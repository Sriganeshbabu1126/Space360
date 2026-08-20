import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# We will use Redis as the broker and result backend
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_BACKEND_URL = os.getenv("REDIS_BACKEND_URL", "redis://localhost:6379/1")

celery_app = Celery(
    "space360_celery",
    broker=REDIS_URL,
    backend=REDIS_BACKEND_URL,
    include=["app.worker"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
