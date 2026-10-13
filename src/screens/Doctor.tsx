import { useEffect, useRef, useState } from 'react'
import {
  LayoutDashboard,
  Sparkles,
  History,
  Stethoscope,
  ShieldAlert,
  Mic,
  MicOff,
  Wand2,
  CheckCircle2,
  Languages,
  RotateCcw,
  Bot,
  ArrowRight,
  AlertCircle,
} from 'lucide-react'
import { api, post, useFetch } from '../api'
import { useLang } from '../i18n'
import { Section, State } from '../ui'
import { extractCardId, decodeQrFromImageFile, scanQrFromVideo } from '../scanner'
import { MenuBar, MenuItemConfig } from '@/components/ui/animated-menu-bar'

export default function Doctor({ currentUser }: { currentUser?: any } = {}) {
  const [stage, setStage] = useState<'scan' | 'otp' | 'dash'>('scan')
  const [cardId, setCardId] = useState('')
  const [otpInfo, setOtpInfo] = useState<any>(null)
  const [err, setErr] = useState('')
  const [breakGlassOpen, setBreakGlassOpen] = useState(false)
  const [emergencySession, setEmergencySession] = useState<any>(null)
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

  const handleEmergencySuccess = (session: any) => {
    setEmergencySession(session)
    setCardId(session.card_id)
    setStage('dash')
  }

  const handleExitDashboard = () => {
    setEmergencySession(null)
    setStage('scan')
  }

  return (
    <Section
      eyebrow="Clinical OPD Suite"
      title="Doctor Consultation & Checkup"
      right={
        <div className="flex items-center gap-2">
          {emergencySession ? (
            <span className="pill pill-red animate-pulse font-mono font-bold">
              🚨 EMERGENCY OVERRIDE
            </span>
          ) : (
            <span className="pill pill-green">
              <span className="dot" />
              OPD Terminal Active
            </span>
          )}
          <span className="pill pill-grey font-mono hidden sm:inline-flex">
            {currentUser?.full_name || 'Dr. Rajesh Kulkarni, MD (SMO)'}
          </span>
        </div>
      }
    >
      {stage === 'scan' && (
        <Scan
          onCard={request}
          err={err}
          onOpenBreakGlass={() => setBreakGlassOpen(true)}
        />
      )}
      {stage === 'otp' && (
        <Otp
          cardId={cardId}
          info={otpInfo}
          onOk={() => setStage('dash')}
          onCancel={() => setStage('scan')}
          resend={() => request(cardId)}
          onOpenBreakGlass={() => setBreakGlassOpen(true)}
        />
      )}
      {stage === 'dash' && (
        <Dashboard
          cardId={cardId}
          onClose={handleExitDashboard}
          emergencySession={emergencySession}
          onEndEmergency={handleExitDashboard}
          t={t}
        />
      )}

      <BreakGlassModal
        isOpen={breakGlassOpen}
        onClose={() => setBreakGlassOpen(false)}
        initialCardId={cardId}
        onSuccess={handleEmergencySuccess}
      />
    </Section>
  )
}

