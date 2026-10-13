import { useLang } from '../i18n'
import { FullLogo } from '../ui'
import Royal3DCard from '@/components/ui/royal-3d-card'
import TextBlockAnimation from '@/components/ui/text-block-animation'
import { FlowButton } from '@/components/ui/flow-button'
import SpotlightCard from '@/components/ui/SpotlightCard'

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
    d: '2-Sigma mathematical disease anomaly detection across 15 Pune wards with minimum group-size privacy thresholds (k ≥ 5).',
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
  const { lang, t } = useLang()

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
            <span className="text-slate-600 font-medium">{t('pmc.tag', 'Pune Health Infrastructure')}</span>
          </div>

          <TextBlockAnimation
            key={lang}
            restartKey={lang}
            useTricolor={true}
            showLogo={true}
            logoSrc="/sslogo-symbol.png"
            animateOnScroll={true}
            delay={0.15}
            duration={0.65}
            stagger={0.14}
            className="mb-1"
          >
            <h1
              className={`text-[36px] sm:text-5xl lg:text-[54px] font-extrabold text-ink ${
                lang === 'mr'
                  ? 'leading-[1.32] tracking-normal font-["Baloo_2","Mukta",sans-serif]'
                  : 'leading-[1.1] tracking-[-0.035em]'
              }`}
            >
              {t('hero.h1a', 'Digital Health Identification')}
              <br />
              <span
                className={`text-black font-extrabold ${
                  lang === 'mr'
                    ? 'font-["Baloo_2","Mukta",sans-serif] tracking-normal'
                    : 'font-["Outfit",sans-serif] tracking-[-0.03em]'
                }`}
              >
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
            <FlowButton href="#/apply" className="btn btn-saffron text-[15px] h-12 px-6 shadow-sm">
              {t('cta.apply', 'Apply for Digital Health Card')} →
            </FlowButton>
            <FlowButton href="#/track" className="btn btn-outline-green text-[15px] h-12 px-6">
              {t('cta.track', 'Track Application Status')}
            </FlowButton>
          </div>

          {/* Infrastructure Capability Highlights */}
          <div className="mt-10 pt-6 border-t border-slate-100 grid grid-cols-3 gap-4 max-w-[520px]">
            <div>
              <div className="text-xs font-bold text-ink flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500" />
                {t('stat.wards', '15 Wards')}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">{t('stat.wards.sub', 'Surveillance Grid')}</div>
            </div>
            <div>
              <div className="text-xs font-bold text-ink flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-orange-500" />
                {t('stat.otp', 'Consent OTP')}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">{t('stat.otp.sub', 'Patient Governed')}</div>
            </div>
            <div>
              <div className="text-xs font-bold text-ink flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-blue-500" />
                {t('stat.qr', 'QR ID')}
              </div>
              <div className="text-[11px] text-slate-500 mt-0.5">{t('stat.qr.sub', 'Instant Check-in')}</div>
            </div>
          </div>
        </div>

        {/* Royal 3D Health Card Experience */}
        <div className="flex flex-col items-center lg:items-end w-full max-w-[420px] mx-auto lg:ml-auto">
          <Royal3DCard
            imageSrc="/royal-health-card.png"
            onClick={() => {
              window.location.hash = '#/apply'
            }}
          />
        </div>
      </section>

      {/* Pillars Section */}
      <section className="max-w-[1240px] mx-auto px-6 md:px-10 pb-24">
        <div className="flex items-center justify-between mb-8">
          <div>
            <div className="eyebrow mb-1">{t('pillars', 'Core Platform Architecture')}</div>
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight text-ink">
              {t('pillars.h2', 'Built for Medical Privacy & Fast Consultations')}
            </h2>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          {pillars.map((p) => (
            <SpotlightCard
              key={p.k}
              as="a"
              href={p.go}
              theme="light"
              spotlightColor="#ec995f"
              intensity={0.4}
              spotlightSize={260}
              softness={0.7}
              shape="circle"
              borderGlow={0.65}
              proximity={80}
              smoothing={0.25}
              grain={0}
              ambient={false}
              flare={true}
              className="p-8 md:p-9 block relative group no-underline text-inherit cursor-pointer transition-transform duration-200 hover:-translate-y-1"
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
                <span>{t('enter.terminal', 'Enter Terminal')}</span>
                <span>→</span>
              </div>
            </SpotlightCard>
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
            <FlowButton href="#/apply" className="btn btn-saffron text-sm px-5 py-2.5">
              Issue My Health Card
            </FlowButton>
            <FlowButton href="#/surveillance" className="btn btn-outline-green text-sm px-5 py-2.5">
              Surveillance Radar
            </FlowButton>
          </div>
        </div>
      </section>
    </>
  )
}
