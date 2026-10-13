import type { ReactNode } from 'react'
import { Emblem, HealthCard } from '../ui'

const SH = { boxShadow: '0 2px 8px rgba(0,0,0,0.04)' }
const Frame = ({ w, children, path }: { w: number; children: ReactNode; path: string }) => (
  <div className="bg-white min-h-[760px] py-14 px-6 border-b border-line">
    <div className="mx-auto" style={{ maxWidth: w }}><div className="font-mono text-[11px] text-slate2 mb-4">{path}</div>{children}</div>
  </div>
)
const Panel = ({ children, className = '' }: { children: ReactNode; className?: string }) => (
  <div className={`bg-white border border-line rounded-2xl p-8 md:p-10 ${className}`} style={SH}>{children}</div>
)
const Title = ({ t, s }: { t: string; s?: string }) => (<div className="mb-8"><h1 className="text-[28px] md:text-[32px] font-extrabold tracking-tight leading-tight">{t}</h1>{s && <p className="text-slate2 mt-2">{s}</p>}</div>)
const Sec = ({ n, t, children }: { n: number; t: string; children: ReactNode }) => (
  <div className="mb-10"><div className="flex items-center gap-3 mb-5"><span className="w-6 h-6 rounded-full bg-peach border border-[#fed7aa] text-saffron text-xs font-bold grid place-items-center">{n}</span><h2 className="font-bold">{t}</h2></div>{children}</div>
)
function F({ l, ph, v, sel, mono, icon, area }: { l: string; ph?: string; v?: string; sel?: string[]; mono?: boolean; icon?: string; area?: boolean }) {
  return (
    <div><label className="label">{l}</label>
      <div className="relative">
        {sel ? <select className="input appearance-none pr-9" defaultValue={v}>{sel.map((o) => <option key={o}>{o}</option>)}</select>
          : area ? <textarea className="input h-28 py-3" placeholder={ph} defaultValue={v} />
          : <input className={`input ${mono ? 'font-mono' : ''}`} placeholder={ph} defaultValue={v} />}
        {(sel || icon) && <span className="absolute right-3 top-1/2 -translate-y-1/2 text-slate2 text-xs pointer-events-none">{icon ?? '▾'}</span>}
      </div>
    </div>
  )
}
const G = ({ c, children }: { c: string; children: ReactNode }) => <div className={`grid gap-5 ${c}`}>{children}</div>

export function ApplyFrame() {
  return (
    <Frame w={880} path="/apply/health-card">
      <Title t="Apply for Swasthya Setu Digital Health Card" s="Citizen & Patient Registration — Pune Health Network" />
      <div className="rounded-xl px-5 py-4 text-sm font-medium mb-8" style={{ background: '#EFF6FF', color: '#1D4ED8' }}>📧 Important: A valid email address is required — your Digital Health e-Card will be delivered directly to your inbox upon approval.</div>
      <Panel>
        <Sec n={1} t="Personal & Demographic Information"><G c="md:grid-cols-2">
          <F l="Full Legal Name (as per Aadhaar / Govt ID) *" ph="e.g. Ramesh Shankar Kulkarni" /><F l="Date of Birth *" v="14/08/1984" icon="📅" />
          <F l="Gender *" v="Male" sel={['Male', 'Female', 'Other / Transgender']} /><F l="Blood Group *" v="O+" sel={['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']} /></G></Sec>
        <Sec n={2} t="Contact & Identification Proof"><G c="md:grid-cols-2">
          <F l="Mobile Phone Number *" ph="10-digit mobile number" v="9822012345" mono /><F l="Email Address *" ph="e.g. ramesh.kulkarni@example.com" />
          <F l="Government ID Type *" v="Aadhaar Card" sel={['Aadhaar Card', 'Voter ID', 'PAN Card', 'Driving License']} /><F l="Government ID Number *" ph="e.g. 12-digit Aadhaar / Voter ID" v="4821 9024 1182" mono /></G></Sec>
        <Sec n={3} t="Pune Locality & Address"><G c="md:grid-cols-[1fr_2fr]">
          <F l="Pune Locality / Ward *" v="Shivajinagar (Ward A)" sel={['Shivajinagar (Ward A)', 'Kothrud', 'Katraj', 'Hadapsar', 'Viman Nagar', 'Aundh', 'Baner', 'Swargate', 'Camp', 'Deccan Gymkhana']} />
          <F l="Full Residential Address *" ph="e.g. Flat 302, Sai Residency, Katraj-Kondhwa Road, Pune 411046" /></G></Sec>
        <Sec n={4} t="Emergency Contact"><G c="md:grid-cols-3">
          <F l="Emergency Contact Full Name *" ph="e.g. Sunita Kulkarni" /><F l="Relationship *" v="Spouse" sel={['Spouse', 'Parent', 'Child', 'Sibling', 'Other']} /><F l="Emergency Phone Number *" ph="10-digit phone number" v="9822098765" mono /></G></Sec>
        <Sec n={5} t="Clinical Baseline & Allergies"><G c="md:grid-cols-2">
          <F l="Known Chronic Medical Conditions" ph="e.g. Hypertension, Type 2 Diabetes, Asthma (or 'None')" /><F l="Known Drug Allergies" ph="e.g. Penicillin, Sulfa drugs, Paracetamol (or 'None')" /></G></Sec>
        <label className="flex gap-3 items-start bg-sage border border-[#bbf7d0] rounded-xl p-5 mb-8 text-sm cursor-pointer"><input type="checkbox" defaultChecked className="mt-0.5 w-4 h-4 accent-emerald2" />I declare that the information provided is authentic and consent to the issuance of a Swasthya Setu Digital Health Card under the DPDP Act 2023.</label>
        <button className="btn btn-saffron w-full h-12">Submit Health Card Application →</button>
      </Panel>
    </Frame>
  )
}

