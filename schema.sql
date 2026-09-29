-- AgriSmart Database Schema (SQLite)
-- Automatically initialized on first launch by models/database.py

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user' NOT NULL,
    location TEXT DEFAULT 'Meerut, Uttar Pradesh',
    village TEXT DEFAULT 'Hastinapur',
    land_area TEXT DEFAULT '4.5 Acres',
    soil_type TEXT DEFAULT 'Alluvial Loam',
    main_crop TEXT DEFAULT 'Wheat & Sugarcane',
    is_active INTEGER DEFAULT 1 NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Crops Table
CREATE TABLE IF NOT EXISTS crops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop_name TEXT NOT NULL,
    season TEXT NOT NULL,
    growing_period TEXT NOT NULL,
    water_requirement TEXT NOT NULL,
    optimal_temp TEXT,
    optimal_humidity TEXT,
    optimal_ph TEXT,
    description TEXT
);

-- 3. Soil Records Table
CREATE TABLE IF NOT EXISTS soil_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    nitrogen REAL NOT NULL,
    phosphorus REAL NOT NULL,
    potassium REAL NOT NULL,
    ph REAL NOT NULL,
    organic_carbon REAL,
    moisture REAL,
    soil_type TEXT,
    health_score TEXT DEFAULT 'Good',
    fertilizer_rec TEXT,
    irrigation_rec TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 4. Crop Recommendations Table (Legacy summary)
CREATE TABLE IF NOT EXISTS crop_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    recommended_crop TEXT NOT NULL,
    suitability TEXT DEFAULT 'High',
    confidence REAL,
    season TEXT,
    nitrogen REAL,
    phosphorus REAL,
    potassium REAL,
    ph REAL,
    temperature REAL,
    humidity REAL,
    rainfall REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 5. Crop Recommendation History Table (Dataset ML features)
CREATE TABLE IF NOT EXISTS crop_recommendation_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    recommended_crop TEXT NOT NULL,
    confidence REAL NOT NULL,
    suitability TEXT NOT NULL,
    season TEXT,
    state TEXT,
    area REAL,
    rainfall REAL,
    fertilizer REAL,
    pesticide REAL,
    nitrogen REAL,
    phosphorus REAL,
    potassium REAL,
    ph REAL,
    input_features TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 6. Mandi Prices Table
CREATE TABLE IF NOT EXISTS mandi_prices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop TEXT NOT NULL,
    state TEXT NOT NULL,
    district TEXT NOT NULL,
    mandi TEXT NOT NULL,
    min_price REAL NOT NULL,
    max_price REAL NOT NULL,
    modal_price REAL NOT NULL,
    date TEXT NOT NULL
);

-- 7. Disease Records Table
CREATE TABLE IF NOT EXISTS disease_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    image_path TEXT NOT NULL,
    disease TEXT NOT NULL,
    confidence REAL NOT NULL,
    symptoms TEXT,
    treatment TEXT,
    is_healthy INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 8. User Settings Table
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    weather_alerts INTEGER DEFAULT 1,
    irrigation_alerts INTEGER DEFAULT 1,
    crop_alerts INTEGER DEFAULT 1,
    market_alerts INTEGER DEFAULT 1,
    language TEXT DEFAULT 'English',
    temp_unit TEXT DEFAULT 'Celsius',
    theme TEXT DEFAULT 'light',
    FOREIGN KEY (user_id) REFERENCES users(id)
);
