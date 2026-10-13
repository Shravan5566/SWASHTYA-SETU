import requests

s = requests.Session()
# 1. Login as doctor
res = s.post("http://127.0.0.1:5000/api/auth/login", json={
    "username": "doctor_demo",
    "password": "password123"
})
print("1. Login:", res.status_code, res.json().get("user", {}).get("name"))

# 2. Get card SS-TEST-001 via Emergency Break-Glass (so token is attached)
res_bg = s.post("http://127.0.0.1:5000/api/consent/emergency", json={
    "card_id": "SS-TEST-001",
    "reason": "Acute Dengue emergency evaluation and OPD logging test"
})
print("2. Break glass:", res_bg.status_code, res_bg.json().get("success"))
grant_token = res_bg.json().get("grant", {}).get("token")
s.headers.update({"X-Consent-Token": grant_token})

# 3. Check current ML forecast for Katraj Dengue
res = s.get("http://127.0.0.1:5000/api/surveillance/ml-forecast?ward=Katraj&disease=dengue")
print("3. Pre-check ML forecast Katraj Dengue:", res.json().get("forecast", {}).get("display_cases"), res.json().get("forecast", {}).get("raw_cases"))

# 4. Check current ward matrix for Dengue
res = s.get("http://127.0.0.1:5000/api/surveillance/ward-matrix?disease=dengue")
wards = res.json().get("wards", [])
katraj_pre = next((w for w in wards if w.get("ward") == "Katraj"), None)
print("4. Pre-check Katraj in ward matrix:", katraj_pre)

# 5. Add OPD consultation record with ward='Katraj', condition='Dengue'
res_add = s.post("http://127.0.0.1:5000/api/patients/SS-TEST-001/records", json={
    "condition": "Dengue",
    "ward": "Katraj",
    "medicines": ["Paracetamol 650mg", "ORS"],
    "notes": "Testing OPD record logging with Katraj ward and Dengue condition",
    "dosage": "1 tab TID",
    "refill_restricted": False
})
print("5. Add record:", res_add.status_code, res_add.json())

# 6. Re-check ML forecast for Katraj Dengue
res_after = s.get("http://127.0.0.1:5000/api/surveillance/ml-forecast?ward=Katraj&disease=dengue")
print("6. Post-check ML forecast Katraj Dengue:", res_after.json().get("forecast", {}).get("display_cases"), res_after.json().get("forecast", {}).get("raw_cases"))

# 7. Re-check ward matrix
res_mat = s.get("http://127.0.0.1:5000/api/surveillance/ward-matrix?disease=dengue")
katraj_post = next((w for w in res_mat.json().get("wards", []) if w.get("ward") == "Katraj"), None)
print("7. Post-check Katraj in ward matrix:", katraj_post)
