import { useState, type ReactNode } from 'react'
import { QRCodeSVG } from 'qrcode.react'

export function Emblem({ size = 38, className = '' }: { size?: number; className?: string }) {
  return (
    <img
      src="/sslogo-symbol.png"
      alt="Swasthya Setu Emblem"
      width={size}
      height={size}
      className={`shrink-0 object-contain drop-shadow-sm select-none ${className}`}
      style={{ width: size, height: size }}
      loading="eager"
    />
  )
}

export function FullLogo({
  height = 48,
  light = false,
  className = '',
}: {
  height?: number
  light?: boolean
  className?: string
}) {
  return (
    <img
      src={light ? '/sslogo-light.png' : '/sslogo.png'}
      alt="Swasthya Setu — SCAN • CARE • TOGETHER"
      className={`object-contain select-none ${className}`}
      style={{ height }}
      loading="eager"
    />
  )
}

export function Logo({
  light = false,
  showTagline = true,
  size = 40,
  className = '',
}: {
  light?: boolean
  showTagline?: boolean
  size?: number
  className?: string
}) {
  return (
    <div className={`flex items-center gap-3 group select-none ${className}`}>
      <div className="relative shrink-0 flex items-center justify-center">
        <img
          src="/sslogo-symbol.png"
          alt="Swasthya Setu Logo"
          width={size}
          height={size}
          className="object-contain drop-shadow-sm transition-transform duration-300 group-hover:scale-105"
          style={{ width: size, height: size }}
          loading="eager"
        />
      </div>
      <div className="leading-tight">
        <div className={`font-extrabold text-[18px] tracking-tight ${light ? 'text-white' : 'text-ink'}`}>
          Swasthya Setu
        </div>
        {showTagline && (
          <div className={`font-mono text-[9px] tracking-[0.2em] font-semibold uppercase ${light ? 'text-slate-400' : 'text-slate-500'}`}>
            SCAN • CARE • TOGETHER
          </div>
        )}
      </div>
    </div>
  )
}

function hash(n: number) {
  n = (n ^ 61) ^ (n >>> 16)
  n = n + (n << 3)
  n = n ^ (n >>> 4)
  n = Math.imul(n, 0x27d4eb2d)
  return (n ^ (n >>> 15)) >>> 0
}

export function QR({ seed = 1, size = 112 }: { seed?: number; size?: number }) {
  const N = 21
  const finder = (x: number, y: number) =>
    [[0, 0], [N - 7, 0], [0, N - 7]].some(([fx, fy]) => x >= fx && x < fx + 7 && y >= fy && y < fy + 7)

  const cells: ReactNode[] = []
  for (let y = 0; y < N; y++) {
    for (let x = 0; x < N; x++) {
      if (finder(x, y)) continue
      if (hash(seed * 997 + y * N + x) % 100 < 50) {
        cells.push(
          <rect
            key={`${x}-${y}`}
            x={x}
            y={y}
            width="1"
            height="1"
            fill={x < N / 2 ? '#c2410c' : '#047857'}
          />
        )
      }
    }
  }

  const F = (fx: number, fy: number, c: string) => (
    <g key={`${fx}${fy}`}>
      <rect x={fx} y={fy} width="7" height="7" fill={c} rx="1" />
      <rect x={fx + 1} y={fy + 1} width="5" height="5" fill="#ffffff" />
      <rect x={fx + 2} y={fy + 2} width="3" height="3" fill={c} rx="0.5" />
    </g>
  )

  return (
    <svg
      width={size}
      height={size}
      viewBox={`-1 -1 ${N + 2} ${N + 2}`}
      shapeRendering="crispEdges"
      role="img"
      aria-label="Secure QR Code"
      className="rounded bg-white shadow-sm"
    >
      <rect x="-1" y="-1" width={N + 2} height={N + 2} fill="#ffffff" />
      {cells}
      {F(0, 0, '#ea580c')}
      {F(N - 7, 0, '#047857')}
      {F(0, N - 7, '#0b192c')}
    </svg>
  )
}

