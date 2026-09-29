# 🌱 AgriSmart — AI-Powered Smart Agriculture Advisory Platform

A comprehensive, production-ready **Smart Agriculture Advisory Web Application** built with **Python (Flask)**, **TensorFlow/Keras**, **Scikit-Learn**, **SQLite**, **Chart.js**, and modern **Vanilla HTML5/CSS3/JavaScript**.

AgriSmart empowers farmers and agricultural extension workers with precision agronomy tools: 7-day hyperlocal weather advisories, ML soil-to-crop matching, soil health diagnostics, live APMC mandi market price discovery, automated 38-class leaf disease scanning, and an administrative control center.

---

## 🌟 Key Application Features

1. **🏠 Unified Farm Dashboard:**
   - Real-time weather, crop stage, soil health, and mandi price summaries.
   - 4 live rule-based agricultural advisories (Irrigation, Fertilizer top-dressing, Precipitation notice, Crop protection).
   - Interactive 7-day weather trend charts.

2. **🌦️ 7-Day Precision Agricultural Weather Advisory:**
   - Hyperlocal coordinate-based weather resolution across Indian agro-climatic zones.
   - Comprehensive metrics: Temperature, Feels-like, Humidity, Wind speed, Precipitation probability, and Cloud cover.
   - 4 green-themed Chart.js forecast curves (Temperature, Rain %, Wind km/h, Humidity %).

3. **🌾 ML Crop Recommendation & Exploration:**
   - Machine Learning soil-to-crop matching engine trained on state-wise agricultural datasets.
   - Evaluates Nitrogen (N), Phosphorus (P), Potassium (K), pH, Annual Rainfall, Fertilizer, and Pesticide requirements.
   - Suitability confidence scoring, agronomic tips, and alternative crop suggestions.

4. **🧪 Soil Analysis & Nutrition Diagnostics:**
   - Evaluates pH, NPK levels, Organic Carbon, and Moisture.
   - Soil Health Score calculation with scientific fertilizer dosage recommendations (Urea, SSP, MOP, FYM) and split schedules.

5. **💰 APMC Mandi Market Prices:**
   - State-wise, crop-wise, and district-level price trend analysis.
   - Minimum, Maximum, and Benchmark Modal prices per quintal.
   - Dynamic interactive market rate search and filtering.

6. **🍃 Deep Learning Crop Disease Detection:**
   - Neural network image classification model trained on the PlantVillage dataset across 38 crop disease classes.
   - Upload leaf images (JPG, JPEG, PNG, WEBP) with Pillow content validation.
   - Confidence percentage, pathological symptoms, chemical & bio-control treatment recommendations, and preventive measures.
   - Real-time persistent scan history tracking.

7. **🛡️ Administrator Control Center & User Management:**
   - System metrics and advisory activity streams.
   - User account directory with role management (Admin / Farmer).
   - Activate/Deactivate account toggle to control platform access.
   - Self-deletion and self-deactivation protection for administrators.

8. **🔒 Robust Security & Hardening:**
   - Session fixation protection, secure cookie settings (`HttpOnly`, `SameSite=Lax`).
   - CSRF protection on state-changing forms (`Flask-WTF`).
   - Rate limiting on authentication and sensitive endpoints (`Flask-Limiter`).
   - Strict file upload containment and deep image validation.
   - Parameterized SQL queries preventing SQL injection.
   - HTTP security headers (`X-Content-Type-Options`, `X-Frame-Options`, `CSP`, `Referrer-Policy`).

---

## 🛠️ Technology Stack

- **Backend:** Python 3.11, Flask 3.x, Werkzeug, Jinja2
- **Machine Learning & AI:** TensorFlow 2.x / Keras 3.x (Disease Classification), Scikit-Learn (Crop Recommendation), NumPy, Pandas
- **Security:** Flask-WTF (CSRF), Flask-Limiter (Rate Limiting), Pillow (Image Validation)
- **Database:** SQLite3 (parameterized queries, automatic migrations)
- **Frontend:** Vanilla HTML5, CSS3, JavaScript (ES6+), Chart.js 4.4, Font Awesome 6.5, Google Fonts (Inter)

---

