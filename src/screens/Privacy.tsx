import { useLang } from '../i18n'
import { Section } from '../ui'

export default function Privacy() {
  const { t } = useLang()

  const protections = [
    {
      num: '01',
      title: 'Ephemeral Patient OTP Consent',
      desc: 'No clinical doctor or hospital staff can unlock a patient history without an active 6-digit SMS OTP authorized by the citizen in real-time. Consent tokens automatically expire after 60 minutes.',
      pill: 'Section 6 • Consent Architecture',
    },
    {
      num: '02',
      title: 'Pharmacist Cryptographic Isolation',
      desc: 'Dispensing terminals operate on strict 4-column isolation (Card ID, Date, Medicine, Dosage). Doctor diagnosis notes, clinical observations, and history are mathematically suppressed from pharmacy queries.',
      pill: 'Section 8 • Purpose Limitation',
    },
    {
      num: '03',
      title: 'Minimum Group-Size Privacy (k ≥ 5)',
      desc: 'Epidemiological outbreak detection enforces a minimum cohort threshold (k ≥ 5 distinct patients). Small sample sizes are suppressed to prevent re-identification of citizens in specific wards.',
      pill: 'Section 4 • Anonymized Statistics',
    },
    {
      num: '04',
      title: 'Role-Based Data Partitioning',
      desc: 'Personally identifiable information is decoupled from medical histories and protected by role-based access control. Practitioners only access relevant clinical records upon active citizen authorization.',
      pill: 'Technical Safeguards',
    },
  ]

  return (
    <Section
      eyebrow="Compliance & Governance"
      title="Digital Personal Data Protection (DPDP) Principles"
      right={
        <span className="pill pill-green">
          <span className="dot" />
          Privacy-First Design
        </span>
      }
    >
      <div className="max-w-[960px] mx-auto">
        <div className="card p-8 md:p-10 mb-10 bg-gradient-to-br from-emerald-50/60 to-white border-emerald-200/80">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-2 bg-white rounded-xl border border-emerald-200 shadow-2xs shrink-0">
              <img src="/sslogo-symbol.png" alt="Swasthya Setu" className="w-10 h-10 object-contain" />
            </div>
            <div>
              <h2 className="text-xl md:text-2xl font-extrabold text-ink tracking-tight">
                Data Protection & Privacy Architecture
              </h2>
              <span className="text-[10px] font-mono tracking-wider text-emerald-800 font-bold uppercase">
                Swasthya Setu • Privacy by Design
              </span>
            </div>
          </div>
          <p className="text-slate-600 leading-relaxed text-base">
            The Swasthya Setu platform is designed to uphold the core principles of
            the Digital Personal Data Protection (DPDP) Act 2023. By decoupling identity tokens,
            enforcing ephemeral patient-controlled OTP access, and cryptographically isolating clinical
            roles, the system ensures medical data is shared only for direct care delivery.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-5 mb-12">
          {protections.map((p) => (
            <div key={p.num} className="card p-7 lift bg-white flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between mb-4">
                  <span className="font-mono text-xs font-bold text-saffron tracking-wider">{p.num}</span>
                  <span className="pill pill-grey text-[11px] font-mono">{p.pill}</span>
                </div>
                <h3 className="text-lg font-bold text-ink mb-2.5">{p.title}</h3>
                <p className="text-slate-600 text-sm leading-relaxed">{p.desc}</p>
              </div>
            </div>
          ))}
        </div>

        <div className="card p-8 bg-slate-50 border-slate-200 flex flex-wrap items-center justify-between gap-6">
          <div>
            <h4 className="font-bold text-ink mb-1">Swasthya Setu Privacy & Support</h4>
            <p className="text-xs text-slate-500">
              For privacy inquiries, account data deletion, or access control questions, contact the support desk.
            </p>
          </div>
          <a
            href="mailto:support@swasthyasetu.org"
            className="btn btn-ghost text-xs font-mono font-bold"
          >
            support@swasthyasetu.org
          </a>
        </div>
      </div>
    </Section>
  )
}
