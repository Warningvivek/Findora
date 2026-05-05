import { useState } from 'react'
import { motion } from 'framer-motion'
import { Star, Trash2, FileText, Image, File, Hash, Calendar, ChevronDown, ChevronUp } from 'lucide-react'
import clsx from 'clsx'

const TYPE_CONFIG = {
  pdf: { icon: File, color: 'text-coral', bg: 'bg-coral/10', label: 'PDF' },
  image: { icon: Image, color: 'text-teal', bg: 'bg-teal/10', label: 'Image' },
  note: { icon: FileText, color: 'text-gold', bg: 'bg-gold/10', label: 'Note' },
  txt: { icon: FileText, color: 'text-accent', bg: 'bg-accent/10', label: 'Text' },
  default: { icon: File, color: 'text-ink-muted', bg: 'bg-muted/40', label: 'File' },
}

function getTypeConfig(type) {
  return TYPE_CONFIG[type?.toLowerCase()] || TYPE_CONFIG.default
}

function ScoreBadge({ score }) {
  if (score == null) return null
  const pct = Math.round(score * 100)
  const color = pct >= 80 ? 'text-teal' : pct >= 60 ? 'text-accent' : 'text-ink-muted'
  return (
    <span className={clsx('score-badge text-xs font-display font-semibold px-2 py-0.5 rounded-full', color)}>
      {pct}%
    </span>
  )
}

export default function MemoryCard({ memory, onFavorite, onDelete, delay = 0, showScore = false }) {
  const [expanded, setExpanded] = useState(false)
  const [favoriteLoading, setFavoriteLoading] = useState(false)
  const [deleteConfirm, setDeleteConfirm] = useState(false)

  const cfg = getTypeConfig(memory.source_type)
  const Icon = cfg.icon

  const snippet =
  memory.snippet ||
  memory.content?.slice(0, 200) ||
  'No content available.'
  const hasMore = (memory.content || memory.snippet)?.length > 200

  async function handleFavorite(e) {
    e.stopPropagation()
    setFavoriteLoading(true)
    try { await onFavorite(memory.id) } finally { setFavoriteLoading(false) }
  }

  async function handleDelete(e) {
    e.stopPropagation()
    if (!deleteConfirm) { setDeleteConfirm(true); return }
    await onDelete(memory.id)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35, delay, ease: 'easeOut' }}
      className="glass rounded-2xl p-5 hover-lift hover-glow cursor-default group"
    >
      {/* Header row */}
      <div className="flex items-start gap-3 mb-3">
        <div className={clsx('w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5', cfg.bg)}>
          <Icon className={clsx('w-4 h-4', cfg.color)} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-display font-semibold text-ink text-sm truncate leading-snug">
              {memory.title || 'Untitled Memory'}
            </h3>
            {showScore && <ScoreBadge score={memory.score} />}
          </div>
          <div className="flex items-center gap-2 mt-1">
            <span className={clsx('tag-chip', cfg.color)}>{cfg.label}</span>
            {memory.created_at && (
              <span className="flex items-center gap-1 text-ink-dim text-xs">
                <Calendar className="w-3 h-3" />
                {new Date(memory.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={handleFavorite}
            disabled={favoriteLoading}
            className={clsx(
              'p-1.5 rounded-lg transition-all',
              memory.is_favorite
                ? 'text-gold bg-gold/10'
                : 'text-ink-dim hover:text-gold hover:bg-gold/10'
            )}
            title={memory.is_favorite ? 'Unfavorite' : 'Favorite'}
          >
            {favoriteLoading
              ? <div className="w-3.5 h-3.5 border border-gold/50 border-t-gold rounded-full animate-spin" />
              : <Star className="w-3.5 h-3.5" fill={memory.is_favorite ? 'currentColor' : 'none'} />
            }
          </button>

          <button
            onClick={handleDelete}
            className={clsx(
              'p-1.5 rounded-lg transition-all',
              deleteConfirm
                ? 'text-coral bg-coral/20 animate-pulse'
                : 'text-ink-dim hover:text-coral hover:bg-coral/10'
            )}
            title={deleteConfirm ? 'Click again to confirm' : 'Delete'}
            onBlur={() => setTimeout(() => setDeleteConfirm(false), 300)}
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Content snippet */}
      <p className={clsx(
        'font-body text-ink-muted text-sm leading-relaxed',
        !expanded && 'line-clamp-3'
      )}>
        {expanded ? memory.content : snippet}
      </p>

      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-1 mt-2 text-accent text-xs font-body hover:text-accent/80 transition-colors"
        >
          {expanded ? <><ChevronUp className="w-3 h-3" /> Show less</> : <><ChevronDown className="w-3 h-3" /> Show more</>}
        </button>
      )}
    </motion.div>
  )
}
