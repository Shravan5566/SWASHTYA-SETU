"use client"

import gsap from "gsap"
import { SplitText } from "gsap/SplitText"
import { ScrollTrigger } from "gsap/ScrollTrigger"
import { useGSAP } from "@gsap/react"
import { useRef, type ReactNode } from "react"

// Ensure plugins are registered safely
if (typeof window !== "undefined") {
  gsap.registerPlugin(SplitText, ScrollTrigger)
}

export interface TextBlockAnimationProps {
  children: ReactNode
  animateOnScroll?: boolean
  delay?: number
  blockColor?: string
  stagger?: number
  duration?: number
  className?: string
  restartKey?: any
  /** Enable minimal pastel Indian tricolor sequence (Saffron -> White -> Green) */
  useTricolor?: boolean
  /** Show Swasthya Setu logo on the leading edge of the revealer */
  showLogo?: boolean
  logoSrc?: string
}

export default function TextBlockAnimation({
  children,
  animateOnScroll = true,
  delay = 0.15,
  blockColor,
  stagger = 0.12,
  duration = 0.65,
  className = "",
  restartKey,
  useTricolor = true,
  showLogo = true,
  logoSrc = "/sslogo-symbol.png",
}: TextBlockAnimationProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useGSAP(
    () => {
      if (!containerRef.current) return

      // Setup SplitText
      let split: SplitText | null = null
      try {
        split = new SplitText(containerRef.current, {
          type: "lines",
          linesClass: "block-line-parent",
        })
      } catch (err) {
        console.warn("SplitText initialization notice:", err)
        return
      }

      const lines = split.lines
      if (!lines || lines.length === 0) return

      const wrappers: HTMLDivElement[] = []
      const blocks: HTMLDivElement[] = []

      // Soft minimal pastel Indian tricolor gradients & borders that blend with background
      const tricolorThemes = [
        {
          // Line 1: Minimal pastel saffron / kesariya
          background: "linear-gradient(90deg, #fff7ed 0%, #ffedd5 50%, #fed7aa 100%)",
          border: "1px solid rgba(251, 146, 60, 0.4)",
          topBorder: "rgba(234, 88, 12, 0.7)",
          shadow: "0 2px 10px rgba(249, 115, 22, 0.08)",
        },
        {
          // Line 2: Minimal pastel India green
          background: "linear-gradient(90deg, #f0fdf4 0%, #dcfce7 50%, #bbf7d0 100%)",
          border: "1px solid rgba(52, 211, 153, 0.4)",
          topBorder: "rgba(5, 150, 105, 0.7)",
          shadow: "0 2px 10px rgba(16, 185, 129, 0.08)",
        },
        {
          // Line 3+: Soft ivory / tricolor blend
          background: "linear-gradient(90deg, #ffedd5 0%, #ffffff 50%, #dcfce7 100%)",
          border: "1px solid rgba(226, 232, 240, 0.9)",
          topBorder: "rgba(100, 116, 139, 0.5)",
          shadow: "0 2px 10px rgba(0, 0, 0, 0.04)",
        },
      ]

      lines.forEach((line, index) => {
        const theme = tricolorThemes[index % tricolorThemes.length]

        const wrapper = document.createElement("div")
        wrapper.style.position = "relative"
        wrapper.style.display = "block"
        wrapper.style.overflow = "hidden"
        wrapper.style.padding = "2px 0"
        wrapper.style.borderRadius = "4px"

        const block = document.createElement("div")
        block.style.position = "absolute"
        block.style.top = "0"
        block.style.left = "0"
        block.style.width = "100%"
        block.style.height = "100%"
        block.style.borderRadius = "6px"

        if (useTricolor) {
          block.style.background = theme.background
          block.style.border = theme.border
          block.style.boxShadow = theme.shadow
          block.style.borderTop = `2px solid ${theme.topBorder}`
        } else {
          block.style.backgroundColor = blockColor || "#059669"
        }

        block.style.zIndex = "2"
        block.style.transform = "scaleX(0)"
        block.style.transformOrigin = "left center"
        block.style.pointerEvents = "none"

        // Attach Swasthya Setu logo badge at the leading edge of the revealer
        if (showLogo) {
          const logoBadge = document.createElement("div")
          logoBadge.style.position = "absolute"
          logoBadge.style.right = "6px"
          logoBadge.style.top = "50%"
          logoBadge.style.transform = "translateY(-50%)"
          logoBadge.style.width = "28px"
          logoBadge.style.height = "28px"
          logoBadge.style.borderRadius = "9999px"
          logoBadge.style.background = "#ffffff"
          logoBadge.style.border = "1.5px solid rgba(254, 215, 170, 0.8)"
          logoBadge.style.boxShadow = "0 2px 6px rgba(0,0,0,0.08)"
          logoBadge.style.display = "flex"
          logoBadge.style.alignItems = "center"
          logoBadge.style.justifyContent = "center"
          logoBadge.style.zIndex = "3"

          const img = document.createElement("img")
          img.src = logoSrc
          img.alt = "Logo"
          img.style.width = "18px"
          img.style.height = "18px"
          img.style.objectFit = "contain"

          logoBadge.appendChild(img)
          block.appendChild(logoBadge)
        }

        if (line.parentNode) {
          line.parentNode.insertBefore(wrapper, line)
          wrapper.appendChild(line)
          wrapper.appendChild(block)
        }

        gsap.set(line, { opacity: 0 })

        wrappers.push(wrapper)
        blocks.push(block)
      })

      // Master Timeline
      const tl = gsap.timeline({
        defaults: { ease: "expo.inOut" },
        scrollTrigger: animateOnScroll
          ? {
              trigger: containerRef.current,
              start: "top 95%",
              toggleActions: "play none none restart",
            }
          : null,
        delay: delay,
      })

      // Animation sequence
      // Step A: Scale Block 0 -> 1 (Left to Right)
      tl.to(blocks, {
        scaleX: 1,
        duration: duration,
        stagger: stagger,
        transformOrigin: "left center",
      })
        // Step B: Reveal Text behind block
        .set(
          lines,
          {
            opacity: 1,
            stagger: stagger,
          },
          `<${duration / 2}`
        )
        // Step C: Scale Block 1 -> 0 (Left to Right / Out)
        .to(
          blocks,
          {
            scaleX: 0,
            duration: duration,
            stagger: stagger,
            transformOrigin: "right center",
          },
          `<${duration * 0.4}`
        )

      // Revert split on cleanup to prevent duplicated wrapper elements
      return () => {
        tl.kill()
        if (split) {
          try {
            split.revert()
          } catch {
            // ignore cleanup errors
          }
        }
      }
    },
    {
      scope: containerRef,
      dependencies: [
        animateOnScroll,
        delay,
        blockColor,
        stagger,
        duration,
        restartKey,
        useTricolor,
        showLogo,
        logoSrc,
      ],
    }
  )

  return (
    <div ref={containerRef} className={`relative ${className}`}>
      {children}
    </div>
  )
}
