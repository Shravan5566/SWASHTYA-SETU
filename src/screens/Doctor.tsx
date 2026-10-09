import { useEffect, useRef, useState } from 'react'
import jsQR from 'jsqr'
import { api, post, useFetch } from '../api'
import { useLang } from '../i18n'
import { Section, State } from '../ui'

function extractCardId(raw: string): string {
  const match = raw.match(/SS-[A-Z0-9]{4,16}/i)
  return match ? match[0].toUpperCase() : raw.trim().toUpperCase()
}

export default function Doctor() {
  const [stage, setStage] = useState<'scan' | 'otp' | 'dash'>('scan')
  const [cardId, setCardId] = useState('')
  const [otpInfo, setOtpInfo] = useState<any>(null)
  const [err, setErr] = useState('')
  const { t } = useLang()

  const request = async (id: string) => {
    setErr('')
    setCardId(id)
    try {
      const info = await post('/api/otp/request', { card_id: id })
      setOtpInfo(info)
      setStage('otp')
    } catch (e: any) {
      setErr(e.message)
    }
  }

  return (
    <Section
      eyebrow="Clinical OPD Suite"
      title="Doctor Consultation & Checkup"
      right={
        <div className="flex items-center gap-2">
          <span className="pill pill-green">
            <span className="dot" />
            OPD Terminal Active
          </span>
          <span className="pill pill-grey font-mono hidden sm:inline-flex">
            Dr. Aisha Verma (SMO)
          </span>
        </div>
      }
    >
      {stage === 'scan' && <Scan onCard={request} err={err} />}
      {stage === 'otp' && (
        <Otp
          cardId={cardId}
          info={otpInfo}
          onOk={() => setStage('dash')}
          onCancel={() => setStage('scan')}
          resend={() => request(cardId)}
        />
      )}
      {stage === 'dash' && <Dashboard cardId={cardId} onClose={() => setStage('scan')} t={t} />}
    </Section>
  )
}

