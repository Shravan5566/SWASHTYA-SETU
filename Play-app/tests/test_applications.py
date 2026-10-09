import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.patient import Patient
from app.models.application import Application
from app.utils.seed import seed_staff_accounts


def test_applications_workflow():
    app = create_app()
    with app.app_context():
        db.create_all()
        Application.query.delete()
        db.session.commit()
        seed_staff_accounts()

    client = app.test_client()

    print("\n--- 0. Testing GET separate application pages ---")
    assert client.get("/apply/health-card").status_code == 200
    assert client.get("/apply/staff").status_code == 200
    assert client.get("/apply/status").status_code == 200
    print("[*] All separate application pages (health-card, staff, status) return HTTP 200.")

    print("\n--- 1. Testing Patient Health Card Application Submission ---")
    res_pat = client.post(
        "/apply/health-card",
        data={
            "full_name": "Suresh Balkrishna Patil",
            "phone": "9822012345",
            "email": "suresh.patil@example.com",
            "dob": "1988-04-12",
            "gender": "Male",
            "blood_group": "B+",
            "gov_id_type": "Aadhaar Card",
            "gov_id_number": "123456789012",
            "locality": "Katraj",
            "address": "Flat 204, Shivneri Heights, Katraj, Pune 411046",
            "emergency_name": "Aarti Patil",
            "emergency_relation": "Spouse",
            "emergency_phone": "9822099999",
            "chronic_conditions": "Hypertension",
            "allergies": "None",
        },
        follow_redirects=True,
    )
    assert res_pat.status_code == 200
    with app.app_context():
        pat_app = Application.query.filter_by(phone="9822012345").first()
        assert pat_app is not None
        assert pat_app.role == "patient"
        assert pat_app.status == "pending"
        pat_app_id = pat_app.id
        pat_app_no = pat_app.app_no
        print(f"[*] Patient application registered: {pat_app.app_no} for {pat_app.full_name}")

    print("\n--- 2. Testing Doctor Staff Application Submission ---")
    res_doc = client.post(
        "/apply/staff",
        data={
            "role": "doctor",
            "full_name": "Dr. Milind Joshi",
            "email": "dr.milind.joshi@punehealth.org",
            "phone": "9823054321",
            "gov_id_type": "Aadhaar/PAN",
            "gov_id_number": "ABCDE1234F",
            "council_reg_no": "MMC-2016-10492",
            "qualification": "MBBS, MD (Medicine)",
            "specialization": "Internal Medicine",
            "experience_years": "8",
            "workplace_name": "Sancheti Hospital & Clinic",
            "workplace_address": "16 Shivajinagar, Pune 411005",
            "locality": "Shivajinagar",
        },
        follow_redirects=True,
    )
    assert res_doc.status_code == 200
    with app.app_context():
        doc_app = Application.query.filter_by(phone="9823054321").first()
        assert doc_app is not None
        assert doc_app.role == "doctor"
        assert doc_app.status == "pending"
        doc_app_id = doc_app.id
        print(f"[*] Doctor application registered: {doc_app.app_no} for {doc_app.full_name}")

    print("\n--- 3. Testing Pharmacist Staff Application Submission ---")
    res_phm = client.post(
        "/apply/staff",
        data={
            "role": "pharmacist",
            "full_name": "Pooja Deshmukh",
            "email": "pooja.d@medpluspune.com",
            "phone": "9824098765",
            "gov_id_type": "Aadhaar/PAN",
            "gov_id_number": "MSPC-9988",
            "council_reg_no": "MSPC-84210",
            "qualification": "B.Pharm",
            "specialization": "Hospital Pharmacy",
            "experience_years": "4",
            "workplace_name": "MedPlus Dispensary Kothrud",
            "workplace_address": "Shop 4, Paud Road, Kothrud, Pune 411038",
            "locality": "Kothrud",
        },
        follow_redirects=True,
    )
    assert res_phm.status_code == 200
    with app.app_context():
        phm_app = Application.query.filter_by(phone="9824098765").first()
        assert phm_app is not None
        assert phm_app.role == "pharmacist"
        phm_app_id = phm_app.id
        print(f"[*] Pharmacist application registered: {phm_app.app_no} for {phm_app.full_name}")

    print("\n--- 4. Testing Public Status Tracker ---")
    res_status = client.get(f"/apply/status?q={pat_app_no}", headers={"X-Requested-With": "XMLHttpRequest"})
    assert res_status.status_code == 200
    json_data = res_status.get_json()
    assert json_data["found"] is True
    assert json_data["status"] == "pending"
    print(f"[*] Status tracker verified: {json_data['app_no']} -> {json_data['status']}")

    print("\n--- 5. Testing SysAdmin Login & Screening Page ---")
    with client:
        # Login as sysadmin
        login_res = client.post("/login", data={"username": "admin_demo", "password": "password123"}, follow_redirects=True)
        assert login_res.status_code == 200

        # View applications
        apps_page = client.get("/admin/applications")
        assert apps_page.status_code == 200
        page_content = apps_page.get_data(as_text=True)
        assert "Suresh Balkrishna Patil" in page_content
        assert "Dr. Milind Joshi" in page_content
        assert "Pooja Deshmukh" in page_content
        print("[*] SysAdmin successfully viewed all 3 pending applications on screening dashboard.")

        print("\n--- 6. Testing SysAdmin Approves Doctor Application ---")
        app_doc_res = client.post(f"/admin/applications/{doc_app_id}/approve", follow_redirects=True)
        assert app_doc_res.status_code == 200
        with app.app_context():
            doc_app_reloaded = Application.query.get(doc_app_id)
            assert doc_app_reloaded.status == "approved"
            assert doc_app_reloaded.assigned_username is not None
            # Check user account was created in users table
            created_user = User.query.filter_by(username=doc_app_reloaded.assigned_username).first()
            assert created_user is not None
            assert created_user.role == "doctor"
            assert created_user.full_name == "Dr. Milind Joshi"
            print(f"[*] Doctor approved! Created user: {created_user.username} with role={created_user.role}")

        print("\n--- 7. Testing SysAdmin Approves Patient Health Card Application ---")
        app_pat_res = client.post(f"/admin/applications/{pat_app_id}/approve", follow_redirects=True)
        assert app_pat_res.status_code == 200
        with app.app_context():
            pat_app_reloaded = Application.query.get(pat_app_id)
            assert pat_app_reloaded.status == "approved"
            assert pat_app_reloaded.assigned_card_id is not None
            # Check patient was created in patients table
            created_patient = Patient.query.filter_by(card_id=pat_app_reloaded.assigned_card_id).first()
            assert created_patient is not None
            print(f"[*] Patient Health Card approved! Issued Card ID: {created_patient.card_id}")

        print("\n--- 8. Testing SysAdmin Rejects Pharmacist Application with Reason ---")
        rej_res = client.post(
            f"/admin/applications/{phm_app_id}/reject",
            data={"reason": "State pharmacy council registration license expired."},
            follow_redirects=True,
        )
        assert rej_res.status_code == 200
        with app.app_context():
            phm_app_reloaded = Application.query.get(phm_app_id)
            assert phm_app_reloaded.status == "rejected"
            assert "expired" in phm_app_reloaded.admin_notes
            print(f"[*] Pharmacist application rejected with note: {phm_app_reloaded.admin_notes}")

    print("\n=======================================================")
    print(">>> ALL APPLICATION & SCREENING TESTS PASSED (100%) <<<")
    print("=======================================================\n")


if __name__ == "__main__":
    test_applications_workflow()
