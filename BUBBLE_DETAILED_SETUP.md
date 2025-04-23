# Detailed Guide: Integrating Alumni Searcher with Bubble

This guide provides detailed step-by-step instructions for integrating your FastAPI Alumni Searcher backend with a Bubble.io application.

## Prerequisites

1. A paid Bubble.io account (Personal plan or higher)
2. The FastAPI backend running and accessible (either locally or deployed)
3. Your RapidAPI key for the LinkedIn Profile Data API

## Step 1: Create a Data Type in Bubble

1. Open your Bubble app editor
2. Navigate to **Data** tab → **Data Types**
3. Click **Add a new type**
4. Name it "Alumni"
5. Add the following fields:
   - `firstName` (Text)
   - `lastName` (Text)
   - `Name` (Text)
   - `Email` (Text)
   - `Company` (Text)
   - `Industry` (Text)
   - `City` (Text)
   - `LinkedIn URL` (Text)
   - `Graduation Year` (Text)
   - `current_title` (Text)
   - `job_id` (Text) - This will store the job ID for enrichment
   - `enriched` (Yes/No) - This will track if the profile has been enriched

[IMAGE PLACEHOLDER: Screenshot of Bubble Data Type setup]

## Step 2: Install API Connector Plugin

1. In the Bubble editor, go to **Plugins** → **Add plugins**
2. Search for "API Connector"
3. Click **Install**

[IMAGE PLACEHOLDER: Screenshot of API Connector installation]

## Step 3: Configure API Connector

1. Go to **Plugins** → **API Connector** in the left sidebar
2. Click **Add another API**
3. Enter API Name: "AlumniSearchAPI"
4. Authentication: "None or self-handled"
5. Add a shared header:
   - Key: "Content-Type"
   - Value: "application/json"

[IMAGE PLACEHOLDER: Screenshot of API setup]

## Step 4: Define API Calls

### API Call 1: Enrich Alumni List

1. Click **Add another call**
2. Name: "Enrich Alumni List"
3. Method: POST
4. URL: `https://your-backend-url/api/enrich-alumni`
5. Headers: (shared headers will be used)
6. Body Type: JSON
7. Use as: Action
8. Initialize call with test data:
```json
[
  {
    "City": "",
    "Company": "",
    "Email": "",
    "Graduation Year": "",
    "Industry": "",
    "LinkedIn URL": "https://www.linkedin.com/in/williamhgates/",
    "Name": "Bill Gates"
  }
]
```

[IMAGE PLACEHOLDER: Screenshot of Enrich Alumni API call setup]

### API Call 2: Check Job Status

1. Click **Add another call**
2. Name: "Check Job Status"
3. Method: GET
4. URL: `https://your-backend-url/jobs/[job_id]`
5. Parameters:
   - job_id: (parameter)
6. Use as: Action

[IMAGE PLACEHOLDER: Screenshot of Job Status API call setup]

### API Call 3: Get Job Results

1. Click **Add another call**
2. Name: "Get Job Results" 
3. Method: GET
4. URL: `https://your-backend-url/jobs/[job_id]/result`
5. Parameters:
   - job_id: (parameter)
6. Use as: Action
7. Expected Return Type: Array

[IMAGE PLACEHOLDER: Screenshot of Get Results API call setup]

### API Call 4: Download Enriched Excel

1. Click **Add another call**
2. Name: "Download Enriched Excel"
3. Method: GET
4. URL: `https://your-backend-url/jobs/[job_id]/download`
5. Parameters:
   - job_id: (parameter)
6. Use as: Data

[IMAGE PLACEHOLDER: Screenshot of Download Excel API call setup]

## Step 5: Design the Alumni Enrichment Page

1. Create a new page named "Alumni Enrichment"
2. Add a Repeating Group:
   - Type of content: Alumni
   - Layout: Table
   - Add columns for Name, Email, LinkedIn URL, Company, Industry, City
3. Add an "Enrich" button above the repeating group
4. Add a "Download Results" button next to the Enrich button
5. Add a Progress Bar element (can be a shape with width animation)
6. Add a Group for status messages

[IMAGE PLACEHOLDER: Screenshot of page design]

## Step 6: Set Up Workflows

### Workflow 1: Enrich Button Click

1. Click on the Enrich button → Workflow tab
2. Add Action: API Connector → Enrich Alumni List
   - Set the body to: Search for Alumni's (if using a database)
     OR
   - Set the body to: an array of manually entered data
3. Add Action: Set State
   - Create a page state variable called "job_id"
   - Set its value to: Result of Step 1's job_id
4. Add Action: Set State
   - Create a page state variable called "polling"
   - Set its value to: Yes
5. Add Action: Set State
   - Create a page state variable called "progress"
   - Set its value to: 0
6. Add Action: Custom Event
   - Create new event called "CheckJobStatus"

[IMAGE PLACEHOLDER: Screenshot of Enrich workflow setup]

### Workflow 2: CheckJobStatus Custom Event

1. Go to Workflow tab → Custom Events → add "CheckJobStatus"
2. Add Condition: When page's polling is yes
3. Inside the condition:
   - Add Action: API Connector → Check Job Status
     - job_id: page's job_id
   - Add Condition: When result's status is "done"
     - Inside this condition:
       - Add Action: API Connector → Get Job Results
         - job_id: page's job_id
       - Add Action: Make changes to a list of Alumni
         - Create entries from: result of step 1
         - Set field job_id to: page's job_id
         - Set field enriched to: Yes
       - Add Action: Refresh data in repeating group
       - Add Action: Set State polling = No
       - Add Action: Show Success Message "Enrichment Complete!"
   - Add Condition: When result's status is "processing"
     - Inside this condition:
       - Add Action: Set State progress = page's progress + 10 (capped at 90)
       - Add Action: Animate Element's Width (the progress bar)
         - Element: Progress Bar
         - Width: page's progress %
       - Add Action: Schedule Event
         - Event: CheckJobStatus
         - Delay: 5 seconds

[IMAGE PLACEHOLDER: Screenshot of polling workflow setup]

### Workflow 3: Download Button Click

1. Click on the Download button → Workflow tab
2. Add Action: Open Link in New Tab
   - URL: `https://your-backend-url/jobs/page's job_id/download`

[IMAGE PLACEHOLDER: Screenshot of download workflow]

## Step 7: Testing the Integration

1. Add some test alumni data to your Bubble database
2. Preview your page
3. Click the "Enrich" button
4. Watch the progress bar increment as the backend processes the data
5. Once complete, the repeating group should populate with enriched data
6. Click "Download Results" to get the Excel file

## Troubleshooting

### CORS Issues
If you encounter CORS errors, make sure your FastAPI backend has your Bubble app URL in the ALLOWED_ORIGIN setting:

```python
# In your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-bubble-app.bubbleapps.io"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Calls Not Working
1. Check the browser console for errors
2. Verify your backend URL is correct and accessible
3. Make sure your data format matches what the API expects

### Empty Results
1. Ensure your LinkedIn URLs are valid
2. Check that your RapidAPI key is active and has sufficient credits

## Next Steps

1. Add data validation to ensure LinkedIn URLs are properly formatted
2. Add error handling for failed enrichments
3. Add search and filtering capabilities to your alumni database
4. Create a dashboard for monitoring enrichment statistics 