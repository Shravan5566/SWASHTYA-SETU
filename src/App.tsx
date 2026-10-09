import type React from 'react'
import { useEffect, useState } from 'react'
import { LangProvider, useLang } from './i18n'
import { FullLogo, Logo } from './ui'
import { post } from './api'
import Landing from './screens/Landing'
import Apply, { Track } from './screens/Apply'
import Doctor from './screens/Doctor'
import Pharmacist from './screens/Pharmacist'
import Surveillance from './screens/Surveillance'
import Admin from './screens/Admin'
import Privacy from './screens/Privacy'
import Frames, {
  ApplyFrame,
  StatusFrame,
  LoginFrame,
  ScanFrame,
  CheckupFrame,
  DispenseFrame,
} from './screens/Frames'

const routes: Record<string, () => React.ReactNode> = {
  '': Landing,
  apply: Apply,
  track: Track,
  doctor: Doctor,
  pharmacist: Pharmacist,
  surveillance: Surveillance,
  admin: Admin,
  privacy: Privacy,
  frames: Frames,
  'apply/health-card': ApplyFrame,
  'apply/status': StatusFrame,
  login: LoginFrame,
  'doctor/scan': ScanFrame,
  'doctor/patient/add-checkup': CheckupFrame,
  'pharmacist/medicines': DispenseFrame,
}

const staffAccounts = [
  { role: 'doctor', name: 'Dr. Aisha Verma', username: 'doctor_demo', title: 'Senior Medical Officer', route: '#/doctor' },
  { role: 'pharmacist', name: 'Rahul Patel, R.Ph', username: 'pharma_demo', title: 'Chief Pharmacist', route: '#/pharmacist' },
  { role: 'public_health', name: 'Priya Nair, MPH', username: 'public_demo', title: 'Chief Epidemiologist', route: '#/surveillance' },
  { role: 'admin', name: 'Vikram Rao', username: 'admin_demo', title: 'Lead Security Director', route: '#/admin' },
]

