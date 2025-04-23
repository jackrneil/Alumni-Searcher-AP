# Bubble API Connector Setup

This guide explains how to set up the API Connector in Bubble to integrate with your FastAPI backend for the Alumni Searcher.

## 1. Install the API Connector Plugin

1. In the Bubble editor, go to **Plugins** → **Add plugins**
2. Search for "API Connector" and click **Install**

## 2. Create a New API

1. Go to **Plugins** → **API Connector**
2. Click **Add another API**
3. Name: "AlumniSearchAPI"
4. Authentication: "None or self-handled"

## 3. Add Shared Headers (if needed)

1. Add a shared header:
   - Key: "Content-Type"
   - Value: "application/json"

## 4. Define API Calls

### Call 1: "Enrich Alumni List"

This call will send your alumni data to be enriched with LinkedIn data.

- **Method**: POST
- **URL**: https://your-backend-url/api/enrich-alumni
- **Headers**: (shared headers will be used)
- **Body Type**: JSON
- **Body**: (the array of alumni entries from your data table)
- **Use as**: Action

### Call 2: "Check Job Status"

This call checks the status of an enrichment job.

- **Method**: GET
- **URL**: https://your-backend-url/jobs/[job_id]
- **Parameters**:
  - job_id: (the job_id you received from the first call)
- **Use as**: Action

### Call 3: "Get Job Results"

This call retrieves the enriched data once the job is complete.

- **Method**: GET
- **URL**: https://your-backend-url/jobs/[job_id]/result
- **Parameters**:
  - job_id: (the job_id you received from the first call)
- **Use as**: Action
- **Expected Return Type**: Array

### Call 4: "Download Enriched Excel"

This call provides a download link for the enriched Excel file.

- **Method**: GET
- **URL**: https://your-backend-url/jobs/[job_id]/download
- **Parameters**:
  - job_id: (the job_id you received from the first call)
- **Use as**: Data

## 5. Using the API with Your Data Table

Here's how to use the API with the data table example you provided:

```json
[
  {
    "City": "",
    "Company": "",
    "Email": "",
    "Graduation Year": "",
    "Industry": "",
    "LinkedIn URL": "",
    "Name": "kyle"
  },
  {
    "City": "",
    "Company": "",
    "Email": "",
    "Graduation Year": "",
    "Industry": "",
    "LinkedIn URL": "",
    "Name": "mark"
  },
  {
    "City": "",
    "Company": "",
    "Email": "",
    "Graduation Year": "",
    "Industry": "",
    "LinkedIn URL": "",
    "Name": "john"
  }
]
```

### Workflow Steps:

1. **Get your data into the correct format**:
   - Ensure your data table has at least a "LinkedIn URL" column
   - All fields shown in your example will be preserved
   
2. **Create a new page in Bubble**:
   - Add a Repeating Group to show your alumni data
   - Add buttons for "Enrich Data" and "Download Results"
   
3. **Set up the Enrichment workflow**:
   - When the "Enrich Data" button is clicked:
   - Call "Enrich Alumni List" with your data table as the body
   - Store the returned job_id in a page or app state variable
   - Start a polling process to check job status

4. **Set up the polling workflow**:
   - Create a custom event that polls every few seconds
   - Call "Check Job Status" with the stored job_id
   - If status is "done", call "Get Job Results"
   - Update your data table or repeating group with the enriched data
   - If status is still "processing", schedule the custom event again

5. **Display and download results**:
   - When the "Download Results" button is clicked:
   - Open a new browser window with the URL from "Download Enriched Excel"
     (https://your-backend-url/jobs/job_id/download)

## 6. Example Bubble Workflow

Here's a pseudo-code example of the Bubble workflow:

```
Event: When "Enrich Data" button is clicked
Action 1: API Connector → Enrich Alumni List (body: table data)
Action 2: Set State → Page state job_id = result's job_id
Action 3: Start polling (Trigger Custom Event: CheckJobStatus)

Custom Event: CheckJobStatus
Action 1: API Connector → Check Job Status (job_id: page's job_id)
Condition: status = "done"
    Yes: API Connector → Get Job Results
         Update Repeating Group (or save to database)
         Show Success Message
    No:  Schedule Custom Event (CheckJobStatus) - wait 5 seconds
```

## 7. Troubleshooting

If you encounter issues:

1. **API calls failing**: Check your backend URL and make sure it's accessible
2. **CORS errors**: Verify that your backend's ALLOWED_ORIGIN includes your Bubble app URL
3. **Empty results**: Make sure your LinkedIn URLs are valid and in the correct format
4. **Data not updating**: Check that you're correctly updating the Bubble data after receiving enriched results 