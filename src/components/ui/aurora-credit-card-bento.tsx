"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

/* -------------------------------------------------------------------------- */
/* Types                                                                      */
/* -------------------------------------------------------------------------- */

export type AuroraCreditCardBentoBrand = "visa" | "mastercard" | "none";

/**
 * The anchors, in order, as six flat props.
 *
 * Six, not a list, because a list cannot be edited from a control panel and a
 * colour cannot be picked out of one. Clear a slot and the band goes with it,
 * so the same six props cover three anchors or five. Two reads as a stripe,
 * three as a ribbon, four covers a sweep of hue, six carries the full circle.
 */
const ANCHOR_DEFAULTS = ["#ff7ac1", "#a06bff", "#4f46e5", "#22d3ee", "#4ade80", "#ffb26b"] as const;

/**
 * One turn of the colour cycle, as a share of the flowing layer's height.
 *
 * The layer travels exactly this far each loop, so half its height has to clear
 * both the travel and the card's far corner — otherwise the layer's own edge
 * crosses the face and cuts the bands short. At 400% × 300% the half-height is
 * 3.17 card widths, the travel 1.78, the corner 0.94: 0.45 to spare.
 */
const PERIOD = 28;

/** Same sum for the caustics, which run the other way on a shorter period. */
const CAUSTIC_PERIOD = 23.1;

/**
 * Filaments down the grain, at `[offset px, weight]`. Positive weights catch the
 * light, negative ones sink. Spacing and weight are uneven on purpose — evenly
 * cut strands read as woven cloth, uneven ones as fibre. The list is fixed, not
 * random, so server and client draw the same card.
 */
const FIBRES: Array<[number, number]> = [
    [2, 0.1],
    [8, -0.06],
    [15.5, 0.16],
    [22, -0.05],
    [30.5, 0.08],
    [39.5, -0.07],
    [48, 0.13],
    [57.5, -0.05],
    [67.5, 0.09],
    [76.5, -0.06],
    [86.5, 0.15],
    [96.5, -0.05],
    [106.5, 0.07],
    [116.5, -0.06],
];

/** How far the filament pattern runs before it repeats. */
const FIBRE_PERIOD = 120;

function fibreGradient() {
    const stops = ["transparent 0px"];
    for (const [at, weight] of FIBRES) {
        const colour = weight > 0 ? `rgba(255,255,255,${weight})` : `rgba(0,0,0,${-weight})`;
        stops.push(`transparent ${(at - 1.3).toFixed(1)}px`, `${colour} ${at}px`, `transparent ${(at + 1.3).toFixed(1)}px`);
    }
    stops.push(`transparent ${FIBRE_PERIOD}px`);
    return `repeating-linear-gradient(180deg, ${stops.join(", ")})`;
}

/**
 * Every colour goes in as `var(--aurora-*, <value>)`. The prop sets the value;
 * the variable, if a page defines one, wins over it. That way the palette can be
 * driven from props or re-pointed in CSS without the two fighting.
 */
function token(name: string, value: string) {
    return `var(--aurora-${name}, ${value})`;
}

/** The narrow light running along the grain — one thin line per period. */
function causticGradient(highlight: string) {
    const a = (CAUSTIC_PERIOD * 0.473).toFixed(2);
    const b = (CAUSTIC_PERIOD * 0.5).toFixed(2);
    const c = (CAUSTIC_PERIOD * 0.527).toFixed(2);
    return `repeating-linear-gradient(180deg, transparent 0%, transparent ${a}%, ${token("highlight", highlight)} ${b}%, transparent ${c}%, transparent ${CAUSTIC_PERIOD}%)`;
}

/**
 * The colour cycle, and nothing else.
 *
 * No light in here. A near-white stop on this layer is spread by its 14px blur
 * into a wide pale band that drains the colour either side of it; the thin
 * caustic on its own layer is what the light is for.
 */
function bandGradient(colors: string[]) {
    const step = PERIOD / colors.length;
    const stops = colors.map((color, i) => `${token(`c${i + 1}`, color)} ${(i * step).toFixed(2)}%`);
    stops.push(`${token("c1", colors[0])} ${PERIOD.toFixed(2)}%`);

    return `repeating-linear-gradient(180deg, ${stops.join(", ")})`;
}

/* -------------------------------------------------------------------------- */
/* Stylesheet                                                                 */
/* -------------------------------------------------------------------------- */

const STYLE_ID = "aurora-card-styles";

