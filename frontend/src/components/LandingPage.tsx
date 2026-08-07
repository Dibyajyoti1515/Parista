import { useEffect, useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

/* ---------- Relationship types with icons ---------- */

interface RelType {
  label: string;
  icon: string;
}

const RELATIONSHIP_TYPES: RelType[] = [
  { label: "Partner", icon: "❤️" },
  { label: "Manager", icon: "💼" },
  { label: "HR", icon: "📋" },
  { label: "Friends", icon: "🤝" },
  { label: "Mother", icon: "💐" },
  { label: "Father", icon: "👔" },
  { label: "Siblings", icon: "👫" },
  { label: "Teacher", icon: "📚" },
];

/* ---------- Background hearts: 3 size tiers for depth ---------- */

type HeartTier = "small" | "medium" | "large";

interface TwinkleHeart {
  top: string;
  left: string;
  tier: HeartTier;
  delay: number;
  duration: number;
}

const TIER_STYLE: Record<HeartTier, { size: number; opacity: number }> = {
  small: { size: 8, opacity: 0.25 },
  medium: { size: 13, opacity: 0.4 },
  large: { size: 20, opacity: 0.55 },
};

const TWINKLE_HEARTS: TwinkleHeart[] = [
  { top: "12%", left: "8%", tier: "medium", delay: 0, duration: 3.2 },
  { top: "22%", left: "22%", tier: "small", delay: 0.6, duration: 2.8 },
  { top: "8%", left: "42%", tier: "medium", delay: 1.1, duration: 3.6 },
  { top: "18%", left: "58%", tier: "small", delay: 0.3, duration: 2.6 },
  { top: "6%", left: "72%", tier: "large", delay: 0.9, duration: 3.4 },
  { top: "30%", left: "88%", tier: "medium", delay: 0.2, duration: 3.0 },
  { top: "40%", left: "6%", tier: "large", delay: 1.4, duration: 3.8 },
  { top: "52%", left: "16%", tier: "small", delay: 0.7, duration: 2.7 },
  { top: "60%", left: "4%", tier: "medium", delay: 1.8, duration: 3.3 },
  { top: "70%", left: "12%", tier: "small", delay: 0.4, duration: 2.5 },
  { top: "78%", left: "30%", tier: "medium", delay: 1.2, duration: 3.5 },
  { top: "85%", left: "18%", tier: "small", delay: 0.8, duration: 2.9 },
  { top: "88%", left: "48%", tier: "large", delay: 1.6, duration: 3.7 },
  { top: "82%", left: "70%", tier: "small", delay: 0.5, duration: 2.6 },
  { top: "90%", left: "84%", tier: "medium", delay: 1.0, duration: 3.1 },
  { top: "68%", left: "92%", tier: "small", delay: 0.1, duration: 2.8 },
  { top: "48%", left: "94%", tier: "large", delay: 1.3, duration: 3.4 },
  { top: "34%", left: "78%", tier: "small", delay: 0.6, duration: 2.4 },
];

function TwinklingHearts() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      {TWINKLE_HEARTS.map((h, i) => {
        const style = TIER_STYLE[h.tier];
        return (
          <span
            key={i}
            className="absolute text-pink-accent"
            style={{
              top: h.top,
              left: h.left,
              fontSize: style.size,
              opacity: style.opacity,
              animation: `twinkle ${h.duration}s ease-in-out ${h.delay}s infinite, float ${h.duration * 1.5}s ease-in-out ${h.delay}s infinite`,
            }}
          >
            ♥
          </span>
        );
      })}
    </div>
  );
}

/* ---------- Atmospheric gradient blobs ---------- */

