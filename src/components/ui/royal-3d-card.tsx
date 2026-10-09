"use client"

import React, { useRef, useState, useEffect, useCallback } from "react"
import { useLang } from "@/i18n"

interface Royal3DCardProps {
  imageSrc?: string
  onClick?: () => void
  className?: string
}

export default function Royal3DCard({
  imageSrc = "/royal-health-card.png",
  onClick,
  className = "",
}: Royal3DCardProps) {
  const { t } = useLang()
  const containerRef = useRef<HTMLDivElement>(null)
  const cardRef = useRef<HTMLDivElement>(null)
  const animFrameRef = useRef<number | null>(null)

  // Target and current interpolated values for 60fps lerping
  const state = useRef({
    targetRotateX: 0,
    targetRotateY: 0,
    targetGlareX: 50,
    targetGlareY: 50,
    targetGlareOpacity: 0,
    currentRotateX: 0,
    currentRotateY: 0,
    currentGlareX: 50,
    currentGlareY: 50,
    currentGlareOpacity: 0,
    isHovered: false,
    idleTime: 0,
  })

  const [springValues, setSpringValues] = useState({
    rotX: 0,
    rotY: 0,
    glareX: 50,
    glareY: 50,
    glareOpacity: 0,
    shadowX: 0,
    shadowY: 20,
  })

  // Animation loop with butter-smooth lerp physics & gentle idle floating
  const animate = useCallback(() => {
    const s = state.current

    if (!s.isHovered) {
      // Gentle natural breathing float when not hovered (Noomo signature idle wave)
      s.idleTime += 0.02
      s.targetRotateX = Math.sin(s.idleTime * 0.8) * 3
      s.targetRotateY = Math.cos(s.idleTime * 0.7) * 4.5
      s.targetGlareX = 50 + Math.sin(s.idleTime * 0.6) * 18
      s.targetGlareY = 50 + Math.cos(s.idleTime * 0.8) * 18
      s.targetGlareOpacity = 0.35 + Math.sin(s.idleTime) * 0.1
    }

    // High-precision lerping
    const lerpFactor = s.isHovered ? 0.12 : 0.06
    s.currentRotateX += (s.targetRotateX - s.currentRotateX) * lerpFactor
    s.currentRotateY += (s.targetRotateY - s.currentRotateY) * lerpFactor
    s.currentGlareX += (s.targetGlareX - s.currentGlareX) * lerpFactor
    s.currentGlareY += (s.targetGlareY - s.currentGlareY) * lerpFactor
    s.currentGlareOpacity += (s.targetGlareOpacity - s.currentGlareOpacity) * lerpFactor

    setSpringValues({
      rotX: s.currentRotateX,
      rotY: s.currentRotateY,
      glareX: s.currentGlareX,
      glareY: s.currentGlareY,
      glareOpacity: s.currentGlareOpacity,
      shadowX: -s.currentRotateY * 1.5,
      shadowY: s.currentRotateX * 1.4 + 22,
    })

    animFrameRef.current = requestAnimationFrame(animate)
  }, [])

  useEffect(() => {
    animFrameRef.current = requestAnimationFrame(animate)
    return () => {
      if (animFrameRef.current) cancelAnimationFrame(animFrameRef.current)
    }
  }, [animate])

  // Mouse move handler
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!containerRef.current) return
    const rect = containerRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const normX = (x / rect.width) * 2 - 1 // -1 to 1
    const normY = (y / rect.height) * 2 - 1 // -1 to 1

    const s = state.current
    s.isHovered = true
    // Tilt angle max ±15 deg
    s.targetRotateX = -normY * 14
    s.targetRotateY = normX * 16
    s.targetGlareX = (x / rect.width) * 100
    s.targetGlareY = (y / rect.height) * 100
    s.targetGlareOpacity = 0.85
  }

  const handleMouseEnter = () => {
    state.current.isHovered = true
  }

  const handleMouseLeave = () => {
    state.current.isHovered = false
    state.current.targetRotateX = 0
    state.current.targetRotateY = 0
    state.current.targetGlareOpacity = 0.3
  }

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      className={`relative w-full max-w-[390px] mx-auto p-4 sm:p-5 rounded-[32px] cursor-pointer select-none transition-all duration-300 ${className}`}
      style={{
        // Minimal luxury frosted bento box matching card and site background
        background:
          "linear-gradient(145deg, rgba(255, 255, 255, 0.95) 0%, rgba(254, 243, 199, 0.28) 40%, rgba(236, 253, 245, 0.35) 80%, rgba(255, 255, 255, 0.95) 100%)",
        border: "1px solid rgba(226, 232, 240, 0.9)",
        boxShadow:
          "0 20px 45px -12px rgba(15, 23, 42, 0.08), 0 4px 16px -2px rgba(249, 115, 22, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.9)",
        perspective: "1200px",
      }}
    >
      {/* Ambient Radial Aura behind the card that reacts to motion */}
      <div
        className="absolute inset-0 rounded-[32px] pointer-events-none transition-opacity duration-500 overflow-hidden"
        style={{
          background: `radial-gradient(circle at ${springValues.glareX}% ${springValues.glareY}%, rgba(249, 115, 22, 0.12) 0%, rgba(16, 185, 129, 0.10) 45%, transparent 70%)`,
        }}
      />

      {/* Top Bento Metadata Strip */}
      <div className="flex items-center justify-between mb-3 px-1 relative z-10">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[11px] font-bold tracking-tight text-slate-800 uppercase font-mono">
            {t('card.title', 'Digital Health ID')}
          </span>
        </div>
        <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-white/90 border border-slate-200/80 shadow-2xs">
          <span className="text-[10px] font-semibold text-slate-600 font-mono">
            {t('card.badge', 'SECURE QR ID')}
          </span>
        </div>
      </div>

      {/* 3D Transform Card Container */}
      <div
        ref={cardRef}
        className="relative rounded-[22px] overflow-hidden transition-transform duration-75 will-change-transform bg-transparent"
        style={{
          transformStyle: "preserve-3d",
          transform: `rotateX(${springValues.rotX.toFixed(2)}deg) rotateY(${springValues.rotY.toFixed(2)}deg) translateZ(12px)`,
          boxShadow: `${springValues.shadowX.toFixed(1)}px ${springValues.shadowY.toFixed(1)}px 32px -8px rgba(15, 23, 42, 0.22), 0 8px 20px -6px rgba(234, 88, 12, 0.08)`,
        }}
      >
        {/* The Royal Health Card Artwork */}
        <img
          src={imageSrc}
          alt="Swasthya Setu Royal Patient Health Card"
          className="w-full h-auto object-contain block select-none pointer-events-none rounded-[22px]"
          loading="eager"
          decoding="async"
        />

        {/* Dynamic Specular Point-Light Spotlight (Tracks Cursor) */}
        <div
          className="absolute inset-0 pointer-events-none rounded-[22px] transition-opacity duration-150"
          style={{
            opacity: springValues.glareOpacity,
            background: `radial-gradient(circle at ${springValues.glareX}% ${springValues.glareY}%, rgba(255, 255, 255, 0.75) 0%, rgba(255, 255, 255, 0.18) 32%, transparent 65%)`,
            mixBlendMode: "overlay",
          }}
        />

        {/* Dynamic Holographic Iridescent Foil Prism Sheen */}
        <div
          className="absolute inset-0 pointer-events-none rounded-[22px] transition-opacity duration-200"
          style={{
            opacity: springValues.glareOpacity * 0.65,
            background: `linear-gradient(${115 + springValues.rotY * 2}deg, transparent 15%, rgba(254, 215, 170, 0.3) 30%, rgba(255, 255, 255, 0.5) 48%, rgba(187, 247, 208, 0.35) 64%, transparent 80%)`,
            mixBlendMode: "color-dodge",
          }}
        />
      </div>

      {/* Bottom Bento Status & Action Bar */}
      <div className="mt-3.5 pt-3 border-t border-slate-200/70 flex items-center justify-between text-xs text-slate-500 relative z-10">
        <span className="text-[11px] font-medium text-slate-600">
          {t('card.citizen', 'Citizen QR Card')}
        </span>
        <span className="inline-flex items-center gap-1 text-[11px] font-bold text-orange-600 group-hover:text-orange-700 transition-colors">
          {t('card.issue', 'Issue Card')} <span className="transition-transform group-hover:translate-x-0.5">→</span>
        </span>
      </div>
    </div>
  )
}
