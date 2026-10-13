import type React from 'react'
import { useEffect, useState } from 'react'
import { LangProvider, useLang } from './i18n'
import { FullLogo, Logo } from './ui'
import { api, post } from './api'
import Landing from './screens/Landing'
import Apply, { Track } from './screens/Apply'
import Doctor from './screens/Doctor'
import Pharmacist from './screens/Pharmacist'
import Surveillance from './screens/Surveillance'
import Admin from './screens/Admin'
import Privacy from './screens/Privacy'
import {
  CreditCard,
  Search,
  Stethoscope,
  Pill,
  Radio,
  Shield,
  ShieldCheck,
} from 'lucide-react'
import { MenuBar, MenuItemConfig } from '@/components/ui/animated-menu-bar'
import MetallicPaint from '@/components/ui/MetallicPaint'
import Frames, {
  ApplyFrame,
  StatusFrame,
  LoginFrame,
  ScanFrame,
  CheckupFrame,
  DispenseFrame,
} from './screens/Frames'

interface RoleGateProps {
  requiredRole: 'doctor' | 'pharmacist' | 'public_health' | 'admin'
  roleTitle: string
  roleIcon: string
  roleDescription: string
  testCredentials: { user: string; pass: string; name: string }
  currentUser: any
  onOpenLogin: (presetUser?: string) => void
  children: React.ReactNode
}

function RoleGate({
  requiredRole,
  roleTitle,
  roleIcon,
  roleDescription,
  testCredentials,
  currentUser,
  onOpenLogin,
  children,
}: RoleGateProps) {
  const roleAliases: Record<string, string[]> = {
    doctor: ['doctor'],
    pharmacist: ['pharmacist'],
    public_health: ['public_health', 'public_health_admin'],
    admin: ['admin', 'sysadmin'],
  }

  const allowedRoles = roleAliases[requiredRole] || [requiredRole]
  const userRole = (currentUser?.role || '').toLowerCase()
  const isAuthorized = currentUser && allowedRoles.includes(userRole)

  // 1. Not Authenticated -> Show Institutional Access Gate
  if (!currentUser) {
    return (
      <div className="max-w-[760px] mx-auto px-6 py-14 animate-in fade-in duration-200">
        <div className="card p-8 md:p-12 bg-white border-slate-200 shadow-xl text-center">
          <div className="w-16 h-16 rounded-2xl bg-orange-50 border border-orange-200 flex items-center justify-center text-3xl mx-auto mb-5 shadow-xs">
            {roleIcon}
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 font-mono text-xs font-bold mb-3">
            <span>🔒 Institutional Authorization Required</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-ink mb-3">
            {roleTitle} Terminal Access
          </h2>
          <p className="text-slate-600 text-sm max-w-[560px] mx-auto mb-7 leading-relaxed">
            {roleDescription} Under the Digital Personal Data Protection (DPDP) Act 2023, access across healthcare, pharmacy, surveillance, and administrative tiers is strictly segregated.
          </p>

          {/* Institutional Test Credentials Quick Card */}
          <div className="bg-slate-50 border border-slate-200 rounded-2xl p-5 max-w-[460px] mx-auto mb-8 text-left">
            <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2.5 flex items-center justify-between">
              <span>Accredited Demonstration Credentials</span>
              <span className="pill pill-grey font-mono text-[9px]">Active</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono mb-2">
              <span className="text-slate-500">Designated Official:</span>
              <span className="font-bold text-ink">{testCredentials.name}</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono mb-2">
              <span className="text-slate-500">Username:</span>
              <span className="font-bold text-orange-600 bg-orange-50 px-2 py-0.5 rounded border border-orange-200/60">{testCredentials.user}</span>
            </div>
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-slate-500">Password:</span>
              <span className="font-bold text-slate-700 bg-white border border-slate-200 px-2 py-0.5 rounded">{testCredentials.pass}</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <button
              type="button"
              className="btn btn-saffron h-12 px-8 text-sm font-bold text-white shadow-sm"
              onClick={() => onOpenLogin(testCredentials.user)}
            >
              Sign In as {roleTitle} →
            </button>
            <a href="#/" className="btn btn-ghost h-12 px-6 text-sm font-semibold">
              Return to Citizen Portal
            </a>
          </div>
        </div>
      </div>
    )
  }

  // 2. Authenticated with WRONG role -> Show Provable 403 Access Denied Shield
  if (!isAuthorized) {
    return (
      <div className="max-w-[760px] mx-auto px-6 py-14 animate-in fade-in duration-200">
        <div className="card p-8 md:p-12 bg-white border-red-200 shadow-xl text-center">
          <div className="w-16 h-16 rounded-2xl bg-red-50 border border-red-200 flex items-center justify-center text-3xl mx-auto mb-5 shadow-xs">
            🛡️
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-50 text-red-800 font-mono text-xs font-bold mb-3 border border-red-200">
            <span>⛔ HTTP 403 Forbidden • Role Authorization Failed</span>
          </div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-ink mb-3">
            Access Prohibited by DPDP Privacy Firewall
          </h2>
          <p className="text-slate-600 text-sm max-w-[580px] mx-auto mb-5 leading-relaxed">
            You are currently signed in as <strong className="text-ink">{currentUser.full_name}</strong> (<code className="font-mono text-orange-600">@{currentUser.username}</code>) with role <span className="pill pill-grey font-mono uppercase text-xs font-bold">{currentUser.role}</span>.
          </p>
          <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200/80 text-amber-900 text-xs max-w-[540px] mx-auto mb-8 leading-relaxed text-left">
            <strong>Mandatory Purpose Limitation & Role Separation:</strong> This portal requires <strong>{roleTitle}</strong> credentials. Administrators cannot view clinical records, clinicians cannot administer systems, and pharmacists cannot access diagnostic charts.
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3">
            <button
              type="button"
              className="btn btn-saffron h-12 px-6 text-sm font-bold text-white"
              onClick={() => onOpenLogin(testCredentials.user)}
            >
              Switch Account (Login as {roleTitle})
            </button>
            <a
              href={
                currentUser.role === 'doctor'
                  ? '#/doctor'
                  : currentUser.role === 'pharmacist'
                  ? '#/pharmacist'
                  : ['admin', 'sysadmin'].includes(currentUser.role)
                  ? '#/admin'
                  : '#/surveillance'
              }
              className="btn btn-ghost h-12 px-6 text-sm font-semibold"
            >
              Back to Your Authorized Terminal
            </a>
          </div>
        </div>
      </div>
    )
  }

  // 3. Authorized -> Render Protected Portal
  return <>{children}</>
}

