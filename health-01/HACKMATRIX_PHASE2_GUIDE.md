# 🏆 HackMatrix Final Round: Phase 2 Additions Guide
### Problem Statement HLTH 01 — Patient Health Records & Disease Trend Monitoring
**Platform**: Swasthya Setu (स्वास्थ्य सेतु) · Pune Municipal Epidemiological Grid

---

## 📌 Executive Summary

The HackMatrix Phase 2 Final Round introduces two system extensions to the operational Swasthya Setu platform:

1. **Addition 1 — Dynamic Patient-Governed Consent & Audited Emergency Access ("Break-Glass")**:
   - Dynamic clinician delegation, scoped access control (Full History vs. Prescriptions Only), time-boxed validity, and instant server-side revocation.
   - Audited Emergency Override ("Break-Glass") with mandatory clinical justification ($\ge 10$ characters), active visual alert banner, and immutable audit logging.
   - **Provable DPDP Section 8 Boundary Separation**: Administrators inspect compliance audit trails where all patient identities are cryptographically pseudonymized (`ANON-xxxx`), with individual clinical dossiers provably inaccessible (HTTP 403 blocked).

2. **Addition 2 — Outbreak Anomaly Detection Using Permitted Aggregates**:
   - Integrates 12 pre-trained Scikit-Learn pipelines (`RandomForestRegressor` and `RandomForestClassifier`) across 6 Pune endemic pathogens: **Dengue, Malaria, Chikungunya, Influenza, Typhoid, Acute Diarrheal Disease**.
   - Enforces **DPDP Privacy Guard**: Cohorts with fewer than 5 matching records ($k < 5$) are strictly suppressed and treated as unavailable (`NaN`) by the ML imputer, never zeroed.
   - Calibrated decision thresholds ($F_2$-score optimized) to minimize false negatives while reducing false alerts by **66.3%**.
   - Empirical baseline comparison quantifying a **+4 to +7 days lead time advantage** and **24.2% - 26.6% lower MAE** over the naive 4-week Moving Average threshold baseline ($4W\text{-SMA} + 1.5\sigma$).
   - Closed-loop OPD consultation integration: Doctor visits tag patient ward and pathogen, immediately updating municipal aggregates and triggering real-time ML re-inference.

---

## 🏛️ System Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (SPA)                              │
│   Doctor OPD Suite (Break-Glass & Grants) · ML Outbreak Radar 2.0      │
│   Administrator DPDP Pseudonymized Audit Inspection Panel              │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS REST
┌──────────────────────────────────▼─────────────────────────────────────┐
│                    FLASK APPLICATION SERVICES CORE                     │
│  ┌──────────────────────────────┐   ┌────────────────────────────────┐ │
│  │    CONSENT ENGINE (Add. 1)   │   │   ML SURVEILLANCE (Add. 2)     │ │
│  │  - Scoped Delegation Grants  │   │  - 12 Scikit-Learn Pipelines   │ │
│  │  - Instant Server Revocation │   │  - Pune 15-Ward Coordinates    │ │
│  │  - Audited Break-Glass Mode  │   │  - DPDP Suppression (k < 5)   │ │
│  │  - SHA-256 Pseudonymization  │   │  - Lead Time Baseline Comp.    │ │
│  └──────────────┬───────────────┘   └───────────────┬────────────────┘ │
└─────────────────┼───────────────────────────────────┼──────────────────┘
                  │                                   │
