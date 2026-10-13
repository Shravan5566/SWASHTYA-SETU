# 🏥 Swasthya Setu (स्वास्थ्य सेतु)
### Pune Municipal Corporation · Digital Citizen Health Identity, Dynamic Consent & Epidemiological Surveillance Platform

[![React](https://img.shields.io/badge/Frontend-React_19_+_TypeScript-blue.svg)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS_v4-38bdf8.svg)](https://tailwindcss.com/)
[![Flask](https://img.shields.io/badge/Backend-Python_Flask_3.x-green.svg)](https://flask.palletsprojects.com/)
[![AI Engine](https://img.shields.io/badge/AI-Google_Gemini_Flash-orange.svg)](https://ai.google.dev/)
[![ML Pipeline](https://img.shields.io/badge/ML-Random_Forest_Epidemic_Forecaster-darkgreen.svg)](https://scikit-learn.org/)
[![Email Engine](https://img.shields.io/badge/Email-Brevo_HTTPS_Port_443-purple.svg)](https://www.brevo.com/)
[![Compliance](https://img.shields.io/badge/Compliance-DPDP_Act_2023_Aligned-red.svg)](https://www.meity.gov.in/)

---

## ⚡ Quick Start: Run the Whole Project (Single Command)

The unified server runs both the **React 19 Frontend SPA** and the **Flask REST Core & ML Subsystems** seamlessly on **`http://127.0.0.1:5000`**.

### 💻 Using Git Bash / Linux / macOS (Recommended)
```bash
# Clone & navigate to project directory
cd "c:/Users/SHRA1/Desktop/SS pccoe"

# Run universal startup script (seeds DB, verifies build & launches server)
./start.sh
```

### 💻 Using Windows PowerShell
```powershell
cd "c:\Users\SHRA1\Desktop\SS pccoe"
.\start.ps1
```

### 💻 Using Windows Command Prompt (`cmd`)
```cmd
cd /d "c:\Users\SHRA1\Desktop\SS pccoe"
start.bat
```

> 🌐 **Open in Browser**: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**  
> ☁️ **Hosted Cloud Deployment**: **[https://health-bridge.up.railway.app](https://health-bridge.up.railway.app)**

---

## 🔑 Master Demo Credentials (For Hackathon Judges & Evaluators)

All four healthcare and administrative portals use the master demo password: **`password123`**

| Role | Username | Password | Direct Portal Route | Core Capabilities & Permissions |
|:---|:---|:---|:---|:---|
| **Attending Doctor** | `doctor_demo` | `password123` | [`/#/doctor`](http://127.0.0.1:5000/#/doctor) | WebRTC camera QR scan, patient email OTP verification, AI voice prescription dictation, 24h record lock |
| **Dispensary Pharmacist** | `pharma_demo` | `password123` | [`/#/pharmacist`](http://127.0.0.1:5000/#/pharmacist) | QR check-in, 4-column DPDP prescription view (diagnosis notes hidden), real-time dispense queue |
| **Public Health Officer** | `public_demo` | `password123` | [`/#/surveillance`](http://127.0.0.1:5000/#/surveillance) | Pune 15-Ward risk matrix, pre-trained Random Forest outbreak forecasts, $k < 5$ suppression |
| **System Administrator** | `admin_demo` | `password123` | [`/#/admin`](http://127.0.0.1:5000/#/admin) | Accreditation reviews, auto-provisioning with email dispatch, DPDP pseudonymized audit logs |

### 🪪 Pre-Seeded Patient Health Cards & Scannable QR Codes
Generated in [`demo_qr_cards/`](file:///c:/Users/SHRA1/Desktop/SS%20pccoe/demo_qr_cards) and on your Desktop:
- **`SS-TEST-001`**: Meera Joshi (`+919876543210`) — *Shivajinagar (Ward A)*  
  • Visit 1: Flu, Cold & Cough (Immutable baseline).  
  • Visit 2: Hypertension (`refill_restricted=True` — shows as blocked in Pharmacist portal).
- **`SS-TEST-002`**: Arjun Sharma (`+919876543211`) — *Kothrud (Ward B)*  
  • Visit 1: Viral Fever & Joint Pain.  
  • Visit 2: Type 2 Diabetes (Metformin & Atorvastatin).
- **`SS-TEST-003`**: Priya Sen (`+919876543212`) — *Katraj (Ward C)*  
  • Dengue & Dehydration. Case count (< 5) demonstrates the `< 5 (Protected by DPDP Privacy Guard)` suppression.

---

## 📌 Executive Overview

**Swasthya Setu** is an enterprise-grade digital health ecosystem built for municipal health administrations (demonstrated on the **Pune Municipal Corporation** jurisdiction). The system solves five fundamental healthcare delivery challenges:

1. **Fragmented Patient Records**: Eliminates physical paper folders through a unified, cryptographically secure **Digital Citizen Health ID Card** with a scannable high-contrast QR code.
2. **DPDP Act 2023 Aligned Dynamic Consent**: Doctors cannot access clinical history without an explicit **6-digit OTP** sent via live email or an active **scoped consent token**. Patients can revoke access at any second with instant revocation.
3. **Audited Emergency Break-Glass**: In life-threatening trauma cases, clinicians can initiate audited emergency access with mandatory clinical justification, while administrators only see cryptographic pseudonymized IDs (`ANON-xxxx`) upholding patient privacy.
4. **Clinical Speed & Safety**: Equips doctors with **Google Gemini AI Multilingual Voice Prescription Dictation** and real-time **Drug-Drug Interaction (DDI) Safety Alerts**.
5. **Epidemiological Early Warning & Machine Learning**: Integrates pre-trained **Random Forest regression and spike anomaly classifiers** trained on 7 years of municipal ward time-series data, providing 4 to 7 day advance outbreak warnings with 66.3% false alert reduction.

---

## 🏗️ Architecture & Technology Stack

```
┌────────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER (SPA)                              │
│   React 19 · TypeScript · Vite 8 · Tailwind CSS v4 · QR WebRTC Scanner │
│   Bilingual (English / Marathi) · Web Audio API Voice Dictation        │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │ HTTPS REST API
┌──────────────────────────────────▼─────────────────────────────────────┐
│                       APPLICATION BACKEND (FLASK)                      │
│   Python 3.11/3.12 · Flask REST Core · Flask-Login · Rate Limiter       │
│   Role-Based Access Control (RBAC) · Append-Only Access Audit Trail    │
└──────────┬───────────────────────┬──────────────────────┬──────────────┘
           │                       │                      │
┌──────────▼──────────┐ ┌──────────▼──────────┐ ┌─────────▼─────────────┐
│   DATABASE & CRYPTO │ │   AI & ML SUBSYSTEM │ │ NOTIFICATION ENGINE   │
│ SQLite + SQLAlchemy │ │ Pretrained ML Models│ │ Brevo HTTPS API (443) │
│ Fernet PII Encrypt  │ │ Gemini Flash Voice  │ │ Inline PNG Card Gen   │
│ k-Anonymity (k ≥ 5) │ │ RF Outbreak Forecast│ │ Gmail SMTP Fallback   │
└─────────────────────┘ └─────────────────────┘ └───────────────────────┘
```

---

## 🌟 Comprehensive Feature Catalog

### 1. 🪪 Citizen Enrollment & Health Identity Card
- **3-Step Application Wizard**:
  - Step 1: Legal Name, Phone Number, Email, Age, Gender, and Date of Birth.
  - Step 2: Pune Ward selection (15 municipal wards), Blood Group, Drug Allergies, Chronic Conditions.
  - Step 3: Real-time dual-sided card preview, DPDP Act 2023 declaration, and instant submission.
- **Dual-Sided Smart Card Design**:
  - **Front Face**: Official Swasthya Setu tricolor hands-heart emblem, NFC wave symbol, "SCAN • CARE • TOGETHER", "PATIENT HEALTH ID".
  - **Back Face**: Framing brackets, unique scannable 2D QR Code, Permanent Card ID, Demographic List (Name, Age, Gender, Blood Group), security seal.
- **Automated High-Resolution Graphic Generator**: Dynamically renders 300 DPI composite cards via Pillow (`card_image_service.py`) attached as `Swasthya_Setu_Health_Card.png` to confirmation emails.

### 2. 🔐 DPDP Consent-Driven Doctor OPD Desk
- **WebRTC Camera QR Scanner & Manual ID Entry**: Instant card detection from physical cards or smartphone displays.
- **Privacy Gate & OTP Authorization**:
  - Scanning a card requires patient authorization.
  - Generates a **6-digit cryptographic OTP** delivered to patient email via Brevo HTTPS / SMTP and displayed in the terminal for demo convenience.
  - Creates a time-bounded 5-minute clinical access session upon entry.
- **Dynamic Consent Delegation**:
  - Patient can delegate granular scopes: `full_history`, `vitals_and_allergies`, or `prescriptions_only`.
  - Diagnosis notes are cryptographically redacted if scope is restricted to prescriptions only.
- **Instant Revocation**: Patient can revoke doctor access at any time; subsequent queries immediately return HTTP 403 Forbidden.
- **Audited Emergency Break-Glass**:
  - In critical trauma scenarios, doctors can initiate emergency override with mandatory clinical justification (min 10 characters).
  - Admin audit logs display pseudonymized token `ANON-xxxx` with zero identifiable clinical data.
- **AI Voice Prescription Dictation**:
  - Doctors click mic and dictate prescriptions in natural English/Hindi/Marathi.
  - Google Gemini AI parses medication name, dosage, frequency, and instructions into structured forms.
- **Real-Time Drug Interaction Alerts**: Automatic cross-referencing against clinical conflict databases (e.g. Paracetamol + Alcohol, Metformin + Contrast).

### 3. 💊 Dispensary Pharmacist Desk
- **Privacy-Preserving 4-Column View**: Strictly isolates data so pharmacists see only Medicine Name, Dosage, Date, and Card ID. Full clinical diagnosis notes and chief complaints are hidden.
- **Refill Lock Enforcement**: Flags restricted or controlled medicines requiring fresh doctor consultations before dispensing.
- **One-Click Dispense Queue**: Marks prescriptions as fulfilled with immutable timestamp and pharmacist identification.

### 4. 📊 Public Health Surveillance & Epidemic ML Forecaster
- **15 Pune Municipal Wards**: Katraj, Kothrud, Hadapsar, Viman Nagar, Shivajinagar, Baner, Hinjewadi, Swargate, Pimpri, Chinchwad, Yerawada, Camp, Aundh, Bibvewadi, Sinhagad Road.
- **Pre-Trained Machine Learning Models**:
  - Trained on 7 years of multi-disease weekly ward synthetic datasets.
  - Random Forest Regressors predict 7-day case counts with 95% confidence intervals.
  - Spike anomaly classifiers calculate outbreak probabilities with tuned decision thresholds.
  - **Lead Time Advantage**: Outbreaks detected **4 to 7 days earlier** than naive moving-average thresholds with a **66.3% false alert reduction**.
- **$k$-Anonymity Privacy Guard ($k < 5$)**:
  - Counts between 1 and 4 are suppressed and displayed as `< 5 (Protected by DPDP Privacy Guard)`.
  - Treated as NaN/unavailable in ML input rather than zero to prevent statistical inference attacks.

### 5. 🛡️ System Administration & Governance Console
- **Accreditation Screening Queue**: Review pending Doctor and Pharmacist licenses with one-click approval or rejection.
- **Automated Credential Provisioning**: Onboarding an approved staff member automatically dispatches their credentials via email.
- **Append-Only Immutable Audit Trail**: Tracks every authentication event, QR scan, consent delegation, and emergency override with IP and timestamps.

---

## 🧪 Automated Verification & Smoke Tests

Run the complete Phase 2 verification suite to test all subsystems:
```bash
python health-01/verify_phase2_full_system.py
```

**Test Suite Coverage (6/6 Tests):**
- `[TEST 1]` Authentication & Role-Based Access Control Tokens
- `[TEST 2]` Dynamic Consent Delegation & Instant Server-Side Revocation
- `[TEST 3]` Audited Emergency Break-Glass & DPDP Cryptographic Pseudonymization (`ANON-xxxx`)
- `[TEST 4]` Pre-Trained ML Outbreak Pipeline Inference & 12 Disease Model Benchmarks
- `[TEST 5]` DPDP Group-Size Suppression ($k < 5$ masked as NaN)
- `[TEST 6]` Closed-Loop System Integration: Doctor OPD consultation updates live surveillance radar

---

## 🎯 Outbreak Simulator (`simulate_outbreak.py`)

Run the interactive outbreak simulator in a second terminal to trigger real-time spikes for evaluators:
```bash
python simulate_outbreak.py
```
**Menu Options:**
1. **Live Outbreak Cycle**: Starts at normal baseline (3 cases), surges to critical peak (55 cases) flipping the dashboard red, then recovers.
2. **Instant Critical Spike**: Instantly triggers an alert on Katraj Dengue or Bibvewadi Chikungunya.
3. **Reset to Baseline**: Restores clean municipal records.
4. **Simulate Multi-Ward Epidemic Surge**: Simulates a citywide monsoon wave across 5 Pune wards.

---

## 📁 Repository Structure

```
SS pccoe/
├── start.sh                          # Universal startup script (Bash / Linux / macOS)
├── start.ps1                         # Universal startup script (Windows PowerShell)
├── start.bat                         # Startup batch script (Windows Command Prompt)
├── run.py                            # Unified application server launcher (Port 5000)
├── seed.py                           # Database initialization & demo account seeder
├── simulate_outbreak.py              # Interactive Outbreak Simulator for demonstrations
├── requirements.txt                  # Python dependencies
├── package.json                      # React frontend dependencies & scripts
├── vite.config.ts                    # Vite 8 configuration with Tailwind v4 & proxy
├── dist/                             # Pre-compiled high-performance React SPA bundle
├── demo_qr_cards/                    # Pre-generated scannable patient QR test cards
├── app/                              # Flask Application Core
│   ├── config.py                     # Environment & security config
│   ├── extensions.py                 # SQLAlchemy, LoginManager extensions
│   ├── models/                       # Data models (User, Patient, Visit, Consent, Stats)
│   ├── routes/                       # Unified API & portal blueprints
│   │   ├── api_routes.py             # REST API for React frontend
│   │   ├── doctor_routes.py          # Doctor clinical workflows
│   │   └── admin_routes.py           # Admin review & audit
│   └── services/                     # Business Logic Services
│       ├── email_service.py          # Brevo HTTPS Port 443 & SMTP dispatcher
│       ├── card_image_service.py     # High-res dual-sided 300 DPI card graphic generator
│       ├── anomaly_ml_service.py     # Pre-trained Random Forest outbreak pipelines
│       ├── consent_service.py        # DPDP consent delegation & break-glass engine
│       ├── ai_service.py             # Google Gemini AI clinical NLP & voice dictation
│       ├── qr_service.py             # QR generation & encryption
│       └── otp_service.py            # Clinical authorization OTP lifecycle
├── src/                              # Modern React 19 Frontend source code
└── health2/                          # Machine learning training datasets & models
    ├── pune_multi_disease_weekly_synthetic_7years(1).csv
    └── trained_models/               # Serialized scikit-learn models & metrics
```

---

## 🔒 Security & Privacy Compliance Standards

- **DPDP Act 2023 Principles**: Citizen health records are encrypted at rest using Fernet symmetric encryption. Decryption occurs only transiently in memory upon verified patient consent.
- **Port 443 Firewall Immunity**: Outbound email and OTP dispatches use HTTPS REST API (Port 443 via Brevo), ensuring delivery across restrictive institutional firewalls and mobile hotspots.
- **Immutable Forensic Auditing**: Access decisions (allowed, denied, break-glass) are permanently committed to append-only database audit logs.

---

## 📄 License & Attribution

Developed for municipal healthcare digitalization under academic and research collaboration.  
**Pune Municipal Corporation Digital Health Initiative** · 2026.