function Scan({
  onCard,
  err,
  onOpenBreakGlass,
}: {
  onCard: (id: string) => void
  err: string
  onOpenBreakGlass: () => void
}) {
  const { t } = useLang()
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
            if (video.current) {
              const detected = scanQrFromVideo(video.current, canvas)
              if (detected) {
                return onCard(detected)
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
    setCam('Scanning uploaded card for QR code...')
    try {
      const detectedId = await decodeQrFromImageFile(file)
      setCam(`✓ Scanned Card ID: ${detectedId}`)
      onCard(detectedId)
    } catch (e: any) {
      setCam(e.message || 'No legible QR code found in uploaded image.')
    }
  }

  return (
    <div className="grid gap-8 max-w-[800px] mx-auto">
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

        {/* Emergency Break-Glass Access Option */}
        <div className="mt-5 pt-4 border-t border-red-200/60 bg-red-50/60 -mx-6 md:-mx-8 -mb-6 md:-mb-8 p-4 px-6 md:px-8 rounded-b-2xl flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-t">
          <div className="flex items-center gap-2.5 text-xs text-red-950">
            <span className="text-xl">🚨</span>
            <div>
              <span className="font-extrabold block text-red-900">Unconscious Citizen / Trauma Emergency?</span>
              <span className="text-[11px] text-red-700 font-medium">Bypass OTP verification with mandatory audited clinical justification</span>
            </div>
          </div>
          <button
            type="button"
            onClick={onOpenBreakGlass}
            className="btn bg-red-600 hover:bg-red-700 text-white text-xs h-9 px-4 font-bold shrink-0 shadow-xs"
          >
            🚨 Emergency Break-Glass
          </button>
        </div>
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
  onOpenBreakGlass,
}: {
  cardId: string
  info: any
  onOk: () => void
  onCancel: () => void
  resend: () => void
  onOpenBreakGlass: () => void
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

      <div className="mt-5 pt-4 border-t border-slate-100 text-center">
        <button
          type="button"
          onClick={onOpenBreakGlass}
          className="text-xs font-bold text-red-600 hover:text-red-700 hover:underline"
        >
          🚨 Patient Incapacitated / Unable to Provide OTP? Initiate Emergency Break-Glass
        </button>
      </div>
    </div>
  )
}

function BreakGlassModal({
  isOpen,
  onClose,
  initialCardId,
  onSuccess,
}: {
  isOpen: boolean
  onClose: () => void
  initialCardId: string
  onSuccess: (session: any) => void
}) {
  const [targetCard, setTargetCard] = useState(initialCardId || '')
  const [reason, setReason] = useState('')
  const [doctorName, setDoctorName] = useState('Dr. Rajesh Kulkarni, MD')
  const [role, setRole] = useState('Senior Medical Officer (SMO)')
  const [duration, setDuration] = useState('30')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')

  useEffect(() => {
    if (initialCardId) setTargetCard(initialCardId)
  }, [initialCardId])

  if (!isOpen) return null

  const submit = async () => {
    if (!targetCard.trim() || reason.trim().length < 10) return
    setLoading(true)
    setErr('')
    try {
      const res = await post('/api/consent/emergency', {
        card_id: targetCard.trim(),
        reason: reason.trim(),
        practitioner_name: doctorName.trim(),
        practitioner_role: role.trim(),
        duration_minutes: Number(duration),
      })
      onSuccess({
        token: res.token,
        card_id: targetCard.trim(),
        reason: reason.trim(),
        expires_at: res.expires_at,
        practitioner_name: doctorName.trim(),
        audit_id: res.audit_id,
      })
      onClose()
    } catch (e: any) {
      setErr(e.message || 'Failed to initiate emergency break-glass access.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl border-2 border-red-500 overflow-hidden relative">
        <div className="flex items-center justify-between pb-3 border-b border-red-100 mb-4">
          <div className="flex items-center gap-2.5">
            <span className="p-2 rounded-xl bg-red-100 text-red-600 text-lg">🚨</span>
            <div>
              <h3 className="font-extrabold text-base text-red-950">Emergency Break-Glass Access</h3>
              <p className="text-[11px] text-red-700 font-medium">DPDP Act 2023 Section 8 Emergency Exemption</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 font-bold p-1 rounded-lg"
          >
            ✕
          </button>
        </div>

        <div className="p-3 bg-red-50 rounded-xl border border-red-200 text-xs text-red-900 leading-relaxed mb-4">
          <p className="font-bold mb-1">⚠️ Legal & Regulatory Notice:</p>
          <p>
            Emergency access bypasses patient OTP verification for unconscious, trauma, or incapacitated citizens. Every session creates an <span className="font-bold">immutable, tamper-evident audit record</span> with your practitioner ID. Falsifying emergency justification is punishable under hospital governance.
          </p>
        </div>

        <div className="space-y-3.5 text-xs">
          <div>
            <label className="label mb-1">Target Patient Health Card ID *</label>
            <input
              className="input font-mono font-bold text-sm h-10"
              placeholder="e.g. SS-A8F392B1"
              value={targetCard}
              onChange={(e) => setTargetCard(e.target.value.toUpperCase())}
            />
          </div>

          <div>
            <label className="label mb-1">
              Mandatory Clinical Emergency Justification *{' '}
              <span className="text-[10px] text-slate-400 font-normal">
                (Min 10 characters — {Math.max(0, 10 - reason.trim().length)} needed)
              </span>
            </label>
            <textarea
              className="input h-20 text-xs py-2 resize-none"
              placeholder="e.g. Unconscious polytrauma victim arriving via ambulance 108. Severe hypotension; urgently need blood group, allergies, and chronic anticoagulant history."
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label mb-1">Attending Clinician</label>
              <input
                className="input text-xs h-9"
                value={doctorName}
                onChange={(e) => setDoctorName(e.target.value)}
              />
            </div>
            <div>
              <label className="label mb-1">Override Duration</label>
              <select
                className="input text-xs h-9"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              >
                <option value="15">15 Minutes</option>
                <option value="30">30 Minutes (Standard)</option>
                <option value="60">60 Minutes</option>
              </select>
            </div>
          </div>
        </div>

        {err && (
          <div className="mt-3 p-2.5 rounded-lg bg-red-50 border border-red-200 text-red-800 text-xs font-semibold">
            ⚠️ {err}
          </div>
        )}

        <div className="flex gap-2.5 mt-5 pt-3 border-t border-slate-100">
          <button
            type="button"
            className="btn btn-ghost flex-1 h-10 text-xs font-semibold"
            onClick={onClose}
            disabled={loading}
          >
            Cancel
          </button>
          <button
            type="button"
            className="btn bg-red-600 hover:bg-red-700 text-white font-bold flex-1 h-10 text-xs shadow-md shadow-red-600/20 disabled:opacity-50"
            disabled={!targetCard.trim() || reason.trim().length < 10 || loading}
            onClick={submit}
          >
            {loading ? 'Authorizing…' : '🚨 Authorize Break-Glass Override'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Dashboard({
  cardId,
  onClose,
  emergencySession,
  onEndEmergency,
  t,
}: {
  cardId: string
  onClose: () => void
  emergencySession?: any
  onEndEmergency?: () => void
  t: any
}) {
  const { lang } = useLang()
  const p = useFetch<any>(`/api/patients/${cardId}`)
  const sum = useFetch<{ bullets: { date?: string; text: string }[]; audio_url?: string }>(
    `/api/patients/${cardId}/summary`
  )
  const hist = useFetch<any[]>(`/api/patients/${cardId}/records`)
  const grants = useFetch<any>(`/api/consent/grants/${cardId}`, 5000)

  const [cond, setCond] = useState('')
  const [ward, setWard] = useState('Shivajinagar')
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

  // AI Voice Assistant & Auto-Scribe State
  const [voiceTranscript, setVoiceTranscript] = useState('')
  const [voiceLang, setVoiceLang] = useState('auto')
  const [voiceListening, setVoiceListening] = useState(false)
  const [voiceParsing, setVoiceParsing] = useState(false)
  const [voiceResult, setVoiceResult] = useState<any>(null)
  const [voiceError, setVoiceError] = useState('')
  const speechRecognitionRef = useRef<any>(null)

  const handleAiVoiceParse = async (rawText?: string) => {
    const textToParse = (rawText !== undefined ? rawText : voiceTranscript).trim()
    if (!textToParse) {
      setVoiceError('Please dictate or enter clinical observations first.')
      return
    }
    setVoiceParsing(true)
    setVoiceError('')
    try {
      const res: any = await post('/api/voice-parse', { transcript: textToParse })
      if (res?.success && res?.parsed) {
        const p = res.parsed
        if (p.condition) setCond(p.condition)
        if (p.ward && PUNE_WARDS.includes(p.ward)) setWard(p.ward)
        if (Array.isArray(p.medicines) && p.medicines.length > 0) {
          setMeds((existing) => Array.from(new Set([...existing, ...p.medicines])))
        }
        if (p.dosage) setDosage(p.dosage)
        if (p.notes) setNotes(p.notes)
        if (typeof p.refill_restricted === 'boolean') setRestricted(p.refill_restricted)
        setVoiceResult(p)
        setMsg(`✓ AI Voice Assistant populated all fields (${p.condition || 'Consultation'} @ ${p.ward || ward})`)
      } else {
        setVoiceError('Could not parse clinical fields from speech. Please verify dictation.')
      }
    } catch (e: any) {
      setVoiceError(e.message || 'AI Voice parsing failed.')
    } finally {
      setVoiceParsing(false)
    }
  }

  const toggleSpeechRecognition = () => {
    const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    if (!SR) {
      setVoiceError('Browser does not support live Web Speech API. Please type consultation notes manually.')
      return
    }
    if (voiceListening) {
      if (speechRecognitionRef.current) {
        try { speechRecognitionRef.current.stop() } catch {}
      }
      setVoiceListening(false)
      return
    }

    try {
      const recognition = new SR()
      speechRecognitionRef.current = recognition
      let langCode = 'en-IN'
      if (voiceLang === 'mr') langCode = 'mr-IN'
      else if (voiceLang === 'hi') langCode = 'hi-IN'
      else if (voiceLang === 'en') langCode = 'en-IN'
      else langCode = lang === 'mr' ? 'mr-IN' : 'en-IN'

      recognition.lang = langCode
      recognition.continuous = true
      recognition.interimResults = true

      recognition.onstart = () => {
        setVoiceListening(true)
        setVoiceError('')
      }
      recognition.onerror = (event: any) => {
        if (event.error !== 'no-speech') {
          setVoiceError(`Voice input error: ${event.error}`)
        }
        setVoiceListening(false)
      }
      recognition.onend = () => {
        setVoiceListening(false)
      }
      recognition.onresult = (event: any) => {
        let fullTranscript = ''
        for (let i = 0; i < event.results.length; i++) {
          fullTranscript += event.results[i][0].transcript + ' '
        }
        setVoiceTranscript(fullTranscript.trim())
      }
      recognition.start()
    } catch (err: any) {
      setVoiceError(err.message || 'Microphone activation failed')
      setVoiceListening(false)
    }
  }

  // Dynamic Consent state
  const [grantScope, setGrantScope] = useState('full_history')
  const [grantDuration, setGrantDuration] = useState('60')
  const [grantRole, setGrantRole] = useState('doctor')
  const [grantRep, setGrantRep] = useState('Dr. Rajesh Kulkarni, MD')
  const [grantMsg, setGrantMsg] = useState('')
  const [grantSubmitting, setGrantSubmitting] = useState(false)

  type DoctorTab = 'all' | 'summary' | 'history' | 'checkup' | 'safety' | 'consent'
  const [activeTab, setActiveTab] = useState<DoctorTab>('all')

  const PUNE_WARDS = [
    'Shivajinagar',
    'Kothrud',
    'Hadapsar',
    'Aundh',
    'Baner',
    'Viman Nagar',
    'Kasba Peth',
    'Dhankawadi',
    'Katraj',
    'Wadgaon Sheri',
    'Bibvewadi',
    'Warje',
    'Sinhagad Road',
    'Yerawada',
    'Kondhwa',
  ]

  const OUTBREAK_DISEASES = [
    'Dengue',
    'Malaria',
    'Chikungunya',
    'Influenza',
    'Typhoid',
    'Acute Diarrheal Disease',
  ]

  const DISEASE_CATEGORIES = [
    { name: 'Dengue', icon: '🦟' },
    { name: 'Malaria', icon: '🦟' },
    { name: 'Viral Fever', icon: '🌡️' },
    { name: 'Flu', icon: '🤧' },
    { name: 'Typhoid', icon: '🧫' },
    { name: 'Gastroenteritis', icon: '🤢' },
    { name: 'Chikungunya', icon: '🦟' },
    { name: 'Acute Bronchitis', icon: '🫁' },
    { name: 'Hypertension', icon: '❤️' },
    { name: 'Type 2 Diabetes', icon: '🩸' },
    { name: 'COVID-19', icon: '🦠' },
    { name: 'Other', icon: '🏥' },
  ]

  const doctorMenuItems: MenuItemConfig<DoctorTab>[] = [
    {
      key: 'all',
      label: 'Overview',
      icon: <LayoutDashboard className="w-4.5 h-4.5 text-slate-700 dark:text-slate-300 group-hover:text-indigo-600 transition-colors" />,
    },
    {
      key: 'summary',
      label: 'AI Summary',
      icon: <Sparkles className="w-4.5 h-4.5 text-slate-700 dark:text-slate-300 group-hover:text-emerald-600 transition-colors" />,
    },
    {
      key: 'history',
      label: 'Visits',
      icon: <History className="w-4.5 h-4.5 text-slate-700 dark:text-slate-300 group-hover:text-blue-600 transition-colors" />,
    },
    {
      key: 'checkup',
      label: 'Rx & Checkup',
      icon: <Stethoscope className="w-4.5 h-4.5 text-slate-700 dark:text-slate-300 group-hover:text-amber-600 transition-colors" />,
    },
    {
      key: 'safety',
      label: 'Drug Safety',
      icon: <ShieldAlert className="w-4.5 h-4.5 text-slate-700 dark:text-slate-300 group-hover:text-rose-600 transition-colors" />,
    },
    {
      key: 'consent',
      label: 'Consent & Grants',
      icon: <ShieldAlert className="w-4.5 h-4.5 text-slate-700 dark:text-slate-300 group-hover:text-purple-600 transition-colors" />,
    },
  ]

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

  useEffect(() => {
    if (p.data?.locality) {
      const match = PUNE_WARDS.find((w) => p.data.locality.toLowerCase().includes(w.toLowerCase()))
      if (match) setWard(match)
    }
  }, [p.data?.locality])

  const save = async () => {
    if (!cond.trim()) return
    setSaving(true)
    setMsg('')
    try {
      const res: any = await post(`/api/patients/${cardId}/records`, {
        condition: cond.trim(),
        ward: ward,
        medicines: meds,
        notes: notes.trim(),
        dosage: dosage.trim(),
        refill_restricted: restricted,
      })
      const countMsg = res?.updated_count ? ` (Active Cases: ${res.updated_count})` : ''
      setMsg(res?.message || `✓ Checkup saved! Ward "${ward}" count updated for "${cond.trim()}"${countMsg}. Live ML Surveillance updated!`)
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

  // Subcomponents for the Doctor OPD suite
  const summarySection = (
    <div className="card p-6 bg-gradient-to-br from-emerald-50/70 via-white to-emerald-50/30 border-emerald-200 shadow-xs">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-emerald-700" />
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
  )

  const historySection = (
    <div className="card p-6 shadow-xs">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <History className="w-5 h-5 text-blue-600" />
          <h3 className="font-bold text-ink">Clinical Visit History</h3>
        </div>
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
  )

  const checkupSection = (
    <div className="card p-6 md:p-7 grid gap-5 shadow-sm">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div className="flex items-center gap-2">
          <Stethoscope className="w-5 h-5 text-amber-600" />
          <div>
            <h3 className="font-extrabold text-ink text-base">New Checkup Record</h3>
            <p className="text-xs text-slate-400">Commit diagnosis & prescriptions</p>
          </div>
        </div>
        <span className="pill pill-amber text-xs font-semibold">
          🔒 {t('lock', 'Locked after 24 hrs')}
        </span>
      </div>

      {/* AI Voice Assistant & Auto-Fill Section (Theme-Matched & Minimal) */}
      <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/70 space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-orange-600" />
            <h4 className="font-bold text-xs text-ink">
              AI Voice Assistant
            </h4>
            <span className="text-[11px] text-slate-500 hidden sm:inline">
              (Dictate in Marathi, Hindi, or English to auto-populate all form fields)
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <Languages className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={voiceLang}
              onChange={(e) => setVoiceLang(e.target.value)}
              className="bg-white border border-slate-200 rounded-lg text-slate-700 text-[11px] font-medium py-1 px-2 focus:outline-none focus:border-orange-500"
            >
              <option value="auto">Auto Detect</option>
              <option value="mr">मराठी (Marathi)</option>
              <option value="hi">हिंदी (Hindi)</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>

        <div className="relative">
          <textarea
            value={voiceTranscript}
            onChange={(e) => setVoiceTranscript(e.target.value)}
            placeholder="Click 'Dictate Voice' or speak clinical observations here (e.g. 'रुग्णाला कात्रज भागात तीव्र ताप आहे, डेंग्यूचा संशय आहे. पॅरासिटामॉल आणि ओआरएस द्या' or 'Patient from Hadapsar has acute diarrhea...')"
            rows={2}
            className="input w-full py-2 px-3 text-xs resize-none bg-white focus:bg-white text-slate-800 placeholder:text-slate-400"
          />
          {voiceListening && (
            <span className="absolute top-2 right-2 flex items-center gap-1.5 bg-red-100 text-red-700 border border-red-200 text-[10px] font-bold px-2 py-0.5 rounded-full animate-pulse">
              <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-ping" />
              Listening…
            </span>
          )}
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={toggleSpeechRecognition}
              className={`btn h-8 px-3 text-xs font-semibold ${
                voiceListening ? 'bg-red-600 hover:bg-red-700 text-white' : 'btn-peach'
              }`}
            >
              {voiceListening ? (
                <>
                  <MicOff className="w-3.5 h-3.5 text-white" />
                  <span>Stop Dictation</span>
                </>
              ) : (
                <>
                  <Mic className="w-3.5 h-3.5 text-orange-600" />
                  <span>Dictate Voice</span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={() => handleAiVoiceParse()}
              disabled={voiceParsing || !voiceTranscript.trim()}
              className="btn btn-saffron h-8 px-3 text-xs font-semibold disabled:opacity-50"
            >
              {voiceParsing ? (
                <>
                  <Sparkles className="w-3.5 h-3.5 animate-spin" />
                  <span>Processing…</span>
                </>
              ) : (
                <>
                  <Wand2 className="w-3.5 h-3.5" />
                  <span>Auto-Fill All Fields</span>
                </>
              )}
            </button>

            {voiceTranscript && (
              <button
                type="button"
                onClick={() => {
                  setVoiceTranscript('')
                  setVoiceResult(null)
                  setVoiceError('')
                }}
                className="btn btn-ghost h-8 px-2 text-xs text-slate-400 hover:text-slate-600"
                title="Clear"
              >
                <RotateCcw className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          <span className="text-[11px] text-slate-400">
            Identifies condition, ward, medicines & dosage
          </span>
        </div>

        {voiceError && (
          <div className="p-2.5 rounded-lg bg-red-50 border border-red-200 text-red-800 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0 text-red-600" />
            <span>{voiceError}</span>
          </div>
        )}

        {voiceResult && (
          <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex flex-wrap items-center justify-between gap-2 animate-in fade-in">
            <div className="flex items-center gap-2 flex-wrap">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="font-bold">
                ✓ Auto-filled: {voiceResult.condition || 'Consultation'} @ {voiceResult.ward || ward}
              </span>
              <span className="pill pill-grey text-[10px] py-0 px-1.5 font-normal">
                {voiceResult.detected_language || 'Multilingual'}
              </span>
            </div>
            {voiceResult.corrections_made && voiceResult.corrections_made.length > 0 && (
              <span className="text-[11px] text-emerald-700">
                Corrected: {voiceResult.corrections_made.join(' • ')}
              </span>
            )}
          </div>
        )}
      </div>

      {/* Disease Category Quick-Select Grid (Accurate Surveillance Tracking) */}
      <div className="space-y-2.5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1.5">
          <div className="flex items-center gap-1.5 flex-wrap">
            <h4 className="font-extrabold text-sm text-ink">Disease Category</h4>
            <span className="text-xs text-slate-500 font-medium">
              (Select for accurate surveillance tracking)
            </span>
          </div>
          <span className="text-[11px] text-amber-700 font-semibold font-mono bg-amber-50 px-2 py-0.5 rounded-md border border-amber-200/70 w-fit">
            📡 Triggers Pune ML Outbreak Radar
          </span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2.5">
          {DISEASE_CATEGORIES.map((dis) => {
            const isSelected =
              cond.toLowerCase() === dis.name.toLowerCase() ||
              (dis.name === 'Flu' && cond.toLowerCase().includes('influenza')) ||
              (dis.name === 'Gastroenteritis' && cond.toLowerCase().includes('diarrhea'))

            return (
              <button
                key={dis.name}
                type="button"
                onClick={() => {
                  if (dis.name === 'Other') {
                    setCond('')
                  } else if (dis.name === 'Flu') {
                    setCond('Influenza')
                  } else if (dis.name === 'Gastroenteritis') {
                    setCond('Acute Diarrheal Disease')
                  } else {
                    setCond(dis.name)
                  }
                }}
                className={`relative group rounded-2xl p-3 sm:p-4 flex flex-col items-center justify-center gap-1.5 text-center transition-all duration-150 cursor-pointer ${
                  isSelected
                    ? 'bg-orange-50/90 border-2 border-orange-500 text-orange-950 shadow-sm ring-2 ring-orange-500/15 scale-[1.02]'
                    : 'bg-white hover:bg-slate-50 border border-slate-200/90 text-slate-800 shadow-2xs hover:border-slate-300 hover:shadow-xs'
                }`}
              >
                <span className="text-2xl sm:text-3xl filter drop-shadow-xs transition-transform duration-150 group-hover:scale-110">
                  {dis.icon}
                </span>
                <span
                  className={`text-xs tracking-tight ${
                    isSelected ? 'font-extrabold text-orange-950' : 'font-semibold text-slate-700'
                  }`}
                >
                  {dis.name}
                </span>
                {isSelected && (
                  <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-orange-600 ring-2 ring-white" />
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Ward & Condition Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="sm:col-span-2">
          <label className="label">Primary Diagnosis / Condition *</label>
          <input
            className="input font-medium"
            placeholder="e.g. Dengue, Acute Bronchitis, Typhoid"
            value={cond}
            onChange={(e) => setCond(e.target.value)}
          />
        </div>
        <div>
          <label className="label">Pune Municipal Ward *</label>
          <select
            className="input font-medium"
            value={ward}
            onChange={(e) => setWard(e.target.value)}
          >
            {PUNE_WARDS.map((w) => (
              <option key={w} value={w}>
                {w}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Live Outbreak Aggregate Sync Indicator */}
      <div className="flex items-center justify-between text-xs px-3.5 py-2 rounded-xl bg-orange-50/70 border border-orange-200/80 text-orange-950 font-medium">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>
            <strong>Municipal Surveillance Pipeline:</strong> Checkups logged for{' '}
            <strong className="text-orange-900">{ward}</strong> ({cond || 'Selected Condition'}) automatically update aggregate epidemiological counts in real-time.
          </span>
        </div>
        <span className="text-[10px] font-mono font-bold bg-white px-2 py-0.5 rounded border border-orange-200 text-orange-800 shrink-0">
          DPDP Act §2023 Compliant
        </span>
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
  )

  const safetySection = (
    <div className="card p-6 md:p-7 grid gap-5 border-rose-200 bg-rose-50/20 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-rose-100">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-rose-600" />
          <div>
            <h3 className="font-extrabold text-ink text-base">Drug Safety & Interaction Monitor</h3>
            <p className="text-xs text-slate-500">Allergy profiles & automated contraindication scan</p>
          </div>
        </div>
        <span className="pill pill-red text-xs font-semibold">
          {allergies.length} Allergies • {conflicts.length} Alert{conflicts.length === 1 ? '' : 's'}
        </span>
      </div>

      <div>
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Patient Known Allergies</h4>
        {allergies.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {allergies.map((a) => (
              <span key={a} className="pill pill-red font-bold text-xs">
                ⚠️ Severe Allergy: {a.trim()}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs text-slate-500 bg-white p-3 rounded-xl border border-slate-200">
            ✓ No known drug allergies flagged in citizen registry.
          </p>
        )}
      </div>

      <div>
        <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">Active Prescriptions Conflict Analysis</h4>
        {conflicts.length > 0 ? (
          <div className="grid gap-2">
            {conflicts.map((c, i) => (
              <div
                key={i}
                className="p-3 rounded-xl bg-red-100/80 border border-red-300 text-red-950 text-xs font-semibold flex items-start gap-2"
              >
                <span>⚠️</span>
                <span>{c.message ?? `${c.a} + ${c.b}`}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-xs text-emerald-800 bg-emerald-50/80 p-3 rounded-xl border border-emerald-200">
            ✓ No drug-drug or drug-allergy interactions detected with current prescription list.
          </p>
        )}
      </div>

      <div className="p-3 bg-amber-50 rounded-xl border border-amber-200 text-xs text-amber-900">
        <span className="font-bold">Schedule H Compliance:</span> Refill restrictions are currently {restricted ? 'ENFORCED (Single-fill only)' : 'Standard (Dispense as per doctor directions)'}.
      </div>

      <button
        type="button"
        className="btn btn-ghost h-10 w-full text-xs font-semibold border border-slate-200"
        onClick={() => setActiveTab('checkup')}
      >
        Return to Prescription Entry →
      </button>
    </div>
  )

  const revokeGrant = async (id: number) => {
    try {
      await post('/api/consent/revoke', {
        grant_id: id,
        reason: 'Revoked by patient or attending clinician.',
      })
      grants.reload()
      setGrantMsg('✓ Consent grant revoked immediately.')
    } catch (e: any) {
      setGrantMsg(`⚠️ ${e.message}`)
    }
  }

  const createGrant = async () => {
    if (!grantRep.trim()) return
    setGrantSubmitting(true)
    setGrantMsg('')
    try {
      await post('/api/consent/grant', {
        card_id: cardId,
        scope: grantScope,
        duration_minutes: Number(grantDuration),
        role_target: grantRole,
        representative_name: grantRep.trim(),
        granted_by: 'patient',
      })
      grants.reload()
      setGrantMsg('✓ Scoped consent grant issued successfully.')
    } catch (e: any) {
      setGrantMsg(`⚠️ ${e.message}`)
    } finally {
      setGrantSubmitting(false)
    }
  }

  const consentSection = (
    <div className="space-y-6">
      {/* Grant creation card */}
      <div className="card p-6 md:p-7 shadow-xs">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">🛡️</span>
            <div>
              <h3 className="font-extrabold text-ink text-base">Dynamic Citizen Consent Governance</h3>
              <p className="text-xs text-slate-400">Scoped, time-bound delegations under DPDP Act 2023</p>
            </div>
          </div>
          <span className="pill pill-green text-xs font-bold">Patient Governed</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5 text-xs mb-4">
          <div>
            <label className="label mb-1">Delegatee Name / Role</label>
            <input
              className="input text-xs h-9"
              value={grantRep}
              onChange={(e) => setGrantRep(e.target.value)}
              placeholder="e.g. Dr. Kulkarni (Cardiologist)"
            />
          </div>
          <div>
            <label className="label mb-1">Permission Scope</label>
            <select
              className="input text-xs h-9"
              value={grantScope}
              onChange={(e) => setGrantScope(e.target.value)}
            >
              <option value="full_history">Full Clinical Dossier (Unrestricted)</option>
              <option value="prescriptions_only">Prescriptions Only (Diagnosis Redacted)</option>
              <option value="vitals_and_allergies">Vitals & Allergies Only</option>
            </select>
          </div>
          <div>
            <label className="label mb-1">Validity Duration</label>
            <select
              className="input text-xs h-9"
              value={grantDuration}
              onChange={(e) => setGrantDuration(e.target.value)}
            >
              <option value="30">30 Minutes</option>
              <option value="60">1 Hour (Standard Consultation)</option>
              <option value="360">6 Hours</option>
              <option value="1440">24 Hours</option>
              <option value="10080">7 Days (Caregiver / Inpatient)</option>
            </select>
          </div>
        </div>

        {grantMsg && (
          <div className="mb-3 p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold">
            {grantMsg}
          </div>
        )}

        <button
          type="button"
          onClick={createGrant}
          disabled={grantSubmitting || !grantRep.trim()}
          className="btn btn-saffron text-xs font-bold h-9 px-4"
        >
          {grantSubmitting ? 'Granting…' : 'Issue Dynamic Consent Grant →'}
        </button>
      </div>

      {/* Active Grants List */}
      <div className="card p-6 md:p-7 shadow-xs">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
          <h4 className="font-bold text-ink text-sm">Active & Historical Record Grants</h4>
          <button
            type="button"
            onClick={() => grants.reload()}
            className="btn btn-ghost h-7 px-2.5 text-[11px]"
          >
            🔄 Refresh
          </button>
        </div>

        <State
          loading={grants.loading}
          error={grants.error}
          empty={!grants.data?.grants?.length}
          emptyText="No active delegations for this citizen card."
          onRetry={grants.reload}
        />

        {!!grants.data?.grants?.length && (
          <div className="overflow-x-auto">
            <table className="w-full font-mono text-xs text-left">
              <thead>
                <tr>
                  <th className="th">Scope</th>
                  <th className="th">Delegatee</th>
                  <th className="th">Time Remaining</th>
                  <th className="th">Status</th>
                  <th className="th text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {grants.data.grants.map((g: any) => (
                  <tr key={g.id} className="hover:bg-slate-50/70">
                    <td className="td">
                      <span className="pill pill-grey text-[10px] uppercase font-bold">
                        {g.scope}
                      </span>
                    </td>
                    <td className="td font-medium text-slate-800">
                      {g.representative_name || g.role_target || 'Clinician'}
                    </td>
                    <td className="td text-slate-500 font-semibold">
                      ⏱️ {g.remaining_minutes} mins
                    </td>
                    <td className="td">
                      <span
                        className={`pill text-[10px] font-bold ${
                          g.status === 'ACTIVE'
                            ? 'pill-green'
                            : g.status === 'REVOKED'
                            ? 'pill-red'
                            : 'pill-amber'
                        }`}
                      >
                        {g.status}
                      </span>
                    </td>
                    <td className="td text-right">
                      {g.status === 'ACTIVE' && (
                        <button
                          type="button"
                          onClick={() => revokeGrant(g.id)}
                          className="px-2.5 py-1 rounded bg-red-50 text-red-700 hover:bg-red-100 font-bold text-[11px] border border-red-200 transition-colors cursor-pointer"
                        >
                          Instant Revoke ✕
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )

  return (
    <div className="grid gap-6 animate-in fade-in duration-200">
      {/* Emergency Break-Glass Active Override Alert Banner */}
      {emergencySession && (
        <div className="p-4 rounded-2xl bg-gradient-to-r from-red-600 via-rose-600 to-red-700 text-white shadow-xl shadow-red-500/20 flex flex-wrap items-center justify-between gap-4 border border-red-400">
          <div className="flex items-center gap-3">
            <span className="p-2.5 rounded-xl bg-white/20 text-xl animate-pulse">🚨</span>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-sm tracking-wide uppercase">Active Emergency Break-Glass Session</span>
                <span className="px-2 py-0.5 rounded-full bg-red-900/60 text-xs font-mono font-bold text-red-200">
                  DPDP Section 8 Overridden
                </span>
              </div>
              <p className="text-xs text-red-100 mt-0.5 max-w-xl">
                <span className="font-semibold text-white">Stated Clinical Rationale:</span> "{emergencySession.reason}"
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className="px-3 py-1.5 rounded-xl bg-white/10 font-mono text-xs font-bold border border-white/20">
              ⏱️ Audit Token Active
            </span>
            <button
              type="button"
              onClick={onEndEmergency}
              className="px-3 py-1.5 rounded-xl bg-white text-red-700 font-bold text-xs hover:bg-red-50 transition-colors shadow-sm"
            >
              End Override ✕
            </button>
          </div>
        </div>
      )}

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

      {/* Animated Navigation Menu Bar for Doctor OPD Suite */}
      <div className="flex justify-center -my-1">
        <MenuBar<DoctorTab>
          active={activeTab}
          onSelect={setActiveTab}
          items={doctorMenuItems}
        />
      </div>

      {/* Subcomponents Rendering depending on selected activeTab */}
      {activeTab === 'all' && (
        <div className="grid lg:grid-cols-2 gap-6 items-start">
          <div className="grid gap-6">
            {summarySection}
            {historySection}
          </div>
          <div>
            {checkupSection}
          </div>
        </div>
      )}

      {activeTab === 'summary' && (
        <div className="max-w-3xl mx-auto w-full">
          {summarySection}
        </div>
      )}

      {activeTab === 'history' && (
        <div className="max-w-3xl mx-auto w-full">
          {historySection}
        </div>
      )}

      {activeTab === 'checkup' && (
        <div className="max-w-3xl mx-auto w-full">
          {checkupSection}
        </div>
      )}

      {activeTab === 'safety' && (
        <div className="max-w-3xl mx-auto w-full">
          {safetySection}
        </div>
      )}

      {activeTab === 'consent' && (
        <div className="max-w-3xl mx-auto w-full">
          {consentSection}
        </div>
      )}
    </div>
  )
}