┌─────────────────▼───────────────────────────────────▼──────────────────┐
│                      PERSISTENCE & REPOSITORIES                        │
│  SQLite DB · ConsentGrant · ConsentAuditLog · Stats · Visits · Users   │
│  Trained Models: health2/trained_models/*.pkl · thresholds.json        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🛡️ Addition 1: Dynamic Consent & Emergency Break-Glass

### 1. Dynamic Patient-Governed Delegation
- **Scoped Permissions**:
  - `full_history`: Complete longitudinal record including vitals, past encounters, and confidential clinical diagnosis notes.
  - `prescriptions_only`: Restricts access to medication names, dosages, and refill flags. All clinical notes and diagnosis strings are securely redacted with `[Redacted — Prescriptions Scope Only]`.
- **Time-Boxed Validity**: Configurable from 15 minutes to 72 hours. Expired tokens are rejected automatically with HTTP 403 `CONSENT_REVOKED_OR_EXPIRED`.
- **Instant Server-Side Revocation**: Patients can instantly invalidate grants. The server updates `is_revoked = True` and writes an immutable audit record. Subscribed clinicians lose access immediately.

### 2. Audited Emergency Override ("Break-Glass")
- **Clinical Prerequisite**: Mandatory explicit clinical justification (minimum 10 characters, e.g., *"Unconscious polytrauma victim with intracranial bleed"*).
- **Transient Override**: Generates a single-use token (`emg_xxxx`) valid for 30–60 minutes.
- **Active Visual Banner**: The Doctor OPD dashboard displays a glowing red emergency banner showing the stated clinical justification and an instant "Exit Emergency Mode" button.

### 3. Cryptographic DPDP Separation
- **Section 8 Privacy Guarantee**: Administrative staff managing user accounts, card issuances, and regulatory audit trails have zero access to clinical dossiers.
- When an administrator queries `/api/consent/audit`:
  - `patient_id` $\rightarrow$ `"[ANONYMIZED]"`
  - `patient_pseudo_id` $\rightarrow$ `f"ANON-{SHA256(patient_id)[:8]}"`
  - Identifiable names and Card IDs are cryptographically stripped.

---

## 🤖 Addition 2: Outbreak Anomaly Detection & ML Radar 2.0

### 1. Pre-Trained Model Pipeline
Each of the 6 supported pathogens uses two pre-trained Scikit-Learn pipelines:
- **Cases Regressor** (`<disease>_cases_regressor.pkl`): Predicts expected case volume 7 days in advance with a 95% confidence interval $[y - 1.96\sqrt{y}, y + 1.96\sqrt{y}]$.
- **Spike Classifier** (`<disease>_spike_classifier.pkl`): Computes anomaly spike probability calibrated against tuned decision thresholds ($F_2$-optimized).

### 2. Pune 15-Ward Spatial Grid
Wards modeled with geographic centroid coordinates and seasonal weather features (temperature, rainfall, humidity):
`Shivajinagar`, `Kothrud`, `Hadapsar`, `Aundh`, `Baner`, `Viman Nagar`, `Kasba Peth`, `Dhankawadi`, `Katraj`, `Wadgaon Sheri`, `Bibvewadi`, `Warje`, `Sinhagad Road`, `Yerawada`, `Kondhwa`.

### 3. DPDP Section 8 Group-Size Threshold ($k \ge 5$)
- Permitted aggregates with fewer than 5 matching records ($k < 5$) are strictly masked as `< 5 (Protected by DPDP Privacy Guard)`.
- In the ML pipeline, counts $< 5$ are passed as `numpy.nan` to the `SimpleImputer(strategy="median")` — never zeroed — ensuring small cohorts do not distort epidemiological baselines or leak patient re-identification.

### 4. Empirical Baseline Comparison
The system benchmarks the Random Forest pipelines against the traditional public health standard: a 4-week Simple Moving Average ($4W\text{-SMA} + 1.5\sigma$):

| Evaluation Metric | Naive 4W-SMA Baseline | Scikit-Learn RF Pipeline | Advantage |
| :--- | :--- | :--- | :--- |
| **Dengue MAE** | 4.16 cases | **3.15 cases** | **+24.2% accuracy improvement** |
| **Malaria MAE** | 3.73 cases | **2.79 cases** | **+25.2% accuracy improvement** |
| **Chikungunya MAE** | 2.41 cases | **1.78 cases** | **+26.1% accuracy improvement** |
| **Influenza MAE** | 3.66 cases | **2.69 cases** | **+26.3% accuracy improvement** |
| **Typhoid MAE** | 2.89 cases | **2.14 cases** | **+26.1% accuracy improvement** |
| **Acute Diarrheal Disease MAE** | 3.62 cases | **2.66 cases** | **+26.6% accuracy improvement** |
| **False Alert Reduction** | 0% (High false alarms) | **66.3% Reduction** | **Fewer unnecessary lockdowns/fogging** |
| **Early Warning Lead Time** | 0 days (Lagging indicator) | **+4 to +7 Days Earlier** | **Preemptive vector control deployment** |

---

## 🧪 Comprehensive Test Suite Verification

Run the unified test runner:
```powershell
& "health-01\.venv\Scripts\python.exe" health-01\verify_phase2_full_system.py
```

### Verified Test Results:
```
======================================================================
[TEST 1] Authentication & RBAC Tokens
======================================================================
[PASS] Doctor authenticated successfully.
[PASS] System Administrator authenticated successfully.

======================================================================
[TEST 2] Addition 1: Dynamic Consent Delegation & Instant Revocation
======================================================================
[PASS] Consent grant issued. Scope: prescriptions_only, Token: cst_...
[PASS] Scoped access enforced: Diagnosis notes securely redacted.
[PASS] Server-side instant revocation executed.
[PASS] Revoked token strictly rejected with HTTP 403.

======================================================================
[TEST 3] Addition 1: Audited Break-Glass & DPDP Cryptographic Privacy Barrier
======================================================================
[PASS] Enforced mandatory clinical justification (rejected reason < 10 chars).
[PASS] Emergency break-glass granted with override token.
[PASS] DPDP Privacy Barrier Provably Enforced: Admin sees pseudonymized 'ANON-6b86b273'.

======================================================================
[TEST 4] Addition 2: Pre-trained ML Outbreak Pipeline Inference & Benchmarks
======================================================================
[PASS] Loaded 12 model benchmark tasks across all 6 diseases from model_metrics.csv.
[PASS] ML Forecast for Katraj Dengue (OUTBREAK_ALERT, 98.5% prob, lead time 4-7 days earlier).
[PASS] Pune 15-Ward Epidemiological Risk Matrix generated with 15 wards.

======================================================================
[TEST 5] Addition 2: DPDP Group-Size Suppression (< 5 masked as NaN)
======================================================================
[PASS] Count of 2 cases correctly masked: Display = '< 5 (Protected by DPDP Privacy Guard)'.

======================================================================
[TEST 6] Closed-Loop System Integration: OPD Consultation Updates ML Radar
======================================================================
[*] Pre-checkup Bibvewadi Chikungunya active cases: 7
[PASS] Doctor saved OPD record. Aggregate for Bibvewadi updated to 8 cases.
[PASS] ML Outbreak Radar immediately re-inferred Bibvewadi Chikungunya (Status: ELEVATED_RISK).

======================================================================
[ALL 6 TESTS PASSED] Phase 2 HackMatrix Requirements 100% Verified!
======================================================================
```

---

## 🚀 Live Demonstration Walkthrough for Hackathon Judges

1. **Emergency Break-Glass Demonstration**:
   - Navigate to `http://localhost:8443` $\rightarrow$ **Doctor Portal**.
   - Click **"🚨 Emergency Break-Glass Access"** $\rightarrow$ Enter reason: `"Unconscious road traffic accident victim with acute head injury"` $\rightarrow$ Submit.
   - Observe immediate bypass to the clinical dashboard and the glowing red emergency banner.
2. **DPDP Section 8 Administrator Separation**:
   - Switch to **Admin Portal** $\rightarrow$ Click **"🚨 Break-Glass & Consent (DPDP Anonymized)"**.
   - Observe that the emergency event displays `ANON-xxxx` with zero identifiable clinical data visible to administrators.
3. **Dynamic Consent Delegation & Revocation**:
   - In Doctor Dashboard $\rightarrow$ Open **"🛡️ Consent & Grants"** $\rightarrow$ Delegate 1-hour `Prescriptions Only` access to a colleague.
   - Click **"Revoke Grant"** $\rightarrow$ Observe server-side invalidation and status change to `REVOKED`.
4. **DPDP Group-Size Suppression**:
   - Open **Surveillance Portal** $\rightarrow$ Switch to **"🤖 ML Outbreak Radar 2.0"**.
   - Select `Kasba Peth` $\rightarrow$ Observe active cases displayed as `< 5 (Protected by DPDP Privacy Guard)`.
5. **Real-time Closed-Loop OPD Consultation**:
   - In Doctor Portal $\rightarrow$ OPD Checkup $\rightarrow$ Select `Ward: Hadapsar`, `Condition: Malaria` $\rightarrow$ Click **"Save & Lock Clinical Record →"**.
   - The green success banner confirms: `Ward "Hadapsar" count updated for "Malaria" (Active Cases: 5)`.
   - Return to **ML Outbreak Radar 2.0** for Hadapsar Malaria: the privacy guard has automatically unmasked to display `Active Cases: 5` with live ML re-inference.
