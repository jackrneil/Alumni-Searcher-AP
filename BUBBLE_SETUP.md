# Bubble Application Setup

This document provides step-by-step instructions for setting up the Bubble side of the Alumni Searcher application.

## 1. Enable Data API & create data type

1. In the Bubble editor, go to **Settings** → **API**
2. Check **Enable Data API**
3. Generate API Token (copy for later, though it's not needed for this setup)
4. Go to **Data** → **Data Types** → **New Type**
5. Name the new type **AlumniTemp**
6. Add the following fields:
   - `firstName` (text)
   - `lastName` (text)
   - `email` (text)
   - `company` (text)
   - `industry` (text)
   - `city` (text)
   - `linkedinURL` (text)
   - `job_id` (text)

## 2. Design page

1. In the Pages dropdown, click **New Page** → name it `enrich`
2. Drag a **FileUploader** onto the page
   - Rename it to "Uploader Excel" in the Inspector panel
3. Drag a **Button** onto the page
   - Set the text to "Start Enrichment"
4. Drag a **ProgressBar** (Shape) onto the page
   - Set width to 100%
   - Set initial width to 0%
   - Rename to "ProgressBar"
5. Drag a **Repeating Group** onto the page
   - Set Type of content to **AlumniTemp**
   - Set Data source to empty for now
   - Inside the first cell, add Text elements for Name, Company, City, etc.
   - Add a Link inside the cell → set Destination external URL to Current cell's linkedinURL

## 3. Install API Connector plugin

1. Go to **Plugins** → **Add plugins** → **API Connector** → **Install**
2. Go to **API Connector** → **Add another API** → Name it "BackendAPI"

## 4. Define API calls

### Call 1: "Upload Job"

- Method: POST
- URL: https://your-backend-url.onrender.com/jobs
- Headers: none
- Body type: form-data
- Key: file → Value: Uploader Excel's value
- Check "Use as Action"
- Initialize call by uploading a sample file

### Call 2: "Check Job"

- Method: GET
- URL: https://your-backend-url.onrender.com/jobs/[job_id]
- [job_id] = parameter
- Check "Use as Action"

### Call 3: "Get Results"

- Method: GET
- URL: https://your-backend-url.onrender.com/jobs/[job_id]/result
- [job_id] = parameter
- Returns array
- Check "Use as Action"

### Call 4: "Download Excel" (optional)

- Method: GET
- URL: https://your-backend-url.onrender.com/jobs/[job_id]/download
- [job_id] = parameter
- Check "Use as Data"

## 5. Workflow setup

### When Button "Start Enrichment" is clicked:

1. API Connector → Upload Job
   - file = Uploader Excel's value
2. Set State (Element: Page)
   - Create custom state `job_id` (text) → value = Result of Step 1's job_id
3. Set State `polling` (yes/no) → yes
4. Trigger Custom Event "Poll"

### Create Custom Event "Poll":

This event will run only when `polling` is yes.

1. API Connector → Check Job (job_id = Page's job_id)
2. When result's status = "done" →
   - API Connector Get Results
   - Data → "Make changes to a list of AlumniTemp": create new entries from returned array
   - Repeating Group data source = Search for AlumniTemp where job_id = Page's job_id
   - Set State polling = no
3. When status ≠ "done" →
   - Element Action → Animate ProgressBar width to % result's progress (if available)
   - Schedule custom event "Poll" (delay 20 s)

### Add Download Button (optional):

- Link URL = https://your-backend-url.onrender.com/jobs/(Page job_id)/download

## 6. Testing

1. Preview the enrich page
2. Upload a sample Excel file with LinkedIn URLs
3. Click "Start Enrichment"
4. Observe the progress bar increments every 20 seconds
5. Once done, the repeating group will populate with enriched data
6. Click LinkedIn links to verify they lead to the correct profiles
7. Download the Excel file to confirm the data has been properly enriched

## Troubleshooting

- **Bubble call returns 400**: Check Bubble → Logs → API Connector response tab
- **CORS error**: Check FastAPI ALLOWED_ORIGIN list or Render HTTPS vs HTTP
- **No progress update**: Check backend logs; the job might be stuck
- **Repeating Group empty**: Verify the data source filter and whether the list was created correctly 