function GradientBlobs() {
  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden" aria-hidden>
      {/* Large soft pink blob behind the heart */}
      <div
        className="absolute right-[5%] top-[20%] h-[520px] w-[520px] rounded-full blur-[120px]"
        style={{
          background:
            "radial-gradient(circle, rgba(236,72,153,0.16) 0%, rgba(244,63,94,0.06) 45%, transparent 70%)",
        }}
      />
      {/* Secondary magenta blob lower-left for atmosphere */}
      <div
        className="absolute bottom-[5%] left-[10%] h-[420px] w-[420px] rounded-full blur-[140px]"
        style={{
          background:
            "radial-gradient(circle, rgba(217,70,239,0.1) 0%, rgba(236,72,153,0.04) 50%, transparent 75%)",
        }}
      />
    </div>
  );
}

/* ---------- Mini heart burst particles (during bloom) ---------- */

interface BurstParticle {
  x: string;
  y: string;
  rot: string;
  size: number;
  delay: number;
}

const BURST_PARTICLES: BurstParticle[] = [
  { x: "-70px", y: "-60px", rot: "-30deg", size: 12, delay: 0 },
  { x: "70px", y: "-50px", rot: "25deg", size: 10, delay: 0.08 },
  { x: "-55px", y: "65px", rot: "20deg", size: 9, delay: 0.15 },
  { x: "60px", y: "60px", rot: "-20deg", size: 13, delay: 0.05 },
  { x: "0px", y: "-85px", rot: "10deg", size: 8, delay: 0.12 },
  { x: "-85px", y: "10px", rot: "-10deg", size: 11, delay: 0.1 },
];

function BurstHearts() {
  return (
    <div className="pointer-events-none absolute inset-0 z-20 flex items-center justify-center" aria-hidden>
      {BURST_PARTICLES.map((p, i) => (
        <span
          key={i}
          className="absolute text-pink-accent"
          style={{
            fontSize: p.size,
            animation: `heart-burst 10s ease-out ${p.delay}s infinite`,
            ["--burst-x" as string]: p.x,
            ["--burst-y" as string]: p.y,
            ["--burst-rot" as string]: p.rot,
          }}
        >
          ♥
        </span>
      ))}
    </div>
  );
}

/* ---------- 3D glass heart (multi-light-source SVG) ---------- */

