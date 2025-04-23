# LinkedIn Alumni Searcher API

A FastAPI backend for enriching LinkedIn profiles from a Bubble app.

## Features

- Enrich LinkedIn profiles with data from the LinkedIn API
- Process individual profiles or batches via Excel uploads
- Easy integration with Bubble apps

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your RapidAPI credentials:

```
RAPID_KEY=your_rapidapi_key
RAPID_HOST=fresh-linkedin-profile-data.p.rapidapi.com
ALLOWED_ORIGIN=https://your-bubble-app.bubbleapps.io
```

## Running Locally

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000/docs

## API Endpoints

- `POST /api/enrich-profile`: Directly enrich a single LinkedIn profile
- `POST /api/enrich-alumni`: Enrich a list of alumni profiles
- `POST /jobs`: Upload an Excel file for batch processing
- `GET /jobs/{job_id}`: Check job status
- `GET /jobs/{job_id}/result`: Get job results
- `GET /jobs/{job_id}/download`: Download enriched Excel file

## Deployment

This API is ready to deploy on Render.com, Heroku, or any other platform that supports Python. 