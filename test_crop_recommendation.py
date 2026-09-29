from app import create_app
from models.database import get_db_connection
import json

def test_full_flow():
    app = create_app()
    client = app.test_client()

    print("=" * 65)
    print("RUNNING CROP PLANNING ADVISORY & 10-RECORD HISTORY TESTS")
    print("=" * 65)

    # 1. Login
    login_res = client.post('/login', data={'email': 'farmer@agrismart.io', 'password': 'password123'}, follow_redirects=True)
    assert login_res.status_code == 200
    print("1. Login: OK")

    # 2. Verify GET /crop/ page content
    get_crop_res = client.get('/crop/')
    assert get_crop_res.status_code == 200
    html = get_crop_res.get_data(as_text=True)

    # Verify Agro-Climatic Planning Guide is PRESENT in LIGHT THEME at the top and collapsible
    assert "Agro-Climatic Planning Guide" in html, "Agro-Climatic Planning Guide must be present"
    assert "planning-guide-card" in html, "Light theme planning card must be present"
    assert "togglePlanningGuideBtn" in html, "Toggle button must be present"
    assert "planningGuideBody" in html, "Collapsible body container must be present"
    assert "advisoryCropSearch" in html, "Searchable crop selector input must be present"
    assert "advisoryCropSelect" in html, "Crop selector dropdown must be present"
    assert "Best Growing Season" in html, "Best Growing Season card must be present"
    assert "Suitable Temperature" in html, "Suitable Temperature card must be present"
    assert "Important Farming Conditions" in html, "Important Conditions must be present"
    assert "Recommended Farming Practices" in html, "Recommended Practices must be present"

    # Verify existing components remain below
    assert "Soil & Climate Parameters" in html, "Soil & Climate Parameters must remain"
    assert "Target Suitability Explorer" in html, "Target Suitability Explorer must remain"
    assert "Alternative Suitable Crops" in html, "Alternative Suitable Crops must remain"
    assert "Recommendation History" in html, "Recommendation History must remain"
    print("2. Page Layout: Agro-Climatic Planning Guide (Light Theme) at TOP with Navbar Location sync.")

    # 3. Test GET /api/crop-planning/advisory with location awareness
    res_patna = client.get('/api/crop-planning/advisory?crop=Rice&location=Patna,%20Bihar,%20India')
    assert res_patna.status_code == 200
    patna_data = res_patna.get_json()
    assert patna_data['success'] is True
    assert patna_data['crop_name'] == 'Rice'
    assert 'Bihar' in patna_data.get('location_note', '') or 'Gangetic' in patna_data.get('location_note', '')

    res_meerut = client.get('/api/crop-planning/advisory?crop=Rice&location=Meerut,%20Uttar%20Pradesh,%20India')
    assert res_meerut.status_code == 200
    meerut_data = res_meerut.get_json()
    assert meerut_data['success'] is True
    assert 'Uttar Pradesh' in meerut_data.get('location_note', '') or 'Plains' in meerut_data.get('location_note', '')
    print("3. Crop Planning Advisory Location Awareness (Patna vs Meerut): OK")
    print(f"   Patna Note : {patna_data.get('location_note')}")
    print(f"   Meerut Note: {meerut_data.get('location_note')}")

    # 4. Test Date Awareness (e.g. Wheat in September vs Rice in September)
    res_wheat = client.get('/api/crop-planning/advisory?crop=Wheat&date=2026-09-27')
    assert res_wheat.status_code == 200
    wheat_data = res_wheat.get_json()
    assert 'Planting window approaching' in wheat_data['status'] or 'Recommended' in wheat_data['status']
    print(f"4. Date Awareness Test (Wheat in Sept): Status='{wheat_data['status']}'")

    res_rice_sept = client.get('/api/crop-planning/advisory?crop=Rice&date=2026-09-27')
    rice_sept_data = res_rice_sept.get_json()
    assert 'passed' in rice_sept_data['status_type'] or 'passed' in rice_sept_data['status'].lower()
    assert '2027' in rice_sept_data['next_window']
    print(f"   Date Awareness Test (Rice in Sept): Status='{rice_sept_data['status']}' | Next Window='{rice_sept_data['next_window']}'")

    # 5. Test Multiple Crops from metadata
    test_crops = ['Maize', 'Sugarcane', 'Soyabean', 'Groundnut', 'Potato', 'Banana']
    for cr in test_crops:
        r = client.get(f'/api/crop-planning/advisory?crop={cr}')
        assert r.status_code == 200
        d = r.get_json()
        assert d['success'] is True
        assert d['crop_name'].lower() == cr.lower()

    # Also test substring matching for Cotton and Mustard
    r_cotton = client.get('/api/crop-planning/advisory?crop=Cotton')
    assert r_cotton.get_json()['success'] is True
    assert 'Cotton' in r_cotton.get_json()['crop_name']

    r_mustard = client.get('/api/crop-planning/advisory?crop=Mustard')
    assert r_mustard.get_json()['success'] is True
    assert 'Mustard' in r_mustard.get_json()['crop_name']

    print(f"5. Metadata verified for: {test_crops} + Cotton & Mustard fuzzy matching")

    # 5b. Test Reverse Target Exploration (What-If Reverse Calculation)
    res_exp_rice = client.post('/api/crop-recommendation/explore', json={
        'crop': 'Rice',
        'target': 75.0,
        'current_inputs': {
            'state': 'Bihar',
            'season': 'Whole Year',
            'area': 5.0,
            'rainfall': 600.0,
            'fertilizer': 400.0,
            'pesticide': 9.0,
            'nitrogen': 60,
            'phosphorus': 40,
            'potassium': 30,
            'ph': 6.5
        }
    })
    assert res_exp_rice.status_code == 200
    exp_data = res_exp_rice.get_json()
    assert exp_data['success'] is True
    assert exp_data['suggested_inputs']['season'] == 'Kharif'
    assert exp_data['suggested_inputs']['rainfall'] > 900
    assert exp_data['suggested_inputs']['fertilizer'] > 0
    assert 'nitrogen' in exp_data['suggested_inputs']
    assert 'phosphorus' in exp_data['suggested_inputs']
    assert 'potassium' in exp_data['suggested_inputs']
    assert 'ph' in exp_data['suggested_inputs']
    assert 'crop_info' in exp_data
    print("5b. Reverse Target Planning Test (Switch from Castor seed to Rice): OK")
    print(f"    Suggested Inputs for Rice: Season={exp_data['suggested_inputs']['season']}, Rain={exp_data['suggested_inputs']['rainfall']}mm, Fert={exp_data['suggested_inputs']['fertilizer']}kg, NPK={exp_data['suggested_inputs']['nitrogen']}-{exp_data['suggested_inputs']['phosphorus']}-{exp_data['suggested_inputs']['potassium']}, pH={exp_data['suggested_inputs']['ph']}")

    # 6. Test 10-Record History Cap in Database
    print("\n6. Testing 10-Record History Cap...")
    with client.session_transaction() as sess:
        uid = sess.get('user_id', 1)

    # Perform 12 consecutive predictions
    for i in range(12):
        payload = {
            'state': 'Uttar Pradesh',
            'season': 'Kharif',
            'area': 5.0 + i * 0.1,
            'rainfall': 1100.0 + i * 10,
            'fertilizer': 500.0 + i * 20,
            'pesticide': 10.0 + i * 0.5,
            'nitrogen': 80 + i,
            'phosphorus': 40,
            'potassium': 45,
            'ph': 6.8
        }
        pred_res = client.post('/api/crop-recommendation/predict', json=payload)
        assert pred_res.status_code == 200

    # Query SQLite database directly to verify count <= 10
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM crop_recommendation_history WHERE user_id = ?", (uid,))
    count_row = cursor.fetchone()
    db_history_count = count_row['cnt']
    conn.close()

    print(f"   Database History Count for user {uid}: {db_history_count}")
    assert db_history_count == 10, f"Expected exactly 10 history records, found {db_history_count}"

    # Also verify via API
    hist_api_res = client.get('/api/crop-recommendation/history')
    assert hist_api_res.status_code == 200
    hist_api_data = hist_api_res.get_json()
    assert len(hist_api_data['history']) <= 10
    print(f"   API History Count: {len(hist_api_data['history'])}")

    print("\n" + "=" * 65)
    print("ALL TESTS PASSED SUCCESSFULLY (100%)!")
    print("=" * 65)

if __name__ == '__main__':
    test_full_flow()

