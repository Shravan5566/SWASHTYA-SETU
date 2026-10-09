import { useState } from 'react'
import { post, useFetch } from '../api'
import { useLang } from '../i18n'
import { HealthCard, Section } from '../ui'

const BLOOD = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

export default function Apply() {
  const { t } = useLang()
  const localities = useFetch<{ name: string }[] | string[]>('/api/localities')
  const [step, setStep] = useState(0)
  const [f, setF] = useState({
    name: '',
    phone: '',
    dob: '',
    locality: 'Shivajinagar',
    blood_group: 'O+',
    allergies: '',
    chronic_conditions: '',
  })
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [card, setCard] = useState<any>(null)

  const set = (k: string, v: string) => setF((s) => ({ ...s, [k]: v }))
  const steps = [t('step.1', 'Identity'), t('step.2', 'Health & Ward'), t('step.3', 'Review & Issue')]

  // Clean locality list
  const localityList: string[] = Array.isArray(localities.data)
    ? (localities.data as any[]).map((l) => (typeof l === 'string' ? l : l.name))
    : [
        'Shivajinagar',
        'Kothrud',
        'Katraj',
        'Hadapsar',
        'Viman Nagar',
        'Baner',
        'Aundh',
        'Swargate',
        'Pimpri',
        'Chinchwad',
      ]

  const submit = async () => {
    setBusy(true)
    setErr('')
    try {
      const res = await post('/api/applications', {
        name: f.name.trim(),
        phone: f.phone.trim(),
        dob: f.dob,
        locality: f.locality,
        blood_group: f.blood_group,
        allergies: f.allergies.trim(),
        chronic_conditions: f.chronic_conditions.trim(),
      })
      setCard(res)
    } catch (e: any) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  if (card) {
    const approved = card.status === 'approved' || card.card_id
    return (
      <Section
        eyebrow="Citizen Health Card Issued"
        title={approved ? 'Your Digital Health Card' : 'Application Received'}
      >
        <div className="grid lg:grid-cols-2 gap-10 items-start max-w-[1040px] mx-auto animate-in fade-in duration-200">
          <div className="card p-8 flex justify-center bg-gradient-to-b from-slate-50/60 to-white shadow-md">
            <HealthCard
              name={card.name ?? f.name}
              blood={card.blood_group ?? f.blood_group}
              locality={card.locality ?? f.locality}
              cardId={card.card_id}
              helpline={card.helpline}
            />
          </div>

          <div className="card p-8 flex flex-col justify-between h-full bg-white">
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="pill pill-green font-bold text-xs">
                  ✓ {approved ? 'Card Issued & Active' : 'Under Review'}
                </span>
                {card.reference && (
                  <span className="pill pill-grey font-mono text-xs">
                    Ref: {card.reference}
                  </span>
                )}
              </div>

              <h3 className="text-2xl font-extrabold text-ink mb-2">
                {card.name ?? f.name}
              </h3>

              <p className="text-slate-600 text-sm leading-relaxed mb-6">
                Your Swasthya Setu digital health identity has been generated with end-to-end
                cryptographic isolation. Show this QR card at participating healthcare centers and clinics for
                instant one-touch check-in.
              </p>

              <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 text-xs text-slate-600 grid gap-1.5 mb-6">
                <div>
                  <span className="font-bold text-ink">Beneficiary Card ID: </span>
                  <span className="font-mono">{card.card_id}</span>
                </div>
                <div>
                  <span className="font-bold text-ink">Ward / Locality: </span>
                  <span>{card.locality ?? f.locality}</span>
                </div>
                <div>
                  <span className="font-bold text-ink">Registered Phone: </span>
                  <span>{f.phone}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                className="btn btn-saffron h-12 px-6 flex-1 text-sm font-bold"
                onClick={() => window.print()}
              >
                🖨️ {t('save', 'Print / Save Health Card')}
              </button>
              <button
                type="button"
                className="btn btn-ghost h-12 px-5 text-sm"
                onClick={() => {
                  setCard(null)
                  setStep(0)
                  setF({
                    name: '',
                    phone: '',
                    dob: '',
                    locality: 'Shivajinagar',
                    blood_group: 'O+',
                    allergies: '',
                    chronic_conditions: '',
                  })
                }}
              >
                Enroll Another Citizen
              </button>
            </div>
          </div>
        </div>
      </Section>
    )
  }

  const ok = [
    f.name.trim().length >= 3 && f.phone.trim().length >= 10,
    f.locality && f.blood_group,
    true,
  ][step]

  return (
    <Section
      eyebrow="Citizen Health Enrollment"
      title={t('nav.apply', 'Apply for Digital Health Card')}
      right={
        <span className="pill pill-green hidden sm:inline-flex">
          <span className="dot" />
          Instant Issuance Available
        </span>
      }
    >
      <div className="max-w-[680px] mx-auto">
        {/* Progress Stepper */}
        <div className="flex gap-3 mb-8">
          {steps.map((s, i) => (
            <div key={s} className="flex-1">
              <div
                className="h-1.5 rounded-full transition-all duration-300"
                style={{
                  background:
                    i < step ? '#059669' : i === step ? '#ea580c' : '#e2e8f0',
                }}
              />
              <div
                className={`mt-2 text-xs font-semibold ${
                  i === step ? 'text-ink font-bold' : 'text-slate-400'
                }`}
              >
                {i + 1}. {s}
              </div>
            </div>
          ))}
        </div>

        <div className="card p-7 md:p-9 shadow-sm bg-white">
          {step === 0 && (
            <div className="grid gap-5">
              <div>
                <label className="label" htmlFor="name">
                  {t('f.name', 'Full Legal Name (as per Govt ID)')} *
                </label>
                <input
                  id="name"
                  className="input"
                  placeholder="e.g. Ramesh Shankar Kulkarni"
                  value={f.name}
                  onChange={(e) => set('name', e.target.value)}
                />
              </div>

              <div>
                <label className="label" htmlFor="phone">
                  {t('f.phone', 'Mobile Phone Number (for OTP Consent)')} *
                </label>
                <input
                  id="phone"
                  className="input font-mono"
                  inputMode="tel"
                  placeholder="10-digit mobile number (e.g. 9822012345)"
                  value={f.phone}
                  onChange={(e) => set('phone', e.target.value)}
                />
              </div>

              <div>
                <label className="label" htmlFor="dob">
                  {t('f.dob', 'Date of Birth')}
                </label>
                <input
                  id="dob"
                  type="date"
                  className="input"
                  value={f.dob}
                  onChange={(e) => set('dob', e.target.value)}
                />
              </div>
            </div>
          )}

          {step === 1 && (
            <div className="grid gap-5">
              <div>
                <label className="label">
                  {t('f.locality', 'Pune Locality / Ward')} *
                </label>
                <select
                  className="input"
                  value={f.locality}
                  onChange={(e) => set('locality', e.target.value)}
                >
                  {localityList.map((loc) => (
                    <option key={loc} value={loc}>
                      {loc}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="label">{t('f.blood', 'Blood Group')} *</label>
                <div className="grid grid-cols-4 gap-2">
                  {BLOOD.map((b) => (
                    <button
                      key={b}
                      type="button"
                      className={`btn h-11 text-xs font-bold border ${
                        f.blood_group === b
                          ? 'bg-orange-500 text-white border-orange-600 shadow-sm'
                          : 'btn-ghost'
                      }`}
                      onClick={() => set('blood_group', b)}
                    >
                      {b}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="label">Known Drug Allergies (Optional)</label>
                <input
                  className="input"
                  placeholder="e.g. Penicillin, Sulfa drugs, Paracetamol"
                  value={f.allergies}
                  onChange={(e) => set('allergies', e.target.value)}
                />
              </div>

              <div>
                <label className="label">Chronic Health Conditions (Optional)</label>
                <input
                  className="input"
                  placeholder="e.g. Hypertension, Type 2 Diabetes, Asthma"
                  value={f.chronic_conditions}
                  onChange={(e) => set('chronic_conditions', e.target.value)}
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="grid gap-5">
              <div className="flex justify-center p-4 bg-gradient-to-b from-slate-50/80 to-white rounded-2xl border border-slate-200/90 shadow-xs">
                <HealthCard
                  name={f.name || 'Citizen Beneficiary'}
                  blood={f.blood_group}
                  locality={f.locality}
                  cardId="SS-PREVIEW-2026"
                />
              </div>

              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 leading-relaxed grid gap-2">
                <div className="font-bold text-sm text-ink mb-1">
                  Confirm Application Details:
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Legal Name:</span>
                  <span className="font-semibold text-ink">{f.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Phone:</span>
                  <span className="font-mono font-semibold text-ink">{f.phone}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Locality:</span>
                  <span className="font-semibold text-ink">{f.locality}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Blood Group:</span>
                  <span className="font-bold text-orange-600">{f.blood_group}</span>
                </div>
                {f.allergies && (
                  <div className="flex justify-between">
                    <span className="text-slate-500">Allergies:</span>
                    <span className="font-semibold text-red-700">{f.allergies}</span>
                  </div>
                )}
              </div>

              <label className="flex gap-3 items-start p-4 rounded-xl bg-emerald-50/70 border border-emerald-200 text-xs text-emerald-900 cursor-pointer select-none">
                <input
                  type="checkbox"
                  defaultChecked
                  className="mt-0.5 w-4 h-4 accent-emerald-700"
                />
                <span>
                  I declare that the information submitted is accurate and consent to the creation of a
                  Swasthya Setu Health Identity under the Digital Personal Data Protection Act 2023.
                </span>
              </label>
            </div>
          )}

          {err && (
            <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-semibold">
              ⚠️ {err}
            </div>
          )}

          <div className="flex justify-between gap-3 mt-8 pt-5 border-t border-slate-100">
            {step > 0 ? (
              <button
                type="button"
                className="btn btn-ghost px-5"
                onClick={() => setStep((s) => s - 1)}
              >
                ← {t('back', 'Back')}
              </button>
            ) : (
              <div />
            )}

            {step < 2 ? (
              <button
                type="button"
                className="btn btn-saffron px-6"
                disabled={!ok}
                onClick={() => setStep((s) => s + 1)}
              >
                {t('next', 'Next Step')} →
              </button>
            ) : (
              <button
                type="button"
                className="btn btn-saffron px-7 font-bold"
                disabled={busy}
                onClick={submit}
              >
                {busy ? 'Issuing Card…' : `✓ ${t('submit', 'Issue Digital Health Card')}`}
              </button>
            )}
          </div>
        </div>
      </div>
    </Section>
  )
}

export function Track() {
  const { t } = useLang()
  const [ref, setRef] = useState('')
  const [res, setRes] = useState<any>(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const check = async (searchVal?: string) => {
    const query = (searchVal || ref).trim()
    if (!query) return
    setErr('')
    setRes(null)
    setBusy(true)
    try {
      const data = await api(`/api/applications/${encodeURIComponent(query)}`)
      setRes(data)
    } catch (e: any) {
      setErr(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <Section
      eyebrow="Citizen Status Portal"
      title={t('nav.track', 'Track Application Status')}
      right={
        <span className="pill pill-grey font-mono text-xs">
          Real-Time Lookup
        </span>
      }
    >
      <div className="max-w-[680px] mx-auto">
        <div className="card p-7 md:p-8 shadow-sm bg-white mb-8">
          <label className="label">
            Enter Application Reference No., Card ID, or Registered Phone
          </label>
          <div className="flex gap-2">
            <input
              className="input font-mono uppercase text-sm"
              placeholder="e.g. APP-PAT-2026-..., SS-A8F392B1, or 9822012345"
              value={ref}
              onChange={(e) => setRef(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && check()}
            />
            <button
              type="button"
              className="btn btn-saffron px-6"
              disabled={!ref.trim() || busy}
              onClick={() => check()}
            >
              {busy ? 'Searching…' : 'Track Status →'}
            </button>
          </div>

          {/* Quick Demo Reference Pill */}
          <div className="mt-3 flex items-center gap-2 text-xs text-slate-500">
            <span>Fast test:</span>
            <button
              type="button"
              className="pill pill-orange cursor-pointer hover:bg-orange-100"
              onClick={() => {
                setRef('SS-A8F392B1')
                check('SS-A8F392B1')
              }}
            >
              ⚡ SS-A8F392B1 (Click to query)
            </button>
          </div>

          {err && (
            <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-semibold">
              ⚠️ {err}
            </div>
          )}
        </div>

        {/* Results Card */}
        {res && (
          <div className="card p-7 md:p-8 bg-white border-slate-200 shadow-md animate-in fade-in duration-200">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100 mb-6">
              <div>
                <span className="pill pill-green font-bold text-xs mb-1.5">
                  ✓ {res.status ? res.status.toUpperCase() : 'ACTIVE'}
                </span>
                <h3 className="text-xl font-extrabold text-ink">{res.name || res.full_name}</h3>
              </div>
              <span className="font-mono text-xs font-bold text-slate-400">
                {res.card_id || res.reference}
              </span>
            </div>

            <div className="grid sm:grid-cols-2 gap-4 text-xs mb-8">
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block mb-0.5">Locality / Ward</span>
                <span className="font-bold text-ink text-sm">{res.locality || 'Pune'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block mb-0.5">Blood Group</span>
                <span className="font-bold text-orange-600 text-sm">
                  {res.blood_group || '—'}
                </span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block mb-0.5">Enrolled Date</span>
                <span className="font-bold text-ink text-sm">{res.created_at || 'Recent'}</span>
              </div>
              <div className="p-3 bg-slate-50 rounded-xl">
                <span className="text-slate-400 block mb-0.5">Emergency Helpline</span>
                <span className="font-mono font-bold text-emerald-700 text-sm">108</span>
              </div>
            </div>

            {/* Display Health Card if issued */}
            {(res.card_id || res.status === 'approved') && (
              <div className="flex flex-col items-center gap-4 pt-4 border-t border-slate-100">
                <HealthCard
                  name={res.name || res.full_name}
                  blood={res.blood_group}
                  locality={res.locality}
                  cardId={res.card_id}
                />
                <button
                  type="button"
                  className="btn btn-saffron h-11 px-6 text-xs font-bold"
                  onClick={() => window.print()}
                >
                  🖨️ Print / Download Health Card
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </Section>
  )
}
