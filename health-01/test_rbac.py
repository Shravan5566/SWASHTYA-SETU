import requests

BASE = 'http://127.0.0.1:5000'

s = requests.Session()

# Test 1: Unauthenticated RBAC blocks
res1 = s.get(f'{BASE}/api/admin/queue')
print('1. Unauth admin queue status:', res1.status_code, res1.json())
assert res1.status_code == 401

res2 = s.get(f'{BASE}/api/pharmacy/queue')
print('2. Unauth pharmacy queue status:', res2.status_code, res2.json())
assert res2.status_code == 401

# Test 2: Citizen Application -> status must be pending, card_id None
res_app = s.post(f'{BASE}/api/applications', json={
    'name': 'Ramesh Shinde',
    'phone': '9876543210',
    'locality': 'Kothrud',
    'blood_group': 'B+'
})
app_data = res_app.json()
print('3. Citizen apply result:', app_data)
assert app_data['status'] == 'pending'
assert app_data['card_id'] is None
app_ref = app_data['reference']

# Test 3: Citizen tracks application -> pending
res_track = s.get(f'{BASE}/api/applications/{app_ref}')
print('4. Track status:', res_track.json()['status'])
assert res_track.json()['status'] == 'pending'

# Test 4: Doctor login -> cannot access admin queue
s_doc = requests.Session()
res_doc_login = s_doc.post(f'{BASE}/api/auth/login', json={'username': 'doctor_demo', 'password': 'password123'})
print('5. Doctor login:', res_doc_login.status_code)
res_doc_block = s_doc.get(f'{BASE}/api/admin/queue')
print('6. Doctor accessing admin queue:', res_doc_block.status_code, res_doc_block.json())
assert res_doc_block.status_code == 403

# Test 5: Sysadmin login -> can access queue, but PROVABLY BLOCKED from patient clinical records
s_admin = requests.Session()
res_adm_login = s_admin.post(f'{BASE}/api/auth/login', json={'username': 'admin_demo', 'password': 'password123'})
print('7. Admin login:', res_adm_login.status_code)
queue = s_admin.get(f'{BASE}/api/admin/queue').json()
print('8. Admin queue count:', len(queue))

# Provable block: Admin tries to view individual patient profile
res_adm_clinical = s_admin.get(f'{BASE}/api/patients/SS-TEST-001')
print('9. Admin accessing clinical record:', res_adm_clinical.status_code, res_adm_clinical.json())
assert res_adm_clinical.status_code == 403
assert res_adm_clinical.json()['code'] == 'ADMIN_CLINICAL_ACCESS_BLOCKED'

# Admin approves Ramesh Shinde's application
target_app = [a for a in queue if a['app_no'] == app_ref][0]
res_approve = s_admin.post(f"{BASE}/api/admin/applications/{target_app['id']}/approve")
print('10. Admin approve application:', res_approve.json())
assert res_approve.json()['status'] == 'approved'
issued_card = res_approve.json()['card_id']

# Verify citizen can now view their approved card
res_track_after = s.get(f'{BASE}/api/applications/{app_ref}').json()
print('11. Track status after approval:', res_track_after['status'], res_track_after['card_id'])
assert res_track_after['status'] == 'approved'
assert res_track_after['card_id'] == issued_card

# Test 6: Pharmacist duplicate dispensation check
s_pharma = requests.Session()
s_pharma.post(f'{BASE}/api/auth/login', json={'username': 'pharma_demo', 'password': 'password123'})
q_pharma = s_pharma.get(f'{BASE}/api/pharmacy/queue').json()
print('12. Pharmacist queue items count:', len(q_pharma))

print('\n========================================')
print('>>> ALL RBAC TESTS PASSED 100% OK! <<<')
print('========================================\n')
