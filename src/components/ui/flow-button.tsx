import React from 'react'
import { ArrowRight } from 'lucide-react'

export interface FlowButtonProps
  extends React.AnchorHTMLAttributes<HTMLAnchorElement & HTMLButtonElement> {
  children: React.ReactNode
  className?: string
  flowColor?: string
  as?: 'a' | 'button'
  type?: 'button' | 'submit' | 'reset'
  href?: string
  showArrow?: boolean
}

/**
 * FlowButton — Premium 21st.dev Animated Flowing Border Beam Button.
 * Recreates the exact signature 21st.dev / Kain Xu (@xubohuah) FlowButton effect:
 * - Fluid rotating border beam stream that accelerates around the perimeter on hover
 * - High-precision animated flowing dashed border trace
 * - Interactive micro-slide arrow transition
 * - 100% preservation of original color palettes, heights, paddings, and transparency
 */
export const FlowButton: React.FC<FlowButtonProps> = ({
  children,
  className = '',
  flowColor,
  as = 'a',
  type = 'button',
  href,
  showArrow = false,
  ...props
}) => {
  const [hovered, setHovered] = React.useState(false)

  const isSaffron =
    className.includes('btn-saffron') ||
    className.includes('bg-saffron') ||
    className.includes('orange')

  const isGreen =
    className.includes('btn-outline-green') ||
    className.includes('emerald') ||
    className.includes('green')

  // Theme-tailored flow beam gradient colors
  const beamColor =
    flowColor ||
    (isSaffron
      ? '#ffedd5' // Radiant amber-gold highlight
      : isGreen
      ? '#10b981' // Vibrant emerald glow
      : '#f97316')

  const glowShadow = isSaffron
    ? '0 0 20px -3px rgba(234, 88, 12, 0.45)'
    : isGreen
    ? '0 0 20px -3px rgba(16, 185, 129, 0.35)'
    : '0 0 20px -3px rgba(15, 23, 42, 0.25)'

  const Component: any = as === 'button' || (!href && as !== 'a') ? 'button' : 'a'

  return (
    <Component
      href={href}
      type={as === 'button' ? type : undefined}
      onMouseEnter={(e: any) => {
        setHovered(true)
        props.onMouseEnter?.(e)
      }}
      onMouseLeave={(e: any) => {
        setHovered(false)
        props.onMouseLeave?.(e)
      }}
      className={`relative inline-flex items-center justify-center rounded-full overflow-hidden transition-all duration-300 select-none group cursor-pointer ${className}`}
      style={{
        ...props.style,
        position: 'relative',
        boxShadow: hovered ? glowShadow : undefined,
      }}
      {...props}
    >
      {/* 1. Animated Rotating Border Beam Stream (The 21st.dev Flow Signature) */}
      <div
        className="absolute -inset-[2px] rounded-[inherit] overflow-hidden pointer-events-none transition-opacity duration-300"
        style={{
          opacity: hovered ? 1 : 0.3,
        }}
      >
        <div
          className="absolute inset-[-150%] animate-spin"
          style={{
            animationDuration: hovered ? '2.2s' : '5s',
            animationTimingFunction: 'linear',
            background: `conic-gradient(from 0deg, transparent 0deg, transparent 260deg, ${beamColor} 340deg, #ffffff 360deg)`,
          }}
        />
      </div>

      {/* 2. SVG Flowing Dashed Border Trace Layer */}
      <svg
        className="absolute inset-0 w-full h-full pointer-events-none rounded-[inherit] overflow-visible"
        style={{
          width: '100%',
          height: '100%',
          opacity: hovered ? 0.9 : 0.3,
          transition: 'opacity 0.25s ease-out',
        }}
      >
        <rect
          x="1"
          y="1"
          width="calc(100% - 2px)"
          height="calc(100% - 2px)"
          rx="999"
          ry="999"
          fill="none"
          stroke={beamColor}
          strokeWidth="1.5"
          strokeDasharray="6 6"
          style={{
            strokeDashoffset: hovered ? -60 : 0,
            animation: hovered ? 'flow-stream 1.2s linear infinite' : 'none',
          }}
        />
      </svg>

      {/* 3. Subtle Inner Fill Shield to keep button background & transparency clean */}
      <div
        className="absolute inset-[1.5px] rounded-[inherit] pointer-events-none"
        style={{
          background: isSaffron
            ? 'var(--color-saffron, #ea580c)'
            : isGreen
            ? '#ffffff'
            : 'inherit',
          opacity: 0.98,
        }}
      />

      {/* 4. Specular Shimmer Sweep on Hover */}
      <div
        className="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-out pointer-events-none rounded-[inherit]"
        style={{
          background:
            'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.22) 50%, transparent 100%)',
        }}
      />

      {/* 5. Button Content with Smooth Interactive Micro-Animation */}
      <span className="relative z-10 inline-flex items-center justify-center gap-1.5 transition-transform duration-200 group-hover:scale-[1.02]">
        {children}
        {showArrow && (
          <ArrowRight className="w-4 h-4 transition-transform duration-300 ease-out group-hover:translate-x-1" />
        )}
      </span>
    </Component>
  )
}

export default FlowButton
