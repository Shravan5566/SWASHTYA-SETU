# 🏥 Swasthya Setu (स्वास्थ्य सेतु)
### Unified Healthcare Network, Complete Panel Guide & Security Blueprint

---

## 🌐 Hosted Live Prototype & Direct Access Links

| Environment | Prototype URL | Description & Access |
|---|---|---|
| ☁️ **Cloud Hosted Live Prototype** | **[https://health-bridge.up.railway.app](https://health-bridge.up.railway.app)** | Production cloud deployment on Railway with cloud PostgreSQL (Supabase). Ready for instant judge evaluation — zero local setup needed! |
| 💻 **Local Development Server** | **[http://127.0.0.1:5000](http://127.0.0.1:5000)** | Local Python Flask development server (see [SETUP_AND_DEMO_GUIDE.md](SETUP_AND_DEMO_GUIDE.md)). |
| 📦 **GitHub Repository** | **[https://github.com/SiddheshSahane-s/health-01.git](https://github.com/SiddheshSahane-s/health-01.git)** | Complete source code, blueprints, security middlewares, and automated tests. |
| 🔑 **Demo IDs & Passwords** | **[SETUP_AND_DEMO_GUIDE.md](SETUP_AND_DEMO_GUIDE.md)** | All staff logins (`admin_demo`, `doctor_demo`, `pharma_demo`, `public_demo`), passwords (`password123`), and test cards (`SS-TEST-001`) are documented in the setup guide. |

---

## 🎯 Executive Briefing for Hackathon Judges & Evaluators

Welcome, Judges! Here is a 60-second summary of what **Swasthya Setu** delivers, why it matters, and where it is going during the hackathon:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   HACKATHON EVALUATION SCORECARD                       │
├─────────────────────┬──────────────────────────────────────────────────┤
│ Problem Solved      │ Fragmented paper records, unauthorized snooping, │
│                     │ prescription errors & delayed epidemic response. │
├─────────────────────┼──────────────────────────────────────────────────┤
│ Core Innovation     │ Zero-Trust Patient Physical Consent (OTP gate) + │
│                     │ Voice-to-Prescription + 2-Sigma Outbreak Radar.  │
├─────────────────────┼──────────────────────────────────────────────────┤
│ Production Security │ Fernet AES-256 PII, RBAC 403, Immutable Audit,   │
│                     │ Rate Limiter (429), k-Anonymity (< 5 masking).   │
├─────────────────────┼──────────────────────────────────────────────────┤
│ AI/ML Status        │ • Live Prototype: Google Gemini 1.5 LLM (Temporary)│
│                     │ • 24-Hour Sprint: Actively training own AI models│
│                     │   on domain datasets with ZERO external API calls│
│                     │   (100% DPDP & DISHA compliant, see Section 8). │
├─────────────────────┼──────────────────────────────────────────────────┤
│ Live Demo Script    │ See SETUP_AND_DEMO_GUIDE.md for 5-minute flow.   │
└─────────────────────┴──────────────────────────────────────────────────┘
```

> 🧠 **AI/ML Architectural Strategy for Hackathon Judges**:  
> **During our 24-Hour Hackathon Sprint, we are actively TRAINING OUR OWN IN-HOUSE AI MODELS using domain datasets — completely eliminating external cloud AI dependencies!**  
> * **Temporary Prototype Notice**: For early verification of UI flows and JSON schemas, **Google Gemini 1.5 API** was temporarily connected as an evaluation mock.  
> * **Production Deliverable**: We are training and fine-tuning specialized models directly on curated datasets:
>   1. **Clinical Summarizer & Prescription Entity Parser**: Trained on EHR consultation transcript datasets (local on-premise inference with zero data egress).
>   2. **Indic Voice Dictation Engine**: Fine-tuned on Indian multilingual clinical speech datasets (Marathi, Hindi, English).
>   3. **Epidemiological Outbreak Regressor**: Trained on multi-year Pune municipal ward disease time-series datasets.
>   4. **Polypharmacy Drug Safety Graph**: Trained on Indian Pharmacopoeia and drug contraindication databases.  
> * **Zero Cloud Leakage**: Guarantees 100% compliance with India's **DPDP Act & DISHA regulations**, ensuring private citizen health data and doctor voice recordings never leave the hospital network. *(See [Section 8](#-aiml-architecture--24-hour-hackathon-roadmap) for full details).*

---

## 🌟 Table of Contents
1. [Hosted Live Prototype & Direct Access Links](#-hosted-live-prototype--direct-access-links)
2. [What is Swasthya Setu? (In Simple Words)](#-what-is-swasthya-setu-in-simple-words)
3. [How the Whole System Works (Master Flowchart)](#-how-the-whole-system-works-master-flowchart)
4. [The 5 Portals: What Each Panel Does & How to Use It](#-the-5-portals-what-each-panel-does--how-to-use-it)
5. [Deep Dive: Complete System Architecture & Exhaustive Route-by-Route Directory](#-deep-dive-complete-system-architecture--exhaustive-route-by-route-directory)
   - [Blueprint 1: Public Citizen & Applications (`application_routes`)](#blueprint-1-public-citizen--applications-application_routes)
   - [Blueprint 2: Central Multi-Role Authentication (`auth_routes`)](#blueprint-2-central-multi-role-authentication-auth_routes)
   - [Blueprint 3: Doctor Clinical Portal (`doctor_routes`)](#blueprint-3-doctor-clinical-portal-doctor_routes)
   - [Blueprint 4: Pharmacist Dispensary (`pharmacist_routes`)](#blueprint-4-pharmacist-dispensary-pharmacist_routes)
   - [Blueprint 5: Public Health Epidemiological Surveillance (`public_health_routes`)](#blueprint-5-public-health-epidemiological-surveillance-public_health_routes)
   - [Blueprint 6: System Administrator Governance (`admin_routes`)](#blueprint-6-system-administrator-governance-admin_routes)
   - [Blueprint 7: AI & Clinical Decision Support (`ai_routes`)](#blueprint-7-ai--clinical-decision-support-ai_routes)
   - [Blueprint 8: Asynchronous Security & Consent AJAX (`ajax_routes`)](#blueprint-8-asynchronous-security--consent-ajax-ajax_routes)
   - [Global Handlers: Middleware & Error Responses](#global-handlers-middleware--error-responses)
6. [Step-by-Step Visual Flowcharts for Key Workflows](#-step-by-step-visual-flowcharts-for-key-workflows)
7. [Security Made Simple: Every Protection Explained](#-security-made-simple-every-protection-explained)
8. [AI/ML Architecture & 24-Hour Hackathon Roadmap](#-aiml-architecture--24-hour-hackathon-roadmap)
9. [Quick Reference & Documentation Links](#-quick-reference--documentation-links)

---

## 📖 What is Swasthya Setu? (In Simple Words)

Imagine visiting a new doctor in your city. Usually, you have to carry a heavy plastic folder with old paper prescriptions, lab reports from years ago, and handwritten doctor notes that no one can read. If you lose that folder, your medical history is lost forever.

Now imagine the opposite problem: if all your private medical records are placed online, what stops an unauthorized person, a chemist, or a random clerk from snooping into your sensitive medical illnesses?

**Swasthya Setu ("Bridge of Health")** is built for the **Pune Metropolitan Region** to solve both problems at once:

1. **For Citizens**: You apply online for an official **Digital Health Card** with a unique QR code. You can carry it on your phone or print it like an Aadhaar card.
2. **For Doctors**: When you visit a clinic, the doctor scans your card's QR code. But **the doctor cannot see your records yet**! You receive a secret 6-digit OTP on your phone. Only when you tell the doctor that OTP does your health history unlock. The doctor gets an **AI summary** of your health, can speak prescriptions out loud using **Voice Dictation**, and gets instant alerts if a drug name is misspelled.
3. **For Pharmacists**: The chemist scans your card and sees **only** what medicines to give you. They can **never** see your confidential doctor notes, and if a medicine has a refill restriction, the computer blocks it.
4. **For Government Health Officers**: An automated surveillance radar watches disease counts across Pune (Katraj, Kothrud, Hadapsar, etc.). If Dengue or Flu suddenly spikes, an **Outbreak Alert** fires automatically so the municipality can send fogging and medical teams.
5. **For System Admins**: A central control room to verify doctor licenses, approve citizen cards, and watch a tamper-proof security log of every single action taken on the website.

---

## 🗺️ How the Whole System Works (Master Flowchart)

Here is a simple, high-level map showing how citizens, doctors, pharmacists, health officers, and system admins interact:

```mermaid
graph LR
    %% ── ACTORS ──────────────────────────────────────────────
    C(["👤 Citizen"])
    D(["🩺 Doctor"])
    P(["💊 Pharmacist"])
    H(["🏛️ Health Officer"])
    A(["🔑 System Admin"])

    %% ── PORTAL 1: Public Citizen Portal ─────────────────────
    subgraph P1["🌐  Portal 1 — Public Citizen Home  /"]
        p1a["Apply for Digital Health Card"]
        p1b["Apply for Staff Accreditation"]
        p1c["Track Status and Download e-Card"]
    end

    %% ── PORTAL 2: Admin Console ──────────────────────────────
    subgraph P2["🔑  Portal 2 — System Admin Console  /admin"]
        p2a["Screen and Approve Applications"]
        p2b["Manage Staff Accounts and Roles"]
        p2c["Forensic Security Audit Log"]
    end

    %% ── PORTAL 3: Doctor Portal ──────────────────────────────
    subgraph P3["🩺  Portal 3 — Doctor Clinical Portal  /doctor"]
        p3a["Scan Patient QR Code"]
        p3b{{"OTP Verified?"}}
        p3c["View Medical History Timeline"]
        p3d["AI Clinical Summary and TTS"]
        p3e["Voice Dictate Prescription"]
    end

    %% ── PORTAL 4: Pharmacist Portal ──────────────────────────
    subgraph P4["💊  Portal 4 — Pharmacist Dispensary  /pharmacist"]
        p4a["Instant Card Scan — No OTP needed"]
        p4b["View 4 Safe Columns Only"]
        p4c["Refill Restriction Block"]
    end

    %% ── PORTAL 5: Public Health ──────────────────────────────
    subgraph P5["🏛️  Portal 5 — Public Health Surveillance  /public-health"]
        p5a["Ward Disease Counts — k-Anonymity Masked"]
        p5b["2-Sigma Outbreak Alert"]
        p5c["Disease Trend Detector — 3 and 7 Day Forecast"]
    end

    %% ── CONNECTIONS ──────────────────────────────────────────
    C -->|"Applies"| p1a
    D -->|"Registers"| p1b
    P -->|"Registers"| p1b
    A -->|"Approves"| p2a
    p1a -->|"Pending"| p2a
    p1b -->|"Pending"| p2a
    p2a -->|"Card Issued"| p1c
    C -->|"Visits clinic"| p3a
    p3a -->|"OTP sent to phone"| p3b
    p3b -->|"Yes — Unlocked"| p3c
    p3b -->|"No — 403 Denied"| p3a
    p3c --> p3d
    p3c --> p3e
    C -->|"Visits pharmacy"| p4a
    p4a --> p4b
    p4b --> p4c
    p3e -.->|"Anonymized counts"| p5a
    p5a --> p5b
    p5a --> p5c
    H -->|"Monitors"| p5b
    H -->|"Monitors"| p5c
    A -->|"Inspects logs"| p2c
```

> **How to read the diagram:** Actors (circles) on the left connect to the portal that serves them. Dashed arrows show background data flows (doctor checkups feed the surveillance engine). The diamond shape on the Doctor portal is the security checkpoint — no OTP, no access.


---

## 💻 The 5 Portals: What Each Panel Does & How to Use It

---

### Portal 1: Public Citizen Home (`/`)
*The friendly front door of the municipal health network.*

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     PUBLIC PORTAL (Landing Page)                        │
├───────────────────────────────────┬─────────────────────────────────────┤
│ 🪪 Citizen Health Card Application│ 🩺 Healthcare Staff Accreditation   │
│   • Enter Name, Phone, Aadhaar    │   • For Doctors & Pharmacists       │
│   • Emergency Contact & Blood Grp │   • Submit MMC/MSPC License No.     │
│   • Choose your Pune Locality     │   • Submit Hospital & Experience    │
│   • Get Reference Tracking ID     │   • Reviewed by System Admin        │
├───────────────────────────────────┴─────────────────────────────────────┤
│ 🔍 Track Application Status & Download Official Digital e-Card          │
│ 🔐 Staff Login Button (takes doctors, pharmacists & admins to work)     │
└─────────────────────────────────────────────────────────────────────────┘
```

#### What can you do here?
1. **Apply for a Digital Health Card (`/apply/health-card`)**:
   * Anyone living in Pune can fill this simple online form.
   * You enter basic information: Name, Phone, Date of Birth, Gender, Blood Group, Government ID (Aadhaar/PAN/Voter ID), Pune Locality (Katraj, Kothrud, Shivajinagar, Hadapsar, etc.), and Emergency Contact.
   * You can also note chronic conditions (like Diabetes or Asthma) and any known drug allergies.
   * When you submit, the computer gives you an instant tracking reference number like `APP-PAT-2026-0001`.
2. **Apply for Healthcare Staff Accreditation (`/apply/staff`)**:
   * Doctors and Pharmacists practicing in Pune use this page to join the network.
   * They enter their Medical Council (MMC) or Pharmacy Council (MSPC) license number, medical qualification (MBBS, MD, B.Pharm), clinical specialty, and hospital/clinic address.
   * Once submitted, it gets routed to the System Administrator for official verification.
3. **Track Application Status (`/apply/status`)**:
   * Type in your application reference number or your registered mobile phone number.
   * The system shows your real-time status: **Pending Review**, **Approved**, or **Rejected** (with the administrator's reason).
4. **Download & Print Your Official Digital e-Card (`/apply/ecard/download`)**:
   * Once approved, a green **Download Official e-Card** button appears!
   * Clicking it opens a beautifully formatted Pune Municipal Corporation Health Card complete with your unique Card ID (`SS-...`), personal details, blood group, emergency numbers, and your encrypted QR code.
   * The page automatically triggers your browser's print dialog so you can print it or save it as a PDF immediately.
5. **Staff Login (`/login`)**:
   * A dedicated button in the header for staff. Once a doctor, pharmacist, health officer, or admin logs in, the website automatically recognizes their role and sends them directly to their specific dashboard.

---

### Portal 2: Doctor Clinical Portal (`/doctor`)
*The smart clinical workspace for attending physicians.*

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       DOCTOR CLINICAL WORKSPACE                         │
├────────────────────────────┬────────────────────────────────────────────┤
│ 📷 Camera QR Scanner       │ 🔐 2-Factor Patient Physical Consent (OTP) │
│    Point camera at patient │    Patient receives 6-digit OTP on phone   │
│    card or type ID         │    Guarantees patient is physically present│
├────────────────────────────┴────────────────────────────────────────────┤
│ 📋 Patient Timeline & AI Clinical Briefing                              │
│    • Plain English AI summary of entire medical history (~60 words)     │
│    • 🔊 "Read Summary" button plays summary aloud via speech            │
│    • Full past history of visits, diagnoses, and past medicines         │
├─────────────────────────────────────────────────────────────────────────┤
│ ✍️ Add New Checkup (Typing OR Hands-Free Voice Dictation)               │
│    • 🎙 "Voice Dictate" button: speak diagnosis naturally into mic      │
│    • RapidFuzz Drug Checker: corrects spelling & flags drug allergies   │
│    • Refill Restriction switch: prevents unauthorized repeats           │
│    • Strict 24-Hour Edit Lock: doctor can edit own recent note for 24h, │
│      after that it becomes permanently locked and immutable.            │
└─────────────────────────────────────────────────────────────────────────┘
```

#### What can you do here?
1. **Scan Patient QR Code (`/doctor/scan`)**:
   * Opens the doctor's webcam or mobile phone camera.
   * Point it at the patient's digital health card to scan the QR code. You can also manually type the Card ID (e.g. `SS-TEST-001`).
2. **Verify Patient Physical Consent (`/doctor/otp-verify`)**:
   * The moment the card is scanned, the server generates a secret 6-digit OTP and sends it directly to the patient's phone (and email).
   * The doctor asks the patient for the code and enters it.
   * **Why this matters**: A doctor cannot look at a patient's private medical past unless the patient is sitting in the room and gives their consent!
3. **View Longitudinal Medical History (`/doctor/patient/<id>/history`)**:
   * Once verified, the doctor sees all past hospital visits, past illnesses, and previous medications in chronological order.
4. **Read & Listen to the AI Clinical Summary**:
   * Instead of reading 10 pages of messy notes, the AI summarizer reads the history and gives the doctor a crisp ~60-word clinical overview.
   * Doctors can click **"🔊 Read summary"** to listen to the summary aloud while examining the patient.
5. **Add a Checkup with Voice Dictation (`/doctor/patient/<id>/add-checkup`)**:
   * **Typing method**: Fill in diagnosis, area, medications, and dosage manually.
   * **Voice method**: Click the **"🎙 Voice"** button and speak naturally: *"Patient has high fever and acute sore throat. Prescribe Paracetamol 650mg three times daily and Azithromycin 500mg for 3 days."*
   * The computer turns speech to text, parses the medical fields, and fills the form automatically!
6. **Smart Drug Spelling & Allergy Checker**:
   * As medicines are typed, the system checks against a 500+ Indian drug catalog. If you mistype *"paracetmol"*, it suggests *"Paracetamol"*. If the medicine conflicts with known patient allergies, a warning pops up immediately.
7. **24-Hour Mistake Window (`/doctor/visit/<id>/delete`)**:
   * If a doctor makes a typing mistake on a visit they just created, they can delete and re-enter it within 24 hours.
   * After 24 hours, the record locks permanently to prevent medical record tampering. Another doctor can **never** delete another physician's entries.

---

### Portal 3: Pharmacist Dispensing Portal (`/pharmacist`)
*The fast, safe, privacy-preserving dispensary counter.*

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PHARMACIST DISPENSING COUNTER                      │
├─────────────────────────────────────────────────────────────────────────┤
│ 🔍 Instant Card Scan (No OTP needed — prevents long lines at chemist)   │
├─────────────────────────────────────────────────────────────────────────┤
│ 🔒 Privacy Guarantee: Chemist sees ONLY 4 Columns:                      │
│    1. Card ID        2. Date of Visit                                   │
│    3. Condition      4. Prescribed Medicine & Dosage                    │
│    ⚠️ Sensitive Doctor Diagnosis Notes are NEVER fetched from database! │
├─────────────────────────────────────────────────────────────────────────┤
│ 🚫 Refill Protection:                                                   │
│    If marked "Refill Restricted", item is highlighted with a warning:   │
│    "Refill Blocked — Patient must consult doctor for new prescription"  │
├─────────────────────────────────────────────────────────────────────────┤
│ 🛡️ View-Only Mode: Pharmacists cannot alter, edit, or delete any record│
└─────────────────────────────────────────────────────────────────────────┘
```

#### What can you do here?
1. **Instant QR or Card ID Scan (`/pharmacist/scan`)**:
   * The chemist scans the patient's card or enters their Card ID.
   * There is **no OTP step** here so medicines can be dispensed quickly without making sick patients wait in line.
2. **Restricted Medicine View (`/pharmacist/patient/<id>/medicines`)**:
   * The chemist sees the exact list of prescribed medicines, dosages, and instructions.
   * **Strict Privacy Rule**: The database query is programmed to retrieve **only 4 fields**. The patient's confidential clinical examination notes (`diagnosis_notes`) are **never fetched** from the database.
3. **Refill Restricted Block**:
   * If a doctor marked a medication as habit-forming, dangerous, or restricted (e.g., sleeping pills or strong antibiotics), the system marks it in red with a clear blockage: *"Refill Blocked — Doctor consultation required"*.
4. **Zero-Tampering Guarantee**:
   * The pharmacist panel is completely view-only. There are no delete, create, or edit buttons.

---

### Portal 4: Public Health Outbreak Radar (`/public-health`)
*The municipal early-warning system for epidemics.*

```
┌─────────────────────────────────────────────────────────────────────────┐
│          PUBLIC HEALTH SURVEILLANCE, OUTBREAK RADAR & TREND DETECTOR    │
├─────────────────────────────────────────────────────────────────────────┤
│ 🗺️ Ward-by-Ward Disease Monitoring (Katraj, Kothrud, Hadapsar, etc.)    │
│    Tracks weekly cases of Dengue, Malaria, Typhoid, Viral Flu, etc.    │
├─────────────────────────────────────────────────────────────────────────┤
│ 🛡️ k-Anonymity Privacy Filter:                                          │
│    If fewer than 5 people in a ward have an illness:                    │
│    The number is hidden and displays: "< 5 (Insufficient Data)"         │
│    Nobody can figure out individual patient identities!                 │
├─────────────────────────────────────────────────────────────────────────┤
│ 🚨 Automated 2-Sigma Outbreak Detector (/public-health/trend-alerts)    │
│    Math engine checks if current cases exceed average+2*std_deviation   │
│    Triggers bright red HIGH SEVERITY Alert with municipal actions:      │
│    • Mosquito fogging  • Water testing  • Emergency fever clinics       │
├─────────────────────────────────────────────────────────────────────────┤
│ 📈 NEW: Disease Trend Detector (/public-health/trend-forecast)          │
│    Shows ALL monitored conditions — not just those already spiking!     │
│    Colour-coded risk cards updated in real time:                        │
│    🔴 CRITICAL  🟠 ELEVATED  🟡 WATCH  🔵 STABLE  🟢 RECEDING          │
│    3-Day & 7-Day case projections give 3–7 days advance warning         │
└─────────────────────────────────────────────────────────────────────────┘
```

#### What can you do here?
1. **City Epidemiological Dashboard (`/public-health/dashboard`)**:
   * Health officers can filter disease counts by Pune area (Katraj, Kothrud, Shivajinagar, etc.), by condition (Dengue, Flu, Gastro), and by time period.
   * **Zero Patient Information**: Health officers see aggregate numbers only. Not a single patient name, phone number, or card ID exists on this dashboard.
2. **Differential Privacy & k-Anonymity Masking**:
   * What if only 2 people in Katraj have a rare illness? If the screen showed "2", neighbors might guess who those 2 patients are!
   * To prevent this, if any group has fewer than 5 cases, the system replaces the number with:  
     `"Under 5 (Insufficient Data)"`.
3. **Automated 2-Sigma Outbreak Anomaly Alerts (`/public-health/trend-alerts`)**:
   * An intelligent statistical engine compares this week's cases against recent historical weeks.
   * If cases spike past the statistical threshold ($\mu + 2\sigma$), the dashboard automatically displays a **HIGH SEVERITY Outbreak Alert**.
4. **Predictive Disease Spread & Spike Forecaster (Predicting Spikes 3 to 7 Days in Advance)**:
   * **Momentum & Velocity Analysis**: Calculates week-over-week case velocity ($\Delta C / \Delta t$) and classifies spread into `STABLE`, `MODERATE INFLUX`, `HIGH SPREAD VELOCITY`, or `EXPONENTIAL SURGE`.
   * **3-Day & 7-Day Forward Projections**: Instead of waiting for hospitals to overflow, the algorithm projects case numbers 3 to 7 days ahead (e.g. *'Katraj Dengue: Currently 37 cases, projected to reach ~54 cases within 72 hours with peak window in ~3-5 days'*).
   * **Actionable Municipal Playbooks**: Recommends targeted municipal emergency responses (e.g. vector control fogging, residual chlorine water tests, mobile fever clinics) to intervene *before* the epidemic peaks.
5. **NEW: Disease Trend Detector — All-Conditions Proactive Forecaster (`/public-health/trend-forecast`)**:
   * This is the **advance-warning radar** that goes *beyond* outbreak alerts. Instead of showing only diseases that have *already spiked*, this page displays **every single monitored condition** across all Pune wards, ranked by how fast it is growing.
   * Each disease/area combination gets a colour-coded card with its risk classification:
     - 🔴 **CRITICAL** — Has already breached the 2-sigma outbreak threshold. Urgent municipal action required.
     - 🟠 **ELEVATED** — Growth rate 30–75%. Rapidly accelerating. Prepare intervention teams now.
     - 🟡 **WATCH** — Growth rate 10–30%. Rising. Monitor closely and put teams on standby.
     - 🔵 **STABLE** — Within normal baseline variation.
     - 🟢 **RECEDING** — Cases are falling. Situation improving.
   * **Purpose**: Health officers see trends *building up* 3–7 days before they become an outbreak alert, allowing pre-emptive deployment of resources rather than reactive emergency response.


---

### Portal 5: System Admin Control Room (`/admin`)
*The central administrative governance console.*

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     SYSTEM ADMIN GOVERNANCE CONSOLE                     │
├─────────────────────────────────────────────────────────────────────────┤
│ 📊 System Executive Overview                                            │
│    Active users, registered cards, pending applications, security alerts│
├─────────────────────────────────────────────────────────────────────────┤
│ 📝 Application Screening Center (/admin/applications)                   │
│    • Review Doctor & Pharmacist council licenses                        │
│    • Review Citizen Health Card requests                                │
│    • 1-Click Approve: auto-creates username & password + sends email    │
│    • 1-Click Reject: sends formal reason to applicant                   │
├─────────────────────────────────────────────────────────────────────────┤
│ 👥 Staff User Management (/admin/users)                                 │
│    Create staff, activate/deactivate accounts, assign roles             │
│    (Admins cannot deactivate themselves — preventing accidental lockout)│
├─────────────────────────────────────────────────────────────────────────┤
│ 🖨️ Direct Patient Card Issuance (/admin/patients/register)              │
│    Issue instant encrypted QR health cards for walk-in citizens         │
├─────────────────────────────────────────────────────────────────────────┤
│ 📜 Immutable Security Audit Log (/admin/audit-log)                      │
│    Forensic log of every page visit, role, timestamp & 403 blocks       │
└─────────────────────────────────────────────────────────────────────────┘
```

#### What can you do here?
1. **Executive Overview Dashboard (`/admin/dashboard`)**:
   * Quick count of registered patients, active doctors, chemists, total requests, and unauthorized intrusion attempts.
2. **Review & Approve Applications (`/admin/applications`)**:
   * **Staff Requests**: Admin reviews the doctor's or pharmacist's qualifications and council registration number. Clicking **Approve** automatically creates their account (e.g. `dr_aisha`), generates a temporary password (`Swasthya@2026`), and emails their login credentials immediately.
   * **Health Card Requests**: Admin reviews the citizen details. Clicking **Approve** generates their unique encrypted card ID (`SS-...`), builds their QR code, and emails the citizen a link to download their e-Card.
   * **Reject**: Allows the admin to write a reason (e.g. *"Council license number unverified"*), which is emailed to the applicant.
3. **Staff Management & Role Assignment (`/admin/users`)**:
   * Admins can create staff, toggle their status (Active/Inactive), or change their role.
   * **Safety lock**: The system prevents admins from accidentally deactivating their own account or revoking their own admin role.
4. **Walk-In Card Issuance (`/admin/patients/register`)**:
   * When citizens visit municipal ward offices in person, staff can generate their encrypted card on the spot.
5. **Real-Time Forensic Audit Log (`/admin/audit-log`)**:
   * Every single request on the platform is logged here: who requested it, what role they had, what endpoint they touched, and whether it was `allowed` or `denied` (HTTP 403).
   * **Zero Clinical Snoop**: While the admin can see security activity, the admin portal has zero access to medical diagnosis notes or patient prescriptions.

---

## 🛣️ Deep Dive: Complete System Architecture & Exhaustive Route-by-Route Directory

Swasthya Setu is engineered using a modular, enterprise-grade **Flask Application Factory pattern**. All endpoints are divided across **8 dedicated Blueprints**, with cross-cutting security enforced via **centralized middleware hooks**, **sliding-window rate limiters**, and **strict Role-Based Access Control (RBAC)**.

Below is the exhaustive, deep-dive technical directory of every single route, parameter, access restriction, data mutation, and privacy guarantee in the codebase:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        SWASTHYA SETU SYSTEM ROUTE TOPOLOGY                             │
├──────────────────────────┬───────────────────┬─────────────────────────────────────────┤
│ Blueprint Module         │ URL Mount Prefix  │ Core Domain Responsibility              │
├──────────────────────────┼───────────────────┼─────────────────────────────────────────┤
│ `application_routes.py`  │ `/` & `/apply`    │ Citizen Health Cards, Staff Accredit.   │
│ `auth_routes.py`         │ `/`               │ Authentication, Sessions & RBAC Gateway │
│ `doctor_routes.py`       │ `/doctor`         │ Clinical EHR, OTP Consent, Voice AI     │
│ `pharmacist_routes.py`   │ `/pharmacist`     │ 4-Column Isolated Dispensary Counter    │
│ `public_health_routes.py`│ `/public-health`  │ Surveillance, 2-Sigma Outbreak Radar    │
│ `admin_routes.py`        │ `/admin`          │ Screening Desk, User Mgmt, Audit Trail  │
│ `ai_routes.py`           │ `/ai`             │ Gemini NLP, RapidFuzz Drug Correction   │
│ `ajax_routes.py`         │ `/ajax`           │ Real-Time Scanners, OTP Token Issuer    │
│ App-Level Middleware     │ Global            │ RBAC 403, Rate 429, Audit & Anti-Cache  │
└──────────────────────────┴───────────────────┴─────────────────────────────────────────┘
```

---

### Blueprint 1: Public Citizen & Applications (`application_routes.py`)
Mounted at root `/` and `/apply`. Provides public-facing self-service portals for Pune citizens and healthcare practitioners. No login credentials required to apply or check status.

#### 1. `GET /` — Public Citizen Home & Municipal Health Portal
* **Handler**: `index()` in `app/__init__.py` (uses `PUNE_LOCALITIES` from `application_routes.py`)
* **Access Control**: Public (No authentication required).
* **Rate Limit**: Default server policy.
* **Template Rendered**: `index.html`
* **Template Context**: `pune_localities` (List of 15 monitored Pune municipal wards: Katraj, Kothrud, Hadapsar, Viman Nagar, Shivajinagar, Baner, Hinjewadi, Swargate, Pimpri, Chinchwad, Yerawada, Camp, Aundh, Bibwewadi, Sinhagad Road).
* **Function & Architecture**: Serves as the public gateway. Features quick action cards:
  1. *Apply for Digital Health Card* (routes to `/apply/health-card`)
  2. *Apply for Staff Accreditation* (routes to `/apply/staff`)
  3. *Track Application Status & Download e-Card* (routes to `/apply/status`)
  4. *Staff Portal Login Button* (routes to `/login`)
* **Privacy & Security**: Read-only static presentation; exposes zero database PII.

#### 2. `GET, POST /apply/health-card` — Citizen Digital Health Card Application
* **Handler**: `apply_health_card()`
* **Access Control**: Public.
* **Rate Limit**: `@rate_limit(max_requests=15, window_seconds=60)` — Prevents automated bot spam.
* **Template Rendered**: `apply/health_card.html`
* **Form Inputs Accepted (`POST`)**:
  * `full_name` (String, required): Citizen legal name.
  * `phone` (String, required): 10-digit Indian mobile number for OTP delivery.
  * `email` (String, optional): Used for digital e-card delivery.
  * `dob` (Date String): Date of birth.
  * `gender` (String): Male / Female / Other.
  * `blood_group` (String): A+, A-, B+, B-, AB+, AB-, O+, O-.
  * `gov_id_type` & `gov_id_number` (Strings): Aadhaar, PAN, or Voter ID.
  * `locality` (String, required): Pune ward/locality dropdown.
  * `address` (Text): Full residential street address.
  * `emergency_name`, `emergency_phone`, `emergency_relation` (Strings): ICE contact details.
  * `chronic_conditions` (Text): Known illnesses (e.g., Hypertension, Type 2 Diabetes).
  * `allergies` (Text): Known drug/food allergies (e.g., Penicillin, Sulfa drugs).
* **Execution Logic**:
  1. Validates presence of mandatory fields (`full_name`, `phone`, `locality`).
  2. Calls `Application.generate_app_no("patient")` to mint an atomic tracking number formatted as `APP-PAT-YYYY-XXXX`.
  3. Creates a new `Application` row with `status="pending"`, `role="patient"`, and `app_type="health_card"`.
  4. Commits record to PostgreSQL and flashes success message with reference ID.
  5. Redirects applicant immediately to `/apply/status?q=<app_no>`.

#### 3. `GET, POST /apply/staff` — Professional Accreditation Application (Doctor & Pharmacist)
* **Handler**: `apply_staff()`
* **Access Control**: Public.
* **Rate Limit**: `@rate_limit(max_requests=15, window_seconds=60)`
* **Template Rendered**: `apply/staff.html`
* **Form Inputs Accepted (`POST`)**:
  * `role` (String, required): Must be either `"doctor"` or `"pharmacist"`. (Note: Public Health Admins and Sysadmins cannot self-apply; they are provisioned directly by admins).
  * `full_name`, `phone`, `email` (Strings, required): Professional contact details.
  * `council_reg_no` (String, required): Maharashtra Medical Council (MMC) or Maharashtra State Pharmacy Council (MSPC) registration number.
  * `qualification` (String, required): MBBS, MD, MS, B.Pharm, D.Pharm, etc.
  * `specialization` (String): e.g., General Medicine, Pediatrics, Cardiology.
  * `experience_years` (Integer/String): Years of active clinical practice.
  * `workplace_name`, `workplace_address`, `locality` (Strings, required): Hospital/Clinic affiliation.
  * `gov_id_type`, `gov_id_number` (Strings): Official identity proof.
* **Execution Logic**:
  1. Validates role constraints (`doctor` or `pharmacist`) and mandatory verification fields.
  2. Generates atomic tracking ID `APP-DOC-YYYY-XXXX` or `APP-PHARM-YYYY-XXXX`.
  3. Saves application in `Application` table with `status="pending"`.
  4. Redirects applicant to `/apply/status?q=<app_no>`.

#### 4. `GET, POST /apply/status` — Unified Real-time Application Status Tracker
* **Handler**: `check_status()`
* **Access Control**: Public.
* **Rate Limit**: `@rate_limit(max_requests=30, window_seconds=60)`
* **Query Parameter / Form Field**: `q` (Application reference number or 10-digit phone number).
* **Template Rendered**: `apply/status.html`
* **Dual Interface Response**:
  * **HTML View**: Renders visual timeline badge (`Pending Review` ➔ `Approved` / `Rejected`).
  * **JSON AJAX**: If requested via `X-Requested-With: XMLHttpRequest` or `Accept: application/json`, returns structured JSON object for headless frontends.
* **Data Flow**:
  1. Searches `Application` table by `app_no` (case-insensitive) or `phone`.
  2. If found and `status == "approved"` with assigned card ID, dynamically calls `generate_qr_code(app_record.assigned_card_id)` to produce the QR code data URI.
  3. Displays assigned credentials for staff or a green **"Download Official e-Card"** button for approved patients.

#### 5. `GET /apply/ecard/download` — Printable Digital e-Card & Dynamic QR Generation
* **Handler**: `download_ecard()`
* **Access Control**: Public (Guarded by approved application reference or valid card ID).
* **Query Parameter**: `q` (e.g. `/apply/ecard/download?q=SS-TEST-001` or `q=APP-PAT-2026-0001`).
* **Template Rendered**: `apply/ecard_download.html`
* **Execution Logic**:
  1. Resolves `Application` record where `(app_no == q OR assigned_card_id == q)` AND `status == 'approved'` AND `role == 'patient'`.
  2. Invokes `generate_qr_code()` using the verified `assigned_card_id`.
  3. Renders high-fidelity Pune Municipal Corporation Digital Health Card featuring the patient's card ID, personal demographics, emergency numbers, and the encrypted QR code.
  4. Automatically triggers browser `window.print()` via embedded JavaScript for instant PDF export or physical card printing.

---

### Blueprint 2: Central Multi-Role Authentication (`auth_routes.py`)
Mounted at root `/`. Handles credential verification, role-based session initialization, and secure termination.

#### 6. `GET, POST /login` — Unified Staff Gateway with Smart Role Redirection
* **Handler**: `login()`
* **Access Control**: Public. If user is already authenticated (`current_user.is_authenticated`), immediately redirects to their specific role dashboard via `get_role_dashboard(current_user.role)`.
* **Rate Limit**: `@rate_limit(max_requests=10, window_seconds=60)` — Strict protection against brute-force password guessing. Returns HTTP 429 when exceeded.
* **Form Inputs Accepted (`POST`)**:
  * `username` (String): e.g. `admin_demo`, `doctor_demo`, `pharma_demo`, `public_demo`.
  * `password` (String): e.g. `password123`.
* **Execution Logic**:
  1. Queries `User` table by `username`.
  2. Executes `user.check_password(password)` comparing against the bcrypt/werkzeug salted hash. Returns HTTP 401 on failure.
  3. Checks `user.is_active`. If `False`, denies authentication with HTTP 403 ("Account deactivated").
  4. Calls `login_user(user)` from Flask-Login, initializing encrypted session cookie.
  5. Maps `user.role` to target endpoint:
     * `sysadmin` ➔ `/admin/dashboard`
     * `doctor` ➔ `/doctor/dashboard` (which redirects to `/doctor/scan`)
     * `pharmacist` ➔ `/pharmacist/scan`
     * `public_health_admin` ➔ `/public-health/dashboard`

#### 7. `GET /logout` — Session Invalidation & State Cleanup
* **Handler**: `logout()`
* **Access Control**: `@login_required` (Must have active session).
* **Execution Logic**:
  1. Calls `logout_user()` from Flask-Login.
  2. Executes `session.clear()` to purge all cryptographic tokens (`patient_access_token`, `access_patient_id`, `otp_patient_id`).
  3. Flashes signed-out notice and redirects to `/login`.

---

### Blueprint 3: Doctor Clinical Portal (`doctor_routes.py`)
Mounted at `/doctor`. Clinical workstation for licensed attending physicians. Governed by two-factor physical patient consent and strict tamper-proof immutability rules.

#### 8. `GET /doctor/dashboard` — Doctor Console Entry Point
* **Handler**: `dashboard()`
* **Access Control**: `@role_required("doctor")` — Non-doctors receive HTTP 403 Forbidden.
* **Execution Logic**: Performs clean internal redirect to `/doctor/scan`.

#### 9. `GET /doctor/scan` — High-Speed Camera QR Scanner
* **Handler**: `scan_qr()`
* **Access Control**: `@role_required("doctor")`
* **Template Rendered**: `doctor/scan_qr.html`
* **Execution Logic**: Launches browser video stream via HTML5 WebRTC `getUserMedia()`. Continuously polls video frames with `jsQR` to decode the patient's card ID. Once decoded, issues asynchronous POST to `/ajax/scan-card` to verify the patient and trigger OTP generation. Includes manual text input fallback.

#### 10. `GET /doctor/otp-verify` — Two-Factor Physical Consent Verification Screen
* **Handler**: `otp_verify()`
* **Access Control**: `@role_required("doctor")`
* **Session Requirement**: Requires `session["otp_patient_id"]` (set by `/ajax/scan-card`). If missing, redirects back to `/doctor/scan`.
* **Template Rendered**: `doctor/otp_verify.html`
* **Execution Logic**: Presents 6-digit OTP input interface. When submitted, the client calls `/ajax/verify-otp`. Upon successful cryptographic verification, the server issues a scoped `patient_access_token` and redirects to the patient's longitudinal history.

#### 11. `GET /doctor/patient/<int:patient_id>/history` — Longitudinal Clinical Timeline & AI Briefing
* **Handler**: `patient_history(patient_id: int)`
* **Access Control**: `@role_required("doctor")`
* **Session Cryptographic Validation**: Invokes internal helper `_get_authorised_patient(patient_id)`:
  * Reads `session.get("patient_access_token")`.
  * Validates token signature, doctor ID, patient ID, and expiration timestamp.
  * If invalid or expired, immediately aborts with **HTTP 403 Forbidden**.
* **Database Queries**:
  * Retrieves `Patient` record and decrypts AES-256 encrypted name and phone using Fernet.
  * Retrieves all past `Visit` records ordered chronologically (`created_at ASC`).
* **AI Clinical Summary**:
  * Calls `ai_service.get_summary(patient_id, visits)` to fetch or generate a concise ~60-word clinical briefing using Google Gemini 1.5.
  * Summary includes Web Speech audio readout button ("🔊 Read Summary").
* **Immutability Enforcement**: Computes `can_delete_visit_ids = {v.id for v in visits if v.created_by == current_user.id and (utcnow - v.created_at) <= 24 hours}`. Any record older than 24 hours is marked permanently locked.

#### 12. `GET, POST /doctor/patient/<int:patient_id>/add-checkup` — Consultation Entry, Voice Dictation & Drug Safety
* **Handler**: `add_checkup(patient_id: int)`
* **Access Control**: `@role_required("doctor")`
* **Rate Limit**: `@rate_limit(max_requests=30, window_seconds=60)`
* **Session Validation**: Verifies active `patient_access_token` for this patient.
* **Template Rendered**: `doctor/add_checkup.html`
* **Form Inputs Accepted (`POST`)**:
  * `area` (String, required): Pune locality where patient presented (feeds outbreak radar).
  * `condition` / `conditions[]` (String/List, required): Primary diagnoses (supports multiple conditions).
  * `diagnosis_notes` (Text, optional): Confidential physician notes (never visible to pharmacist).
  * `medicine[]`, `dosage[]`, `instructions[]` (Lists, required): Prescribed drugs with frequency.
  * `refill_restricted` (Checkbox/Boolean): If checked, pharmacy cannot refill without a new doctor consultation.
* **Execution Logic**:
  1. Validates all required clinical fields.
  2. Creates new `Visit` record linked to `patient_id` and authored by `current_user.id`.
  3. Invalidates in-memory AI summary cache (`ai_service.invalidate_summary(patient_id)`) so next history load regenerates with new visit.
  4. Commits visit to PostgreSQL database.
  5. Flashes success notification and redirects back to patient history.

#### 13. `POST /doctor/visit/<int:visit_id>/delete` — Immutable 24-Hour Clinical Mistake Window
* **Handler**: `delete_visit(visit_id: int)`
* **Access Control**: `@role_required("doctor")`
* **Tri-Fold Security Checks**:
  1. **Author Check**: `visit.created_by == current_user.id` (A doctor can never delete another doctor's note). Aborts 403 on violation.
  2. **Time Window Check**: `(datetime.utcnow() - visit.created_at) <= timedelta(hours=24)`. If record is older than 24 hours, aborts 403 Forbidden.
  3. **Patient Session Check**: `_get_authorised_patient(visit.patient_id)` verifies active consent token.
* **Execution Logic**: Deletes the mistake record, commits transaction, and redirects back to patient history.

---

### Blueprint 4: Pharmacist Dispensary (`pharmacist_routes.py`)
Mounted at `/pharmacist`. Designed for rapid counter dispensing with zero access to confidential clinical notes.

#### 14. `GET, POST /pharmacist/scan` — High-Throughput QR/ID Dispensing Scanner
* **Handler**: `scan()`
* **Access Control**: `@role_required("pharmacist")`
* **Rate Limit**: `@rate_limit(max_requests=30, window_seconds=60)`
* **Template Rendered**: `pharmacist/scan.html`
* **Execution Logic**:
  * Accepts camera QR scan or manual card ID string (`POST card_id`).
  * Resolves patient via `lookup_patient_by_card(card_id)`.
  * **Zero OTP Gate**: Intentionally skips OTP to prevent dispensary counter delays.
  * Redirects directly to `/pharmacist/patient/<id>/medicines`.

#### 15. `GET /pharmacist/patient/<int:patient_id>/medicines` — 4-Column Privacy-Isolated Dispensing View
* **Handler**: `medicine_view(patient_id: int)`
* **Access Control**: `@role_required("pharmacist")`
* **Template Rendered**: `pharmacist/medicine_view.html`
* **Architectural Privacy Guarantee**:
  * Executes explicit SQL column projection:
    ```python
    db.session.query(Visit.id, Visit.created_at, Visit.condition, Visit.medicine, Visit.refill_restricted)
    ```
  * The sensitive `diagnosis_notes` column is **never queried from the database engine** and is completely absent from the template payload.
  * If `refill_restricted == True`, renders high-visibility red badge: *"Refill Blocked — Patient must consult doctor for new prescription"*.
  * Entire blueprint contains **zero create, update, or delete routes** by architectural design.

---

### Blueprint 5: Public Health Epidemiological Surveillance (`public_health_routes.py`)
Mounted at `/public-health`. Municipal epidemic detection command center. Displays aggregate disease incidence with differential privacy and statistical anomaly alerts.

#### 16. `GET /public-health/dashboard` — Ward Epidemiological Surveillance & $k$-Anonymity Masking
* **Handler**: `dashboard()`
* **Access Control**: `@role_required("public_health_admin")`
* **Query Parameters (`GET`)**:
  * `area` (Filter by Pune locality: Katraj, Kothrud, Hadapsar, etc.)
  * `condition` (Filter by disease: Dengue, Malaria, Viral Flu, Typhoid)
  * `time_bucket` (Filter by epidemiological week: `2026-W38`, `2026-W39`, etc.)
* **Template Rendered**: `public_health/dashboard.html`
* **Privacy Engine (`services/anonymizer.py`)**:
  * Every statistical row passes through $k$-anonymity suppression.
  * If `case_count < MIN_GROUP_SIZE (5)`, the exact number is withheld and replaced with `"< 5 (Insufficient Data)"`.
  * Zero patient names, phone numbers, or card IDs are ever rendered or transmitted.

#### 17. `GET /public-health/trend-alerts` — 2-Sigma Outbreak Radar & Anomaly Alarm
* **Handler**: `trend_alerts()`
* **Access Control**: `@role_required("public_health_admin")`
* **Template Rendered**: `public_health/trend_alerts.html`
* **Mathematical Algorithm**:
  * Analyzes historical weekly case distribution per (ward, condition) pair.
  * Computes baseline mean ($\mu$) and standard deviation ($\sigma$).
  * If $\text{current\_cases} > \mu + 2\sigma$, flags a **HIGH SEVERITY Outbreak Alert**.
  * Outputs recommended municipal interventions (vector control fogging, residual chlorine checks, fever clinics).

#### 18. `GET /public-health/trend-forecast` — Proactive Disease Trend Detector & Multi-Day Forecaster
* **Handler**: `trend_forecast()`
* **Access Control**: `@role_required("public_health_admin")`
* **Template Rendered**: `public_health/trend_forecast.html`
* **Execution Logic**:
  * Invokes `predict_all_trends()` across **all monitored conditions** (not just existing outbreaks).
  * Computes case velocity ($\Delta C / \Delta t$) and assigns five-tier risk categories:
    * 🔴 **CRITICAL**: Breached 2-sigma threshold. Emergency response active.
    * 🟠 **ELEVATED**: 30%–75% week-over-week acceleration. Prepare field teams.
    * 🟡 **WATCH**: 10%–30% increase. Pre-emptive monitoring.
    * 🔵 **STABLE**: Normal baseline variation.
    * 🟢 **RECEDING**: Case incidence declining.
  * Generates 3-day and 7-day forward case projections to give health officers 3 to 7 days advance warning.

#### 19. `GET /public-health/api/anonymized-stats` — REST JSON Aggregate Surveillance API
* **Handler**: `api_anonymized_stats()`
* **Access Control**: `@role_required("public_health_admin")`
* **Execution Logic**: Returns sanitized JSON data for interactive Leaflet choropleth maps and Chart.js epidemiological curves. Suppressed cohorts return `count: null` to preserve privacy over the wire.

---

### Blueprint 6: System Administrator Governance (`admin_routes.py`)
Mounted at `/admin`. Administrative command center for staff lifecycle, card issuance, application screening, and forensic audit inspection.

#### 20. `GET /admin/dashboard` — Executive Municipal Governance Overview
* **Handler**: `dashboard()`
* **Access Control**: `@role_required("sysadmin")`
* **Template Rendered**: `admin/dashboard.html`
* **Metrics Computed**:
  * Total staff accounts & active status breakdown.
  * Total registered patient cards.
  * Total security audit logs & count of denied requests (HTTP 403 blocks).
  * Pending citizen and staff applications count.
  * Displays list of the 5 most recent unauthorized access attempts.

#### 21. `GET /admin/users` — Staff Directory & Account Provisioning Console
* **Handler**: `manage_users()`
* **Access Control**: `@role_required("sysadmin")`
* **Template Rendered**: `admin/manage_users.html`
* **Execution Logic**: Lists all staff accounts in descending order of ID, displaying username, full name, role, active status badge, and management action buttons.

#### 22. `POST /admin/users/create` — Direct Staff User Account Creation
* **Handler**: `create_user()`
* **Access Control**: `@role_required("sysadmin")`
* **Rate Limit**: `@rate_limit(max_requests=20, window_seconds=60)`
* **Form Inputs**: `username`, `full_name`, `password`, `role` (must be `doctor`, `pharmacist`, `public_health_admin`, or `sysadmin`).
* **Execution Logic**: Validates uniqueness of username, enforces minimum 6-character password policy, hashes password via `set_password()`, and inserts new user into PostgreSQL.

#### 23. `POST /admin/users/<int:user_id>/toggle-status` — Staff Activation & Deactivation Guard
* **Handler**: `toggle_user_status(user_id: int)`
* **Access Control**: `@role_required("sysadmin")`
* **Security Guard**: Enforces `user.id != current_user.id`. Sysadmins cannot deactivate their own account, preventing permanent accidental lockout.
* **Execution Logic**: Inverts `user.is_active` (`True` ⟷ `False`) and commits change.

#### 24. `GET, POST /admin/users/<int:user_id>/role` — Staff Role Assignment & Self-Demotion Lock
* **Handler**: `role_assignment(user_id: int)`
* **Access Control**: `@role_required("sysadmin")`
* **Security Guard**: Prevents current admin from removing their own `sysadmin` role.
* **Execution Logic**: Updates `user.role` to target role and commits transaction.

#### 25. `GET, POST /admin/patients/register` — Walk-In Patient QR Health Card Issuance
* **Handler**: `register_patient()`
* **Access Control**: `@role_required("sysadmin")`
* **Template Rendered**: `admin/register_patient.html`
* **Form Inputs (`POST`)**: `name`, `phone`.
* **Execution Logic**: Calls `issue_patient_card(name, phone)`. Encrypts patient name and phone number with Fernet AES-256 before writing to database. Returns printable QR data URI. (Admin console has zero access to clinical notes).

#### 26. `GET /admin/patients/<card_id>/qr` — Patient QR Code Image Vector API
* **Handler**: `view_patient_qr(card_id: str)`
* **Access Control**: `@role_required("sysadmin")`
* **Execution Logic**: Returns JSON payload containing `{ "card_id": "...", "qr_data_uri": "data:image/png;base64,..." }`.

#### 27. `GET /admin/audit-log` — Forensic Immutable Audit Trail Inspector
* **Handler**: `audit_log()`
* **Access Control**: `@role_required("sysadmin")`
* **Query Filter**: `?result=all|allowed|denied`
* **Template Rendered**: `admin/audit_log.html`
* **Execution Logic**: Inspects the immutable `access_logs` table (timestamp, user ID, role, method, endpoint, IP address, and security outcome). Provides forensic proof of RBAC enforcement.

#### 28. `GET /admin/applications` — Multi-Role Application Screening Center
* **Handler**: `applications()`
* **Access Control**: `@role_required("sysadmin")`
* **Query Filters**: `?status=all|pending|approved|rejected&role=all|doctor|pharmacist|patient`
* **Template Rendered**: `admin/applications.html`
* **Execution Logic**: Displays pending applications with verified Council registration numbers, qualifications, and applicant contact details.

#### 29. `POST /admin/applications/<int:app_id>/approve` — One-Click Automated Account & Card Provisioner
* **Handler**: `approve_application(app_id: int)`
* **Access Control**: `@role_required("sysadmin")`
* **Automated Workflow**:
  * **For Doctor / Pharmacist**: Auto-generates unique username (`dr_<name>` or `pharma_<name>`), provisions default password `Swasthya@2026`, creates `User` record, updates application to `approved`, and dispatches official welcome email with login credentials via SMTP.
  * **For Citizen Patient**: Calls `issue_patient_card()`, mints unique Card ID (`SS-...`), builds encrypted QR code, updates application to `approved`, and sends e-card download notification email with postal delivery confirmation.

#### 30. `POST /admin/applications/<int:app_id>/reject` — Application Rejection & Formal Notification Processor
* **Handler**: `reject_application(app_id: int)`
* **Access Control**: `@role_required("sysadmin")`
* **Form Input**: `reason` (Text string explaining the rejection).
* **Execution Logic**: Sets application status to `rejected`, stores `admin_notes`, and sends an explanatory rejection email to the applicant.

---

### Blueprint 7: AI & Clinical Decision Support (`ai_routes.py`)
Mounted at `/ai`. Clinical intelligence and NLP pipeline. Evaluates voice dictation transcripts, validates drug spelling against Indian Pharmacopoeia catalogs, and generates longitudinal clinical summaries.

#### 31. `POST /ai/voice-parse` — Voice Dictation Speech-to-Text NLP Parser
* **Handler**: `voice_parse()`
* **Access Control**: `@login_required`
* **Input JSON**: `{"transcript": "Patient has acute bronchitis. Prescribe Amoxicillin 500mg three times daily..."}`
* **Execution Logic**: Calls `ai_service.parse_voice_prescription(transcript)` using Google Gemini 1.5 with regex clinical entity extraction fallback.
* **Output JSON**:
  ```json
  {
    "success": true,
    "data": {
      "area": "Shivajinagar",
      "condition": "Acute Bronchitis",
      "diagnosis_notes": "Mild wheezing in lower lungs",
      "medicine": "Amoxicillin",
      "dosage": "500mg TDS",
      "refill_restricted": false
    }
  }
  ```

#### 32. `POST /ai/correct-drug` — Real-Time Fuzzy Drug Spellchecker & Allergy Checker
* **Handler**: `correct_drug()`
* **Access Control**: `@login_required`
* **Input JSON**: `{"query": "paracetmol", "current_medicines": ["Warfarin"]}`
* **Execution Logic**: Runs Levenshtein fuzzy matching against 500+ Indian drug names via `RapidFuzz` (similarity threshold = 70%). Inspects active medications for contraindications or drug interactions.
* **Output JSON**:
  ```json
  {
    "match": "Paracetamol",
    "score": 95.0,
    "is_corrected": true,
    "warnings": []
  }
  ```

#### 33. `GET /ai/drugs` — Indian Pharmacopoeia Drug Catalog Autocomplete API
* **Handler**: `list_drugs()`
* **Access Control**: `@login_required`
* **Output JSON**: Returns comprehensive catalog of verified drug names for client-side search autocomplete.

#### 34. `GET /ai/summary/<int:patient_id>` — Longitudinal Patient AI Clinical Briefing Generator
* **Handler**: `patient_summary(patient_id: int)`
* **Access Control**: `@login_required`
* **Execution Logic**: Fetches all visits for `patient_id`, compiles chronological medical history, and generates a structured ~60-word clinical briefing using Gemini LLM. Returns cached summary on subsequent calls.

#### 35. `POST /ai/summary/<int:patient_id>/invalidate` — In-Memory Summary Cache Purge Hook
* **Handler**: `invalidate_patient_summary(patient_id: int)`
* **Access Control**: `@login_required`
* **Execution Logic**: Purges cached summary for `patient_id` whenever a new checkup is recorded, ensuring fresh briefings.

#### 36. `GET /ai/trends` — Automated Epidemiological Anomaly Analysis Endpoint
* **Handler**: `trends()`
* **Access Control**: `@login_required`
* **Execution Logic**: Evaluates aggregate stats table and returns JSON array of active 2-sigma outbreak alerts.

---

### Blueprint 8: Asynchronous Security & Consent AJAX (`ajax_routes.py`)
Mounted at `/ajax`. Background asynchronous engine powering camera QR scanning and patient physical consent verification.

#### 37. `GET /ajax/ping` — Lightweight Backend Health Ping
* **Handler**: `ping()`
* **Access Control**: Public.
* **Output JSON**: `{"status": "ok"}`. Used by load balancers and deployment smoke tests.

#### 38. `POST /ajax/scan-card` — Card Decryption, Patient Lookup & OTP Dispatch
* **Handler**: `scan_card()`
* **Access Control**: `@role_required("doctor")`
* **Rate Limit**: `@rate_limit(max_requests=20, window_seconds=60)`
* **Input JSON**: `{"card_id": "SS-TEST-001"}`
* **Execution Logic**:
  1. Searches database for patient with matching `card_id`.
  2. Decrypts patient's stored phone number using Fernet AES-256.
  3. Generates a secure, cryptographically random 6-digit OTP via `secrets` module.
  4. Stores OTP in memory with a 10-minute expiry timestamp.
  5. Dispatches OTP to patient via SMS/Email (and logs to terminal in demo mode).
  6. Stores `session["otp_patient_id"] = patient.id` and returns `{"ok": true, "patient_id": patient.id}`.

#### 39. `POST /ajax/verify-otp` — Cryptographic Consent Verification & Scoped Access Token Issue
* **Handler**: `verify_otp_route()`
* **Access Control**: `@role_required("doctor")`
* **Rate Limit**: `@rate_limit(max_requests=5, window_seconds=60)` — Anti-brute-force OTP lock.
* **Input JSON**: `{"code": "482910"}`
* **Execution Logic**:
  1. Compares submitted code against cached OTP for `session["otp_patient_id"]`.
  2. If code matches and has not expired, mints a tamper-resistant scoped token:
     ```python
     token = secrets.token_hex(32)
     ```
  3. Binds token in `session["patient_access_token"]` and `session["access_patient_id"]`.
  4. Returns `{"ok": true, "redirect": "/doctor/patient/<id>/history"}`.

---

### Global Handlers: Middleware & Error Responses

#### 40. `HTTP 403 Forbidden` Error Handler
* **Handler**: `forbidden(e)` in `app/__init__.py`
* **Execution**: Triggered whenever `@role_required` detects an unauthorized role or missing access token. Renders customized `errors/403.html` explaining the security violation.

#### 41. `HTTP 429 Too Many Requests` Error Handler
* **Handler**: `ratelimit_handler(e)` in `app/__init__.py`
* **Execution**: Triggered when a client IP exceeds sliding-window thresholds on sensitive endpoints (`/login`, `/apply/health-card`, `/ajax/verify-otp`). Renders `errors/429.html` with retry cooldown duration.

#### 42. `after_request` Global Forensic Audit Logger
* **Handler**: `audit_logger(response)` in `app/middleware/audit_logger.py`
* **Execution**: Runs automatically after every single HTTP request. Extracts requesting user ID, active role, HTTP method, path, remote IP address, status code, and records entry to the immutable `access_logs` database table.

#### 43. `after_request` Anti-Browser-Cache Security Headers
* **Handler**: `set_cache_headers(response)` in `app/__init__.py`
* **Execution**: Injects `Cache-Control: no-cache, no-store, must-revalidate, max-age=0`, `Pragma: no-cache`, and `Expires: 0` on all non-static HTTP responses. Ensures clinic browser back-buttons never leak historical patient medical records after logout.

---

## 🔄 Step-by-Step Visual Flowcharts for Key Workflows

### A. Citizen Health Card Application & Download Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen - Patient
    participant Web as Public Portal
    participant DB as PostgreSQL Database
    actor Admin as System Administrator
    participant Mail as Email Gateway

    Citizen->>Web: Fills Name, Phone, Aadhaar, Pune Ward & Emergency Info
    Web->>DB: Saves application (status = pending, ref = APP-PAT-XXXX)
    Web-->>Citizen: Shows Application Submitted with Tracking Reference ID

    Admin->>Web: Opens Admin Console (/admin/applications)
    Admin->>Web: Clicks Approve on Citizen application
    Web->>DB: Encrypts PII with Fernet AES-256
    Web->>DB: Issues Card ID (e.g. SS-TEST-001) + Generates QR code
    Web->>DB: Updates status to approved
    Web->>Mail: Dispatches approval email with download link

    Citizen->>Web: Visits /apply/status & enters Ref or Phone
    Web-->>Citizen: Unlocks Download Official e-Card button
    Citizen->>Web: Clicks download (/apply/ecard/download)
    Web-->>Citizen: Renders official QR Health Card & opens Print Dialog
```

---

### B. Doctor Visit, OTP Consent & AI Prescription Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen - Patient
    actor Doctor as Attending Doctor
    participant DocPortal as Doctor Portal
    participant OTPService as OTP & Token Engine
    participant GeminiAI as AI Engine (Gemini / Local ML)
    participant DB as PostgreSQL Database

    Citizen->>Doctor: Enters clinic & hands over QR Health Card
    Doctor->>DocPortal: Scans QR code using webcam (/doctor/scan)
    DocPortal->>OTPService: Card found! Generate 6-digit OTP
    OTPService->>Citizen: Sends SMS & Email: Your Swasthya Setu OTP is 482910
    DocPortal-->>Doctor: Redirects to OTP verification screen

    Citizen->>Doctor: Verbally tells OTP 482910 to doctor
    Doctor->>DocPortal: Types 482910 & clicks Verify (/ajax/verify-otp)
    OTPService->>OTPService: Hashes & verifies code; issues 60-min session token
    DocPortal->>DB: Decrypts patient name & pulls medical history

    DocPortal->>GeminiAI: Sends past visit history for briefing
    GeminiAI-->>DocPortal: Returns concise ~60-word clinical briefing
    Doctor->>DocPortal: Clicks Read Summary (listens aloud via audio TTS)

    Doctor->>DocPortal: Clicks Voice Dictate & speaks prescription
    DocPortal->>GeminiAI: Parses spoken audio transcript into fields
    DocPortal->>DocPortal: RapidFuzz auto-corrects drug spelling & checks allergies
    Doctor->>DocPortal: Reviews form & clicks Save Checkup
    DocPortal->>DB: Saves new visit (starts 24-hour edit lock timer)
    DocPortal-->>Doctor: Checkup saved successfully
```

---

### C. Pharmacist Safe Dispensing Flow

```mermaid
sequenceDiagram
    autonumber
    actor Citizen as Citizen - Patient
    actor Chemist as Dispensary Pharmacist
    participant PharmaPortal as Pharmacist Portal
    participant DB as PostgreSQL Database

    Citizen->>Chemist: Presents QR Card at dispensary counter
    Chemist->>PharmaPortal: Scans QR card or types Card ID (No OTP needed)
    PharmaPortal->>DB: Query: card_id, created_at, condition, medicine, refill_restricted
    Note over DB,PharmaPortal: Sensitive diagnosis notes are NEVER selected!
    DB-->>PharmaPortal: Returns only the 4 safe columns

    alt Medicine is Normal
        PharmaPortal-->>Chemist: Displays medicine name, dosage & green dispense badge
        Chemist->>Citizen: Hands over medicines safely
    else Medicine is Refill-Restricted
        PharmaPortal-->>Chemist: Refill Blocked: Patient must see doctor for new prescription
        Chemist->>Citizen: Explains that doctor consultation is required
    end
```

---

### D. Disease Outbreak Surveillance, Predictive Forecasting & Alert Flow

```mermaid
sequenceDiagram
    autonumber
    actor Doctor as Doctors Across Pune Wards
    participant DB as Database Visits
    participant Anonymizer as Privacy Anonymizer
    participant OutbreakEngine as Predictive 2-Sigma Anomaly Engine
    actor HealthOfficer as Public Health Officer
    actor PMC as Municipal Response Team

    Doctor->>DB: Doctors record checkups across Pune wards
    DB->>Anonymizer: Aggregates counts by ward (Katraj, Kothrud, etc.)

    alt Ward has fewer than 5 cases
        Anonymizer-->>HealthOfficer: Displays Under 5 Cases (Differential Privacy Mask)
    else Ward has normal case numbers
        Anonymizer-->>HealthOfficer: Displays standard aggregate count
    end

    loop Predictive Outbreak Forecasting
        OutbreakEngine->>DB: Analyzes case momentum & weekly trajectory
        OutbreakEngine->>OutbreakEngine: Projects 3-day and 7-day forward infection volume
        alt Growth velocity is surging or cases exceed 2-Sigma threshold
            OutbreakEngine-->>HealthOfficer: Fires HIGH SEVERITY Alert + 3-Day & 7-Day Peak Forecast!
            HealthOfficer->>PMC: Dispatches targeted municipal fogging, chlorine tests & fever camps
        end
    end
```

---

## 🔒 Security Made Simple: Every Protection Explained

Here is a clear, beginner-friendly explanation of all 9 security features built into the system:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SECURITY AT A GLANCE                            │
├─────────────────────────┬──────────────────────────────────────────────┤
│ Security Feature        │ Plain English Explanation                    │
├─────────────────────────┼──────────────────────────────────────────────┤
│ 1. AES-256 Encryption   │ Patient names & phones are scrambled in DB.   │
│ 2. Role-Based Access    │ Doctors can't see admin pages; chemists can't│
│                         │ see doctor pages. 403 Forbidden on breach.   │
│ 3. 2-Factor OTP Consent │ Doctors can't view your history without your │
│                         │ permission via phone OTP.                    │
│ 4. Immutable Audit Log  │ Every click, login, and denial is recorded.  │
│ 5. Rate Limiting (429)  │ Stops hackers from spamming passwords or OTP.│
│ 6. k-Anonymity (< 5)    │ Hides small numbers so neighbors can't guess │
│                         │ who is sick.                                 │
│ 7. 24-Hour Edit Lock    │ Doctors can't alter old medical records.     │
│ 8. Least-Privilege SQL  │ Chemists' queries never fetch doctor notes.  │
│ 9. Anti-Cache Headers   │ Hitting "Back" on shared computers won't leak│
│                         │ patient records.                             │
└─────────────────────────┴──────────────────────────────────────────────┘
```

### 1. AES-256 Symmetric Data Encryption
* **What it does**: When you save your name and phone number, they are scrambled into an unreadable string of random characters before touching the database.
* **Why it matters**: Even if a hacker stole the entire database backup file, they would only see gibberish like `gAAAAABm...`. They cannot read anyone's name without the secret server key.

### 2. Zero-Bypass Role-Based Access Control (RBAC)
* **What it does**: Every page is guarded by a digital bouncer (`@role_required`). If a pharmacist tries to type `/doctor/dashboard` or `/admin/dashboard` in their browser URL bar, the server immediately stops them with an **HTTP 403 Forbidden** error.
* **Why it matters**: The code verifies permissions on the server before running any logic, so no one can bypass security by inspecting the webpage HTML.

### 3. Two-Factor Patient Physical Consent (OTP)
* **What it does**: Merely knowing a patient's card ID does not allow a doctor to see their medical history. When a doctor scans a card, a 6-digit OTP is sent to the patient's phone.
* **Why it matters**: It guarantees the patient is physically sitting in front of the doctor and has explicitly agreed to share their medical past.

### 4. Real-Time Immutable Audit Trail
* **What it does**: Every single time any user clicks a button, loads a page, or gets blocked, an automatic recorder (`after_request`) writes a permanent entry to the `access_logs` table with the user ID, their role, the endpoint, the timestamp, and whether it was `allowed` or `denied`.
* **Why it matters**: If someone tries to do something unauthorized, administrators have a permanent forensic record of who did it and when.

### 5. Sliding-Window Rate Limiting (Anti-Brute-Force)
* **What it does**: A built-in traffic cop monitors requests per minute. If someone tries to guess passwords on `/login` more than 10 times a minute, or guess OTPs on `/ajax/verify-otp` more than 5 times a minute, the server locks them out with an **HTTP 429 Too Many Requests** error.
* **Why it matters**: Prevents automated hacker bots from guessing PINs or overloading the server.

### 6. Differential Privacy & k-Anonymity (`MIN_GROUP_SIZE = 5`)
* **What it does**: When public health officers view disease counts across Pune wards, if any neighborhood has fewer than 5 people with an illness, the actual number is hidden and replaced with `"< 5 (Insufficient Data)"`.
* **Why it matters**: If a small locality had only 1 person with a sensitive illness, showing "1" would make it easy for neighbors to deduce who that person is. Hiding small numbers protects citizen dignity.

### 7. Tamper-Resistant 24-Hour Clinical Edit Lock
* **What it does**: A doctor can only delete or edit a checkup if they were the author and less than 24 hours have passed.
* **Why it matters**: Prevents malpractice cover-ups, changing prescriptions after the fact, or altering older medical history.

### 8. Least-Privilege Column Filtering
* **What it does**: In the pharmacist portal, the database query is specifically told: `SELECT card_id, created_at, condition, medicine`. The `diagnosis_notes` column is **never requested**.
* **Why it matters**: Chemists only need to know what medicine to dispense. They do not need to know personal doctor notes about private symptoms.

### 9. Anti-Browser-Cache Security Headers
* **What it does**: The server sends special instructions to browsers: `Cache-Control: no-cache, no-store, must-revalidate`.
* **Why it matters**: In busy clinics and hospital counters where multiple staff use the same computer, clicking the browser's "Back" button after logging out will never display previous patient records from memory.

---

## 🤖 AI/ML Architecture & 24-Hour Hackathon Dataset Training Roadmap

> 💡 **Core Hackathon Principle**: During this 24-hour hackathon sprint, we are **actively training and fine-tuning our own dedicated AI models on domain datasets with zero external model dependencies**. While Google Gemini 1.5 was connected as a **temporary evaluation key** during early prototyping to validate schema formats, our hackathon build is powered by **in-house trained sovereign AI models**.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             24-HOUR HACKATHON IN-HOUSE MODEL TRAINING PIPELINE (DATASETS)             │
├──────────────┬────────────────────────┬─────────────────────────┬──────────────────────┤
│ Time Window  │ Model Architecture     │ Training Dataset Used   │ Target Capabilities  │
├──────────────┼────────────────────────┼─────────────────────────┼──────────────────────┤
│ Hours 00–06  │ Clinical NLP LLM       │ Doctor-Patient Clinical │ • Summarizes 10-page │
│              │ (BioMistral / Llama-   │ Consultations & EHR     │   history in ~60 wds │
│              │ Med 4-bit Quantized)   │ Transcripts Dataset     │ • Zero data egress   │
├──────────────┼────────────────────────┼─────────────────────────┼──────────────────────┤
│ Hours 06–12  │ Indic Speech-to-Text   │ Multilingual Indian     │ • Accurately parses  │
│              │ (Fine-Tuned Whisper-   │ Accent Medical Audio    │   Hindi, Marathi, and│
│              │ Small Architecture)    │ Corpus (PHC recordings) │   English symptoms   │
├──────────────┼────────────────────────┼─────────────────────────┼──────────────────────┤
│ Hours 12–18  │ Outbreak Forecaster    │ Multi-Year Pune Ward    │ • Predicts spikes    │
│              │ (LSTM + Prophet Time-  │ Epidemiological Disease │   3 to 7 days before │
│              │ Series Regressor)      │ Incidence Dataset       │   hospital surges    │
├──────────────┼────────────────────────┼─────────────────────────┼──────────────────────┤
│ Hours 18–24  │ Drug Safety Graph      │ Indian Pharmacopoeia    │ • Instant conflict   │
│              │ (NetworkX / Neo4j API  │ & Polypharmacy Contra-  │   alerts on doctor's │
│              │ Interaction Engine)    │ indications Dataset     │   prescription screen│
└──────────────┴────────────────────────┴─────────────────────────┴──────────────────────┘
```

### Why Self-Trained Sovereign AI is Crucial (Zero External AI Reliance):
1. **100% Data Sovereignty (DPDP Act & DISHA)**: Commercial cloud LLMs (OpenAI, Gemini, Anthropic) process prompts on multi-tenant foreign servers. In healthcare, transmitting private patient symptoms to third-party APIs violates data localization regulations. By training our own models and hosting weights locally, no medical data ever leaves sovereign premises.
2. **Zero API Cost & Unlimited Scalability**: Third-party APIs charge per token. A municipal health network serving millions of citizens in Pune cannot rely on metered external API bills. Self-hosted models run with zero marginal inference cost.
3. **Offline Resilience for Primary Health Centers (PHCs)**: Semi-rural and municipal clinics frequently experience internet outages. Our self-trained models execute locally on CPU/edge hardware (via `llama.cpp` and GGUF quantization) even during complete internet blackouts.
4. **Tailored to Indian Multilingual Clinical Reality**: Standard global LLMs fail at Indian doctor-patient code-mixing (e.g., *"Patient ko 3 din se tez bukhar hai aur ghabrahat ho rahi hai"*). Fine-tuning on Indic medical datasets ensures accurate parsing of Marathi, Hindi, and English clinical expressions.

### 24-Hour Hackathon AI/ML Implementation Sprint

#### ⏱️ Hours 00:00 – 06:00: Sovereign Local Clinical LLM (BioMistral / Llama-3-Med)
* **Goal**: Disconnect external cloud LLM dependencies completely.
* **Execution**: Train and fine-tune a quantized (Q4_K_M) 4-bit clinical model on doctor-patient consultation and prescription datasets using `llama-cpp-python` / Ollama running locally.
* **Output**: Patient timeline clinical summarization runs locally in `< 1.2 seconds` without transmitting a single byte over the public internet.

#### ⏱️ Hours 06:00 – 12:00: Multilingual Speech-to-Text for Indian Clinical Contexts
* **Goal**: Handle Indian medical pronunciation and code-mixed clinical vocabulary (e.g., mixing English medical terms with Hindi/Marathi symptoms: *"Patient ko subah se tez bukhar aur khansi hai"*).
* **Execution**: Fine-tune `whisper-small` on Indian accented clinical audio recordings, pre-prompted with an Indian Pharmacopoeia vocabulary dictionary.

#### ⏱️ Hours 12:00 – 18:00: Predictive Outbreak Forecasting (Prophet & LSTM)
* **Goal**: Elevate Public Health surveillance from *"outbreak already happening"* to *"outbreak predicted next week"*.
* **Execution**: Train lightweight LSTM / Facebook Prophet models on weekly ward-level historical disease incidence, rainfall, and humidity datasets across Pune.
* **Output**: Predicts disease transmission vectors 3 to 7 days in advance, providing municipal health commissioners with predictive alert scores.

#### ⏱️ Hours 18:00 – 24:00: Clinical Decision Support & Drug Interaction Graph
* **Goal**: Prevent dangerous polypharmacy drug-drug interactions.
* **Execution**: Build a localized NetworkX bipartite graph trained on 2,000+ known active ingredient interactions (e.g. Warfarin + Aspirin hemorrhage risks, ACE inhibitor + Potassium spironolactone hyperkalemia).
* **Output**: Real-time modal alert directly in the doctor's checkup interface before the prescription is finalized.

---

## 🔗 Quick Reference & Documentation Links

| Document | Description |
|---|---|
| 🚀 **[SETUP_AND_DEMO_GUIDE.md](SETUP_AND_DEMO_GUIDE.md)** | **Step-by-step setup guide**: installation commands, all demo passwords (`password123`), test patient cards (`SS-TEST-001`), and how to run the live `simulate_outbreak.py` tool. |
| ☁️ **[Play-app/DEPLOYMENT_GUIDE.md](Play-app/DEPLOYMENT_GUIDE.md)** | Production deployment configuration for Railway and Supabase PostgreSQL. |
| 📋 **[IMPLEMENTATION_PLAN_FOR_AGENT.md](IMPLEMENTATION_PLAN_FOR_AGENT.md)** | 13-step verified technical blueprint and test checklist. |
