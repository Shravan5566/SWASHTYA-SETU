import { useState, useRef, useEffect } from 'react'
import { post, useFetch } from '../api'
import { useLang } from '../i18n'
import { Section, State } from '../ui'
import { extractCardId, decodeQrFromImageFile, scanQrFromVideo } from '../scanner'

export default function Pharmacist() {
  const { t } = useLang()
  const [filterCard, setFilterCard] = useState('')
  const [showCamera, setShowCamera] = useState(false)
  const [scanStatus, setScanStatus] = useState('')
  const videoRef = useRef<HTMLVideoElement>(null)

  const qUrl = filterCard.trim()
    ? `/api/pharmacy/queue?card_id=${encodeURIComponent(filterCard.trim())}`
    : '/api/pharmacy/queue'
  const q = useFetch<any[]>(qUrl, 10000)
  const [dispensingId, setDispensingId] = useState<number | null>(null)
  const [err, setErr] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

  // Live Camera Scanner Lifecycle
  useEffect(() => {
    if (!showCamera) return

    let stopped = false
    let stream: MediaStream | null = null
    let raf: number
    const canvas = document.createElement('canvas')

    if (navigator.mediaDevices?.getUserMedia) {
      navigator.mediaDevices
        .getUserMedia({ video: { facingMode: 'environment' } })
        .then((s) => {
          stream = s
          if (videoRef.current) {
            videoRef.current.srcObject = s
            videoRef.current.play().catch(() => {})
          }
          const tick = () => {
            if (stopped) return
            if (videoRef.current) {
              const detected = scanQrFromVideo(videoRef.current, canvas)
              if (detected) {
                setFilterCard(detected)
                setScanStatus(`✓ Successfully Scanned Card: ${detected}`)
                setShowCamera(false)
                return
              }
            }
            raf = requestAnimationFrame(tick)
          }
          tick()
        })
        .catch(() => {
          setScanStatus('Camera unavailable. You can upload a QR card photo or enter the Card ID.')
        })
    }

    return () => {
      stopped = true
      cancelAnimationFrame(raf)
      stream?.getTracks().forEach((x) => x.stop())
    }
  }, [showCamera])

  const handleUpload = async (file?: File) => {
    if (!file) return
    setScanStatus('Scanning uploaded card image for QR code...')
    try {
      const detected = await decodeQrFromImageFile(file)
      setFilterCard(detected)
      setScanStatus(`✓ Successfully Scanned Card: ${detected}`)
      setShowCamera(false)
    } catch (e: any) {
      setScanStatus(e.message || 'No legible QR code found in uploaded card image.')
    }
  }

  const dispense = async (id: number) => {
    setErr('')
    setSuccessMsg('')
    setDispensingId(id)
    try {
      const res = await post('/api/pharmacy/dispense', { id })
      setSuccessMsg(res.message || 'Medication successfully dispensed and logged to audit trail.')
      q.reload()
    } catch (e: any) {
      setErr(e.message)
    } finally {
      setDispensingId(null)
    }
  }

  return (
    <Section
      eyebrow="Pharmacy Dispensary Terminal"
      title="Medication Dispensing Suite"
      right={
        <div className="flex items-center gap-2">
          <span className="pill pill-green">
            <span className="dot" />
            Live Queue ({q.data?.length ?? 0})
          </span>
          <button
            type="button"
            className="btn btn-ghost h-8 px-3 text-xs"
            onClick={() => q.reload()}
          >
            🔄 Refresh
          </button>
        </div>
      }
    >
      {/* Privacy Isolation Banner */}
      <div className="card p-5 mb-8 bg-gradient-to-r from-orange-50/70 via-amber-50/40 to-white border-orange-200 shadow-xs flex items-start gap-4">
        <div className="p-2 bg-white rounded-xl border border-orange-200/80 shadow-2xs shrink-0 mt-0.5">
          <img src="/sslogo-symbol.png" alt="Swasthya Setu" className="w-8 h-8 object-contain" />
        </div>
        <div>
          <div className="text-sm font-bold text-orange-950 flex items-center gap-2">
            <span>DPDP 2023 Cryptographic Role Isolation Active</span>
            <span className="pill pill-grey text-[10px] font-mono">Zero Leakage</span>
          </div>
          <p className="text-xs text-orange-900/80 mt-1 leading-relaxed">
            {t(
              'priv.banner',
              'Clinical diagnosis notes, doctor confidential observations, and patient medical histories are cryptographically excluded from dispensing queries. Pharmacists receive strictly isolated dosage directives.'
            )}
          </p>
        </div>
      </div>

      {/* Patient Card QR Scanner & Filter Bar */}
      <div className="card p-4 mb-6 bg-white shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          {/* Action buttons: Camera scan & Upload */}
          <div className="flex items-center gap-2">
            <button
              type="button"
              className={`btn h-9 px-3.5 text-xs font-bold flex items-center gap-1.5 ${
                showCamera ? 'btn-saffron' : 'btn-ghost border border-slate-200'
              }`}
              onClick={() => {
                setShowCamera(!showCamera)
                setScanStatus('')
              }}
            >
              📷 {showCamera ? 'Close QR Scanner' : 'Scan Patient QR Card'}
            </button>

            <label className="btn btn-ghost border border-slate-200 h-9 px-3.5 text-xs font-bold cursor-pointer flex items-center gap-1.5">
              📁 Upload QR Card
              <input
                type="file"
                accept="image/*"
                hidden
                onChange={(e) => handleUpload(e.target.files?.[0])}
              />
            </label>
          </div>

          {/* Card search / manual filter */}
          <div className="flex items-center gap-2 flex-1 min-w-[280px]">
            <span className="text-sm text-slate-400">🔍</span>
            <input
              className="input text-xs font-mono h-9 flex-1"
              placeholder="Filter by Patient Card ID (e.g. SS-TEST-001)…"
              value={filterCard}
              onChange={(e) => setFilterCard(e.target.value.toUpperCase())}
            />
            {filterCard && (
              <button
                type="button"
                className="btn btn-ghost h-9 px-3 text-xs"
                onClick={() => {
                  setFilterCard('')
                  setScanStatus('')
                }}
              >
                Clear
              </button>
            )}
          </div>
        </div>

        {/* Live Camera Viewfinder Modal / Tray */}
        {showCamera && (
          <div className="mt-4 pt-4 border-t border-slate-100">
            <div className="relative aspect-[16/10] max-w-[500px] mx-auto bg-slate-950 rounded-2xl overflow-hidden shadow-inner flex items-center justify-center">
              <video
                ref={videoRef}
                muted
                playsInline
                className="absolute inset-0 w-full h-full object-cover opacity-90"
              />
              {/* Target Reticle */}
              <div className="absolute inset-[15%] pointer-events-none border-2 border-emerald-500/40 rounded-2xl">
                <span className="absolute top-0 left-0 w-7 h-7 border-t-4 border-l-4 border-emerald-400 rounded-tl-xl" />
                <span className="absolute top-0 right-0 w-7 h-7 border-t-4 border-r-4 border-emerald-400 rounded-tr-xl" />
                <span className="absolute bottom-0 left-0 w-7 h-7 border-b-4 border-l-4 border-emerald-400 rounded-bl-xl" />
                <span className="absolute bottom-0 right-0 w-7 h-7 border-b-4 border-r-4 border-emerald-400 rounded-br-xl" />
                <span
                  className="absolute left-2 right-2 h-0.5 bg-emerald-400/90 shadow-[0_0_12px_#10b981]"
                  style={{ animation: 'scan 2.4s ease-in-out infinite' }}
                />
              </div>
            </div>
            <p className="text-center text-xs text-slate-500 mt-2 font-mono">
              Hold the patient's Digital Health Card QR in front of the lens to auto-dispense
            </p>
          </div>
        )}

        {/* Status banner */}
        {scanStatus && (
          <div className="mt-3 p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-xs font-mono text-slate-700 flex items-center justify-between">
            <span>ℹ️ {scanStatus}</span>
            <button
              type="button"
              className="text-slate-400 hover:text-slate-700 font-bold ml-2"
              onClick={() => setScanStatus('')}
            >
              ✕
            </button>
          </div>
        )}

        {filterCard && (
          <div className="mt-3 flex items-center gap-2 text-xs">
            <span className="pill pill-green font-mono font-bold">
              Filtering Card: {filterCard}
            </span>
            <span className="text-slate-500">
              ({q.data?.length ?? 0} matching prescription{q.data?.length === 1 ? '' : 's'})
            </span>
          </div>
        )}
      </div>

      {successMsg && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-semibold flex items-center justify-between">
          <span>✓ {successMsg}</span>
          <button
            type="button"
            className="text-emerald-700 hover:underline"
            onClick={() => setSuccessMsg('')}
          >
            ✕
          </button>
        </div>
      )}

      {err && (
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-900 text-xs font-semibold flex items-start gap-2">
          <span className="text-base">⛔</span>
          <div className="flex-1">{err}</div>
        </div>
      )}

      <div className="card overflow-hidden">
        <State
          loading={q.loading}
          error={q.error}
          empty={!q.data?.length}
          emptyText="No prescriptions currently awaiting dispensing in the Pune dispensary queue."
          onRetry={q.reload}
        />

        {!!q.data?.length && (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[780px] text-left">
              <thead>
                <tr>
                  <th className="th">Patient Card ID</th>
                  <th className="th">Issued Timestamp</th>
                  <th className="th">Condition Category</th>
                  <th className="th">Prescribed Medication & Dosage</th>
                  <th className="th text-right">Dispensing Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {q.data.map((r) => {
                  const isBlocked = r.restricted && r.dispensed
                  const isDispensed = r.dispensed

                  return (
                    <tr key={r.id} className="hover:bg-slate-50/60 transition-colors">
                      <td className="td">
                        <div className="font-mono font-bold text-ink">{r.card_id}</div>
                        <span className="text-[10px] font-mono text-slate-400">Prescription #{r.id}</span>
                      </td>
                      <td className="td font-mono text-xs text-slate-500">{r.date}</td>
                      <td className="td">
                        <span className="font-semibold text-slate-800 text-sm">{r.condition}</span>
                      </td>
                      <td className="td">
                        <div className="font-mono font-semibold text-sm text-ink">
                          {r.medicine}
                        </div>
                        <div className="text-xs text-slate-500 font-medium mt-0.5">{r.dosage}</div>

                        {/* Status Badges */}
                        <div className="mt-2 flex flex-wrap gap-2">
                          {r.restricted && !isDispensed && (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-amber-50 border border-amber-200 text-amber-900 text-[11px] font-bold">
                              ⚠️ Schedule H (Single Dispense Limit)
                            </span>
                          )}

                          {isBlocked && (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-red-50 border border-red-200 text-red-900 text-[11px] font-bold">
                              ⛔ Refill Restricted • Second Dispensing Prohibited
                            </span>
                          )}

                          {isDispensed && !r.restricted && (
                            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md bg-emerald-50 border border-emerald-200 text-emerald-800 text-[11px] font-bold">
                              ✓ Dispensed {r.dispensed_at ? `(${r.dispensed_at})` : ''}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="td text-right">
                        {isBlocked ? (
                          <button
                            type="button"
                            className="btn btn-ghost h-10 px-4 text-xs font-bold text-red-600 bg-red-50/50 border border-red-200 cursor-not-allowed"
                            disabled
                          >
                            ⛔ Refill Blocked
                          </button>
                        ) : isDispensed ? (
                          <button
                            type="button"
                            className="btn btn-ghost h-10 px-4 text-xs font-bold text-slate-400 bg-slate-50 border border-slate-200 cursor-not-allowed"
                            disabled
                          >
                            ✓ Dispensed
                          </button>
                        ) : (
                          <button
                            type="button"
                            className="btn btn-sage h-10 px-5 text-xs font-bold"
                            disabled={dispensingId === r.id}
                            onClick={() => dispense(r.id)}
                          >
                            {dispensingId === r.id
                              ? 'Logging…'
                              : `✓ ${t('dispense', 'Dispense & Log')}`}
                          </button>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Section>
  )
}
