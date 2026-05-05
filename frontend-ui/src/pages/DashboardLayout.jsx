import { useState } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Upload, Star, BookOpen,
  LogOut, Menu, X, ChevronRight,
  Sparkles
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'
import FindoraLogo from '../components/FindoraLogo'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const NAV = [
  { to: '/search',    icon: Search,   label: 'Search'      },
  { to: '/upload',    icon: Upload,   label: 'Upload'      },
  { to: '/memories',  icon: BookOpen, label: 'All Memories' },
  { to: '/favorites', icon: Star,     label: 'Favorites'   },
]

function NavItem({ to, icon: Icon, label, onClick }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        clsx(
          'flex items-center gap-3 px-4 py-3 rounded-xl font-body text-sm transition-all duration-200 group',
          isActive
            ? 'bg-accent-glow text-accent border-r-2 border-accent'
            : 'text-ink-muted hover:text-ink hover:bg-muted/40'
        )
      }
    >
      <Icon className="w-4 h-4 flex-shrink-0" />
      <span>{label}</span>
      <ChevronRight className="w-3 h-3 ml-auto opacity-0 group-hover:opacity-50 transition-opacity" />
    </NavLink>
  )
}

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/auth', { replace: true })
    toast.success('Signed out successfully')
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full">

      {/* ── Logo ───────────────────────────────────────────────────── */}
      <div className="p-5 border-b border-border">
        <FindoraLogo size={34} showText={true} />
      </div>

      {/* ── Nav ────────────────────────────────────────────────────── */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        <p className="font-body text-ink-dim text-xs font-medium px-4 mb-2 mt-1 uppercase tracking-widest">
          Navigation
        </p>
        {NAV.map((item) => (
          <NavItem key={item.to} {...item} onClick={() => setSidebarOpen(false)} />
        ))}
      </nav>

      {/* ── User ───────────────────────────────────────────────────── */}
      <div className="p-4 border-t border-border">
        <div className="glass rounded-xl p-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-brand-blue/30 to-brand-violet/20 flex items-center justify-center flex-shrink-0">
            <span className="font-display font-bold text-brand-blue text-xs">
              {user?.username?.[0]?.toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="font-body font-medium text-ink text-xs truncate">{user?.username}</p>
            <p className="font-body text-ink-dim text-xs">Free plan</p>
          </div>
          <button
            onClick={handleLogout}
            className="text-ink-dim hover:text-coral transition-colors p-1 rounded-lg hover:bg-coral/10"
            title="Sign out"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-void flex">

      {/* Desktop sidebar */}
      <aside className="hidden lg:flex flex-col w-60 bg-surface border-r border-border flex-shrink-0 fixed top-0 left-0 h-full z-30">
        <SidebarContent />
      </aside>

      {/* Mobile sidebar overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-void/80 z-40 lg:hidden"
              onClick={() => setSidebarOpen(false)}
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 30, stiffness: 300 }}
              className="fixed top-0 left-0 h-full w-64 bg-surface border-r border-border z-50 lg:hidden"
            >
              <button
                onClick={() => setSidebarOpen(false)}
                className="absolute top-4 right-4 text-ink-dim hover:text-ink p-1"
              >
                <X className="w-5 h-5" />
              </button>
              <SidebarContent />
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div className="flex-1 flex flex-col lg:ml-60 min-h-screen">

        {/* Mobile top bar */}
        <header className="lg:hidden flex items-center gap-4 px-4 py-3 border-b border-border bg-surface/80 backdrop-blur-xl sticky top-0 z-20">
          <button onClick={() => setSidebarOpen(true)} className="text-ink-muted hover:text-ink">
            <Menu className="w-5 h-5" />
          </button>

          {/* Compact logo for mobile header */}
          <FindoraLogo size={28} showText={true} />

          <div className="ml-auto flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-accent animate-pulse-slow" />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