export function HealthCardFront({ className = '' }: { className?: string }) {
  return (
    <div
      className={`relative select-none overflow-hidden rounded-[24px] bg-[#F7F5EE] border border-slate-200/90 shadow-xl transition-all ${className}`}
      style={{ aspectRatio: '682 / 1024', maxWidth: '320px', width: '100%' }}
    >
      <img
        src="/card-front-bg.png"
        alt="Swasthya Setu Patient Health ID Front Face"
        className="w-full h-full object-cover block select-none pointer-events-none"
        draggable={false}
      />
    </div>
  )
}

export function HealthCardBack({
  name = 'Meera Joshi',
  cardId = 'SS-TEST-001',
  age,
  dob,
  gender,
  blood = 'O+',
  className = '',
}: {
  name?: string
  cardId?: string
  age?: string | number
  dob?: string
  gender?: string
  blood?: string
  className?: string
}) {
  let displayAge = age ? `${age}` : ''
  if (!displayAge && dob) {
    const yr = new Date(dob).getFullYear()
    if (!isNaN(yr)) {
      displayAge = `${new Date().getFullYear() - yr} Years`
    }
  }
  if (!displayAge) displayAge = '28 Years'
  const displayGender = gender || 'Female'

  return (
    <div
      className={`relative select-none overflow-hidden rounded-[24px] bg-[#F5F3ED] border border-slate-200/90 shadow-xl transition-all ${className}`}
      style={{ aspectRatio: '764 / 1024', maxWidth: '320px', width: '100%' }}
    >
      {/* Authentic Background Template */}
      <img
        src="/card-back-clean-template.png"
        alt="Swasthya Setu Card Back Background"
        className="w-full h-full object-cover block select-none pointer-events-none"
        draggable={false}
      />

      {/* 1. Dynamic Scannable QR Code */}
      <div
        className="absolute z-10 flex items-center justify-center bg-white rounded-md p-1"
        style={{
          top: '15.0%',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '30.5%',
          height: '22.8%',
        }}
      >
        <QRCodeSVG
          value={cardId || 'SS-TEST-001'}
          size={95}
          level="M"
          className="w-full h-full object-contain"
        />
      </div>

      {/* 2. Dynamic Card ID */}
      <div
        className="absolute z-10 text-center font-mono font-semibold tracking-wider text-slate-800"
        style={{
          top: '42.8%',
          left: '50%',
          transform: 'translateX(-50%)',
          fontSize: '11px',
          width: '80%',
        }}
      >
        {cardId || 'SS-XXXX-XXXX-XXXX'}
      </div>

      {/* 3. Patient Demographic Rows (Label + Value) */}
      {/* Row 1: Name */}
      <div
        className="absolute z-10 flex flex-col justify-center"
        style={{ top: '50.6%', left: '46.0%', right: '8%' }}
      >
        <span className="text-[9.5px] font-medium text-slate-500 leading-tight">Name</span>
        <span className="text-[11.5px] font-bold text-slate-800 leading-tight truncate">
          {name || 'Citizen Patient'}
        </span>
      </div>

      {/* Row 2: Age */}
      <div
        className="absolute z-10 flex flex-col justify-center"
        style={{ top: '57.8%', left: '46.0%', right: '8%' }}
      >
        <span className="text-[9.5px] font-medium text-slate-500 leading-tight">Age</span>
        <span className="text-[11px] font-semibold text-slate-800 leading-tight">
          {displayAge}
        </span>
      </div>

      {/* Row 3: Gender */}
      <div
        className="absolute z-10 flex flex-col justify-center"
        style={{ top: '64.8%', left: '46.0%', right: '8%' }}
      >
        <span className="text-[9.5px] font-medium text-slate-500 leading-tight">Gender</span>
        <span className="text-[11px] font-semibold text-slate-800 leading-tight">
          {displayGender}
        </span>
      </div>

      {/* Row 4: Blood Group */}
      <div
        className="absolute z-10 flex flex-col justify-center"
        style={{ top: '72.0%', left: '46.0%', right: '8%' }}
      >
        <span className="text-[9.5px] font-medium text-slate-500 leading-tight">Blood Group</span>
        <span className="text-[11.5px] font-bold text-slate-800 leading-tight">
          {blood || 'O+'}
        </span>
      </div>
    </div>
  )
}

