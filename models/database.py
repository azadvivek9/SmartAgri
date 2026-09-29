import sqlite3
import os
from werkzeug.security import generate_password_hash
from config import Config

def get_db_connection():
    db_path = Config.DATABASE
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE), exist_ok=True)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users table
    cursor.execute('''
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
        )
    ''')

    # Migration: Ensure 'role' and 'is_active' columns exist in existing users table
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [col[1] for col in cursor.fetchall()]
    if 'role' not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user' NOT NULL")
    if 'is_active' not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1 NOT NULL")

    # 2. Crops table
    cursor.execute('''
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
        )
    ''')

    # 3. Soil records table
    cursor.execute('''
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
        )
    ''')

    # 4. Crop recommendations table
    cursor.execute('''
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
        )
    ''')

    # 4b. Crop recommendation history table (with exact dataset input features JSON)
    cursor.execute('''
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
        )
    ''')

    # 5. Mandi prices table
    cursor.execute('''
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
        )
    ''')

    # 6. Disease records table
    cursor.execute('''
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
        )
    ''')

    # 7. User settings table
    cursor.execute('''
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
        )
    ''')

    conn.commit()
    seed_initial_data(conn)
    conn.close()

def seed_initial_data(conn):
    cursor = conn.cursor()

    # 1. Ensure Default Farmer User exists
    cursor.execute("SELECT id, role FROM users WHERE email = 'farmer@agrismart.io'")
    farmer_user = cursor.fetchone()
    if not farmer_user:
        default_pwd = generate_password_hash('password123')
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, role, location, village, land_area, soil_type, main_crop)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'Ramesh Patel',
            'farmer@agrismart.io',
            '+91 98765 43210',
            default_pwd,
            'user',
            'Meerut, Uttar Pradesh',
            'Hastinapur Block 4',
            '4.5 Acres',
            'Alluvial Loam',
            'Wheat & Sugarcane'
        ))
        farmer_id = cursor.lastrowid
        cursor.execute('''
            INSERT OR IGNORE INTO user_settings (user_id, weather_alerts, irrigation_alerts, crop_alerts, market_alerts, language, temp_unit, theme)
            VALUES (?, 1, 1, 1, 1, 'English', 'Celsius', 'light')
        ''', (farmer_id,))
    else:
        # Ensure role is set for existing farmer
        cursor.execute("UPDATE users SET role = 'user' WHERE email = 'farmer@agrismart.io' AND (role IS NULL OR role = '')")

    # 2. Ensure Default System Admin User exists
    cursor.execute("SELECT id FROM users WHERE email = 'admin@agrismart.io'")
    admin_user = cursor.fetchone()
    if not admin_user:
        admin_pwd = generate_password_hash('admin123')
        cursor.execute('''
            INSERT INTO users (name, email, phone, password, role, location, village, land_area, soil_type, main_crop)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            'System Administrator',
            'admin@agrismart.io',
            '+91 98000 00000',
            admin_pwd,
            'admin',
            'New Delhi, India',
            'HQ Central Block',
            'N/A (Admin)',
            'N/A',
            'System Operations'
        ))
        admin_id = cursor.lastrowid
        cursor.execute('''
            INSERT OR IGNORE INTO user_settings (user_id, weather_alerts, irrigation_alerts, crop_alerts, market_alerts, language, temp_unit, theme)
            VALUES (?, 1, 1, 1, 1, 'English', 'Celsius', 'light')
        ''', (admin_id,))
    else:
        # Ensure admin role is assigned
        cursor.execute("UPDATE users SET role = 'admin' WHERE email = 'admin@agrismart.io'")

    # Seed Crops
    cursor.execute('SELECT COUNT(*) FROM crops')
    if cursor.fetchone()[0] == 0:
        crops_data = [
            ('Wheat', 'Rabi (Winter)', '110-130 Days', 'Medium (450-650 mm)', '15-25°C', '50-70%', '6.0-7.5', 'High yielding staple grain suited for cool growing seasons and well-drained loam soil.'),
            ('Rice (Paddy)', 'Kharif (Monsoon)', '120-150 Days', 'High (1200-1500 mm)', '22-32°C', '70-90%', '5.5-7.0', 'Thrives in heavy clayey loam soils with abundant water and warm humid weather.'),
            ('Maize', 'Kharif / Spring', '90-110 Days', 'Medium (500-800 mm)', '18-28°C', '55-75%', '5.8-7.2', 'Versatile cereal crop requiring well-aerated fertile soil with good organic matter.'),
            ('Sugarcane', 'Annual (10-12 Mos)', '300-360 Days', 'Very High (1500-2500 mm)', '20-35°C', '65-85%', '6.5-7.5', 'Long-duration cash crop best suited to tropical alluvial regions with deep soil.'),
            ('Mustard', 'Rabi (Winter)', '95-115 Days', 'Low to Medium (300-400 mm)', '10-22°C', '45-65%', '6.0-7.5', 'Excellent oilseed crop with drought tolerance and modest irrigation needs.'),
            ('Cotton', 'Kharif', '150-180 Days', 'Medium (700-1100 mm)', '21-30°C', '60-80%', '6.0-8.0', 'Commercial fiber crop preferring deep black soil or alluvial loam with good drainage.'),
            ('Chickpea (Gram)', 'Rabi', '90-110 Days', 'Low (350-450 mm)', '15-25°C', '40-60%', '6.0-7.8', 'Nitrogen-fixing pulse crop improving soil fertility with low fertilizer dependency.'),
            ('Potato', 'Rabi', '80-100 Days', 'Medium (400-500 mm)', '15-22°C', '60-80%', '5.2-6.5', 'High value tuber requiring loose, friable sandy loam rich in potassium.')
        ]
        cursor.executemany('''
            INSERT INTO crops (crop_name, season, growing_period, water_requirement, optimal_temp, optimal_humidity, optimal_ph, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', crops_data)

    # Seed Mandi Prices
    cursor.execute('SELECT COUNT(*) FROM mandi_prices')
    if cursor.fetchone()[0] == 0:
        mandi_data = [
            ('Wheat', 'Uttar Pradesh', 'Meerut', 'Meerut Mandi (Partapur)', 2275.0, 2450.0, 2380.0, '2026-09-25'),
            ('Wheat', 'Uttar Pradesh', 'Hapur', 'Hapur Grain Mandi', 2250.0, 2420.0, 2360.0, '2026-09-25'),
            ('Wheat', 'Uttar Pradesh', 'Lucknow', 'Dubagga Mandi', 2260.0, 2440.0, 2370.0, '2026-09-25'),
            ('Wheat', 'Haryana', 'Karnal', 'Karnal Main Mandi', 2290.0, 2480.0, 2410.0, '2026-09-25'),
            ('Wheat', 'Punjab', 'Ludhiana', 'Ludhiana Mandi', 2300.0, 2500.0, 2425.0, '2026-09-25'),
            
            ('Rice (Paddy)', 'Uttar Pradesh', 'Meerut', 'Meerut Mandi (Partapur)', 2180.0, 2400.0, 2310.0, '2026-09-25'),
            ('Rice (Paddy)', 'Uttar Pradesh', 'Varanasi', 'Varanasi Central Mandi', 2150.0, 2380.0, 2290.0, '2026-09-25'),
            ('Rice (Paddy)', 'Punjab', 'Amritsar', 'Amritsar Grain Market', 2350.0, 2650.0, 2520.0, '2026-09-25'),
            ('Rice (Paddy)', 'Haryana', 'Kurukshetra', 'Thanesar Mandi', 2320.0, 2590.0, 2480.0, '2026-09-25'),
            
            ('Sugarcane', 'Uttar Pradesh', 'Meerut', 'Daurala Mill Yard', 370.0, 395.0, 385.0, '2026-09-25'),
            ('Sugarcane', 'Uttar Pradesh', 'Muzaffarnagar', 'Mansurpur Yard', 365.0, 390.0, 380.0, '2026-09-25'),
            ('Sugarcane', 'Maharashtra', 'Kolhapur', 'Kolhapur Sugar Yard', 380.0, 410.0, 395.0, '2026-09-25'),

            ('Mustard', 'Uttar Pradesh', 'Meerut', 'Meerut Mandi (Partapur)', 5350.0, 5750.0, 5600.0, '2026-09-25'),
            ('Mustard', 'Rajasthan', 'Bharatpur', 'Bharatpur Oilseed Mandi', 5420.0, 5820.0, 5680.0, '2026-09-25'),
            ('Mustard', 'Haryana', 'Hisar', 'Hisar Krishi Mandi', 5380.0, 5780.0, 5620.0, '2026-09-25'),

            ('Maize', 'Uttar Pradesh', 'Meerut', 'Meerut Mandi (Partapur)', 2050.0, 2240.0, 2160.0, '2026-09-25'),
            ('Maize', 'Bihar', 'Gulabbagh', 'Purnea Mandi', 2100.0, 2320.0, 2240.0, '2026-09-25'),
            ('Maize', 'Karnataka', 'Davangere', 'Davangere APMC', 2120.0, 2350.0, 2260.0, '2026-09-25'),

            ('Cotton', 'Gujarat', 'Rajkot', 'Rajkot APMC', 7100.0, 7650.0, 7420.0, '2026-09-25'),
            ('Cotton', 'Maharashtra', 'Nagpur', 'Nagpur Mandi', 6950.0, 7500.0, 7300.0, '2026-09-25'),
            
            ('Potato', 'Uttar Pradesh', 'Agra', 'Khandauli Cold Mandi', 1450.0, 1720.0, 1600.0, '2026-09-25'),
            ('Potato', 'Uttar Pradesh', 'Meerut', 'Meerut Sabzi Mandi', 1500.0, 1780.0, 1640.0, '2026-09-25'),
            ('Potato', 'West Bengal', 'Hooghly', 'Tarakeswar Mandi', 1420.0, 1690.0, 1580.0, '2026-09-25'),

            ('Tomato', 'Uttar Pradesh', 'Meerut', 'Meerut Sabzi Mandi', 1800.0, 2400.0, 2100.0, '2026-09-25'),
            ('Tomato', 'Maharashtra', 'Nashik', 'Pimpalgaon Mandi', 1900.0, 2550.0, 2250.0, '2026-09-25'),
            ('Onion', 'Maharashtra', 'Lasalgaon', 'Lasalgaon APMC', 2200.0, 2850.0, 2550.0, '2026-09-25'),
            ('Onion', 'Uttar Pradesh', 'Meerut', 'Meerut Sabzi Mandi', 2400.0, 3100.0, 2800.0, '2026-09-25')
        ]
        cursor.executemany('''
            INSERT INTO mandi_prices (crop, state, district, mandi, min_price, max_price, modal_price, date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', mandi_data)

    # Seed Initial Soil Record
    cursor.execute('SELECT COUNT(*) FROM soil_records')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO soil_records (user_id, nitrogen, phosphorus, potassium, ph, organic_carbon, moisture, soil_type, health_score, fertilizer_rec, irrigation_rec)
            VALUES (?, 78.5, 38.0, 210.0, 6.8, 0.65, 55.0, 'Alluvial Loam', 'Good', 'Urea: 45 kg/acre split dosage, SSP: 25 kg/acre at sowing', 'Moderate moisture detected. Light sprinkler irrigation recommended in 3 days.')
        ''', (1,))

    # Seed Initial Disease Record
    cursor.execute('SELECT COUNT(*) FROM disease_records')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO disease_records (user_id, image_path, disease, confidence, symptoms, treatment, is_healthy)
            VALUES (?, 'sample_rice_blast.jpg', 'Leaf Blight (Xanthomonas oryzae)', 94.2, 'Yellow-orange lesions with wavy margins starting from leaf tips, gradual wilting and water-soaked streaks.', 'Apply Copper Oxychloride 50% WP @ 2.5g/L + Streptocycline 100ppm. Avoid excess nitrogen fertilization during active lesion spread.', 0)
        ''', (1,))

    conn.commit()
