
# Visual Search Assistant — Backend (FastAPI)

## Prereqs
- Python 3.10+
- (Optional) Tesseract OCR binary if you want OCR:  
  - macOS: `brew install tesseract`  
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`  
  - Windows: https://github.com/UB-Mannheim/tesseract/wiki

## Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python index_repo.py
uvicorn app:app --reload --port 8000
```

Open docs: http://127.0.0.1:8000/docs
