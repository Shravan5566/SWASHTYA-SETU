import { useLang } from '../i18n'
import { FullLogo } from '../ui'
import { AuroraCreditCardBento } from '@/components/ui/aurora-credit-card-bento'
import TextBlockAnimation from '@/components/ui/text-block-animation'

const pillars = [
  {
    k: 'p1',
    t: 'Doctor Clinical OPD Suite',
    d: 'Instant QR card scan followed by 6-digit patient authorization OTP. Full medical history, live formulary autocomplete, and drug allergy safety alerts.',
    n: '01',
    go: '#/doctor',
    tag: 'Clinical Care',
  },
  {
    k: 'p2',
    t: 'Pharmacist Isolation Terminal',
    d: 'Strict 4-column isolation: Medicine, dosage, and card ID only. Clinical diagnosis notes and internal doctor records are cryptographically hidden.',
    n: '02',
    go: '#/pharmacist',
    tag: 'Zero Leakage',
  },
  {
    k: 'p3',
    t: 'Public Health Surveillance Radar',
    d: '2-Sigma mathematical disease anomaly detection across 15 Pune wards with differential privacy thresholds.',
    n: '03',
    go: '#/surveillance',
    tag: 'Public Health',
  },
  {
    k: 'p4',
    t: 'Clinical Dossier & Summary',
    d: 'Clinical history summarization and consultation review with patient-controlled OTP authorization.',
    n: '04',
    go: '#/doctor',
    tag: 'Consent-First',
  },
]