## 🚀 Installation & Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/SmartAgriculture.git
cd SmartAgriculture
```

### 2. Set Up Python Virtual Environment
```powershell
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and configure your keys:
```powershell
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Edit `.env`:
```env
OPENWEATHER_API_KEY=your_openweather_api_key_here
SECRET_KEY=your_secure_secret_key_here
SESSION_COOKIE_SECURE=False
```

### 5. Initialize the Database
The SQLite database (`agrismart.db`) is automatically initialized and seeded with default baseline records on the first application launch.

You can also inspect the schema definition in [`schema.sql`](schema.sql).

### 6. Run the Application
```bash
python app.py
```

Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🤖 Machine Learning Models & Git LFS

This project includes trained machine learning models in the `models/` directory:

| Model | File | Format | Purpose |
| :--- | :--- | :--- | :--- |
| **Plant Disease Classification** | `models/plant_disease_model.keras` | Keras / TensorFlow | 38-class crop leaf disease detection |
| **Class Label Mapping** | `models/class_names.json` | JSON | 38 disease class index mappings |
| **Crop Recommendation Engine** | `models/crop_recommendation_model.pkl` | Pickle / Scikit-Learn | Crop-to-soil recommendation pipeline |

### Git LFS Setup for GitHub
Because serialized model files (`*.pkl`, `*.keras`) can exceed standard GitHub file size limits, Git Large File Storage (LFS) is configured in [`.gitattributes`](.gitattributes).

Before pushing to GitHub, install Git LFS once:
```bash
# Install Git LFS
git lfs install

# Track large model binaries
git lfs track "*.pkl"
git lfs track "*.keras"
```

---

## 🧪 Running Automated Tests

Run the security and functional test suite:
```bash
python test_security.py
```

---

## 📂 Project Structure

```text
SmartAgriculture/
├── app.py                     # Main application factory & error handlers
├── config.py                  # Application configuration & session settings
├── extensions.py              # Central Flask-Limiter and CSRF instances
├── schema.sql                 # Database table schema definition
├── requirements.txt           # Python package dependencies
├── .env.example               # Template environment configuration
├── .gitignore                 # Excludes local databases, venv, uploads, and secrets
├── .gitattributes             # Git LFS configuration for ML models
├── models/
│   ├── database.py            # Database initialization and connection helpers
│   ├── plant_disease_model.keras # Trained 38-class plant disease neural network
│   ├── class_names.json       # 38 plant disease class labels
│   └── crop_recommendation_model.pkl # Crop recommendation ML pipeline
├── ml/
│   └── disease/
│       ├── predict.py         # DiseasePredictor inference class
│       └── train_model.py     # Training script for PlantVillage dataset
├── routes/
│   ├── auth.py                # Authentication, registration, logout, RBAC
│   ├── admin.py               # Admin panel & user management
│   ├── dashboard.py           # Farm dashboard route
│   ├── weather.py             # 7-day agricultural weather advisories
│   ├── crop.py                # ML crop recommendation & planning APIs
│   ├── soil.py                # Soil health analysis
│   ├── mandi.py               # APMC mandi price trends
│   ├── disease.py             # Crop disease image scanning
│   ├── profile.py             # Farmer profile management
│   └── settings.py            # User settings and password updates
├── services/
│   ├── weather_service.py     # Weather data resolution and agro-advisories
│   ├── crop_recommendation_service.py # Crop recommendation service
│   ├── soil_service.py        # Soil nutrition & fertilizer calculations
│   └── mandi_service.py       # Mandi market dataset indexing
├── static/
│   ├── css/style.css          # Main responsive stylesheet
│   └── js/                    # Client-side scripts
├── templates/
│   ├── base.html              # Base layout with navbar, sidebar, and CSRF meta
│   ├── login.html             # Secure login form
│   ├── register.html          # Farmer account registration
│   ├── dashboard.html         # Overview dashboard
│   ├── weather.html           # Weather advisory view
│   ├── crop.html              # Crop recommendation view
│   ├── soil.html              # Soil testing view
│   ├── mandi.html             # Mandi market view
│   ├── disease.html           # Disease scanner interface
│   ├── profile.html           # Profile view
│   ├── settings.html          # Settings view
│   └── admin/
│       ├── index.html         # Admin control panel
│       └── users.html         # User directory & active/deactive management
└── data/                      # Public benchmark datasets (Crop & Mandi prices)
```

---

## 🛡️ License

This project is open source and available under the [MIT License](LICENSE).