function Shell() {
  const { lang, setLang, t } = useLang()
  const [route, setRoute] = useState(location.hash.replace('#/', ''))
  const [menu, setMenu] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(null)

  useEffect(() => {
    const handleHash = () => {
      setRoute(location.hash.replace('#/', ''))
      setMenu(false)
      window.scrollTo(0, 0)
    }
    window.addEventListener('hashchange', handleHash)
    return () => window.removeEventListener('hashchange', handleHash)
  }, [])

  const quickLogin = async (username: string, targetRoute: string) => {
    try {
      const res = await post('/api/auth/login', { username, password: 'password123' })
      setCurrentUser(res.user)
      location.hash = targetRoute
      setMenu(false)
    } catch {
      location.hash = targetRoute
      setMenu(false)
    }
  }

  const Page = routes[route] ?? Landing

  const links: [string, string, string][] = [
    ['#/apply', 'nav.apply', 'Apply for Health Card'],
    ['#/track', 'nav.track', 'Track Status'],
    ['#/surveillance', 'nav.network', 'Surveillance Radar'],
    ['#/privacy', 'nav.privacy', 'DPDP Privacy'],
  ]

  return (
    <div className="min-h-screen bg-white text-ink flex flex-col font-sans">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/90 shadow-2xs">
        <div className="max-w-[1240px] mx-auto px-6 md:px-10 h-[74px] flex items-center justify-between gap-4">
          {/* Logo & Civic Branding */}
          <a href="#/" className="flex items-center gap-3">
            <Logo />
          </a>

          {/* Desktop Navigation */}
          <nav className="hidden lg:flex items-center gap-7 text-sm font-semibold text-slate-600">
            {links.map(([h, k, fallback]) => {
              const active = `#/${route}` === h || (h === '#/' && !route)
              return (
                <a
                  key={h}
                  href={h}
                  className={`transition-colors py-1 border-b-2 ${
                    active
                      ? 'text-orange-600 border-orange-500 font-bold'
                      : 'border-transparent hover:text-ink'
                  }`}
                >
                  {t(k, fallback)}
                </a>
              )
            })}
          </nav>

          {/* Right Toolbar: Lang Switcher & Staff Login */}
          <div className="flex items-center gap-3">
            {/* Language Switcher */}
            <div className="flex border border-slate-200 rounded-full p-0.5 text-xs font-bold bg-slate-50">
              {(['en', 'mr'] as const).map((l) => (
                <button
                  key={l}
                  type="button"
                  aria-pressed={lang === l}
                  onClick={() => setLang(l)}
                  className={`px-2.5 h-7 rounded-full transition-all cursor-pointer ${
                    lang === l ? 'bg-ink text-white shadow-xs' : 'text-slate-500 hover:text-ink'
                  }`}
                >
                  {l === 'en' ? 'EN' : 'मराठी'}
                </button>
              ))}
            </div>

            {/* Staff Dropdown Menu */}
            <div className="relative">
              <button
                type="button"
                className="btn btn-ghost h-9 px-3.5 text-xs font-bold border-slate-300"
                onClick={() => setMenu(!menu)}
              >
                <span>{currentUser ? currentUser.full_name.split(' ')[0] : t('nav.staff', 'Staff Login')}</span>
                <span className="text-[10px]">▾</span>
              </button>

              {menu && (
                <div className="absolute right-0 mt-2 w-64 bg-white border border-slate-200 rounded-2xl shadow-xl p-2 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                  <div className="px-3 py-2 border-b border-slate-100 text-[11px] font-mono text-slate-400 font-bold uppercase tracking-wider">
                    One-Click Practitioner Logins
                  </div>
                  <div className="grid gap-1 mt-1">
                    {staffAccounts.map((s) => (
                      <button
                        key={s.username}
                        type="button"
                        onClick={() => quickLogin(s.username, s.route)}
                        className="w-full text-left px-3 py-2.5 rounded-xl text-xs hover:bg-slate-50 transition-colors flex flex-col cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-ink">{s.name}</span>
                          <span className="pill pill-grey text-[9px] uppercase font-mono">{s.role}</span>
                        </div>
                        <span className="text-[10px] text-slate-400 mt-0.5">{s.title}</span>
                      </button>
                    ))}
                  </div>
                  <div className="pt-2 mt-1 border-t border-slate-100 flex items-center justify-between px-2 text-[10px] text-slate-400">
                    <span>Default Pass: password123</span>
                    <a href="#/frames" className="text-orange-600 font-semibold hover:underline">
                      UI Frames →
                    </a>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1">
        <Page />
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-200/90 bg-slate-50/70 py-12 text-slate-500 text-xs">
        <div className="max-w-[1240px] mx-auto px-6 md:px-10 flex flex-wrap items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <FullLogo height={44} />
          </div>

          <div className="flex flex-wrap items-center gap-6 text-xs font-semibold">
            <a href="#/apply" className="hover:text-ink">Apply for Card</a>
            <a href="#/track" className="hover:text-ink">Track Status</a>
            <a href="#/doctor" className="hover:text-ink">OPD Suite</a>
            <a href="#/pharmacist" className="hover:text-ink">Pharmacy</a>
            <a href="#/surveillance" className="hover:text-ink">Surveillance Radar</a>
            <a href="#/privacy" className="hover:text-ink">Data Privacy</a>
            <a href="#/admin" className="hover:text-ink">Sysadmin</a>
          </div>

          <div className="text-right flex flex-col gap-0.5">
            <span className="font-mono text-[11px] font-bold text-slate-600">
              SWASTHYA SETU HEALTH PLATFORM
            </span>
            <span className="text-[10px] text-slate-400">
              Digital Health Identity • Built with Privacy by Design
            </span>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default function App() {
  return (
    <LangProvider>
      <Shell />
    </LangProvider>
  )
}
