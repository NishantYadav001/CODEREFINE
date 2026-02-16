# Create root folder
New-Item -ItemType Directory -Name CODEREVGENAI

# Create backend folder and files
New-Item -ItemType Directory -Name CODEREVGENAI/backend
New-Item -ItemType File -Path "CODEREVGENAI/backend/main.py"
New-Item -ItemType File -Path "CODEREVGENAI/backend/requirements.txt"
"fastapi`nuvicorn`npython-dotenv`nmysql-connector-python`ngroq`nhttpx`nslowapi`npython-multipart`npython-docx`nfpdf`nPillow`npytesseract`ngoogle-generativeai`npasslib[bcrypt]`npython-jose[cryptography]" | Out-File -FilePath "CODEREVGENAI/backend/requirements.txt"
New-Item -ItemType File -Path "CODEREVGENAI/backend/.env"
"GROQ_API_KEY=" | Out-File -FilePath "CODEREVGENAI/backend/.env"
New-Item -ItemType File -Path "CODEREVGENAI/backend/__init__.py"

# Create frontend folder and files
New-Item -ItemType Directory -Name CODEREVGENAI/frontend
New-Item -ItemType File -Path "CODEREVGENAI/frontend/index.html"
New-Item -ItemType File -Path "CODEREVGENAI/frontend/login.html"