const STYLES = `
/* One period of travel, so the bands loop without a seam. */
@keyframes aurora-card-flow {
    from { transform: rotate(-25deg) translate3d(0, 0, 0); }
    to   { transform: rotate(-25deg) translate3d(0, 28%, 0); }
}
/* The other way, on a different period — the two never line up twice. */
@keyframes aurora-card-caustic {
    from { transform: rotate(-25deg) translate3d(0, 0, 0); }
    to   { transform: rotate(-25deg) translate3d(0, -23.1%, 0); }
}
/* The filaments creep, slower than either, so the grain never sits still. */
@keyframes aurora-card-fibre {
    from { transform: rotate(-25deg) translate3d(0, 0, 0); }
    to   { transform: rotate(-25deg) translate3d(0, 120px, 0); }
}
@keyframes aurora-card-float {
    0%, 100% { transform: translate3d(0, 5px, 0); }
    50%      { transform: translate3d(0, -7px, 0); }
}
.aurora-card__flow    { animation: aurora-card-flow 26s linear infinite; }
.aurora-card__caustic { animation: aurora-card-caustic 19s linear infinite; }
.aurora-card__fibre   { animation: aurora-card-fibre 34s linear infinite; }
.aurora-card__float   { animation: aurora-card-float 7s ease-in-out infinite; }

.aurora-card__tilt {
    transform:
        perspective(1100px)
        rotateX(var(--aurora-rx, 0deg))
        rotateY(var(--aurora-ry, 0deg))
        translate3d(var(--aurora-tx, 0px), var(--aurora-ty, 0px), 0)
        scale(var(--aurora-scale, 1));
    transition: transform 420ms cubic-bezier(0.22, 0.7, 0.28, 1);
}
.aurora-card:active .aurora-card__tilt { --aurora-scale: 1.01; }

/*
 * The tile takes a step forward. Long and eased right out, the way Stripe moves
 * its card container; the layer is promoted so the scale stays composited and
 * does not judder as the text re-rasterises.
 */
.aurora-card {
    transition: transform 800ms cubic-bezier(0.165, 0.84, 0.44, 1);
    will-change: transform;
}
.aurora-card:hover { transform: scale(1.02); }

/* The glyph picks up the card's own accent rather than a border. */
.aurora-card__glyph-box {
    transition: background-color 300ms ease, color 300ms ease;
}
.aurora-card:hover .aurora-card__glyph-box,
.aurora-card:focus-visible .aurora-card__glyph-box {
    background-color: var(--aurora-accent);
    color: #fff;
}

/* The two brackets pull apart, as if the card were opening out. */
.aurora-card__glyph g { transition: transform 600ms cubic-bezier(0.16, 1, 0.3, 1); }
.aurora-card:hover .aurora-card__glyph-a,
.aurora-card:focus-visible .aurora-card__glyph-a { transform: translate(0.9px, -0.9px); }
.aurora-card:hover .aurora-card__glyph-b,
.aurora-card:focus-visible .aurora-card__glyph-b { transform: translate(-0.9px, 0.9px); }

@media (prefers-reduced-motion: reduce) {
    .aurora-card__flow,
    .aurora-card__caustic,
    .aurora-card__fibre,
    .aurora-card__float { animation: none !important; }
    .aurora-card__tilt { transition: none; transform: none; }
    .aurora-card,
    .aurora-card__glyph-box,
    .aurora-card__glyph g { transition: none; }
    .aurora-card:hover { transform: none; }
}
`;

function useStyles() {
    React.useEffect(() => {
        if (typeof document === "undefined" || document.getElementById(STYLE_ID)) return;
        const tag = document.createElement("style");
        tag.id = STYLE_ID;
        tag.textContent = STYLES;
        document.head.appendChild(tag);
    }, []);
}

/* -------------------------------------------------------------------------- */
/* Grain                                                                      */
/* -------------------------------------------------------------------------- */

/**
 * The two grains the face uses: a soft one under the caustics, a fine one under
 * the filaments. Same warp, different softening.
 */
const GRAINS = [
    { key: "soft", blur: 2 },
    { key: "fine", blur: 0.3 },
] as const;