const Row = ({ k, v, mono }: { k: string; v: string; mono?: boolean }) => (<div><div className="eyebrow mb-1">{k}</div><div className={`font-semibold ${mono ? 'font-mono text-sm' : ''}`}>{v}</div></div>)
export function StatusFrame() {
  return (
    <Frame w={800} path="/apply/status">
      <Title t="Application Status" s="Track your Digital Health Card in real time." />
      <div className="flex gap-3 mb-6"><input className="input h-12" placeholder="Enter Ref ID (e.g. APP-PAT-XXXXXX) or Mobile Number" defaultValue="APP-PAT-2026-EDD70F" /><button className="btn btn-saffron h-12">Search Status</button></div>
      <Panel>
        <div className="flex flex-wrap justify-between items-center gap-3 mb-6">
          <span className="pill" style={{ background: '#F3E8FF', borderColor: '#E9D5FF', color: '#7E22CE' }}>🪪 HEALTH CARD APPLICANT</span>
          <span className="pill" style={{ background: '#DCFCE7', borderColor: '#BBF7D0', color: '#15803D' }}><span className="dot" />APPROVED & ACTIVE</span></div>
        <div className="text-2xl font-bold mb-1">Suresh Balkrishna Patil</div><div className="font-mono text-xs text-slate2 mb-8">Ref: APP-PAT-2026-EDD70F</div>
        <div className="grid sm:grid-cols-2 gap-6 pt-6 border-t border-line mb-8">
          <Row k="Mobile" v="+91 98220 12345" mono /><Row k="Email" v="suresh.patil@example.com" /><Row k="Assigned Card ID" v="SS-PUN-2026-904128" mono /><Row k="Ward" v="Shivajinagar" /></div>
        <button className="btn w-full h-12 text-white" style={{ background: '#15803D' }}>⬇️ Download Digital Health e-Card (PNG/PDF)</button>
      </Panel>
    </Frame>
  )
}

export function LoginFrame() {
  const dir = [['🩺 Doctor OPD', 'dr.rajesh.kulkarni'], ['💊 Pharmacist', 'ramesh.kadam'], ['📊 Epidemiologist', 'dr.meenakshi.sundaram'], ['🛡️ System Admin', 'director.raman']]
  return (
    <Frame w={460} path="/login">
      <Panel>
        <div className="flex flex-col items-center text-center mb-8"><Emblem size={56} /><div className="font-extrabold text-xl mt-3">Swasthya Setu</div><div className="font-mono text-[10px] tracking-[0.2em] text-slate2 mt-1">SCAN • CARE • TOGETHER</div></div>
        <h1 className="text-2xl font-extrabold tracking-tight text-center">Staff Sign In</h1><p className="text-slate2 text-sm text-center mt-1 mb-8">Healthcare Practitioner & Administrative Staff Access</p>
        <div className="grid gap-5 mb-6"><F l="Username" ph="e.g. dr.rajesh.kulkarni" /><div><label className="label">Password</label><input type="password" className="input" placeholder="Enter your password" /></div></div>
        <button className="btn btn-saffron w-full h-12 mb-8">Authenticate & Sign In</button>
        <div className="eyebrow mb-3">Accredited directory</div>
        <div className="grid grid-cols-2 gap-2.5">{dir.map(([a, b]) => <div key={b} className="lift border border-line rounded-xl p-3.5 cursor-pointer"><div className="text-sm font-semibold">{a}</div><div className="font-mono text-[11px] text-slate2 mt-0.5">{b}</div></div>)}</div>
        <div className="mt-8 pt-6 border-t border-line text-center text-xs text-slate2">🔒 Built with Patient Consent & Role-Based Privacy.</div>
      </Panel>
    </Frame>
  )
}

