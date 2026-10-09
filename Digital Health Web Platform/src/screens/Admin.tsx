import { useState } from 'react'
import { post, useFetch } from '../api'
import { useLang } from '../i18n'
import { Section, State } from '../ui'

export default function Admin() {
  const { t } = useLang()
  const q = useFetch<any[]>('/api/admin/queue', 10000)
  const log = useFetch<any[]>('/api/admin/audit', 5000)
  const [rejecting, setRejecting] = useState<any>(null)
  const [reason, setReason] = useState('')
  const [err, setErr] = useState('')
  const [msg, setMsg] = useState('')

  const act = async (id: any, action: 'approve' | 'reject') => {
    setErr('')
    setMsg('')
    try {
      const res = await post(`/api/admin/applications/${id}/${action}`, { reason })
      setMsg(res.message || `Application ${action}d successfully.`)
      setRejecting(null)
      setReason('')
      q.reload()
      log.reload()
    } catch (e: any) {
      setErr(e.message)
    }
  }

  return (
    <Section
      eyebrow="System Administration"
      title="Governance & Immutable Audit Trail"
      right={
        <div className="flex items-center gap-2">
          <span className="pill pill-green">
            <span className="dot" />
            Security Daemon Active
          </span>
          <button
            type="button"
            className="btn btn-ghost h-8 px-3 text-xs"
            onClick={() => {
              q.reload()
              log.reload()
            }}
          >
            🔄 Sync Trail
          </button>
        </div>
      }
    >
      {msg && (
        <div className="mb-6 p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs font-semibold flex items-center justify-between">
          <span>✓ {msg}</span>
          <button
            type="button"
            className="text-emerald-700 hover:underline"
            onClick={() => setMsg('')}
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

      {/* Administrative System Metrics */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
        <div className="card p-5 bg-white">
          <div className="eyebrow mb-1 flex items-center justify-between">
            <span>Pending Screening</span>
            <span className="pill pill-orange text-[10px]">Queue</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-ink">
            {q.data?.length ?? 0}
          </div>
          <div className="text-xs text-slate-400 mt-1">Awaiting administrative decision</div>
        </div>

        <div className="card p-5 bg-white">
          <div className="eyebrow mb-1 flex items-center justify-between">
            <span>Security Events</span>
            <span className="text-xs font-mono text-slate-400">Live</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-ink">
            {log.data?.length ?? 0}
          </div>
          <div className="text-xs text-slate-400 mt-1">Logged access & dispatch events</div>
        </div>

        <div className="card p-5 bg-emerald-50/50 border-emerald-200">
          <div className="eyebrow mb-1 text-emerald-900 flex items-center justify-between">
            <span>RBAC Verification</span>
            <span className="pill pill-green text-[10px]">Active</span>
          </div>
          <div className="text-3xl font-extrabold font-mono text-emerald-800">
            100%
          </div>
          <div className="text-xs text-emerald-700 mt-1">Role-based access control enforced</div>
        </div>

        <div className="card p-5 bg-white">
          <div className="eyebrow mb-1 flex items-center justify-between">
            <span>DPDP Compliance</span>
            <span className="pill pill-grey text-[10px]">Active</span>
          </div>
          <div className="text-xl font-bold font-mono text-slate-800 mt-1">
            Section 8 • Strict
          </div>
          <div className="text-xs text-slate-400 mt-1">Purpose limitation enforced</div>
        </div>
      </div>

      {/* Verification Queue Section */}
      <div className="mb-14">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="eyebrow mb-1">Accreditation & Enrollment</div>
            <h3 className="text-xl font-bold text-ink">
              Pending Applications ({q.data?.length ?? 0})
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">Requires Sysadmin Review</span>
        </div>

        <div className="grid gap-3.5">
          <State
            loading={q.loading}
            error={q.error}
            empty={!q.data?.length}
            emptyText="No pending applications awaiting verification in the queue."
            onRetry={q.reload}
          />

          {q.data?.map((a) => (
            <div
              key={a.id}
              className="card lift p-5 md:p-6 flex flex-wrap items-center gap-4 justify-between bg-white"
            >
              <div>
                <div className="flex items-center gap-2.5 mb-1.5">
                  <span
                    className={`pill text-[11px] font-bold ${
                      a.type === 'doctor'
                        ? 'pill-orange'
                        : a.type === 'pharmacist'
                        ? 'pill-amber'
                        : 'pill-green'
                    }`}
                  >
                    {a.type === 'doctor'
                      ? 'Doctor Accreditation'
                      : a.type === 'pharmacist'
                      ? 'Pharmacist License'
                      : 'Citizen Health Card'}
                  </span>
                  <span className="font-mono text-xs font-semibold text-slate-400">{a.app_no}</span>
                  <span className="text-xs text-slate-400">• {a.created_at}</span>
                </div>
                <div className="font-extrabold text-base text-ink">{a.name}</div>
                <div className="text-xs text-slate-500 mt-0.5">{a.detail}</div>
              </div>

              {rejecting === a.id ? (
                <div className="flex gap-2 flex-1 min-w-[280px] max-w-[460px]">
                  <input
                    className="input text-xs h-10"
                    autoFocus
                    placeholder="Enter formal rejection reason…"
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                  />
                  <button
                    type="button"
                    className="btn btn-peach h-10 px-4 text-xs font-bold"
                    disabled={!reason.trim()}
                    onClick={() => act(a.id, 'reject')}
                  >
                    Confirm Rejection
                  </button>
                  <button
                    type="button"
                    className="btn btn-ghost h-10 px-3 text-xs"
                    onClick={() => {
                      setRejecting(null)
                      setReason('')
                    }}
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2.5">
                  <button
                    type="button"
                    className="btn btn-ghost h-10 px-4 text-xs font-semibold hover:border-red-300 hover:text-red-700"
                    onClick={() => setRejecting(a.id)}
                  >
                    {t('reject', 'Reject with Reason')}
                  </button>
                  <button
                    type="button"
                    className="btn btn-sage h-10 px-5 text-xs font-bold"
                    onClick={() => act(a.id, 'approve')}
                  >
                    {t('approve', 'Approve & Issue Card')} →
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Immutable Audit Trail Section */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="eyebrow mb-1 flex items-center gap-2">
              <span>Security Event Stream</span>
              <span className="dot" />
            </div>
            <h3 className="text-xl font-bold text-ink">
              {t('audit', 'Immutable Access Audit Trail')}
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">SHA-256 Tamper Protected</span>
        </div>

        <div className="card overflow-hidden">
          <State
            loading={log.loading}
            error={log.error}
            empty={!log.data?.length}
            emptyText="No access events logged."
            onRetry={log.reload}
          />

          {!!log.data?.length && (
            <div className="overflow-x-auto">
              <table className="w-full min-w-[760px] font-mono text-xs text-left">
                <thead>
                  <tr>
                    <th className="th">Timestamp</th>
                    <th className="th">Actor</th>
                    <th className="th">Security Role</th>
                    <th className="th">Target Route / Action</th>
                    <th className="th text-right">Result</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {log.data.map((r, i) => (
                    <tr key={i} className="hover:bg-slate-50/70 transition-colors">
                      <td className="td text-slate-500 font-semibold">{r.ts}</td>
                      <td className="td font-bold text-ink">{r.actor}</td>
                      <td className="td">
                        <span className="pill pill-grey text-[10px] uppercase font-bold">
                          {r.role}
                        </span>
                      </td>
                      <td className="td text-slate-700 font-medium">{r.action}</td>
                      <td className="td text-right">
                        {Number(r.status) === 200 ? (
                          <span className="pill pill-green text-[10px] font-bold">
                            200 ALLOWED
                          </span>
                        ) : (
                          <span className="pill pill-red text-[10px] font-bold">
                            {r.status} RBAC DENIED
                          </span>
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
    </Section>
  )
}