/**
 * Turns flat stripes into material.
 *
 * `feDisplacementMap` bends the strands, driven by noise stretched along the
 * grain — low frequency across them, higher along them — so they curve rather
 * than dissolve. A second, coarser noise modulates their weight, so each strand
 * surfaces and sinks as it travels.
 *
 * That second noise is mapped to an alpha floored well above zero. The composite
 * below multiplies alpha, so a mask reaching zero severs the strand and leaves a
 * hard end mid-card. Bounded to 0.38–0.93 a strand can only ever fade.
 *
 * The softening is the last primitive in here rather than a CSS `blur()` after
 * the filter, so the whole grain is one pass with nothing to hand between two
 * filters.
 *
 * Where the filter is applied matters more than what is in it. It goes on a
 * still box the size of the card, and the layer that travels sits inside that
 * box. Put it on the travelling layer instead — a rotated box two card widths
 * across, redrawn every frame — and the browser has to work out, frame by frame,
 * how much of that box shows through a card turned in 3D. It gets it wrong, and
 * a strand ends in mid-air with a clean edge. Only while the card is turning,
 * and only on some frames, which is what made it so hard to pin down. Still box,
 * fixed bounds, nothing left to work out.
 */
function GrainFilters({ id }: { id: string }) {
    return (
        <svg width="0" height="0" className="pointer-events-none absolute" aria-hidden="true" focusable="false">
            <defs>
                {GRAINS.map(({ key, blur }) => (
                    <filter
                        key={key}
                        id={`${id}-${key}`}
                        x="-15%"
                        y="-15%"
                        width="130%"
                        height="130%"
                        colorInterpolationFilters="sRGB"
                    >
                        {/*
                         * One octave, and scale × 2π × frequency kept under 1
                         * (14 × 6.28 × 0.010 = 0.88). Above 1 the displacement
                         * field folds over itself and tears what it is bending.
                         */}
                        <feTurbulence
                            type="fractalNoise"
                            baseFrequency="0.003 0.01"
                            numOctaves={1}
                            seed={7}
                            result="warp"
                        />
                        <feDisplacementMap
                            in="SourceGraphic"
                            in2="warp"
                            scale={14}
                            xChannelSelector="R"
                            yChannelSelector="G"
                            result="bent"
                        />
                        <feTurbulence
                            type="fractalNoise"
                            baseFrequency="0.009"
                            numOctaves={1}
                            seed={19}
                            result="patch"
                        />
                        <feColorMatrix
                            in="patch"
                            type="matrix"
                            values="0 0 0 0 1
                                    0 0 0 0 1
                                    0 0 0 0 1
                                    0.55 0 0 0 0.38"
                            result="patchAlpha"
                        />
                        <feComposite in="bent" in2="patchAlpha" operator="in" />
                        <feGaussianBlur stdDeviation={blur} />
                    </filter>
                ))}
            </defs>
        </svg>
    );
}

/* -------------------------------------------------------------------------- */
/* Glyphs                                                                     */
/* -------------------------------------------------------------------------- */

/**
 * The contact pads of an EMV module, taken from the supplied artwork.
 *
 * The artwork arrives as flat black line work, which would sit on the face like
 * a sticker. So it is used as a mask rather than as a picture: the shape is the
 * artwork's, the colour is the same brushed light the rest of the card carries.
 *
 * Cropped to its own ink and turned upright for a card stood on its end, so the
 * box it is given is the module and nothing else — no padding to allow for.
 */
const CHIP_ART =
    "data:image/png;base64,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";