export function ScanFrame() {
  const chips = ['Meera Joshi (Card: SS-TEST-001 · Shivajinagar)', 'Arjun Sharma (Card: SS-TEST-002 · Kothrud)', 'Kavita Patil (Card: SS-TEST-003 · Katraj)']
  return (
    <Frame w={640} path="/doctor/scan & /doctor/otp-verify">
      <div className="bg-alabaster border border-line rounded-2xl p-5 mb-6">
        <div className="text-sm font-bold mb-3 flex items-center gap-2"><span className="dot" />Active OPD Registry Roster (Fast-Track Check-In) — Shift: Morning OPD</div>
        <div className="grid gap-2">{chips.map((c) => <button key={c} className="lift text-left text-sm bg-alabaster border rounded-lg px-4 py-2.5" style={{ borderColor: '#CBD5E1' }}>📋 {c}</button>)}</div></div>
      <Panel className="!p-6 mb-8">
        <div className="relative aspect-[4/3] rounded-xl grid place-items-center text-center px-10 mb-5" style={{ background: '#0F172A' }}>
          {['top-5 left-5 border-t-4 border-l-4 rounded-tl-xl', 'top-5 right-5 border-t-4 border-r-4 rounded-tr-xl', 'bottom-5 left-5 border-b-4 border-l-4 rounded-bl-xl', 'bottom-5 right-5 border-b-4 border-r-4 rounded-br-xl'].map((c) => <span key={c} className={`absolute w-10 h-10 border-emerald-500 ${c}`} />)}
          <span className="text-slate-300 text-sm">📷 Camera active — hold the QR code steady in front of lens</span></div>
        <button className="btn btn-ghost w-full mb-4">📁 Upload QR Card Image</button>
        <div className="flex gap-2"><input className="input font-mono" placeholder="Card ID e.g. SS-TEST-001" /><button className="btn btn-saffron">Look Up Patient</button></div>
      </Panel>
      <Panel>
        <h2 className="text-xl font-bold">Patient Consent Authorization</h2><p className="text-slate2 text-sm mt-1 mb-6">A 6-digit PIN has been dispatched to Meera Joshi's registered contact.</p>
        <div className="bg-sage rounded-xl p-5 mb-6 border border-[#bbf7d0]" style={{ borderLeft: '4px solid #15803D' }}>
          <div className="text-xs font-bold text-emerald2 mb-3">ABDM Tele-Gateway SMS Active | Delivered to Handset</div>
          <div className="font-mono text-4xl font-bold tracking-[0.35em] mb-4">8 2 6 0 4 1</div>
          <button className="btn h-10 text-white" style={{ background: '#15803D' }}>Verify Token →</button></div>
        <div className="flex gap-2 justify-center">{[8, 2, 6, 0, 4, 1].map((d, i) => <div key={i} className="w-14 h-14 border border-line rounded-xl grid place-items-center font-mono text-2xl font-bold" style={i === 5 ? { borderColor: '#ea580c' } : {}}>{d}</div>)}</div>
      </Panel>
    </Frame>
  )
}

