# Food Expiration Tracker

A web app that lets users upload or capture images of food, automatically detect the food name using Google Cloud Vision, and track expiration dates.

---

##  Features

- Take or upload a picture of food
- Automatically detect food name (Google Vision API)
- Upload images to Google Cloud Storage
- Track expiration dates
- Store items locally in a database

---

##  Tech Stack

- Python
- Streamlit (frontend)
- FastAPI (backend)
- Google Cloud Storage
- Google Cloud Vision API
- SQLite

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd food-expiration-tracker
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up Google Cloud credentials
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account.json"
```
Replace `/path/to/your-service-account.json` with your actual file path.

### 5. Run the application

Terminal 1 (Backend):
```bash
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account.json"
python -m uvicorn main:app --reload
```

Terminal 2 (Frontend):
```bash
source venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-service-account.json"
streamlit run app.py
```