function GlassHeart() {
  return (
    <div className="relative flex items-center justify-center">
      {/* Mini heart burst particles (above bloom glow, in front of heart) */}
      <BurstHearts />
      {/* Layered glow — tight bright core + soft outer halo (light bouncing off glass) */}
      <div
        className="absolute h-[380px] w-[380px] rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(255,255,255,0.12) 0%, rgba(236,72,153,0.28) 30%, rgba(244,63,94,0.1) 55%, transparent 72%)",
          filter: "blur(40px)",
        }}
      />

      {/* Bloom layers — soft radial light bursts radiating outward every 10s.
          Positioned behind the heart (lower z-index) so they read as light
          emanating from it, not overlapping on top. Uses transform/opacity only. */}
      <div
        className="animate-bloom pointer-events-none absolute h-[300px] w-[300px] rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(255,255,255,0.5) 0%, rgba(236,72,153,0.4) 30%, rgba(244,63,94,0.15) 60%, transparent 80%)",
          filter: "blur(20px)",
        }}
      />
      <div
        className="animate-bloom-delayed pointer-events-none absolute h-[300px] w-[300px] rounded-full"
        style={{
          background:
            "radial-gradient(circle, rgba(255,255,255,0.35) 0%, rgba(236,72,153,0.3) 35%, rgba(244,63,94,0.1) 65%, transparent 85%)",
          filter: "blur(24px)",
        }}
      />

      {/* The 3D heart */}
      <div className="animate-heartbeat animate-heart-glow relative z-10 h-[260px] w-[300px] sm:h-[310px] sm:w-[350px]">
        <svg
          viewBox="0 0 200 180"
          className="h-full w-full"
          style={{ filter: "drop-shadow(0 24px 48px rgba(0,0,0,0.55))" }}
        >
          <defs>
            {/* Base body: pink-to-white with darker lower edges for volume */}
            <linearGradient id="heartBody" x1="0" y1="0" x2="0.6" y2="1">
              <stop offset="0%" stopColor="#fdf2f8" />
              <stop offset="30%" stopColor="#f9a8d4" />
              <stop offset="65%" stopColor="#ec4899" />
              <stop offset="100%" stopColor="#9d174d" />
            </linearGradient>

            {/* Strong specular highlight (upper-left) */}
            <radialGradient id="heartSpecular" cx="0.28" cy="0.22" r="0.45">
              <stop offset="0%" stopColor="rgba(255,255,255,0.95)" />
              <stop offset="45%" stopColor="rgba(255,255,255,0.35)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0)" />
            </radialGradient>

            {/* Softer secondary highlight (upper-right) */}
            <radialGradient id="heartSecondary" cx="0.72" cy="0.3" r="0.35">
              <stop offset="0%" stopColor="rgba(255,255,255,0.5)" />
              <stop offset="100%" stopColor="rgba(255,255,255,0)" />
            </radialGradient>

            {/* Inner shadow near center dip (two-lobe form) */}
            <linearGradient id="heartCleft" x1="0.5" y1="0" x2="0.5" y2="1">
              <stop offset="0%" stopColor="rgba(0,0,0,0)" />
              <stop offset="35%" stopColor="rgba(0,0,0,0.28)" />
              <stop offset="70%" stopColor="rgba(0,0,0,0)" />
            </linearGradient>

            {/* Darker lower-edge shading for curvature */}
            <linearGradient id="heartLower" x1="0" y1="0.6" x2="0" y2="1">
              <stop offset="0%" stopColor="rgba(0,0,0,0)" />
              <stop offset="100%" stopColor="rgba(0,0,0,0.35)" />
            </linearGradient>

            <filter id="heartBlur" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2" />
            </filter>
          </defs>

          {/* Heart path */}
          <path
            d="M100 170 C 40 120, 10 80, 10 50 C 10 22, 34 6, 58 6 C 76 6, 92 16, 100 30 C 108 16, 124 6, 142 6 C 166 6, 190 22, 190 50 C 190 80, 160 120, 100 170 Z"
            fill="url(#heartBody)"
          />

          {/* Strong specular highlight (upper-left) */}
          <path
            d="M100 170 C 40 120, 10 80, 10 50 C 10 22, 34 6, 58 6 C 76 6, 92 16, 100 30 C 108 16, 124 6, 142 6 C 166 6, 190 22, 190 50 C 190 80, 160 120, 100 170 Z"
            fill="url(#heartSpecular)"
          />

          {/* Softer secondary highlight (upper-right) */}
          <path
            d="M100 170 C 40 120, 10 80, 10 50 C 10 22, 34 6, 58 6 C 76 6, 92 16, 100 30 C 108 16, 124 6, 142 6 C 166 6, 190 22, 190 50 C 190 80, 160 120, 100 170 Z"
            fill="url(#heartSecondary)"
          />

          {/* Inner shadow near center dip */}
          <path
            d="M100 170 C 40 120, 10 80, 10 50 C 10 22, 34 6, 58 6 C 76 6, 92 16, 100 30 C 108 16, 124 6, 142 6 C 166 6, 190 22, 190 50 C 190 80, 160 120, 100 170 Z"
            fill="url(#heartCleft)"
          />

          {/* Darker lower-edge shading for curvature */}
          <path
            d="M100 170 C 40 120, 10 80, 10 50 C 10 22, 34 6, 58 6 C 76 6, 92 16, 100 30 C 108 16, 124 6, 142 6 C 166 6, 190 22, 190 50 C 190 80, 160 120, 100 170 Z"
            fill="url(#heartLower)"
          />

          {/* Small crisp specular dot */}
          <ellipse
            cx="58"
            cy="34"
            rx="12"
            ry="8"
            fill="rgba(255,255,255,0.85)"
            transform="rotate(-20 58 34)"
            filter="url(#heartBlur)"
          />

          {/* Bottom rim light */}
          <path
            d="M100 170 C 40 120, 10 80, 10 50"
            fill="none"
            stroke="rgba(255,255,255,0.22)"
            strokeWidth="3"
            strokeLinecap="round"
            filter="url(#heartBlur)"
          />
        </svg>
      </div>
    </div>
  );
}