function Shell() {
  const { lang, setLang, t } = useLang()
  const [route, setRoute] = useState(location.hash.replace('#/', ''))
  const [menu, setMenu] = useState(false)
  const [loginModal, setLoginModal] = useState(false)
  const [currentUser, setCurrentUser] = useState<any>(() => {
    try {
      const stored = localStorage.getItem('swasthya_setu_user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [authErr, setAuthErr] = useState('')
  const [loggingIn, setLoggingIn] = useState(false)

  useEffect(() => {
    const handleHash = () => {
      setRoute(location.hash.replace('#/', ''))
      setMenu(false)
      window.scrollTo(0, 0)
    }
    window.addEventListener('hashchange', handleHash)
    return () => window.removeEventListener('hashchange', handleHash)
  }, [])

  // Restore authenticated session on load & sync with server
  useEffect(() => {
    api('/api/auth/me')
      .then((res) => {
        if (res?.authenticated && res.user) {
          setCurrentUser(res.user)
          try {
            localStorage.setItem('swasthya_setu_user', JSON.stringify(res.user))
          } catch {}
        } else if (res && res.authenticated === false) {
          // Explicit logout from server
          setCurrentUser(null)
          try {
            localStorage.removeItem('swasthya_setu_user')
          } catch {}
        }
      })
      .catch(() => {
        // Network offline or momentary interruption: retain existing authenticated state
      })
  }, [])

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim() || !password.trim()) {
      setAuthErr('Please provide both username and password.')
      return
    }
    setAuthErr('')
    setLoggingIn(true)
    try {
      const res = await post('/api/auth/login', { username: username.trim(), password })
      setCurrentUser(res.user)
      try {
        localStorage.setItem('swasthya_setu_user', JSON.stringify(res.user))
      } catch {}
      setLoginModal(false)
      setUsername('')
      setPassword('')
      if (res.user.role === 'doctor') location.hash = '#/doctor'
      else if (res.user.role === 'pharmacist') location.hash = '#/pharmacist'
      else if (res.user.role === 'public_health' || res.user.role === 'public_health_admin') location.hash = '#/surveillance'
      else if (res.user.role === 'admin' || res.user.role === 'sysadmin') location.hash = '#/admin'
    } catch (err: any) {
      setAuthErr(err.message || 'Authentication failed. Please verify credentials.')
    } finally {
      setLoggingIn(false)
    }
  }

  const handleLogout = async () => {
    try {
      await post('/api/auth/logout')
    } catch {}
    try {
      localStorage.removeItem('swasthya_setu_user')
      sessionStorage.removeItem('swasthya_setu_user')
    } catch {}
    setCurrentUser(null)
    setMenu(false)
    location.hash = '#/'
  }

  const openLoginForRole = (presetUser?: string) => {
    if (presetUser) setUsername(presetUser)
    setPassword('password123')
    setAuthErr('')
    setLoginModal(true)
  }

  const renderPage = () => {
    switch (route) {
      case '':
        return <Landing />
      case 'apply':
        return <Apply />
      case 'track':
        return <Track />
      case 'privacy':
        return <Privacy />
      case 'doctor':
        return (
          <RoleGate
            requiredRole="doctor"
            roleTitle="Doctor"
            roleIcon="🩺"
            roleDescription="Access the clinical OPD Suite, scan patient QR cards, obtain OTP verification consent, and record diagnostic checkups."
            testCredentials={{
              user: 'doctor_demo',
              pass: 'password123',
              name: 'Dr. Rajesh Kulkarni, MD (Senior Medical Officer)',
            }}
            currentUser={currentUser}
            onOpenLogin={openLoginForRole}
          >
            <Doctor currentUser={currentUser} />
          </RoleGate>
        )
      case 'pharmacist':
        return (
          <RoleGate
            requiredRole="pharmacist"
            roleTitle="Pharmacist"
            roleIcon="💊"
            roleDescription="Access the isolated medication dispensing desk, verify prescribed medicines, and enforce single-dispense refill controls."
            testCredentials={{
              user: 'pharma_demo',
              pass: 'password123',
              name: 'Ramesh Kadam, R.Ph (Lead Clinical Pharmacist)',
            }}
            currentUser={currentUser}
            onOpenLogin={openLoginForRole}
          >
            <Pharmacist />
          </RoleGate>
        )
      case 'surveillance':
        return (
          <RoleGate
            requiredRole="public_health"
            roleTitle="Public Health Administrator"
            roleIcon="📊"
            roleDescription="Inspect municipal epidemiological radars, anonymized trend statistics (k>=5 privacy suppression), and 2-sigma outbreak alerts."
            testCredentials={{
              user: 'public_demo',
              pass: 'password123',
              name: 'Dr. Meenakshi Sundaram, MD, MPH (Chief Epidemiologist)',
            }}
            currentUser={currentUser}
            onOpenLogin={openLoginForRole}
          >
            <Surveillance />
          </RoleGate>
        )
      case 'admin':
        return (
          <RoleGate
            requiredRole="admin"
            roleTitle="System Administrator"
            roleIcon="🛡️"
            roleDescription="Review pending health card applications, issue citizen credentials, and verify append-only audit trail logs. (Forbidden from clinical records)."
            testCredentials={{
              user: 'admin_demo',
              pass: 'password123',
              name: 'Director V. K. Raman (Lead Healthcare Systems Security Officer)',
            }}
            currentUser={currentUser}
            onOpenLogin={openLoginForRole}
          >
            <Admin />
          </RoleGate>
        )
      case 'frames':
        return <Frames />
      case 'apply/health-card':
        return <ApplyFrame />
      case 'apply/status':
        return <StatusFrame />
      case 'login':
        return <LoginFrame />
      case 'doctor/scan':
        return <ScanFrame />
      case 'doctor/patient/add-checkup':
        return <CheckupFrame />
      case 'pharmacist/medicines':
        return <DispenseFrame />
      default:
        return <Landing />
    }
  }

  const currentNavKey = route.split('/')[0] || ''

  const headerDockItems: MenuItemConfig<string>[] = [
    {
      key: 'apply',
      label: t('nav.apply_short', 'Apply'),
      icon: <CreditCard className="w-4 h-4" strokeWidth={1.8} />,
    },
    {
      key: 'track',
      label: t('nav.track_short', 'Track'),
      icon: <Search className="w-4 h-4" strokeWidth={1.8} />,
    },
    {
      key: 'doctor',
      label: t('nav.opd_short', 'Doctor OPD'),
      icon: <Stethoscope className="w-4 h-4" strokeWidth={1.8} />,
    },
    {
      key: 'pharmacist',
      label: t('nav.pharma_short', 'Pharmacy'),
      icon: <Pill className="w-4 h-4" strokeWidth={1.8} />,
    },
    {
      key: 'surveillance',
      label: t('nav.network_short', 'Surveillance'),
      icon: <Radio className="w-4 h-4" strokeWidth={1.8} />,
    },
    {
      key: 'admin',
      label: t('nav.admin_short', 'Admin'),
      icon: <Shield className="w-4 h-4" strokeWidth={1.8} />,
    },
    {
      key: 'privacy',
      label: t('nav.privacy_short', 'DPDP Privacy'),
      icon: <ShieldCheck className="w-4 h-4" strokeWidth={1.8} />,
    },
  ]

  return (
    <div className="min-h-screen bg-white text-ink flex flex-col font-sans">
      {/* Top Header */}
      <header className="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200/80 shadow-2xs">
        <div className="max-w-[1400px] mx-auto px-4 md:px-8 h-[74px] flex items-center justify-between gap-4">
          {/* Logo & Civic Branding */}
          <a href="#/" className="flex items-center gap-3 shrink-0">
            <Logo />
          </a>

          {/* Top iOS Frosted Glass Dock Navigation */}
          <div className="hidden lg:flex items-center justify-center">
            <MenuBar<string>
              active={currentNavKey}
              onSelect={(k) => {
                window.location.hash = `#/${k}`
              }}
              items={headerDockItems}
              size="sm"
            />
          </div>

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

            {/* Staff Authentication & Session Menu */}
            <div className="relative">
              {currentUser ? (
                <div>
                  <button
                    type="button"
                    className="btn btn-ghost h-9 px-3.5 text-xs font-bold border-slate-300 flex items-center gap-2 cursor-pointer"
                    onClick={() => setMenu(!menu)}
                  >
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span>{currentUser.full_name?.split(' ')[0] || currentUser.username}</span>
                    <span className="pill pill-grey text-[9px] uppercase font-mono">{currentUser.role}</span>
                    <span className="text-[10px]">▾</span>
                  </button>

                  {menu && (
                    <div className="absolute right-0 mt-2 w-64 bg-white border border-slate-200 rounded-2xl shadow-xl p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
                      <div className="px-2 py-1.5 border-b border-slate-100">
                        <div className="text-xs font-bold text-ink">{currentUser.full_name}</div>
                        <div className="text-[10px] text-slate-400 font-mono">@{currentUser.username} · {currentUser.role?.toUpperCase()}</div>
                      </div>
                      <div className="grid gap-1 mt-2">
                        {currentUser.role === 'doctor' && (
                          <a href="#/doctor" onClick={() => setMenu(false)} className="px-3 py-2 text-xs font-semibold rounded-lg hover:bg-slate-50 flex items-center gap-2 text-slate-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-orange-500" />
                            Doctor OPD Suite
                          </a>
                        )}
                        {currentUser.role === 'pharmacist' && (
                          <a href="#/pharmacist" onClick={() => setMenu(false)} className="px-3 py-2 text-xs font-semibold rounded-lg hover:bg-slate-50 flex items-center gap-2 text-slate-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
                            Pharmacy Dispense Desk
                          </a>
                        )}
                        {(currentUser.role === 'public_health' || currentUser.role === 'public_health_admin') && (
                          <a href="#/surveillance" onClick={() => setMenu(false)} className="px-3 py-2 text-xs font-semibold rounded-lg hover:bg-slate-50 flex items-center gap-2 text-slate-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                            Disease Surveillance Radar
                          </a>
                        )}
                        {(currentUser.role === 'admin' || currentUser.role === 'sysadmin') && (
                          <a href="#/admin" onClick={() => setMenu(false)} className="px-3 py-2 text-xs font-semibold rounded-lg hover:bg-slate-50 flex items-center gap-2 text-slate-700">
                            <span className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                            System Admin Console
                          </a>
                        )}
                        <button
                          type="button"
                          onClick={handleLogout}
                          className="w-full text-left px-3 py-2 text-xs font-semibold rounded-lg hover:bg-red-50 text-red-600 flex items-center gap-2 cursor-pointer mt-1 border-t border-slate-100 pt-2"
                        >
                          <span className="w-1.5 h-1.5 rounded-full bg-red-400" />
                          Sign Out
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <button
                  type="button"
                  className="btn btn-ghost h-9 px-3.5 text-xs font-bold border-slate-300 flex items-center gap-1.5 cursor-pointer"
                  onClick={() => {
                    setAuthErr('')
                    setLoginModal(true)
                  }}
                >
                  <ShieldCheck className="w-3.5 h-3.5 text-slate-600" />
                  <span>{t('nav.staff', 'Staff Sign In')}</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Real Mode Staff Sign In Modal */}
      {loginModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border border-slate-200 rounded-2xl shadow-2xl max-w-[420px] w-full p-6 md:p-8 animate-in fade-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2.5">
                <img src="/sslogo-symbol.png" alt="Swasthya Setu" className="w-6 h-6 object-contain" />
                <h3 className="font-extrabold text-lg text-ink">Staff Authentication</h3>
              </div>
              <button
                type="button"
                onClick={() => setLoginModal(false)}
                className="text-slate-400 hover:text-ink text-sm font-bold p-1 cursor-pointer"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-500 mb-5 leading-relaxed">
              Enter your accredited healthcare practitioner or administrator credentials to access clinical dossiers.
            </p>

            <form onSubmit={handleLogin} className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Username / Staff ID</label>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="e.g. doctor_demo, pharma_demo, admin_demo"
                  autoFocus
                  required
                  className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:border-orange-500 outline-none transition-all font-mono"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your confidential password"
                  required
                  className="w-full px-3.5 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:border-orange-500 outline-none transition-all"
                />
              </div>

              {authErr && (
                <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs font-semibold">
                  ⚠️ {authErr}
                </div>
              )}

              <div className="pt-2 flex items-center justify-end gap-2.5">
                <button
                  type="button"
                  onClick={() => setLoginModal(false)}
                  className="btn btn-ghost h-10 px-4 text-xs font-semibold text-slate-600"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loggingIn}
                  className="btn btn-saffron h-10 px-5 text-xs font-bold text-white disabled:opacity-50"
                >
                  {loggingIn ? 'Authenticating…' : 'Authenticate & Sign In →'}
                </button>
              </div>
            </form>

            <div className="mt-5 pt-4 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
              <span>Need accreditation?</span>
              <a
                href="#/apply"
                onClick={() => setLoginModal(false)}
                className="text-orange-600 font-semibold hover:underline"
              >
                Apply for Practitioner License →
              </a>
            </div>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1">
        {renderPage()}
      </main>

      {/* Professional Medical Platform Footer (White Background Only) */}
      <footer className="border-t border-slate-200 bg-white pt-14 pb-12 text-slate-600">
        <div className="max-w-[1240px] mx-auto px-6 md:px-10">
          {/* Main Footer Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-12 items-start pb-12 border-b border-slate-100">
            {/* Left 5 Cols: Larger Metallic Emblem on White Background */}
            <div className="lg:col-span-5 flex flex-col items-start gap-4">
              <div className="w-full max-w-[380px] h-[190px] sm:h-[210px] rounded-2xl bg-white border border-slate-200/90 shadow-xs overflow-hidden flex items-center justify-center p-2">
                <MetallicPaint
                  imageSrc="/ss-logo.png"
                  color="#ea580c"
                  backgroundColor="#ffffff"
                  lightMode={true}
                  scale={0.88}
                  density={2.2}
                  edgeBend={0.75}
                  mouseTilt={0.5}
                  dispersion={0.2}
                  className="w-full h-full"
                />
              </div>

              <div className="space-y-1.5">
                <h4 className="font-extrabold text-base sm:text-lg text-ink tracking-tight">
                  Swasthya Setu
                </h4>
                <p className="text-xs sm:text-[13px] text-slate-500 leading-relaxed max-w-[380px]">
                  Digital Health Identity & Disease Surveillance System for Pune Municipal Corporation.
                </p>
              </div>
            </div>

            {/* Right 7 Cols: Larger Navigation Columns with Clean Bulleting Dots */}
            <div className="lg:col-span-7 grid grid-cols-2 sm:grid-cols-3 gap-8 sm:gap-10 pt-1">
              <div>
                <h5 className="font-extrabold text-sm text-ink uppercase tracking-wider mb-4">
                  Citizen Services
                </h5>
                <ul className="space-y-3 text-[13px] sm:text-sm font-medium">
                  <li>
                    <a href="#/apply" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>Apply for Health Card</span>
                    </a>
                  </li>
                  <li>
                    <a href="#/track" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>Track Application</span>
                    </a>
                  </li>
                  <li>
                    <a href="#/privacy" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>DPDP Privacy Charter</span>
                    </a>
                  </li>
                </ul>
              </div>

              <div>
                <h5 className="font-extrabold text-sm text-ink uppercase tracking-wider mb-4">
                  Clinical Providers
                </h5>
                <ul className="space-y-3 text-[13px] sm:text-sm font-medium">
                  <li>
                    <a href="#/doctor" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>OPD Consultation Suite</span>
                    </a>
                  </li>
                  <li>
                    <a href="#/pharmacist" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>Pharmacy Dispense Desk</span>
                    </a>
                  </li>
                  <li>
                    <button
                      type="button"
                      onClick={() => setLoginModal(true)}
                      className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors text-left cursor-pointer"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>Practitioner Sign In</span>
                    </button>
                  </li>
                  <li>
                    <a href="#/apply" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>Clinical Accreditation</span>
                    </a>
                  </li>
                </ul>
              </div>

              <div className="col-span-2 sm:col-span-1">
                <h5 className="font-extrabold text-sm text-ink uppercase tracking-wider mb-4">
                  Surveillance & Admin
                </h5>
                <ul className="space-y-3 text-[13px] sm:text-sm font-medium">
                  <li>
                    <a href="#/surveillance" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>Pune 15-Ward Surveillance</span>
                    </a>
                  </li>
                  <li>
                    <a href="#/admin" className="group flex items-center gap-2.5 hover:text-orange-600 transition-colors">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-300 group-hover:bg-orange-500 shrink-0 transition-colors" />
                      <span>System Administration</span>
                    </a>
                  </li>
                  <li className="pt-2">
                    <span className="text-xs text-slate-500 font-mono block">
                      Emergency Ambulance: 108
                    </span>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {/* Bottom Bar */}
          <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500">
            <div className="flex items-center gap-3 flex-wrap">
              <span>© 2026 Swasthya Setu</span>
              <span>•</span>
              <span>Pune Municipal Corporation Project</span>
              <span>•</span>
              <span className="font-mono text-slate-600 font-medium">DPDP Act 2023 Consent Architecture</span>
            </div>

            <div className="flex items-center gap-3">
              <span className="text-slate-400 font-mono text-[11px]">
                Pune Municipal Ward Health Informatics
              </span>
            </div>
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
