import pandas as pd

# Sample LinkedIn profiles
sample_data = [
    {"LinkedIn URL": "https://www.linkedin.com/in/williamhgates/"},
    {"LinkedIn URL": "https://www.linkedin.com/in/satyanadella/"},
    {"LinkedIn URL": "https://www.linkedin.com/in/sundar-pichai/"},
    {"LinkedIn URL": "https://www.linkedin.com/in/jeffweiner08/"},
    {"LinkedIn URL": "https://www.linkedin.com/in/tim-cook-1/"}
]

# Create DataFrame
df = pd.DataFrame(sample_data)

# Save to Excel
df.to_excel("sample_linkedin_urls.xlsx", index=False)

print("Sample Excel file created: sample_linkedin_urls.xlsx") 