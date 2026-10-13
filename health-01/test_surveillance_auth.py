import requests

s = requests.Session()
# 1. Login as doctor
res = s.post("http://127.0.0.1:5000/api/auth/login", json={
    "username": "doctor_demo",
    "password": "password123"
})
print("1. Login:", res.status_code, res.json().get("user", {}).get("name"))

# 2. Test /api/surveillance endpoint
r_surv = s.get("http://127.0.0.1:5000/api/surveillance")
print("2. /api/surveillance status:", r_surv.status_code)
if r_surv.status_code == 200:
    data = r_surv.json()
    print("   Total Cases:", data.get("cases"))
    print("   Total Cells:", len(data.get("cells", [])))
    print("   Anomalies:", data.get("anomalies"))
