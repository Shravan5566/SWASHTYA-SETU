import type { ReactNode } from 'react'

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

export function HealthCard({
  name,
  blood,
  locality,
  cardId,
  helpline = '108',
}: {
  name?: string
  blood?: string
  locality?: string
  cardId?: string
  helpline?: string
}) {
  const row = (k: string, v?: string) => (
    <div>
      <div className="text-[10px] font-bold tracking-[0.14em] uppercase text-slate-400">{k}</div>
      <div className="text-[14px] md:text-[15px] font-semibold text-ink tracking-tight truncate max-w-[200px]">
        {v || '—'}
      </div>
    </div>
  )

  return (
    <div
      className="print-area w-full max-w-[460px] bg-white border border-slate-200/90 rounded-[22px] overflow-hidden shadow-lg transition-transform duration-200 relative select-none"
      style={{ aspectRatio: '1.586' }}
    >
      {/* Dual sovereign flag strip */}
      <div className="h-2 w-full" style={{ background: 'linear-gradient(90deg, #ea580c 50%, #059669 50%)' }} />

      {/* Subtle security watermark seal */}
      <div className="absolute right-28 top-1/2 -translate-y-1/2 w-44 h-44 opacity-[0.05] pointer-events-none select-none z-0">
        <img src="/sslogo-symbol.png" alt="" className="w-full h-full object-contain" />
      </div>

      {/* Top Header */}
      <div className="flex items-center justify-between px-6 pt-4 pb-2 border-b border-slate-100 relative z-10">
        <div className="flex items-center gap-2.5">
          <Emblem size={34} />
          <div>
            <span className="font-extrabold text-[15px] text-ink tracking-tight">Swasthya Setu</span>
            <div className="text-[9px] font-mono tracking-[0.14em] text-slate-400 uppercase -mt-0.5">
              Digital Health ID
            </div>
          </div>
        </div>
        <div className="text-right">
          <span className="text-[9px] font-extrabold tracking-[0.12em] text-slate-500 uppercase block">
            Pune Health Card
          </span>
          <span className="inline-flex items-center gap-1 text-[8px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
            Encrypted QR ID
          </span>
        </div>
      </div>

      {/* Body Content */}
      <div className="flex items-center justify-between gap-4 px-6 pt-3.5 relative z-10">
        <div className="grid gap-2.5 flex-1">
          {row('Beneficiary', name)}
          <div className="flex items-center gap-6">
            {row('Blood Group', blood)}
            {row('Locality', locality)}
          </div>
        </div>

        {/* QR Code Container with micro-hologram */}
        <div className="flex flex-col items-center">
          <div className="p-1.5 bg-white border border-slate-200 rounded-xl shadow-sm">
            <QR
              seed={cardId ? [...cardId].reduce((a, c) => a + c.charCodeAt(0), 0) : 42}
              size={100}
            />
          </div>
          <span className="text-[8px] font-mono font-bold tracking-wider text-slate-400 mt-1 uppercase">
            Scan for Check-in
          </span>
        </div>
      </div>

      {/* Footer Bar */}
      <div className="absolute bottom-0 inset-x-0 bg-slate-50/90 border-t border-slate-100 px-6 py-2.5 flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <span className="font-mono font-bold tracking-wider text-ink text-[13px]">
            {cardId || 'SS-XXXX-000'}
          </span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
        </div>
        <div className="flex items-center gap-2 text-slate-500 text-[11px]">
          <span>Emergency Helpline:</span>
          <span className="font-mono font-bold text-ink bg-slate-200/70 px-1.5 py-0.5 rounded">
            {helpline}
          </span>
        </div>
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
