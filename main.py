from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import os
import uuid
import asyncio
import httpx
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("ALLOWED_ORIGIN")],
    allow_methods=["*"],
    allow_headers=["*"],
)

RAPID_HEADERS = {
    "X-RapidAPI-Key": os.getenv("RAPID_KEY"),
    "X-RapidAPI-Host": os.getenv("RAPID_HOST")
}

JOB_DIR = "jobs"
os.makedirs(JOB_DIR, exist_ok=True)

def read_excel(content: bytes) -> pd.DataFrame:
    df = pd.read_excel(io.BytesIO(content))
    if "LinkedIn URL" not in df.columns:
        raise HTTPException(400, "Column 'LinkedIn URL' required")
    return df

async def enrich_profile(url: str, client: httpx.AsyncClient) -> dict:
    """Extract LinkedIn profile data using the RapidAPI endpoint"""
    try:
        # Extract LinkedIn public ID from the URL
        # Format could be: https://www.linkedin.com/in/username/
        parts = url.strip().split('/')
        if 'linkedin.com' not in url:
            return {"linkedinURL": url, "error": "Not a valid LinkedIn URL"}
        
        public_id = None
        for i, part in enumerate(parts):
            if part == "in" and i + 1 < len(parts) and parts[i + 1]:
                public_id = parts[i + 1].split('?')[0]  # Remove any query params
                break
        
        if not public_id:
            return {"linkedinURL": url, "error": "Could not extract profile ID"}
            
        # Call the RapidAPI endpoint to get profile data
        api_url = f"https://{os.getenv('RAPID_HOST')}/get-profile"
        params = {"linkedin_url": url}
        response = await client.get(api_url, headers=RAPID_HEADERS, params=params)
        
        if response.status_code != 200:
            return {
                "linkedinURL": url,
                "error": f"API error: {response.status_code}"
            }
            
        data = response.json()
        
        # Extract the relevant fields from the API response
        return {
            "linkedinURL": url,
            "firstName": data.get("first_name", ""),
            "lastName": data.get("last_name", ""),
            "email": "",  # LinkedIn API doesn't provide emails
            "company": data.get("experiences", [{}])[0].get("company", "") if data.get("experiences") else "",
            "industry": data.get("industry", ""),
            "city": data.get("city", ""),
            "current_title": data.get("headline", ""),
        }
    except Exception as e:
        return {
            "linkedinURL": url,
            "error": f"Error: {str(e)}"
        }

async def process_job(job_id, path_raw):
    """Process a job in the background"""
    try:
        # Read Excel file
        df = read_excel(open(path_raw, "rb").read())
        
        # Process each LinkedIn URL
        async with httpx.AsyncClient() as client:
            tasks = []
            for _, row in df.iterrows():
                linkedin_url = row.get("LinkedIn URL", "")
                # Include original row data to preserve it
                original_data = row.to_dict()
                if linkedin_url:
                    task = enrich_profile_with_original(linkedin_url, original_data, client)
                    tasks.append(task)
                else:
                    # If no LinkedIn URL, keep the original data as is
                    tasks.append(asyncio.create_task(asyncio.to_thread(lambda: original_data)))
            
            # Wait for all tasks to complete
            enriched_rows = await asyncio.gather(*tasks)
        
        # Create a new DataFrame with enriched data
        enriched_df = pd.DataFrame(enriched_rows)
        
        # Save enriched data to Excel
        output_path = f"{JOB_DIR}/{job_id}_enriched.xlsx"
        enriched_df.to_excel(output_path, index=False)
        
        # Update job status
        with open(f"{JOB_DIR}/{job_id}.json", "w") as fp:
            json.dump({"status": "done"}, fp)
            
    except Exception as e:
        # Update job status with error
        with open(f"{JOB_DIR}/{job_id}.json", "w") as fp:
            json.dump({"status": "error", "message": str(e)}, fp)

async def enrich_profile_with_original(url: str, original_data: dict, client: httpx.AsyncClient) -> dict:
    """Enrich profile data while preserving original fields"""
    if not url:
        return original_data
        
    try:
        # Extract LinkedIn public ID from the URL
        # Format could be: https://www.linkedin.com/in/username/
        parts = url.strip().split('/')
        if 'linkedin.com' not in url:
            original_data["error"] = "Not a valid LinkedIn URL"
            return original_data
        
        public_id = None
        for i, part in enumerate(parts):
            if part == "in" and i + 1 < len(parts) and parts[i + 1]:
                public_id = parts[i + 1].split('?')[0]  # Remove any query params
                break
        
        if not public_id:
            original_data["error"] = "Could not extract profile ID"
            return original_data
            
        # Call the RapidAPI endpoint to get profile data
        api_url = f"https://{os.getenv('RAPID_HOST')}/get-profile"
        params = {"linkedin_url": url}
        response = await client.get(api_url, headers=RAPID_HEADERS, params=params)
        
        if response.status_code != 200:
            original_data["error"] = f"API error: {response.status_code}"
            return original_data
            
        data = response.json()
        
        # Update original data with enriched fields but don't overwrite existing values
        if not original_data.get("Name") and (data.get("first_name") or data.get("last_name")):
            original_data["Name"] = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
            
        if not original_data.get("Company") and data.get("experiences"):
            original_data["Company"] = data.get("experiences", [{}])[0].get("company", "")
            
        if not original_data.get("Industry"):
            original_data["Industry"] = data.get("industry", "")
            
        if not original_data.get("City"):
            original_data["City"] = data.get("city", "")
        
        # Always add these fields
        if "firstName" not in original_data:
            original_data["firstName"] = data.get("first_name", "")
        if "lastName" not in original_data:
            original_data["lastName"] = data.get("last_name", "")
        if "current_title" not in original_data:
            original_data["current_title"] = data.get("headline", "")
        
        return original_data
    except Exception as e:
        original_data["error"] = f"Error: {str(e)}"
        return original_data

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok"}

