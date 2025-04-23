# Create the necessary directories
New-Item -Path "github-upload" -ItemType Directory -Force
New-Item -Path "github-upload\app" -ItemType Directory -Force
New-Item -Path "github-upload\test" -ItemType Directory -Force
New-Item -Path "github-upload\jobs" -ItemType Directory -Force

# Copy app files
Copy-Item -Path "app\main.py" -Destination "github-upload\app\" -Force

# Copy configuration files
Copy-Item -Path "requirements.txt" -Destination "github-upload\" -Force
Copy-Item -Path "Procfile" -Destination "github-upload\" -Force
Copy-Item -Path "run.py" -Destination "github-upload\" -Force

# Copy documentation
Copy-Item -Path "README.md" -Destination "github-upload\" -Force
Copy-Item -Path "BUBBLE_API_SETUP.md" -Destination "github-upload\" -Force
Copy-Item -Path "BUBBLE_DETAILED_SETUP.md" -Destination "github-upload\" -Force
Copy-Item -Path "BUBBLE_SETUP.md" -Destination "github-upload\" -Force

# Copy test files
Copy-Item -Path "test\test_api.py" -Destination "github-upload\test\" -Force
Copy-Item -Path "test\create_sample_excel.py" -Destination "github-upload\test\" -Force

# Create a sample .env file (with placeholders instead of real credentials)
@"
RAPID_KEY=your_rapidapi_key_here
RAPID_HOST=fresh-linkedin-profile-data.p.rapidapi.com
ALLOWED_ORIGIN=https://your-bubble-app.bubbleapps.io
"@ | Out-File -FilePath "github-upload\.env.example" -Encoding utf8

# Create .gitignore
@"
# Environment
venv/
.env

# Python cache
__pycache__/
*.py[cod]
*$py.class

# Job data files
jobs/*.xlsx
jobs/*.json

# Local test data
*.xlsx
sample_*.xlsx

# IDE files
.vscode/
.idea/

# Logs
*.log
"@ | Out-File -FilePath "github-upload\.gitignore" -Encoding utf8

# Create a placeholder file to ensure jobs directory is created when cloned
"# This directory stores job data files.`nIt is intentionally kept empty in the repository." | Out-File -FilePath "github-upload\jobs\.gitkeep" -Encoding utf8

Write-Host "Files prepared for GitHub in the 'github-upload' folder."
Write-Host "Next steps:"
Write-Host "1. Copy the 'github-upload' folder to your desired location or rename it"
Write-Host "2. Initialize a git repository: git init"
Write-Host "3. Add files: git add ."
Write-Host "4. Commit changes: git commit -m 'Initial commit'"
Write-Host "5. Add your remote repository: git remote add origin <your-repo-url>"
Write-Host "6. Push changes: git push -u origin main" 