export function CheckupFrame() {
  return (
    <Frame w={820} path="/doctor/patient/<id>/add-checkup">
      <Panel className="!p-6 mb-5 flex flex-wrap items-center justify-between gap-4">
        <div><div className="text-2xl font-extrabold">Meera Joshi</div><div className="text-sm text-slate2 mt-1"><span className="font-mono">SS-TEST-001</span> · 34 Yrs</div></div>
        <div className="flex gap-2"><span className="pill pill-orange">O+</span><span className="pill pill-red">⚠️ Penicillin Allergy</span></div></Panel>
      <div className="rounded-2xl p-6 mb-5 flex flex-wrap items-center justify-between gap-4" style={{ background: '#F0FDF4', border: '1px solid #BBF7D0' }}>
        <p className="text-sm max-w-[520px]"><b className="text-emerald2">Clinical Summary:</b> Patient presented with seasonal viral symptoms and mild chronic hypertension. Stable vitals.</p>
        <button className="pill pill-green h-9 bg-white">🔊 Listen to Audio Summary</button></div>
      <Panel>
        <div className="flex items-center justify-between bg-peach border border-[#fed7aa] rounded-xl px-5 py-3 mb-8"><span className="text-sm font-semibold text-[#9a3412]">🎙 Voice Dictation Assistant</span><button className="btn btn-saffron h-9">🎙 Dictate</button></div>
        <div className="grid gap-5">
          <F l="Locality" v="Shivajinagar (Ward A)" sel={['Shivajinagar (Ward A)', 'Kothrud', 'Katraj']} />
          <div><F l="Diagnosed Conditions" ph="e.g. Cold, Viral Fever, Bronchitis" v="Flu, Cold & Cough" />
            <div className="flex flex-wrap gap-2 mt-3">{['Cold', 'Fever', 'Cough', 'Dengue', 'Hypertension'].map((c) => <button key={c} className="pill pill-grey h-8 cursor-pointer lift">+ {c}</button>)}</div></div>
          <F l="Doctor Notes" ph="Examination notes, vitals (BP: 120/80 mmHg, Pulse: 72 bpm)…" area />
          <div><div className="label">Prescribed Medicines</div>
            <div className="grid md:grid-cols-3 gap-3"><input className="input" placeholder="e.g. Paracetamol" defaultValue="Paracetamol 650mg" /><input className="input font-mono" placeholder="e.g. 650mg TDS" defaultValue="1 Tab TDS" /><input className="input" placeholder="e.g. After food - 5 days" defaultValue="After food x 5 days" /></div>
            <button className="text-saffron text-sm font-semibold mt-3">+ Add medicine</button></div>
          <label className="flex gap-3 items-start bg-[#fffbeb] border border-[#fde68a] rounded-xl p-4 text-sm text-[#92400e]"><input type="checkbox" className="mt-0.5 w-4 h-4 accent-saffron" />Mark as Refill Restricted (Schedule H Drug — Blocks repeat dispensing without fresh visit)</label>
          <div className="flex justify-end gap-3 pt-2"><button className="btn btn-ghost">Cancel</button><button className="btn btn-saffron">Save Consultation & Issue Prescription</button></div>
        </div>
      </Panel>
    </Frame>
  )
}

export function DispenseFrame() {
  return (
    <Frame w={960} path="/pharmacist/patient/<id>/medicines">
      <div className="rounded-xl border border-[#fed7aa] bg-peach text-[#9a3412] px-5 py-4 text-sm font-medium mb-6">🔒 Privacy Isolation Active: Clinical diagnosis notes and private patient histories are cryptographically hidden from dispensing terminals (DPDP Section 8 Compliant).</div>
      <div className="flex gap-3 mb-6"><input className="input h-12 font-mono" placeholder="e.g. SS-TEST-001" /><button className="btn btn-saffron h-12">Look Up Prescriptions</button></div>
      <Panel className="!p-0 overflow-x-auto mb-6">
        <table className="w-full min-w-[760px]"><thead><tr>{['Card ID', 'Date & Time', 'Medical Condition', 'Medicine & Dosage'].map((h) => <th key={h} className="th">{h}</th>)}</tr></thead><tbody>
          <tr><td className="td"><span className="pill pill-grey font-mono">SS-TEST-001</span></td><td className="td text-slate2">07 Oct 2026, 11:30 AM</td><td className="td">Hypertension & Chronic Headache</td><td className="td font-mono text-[13px]">Amlodipine 5mg OD, Telmisartan 40mg OD</td></tr>
          <tr><td className="td"><span className="pill pill-grey font-mono">SS-TEST-001</span></td><td className="td text-slate2">07 Oct 2026, 11:30 AM</td><td className="td">Acute Insomnia & Anxiety</td><td className="td"><div className="font-mono text-[13px] mb-2">Zolpidem 5mg HS</div><span className="pill pill-red">⛔ Refill Restricted (Schedule X) — Doctor Re-Authorization Required</span></td></tr>
        </tbody></table></Panel>
      <button className="btn h-12 text-white w-full" style={{ background: '#15803D' }}>Dispense Medication & Log Audit Trail</button>
    </Frame>
  )
}

export default function Frames() {
  return (<><div className="max-w-[1200px] mx-auto px-6 pt-10 pb-2"><div className="eyebrow">Design system · 6 frames</div></div>
    <ApplyFrame /><StatusFrame /><LoginFrame /><ScanFrame /><CheckupFrame /><DispenseFrame />
    <div className="py-16 grid place-items-center bg-alabaster"><HealthCard name="Meera Joshi" blood="O+" locality="Shivajinagar" cardId="SS-TEST-001" /></div></>)
}