function Scan({ onCard, err }: { onCard: (id: string) => void; err: string }) {
  const { t } = useLang()
  const quick = useFetch<{ name: string; card_id: string; locality?: string; blood_group?: string }[]>(
    '/api/quick-patients'
  )
  const video = useRef<HTMLVideoElement>(null)
  const [manual, setManual] = useState('')
  const [cam, setCam] = useState('')

  useEffect(() => {
    let stream: MediaStream | undefined
    let raf = 0
    let stopped = false
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d', { willReadFrequently: true })

    if (navigator.mediaDevices?.getUserMedia) {
      navigator.mediaDevices
        .getUserMedia({ video: { facingMode: 'environment' } })
        .then((s) => {
          stream = s
          if (video.current) {
            video.current.srcObject = s
            video.current.play().catch(() => {})
          }
          const tick = () => {
            if (stopped) return
            if (video.current && video.current.readyState >= 2) {
              const vw = video.current.videoWidth || 640
              const vh = video.current.videoHeight || 480
              canvas.width = vw
              canvas.height = vh
              ctx?.drawImage(video.current, 0, 0, vw, vh)
              const imgData = ctx?.getImageData(0, 0, vw, vh)
              if (imgData) {
                const code = jsQR(imgData.data, imgData.width, imgData.height, {
                  inversionAttempts: 'dontInvert',
                })
                if (code && code.data) {
                  return onCard(extractCardId(code.data))
                }
              }
            }
            raf = requestAnimationFrame(tick)
          }
          tick()
        })
        .catch(() => {
          setCam('Camera viewfinder in preview mode. Click a registered patient below or enter Card ID.')
        })
    }

    return () => {
      stopped = true
      cancelAnimationFrame(raf)
      stream?.getTracks().forEach((x) => x.stop())
    }
  }, [onCard])

  const upload = async (file?: File) => {
    if (!file) return
    const img = new Image()
    img.onload = () => {
      const canvas = document.createElement('canvas')
      canvas.width = img.width
      canvas.height = img.height
      const ctx = canvas.getContext('2d')
      ctx?.drawImage(img, 0, 0)
      const imgData = ctx?.getImageData(0, 0, canvas.width, canvas.height)
      if (imgData) {
        const code = jsQR(imgData.data, imgData.width, imgData.height)
        if (code && code.data) {
          onCard(extractCardId(code.data))
        } else {
          setCam('No legible QR code found in uploaded image. Please enter Card ID.')
        }
      }
    }
    img.onerror = () => setCam('Failed to process uploaded image.')
    img.src = URL.createObjectURL(file)
  }


  return (
    <div className="grid gap-8 max-w-[800px] mx-auto">
      {/* Quick patient shortcuts for instant demonstration */}
      {(quick.data?.length ?? 0) > 0 && (
        <div className="card p-5 bg-gradient-to-r from-orange-50/50 to-emerald-50/50 border-orange-200/60">
          <div className="eyebrow mb-2.5 text-slate-700 flex items-center justify-between">
            <span>Fast-Select Registered Patients</span>
            <span className="text-[10px] font-mono font-normal">Click to test check-in flow</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {quick.data!.map((p) => (
              <button
                key={p.card_id}
                type="button"
                className="btn btn-ghost h-9 px-3.5 text-xs bg-white hover:border-orange-300 hover:text-orange-700"
                onClick={() => onCard(p.card_id)}
              >
                <span className="text-orange-600 font-bold">⚡</span>
                <span className="font-semibold">{p.name}</span>
                <span className="font-mono text-slate-400">({p.card_id})</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Camera scanner & Manual entry card */}
      <div className="card p-6 md:p-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2.5">
            <img src="/sslogo-symbol.png" alt="Swasthya Setu" className="w-6 h-6 object-contain" />
            <h2 className="text-lg font-bold text-ink">Scan Citizen QR Health Card</h2>
          </div>
          <span className="text-xs font-mono text-slate-400">Scanner Viewport</span>
        </div>

        <div className="relative aspect-[16/10] bg-slate-950 rounded-2xl overflow-hidden shadow-inner flex items-center justify-center">
          <video
            ref={video}
            muted
            playsInline
            className="absolute inset-0 w-full h-full object-cover opacity-85"
          />
          {/* Target Reticle */}
          <div className="absolute inset-[15%] pointer-events-none border-2 border-emerald-500/40 rounded-2xl">
            {/* Viewfinder Corners */}
            <span className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-emerald-400 rounded-tl-xl" />
            <span className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-emerald-400 rounded-tr-xl" />
            <span className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-emerald-400 rounded-bl-xl" />
            <span className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-emerald-400 rounded-br-xl" />
            {/* Sweeping laser line */}
            <span
              className="absolute left-2 right-2 h-0.5 bg-emerald-400/90 shadow-[0_0_12px_#10b981]"
              style={{ animation: 'scan 2.4s ease-in-out infinite' }}
            />
          </div>
        </div>

        {cam && (
          <p className="text-xs text-slate-500 mt-3 bg-slate-50 p-2.5 rounded-lg border border-slate-200">
            ℹ️ {cam}
          </p>
        )}

        {/* Manual Input & File Upload */}
        <div className="flex flex-wrap gap-3 mt-6 pt-5 border-t border-slate-100">
          <label className="btn btn-ghost h-11 text-xs font-semibold cursor-pointer">
            📁 {t('scan.upload', 'Upload QR Card Image')}
            <input
              type="file"
              accept="image/*"
              hidden
              onChange={(e) => upload(e.target.files?.[0])}
            />
          </label>

          <div className="flex gap-2 flex-1 min-w-[260px]">
            <input
              className="input font-mono font-bold tracking-wider uppercase text-sm h-11"
              placeholder="e.g. SS-A8F392B1"
              value={manual}
              onChange={(e) => setManual(e.target.value.toUpperCase())}
              onKeyDown={(e) => e.key === 'Enter' && manual && onCard(manual)}
            />
            <button
              className="btn btn-saffron h-11 px-5"
              disabled={!manual.trim()}
              onClick={() => onCard(manual.trim())}
            >
              {t('scan.verify', 'Verify Card')} →
            </button>
          </div>
        </div>

        {err && (
          <div className="mt-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-medium flex items-center gap-2">
            <span>⚠️</span>
            <span>{err}</span>
          </div>
        )}
      </div>
    </div>
  )
}

function Otp({
  cardId,
  info,
  onOk,
  onCancel,
  resend,
}: {
  cardId: string
  info: any
  onOk: () => void
  onCancel: () => void
  resend: () => void
}) {
  const { t } = useLang()
  const [digits, setDigits] = useState(['', '', '', '', '', ''])
  const [left, setLeft] = useState<number>(info?.expires_in ?? 300)
  const [err, setErr] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const refs = useRef<(HTMLInputElement | null)[]>([])

  useEffect(() => {
    setLeft(info?.expires_in ?? 300)
  }, [info])

  useEffect(() => {
    const i = setInterval(() => setLeft((s) => Math.max(0, s - 1)), 1000)
    return () => clearInterval(i)
  }, [])

  const code = digits.join('')

  const verify = async () => {
    if (code.length < 6) return
    setErr('')
    setSubmitting(true)
    try {
      await post('/api/otp/verify', { card_id: cardId, otp: code })
      onOk()
    } catch (e: any) {
      setErr(e.message)
    } finally {
      setSubmitting(false)
    }
  }

  const type = (i: number, v: string) => {
    v = v.replace(/\D/g, '').slice(-1)
    setDigits((s) => s.map((x, j) => (j === i ? v : x)))
    if (v && i < 5) refs.current[i + 1]?.focus()
  }

  const autofillDemo = () => {
    const demoCode = info?.demo_otp || '123456'
    setDigits(demoCode.split('').slice(0, 6))
  }

  return (
    <div className="card p-8 md:p-10 max-w-[540px] mx-auto shadow-md">
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-xl font-extrabold text-ink">{t('otp.title', 'Citizen Consent Gate')}</h2>
        <span className="pill pill-grey font-mono text-xs font-bold">{cardId}</span>
      </div>

      <p className="text-xs text-slate-500 mb-4 leading-relaxed">
        Under DPDP Act 2023, patient medical dossiers require active real-time verification before
        practitioners can access clinical records.
      </p>

      <div className="flex flex-wrap items-center gap-2 my-2">
        <span className="pill pill-green">
          <span className="dot" />
          OTP sent to {info?.phone_masked || 'registered contact'}
        </span>
        {info?.demo_otp && (
          <button
            type="button"
            onClick={autofillDemo}
            className="pill pill-orange cursor-pointer hover:bg-orange-100"
            title="Click to autofill test code"
          >
            ⚡ Test Code: {info.demo_otp} (Click to fill)
          </button>
        )}
      </div>

      {/* 6 Digits Container */}
      <div
        className="flex gap-2.5 my-6 justify-between"
        onPaste={(e) => {
          const p = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
          if (p) {
            e.preventDefault()
            setDigits([...p.padEnd(6, ' ').split('').map((c) => c.trim())])
          }
        }}
      >
        {digits.map((v, i) => (
          <input
            key={i}
            ref={(el) => {
              refs.current[i] = el
            }}
            value={v}
            inputMode="numeric"
            maxLength={1}
            aria-label={`Digit ${i + 1}`}
            onChange={(e) => type(i, e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Backspace' && !v && i > 0) {
                refs.current[i - 1]?.focus()
              } else if (e.key === 'Enter' && code.length === 6) {
                verify()
              }
            }}
            className="font-mono text-2xl font-bold text-center w-full aspect-square max-w-[64px] bg-slate-50 border border-slate-200 rounded-xl focus:border-orange-500 focus:bg-white focus:shadow-md outline-none transition-all"
          />
        ))}
      </div>

      <div className="flex items-center justify-between text-xs text-slate-500 mb-6">
        <span className="font-mono font-semibold">
          ⏱️ Expires in {String(Math.floor(left / 60)).padStart(2, '0')}:
          {String(left % 60).padStart(2, '0')}
        </span>
        <button
          type="button"
          className="font-semibold text-saffron hover:underline disabled:opacity-40"
          disabled={left > 240}
          onClick={resend}
        >
          Resend OTP
        </button>
      </div>

      {err && (
        <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-medium">
          ⚠️ {err}
        </div>
      )}

      <div className="flex gap-3">
        <button type="button" className="btn btn-ghost px-5" onClick={onCancel}>
          Cancel
        </button>
        <button
          type="button"
          className="btn btn-saffron flex-1"
          disabled={code.length < 6 || left === 0 || submitting}
          onClick={verify}
        >
          {submitting ? 'Verifying…' : `${t('otp.verify', 'Verify Citizen OTP')} →`}
        </button>
      </div>
    </div>
  )
}

function Dashboard({
  cardId,
  onClose,
  t,
}: {
  cardId: string
  onClose: () => void
  t: any
}) {
  const { lang } = useLang()
  const p = useFetch<any>(`/api/patients/${cardId}`)
  const sum = useFetch<{ bullets: { date?: string; text: string }[]; audio_url?: string }>(
    `/api/patients/${cardId}/summary`
  )
  const hist = useFetch<any[]>(`/api/patients/${cardId}/records`)

  const [cond, setCond] = useState('')
  const [notes, setNotes] = useState('')
  const [q, setQ] = useState('')
  const [opts, setOpts] = useState<any[]>([])
  const [meds, setMeds] = useState<string[]>([])
  const [dosage, setDosage] = useState('1 tab twice daily')
  const [restricted, setRestricted] = useState(false)
  const [conflicts, setConflicts] = useState<any[]>([])
  const [rec, setRec] = useState(false)
  const [msg, setMsg] = useState('')
  const [saving, setSaving] = useState(false)
  const [playingAudio, setPlayingAudio] = useState(false)

  // Formulary autocomplete
  useEffect(() => {
    if (q.length < 2) return setOpts([])
    const h = setTimeout(() => {
      api(`/api/formulary?q=${encodeURIComponent(q)}`)
        .then(setOpts)
        .catch(() => setOpts([]))
    }, 180)
    return () => clearTimeout(h)
  }, [q])

  // Conflict & allergy detector
  useEffect(() => {
    if (!meds.length) return setConflicts([])
    post('/api/interactions/check', { card_id: cardId, medicines: meds })
      .then((r) => setConflicts(r.conflicts ?? []))
      .catch(() => {})
  }, [cardId, meds])

  const listen = () => {
    if (sum.data?.audio_url) {
      const a = new Audio(sum.data.audio_url)
      setPlayingAudio(true)
      a.onended = () => setPlayingAudio(false)
      return a.play()
    }
    const textToSpeak = (sum.data?.bullets ?? []).map((b) => b.text).join('. ')
    if (!textToSpeak) return
    const u = new SpeechSynthesisUtterance(textToSpeak)
    u.lang = lang === 'mr' ? 'mr-IN' : 'en-IN'
    u.onstart = () => setPlayingAudio(true)
    u.onend = () => setPlayingAudio(false)
    speechSynthesis.speak(u)
  }

  const dictate = () => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) return setMsg('Browser does not support speech recognition. Type notes manually.')
    const r = new SR()
    r.lang = lang === 'mr' ? 'mr-IN' : 'en-IN'
    r.onstart = () => setRec(true)
    r.onend = () => setRec(false)
    r.onresult = (e: any) => {
      const transcript = e.results[0][0].transcript
      setNotes((n) => (n ? `${n} ${transcript}` : transcript).trim())
    }
    r.start()
  }

  const save = async () => {
    if (!cond.trim()) return
    setSaving(true)
    setMsg('')
    try {
      await post(`/api/patients/${cardId}/records`, {
        condition: cond.trim(),
        medicines: meds,
        notes: notes.trim(),
        dosage: dosage.trim(),
        refill_restricted: restricted,
      })
      setMsg('Checkup record and prescription committed to registry.')
      setCond('')
      setNotes('')
      setMeds([])
      setRestricted(false)
      hist.reload()
      sum.reload()
    } catch (e: any) {
      setMsg(e.message)
    } finally {
      setSaving(false)
    }
  }

  if (p.loading || p.error) {
    return (
      <div className="card max-w-[800px] mx-auto">
        <State loading={p.loading} error={p.error} onRetry={p.reload} />
      </div>
    )
  }

  const allergies: string[] = Array.isArray(p.data?.allergies)
    ? p.data.allergies
    : p.data?.allergies
    ? String(p.data.allergies).split(',')
    : []

  return (
    <div className="grid gap-6 animate-in fade-in duration-200">
      {/* Patient Dossier Top Bar */}
      <div className="card p-6 flex flex-wrap items-center gap-4 justify-between bg-gradient-to-r from-slate-50 to-white">
        <div className="flex items-center gap-4">
          <div className="p-2 bg-white rounded-xl border border-slate-200 shadow-2xs shrink-0">
            <img src="/sslogo-symbol.png" alt="Swasthya Setu" className="w-9 h-9 object-contain" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-2xl font-extrabold text-ink">{p.data?.name}</h2>
              {p.data?.blood_group && (
                <span className="pill pill-orange font-bold text-xs">
                  🩸 {p.data.blood_group}
                </span>
              )}
            </div>
            <div className="flex items-center gap-3 font-mono text-xs text-slate-500 mt-1">
              <span className="font-bold text-ink">{cardId}</span>
              <span>•</span>
              <span>Locality: {p.data?.locality || 'Pune'}</span>
              <span>•</span>
              <span>Visits: {p.data?.visits_count ?? 0}</span>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 items-center">
          {allergies.map((a) => (
            <span key={a} className="pill pill-red font-bold text-xs">
              ⚠️ Allergy: {a.trim()}
            </span>
          ))}
          <button
            type="button"
            className="btn btn-ghost h-9 px-4 text-xs font-semibold"
            onClick={onClose}
          >
            Exit Patient Dossier ✕
          </button>
        </div>
      </div>

      {/* Main OPD Grid: Left Clinical AI & History, Right Checkup Entry */}
      <div className="grid lg:grid-cols-2 gap-6 items-start">
        {/* Left Column */}
        <div className="grid gap-6">
          {/* Clinical History Summary */}
          <div className="card p-6 bg-gradient-to-br from-emerald-50/70 via-white to-emerald-50/30 border-emerald-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <span className="text-emerald-700 font-bold text-base">📋</span>
                <h3 className="font-extrabold text-emerald-900 text-base">
                  Clinical History Summary
                </h3>
              </div>
              <button
                type="button"
                className={`pill pill-green h-8 bg-white cursor-pointer hover:bg-emerald-100 ${
                  playingAudio ? 'ring-2 ring-emerald-500' : ''
                }`}
                onClick={listen}
              >
                {playingAudio ? '🔊 Playing…' : `🔊 ${t('listen', 'Listen to Summary')}`}
              </button>
            </div>

            <State
              loading={sum.loading}
              error={sum.error}
              empty={!sum.data?.bullets?.length}
              emptyText="No previous visits to summarise."
            />

            <ul className="grid gap-3">
              {sum.data?.bullets?.map((b, i) => (
                <li
                  key={i}
                  className="flex gap-3 text-sm text-slate-700 bg-white/80 p-3 rounded-xl border border-emerald-100 shadow-xs"
                >
                  <span className="mt-1.5 w-2 h-2 rounded-full bg-emerald-600 shrink-0" />
                  <div>
                    {b.date && (
                      <span className="font-mono text-xs font-semibold text-slate-500 block mb-0.5">
                        {b.date}
                      </span>
                    )}
                    <span className="leading-relaxed">{b.text}</span>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          {/* Historical Visits Timeline */}
          <div className="card p-6">
            <div className="flex items-center justify-between mb-5">
              <h3 className="font-bold text-ink">Clinical Visit History</h3>
              <span className="text-xs text-slate-400 font-mono">Chronological</span>
            </div>

            <State
              loading={hist.loading}
              error={hist.error}
              empty={!hist.data?.length}
              emptyText="No prior visits recorded for this health card."
            />

            <ol className="grid gap-5 border-l-2 border-slate-200 ml-2 pl-5 relative">
              {hist.data?.map((h, i) => (
                <li key={i} className="relative group">
                  <span className="absolute -left-[27px] top-1 w-3 h-3 rounded-full bg-orange-500 border-2 border-white shadow-xs" />
                  <div className="font-mono text-[11px] text-slate-400 font-semibold mb-1">
                    {h.date} • {h.doctor}
                  </div>
                  <div className="font-bold text-sm text-ink mb-1">{h.condition}</div>
                  {h.notes && (
                    <p className="text-xs text-slate-600 italic bg-slate-50 p-2 rounded-lg mb-2">
                      "{h.notes}"
                    </p>
                  )}
                  <div className="flex flex-wrap gap-1.5 items-center">
                    {(h.medicines ?? []).map((m: string, mi: number) => (
                      <span key={mi} className="pill pill-grey text-[11px] font-mono">
                        💊 {m}
                      </span>
                    ))}
                    {h.dosage && (
                      <span className="text-[11px] text-slate-500 font-medium">({h.dosage})</span>
                    )}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>

        {/* Right Column: Checkup Entry Form */}
        <div className="card p-6 md:p-7 grid gap-5 shadow-sm">
          <div className="flex items-center justify-between pb-3 border-b border-slate-100">
            <div>
              <h3 className="font-extrabold text-ink text-base">New Checkup Record</h3>
              <p className="text-xs text-slate-400">Commit diagnosis & prescriptions</p>
            </div>
            <span className="pill pill-amber text-xs font-semibold">
              🔒 {t('lock', 'Locked after 24 hrs')}
            </span>
          </div>

          {/* Condition */}
          <div>
            <label className="label">Primary Clinical Diagnosis / Condition *</label>
            <input
              className="input font-medium"
              placeholder="e.g. Acute Bronchitis, Type 2 Diabetes, Viral Fever"
              value={cond}
              onChange={(e) => setCond(e.target.value)}
            />
          </div>

          {/* Clinical Notes & Voice Dictation */}
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label className="label mb-0">Confidential Examination Notes</label>
              <button
                type="button"
                className={`btn h-8 px-3 text-xs ${rec ? 'btn-saffron' : 'btn-peach'}`}
                onClick={dictate}
              >
                {rec ? (
                  <span className="flex items-end gap-1 h-3.5">
                    {[0, 1, 2, 3, 4].map((i) => (
                      <i
                        key={i}
                        className="w-0.5 h-3.5 bg-white origin-bottom"
                        style={{ animation: `wave .7s ${i * 0.12}s infinite` }}
                      />
                    ))}
                  </span>
                ) : (
                  '🎙️'
                )}
                <span>{rec ? 'Recording Voice…' : t('dictate', 'Dictate')}</span>
              </button>
            </div>
            <textarea
              className="input h-24 py-2.5 text-sm resize-none"
              placeholder="Patient symptoms, vital observations, clinical rationale…"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
            />
          </div>

          {/* Formulary Search & Prescription */}
          <div className="relative">
            <label className="label">Prescribed Medicines (Standard Formulary Auto-complete)</label>
            <input
              className="input"
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search catalog: Paracetamol, Amoxicillin, Metformin…"
            />

            {opts.length > 0 && (
              <ul className="absolute z-20 left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden max-h-48 overflow-y-auto">
                {opts.map((o) => {
                  const name = o.name ?? o
                  return (
                    <li key={name}>
                      <button
                        type="button"
                        className="w-full text-left px-4 py-2.5 text-sm hover:bg-emerald-50 hover:text-emerald-900 border-b border-slate-100 last:border-none flex items-center justify-between"
                        onClick={() => {
                          setMeds((m) => [...new Set([...m, name])])
                          setQ('')
                          setOpts([])
                        }}
                      >
                        <span className="font-semibold">{name}</span>
                        <span className="text-xs text-emerald-600 font-bold">+ Add</span>
                      </button>
                    </li>
                  )
                })}
              </ul>
            )}

            {/* Selected Medicines Pills */}
            <div className="flex flex-wrap gap-2 mt-3">
              {meds.map((m) => (
                <button
                  key={m}
                  type="button"
                  className="pill pill-green font-mono cursor-pointer hover:bg-red-50 hover:border-red-300 hover:text-red-700"
                  onClick={() => setMeds(meds.filter((x) => x !== m))}
                  title="Click to remove"
                >
                  💊 {m} <span className="ml-1 font-bold">✕</span>
                </button>
              ))}
              {!meds.length && (
                <span className="text-xs text-slate-400 italic">No medications prescribed yet.</span>
              )}
            </div>
          </div>

          {/* Dosage & Refill restriction */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="label">Dosage Instructions</label>
              <input
                className="input text-sm"
                value={dosage}
                onChange={(e) => setDosage(e.target.value)}
                placeholder="e.g. 1 tab after meals x 5 days"
              />
            </div>
            <div className="flex flex-col justify-end">
              <label className="flex items-center gap-2.5 p-3 rounded-xl border border-slate-200 bg-slate-50 cursor-pointer text-xs font-semibold select-none">
                <input
                  type="checkbox"
                  checked={restricted}
                  onChange={(e) => setRestricted(e.target.checked)}
                  className="w-4 h-4 accent-orange-600"
                />
                <span>Schedule H / Refill Restricted</span>
              </label>
            </div>
          </div>

          {/* Conflict warnings */}
          {conflicts.map((c, i) => (
            <div
              key={i}
              className="p-3 rounded-xl bg-red-50 border border-red-300 text-red-900 text-xs font-semibold leading-relaxed flex items-start gap-2"
            >
              <span>⚠️</span>
              <span>{c.message ?? `${c.a} + ${c.b}`}</span>
            </div>
          ))}

          {msg && (
            <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-medium">
              ✓ {msg}
            </div>
          )}

          <button
            type="button"
            className="btn btn-saffron h-12 w-full mt-2 font-bold"
            disabled={!cond.trim() || saving}
            onClick={save}
          >
            {saving ? 'Committed to Registry…' : 'Save & Lock Clinical Record →'}
          </button>
        </div>
      </div>
    </div>
  )
}
