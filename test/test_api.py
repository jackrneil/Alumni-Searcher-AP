import requests
import json
import time

# Test data in the format provided
test_data = [
    {
        "City": "",
        "Company": "",
        "Email": "",
        "Graduation Year": "",
        "Industry": "",
        "LinkedIn URL": "https://www.linkedin.com/in/williamhgates/",
        "Name": "Bill Gates"
    },
    {
        "City": "",
        "Company": "",
        "Email": "",
        "Graduation Year": "",
        "Industry": "",
        "LinkedIn URL": "https://www.linkedin.com/in/satyanadella/",
        "Name": "Satya Nadella"
    },
    {
        "City": "",
        "Company": "",
        "Email": "",
        "Graduation Year": "",
        "Industry": "",
        "LinkedIn URL": "",
        "Name": "John Doe"
    }
]

# API endpoint
base_url = "http://localhost:8000"

# Step 1: Submit the data
print("Submitting data to enrich...")
response = requests.post(
    f"{base_url}/api/enrich-alumni",
    json=test_data
)
response_data = response.json()
print(f"Response: {response_data}")

# Extract job ID
job_id = response_data.get("job_id")
if not job_id:
    print("No job_id returned")
    exit(1)

# Step 2: Poll for job completion
print(f"Polling for job {job_id}...")
status = "pending"
while status != "done":
    print("Checking job status...")
    response = requests.get(f"{base_url}/jobs/{job_id}")
    status_data = response.json()
    status = status_data.get("status", "")
    print(f"Status: {status}")
    
    if status == "error":
        print(f"Job failed: {status_data.get('message', 'Unknown error')}")
        exit(1)
    
    if status != "done":
        print("Waiting 5 seconds...")
        time.sleep(5)

# Step 3: Get results
print("Job complete! Getting results...")
response = requests.get(f"{base_url}/jobs/{job_id}/result")
results = response.json()

print("\nEnriched Data:")
print(json.dumps(results, indent=2))

print(f"\nDownload Excel: {base_url}/jobs/{job_id}/download") 