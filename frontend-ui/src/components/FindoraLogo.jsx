// src/components/FindoraLogo.jsx
// Glassmorphic gradient magnify logo — matches the uploaded brand reference image.
// Props:
//   size      — number, controls overall diameter of the icon (default 40)
//   showText  — boolean, show wordmark beside icon (default true)
//   className — extra classes on the wrapper

export default function FindoraLogo({ size = 40, showText = true, className = '' }) {
  // Unique IDs so multiple instances on the same page don't clash
  const uid = 'fl'

  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>

      {/* ── Icon ──────────────────────────────────────────────────────── */}
      <div style={{ width: size, height: size }} className="relative flex-shrink-0">
        <svg
          viewBox="0 0 80 80"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{ width: size, height: size, overflow: 'visible' }}
        >
          <defs>
            {/* Soft ambient glow behind the sphere */}
            <radialGradient id={`${uid}-ambient`} cx="50%" cy="50%" r="50%">
              <stop offset="0%"   stopColor="#4fc3f7" stopOpacity="0.5"  />
              <stop offset="35%"  stopColor="#7c6aff" stopOpacity="0.32" />
              <stop offset="65%"  stopColor="#f06292" stopOpacity="0.22" />
              <stop offset="100%" stopColor="#f06292" stopOpacity="0"    />
            </radialGradient>

            {/* Glass sphere fill */}
            <radialGradient id={`${uid}-glass`} cx="35%" cy="28%" r="70%">
              <stop offset="0%"   stopColor="#8899ff" stopOpacity="0.60" />
              <stop offset="55%"  stopColor="#6070f0" stopOpacity="0.38" />
              <stop offset="100%" stopColor="#3a3fbf" stopOpacity="0.20" />
            </radialGradient>

            {/* Glass specular highlight */}
            <radialGradient id={`${uid}-highlight`} cx="28%" cy="22%" r="55%">
              <stop offset="0%"   stopColor="#ffffff" stopOpacity="0.32" />
              <stop offset="100%" stopColor="#ffffff" stopOpacity="0"    />
            </radialGradient>

            {/* Ambient glow blur filter */}
            <filter id={`${uid}-blurAmb`} x="-60%" y="-60%" width="220%" height="220%">
              <feGaussianBlur stdDeviation="7" />
            </filter>

            {/* Icon glow filter */}
            <filter id={`${uid}-iconGlow`} x="-25%" y="-25%" width="150%" height="150%">
              <feGaussianBlur stdDeviation="1.4" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>

            {/* Orange-pink orb gradient */}
            <radialGradient id={`${uid}-orbOrange`} cx="40%" cy="35%" r="60%">
              <stop offset="0%"   stopColor="#ff9a4c" />
              <stop offset="100%" stopColor="#f06292" />
            </radialGradient>
          </defs>

          {/* 1 — Ambient glow blob (blurred ellipse) */}
          <ellipse
            cx="40" cy="40" rx="38" ry="35"
            fill={`url(#${uid}-ambient)`}
            filter={`url(#${uid}-blurAmb)`}
          />

          {/* 2 — Glass sphere */}
          <circle
            cx="40" cy="40" r="27"
            fill={`url(#${uid}-glass)`}
            stroke="rgba(255,255,255,0.16)"
            strokeWidth="1"
          />

          {/* 3 — Glass specular */}
          <circle cx="40" cy="40" r="27" fill={`url(#${uid}-highlight)`} />

          {/* 4 — Search icon + rays */}
          <g filter={`url(#${uid}-iconGlow)`}>
            {/* Radiating dashes — 8 directions */}
            {[0, 45, 90, 135, 180, 225, 270, 315].map((deg) => {
              const rad = (deg * Math.PI) / 180
              const cx = 37, cy = 36
              return (
                <line
                  key={deg}
                  x1={cx + 13 * Math.cos(rad)}
                  y1={cy + 13 * Math.sin(rad)}
                  x2={cx + 17 * Math.cos(rad)}
                  y2={cy + 17 * Math.sin(rad)}
                  stroke="rgba(255,255,255,0.72)"
                  strokeWidth="2"
                  strokeLinecap="round"
                />
              )
            })}
            {/* Magnifying glass circle */}
            <circle
              cx="37" cy="36" r="7.5"
              stroke="rgba(255,255,255,0.95)"
              strokeWidth="2.4"
              fill="none"
            />
            {/* Handle */}
            <line
              x1="42.5" y1="42.5" x2="49.5" y2="49.5"
              stroke="rgba(255,255,255,0.95)"
              strokeWidth="2.4"
              strokeLinecap="round"
            />
          </g>

          {/* 5 — Outer dashed ring (pulse) */}
          <circle
            cx="40" cy="40" r="32"
            stroke="rgba(255,255,255,0.12)"
            strokeWidth="1"
            strokeDasharray="7 5"
            fill="none"
            className="logo-ring"
          />

          {/* 6 — Accent orbs */}
          {/* Blue top-right */}
          <circle cx="64" cy="20" r="4.2"  fill="#4fc3f7" opacity="0.92" />
          {/* Small blue right-middle */}
          <circle cx="63" cy="54" r="2.5"  fill="#4fc3f7" opacity="0.80" />
          {/* Translucent blue left */}
          <circle cx="17" cy="27" r="3.5"  fill="#4fc3f7" opacity="0.55" />
          {/* Orange-pink bottom-left */}
          <circle cx="21" cy="57" r="5.8"  fill={`url(#${uid}-orbOrange)`} opacity="0.92" />
        </svg>
      </div>

      {/* ── Wordmark ────────────────────────────────────────────────── */}
      {showText && (
        <div className="flex flex-col leading-none">
          <span
            className="gradient-text font-display font-bold tracking-tight"
            style={{ fontSize: size * 0.55 }}
          >
            Findora
          </span>
          <span
            className="font-body text-ink-dim"
            style={{
              fontSize: Math.max(9, size * 0.21),
              letterSpacing: '0.1em',
              marginTop: 2,
            }}
          >
            KNOWLEDGE SPACE
          </span>
        </div>
      )}
    </div>
  )
}
