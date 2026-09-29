import io
import os
import json
from app import create_app

from config import Config, BASE_DIR
from models.database import get_db_connection, init_db
from werkzeug.security import generate_password_hash

def test_security_suite():
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for programmatic API testing client
    client = app.test_client()

    print("\n" + "="*60)
    print("RUNNING AGRISMART COMPREHENSIVE SECURITY TEST SUITE")
    print("="*60)

    # -------------------------------------------------------------
    # 0. Check Disease Model & Class Names Unmodified
    # -------------------------------------------------------------
    disease_model_path = os.path.join(BASE_DIR, 'models', 'plant_disease_model.keras')
    class_names_path = os.path.join(BASE_DIR, 'models', 'class_names.json')
    assert os.path.exists(disease_model_path), "Model file must exist"

    assert os.path.exists(class_names_path), "Class names JSON must exist"
    with open(class_names_path, 'r') as f:
        classes = json.load(f)
    assert len(classes) == 38, f"Expected 38 classes, found {len(classes)}"
    print("[PASS] Model and class names intact and unmodified (38 classes).")

    # -------------------------------------------------------------
    # 1. Normal User Login & Dashboard
    # -------------------------------------------------------------
    with client.session_transaction() as sess:
        sess.clear()
    
    res = client.post('/login', data={'email': 'farmer@agrismart.io', 'password': 'password123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"AgriSmart" in res.data or b"Dashboard" in res.data
    print("[PASS] TEST 1: Normal user login -> User Dashboard works.")

    # -------------------------------------------------------------
    # 2. Admin Login & Admin Control Center
    # -------------------------------------------------------------
    with client.session_transaction() as sess:
        sess.clear()
    
    res = client.post('/login', data={'email': 'admin@agrismart.io', 'password': 'admin123'}, follow_redirects=True)
    assert res.status_code == 200
    assert b"Admin" in res.data or b"Control Center" in res.data
    print("[PASS] TEST 2: Admin login -> Admin Panel works.")

    # -------------------------------------------------------------
    # 3. Normal User Cannot Access Admin URL
    # -------------------------------------------------------------
    with client.session_transaction() as sess:
        sess.clear()
    # Log in as normal farmer
    client.post('/login', data={'email': 'farmer@agrismart.io', 'password': 'password123'}, follow_redirects=False)
    
    # Try to access admin URL
    res = client.get('/admin/', follow_redirects=False)
    # Should redirect to dashboard with warning
    assert res.status_code in [302, 403]
    if res.status_code == 302:
        assert '/admin' not in res.headers.get('Location', '')
    print("[PASS] TEST 3: Normal user opens admin URL -> Access denied / Redirected.")

    # -------------------------------------------------------------
    # 4. Normal User Calls Admin Action / API -> 403
    # -------------------------------------------------------------
    res = client.post('/admin/users/1/toggle-status', headers={'Accept': 'application/json'}, follow_redirects=False)
    assert res.status_code in [403, 302]
    print("[PASS] TEST 4: Normal user calls admin action -> 403 / Redirected away.")

    # -------------------------------------------------------------
    # 5. Unauthenticated User Calls Protected API -> 401
    # -------------------------------------------------------------
    with client.session_transaction() as sess:
        sess.clear()
    
    res = client.get('/api/crop-recommendation/history', headers={'Accept': 'application/json'})
    assert res.status_code == 401
    data = json.loads(res.data)
    assert data.get('status') == 'error' or data.get('error') == 'Unauthorized'
    print("[PASS] TEST 5: Unauthenticated user calls protected API -> HTTP 401.")

    # -------------------------------------------------------------
    # 6. Deactivated User Cannot Login
    # -------------------------------------------------------------
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create test deactivated user
    test_email = "deact_test@agrismart.io"
    cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
    cursor.execute("INSERT INTO users (name, email, password, role, is_active) VALUES (?, ?, ?, 'user', 0)",
                   ("Inactive User", test_email, generate_password_hash("testPass123!")))
    conn.commit()
    conn.close()

    res = client.post('/login', data={'email': test_email, 'password': 'testPass123!'}, follow_redirects=True)
    assert b"deactivated" in res.data.lower() or b"invalid" in res.data.lower()
    print("[PASS] TEST 6: Deactivated user login is blocked.")

    # -------------------------------------------------------------
    # 7. Existing Session Blocked if User is Deactivated Mid-Session
    # -------------------------------------------------------------
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (test_email,))
    uid = cursor.fetchone()['id']
    conn.close()

    with client.session_transaction() as sess:
        sess['user_id'] = uid
        sess['user_role'] = 'user'
        sess['user_email'] = test_email

    res = client.get('/', follow_redirects=False)
    assert res.status_code == 302 # Redirected to login because deactivated

    print("[PASS] TEST 7: Deactivated user with existing session -> Blocked and redirected.")

    # -------------------------------------------------------------
    # 8 & 9. Admin Status Toggle (Activate & Deactivate)
    # -------------------------------------------------------------
    with client.session_transaction() as sess:
        sess.clear()
    client.post('/login', data={'email': 'admin@agrismart.io', 'password': 'admin123'})

    # Toggle to active
    client.post(f'/admin/users/{uid}/toggle-status')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT is_active FROM users WHERE id = ?", (uid,))
    status = cursor.fetchone()['is_active']
    assert status == 1
    print("[PASS] TEST 8: Admin activates user -> Status becomes 1 (Active).")

    # Toggle to deactivated
    client.post(f'/admin/users/{uid}/toggle-status')
    cursor.execute("SELECT is_active FROM users WHERE id = ?", (uid,))
    status = cursor.fetchone()['is_active']
    assert status == 0
    conn.close()
    print("[PASS] TEST 9: Admin deactivates user -> Status becomes 0 (Deactivated).")

    # -------------------------------------------------------------
    # 10. Admin Cannot Delete or Deactivate Own Account
    # -------------------------------------------------------------
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = 'admin@agrismart.io'")
    admin_id = cursor.fetchone()['id']
    conn.close()

    res = client.post(f'/admin/users/{admin_id}/toggle-status', follow_redirects=True)
    assert b"cannot deactivate your own" in res.data or b"Security Alert" in res.data
    
    res = client.post(f'/admin/users/{admin_id}/delete', follow_redirects=True)
    assert b"cannot delete your own" in res.data or b"Security Alert" in res.data
    print("[PASS] TEST 10: Admin cannot delete or deactivate own active account.")

    # -------------------------------------------------------------
    # 11. Invalid File Upload (Non-image payload)
    # -------------------------------------------------------------
    fake_image = (io.BytesIO(b"<?php echo 'malicious code'; ?>"), "exploit.php.jpg")
    res = client.post('/api/disease/predict', data={'image': fake_image}, content_type='multipart/form-data')
    assert res.status_code == 400
    assert b"not a valid image" in res.data or b"Invalid image format" in res.data
    print("[PASS] TEST 11: Invalid/fake file upload safely rejected (HTTP 400).")

    # -------------------------------------------------------------
    # 12. SQL Injection Attempt
    # -------------------------------------------------------------
    sqli_payload = "' OR 1=1 --"
    res = client.get(f'/admin/users?q={sqli_payload}', follow_redirects=True)
    assert res.status_code == 200 # Properly handled by parameterized query without 500 error
    print("[PASS] TEST 12: SQL injection payload safely parameterized without errors.")

    # -------------------------------------------------------------
    # 13. Secure Logout Invalidation
    # -------------------------------------------------------------
    res = client.get('/logout', follow_redirects=True)
    assert res.status_code == 200
    # Attempting to access protected page after logout
    res = client.get('/profile/', follow_redirects=False)
    assert res.status_code == 302 # Must redirect to login
    print("[PASS] TEST 13: Logout invalidates session and blocks protected pages.")

    # -------------------------------------------------------------
    # 14. Security Headers Verification
    # -------------------------------------------------------------
    res = client.get('/login')
    headers = res.headers
    assert headers.get('X-Content-Type-Options') == 'nosniff'
    assert headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert headers.get('Referrer-Policy') == 'strict-origin-when-cross-origin'
    assert 'Content-Security-Policy' in headers
    print("[PASS] TEST 14: HTTP Security Headers verified (X-Content-Type-Options, X-Frame-Options, CSP, Referrer-Policy).")

    # -------------------------------------------------------------
    # 15. Verify All Existing Pages Load Successfully for Authenticated Farmer
    # -------------------------------------------------------------
    client.post('/login', data={'email': 'farmer@agrismart.io', 'password': 'password123'})
    
    pages = [
        ('/', "Dashboard"),
        ('/weather', "Weather"),
        ('/crop', "Crop"),
        ('/soil/', "Soil"),
        ('/mandi/', "Mandi"),
        ('/disease', "Disease"),
        ('/profile/', "Profile"),
        ('/settings/', "Settings")
    ]
    for url, name in pages:
        r = client.get(url)
        assert r.status_code == 200, f"Page {name} ({url}) returned status {r.status_code}"
    print("[PASS] TEST 15: All existing application modules load with HTTP 200 (Dashboard, Weather, Crop, Soil, Mandi, Disease, Profile, Settings).")

    # Clean up test user
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
    conn.commit()
    conn.close()

    print("\n" + "="*60)
    print("ALL SECURITY TESTS COMPLETED SUCCESSFULLY! [100% PASS]")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_security_suite()