const CHIP_FACE =
    "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAIgAAAC6CAYAAAB1CAX0AAAC4ElEQVR42u3cW08TURSA0dObVIqFYGlCROShVEyBQCAx/v8fhqfpeWgmvdnO1LmsnawnfWD2fM6lpIZgTAWmFfWjq+guuo9m0eOSafqz62gYdSp0fJ30M1+nY5hmjm2Wjvku7eCkaQG00wI+yMUk/aOq7HSdxKPrVuEy6kSVQ6luv+dOSGl9+Z9h9J2Ayjj6Q6+lV1Ph07NkD7Pr5sJya2OYdxwjS62dy7ziOLPM2jrN4yNwi6y3gz6RtUBvN2vnweIa9bsdtxbyu4pYmEhcPdgvEItqrt8C4aCryMCCGu+zqwd7X0Ushw9vL+z18fvEYkhu3V7459uMpSAQBEIBgfjSExvfZL5ZCBnj5UDeLISMJ88f7PwcYhkIBIEgEASCQBAIAkEgCMQiEAgCQSAIBIEgEASCQBCIQBAIAkEgCASBIBAEgkBAIAgEgSAQBIJAEAgCQSAgEASCQBAIAkEgCASBIBAQCAJBIAgEgSAQBIJAEAgIBIEgEASCQBAIAkEgCAQEgkAQCAJBIAgEgSAQBAICQSAIBIEgEASCQBAIAgGBIBAEgkAQCAJBIAgEgVgGAkEgCASBIBAEgkAQCAIRCAJBIAgEgSAQBIJAEAgCEQgCQSAIBIEgEASCQBAICASBIBAEgkAocSBvlkHG03IgNxZCxng5kI6FkNEKmbEUVj5/CASBIBAKDuTeUkh+rAqkZTGse4Nxm2Hj7UUg7BTImeU03mnYMpbk6iEQVvqzSyDeZlw9XEU4LBBXEZ99bJ2ZpTXGz7DnWJ5by8ZpW55by7YZWmJtDUJOM7bM2hmFnOerpdbGRShoPllu5fXCEcaiG/a2ss8MLLw+v6EtckZOQGldhhJNzwkpjW4o+fSdpKM7CRWeedG/nMTcPFThKpHnzD/SPw+LL5FPo+foNXoPi/954CV6DIuvZsz/zvf0kNyqwLG10kPibfrZJ+lYXtKxvadjfU7HfpM+p2gHY8o+fwHR49L0kai2bwAAAABJRU5ErkJggg==";

function Chip({ className, style }: { className?: string; style?: React.CSSProperties }) {
    const mask = (art: string) => ({
        WebkitMaskImage: `url("${art}")`,
        maskImage: `url("${art}")`,
        WebkitMaskSize: "100% 100%",
        maskSize: "100% 100%",
        WebkitMaskRepeat: "no-repeat" as const,
        maskRepeat: "no-repeat" as const,
    });
    return (
        <span
            aria-hidden="true"
            className={cn("relative block", className)}
            style={{
                filter: "drop-shadow(0 0.14cqw 0.3cqw rgba(18, 12, 38, 0.28))",
                ...style,
            }}
        >
            {/* the plate */}
            <span
                className="absolute inset-0"
                style={{
                    background: "linear-gradient(150deg, #ffffff 0%, #f1f0f8 52%, #cfcddc 100%)",
                    ...mask(CHIP_FACE),
                }}
            />
            {/* the pads, cut into it */}
            <span
                className="absolute inset-0"
                style={{ background: "rgba(26, 20, 52, 0.55)", ...mask(CHIP_ART) }}
            />
        </span>
    );
}

function Contactless({ className, style }: { className?: string; style?: React.CSSProperties }) {
    return (
        <svg
            viewBox="0 0 22 34"
            className={className}
            style={style}
            fill="none"
            stroke="currentColor"
            strokeWidth="2.6"
            strokeLinecap="round"
            aria-hidden="true"
        >
            <path d="M2.5 13a7.5 7.5 0 0 1 0 8" />
            <path d="M9 8.5a14 14 0 0 1 0 17" />
            <path d="M15.5 4a20.5 20.5 0 0 1 0 26" />
        </svg>
    );
}

function BrandMark({ id, brand }: { id: string; brand: AuroraCreditCardBentoBrand }) {
    if (brand === "none") return null;

    if (brand === "mastercard") {
        const lens = `${id}-mark-lens`;
        return (
            <svg
                viewBox="0 0 44 26"
                className="h-[1.5rem] w-auto drop-shadow-[0_1px_5px_rgba(24,16,54,0.35)]"
                aria-hidden="true"
            >
                <defs>
                    <clipPath id={lens}>
                        <circle cx="31" cy="13" r="12" />
                    </clipPath>
                </defs>
                <circle cx="13" cy="13" r="12" fill="#ffffff" />
                <circle cx="31" cy="13" r="12" fill="#8e8ea0" />
                <g clipPath={`url(#${lens})`}>
                    <circle cx="13" cy="13" r="12" fill="#c9c9d6" />
                </g>
            </svg>
        );
    }

    return (
        <span className="text-[1.3rem] font-bold italic leading-none tracking-[-0.05em] text-white drop-shadow-[0_1px_6px_rgba(24,16,54,0.45)]">
            VISA
        </span>
    );
}