export default function Landing() {
  const { t } = useLang()

  return (
    <>
      {/* Hero Section */}
      <section className="max-w-[1240px] mx-auto px-6 md:px-10 pt-10 md:pt-16 pb-16 grid lg:grid-cols-[1.1fr_0.9fr] gap-12 lg:gap-16 items-center">
        <div>
          {/* Institutional Eyebrow */}
          <div className="inline-flex items-center gap-2.5 px-3.5 py-1.5 rounded-full bg-slate-100/90 border border-slate-200/90 text-slate-700 text-xs font-semibold mb-6 shadow-2xs">
            <img src="/sslogo-symbol.png" alt="Swasthya Setu" className="w-5 h-5 object-contain" />
            <span className="font-bold text-ink">Swasthya Setu</span>
            <span className="text-slate-300">•</span>
            <span className="text-slate-600 font-medium">Pune Health Infrastructure</span>
          </div>

          <TextBlockAnimation
            useTricolor={true}
            showLogo={true}
            logoSrc="/sslogo-symbol.png"
            animateOnScroll={true}
            delay={0.15}
            duration={0.65}
            stagger={0.14}
            className="mb-1"
          >
            <h1 className="text-[38px] sm:text-5xl lg:text-[56px] leading-[1.1] font-extrabold tracking-[-0.035em] text-ink">
              {t('hero.h1a', 'Digital Health Identification')}
              <br />
              <span className="text-black font-['Outfit',sans-serif] font-extrabold tracking-[-0.03em]">
                {t('hero.h1b', '& Civic Care Network.')}
              </span>
            </h1>
          </TextBlockAnimation>

          <p className="mt-5 text-base sm:text-lg text-slate-600 max-w-[540px] leading-relaxed">
            {t(
              'hero.sub',
              'A unified digital health infrastructure connecting citizens, healthcare practitioners, and public health surveillance across Pune wards with patient-governed consent.'
            )}
          </p>

          <div className="mt-8 flex flex-wrap gap-3.5 items-center">
            <a href="#/apply" className="btn btn-saffron text-[15px] h-12 px-6 shadow-sm">
              {t('cta.apply', 'Apply for Digital Health Card')} →
            </a>
            <a href="#/track" className="btn btn-outline-green text-[15px] h-12 px-6">
              {t('cta.track', 'Track Application Status')}
            </a>
          </div>

          {/* Infrastructure Capability Highlights */}
          <div className="mt-10 pt-6 border-t border-slate-100 grid grid-cols-3 gap-4 max-w-[520px]">
            <div>
              <div className="text-xs font-bold text-ink flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                15 Wards
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">Surveillance Grid</div>
            </div>
            <div>
              <div className="text-xs font-bold text-ink flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-orange-500" />
                Consent OTP
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">Patient Governed</div>
            </div>
            <div>
              <div className="text-xs font-bold text-ink flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                QR ID
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">Instant Check-in</div>
            </div>
          </div>
        </div>

        {/* Sovereign Smart Card Bento Experience */}
        <div className="flex flex-col items-center lg:items-end w-full max-w-[430px] mx-auto lg:ml-auto">
          <AuroraCreditCardBento
            title={
              <div className="space-y-1">
                <span className="text-[1.35rem] font-extrabold tracking-tight text-white block">
                  Digital Health Card
                </span>
                <span className="text-xs font-mono tracking-wider text-orange-400 font-semibold block uppercase">
                  Swasthya Setu Platform
                </span>
              </div>
            }
            brand="none"
            brandMark={
              <div className="flex items-center gap-2 bg-slate-950/80 backdrop-blur-md px-2.5 py-1.5 rounded-xl border border-white/15 shadow-sm">
                <img
                  src="/sslogo-symbol.png"
                  alt="Swasthya Setu Emblem"
                  className="w-5 h-5 object-contain"
                />
                <div className="leading-none text-left">
                  <div className="text-[10px] font-extrabold tracking-tight text-white uppercase font-sans">
                    Swasthya Setu
                  </div>
                  <div className="text-[7.5px] font-mono tracking-widest text-slate-400 uppercase font-semibold">
                    SECURE QR ID
                  </div>
                </div>
              </div>
            }
            color1="#ea580c"
            color2="#f97316"
            color3="#10b981"
            color4="#047857"
            color5="#0b192c"
            color6="#f59e0b"
            glow="#ea580c"
            highlight="rgba(255, 255, 255, 0.95)"
            tilt={18}
            float={true}
            onClick={() => {
              window.location.hash = '#/apply'
            }}
            className="border border-slate-800/90 shadow-2xl bg-gradient-to-b from-[#0e1726] to-[#070b12]"
          />
        </div>
      </section>

      {/* Pillars Section */}
      <section className="max-w-[1240px] mx-auto px-6 md:px-10 pb-24">
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="eyebrow mb-1">{t('pillars', 'Core Platform Architecture')}</div>
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-ink">
              Built for Medical Privacy & Fast Consultations
            </h2>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {pillars.map((p) => (
            <a
              key={p.k}
              href={p.go}
              className="card lift p-8 md:p-9 block bg-white hover:bg-slate-50/50 relative overflow-hidden group"
            >
              <div className="flex items-center justify-between mb-6">
                <span className="font-mono text-sm font-extrabold text-saffron tracking-wider bg-orange-50 px-2.5 py-1 rounded-md border border-orange-200/60">
                  {p.n}
                </span>
                <span className="pill pill-grey text-[11px] font-mono group-hover:border-slate-300">
                  {p.tag}
                </span>
              </div>
              <h3 className="text-xl font-bold tracking-tight text-ink mb-2.5 group-hover:text-orange-600 transition-colors">
                {t(p.k + '.t', p.t)}
              </h3>
              <p className="text-slate-600 text-sm leading-relaxed">{t(p.k + '.d', p.d)}</p>
              <div className="mt-6 flex items-center text-xs font-semibold text-saffron gap-1 group-hover:gap-2 transition-all">
                <span>Enter Terminal</span>
                <span>→</span>
              </div>
            </a>
          ))}
        </div>
      </section>

      {/* Sovereign Authority Banner with Full Logo */}
      <section className="bg-gradient-to-r from-orange-50/70 via-white to-emerald-50/70 border-y border-slate-200/90 py-12">
        <div className="max-w-[1240px] mx-auto px-6 md:px-10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex flex-col sm:flex-row items-center sm:items-start text-center sm:text-left gap-6">
            <div className="p-3 bg-white rounded-2xl border border-slate-200/90 shadow-sm shrink-0">
              <FullLogo height={58} />
            </div>
            <div>
              <h3 className="text-xl font-bold text-ink">
                Swasthya Setu Digital Health Infrastructure
              </h3>
              <p className="text-sm text-slate-600 max-w-xl mt-1.5 leading-relaxed">
                A unified platform providing citizen QR health identities, cryptographically isolated clinical consultation, and real-time public health surveillance.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <a href="#/apply" className="btn btn-saffron text-sm px-5 py-2.5">
              Issue My Health Card
            </a>
            <a href="#/surveillance" className="btn btn-outline-green text-sm px-5 py-2.5">
              Surveillance Radar
            </a>
          </div>
        </div>
      </section>
    </>
  )
}
