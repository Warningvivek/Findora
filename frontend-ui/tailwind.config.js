/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body: ['DM Sans', 'sans-serif'],
      },
      colors: {
        void: '#050507',
        surface: '#0c0c10',
        panel: '#121218',
        card: '#18181f',
        border: '#1e1e28',
        muted: '#2a2a38',
        // keep original accent for all existing component classes
        accent: '#7c6aff',
        'accent-soft': '#4a3fbf',
        'accent-glow': 'rgba(124,106,255,0.15)',
        teal: '#00e5cc',
        coral: '#ff6b6b',
        gold: '#ffd166',
        ink: '#e8e8f0',
        'ink-muted': '#8888a0',
        'ink-dim': '#44445a',
        // ── Findora brand spectrum (blue → violet → pink) ──────────────
        brand: {
          blue:    '#4fc3f7',
          violet:  '#7c6aff',
          pink:    '#f06292',
          magenta: '#e040fb',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        // Findora brand gradient
        'brand-gradient': 'linear-gradient(135deg, #4fc3f7 0%, #7c6aff 55%, #f06292 100%)',
        'noise': "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.4'/%3E%3C/svg%3E\")",
      },
      boxShadow: {
        'glow': '0 0 40px rgba(124,106,255,0.15)',
        'glow-sm': '0 0 20px rgba(124,106,255,0.1)',
        'glow-brand': '0 0 40px rgba(79,195,247,0.18)',
        'card': '0 4px 24px rgba(0,0,0,0.4)',
        'card-hover': '0 8px 40px rgba(0,0,0,0.6)',
      },
      animation: {
        'float': 'float 6s ease-in-out infinite',
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'slide-up': 'slideUp 0.4s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
        'spin-slow': 'spin 3s linear infinite',
        'orb-drift': 'orbDrift 12s ease-in-out infinite',
        'logo-ring': 'logoRing 3s ease-in-out infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        slideUp: {
          '0%': { opacity: 0, transform: 'translateY(20px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: 0 },
          '100%': { opacity: 1 },
        },
        orbDrift: {
          '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
          '33%':       { transform: 'translate(25px, -20px) scale(1.06)' },
          '66%':       { transform: 'translate(-18px, 14px) scale(0.96)' },
        },
        logoRing: {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%':      { opacity: '0.75', transform: 'scale(1.04)' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
}