function ExpandGlyph({ className }: { className?: string }) {
    return (
        <svg
            viewBox="0 0 20 20"
            className={cn("aurora-card__glyph", className)}
            fill="none"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
            strokeLinejoin="round"
            aria-hidden="true"
        >
            <g className="aurora-card__glyph-a">
                <path d="M11.75 4.5h3.75v3.75" />
                <path d="M15.5 4.5 10.75 9.25" />
            </g>
            <g className="aurora-card__glyph-b">
                <path d="M8.25 15.5H4.5v-3.75" />
                <path d="M4.5 15.5 9.25 10.75" />
            </g>
        </svg>
    );
}

/* -------------------------------------------------------------------------- */
/* Component                                                                  */
/* -------------------------------------------------------------------------- */

export type AuroraCreditCardBentoProps = {
    /** The line across the top of the tile. */
    title?: React.ReactNode;
    /** Which mark sits in the bottom corner of the card. */
    brand?: AuroraCreditCardBentoBrand;
    /** Your own mark instead of `brand`. */
    brandMark?: React.ReactNode;
    /** First anchor. The cycle runs from here and comes back to it. */
    color1?: string;
    /** Second anchor. */
    color2?: string;
    /** Third anchor. Clear it, and the ones after, to run fewer bands. */
    color3?: string;
    /** Fourth anchor. */
    color4?: string;
    /** Fifth anchor. */
    color5?: string;
    /** Sixth anchor. */
    color6?: string;
    /** The thin catch of light crossing the bands. */
    highlight?: string;
    /** Colour pooling on the tile's ring under the pointer. */
    glow?: string;
    /**
     * How far the card turns towards the pointer, in degrees at the tile's edge.
     * `0` holds it still.
     */
    tilt?: number;
    /** The slow bob when the pointer is elsewhere. Default `true`. */
    float?: boolean;
    /** The glyph in the top corner. Pass `null` to drop it. */
    action?: React.ReactNode;
} & Omit<React.ComponentProps<"button">, "title" | "color">;

/**
 * A payment card floating in a dark tile, lit by its own gradient.
 *
 * The tile carries a ring that brightens under the pointer, and the card turns
 * to follow it. Everything is CSS — no canvas, no WebGL, no dependency past
 * React and Tailwind.
 */