export function HealthCard({
  name,
  blood,
  locality,
  cardId,
  age,
  dob,
  gender,
  helpline = '108',
  defaultSide = 'both',
}: {
  name?: string
  blood?: string
  locality?: string
  cardId?: string
  age?: string | number
  dob?: string
  gender?: string
  helpline?: string
  defaultSide?: 'both' | 'front' | 'back'
}) {
  const [view, setView] = useState<'both' | 'front' | 'back'>(defaultSide)

  return (
    <div className="flex flex-col items-center gap-4 w-full">
      {/* Interactive Side Toggle Bar */}
      <div className="flex items-center gap-1.5 p-1 bg-slate-100 rounded-xl text-xs font-bold border border-slate-200">
        <button
          type="button"
          onClick={() => setView('both')}
          className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
            view === 'both' ? 'bg-white text-ink shadow-xs' : 'text-slate-500 hover:text-ink'
          }`}
        >
          🪪 Dual Sided (Front & Back)
        </button>
        <button
          type="button"
          onClick={() => setView('front')}
          className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
            view === 'front' ? 'bg-white text-ink shadow-xs' : 'text-slate-500 hover:text-ink'
          }`}
        >
          Front Face
        </button>
        <button
          type="button"
          onClick={() => setView('back')}
          className={`px-3 py-1.5 rounded-lg transition-all cursor-pointer ${
            view === 'back' ? 'bg-white text-ink shadow-xs' : 'text-slate-500 hover:text-ink'
          }`}
        >
          Back (QR & Patient Info)
        </button>
      </div>

      {/* Card Presentation Area */}
      <div className="print-area flex flex-wrap items-center justify-center gap-6 sm:gap-8 w-full py-2">
        {(view === 'both' || view === 'front') && (
          <div className="flex flex-col items-center">
            <HealthCardFront />
            <span className="text-[11px] font-mono text-slate-400 mt-2 font-semibold">
              Front: NFC Smart Identity
            </span>
          </div>
        )}

        {(view === 'both' || view === 'back') && (
          <div className="flex flex-col items-center">
            <HealthCardBack
              name={name}
              cardId={cardId}
              blood={blood}
              age={age}
              dob={dob}
              gender={gender}
            />
            <span className="text-[11px] font-mono text-slate-400 mt-2 font-semibold">
              Back: Scannable Clinical QR & Demographics
            </span>
          </div>
        )}
      </div>
    </div>
  )
}

export function State({
  loading,
  error,
  empty,
  emptyText = 'No records found.',
  onRetry,
}: {
  loading?: boolean
  error?: string | null
  empty?: boolean
  emptyText?: string
  onRetry?: () => void
}) {
  if (loading) {
    return (
      <div className="p-10 text-center flex flex-col items-center justify-center gap-3">
        <div className="w-8 h-8 rounded-full border-2 border-orange-200 border-t-orange-600 animate-spin" />
        <span className="text-sm font-medium text-slate-500">Querying secure clinical registry…</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-6 m-4 rounded-xl border border-red-200 bg-red-50/80 text-red-900 flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <span className="text-lg">⚠️</span>
          <div>
            <div className="text-sm font-bold">Request Error</div>
            <div className="text-xs text-red-700 mt-0.5 leading-relaxed">{error}</div>
          </div>
        </div>
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-red-100 hover:bg-red-200 text-red-800 transition-colors shrink-0"
          >
            Retry
          </button>
        )}
      </div>
    )
  }

  if (empty) {
    return (
      <div className="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-2">
        <span className="text-2xl">📋</span>
        <span className="text-sm font-medium">{emptyText}</span>
      </div>
    )
  }

  return null
}

export function Section({
  eyebrow,
  title,
  children,
  right,
}: {
  eyebrow?: string
  title: string
  children: ReactNode
  right?: ReactNode
}) {
  return (
    <section className="max-w-[1240px] mx-auto px-6 md:px-10 py-10 md:py-14 animate-in fade-in duration-200">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-8 pb-4 border-b border-slate-100">
        <div>
          {eyebrow && <div className="eyebrow mb-1.5">{eyebrow}</div>}
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-ink">{title}</h1>
        </div>
        {right && <div className="flex items-center gap-3">{right}</div>}
      </div>
      {children}
    </section>
  )
}
