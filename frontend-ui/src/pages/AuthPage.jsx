import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, Zap, Shield, Sparkles } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import FindoraLogo from '../components/FindoraLogo'
import toast from 'react-hot-toast'

const features = [
  { icon: Sparkles, label: 'Semantic Memory',  desc: 'AI-powered search across all your notes'  },
  { icon: Zap,      label: 'Instant Recall',   desc: 'Find anything in milliseconds'            },
  { icon: Shield,   label: 'Secure & Private', desc: 'Your data, your control'                  },
]

export default function AuthPage() {
  const [mode, setMode] = useState('login')

  const [regUsername, setRegUsername] = useState('')
  const [regEmail,    setRegEmail]    = useState('')
  const [regPassword, setRegPassword] = useState('')

  const [loginIdentifier, setLoginIdentifier] = useState('')
  const [loginPassword,   setLoginPassword]   = useState('')

  const [showPass, setShowPass] = useState(false)
  const [loading,  setLoading]  = useState(false)

  const { login, register, user } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (user) navigate('/search', { replace: true })
  }, [user, navigate])

  function switchMode(m) {
    setMode(m)
    setShowPass(false)
    setRegUsername(''); setRegEmail(''); setRegPassword('')
    setLoginIdentifier(''); setLoginPassword('')
  }

  async function handleSubmit(e) {
    e.preventDefault()

    if (mode === 'register') {
      if (!regUsername.trim()) { toast.error('Username is required'); return }
      if (!regEmail.trim())    { toast.error('Email is required'); return }
      if (!regEmail.includes('@')) { toast.error('Enter a valid email address'); return }
      if (!regPassword.trim()) { toast.error('Password is required'); return }
      if (regPassword.length < 6) { toast.error('Password must be at least 6 characters'); return }

      setLoading(true)
      try {
        await register(regUsername.trim(), regEmail.trim(), regPassword)
        toast.success('Account created! Please sign in.')
        switchMode('login')
      } catch (err) {
        toast.error(parseError(err))
      } finally {
        setLoading(false)
      }
    } else {
      if (!loginIdentifier.trim()) { toast.error('Username or email is required'); return }
      if (!loginPassword.trim())   { toast.error('Password is required'); return }

      setLoading(true)
      try {
        await login(loginIdentifier.trim(), loginPassword)
        navigate('/search', { replace: true })
      } catch (err) {
        toast.error(parseError(err))
      } finally {
        setLoading(false)
      }
    }
  }

  function parseError(err) {
    const detail = err.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) return detail.map(d => d.msg).join(', ')
    return 'Something went wrong. Please try again.'
  }

  return (
    <div className="min-h-screen bg-void flex overflow-hidden relative">

      {/* Background orbs — updated to Findora brand colours */}
      <div className="orb w-96 h-96 bg-brand-blue  opacity-[0.07] -top-32 -left-32" />
      <div className="orb w-80 h-80 bg-brand-pink  opacity-[0.05] bottom-0 right-1/4" />

      {/* ── Left panel — Branding ─────────────────────────────────────── */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 p-12 relative z-10">

        {/* Logo */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <FindoraLogo size={38} showText={true} />
        </motion.div>

        {/* Hero copy + feature cards */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="space-y-10"
        >
          <div>
            <h1 className="font-display text-5xl font-bold leading-tight text-ink mb-4">
              An intelligent space<br />
              <span className="gradient-text">where knowledge lives.</span>
            </h1>
            <p className="text-ink-muted font-body text-lg max-w-sm leading-relaxed">
              An intelligent space where your knowledge lives and responds instantly.
            </p>
          </div>

          <div className="space-y-4">
            {features.map(({ icon: Icon, label, desc }, i) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 + i * 0.1 }}
                className="flex items-start gap-4 glass rounded-2xl p-4"
              >
                <div className="w-9 h-9 rounded-xl bg-accent-glow flex items-center justify-center flex-shrink-0">
                  <Icon className="w-4 h-4 text-accent" />
                </div>
                <div>
                  <p className="font-display font-semibold text-ink text-sm">{label}</p>
                  <p className="font-body text-ink-dim text-xs mt-0.5">{desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <div className="text-ink-dim font-body text-xs">
          © 2025 Findora — Intelligent Knowledge Space
        </div>
      </div>

      {/* ── Right panel — Form ────────────────────────────────────────── */}
      <div className="flex-1 flex items-center justify-center p-8 relative z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >

          {/* Mobile logo */}
          <div className="mb-8 lg:hidden">
            <FindoraLogo size={32} showText={true} />
          </div>

          <div className="glass-strong rounded-3xl p-8">

            {/* Tab switcher */}
            <div className="flex rounded-xl bg-muted/50 p-1 mb-8">
              {['login', 'register'].map((m) => (
                <button
                  key={m}
                  onClick={() => switchMode(m)}
                  className={`flex-1 py-2 rounded-lg font-display font-semibold text-sm transition-all duration-200 ${
                    mode === m
                      ? 'bg-card text-ink shadow-card'
                      : 'text-ink-dim hover:text-ink-muted'
                  }`}
                >
                  {m === 'login' ? 'Sign In' : 'Sign Up'}
                </button>
              ))}
            </div>

            <AnimatePresence mode="wait">
              <motion.div
                key={mode}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.2 }}
              >
                <h2 className="font-display font-bold text-2xl text-ink mb-1">
                  {mode === 'login' ? 'Welcome back' : 'Create account'}
                </h2>
                <p className="text-ink-dim font-body text-sm mb-6">
                  {mode === 'login'
                    ? 'Sign in with your username or email'
                    : 'Fill in all details to get started'}
                </p>

                <form onSubmit={handleSubmit} className="space-y-4" noValidate>

                  {/* ── Register fields ── */}
                  {mode === 'register' && (
                    <>
                      <div>
                        <label className="block font-body text-ink-muted text-xs mb-1.5 ml-1">
                          Username
                        </label>
                        <input
                          type="text"
                          value={regUsername}
                          onChange={(e) => setRegUsername(e.target.value)}
                          placeholder="your_username"
                          className="input-focus w-full rounded-xl px-4 py-3 text-sm"
                          autoComplete="username"
                        />
                      </div>

                      <div>
                        <label className="block font-body text-ink-muted text-xs mb-1.5 ml-1">
                          Email
                        </label>
                        <input
                          type="email"
                          value={regEmail}
                          onChange={(e) => setRegEmail(e.target.value)}
                          placeholder="you@example.com"
                          className="input-focus w-full rounded-xl px-4 py-3 text-sm"
                          autoComplete="email"
                        />
                      </div>

                      <div>
                        <label className="block font-body text-ink-muted text-xs mb-1.5 ml-1">
                          Password
                        </label>
                        <div className="relative">
                          <input
                            type={showPass ? 'text' : 'password'}
                            value={regPassword}
                            onChange={(e) => setRegPassword(e.target.value)}
                            placeholder="min. 6 characters"
                            className="input-focus w-full rounded-xl px-4 py-3 text-sm pr-11"
                            autoComplete="new-password"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPass(!showPass)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-dim hover:text-ink-muted transition-colors"
                          >
                            {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </>
                  )}

                  {/* ── Login fields ── */}
                  {mode === 'login' && (
                    <>
                      <div>
                        <label className="block font-body text-ink-muted text-xs mb-1.5 ml-1">
                          Username or Email
                        </label>
                        <input
                          type="text"
                          value={loginIdentifier}
                          onChange={(e) => setLoginIdentifier(e.target.value)}
                          placeholder="your_username or you@example.com"
                          className="input-focus w-full rounded-xl px-4 py-3 text-sm"
                          autoComplete="username"
                        />
                      </div>

                      <div>
                        <label className="block font-body text-ink-muted text-xs mb-1.5 ml-1">
                          Password
                        </label>
                        <div className="relative">
                          <input
                            type={showPass ? 'text' : 'password'}
                            value={loginPassword}
                            onChange={(e) => setLoginPassword(e.target.value)}
                            placeholder="••••••••"
                            className="input-focus w-full rounded-xl px-4 py-3 text-sm pr-11"
                            autoComplete="current-password"
                          />
                          <button
                            type="button"
                            onClick={() => setShowPass(!showPass)}
                            className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-dim hover:text-ink-muted transition-colors"
                          >
                            {showPass ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                      </div>
                    </>
                  )}

                  <button
                    type="submit"
                    disabled={loading}
                    className="btn-primary w-full py-3 rounded-xl text-sm mt-2 flex items-center justify-center gap-2 disabled:opacity-60 disabled:cursor-not-allowed"
                  >
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        <span>{mode === 'login' ? 'Signing in...' : 'Creating account...'}</span>
                      </>
                    ) : (
                      mode === 'login' ? 'Sign In' : 'Create Account'
                    )}
                  </button>

                </form>
              </motion.div>
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  )
}
