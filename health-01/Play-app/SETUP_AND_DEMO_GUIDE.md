# 🚀 Swasthya Setu — Step-by-Step Setup, Demo Passwords & Outbreak Simulator Guide

> **Looking for the master feature directory, visual flowcharts, or full security blueprint?**  
> ➔ **See the main [Project Overview, Portals & Security Blueprint (README.md)](README.md)**

---

## 🎯 Hackathon Judges' 5-Minute Evaluation Walkthrough

Welcome, Judges! If you have only 5 minutes to evaluate **Swasthya Setu**, follow this rapid evaluation script:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   5-MINUTE JUDGE DEMONSTRATION SCRIPT                  │
├──────┬──────────────────────┬─────────────────┬────────────────────────┤
│ Step │ Feature Tested       │ URL / Screen    │ Action to Perform      │
├──────┼──────────────────────┼─────────────────┼────────────────────────┤
│ 1    │ Citizen Application  │ /               │ Click "Apply for Health│
│      │ & e-Card Download    │                 │ Card" or "Track Status"│
├──────┼──────────────────────┼─────────────────┼────────────────────────┤
│ 2    │ Admin Screening      │ /admin          │ Login: admin_demo      │
│      │ & Auto-Provisioning  │ /applications   │ Approve pending card   │
├──────┼──────────────────────┼─────────────────┼────────────────────────┤
│ 3    │ Doctor QR + OTP      │ /doctor/scan    │ Login: doctor_demo     │
│      │ Voice & AI Summary   │                 │ Scan SS-TEST-001 + OTP │
├──────┼──────────────────────┼─────────────────┼────────────────────────┤
│ 4    │ Pharmacist Privacy   │ /pharmacist/scan│ Login: pharma_demo     │
│      │ 4-Column Isolation   │                 │ Scan SS-TEST-001       │
├──────┼──────────────────────┼─────────────────┼────────────────────────┤
│ 5a   │ Disease Trend        │ /public-health/ │ Login: health_demo     │
│      │ Detector (NEW!)      │ trend-forecast  │ See WATCH/ELEVATED/    │
│      │ 3-7 Day Forecast     │                 │ CRITICAL colour cards  │
├──────┼──────────────────────┼─────────────────┼────────────────────────┤
│ 5b   │ Live Outbreak Radar  │ /public-health/ │ Run simulate_outbreak  │
│      │ 2-Sigma Anomaly Math │ trend-alerts    │ Watch severity flip RED│
└──────┴──────────────────────┴─────────────────┴────────────────────────┘
```

> ⚠️ **Note on AI/ML Integration**:  
> For this evaluation prototype, **Google Gemini 1.5 API** is integrated as a **temporary evaluation service** for clinical history summarization and voice prescription parsing.  
> **During our 24-Hour Hackathon Sprint**, we are actively integrating **self-hosted, sovereign open-source AI/ML models** (BioMistral / Llama-3-Med, fine-tuned multilingual Whisper for Indian accents, and ML time-series forecasting). This ensures 100% compliance with India's **DPDP Act & DISHA regulations**, guaranteeing sensitive medical transcripts never leave sovereign hospital networks. *(See [Section 5](#-aiml-architecture--24-hour-hackathon-sprint-plan) for details).*

---

## 📑 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Step-by-Step Procedure to Turn On the Website](#-step-by-step-procedure-to-turn-on-the-website)
   - [Step 1: Clone / Open the Project Folder](#step-1-clone--open-the-project-folder)
   - [Step 2: Create & Activate a Python Virtual Environment](#step-2-create--activate-a-python-virtual-environment)
   - [Step 3: Install Required Dependencies](#step-3-install-required-dependencies)
   - [Step 4: Configure the Environment Variables (`.env`)](#step-4-configure-the-environment-variables-env)
   - [Step 5: Seed Initial Database Records](#step-5-seed-initial-database-records)
   - [Step 6: Launch the Web Application Server](#step-6-launch-the-web-application-server)
3. [Stored Demo Credentials & Passwords](#-stored-demo-credentials--passwords)
   - [Staff Accounts (All 4 Portals)](#staff-accounts-all-4-portals)
   - [Pre-Seeded Test Patient Cards](#pre-seeded-test-patient-cards)
   - [How Clinical Access OTP Works in Demo Mode](#how-clinical-access-otp-works-in-demo-mode)
   - [Application Approval Credentials](#application-approval-credentials)
4. [Disease Outbreak Simulator (`simulate_outbreak.py`)](#-disease-outbreak-simulator-simulate_outbreakpy)
   - [Overview & Purpose](#overview--purpose)
   - [How to Run the Simulator in a Second Terminal](#how-to-run-the-simulator-in-a-second-terminal)
   - [Interactive Menu Options](#interactive-menu-options)
   - [Live Demonstration Workflow for Judges & Reviewers](#live-demonstration-workflow-for-judges--reviewers)
5. [AI/ML Architecture & 24-Hour Hackathon Sprint Plan](#-aiml-architecture--24-hour-hackathon-sprint-plan)
6. [Automated Verification & Smoke Tests](#-automated-verification--smoke-tests)
7. [Troubleshooting & Frequently Asked Questions](#-troubleshooting--frequently-asked-questions)

---

## 🛠️ Prerequisites

Before starting, ensure your system has the following installed:
* **Python**: Version `3.10` or higher (`python --version`)
* **Git**: Version `2.x` or higher
* **Terminal**: Windows PowerShell, Command Prompt, or bash/zsh on macOS/Linux
* **Modern Web Browser**: Google Chrome, Mozilla Firefox, or Microsoft Edge (with camera and microphone permissions enabled for QR scanning and voice dictation)

---

## ⚙️ Step-by-Step Procedure to Turn On the Website

Follow these steps sequentially from your terminal:

### Step 1: Clone / Open the Project Folder
Open your terminal and navigate to the application directory:
```powershell
cd "c:\Users\Sahane's Laptop\Desktop\SWASTYA_SETU\Play-app"
```
*(On Linux/macOS or if you cloned elsewhere, navigate to `<your-repo>/Play-app`)*.

---

### Step 2: Create & Activate a Python Virtual Environment
Creating an isolated virtual environment prevents library conflicts:

* **On Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```
  *(If PowerShell displays an `Execution_Policies` script error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` then re-run the activate command).*

* **On Windows (Command Prompt `cmd`)**:
  ```cmd
  python -m venv venv
  venv\Scripts\activate.bat
  ```

* **On Linux / macOS**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

When activated, you will see `(venv)` prepended to your command prompt.

---

### Step 3: Install Required Dependencies
With your virtual environment active, install all pinned dependencies:
```bash
pip install -r requirements.txt
```

This installs:
* `Flask`, `Flask-Login`, `Flask-SQLAlchemy`, `SQLAlchemy` (Core backend & ORM)
* `psycopg2-binary` (PostgreSQL driver for cloud database support)
* `cryptography` (Fernet AES-128-CBC encryption for patient PII)
* `rapidfuzz` (Fuzzy Levenshtein matching for drug catalog spellchecking)
* `qrcode` & `pillow` (High-resolution QR code generator)
* `python-dotenv` (Automatic `.env` loader)
* `gunicorn` (Production WSGI web server)

---

### Step 4: Configure the Environment Variables (`.env`)
The application requires configuration parameters to connect to the database, cryptographic engine, and mail server.

Create a file named `.env` inside the `Play-app` folder (or copy from `.env.example`):
```powershell
Copy-Item .env.example .env
```

Here is the recommended demo `.env` file configuration:
```env
# ── Database Connection ──────────────────────────────────────────────────────────
# Use Supabase cloud PostgreSQL (already configured) or fallback to local SQLite:
DATABASE_URL=postgresql://postgres.dttgwzypyttkpqqeydms:Siddhesh123@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres?sslmode=require

# (Optional SQLite fallback if testing offline without internet):
# DATABASE_URL=sqlite:///instance/swasthya_setu.db

# ── Cryptography & Sessions ──────────────────────────────────────────────────────
SECRET_KEY=swasthya-setu-super-secret-key-2026-hackathon

# ── Google Gemini AI API Key (Temporary Prototyping Model) ──────────────────────
# NOTE: Currently utilizing Gemini for prototype summarization; will be replaced 
# with localized on-premise BioMistral/Ollama models during the 24-hr hackathon sprint.
GEMINI_API_KEY=AQ.Ab8RN6LIBHdR1WQyQbgCtdySgYf9m9UMiLzmEy7cftv2Qm1abAAQ.Ab8RN6LIBHdR1WQyQbgCtdySgYf9m9UMiLzmEy7cftv2Qm1abA
AI_API_KEY=AQ.Ab8RN6LIBHdR1WQyQbgCtdySgYf9m9UMiLzmEy7cftv2Qm1abAAQ.Ab8RN6LIBHdR1WQyQbgCtdySgYf9m9UMiLzmEy7cftv2Qm1abA

# ── SMS / OTP Service (Leave blank for automated terminal logging + email) ───────
OTP_PROVIDER_API_KEY=

# ── Gmail SMTP Email Notification Gateway ─────────────────────────────────────────
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=wastya-setu1112@gmail.com
MAIL_PASSWORD=vpuwazdbvvkksgbr
MAIL_DEFAULT_SENDER="Swasthya Setu Health Authority <wastya-setu1112@gmail.com>"

# ── Privacy & Clinical Governance Rules ───────────────────────────────────────────
MIN_GROUP_SIZE=5
DOCTOR_RECORD_EDIT_WINDOW_HOURS=24
```

> [!NOTE]
> Database schema tables (`users`, `patients`, `visits`, `access_logs`, `stats`, `applications`) are automatically created on startup by `run.py` via `db.create_all()`.

---

### Step 5: Seed Initial Database Records
Populate the database with default staff logins, test patients, encrypted health cards, and epidemiological ward cohorts:
```bash
python seed.py
```

Expected terminal output:
```text
[*] Seeding database target: postgresql://postgres.dttgwzypyttkpqqeydms:****@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres?sslmode=require
[OK] Database seeded successfully:
    - Staff accounts: ['doctor_demo', 'pharma_demo', 'public_demo', 'admin_demo']
    - Patient cards: ['SS-TEST-001', 'SS-TEST-002', 'SS-TEST-003']
    - Stats cohorts: 14 rows
```

---

### Step 6: Launch the Web Application Server
Start the Flask development server:
```bash
python run.py
```

You will see the diagnostic ASCII banner in your terminal:
```text
======================================================================
   🏥 SWASTHYA SETU — PUNE MUNICIPAL HEALTHCARE GRID ACTIVE
======================================================================
   Local Server URL : http://127.0.0.1:5000
   Staff Login Page : http://127.0.0.1:5000/login
   Citizen Portal   : http://127.0.0.1:5000/
======================================================================
```

Open your browser and navigate to:  
👉 **`http://127.0.0.1:5000`**

---

## 🔑 Stored Demo Credentials & Passwords

### Staff Accounts (All 4 Portals)
The following pre-configured staff accounts are ready for testing. All accounts share the same demo password:

| Role | Username | Password | Dedicated Dashboard URL | Permissions & Capabilities |
|---|---|---|---|---|
| **System Administrator** | `admin_demo` | `password123` | [`/admin/dashboard`](http://127.0.0.1:5000/admin/dashboard) | Screen applications, approve/reject staff & cards, manage users, inspect immutable audit logs. |
| **Attending Doctor** | `doctor_demo` | `password123` | [`/doctor/scan`](http://127.0.0.1:5000/doctor/scan) | Camera QR scan, verify patient OTP, view full history, listen to AI summary, voice dictation, add checkup, 24h delete lock. |
| **Pharmacist** | `pharma_demo` | `password123` | [`/pharmacist/scan`](http://127.0.0.1:5000/pharmacist/scan) | Rapid QR/ID lookup, view 4 allowed fields (medicine, condition, date, card ID), refill restriction blocks. Zero diagnosis notes. |
| **Public Health Officer** | `public_demo` | `password123` | [`/public-health/dashboard`](http://127.0.0.1:5000/public-health/dashboard) | Ward epidemiology monitoring, $k$-anonymity suppression (`< 5`), automated 2-sigma outbreak alerts, GIS data API. |

---

### Pre-Seeded Test Patient Cards
These cards are pre-encrypted with Fernet AES-256 and pre-loaded with clinical visits:

| Card ID | Patient Name | Registered Phone | Pune Locality / Ward | Seeded Medical Scenario & Test Cases |
|---|---|---|---|---|
| **`SS-TEST-001`** | Meera Joshi | `+919876543210` | Shivajinagar (Ward A) | • **Visit 1 (10 days ago)**: Flu, Cold & Cough (Immutable — cannot be deleted).<br>• **Visit 2 (3 days ago)**: Hypertension (`refill_restricted=True` — shows as blocked in Pharmacist portal). |
| **`SS-TEST-002`** | Arjun Sharma | `+919876543211` | Kothrud (Ward B) | • **Visit 1 (5 days ago)**: Viral Fever & Joint Pain.<br>• **Visit 2 (2 days ago)**: Type 2 Diabetes (Metformin & Atorvastatin). |
| **`SS-TEST-003`** | Priya Sen | `+919876543212` | Katraj (Ward C) | • **Visit 1 (1 day ago)**: Dengue fever.<br>• **Privacy Test**: Katraj Dengue has only 3 cases, deliberately below `MIN_GROUP_SIZE < 5` to demonstrate the `"< 5 (Insufficient Data)"` suppression in the Public Health portal. |

---

### How Clinical Access OTP Works in Demo Mode
When testing the **Doctor Portal** (`/doctor/scan`), you do not need a physical SMS gateway SIM:
1. Doctor scans patient card `SS-TEST-001` or types `SS-TEST-001` and submits.
2. The server instantly generates a 6-digit OTP (e.g., `482910`).
3. **Where to get the OTP**:
   * **In the Server Terminal**: The server immediately prints the OTP with an eye-catching box:
     ```text
     [OTP CODE] Patient #1 (+919876543210) -> Code: 482910
     ```
   * **In Email**: If the patient registered with an email, the OTP is simultaneously delivered via Gmail.
4. Type the 6-digit code into the `/doctor/otp-verify` box and click **Verify**.
5. The session unlocks and navigates to the patient's full medical history!

---

### Application Approval Credentials
When an administrator reviews public applications in the Admin Console (`/admin/applications`):
* **Approved Doctors**: Given an auto-generated username (e.g., `dr_rajesh`) and default password:
  ```text
  Swasthya@2026
  ```
* **Approved Pharmacists**: Given a username (e.g., `pharma_suresh`) and default password:
  ```text
  Swasthya@2026
  ```
* Credentials and e-Card download links are automatically emailed to the applicant upon clicking **Approve**.

---

## 🚨 Disease Outbreak Simulator (`simulate_outbreak.py`)

### Overview & Purpose
`simulate_outbreak.py` is an interactive command-line tool built to demonstrate the platform's **real-time epidemiological surveillance engine** and **2-sigma outbreak detection algorithm** to hackathon judges.

It directly manipulates the database's aggregated health cohorts in real time without restarting the web server.

---

### How to Run the Simulator in a Second Terminal
1. Leave your Flask application server running in **Terminal 1** (`python run.py`).
2. Open a **new, separate Terminal window (Terminal 2)**.
3. Navigate to `Play-app` and activate the virtual environment:
   ```powershell
   cd "c:\Users\Sahane's Laptop\Desktop\SWASTYA_SETU\Play-app"
   .\venv\Scripts\Activate.ps1
   ```
4. Run the simulator script:
   ```powershell
   python simulate_outbreak.py
   ```

You will see the interactive console menu:
```text
=================================================================
   [+] SWASTHYA SETU -- LIVE DISEASE OUTBREAK SIMULATOR
   Pune Municipal Epidemiological Surveillance Engine
=================================================================

Select an action:
  [1] Run Animated Outbreak Cycle (Increases -> Peaks -> Recedes to normal)
  [2] Set Instant Outbreak Spike (Katraj Dengue = 52 cases)
  [3] Reset Stats Back to Normal Seed Baseline
  [4] Exit Simulator

Enter choice [1-4]:
```

---

### Interactive Menu Options

#### Option `[1]`: Run Animated Outbreak Cycle
Simulates the realistic timeline of an emerging epidemic wave in **Katraj (Ward C)** for **Dengue**:
* **Phase 1 (Baseline)**: Case count = 3. Suppressed under $k$-anonymity rule (`< 5 Insufficient Data`).
* **Phase 2 (Influx)**: Case count climbs to 8. Visible on dashboard.
* **Phase 3 (Warning)**: Case count rises to 19. Threshold breached.
* **Phase 4 (Rapid Escalation)**: Case count reaches 37. Severity switches to HIGH.
* **Phase 5 (Epidemic Peak)**: Case count reaches 54. 2-Sigma mathematical anomaly triggered!
* **Phase 6 (Municipal Intervention)**: Pune Municipal Corporation mobilizes fogging teams & fever clinics. Count drops to 28.
* **Phase 7 (Receding)**: Count falls to 11.
* **Phase 8 (Safe Baseline)**: Normalizes back to 4 cases.

#### Option `[2]`: Set Instant Outbreak Spike
Immediately sets Katraj Dengue cases to **52 cases**. Ideal for showing hackathon judges the instant transition of the Outbreak Trend Alert from green to bright red without waiting.

#### Option `[3]`: Reset Stats Back to Normal Seed Baseline
Instantly restores Katraj Dengue back to 3 cases and Kothrud to 38 cases. Use this to reset the demo after your presentation.

#### Option `[4]`: Exit Simulator
Exits cleanly back to the terminal prompt.

---

### Live Demonstration Workflow for Judges & Reviewers
Follow this 3-step demonstration sequence to showcase the system:

1. **Step 1 — Show the Normal Baseline**:
   * Log into the Public Health portal as `public_demo` / `password123`.
   * Go to [`http://127.0.0.1:5000/public-health/trend-alerts`](http://127.0.0.1:5000/public-health/trend-alerts).
   * Point out to the judges that Katraj is either not flagged or shows normal baseline metrics.
2. **Step 2 — Trigger the Live Outbreak**:
   * Switch to Terminal 2 and choose **`[2]`** (or run **`[1]`** for the animated cycle).
   * The terminal confirms: `Katraj (Ward C) - Dengue set to 52 cases`.
3. **Step 3 — Refresh the Browser & Inspect Predictive Forecaster**:
   * Refresh the Trend Alerts webpage (`F5`).
   * **Result for Judges**:
     * 🔴 **2-Sigma Anomaly Alert**: High Severity alert badge with statistical deviation ($\mu + 2\sigma$).
     * 📈 **Predictive Spread Velocity**: Shows case growth trajectory (e.g. `+145.0% WoW trajectory` and velocity tag: `EXPONENTIAL SURGE`).
     * 🔮 **Forward Projections**: Shows projected infection volume in **3 Days** (projected within 72 hrs) and **7 Days** (projected outbreak peak window in ~3-5 days).
     * 🛡️ **Municipal Intervention Playbook**: Automatically generates tailored municipal action steps (e.g., *"Deploy PMC vector-control fogging in Katraj (Ward C), inspect stagnant water coolers, distribute abate granules, and mobilize ASHA workers for fever survey door-to-door"*).

---

## 🤖 AI/ML Architecture & 24-Hour Hackathon Sprint Plan

```
┌────────────────────────────────────────────────────────────────────────┐
│                   24-HOUR HACKATHON AI/ML DELIVERABLES                 │
├──────────────┬────────────────────────┬────────────────────────────────┤
│ Time Window  │ Module / Model Target  │ Clinical & Architectural Impact│
├──────────────┼────────────────────────┼────────────────────────────────┤
│ Hours 00–06  │ Local BioMistral /     │ Replaces cloud Gemini with     │
│              │ Llama-3-Med GGUF       │ sovereign on-prem inference.   │
├──────────────┼────────────────────────┼────────────────────────────────┤
│ Hours 06–12  │ Multilingual Whisper   │ Transcribes Indian medical     │
│              │ Fine-Tuned Model       │ accents (Hindi, Marathi, Eng). │
├──────────────┼────────────────────────┼────────────────────────────────┤
│ Hours 12–18  │ Prophet / LSTM Outbreak│ Predicts disease trajectory    │
│              │ Time-Series Forecaster │ 7–14 days before epidemic peak.│
├──────────────┼────────────────────────┼────────────────────────────────┤
│ Hours 18–24  │ Neo4j / NetworkX Drug  │ Real-time polypharmacy conflict│
│              │ Interaction Knowledge  │ warnings on doctor's screen.   │
└──────────────┴────────────────────────┴────────────────────────────────┘
```

### Why Sovereign Local AI is Mandatory for Indian Healthcare:
1. **Regulatory Compliance (DPDP Act & DISHA)**: Indian health guidelines strictly discourage sending identifiable citizen symptom logs to external third-party cloud LLMs.
2. **Rural & Offline Resilience**: Many Primary Health Centers (PHCs) around Pune district suffer from sporadic internet connectivity. Deploying lightweight, quantized open-source models (via `llama.cpp` or Ollama) ensures doctors can still dictate prescriptions and receive clinical summaries completely offline.
3. **Multilingual Inclusivity**: Real doctor-patient consultations in Maharashtra frequently mix Marathi, Hindi, and English medical terminology. A fine-tuned localized Whisper model bridges this communication barrier effortlessly.

---

## 🧪 Automated Verification & Smoke Tests

To verify that all 13 build steps, cross-role RBAC restrictions, encryption layers, and route handlers are operating with 100% compliance, run the automated test suite:

```powershell
python -m unittest tests/test_step12_e2e_smoke.py
```

To run the live HTTP network verification test (verifies 403 blocks, pharmacist 4-column isolation, and public health anonymity over HTTP):
```powershell
python tests/test_live_deployment_smoke.py --url http://127.0.0.1:5000
```

---

## ❓ Troubleshooting & Frequently Asked Questions

### 1. Port 5000 is already in use
If another application or previous Flask process is occupying port 5000, start the server on a custom port:
```powershell
$env:PORT="5001"
python run.py
```
Then access the site at `http://127.0.0.1:5001`.

### 2. "Database connection warning" on startup
If your internet is temporarily offline or the Supabase pooler times out, the application falls back safely. To run completely offline locally, switch the connection in `.env` to:
```env
DATABASE_URL=sqlite:///instance/swasthya_setu.db
```
Then re-run `python seed.py` and `python run.py`.

### 3. Microphone or Voice Dictation not responding
The Web Speech API requires access to your microphone:
* Ensure you are running on `http://127.0.0.1:5000` or `http://localhost:5000` (browsers treat localhost as a secure origin).
* When prompted by your browser, click **Allow** for microphone access.

### 4. OTP not appearing
In demo mode, you do not need an SMS provider. Simply glance at your active server terminal running `python run.py`. The 6-digit OTP is highlighted in yellow text upon every card scan.

---

## 🔗 Cross References & Documentation

* 📖 **[Website Portals, Feature Directory & Security Architecture (README.md)](README.md)**: Master architectural guide explaining all panels, citizen workflows, visual flowcharts, and security safeguards.
* 📋 **[Agent Implementation Plan (IMPLEMENTATION_PLAN_FOR_AGENT.md)](IMPLEMENTATION_PLAN_FOR_AGENT.md)**: Full chronological step-by-step build record.
* 🚀 **[Cloud Deployment Guide (Play-app/DEPLOYMENT_GUIDE.md)](Play-app/DEPLOYMENT_GUIDE.md)**: Railway and Supabase cloud setup instructions.
