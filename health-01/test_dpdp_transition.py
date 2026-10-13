import requests

s = requests.Session()
# 1. Login as doctor
res = s.post("http://127.0.0.1:5000/api/auth/login", json={
    "username": "doctor_demo",
    "password": "password123"
})
print("1. Login:", res.status_code)

# 2. Get card SS-TEST-002 via Emergency Break-Glass
res_bg = s.post("http://127.0.0.1:5000/api/consent/emergency", json={
    "card_id": "SS-TEST-002",
    "reason": "Suspected Malaria high fever evaluation"
})
token = res_bg.json().get("grant", {}).get("token")
s.headers.update({"X-Consent-Token": token})

# Reset Hadapsar Malaria stat to 4 (deliberately < 5 for DPDP test)
res_spike = s.post("http://127.0.0.1:5000/api/surveillance/simulate-spike", json={
    "ward": "Hadapsar",
    "disease": "malaria",
    "cases": 4
})
print("2. Set Hadapsar Malaria baseline to 4:", res_spike.status_code)

# 3. Check ML forecast before OPD consultation
res_before = s.get("http://127.0.0.1:5000/api/surveillance/ml-forecast?ward=Hadapsar&disease=malaria")
f_before = res_before.json().get("forecast", {})
print("3. BEFORE OPD Checkup:")
print("   - Raw cases:", f_before.get("raw_cases"))
print("   - Display cases:", f_before.get("display_cases"))
print("   - Is Suppressed by DPDP:", f_before.get("is_suppressed"))

# 4. Doctor logs an OPD consultation in Hadapsar for Malaria
res_opd = s.post("http://127.0.0.1:5000/api/patients/SS-TEST-002/records", json={
    "condition": "Malaria",
    "ward": "Hadapsar",
    "medicines": ["Chloroquine 250mg", "Primaquine"],
    "notes": "Chills, rigor, peripheral smear confirmed Plasmodium vivax",
    "dosage": "As per NVBDCP regimen",
    "refill_restricted": False
})
print("4. OPD Log Result:", res_opd.status_code, res_opd.json())

# 5. Check ML forecast after OPD consultation
res_after = s.get("http://127.0.0.1:5000/api/surveillance/ml-forecast?ward=Hadapsar&disease=malaria")
f_after = res_after.json().get("forecast", {})
print("5. AFTER OPD Checkup:")
print("   - Raw cases:", f_after.get("raw_cases"))
print("   - Display cases:", f_after.get("display_cases"))
print("   - Is Suppressed by DPDP:", f_after.get("is_suppressed"))
print("   - Anomaly Status:", f_after.get("anomaly_status"))
print("   - Predicted Next Week:", f_after.get("predicted_cases_next_week"))