export function AuroraCreditCardBento({
    title = "Create a card issuing programme",
    brand = "visa",
    brandMark,
    color1 = ANCHOR_DEFAULTS[0],
    color2 = ANCHOR_DEFAULTS[1],
    color3 = ANCHOR_DEFAULTS[2],
    color4 = ANCHOR_DEFAULTS[3],
    color5 = ANCHOR_DEFAULTS[4],
    color6 = ANCHOR_DEFAULTS[5],
    highlight = "rgba(255, 255, 255, 0.92)",
    glow: glowColor,
    tilt = 15,
    float = true,
    action,
    className,
    onPointerMove,
    onPointerLeave,
    ...rest
}: AuroraCreditCardBentoProps) {
    useStyles();

    const id = React.useId().replace(/:/g, "");
    const rootRef = React.useRef<HTMLButtonElement>(null);
    const frameRef = React.useRef(0);

    // An empty slot drops its band. Below two there is no cycle to run, so the
    // defaults come back rather than leave the face flat.
    const picked = [color1, color2, color3, color4, color5, color6].filter(
        (c): c is string => typeof c === "string" && c.trim() !== "",
    );
    const colors = picked.length > 1 ? picked : [...ANCHOR_DEFAULTS];
    const glow = token("glow", glowColor ?? colors[0]);
    const grain = `${id}-grain`;

    const reset = React.useCallback(() => {
        const root = rootRef.current;
        if (!root) return;
        root.style.setProperty("--aurora-rx", "0deg");
        root.style.setProperty("--aurora-ry", "0deg");
        root.style.setProperty("--aurora-tx", "0px");
        root.style.setProperty("--aurora-ty", "0px");
    }, []);

    React.useEffect(() => () => cancelAnimationFrame(frameRef.current), []);

    const handlePointerMove = (event: React.PointerEvent<HTMLButtonElement>) => {
        onPointerMove?.(event);
        const root = rootRef.current;
        if (!root) return;

        const { clientX, clientY } = event;
        cancelAnimationFrame(frameRef.current);
        frameRef.current = requestAnimationFrame(() => {
            const box = root.getBoundingClientRect();
            const x = (clientX - box.left) / box.width;
            const y = (clientY - box.top) / box.height;

            // The spotlight follows the pointer whatever the card is doing.
            root.style.setProperty("--aurora-mx", `${clientX - box.left}px`);
            root.style.setProperty("--aurora-my", `${clientY - box.top}px`);

            if (tilt === 0) return;
            root.style.setProperty("--aurora-rx", `${(0.5 - y) * tilt * 2}deg`);
            root.style.setProperty("--aurora-ry", `${(x - 0.5) * tilt * 2}deg`);
            root.style.setProperty("--aurora-tx", `${(x - 0.5) * 22}px`);
            root.style.setProperty("--aurora-ty", `${(y - 0.5) * 16}px`);
        });
    };

    const handlePointerLeave = (event: React.PointerEvent<HTMLButtonElement>) => {
        onPointerLeave?.(event);
        cancelAnimationFrame(frameRef.current);
        reset();
    };

    // Colour in bands down the face, ending in the dark the tile is cut from.
    // Sits under the flowing bands, so the face is never bare on first paint.
    const faceWash = `linear-gradient(168deg, ${colors
        .map((c, i) => `${token(`c${i + 1}`, c)} ${((i / colors.length) * 90).toFixed(1)}%`)
        .join(", ")}, #120e26 100%)`;

    return (
        <button
            ref={rootRef}
            type="button"
            onPointerMove={handlePointerMove}
            onPointerLeave={handlePointerLeave}
            className={cn(
                "aurora-card group relative isolate flex h-full min-h-[500px] w-full flex-col overflow-hidden",
                "rounded-[22px] bg-card p-7 text-left",
                "focus:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
                className,
            )}
            // Hands the accent to CSS, which cannot reach the prop. A page setting
            // --aurora-glow still wins, since that is resolved where it is used.
            style={{ "--aurora-accent": glow } as React.CSSProperties}
            {...rest}
        >
            {/* the ring: a hairline, plus a spotlight that follows the pointer */}
            <span
                aria-hidden="true"
                // Flat, and drawn from the theme, so it reads on a light tile too.
                className="pointer-events-none absolute inset-0 rounded-[inherit] bg-foreground/10 p-px"
                style={{
                    WebkitMask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                    mask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                    WebkitMaskComposite: "xor",
                    maskComposite: "exclude",
                }}
            />
            <span
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 rounded-[inherit] p-px text-foreground opacity-0 transition-opacity duration-300 group-hover:opacity-100 group-focus-visible:opacity-100"
                style={{
                    // A blob centred on the pointer, wide enough to reach the edge from
                    // the middle of the tile, and gone by the far side — so the ring
                    // lights where the pointer is rather than all over. The mid stop
                    // comes off the theme, so it darkens on a light tile and lightens
                    // on a dark one.
                    background: `radial-gradient(320px circle at var(--aurora-mx, 50%) var(--aurora-my, 50%), ${glow} 0%, color-mix(in srgb, currentColor 42%, transparent) 30%, transparent 75%)`,
                    WebkitMask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                    mask: "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                    WebkitMaskComposite: "xor",
                    maskComposite: "exclude",
                }}
            />

            {/* heading */}
            <span className="relative flex items-start justify-between gap-4">
                {title ? (
                    <span className="max-w-[15ch] text-[1.45rem] font-semibold leading-[1.15] tracking-[-0.02em] text-foreground">
                        {title}
                    </span>
                ) : (
                    <span />
                )}

                {action === null ? null : (
                    <span
                        aria-hidden="true"
                        className={cn(
                            "aurora-card__glyph-box grid size-10 shrink-0 place-items-center rounded-xl",
                            "bg-foreground/[0.05] text-muted-foreground",
                        )}
                    >
                        {action ?? <ExpandGlyph className="size-5" />}
                    </span>
                )}
            </span>

            {/* the card */}
            <span className="relative mt-auto flex flex-1 items-center justify-center pt-8 [perspective:1100px]">
                <span
                    className={cn("block w-[74%] max-w-[240px]", float && "aurora-card__float")}
                    // Lets the corner radius stay a fixed share of the card's width.
                    style={{ containerType: "inline-size" }}
                >
                    <span
                        className={cn(
                            // ID-1: 85.60 × 53.98 mm, corners 3.18 mm — 5.89% of the short side.
                            "aurora-card__tilt relative block aspect-[1/1.586] overflow-hidden",
                            // Feeds currentColor to the shadow below. No preserve-3d: the
                            // perspective lives in this element's own transform and nothing
                            // inside it stands in 3D, so there is no reason to pay for a
                            // 3D rendering context on every layer under it.
                            "text-foreground will-change-transform",
                        )}
                        style={{
                            background: faceWash,
                            borderRadius: "5.89cqw",
                            // Just enough to lift the card off the tile. Drawn from the
                            // theme, so it goes dark under a light tile and light under a
                            // dark one — a black shadow on black would show nothing.
                            boxShadow: [
                                "0 0.4cqw 0.9cqw color-mix(in srgb, currentColor 10%, transparent)",
                                "0 1.1cqw 2.4cqw -0.6cqw color-mix(in srgb, currentColor 12%, transparent)",
                            ].join(", "),
                        }}
                    >
                        <GrainFilters id={grain} />

                        {/* Bands of colour drawn across the grain, each running into the next. */}
                        <span
                            aria-hidden="true"
                            className="aurora-card__flow pointer-events-none absolute left-[-100%] top-[-150%] h-[400%] w-[300%] blur-[14px]"
                            style={{
                                background: bandGradient(colors),
                            }}
                        />

                        {/* Light caught along the grain: narrow caustics over a brushed texture. */}
                        <span
                            aria-hidden="true"
                            // The filter sits on this still, card-sized box, never on
                            // the layer that moves. See the note on GrainFilters.
                            className="aurora-card__grain pointer-events-none absolute inset-0"
                            style={{
                                filter: `url(#${grain}-soft)`,
                                opacity: 0.34,
                                mixBlendMode: "plus-lighter",
                            }}
                        >
                            <span
                                // Sized to its own travel, not the flow's — half its
                                // height has to clear both the loop and the card's far
                                // corner.
                                className="aurora-card__caustic absolute left-[-55%] top-[-90%] h-[280%] w-[210%]"
                                style={{
                                    background: causticGradient(highlight),
                                }}
                            />
                        </span>

                        {/* Filaments down the grain — the fibre the light runs along. */}
                        <span
                            aria-hidden="true"
                            className="aurora-card__grain pointer-events-none absolute inset-0"
                            style={{
                                filter: `url(#${grain}-fine)`,
                                opacity: 0.95,
                                mixBlendMode: "overlay",
                            }}
                        >
                            <span
                                className="aurora-card__fibre absolute left-[-55%] top-[-70%] h-[240%] w-[210%]"
                                style={{ background: fibreGradient() }}
                            />
                        </span>

                        {/* grain, so the gradient does not band */}
                        <span
                            aria-hidden="true"
                            className="pointer-events-none absolute inset-0 opacity-[0.16] mix-blend-overlay"
                            style={{
                                backgroundImage:
                                    "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='120' height='120' filter='url(%23n)'/%3E%3C/svg%3E\")",
                            }}
                        />

                        {/* edge light and a soft vignette — no outline, the light catch does the work */}
                        <span
                            aria-hidden="true"
                            className="pointer-events-none absolute inset-0 rounded-[inherit]"
                            style={{
                                background: [
                                    "linear-gradient(200deg, rgba(255,255,255,0.24) 0%, transparent 24%)",
                                    "linear-gradient(0deg, rgba(9,6,22,0.62) 0%, rgba(9,6,22,0.22) 26%, transparent 48%)",
                                    "radial-gradient(130% 80% at 50% 116%, rgba(9,6,22,0.5) 0%, transparent 60%)",
                                ].join(", "),
                            }}
                        />

                        {/* Chip, then the waves to the right of it, high on the face.
                            The module is 15 cqw across — 8.1 mm on a card this size,
                            against the 10 to 13 mm of a real one, so it sits a little
                            under life size and reads better for it. Both figures in cqw,
                            so the pair keeps its shape whatever the card is scaled to. */}
                        <span
                            className="pointer-events-none absolute flex items-center"
                            style={{ top: "20.6cqw", left: "53cqw", gap: "5cqw" }}
                        >
                            <Chip style={{ width: "15cqw", height: "20.5cqw" }} />
                            <Contactless className="text-white/90" style={{ width: "8.5cqw", height: "13.1cqw" }} />
                        </span>

                        {/* cqw both ways, so the gap off the bottom matches the gap off the side. */}
                        <span
                            className="pointer-events-none absolute flex items-end"
                            style={{ bottom: "8cqw", right: "8cqw" }}
                        >
                            {brandMark ?? <BrandMark id={id} brand={brand} />}
                        </span>
                    </span>
                </span>
            </span>
        </button>
    );
}

export default AuroraCreditCardBento;
