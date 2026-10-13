import requests

s = requests.Session()
login_res = s.post("http://127.0.0.1:5000/api/auth/login", json={
    "username": "doctor_demo",
    "password": "password123"
})
print("1. Login:", login_res.status_code)

res = s.post("http://127.0.0.1:5000/api/voice-parse", json={
    "transcript": "रुग्णाला कात्रज भागात तीव्र ताप आणि सांधेदुखी आहे, डेंग्यूचा संशय आहे, पॅरासिटामॉल आणि ओआरएस द्या दिवसातून तीन वेळा"
})
print("2. /api/voice-parse:", res.status_code)
if res.status_code == 200:
    parsed = res.json().get("parsed", {})
    print("   Detected Language:", parsed.get("detected_language"))
    print("   Condition:", parsed.get("condition"))
    print("   Ward:", parsed.get("ward"))
    print("   Medicines:", parsed.get("medicines"))
    print("   Dosage:", parsed.get("dosage"))
    print("   Notes:", parsed.get("notes"))
    print("   Corrections:", parsed.get("corrections_made"))
