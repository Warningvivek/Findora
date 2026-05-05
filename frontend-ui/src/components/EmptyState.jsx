import { motion } from 'framer-motion'

const ICONS = {
  search: (
    <svg viewBox="0 0 80 80" className="w-full h-full" fill="none">
      <circle cx="34" cy="34" r="20" stroke="currentColor" strokeWidth="3" strokeDasharray="4 3" className="text-muted" />
      <path d="M49 49L62 62" stroke="currentColor" strokeWidth="3" strokeLinecap="round" className="text-muted" />
      <path d="M28 34h12M34 28v12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-ink-dim" />
    </svg>
  ),
  memories: (
    <svg viewBox="0 0 80 80" className="w-full h-full" fill="none">
      <rect x="14" y="22" width="32" height="40" rx="4" stroke="currentColor" strokeWidth="2.5" className="text-muted" />
      <rect x="34" y="18" width="32" height="40" rx="4" stroke="currentColor" strokeWidth="2.5" className="text-ink-dim" />
      <path d="M22 34h16M22 42h10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-muted" />
    </svg>
  ),
  favorites: (
    <svg viewBox="0 0 80 80" className="w-full h-full" fill="none">
      <path d="M40 58L22 44c-5-4-7-12-3-17a12 12 0 0 1 17 0h8a12 12 0 0 1 17 0c4 5 2 13-3 17L40 58z"
        stroke="currentColor" strokeWidth="2.5" strokeLinejoin="round" className="text-muted" />
    </svg>
  ),
  upload: (
    <svg viewBox="0 0 80 80" className="w-full h-full" fill="none">
      <path d="M28 48 L40 36 L52 48" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="text-muted" />
      <path d="M40 36v24" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="text-muted" />
      <path d="M20 56a16 8 0 0 1 40 0" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="text-ink-dim" strokeDasharray="4 3" />
    </svg>
  ),
}

export default function EmptyState({ type = 'memories', title, description, action }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex flex-col items-center justify-center py-20 px-8 text-center"
    >
      <div className="w-24 h-24 mb-6 opacity-60">
        {ICONS[type] || ICONS.memories}
      </div>
      <h3 className="font-display font-semibold text-ink text-lg mb-2">{title}</h3>
      <p className="font-body text-ink-dim text-sm max-w-xs leading-relaxed mb-6">{description}</p>
      {action}
    </motion.div>
  )
}