/* ---------- Floating glass cards (gradient border, icons, independent float) ---------- */

function GlassCard({
  className,
  floatClass,
  children,
}: {
  className?: string;
  floatClass: string;
  children: React.ReactNode;
}) {
  return (
    <div
      className={`gradient-border absolute z-10 rounded-3xl p-4 shadow-[0_16px_40px_rgba(0,0,0,0.55)] backdrop-blur-xl ${floatClass} ${className ?? ""}`}
    >
      {children}
    </div>
  );
}

/* ---------- Relationship-type dropdown ---------- */

function RelationshipDropdown({
  selected,
  onSelect,
}: {
  selected: string | null;
  onSelect: (label: string) => void;
}) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className="relative"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
    >
      <button className="flex items-center gap-1 text-sm text-white/70 transition-colors hover:text-white">
        {selected ?? "For couples"}
        <svg viewBox="0 0 20 20" className="h-4 w-4 fill-current">
          <path
            fillRule="evenodd"
            d="M5.23 7.21a.75.75 0 011.06.02L10 11.17l3.71-3.94a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
            clipRule="evenodd"
          />
        </svg>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8, scaleY: 0.95 }}
            animate={{ opacity: 1, y: 0, scaleY: 1 }}
            exit={{ opacity: 0, y: -8, scaleY: 0.95 }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className="absolute left-0 top-full z-30 mt-2 w-72 origin-top rounded-2xl border border-white/10 bg-black/70 p-3 shadow-[0_12px_40px_rgba(0,0,0,0.6)] backdrop-blur-2xl"
            style={{ boxShadow: "0 0 0 1px rgba(236,72,153,0.3), 0 0 30px rgba(236,72,153,0.15)" }}
          >
            <div className="grid grid-cols-2 gap-1.5">
              {RELATIONSHIP_TYPES.map((rt) => {
                const isActive = selected === rt.label;
                return (
                  <button
                    key={rt.label}
                    onClick={() => {
                      onSelect(rt.label);
                      setOpen(false);
                    }}
                    className={`flex items-center gap-2.5 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-150 ${
                      isActive
                        ? "bg-pink-accent/20 text-pink-accent"
                        : "text-white/70 hover:scale-[1.03] hover:bg-pink-accent/10 hover:text-white"
                    }`}
                  >
                    <span className="text-base">{rt.icon}</span>
                    {rt.label}
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ---------- Conversation modal ---------- */

function ConversationModal({
  isOpen,
  onClose,
  relationshipType,
}: {
  isOpen: boolean;
  onClose: () => void;
  relationshipType: string | null;
}) {
  const [text, setText] = useState("");

  const hasText = text.trim().length > 0;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm"
          onClick={onClose}
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.92, y: 20 }}
            transition={{ duration: 0.3, ease: "easeOut" }}
            onClick={(e) => e.stopPropagation()}
            className="relative w-full max-w-lg rounded-3xl border border-white/10 bg-black/70 p-8 shadow-[0_20px_60px_rgba(0,0,0,0.7)] backdrop-blur-2xl"
            style={{ boxShadow: "0 0 0 1px rgba(236,72,153,0.25), 0 0 40px rgba(236,72,153,0.12)" }}
          >
            {/* Close button */}
            <button
              onClick={onClose}
              className="absolute right-5 top-5 flex h-8 w-8 items-center justify-center rounded-full text-white/40 transition-colors hover:bg-white/10 hover:text-white"
            >
              <svg viewBox="0 0 24 24" className="h-5 w-5 fill-current">
                <path
                  fillRule="evenodd"
                  d="M5.47 5.47a.75.75 0 011.06 0L12 10.94l5.47-5.47a.75.75 0 111.06 1.06L13.06 12l5.47 5.47a.75.75 0 11-1.06 1.06L12 13.06l-5.47 5.47a.75.75 0 01-1.06-1.06L10.94 12 5.47 6.53a.75.75 0 010-1.06z"
                  clipRule="evenodd"
                />
              </svg>
            </button>

            {/* Relationship type pill */}
            {relationshipType && (
              <div className="mb-4">
                <span className="inline-flex items-center gap-1.5 rounded-full border border-pink-accent/30 bg-pink-accent/10 px-3 py-1 text-xs font-medium text-pink-accent">
                  <span className="h-1.5 w-1.5 rounded-full bg-pink-accent" />
                  {relationshipType}
                </span>
              </div>
            )}

            {/* Title */}
            <h2 className="text-2xl font-bold text-white">What's on your mind?</h2>

            {/* Textarea */}
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Tell us what's going on in your relationship..."
              rows={5}
              className="mt-5 w-full resize-none rounded-2xl border border-white/10 bg-white/5 p-4 text-sm leading-relaxed text-white placeholder-white/30 outline-none transition-colors focus:border-pink-accent/50 focus:ring-1 focus:ring-pink-accent/30"
            />

            {/* Continue button + helper text */}
            <div className="mt-5 flex items-center justify-between">
              <p className="text-xs text-white/40">This stays private between you and Parista</p>
              <button
                disabled={!hasText}
                className={`rounded-full px-6 py-2.5 text-sm font-semibold transition-all duration-200 ${
                  hasText
                    ? "bg-gradient-to-r from-pink-accent to-rose-accent text-white shadow-lg shadow-pink-accent/30 hover:scale-105 hover:brightness-110"
                    : "bg-white/10 text-white/30 cursor-not-allowed"
                }`}
              >
                Continue
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/* ---------- Navbar (scroll-aware translucent bg) ---------- */

function Navbar({
  relationshipType,
  onSelectRelationship,
}: {
  relationshipType: string | null;
  onSelectRelationship: (label: string) => void;
}) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 24);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <motion.header
      initial={{ opacity: 0, y: -16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`sticky top-0 z-40 mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4 transition-all duration-300 ${
        scrolled ? "bg-black/60 backdrop-blur-xl" : "bg-transparent"
      }`}
    >
      {/* Logo */}
      <a href="#" className="flex items-center gap-2.5">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-pink-accent to-rose-accent shadow-lg shadow-pink-accent/30">
          <svg viewBox="0 0 24 24" className="h-5 w-5 fill-white">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
        </span>
        <span className="text-xl font-bold tracking-tight text-white">parista</span>
      </a>

      {/* Center nav */}
      <nav className="hidden items-center gap-8 md:flex">
        <a
          href="#"
          className="animated-underline text-sm text-white/70 transition-colors hover:text-white"
        >
          How it works
        </a>
        <a
          href="#"
          className="animated-underline text-sm text-white/70 transition-colors hover:text-white"
        >
          Resources
        </a>
        <RelationshipDropdown selected={relationshipType} onSelect={onSelectRelationship} />
      </nav>

      {/* Right side */}
      <div className="flex items-center gap-4">
        <a
          href="#"
          className="animated-underline hidden text-sm text-white/70 transition-colors hover:text-white sm:block"
        >
          Log in
        </a>
        <a
          href="#"
          className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-ink transition-all duration-200 hover:scale-[1.03] hover:shadow-[0_8px_24px_rgba(255,255,255,0.25)]"
        >
          Get started
        </a>
      </div>
    </motion.header>
  );
}

/* ---------- Hero ---------- */

function Hero({ onStartJourney }: { onStartJourney: () => void }) {
  const reduceMotion = useReducedMotion();

  const fadeUp = (delay: number) => ({
    initial: reduceMotion ? { opacity: 1 } : { opacity: 0, y: 24 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.7, delay, ease: "easeOut" as const },
  });

  return (
    <section className="relative z-10 mx-auto grid w-full max-w-6xl grid-cols-1 items-center gap-12 px-6 pb-16 pt-12 md:grid-cols-2 md:pb-24 md:pt-20">
      {/* Left column */}
      <div className="flex flex-col items-start gap-7">
        {/* Badge */}
        <motion.div
          {...fadeUp(0.1)}
          className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 backdrop-blur-md"
        >
          <svg viewBox="0 0 24 24" className="h-4 w-4 fill-pink-accent">
            <path d="M12 2l1.9 5.7L19.6 9.6l-5.7 1.9L12 17.2l-1.9-5.7L4.4 9.6l5.7-1.9L12 2z" />
          </svg>
          <span className="text-sm font-medium text-white/80">Relationship clarity, reimagined</span>
        </motion.div>

        {/* Headline — tighter line-height */}
        <motion.h1
          {...fadeUp(0.2)}
          className="text-5xl font-extrabold leading-[1.02] tracking-tight sm:text-6xl lg:text-[72px]"
        >
          <span className="block text-white">Make space for what</span>
          <span className="block bg-gradient-to-r from-pink-accent via-rose-accent to-pink-accent bg-clip-text text-transparent">
            matters most.
          </span>
        </motion.h1>

        {/* Subtext — more line-height for readability */}
        <motion.p
          {...fadeUp(0.3)}
          className="max-w-md text-lg leading-relaxed text-white/50"
        >
          Parista helps you navigate the moments that matter — with grounded,
          research-backed guidance and gentle rituals that bring you closer.
        </motion.p>

        {/* CTA row */}
        <motion.div
          {...fadeUp(0.4)}
          className="flex flex-wrap items-center gap-6"
        >
          <button
            onClick={onStartJourney}
            className="group flex cursor-pointer items-center gap-2 rounded-full bg-gradient-to-r from-pink-accent to-rose-accent px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-pink-accent/30 transition-all duration-200 hover:scale-[1.03] hover:shadow-[0_12px_32px_rgba(236,72,153,0.45)]"
          >
            Start your journey
            <svg
              viewBox="0 0 20 20"
              className="h-4 w-4 fill-current transition-transform duration-200 group-hover:translate-x-0.5"
            >
              <path
                fillRule="evenodd"
                d="M3 10a.75.75 0 01.75-.75h10.19L9.22 5.03a.75.75 0 111.06-1.06l6.5 6.5a.75.75 0 010 1.06l-6.5 6.5a.75.75 0 11-1.06-1.06l4.72-4.72H3.75A.75.75 0 013 10z"
                clipRule="evenodd"
              />
            </svg>
          </button>
          <a
            href="#"
            className="animated-underline text-base font-medium text-white/70 transition-colors hover:text-white"
          >
            See how it works
          </a>
        </motion.div>

        {/* Feature tag */}
        <motion.div
          {...fadeUp(0.5)}
          className="flex items-center gap-2.5"
        >
          <span className="h-2 w-2 rounded-full bg-pink-accent shadow-[0_0_12px_rgba(236,72,153,0.8)]" />
          <span className="text-sm text-white/50">Gentle daily rituals</span>
        </motion.div>
      </div>

      {/* Right column */}
      <motion.div
        initial={reduceMotion ? { opacity: 1 } : { opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8, delay: 0.3, ease: "easeOut" }}
        className="relative flex items-center justify-center py-10 md:py-0"
      >
        <GlassHeart />

        {/* Floating card — top-left (phone-off icon, independent float) */}
        <GlassCard floatClass="animate-card-float-a" className="left-0 top-6 w-[270px] md:-left-2 md:top-10">
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-pink-accent" />
            <span className="text-[10px] font-semibold tracking-widest text-pink-accent">TODAY</span>
          </div>
          <div className="mt-2 flex items-start gap-2">
            <svg viewBox="0 0 24 24" className="mt-0.5 h-4 w-4 shrink-0 fill-pink-accent">
              <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z" />
              <path d="M22 6.5l-1.5-1.5-2.5 2.5-2.5-2.5L14 6.5l2.5 2.5L14 11.5l1.5 1.5 2.5-2.5 2.5 2.5 1.5-1.5-2.5-2.5 2.5-2.5z" />
            </svg>
            <div>
              <p className="text-sm font-bold text-white">Plan a no-phone dinner</p>
              <p className="mt-0.5 text-xs text-gray-300">Just the two of you</p>
            </div>
          </div>
        </GlassCard>

        {/* Floating card — bottom-right, overlapping heart (independent float) */}
        <GlassCard floatClass="animate-card-float-b" className="bottom-2 right-0 w-[270px] md:-right-4 md:bottom-8">
          <div className="flex items-center gap-2">
            <svg viewBox="0 0 24 24" className="h-4 w-4 shrink-0 fill-pink-accent">
              <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
            </svg>
            <span className="whitespace-nowrap text-[10px] font-semibold tracking-[0.12em] text-pink-accent">
              YOUR WEEK TOGETHER
            </span>
          </div>
          <p className="mt-2 text-sm font-bold text-white">
            Feeling connected{" "}
            <svg viewBox="0 0 20 20" className="inline h-4 w-4 fill-pink-accent">
              <path
                fillRule="evenodd"
                d="M3 10a.75.75 0 01.75-.75h10.19L9.22 5.03a.75.75 0 111.06-1.06l6.5 6.5a.75.75 0 010 1.06l-6.5 6.5a.75.75 0 11-1.06-1.06l4.72-4.72H3.75A.75.75 0 013 10z"
                clipRule="evenodd"
              />
            </svg>
          </p>
        </GlassCard>
      </motion.div>
    </section>
  );
}

/* ---------- Trust / social proof strip ---------- */

function TrustStrip() {
  const items = [
    "Research-backed guidance",
    "Gentle daily rituals",
    "Built for real conversations",
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7, delay: 0.6, ease: "easeOut" }}
      className="relative z-10 mx-auto flex w-full max-w-6xl flex-wrap items-center justify-center gap-x-10 gap-y-3 px-6 pb-16 md:pb-20"
    >
      {items.map((item, i) => (
        <div key={item} className="flex items-center gap-2.5">
          <span className="h-1.5 w-1.5 rounded-full bg-pink-accent/70" />
          <span className="text-sm text-white/40">{item}</span>
          {i < items.length - 1 && (
            <span className="ml-10 hidden h-4 w-px bg-white/10 md:block" />
          )}
        </div>
      ))}
    </motion.div>
  );
}

/* ---------- Landing page ---------- */

export default function LandingPage() {
  const [relationshipType, setRelationshipType] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);

  return (
    <div className="grain relative min-h-screen overflow-hidden bg-ink">
      {/* Pink radial glow from center-right */}
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 60% 50% at 70% 40%, rgba(236,72,153,0.18) 0%, rgba(244,63,94,0.08) 40%, transparent 70%)",
        }}
      />

      {/* Atmospheric gradient blobs */}
      <GradientBlobs />

      {/* Twinkling hearts */}
      <TwinklingHearts />

      <Navbar relationshipType={relationshipType} onSelectRelationship={setRelationshipType} />
      <Hero onStartJourney={() => setModalOpen(true)} />
      <TrustStrip />

      <ConversationModal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        relationshipType={relationshipType}
      />
    </div>
  );
}