@app.post("/jobs")
async def create_job(background_tasks: BackgroundTasks,
                    file: UploadFile = File(...)):
    """Upload Excel with LinkedIn URLs and start enrichment job"""
    job_id = str(uuid.uuid4())
    path_raw = f"{JOB_DIR}/{job_id}_raw.xlsx"
    
    # Save uploaded file
    with open(path_raw, "wb") as f:
        f.write(await file.read())

    # Start background processing
    background_tasks.add_task(process_job, job_id, path_raw)
    
    return {"job_id": job_id, "status": "pending"}

@app.get("/jobs/{job_id}")
def job_status(job_id: str):
    """Check status of a job"""
    meta_path = f"{JOB_DIR}/{job_id}.json"
    
    if not os.path.exists(meta_path):
        return {"status": "processing"}
        
    with open(meta_path, "r") as f:
        meta = json.load(f)
    
    return meta

@app.get("/jobs/{job_id}/result")
def job_result(job_id: str):
    """Get results of a completed job"""
    excel_path = f"{JOB_DIR}/{job_id}_enriched.xlsx"
    
    if not os.path.exists(excel_path):
        raise HTTPException(404, "Job results not found")
        
    df = pd.read_excel(excel_path)
    return df.to_dict(orient="records")

@app.get("/jobs/{job_id}/download")
def job_download(job_id: str):
    """Download enriched Excel file"""
    excel_path = f"{JOB_DIR}/{job_id}_enriched.xlsx"
    
    if not os.path.exists(excel_path):
        raise HTTPException(404, "Job results not found")
        
    return FileResponse(
        excel_path, 
        filename="enriched_alumni.xlsx",
        media_type="application/vnd.ms-excel"
    )

@app.post("/api/enrich")
async def enrich_list(background_tasks: BackgroundTasks, data: List[Dict[str, Any]]):
    """Enrich a list of alumni entries directly from JSON"""
    job_id = str(uuid.uuid4())
    
    # Create a temporary DataFrame from the JSON data
    df = pd.DataFrame(data)
    
    # Save to temporary Excel file
    path_raw = f"{JOB_DIR}/{job_id}_raw.xlsx"
    df.to_excel(path_raw, index=False)
    
    # Start background processing
    background_tasks.add_task(process_job, job_id, path_raw)
    
    return {"job_id": job_id, "status": "pending"}

@app.post("/api/enrich-alumni")
async def enrich_alumni(background_tasks: BackgroundTasks, data: List[Dict[str, Any]]):
    """Enrich a list of alumni entries from the specific format provided"""
    job_id = str(uuid.uuid4())
    
    # Process the input data to ensure correct format
    processed_data = []
    for entry in data:
        # Process each alumni entry
        # Convert keys to match required format if needed
        processed_entry = {}
        for key, value in entry.items():
            # Ensure LinkedIn URL key is consistent
            if key.lower() in ["linkedin url", "linkedinurl", "linkedin_url"]:
                processed_entry["LinkedIn URL"] = value
            else:
                processed_entry[key] = value
                
        # If Name is provided but no LinkedIn URL, we might need to add LinkedIn URL later
        processed_data.append(processed_entry)
    
    # Create DataFrame from processed data
    df = pd.DataFrame(processed_data)
    
    # Save to temporary Excel file
    path_raw = f"{JOB_DIR}/{job_id}_raw.xlsx"
    df.to_excel(path_raw, index=False)
    
    # Start background processing
    background_tasks.add_task(process_alumni, job_id, path_raw)
    
    return {"job_id": job_id, "status": "pending"}

async def process_alumni(job_id, path_raw):
    """Process alumni job with special handling for names without LinkedIn URLs"""
    try:
        # Read Excel file
        df = read_excel(open(path_raw, "rb").read())
        
        # Process each entry
        async with httpx.AsyncClient() as client:
            tasks = []
            for _, row in df.iterrows():
                linkedin_url = row.get("LinkedIn URL", "")
                name = row.get("Name", "")
                original_data = row.to_dict()
                
                if linkedin_url:
                    # If LinkedIn URL exists, enrich directly
                    task = enrich_profile_with_original(linkedin_url, original_data, client)
                    tasks.append(task)
                elif name:
                    # If only name exists, we could try to find the LinkedIn URL
                    # This is a placeholder for potential future enhancement
                    # For now, we'll just return the original data
                    tasks.append(asyncio.create_task(asyncio.to_thread(lambda: original_data)))
                else:
                    # If neither LinkedIn URL nor name, just return original
                    tasks.append(asyncio.create_task(asyncio.to_thread(lambda: original_data)))
            
            # Wait for all tasks to complete
            enriched_rows = await asyncio.gather(*tasks)
        
        # Create a new DataFrame with enriched data
        enriched_df = pd.DataFrame(enriched_rows)
        
        # Save enriched data to Excel
        output_path = f"{JOB_DIR}/{job_id}_enriched.xlsx"
        enriched_df.to_excel(output_path, index=False)
        
        # Update job status
        with open(f"{JOB_DIR}/{job_id}.json", "w") as fp:
            json.dump({"status": "done"}, fp)
            
    except Exception as e:
        # Update job status with error
        with open(f"{JOB_DIR}/{job_id}.json", "w") as fp:
            json.dump({"status": "error", "message": str(e)}, fp) 