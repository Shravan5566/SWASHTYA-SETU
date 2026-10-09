import { useState } from 'react'
import { post, useFetch } from '../api'
import { useLang } from '../i18n'
import { Section, State } from '../ui'

export default function Pharmacist() {
  const { t } = useLang()
  const q = useFetch<any[]>('/api/pharmacy/queue', 10000)
  const [dispensingId, setDispensingId] = useState<number | null>(null)
  const [err, setErr] = useState('')
  const [successMsg, setSuccessMsg] = useState('')

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
        <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 text-red-900 text-xs font-semibold">
          ⚠️ {err}
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
                  <th className="th text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {q.data.map((r) => (
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
                      {r.restricted && (
                        <div className="mt-2 inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-amber-50 border border-amber-200 text-amber-900 text-[11px] font-bold">
                          <span>⚠️</span>
                          <span>{t('restricted', 'Schedule H (Doctor re-authorization required)')}</span>
                        </div>
                      )}
                    </td>
                    <td className="td text-right">
                      <button
                        type="button"
                        className="btn btn-sage h-10 px-5 text-xs font-bold"
                        disabled={r.restricted || dispensingId === r.id}
                        onClick={() => dispense(r.id)}
                      >
                        {dispensingId === r.id
                          ? 'Logging…'
                          : `✓ ${t('dispense', 'Dispense & Log')}`}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Section>
  )
}
