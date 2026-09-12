# Insta360 X4 Video Handling Module

This is a standalone Python module designed for the Space360 project. It handles the ingestion, processing, and uploading of 360° video files from Insta360 X4 cameras.

## Relationship to Space360
This module is being developed as a standalone component. It will later be integrated into the main Space360 platform as a pluggable input handler for 360-degree field inspection videos.

## Folder Structure Overview

- `api/`: FastAPI application for ingestion endpoints.
- `core/`: Core business logic (camera interaction, stitching, metadata, validation, upload).
- `sdk/`: Contains Insta360 SDK repositories (C++ Desktop, Android, iOS, etc.). Do not modify directly.
- `sdk_bridge/`: Python wrappers for the C++ SDK calls.
- `tests/`: Unit and integration tests.
- `output/`: Local staging area for processed files (ignored by git).
- `logs/`: Application logs (ignored by git).

## Setup Instructions

### Requirements
- Python 3.11+
- Discrete GPU (Required for MediaSDK operations)
- Insta360 X4 firmware update to enable Android mode for USB control (Required for CameraSDK)

### Installation
1. Ensure Python 3.11+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure the necessary environment variables:
   ```bash
   cp .env.example .env
   ```

### Running the API Server Locally
To run the FastAPI server locally in development mode:
```bash
uvicorn api.main:app --reload
```
