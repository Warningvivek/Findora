import { useState, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Sparkles, SlidersHorizontal, X, ChevronDown } from 'lucide-react'
import { searchService, memoriesService } from '../services/api'
import MemoryCard from '../components/MemoryCard'
import EmptyState from '../components/EmptyState'
import { SkeletonGrid, SummarySkeleton } from '../components/Skeleton'
import toast from 'react-hot-toast'

const SOURCE_TYPES = ['all', 'note', 'pdf', 'image', 'txt']

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [showFilters, setShowFilters] = useState(false)
  const [maxResults, setMaxResults] = useState(10)
  const [sourceType, setSourceType] = useState('all')
  const inputRef = useRef(null)

  const handleSearch = useCallback(async (e) => {
    e?.preventDefault()
    const q = query.trim()
    if (!q) return

    setLoading(true)
    setSearched(true)
    setResults([])
    setSummary(null)

    try {
      const params = { max_results: maxResults }
      if (sourceType !== 'all') params.source_type = sourceType

      const data = await searchService.search(q, params)
      setResults(data.results || [])
      setSummary(data.summary || null)
    } catch (err) {
      toast.error('Search failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [query, maxResults, sourceType])

  function handleKeyDown(e) {
    if (e.key === 'Enter') handleSearch(e)
  }

  async function handleFavorite(id) {
    try {
      await memoriesService.toggleFavorite(id)
      setResults((prev) =>
        prev.map((m) => m.id === id ? { ...m, is_favorite: !m.is_favorite } : m)
      )
      toast.success('Updated!')
    } catch {
      toast.error('Failed to update')
    }
  }

  async function handleDelete(id) {
    try {
      await memoriesService.delete(id)
      setResults((prev) => prev.filter((m) => m.id !== id))
      toast.success('Memory deleted')
    } catch {
      toast.error('Failed to delete')
    }
  }

  return (
    <div className="min-h-full relative">
      {/* Background orbs */}
      <div className="orb w-[500px] h-[500px] bg-accent opacity-[0.04] top-0 left-1/2 -translate-x-1/2 -translate-y-1/2" />

      <div className="max-w-4xl mx-auto px-6 pt-16 pb-12">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-10"
        >
          <div className="flex items-center justify-center gap-2 mb-3">
            <Sparkles className="w-4 h-4 text-accent animate-pulse-slow" />
            <span className="font-body text-ink-dim text-sm">Semantic AI Search</span>
          </div>
          <h1 className="font-display font-bold text-4xl text-ink mb-2">
            What are you looking for?
          </h1>
          <p className="font-body text-ink-muted text-sm">
            Search across all your notes, PDFs, and images using natural language
          </p>
        </motion.div>

        {/* Search bar */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="relative mb-4"
        >
          <div className="glass-strong rounded-2xl flex items-center gap-3 px-5 py-4 focus-within:border-accent/40 border border-border transition-all duration-300 focus-within:shadow-glow">
            <Search className="w-5 h-5 text-ink-dim flex-shrink-0" />
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask anything about your memories..."
              className="flex-1 bg-transparent outline-none font-body text-ink placeholder-ink-dim text-base"
              autoFocus
            />
            {query && (
              <button onClick={() => setQuery('')} className="text-ink-dim hover:text-ink transition-colors">
                <X className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={handleSearch}
              disabled={!query.trim() || loading}
              className="btn-primary px-4 py-2 rounded-xl text-sm flex-shrink-0 disabled:opacity-50"
            >
              {loading ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Search'
              )}
            </button>
          </div>
        </motion.div>

        {/* Filters toggle */}
        <div className="flex justify-end mb-8">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2 font-body text-ink-muted text-sm hover:text-ink transition-colors"
          >
            <SlidersHorizontal className="w-3.5 h-3.5" />
            Filters
            <ChevronDown className={`w-3.5 h-3.5 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Filters panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden -mt-4 mb-6"
            >
              <div className="glass rounded-xl p-4 flex flex-wrap gap-4 items-center">
                <div className="flex items-center gap-2">
                  <span className="font-body text-ink-dim text-xs">Type:</span>
                  <div className="flex gap-1 flex-wrap">
                    {SOURCE_TYPES.map((t) => (
                      <button
                        key={t}
                        onClick={() => setSourceType(t)}
                        className={`px-3 py-1 rounded-lg font-body text-xs transition-all capitalize ${
                          sourceType === t
                            ? 'bg-accent text-white'
                            : 'bg-muted/50 text-ink-muted hover:text-ink hover:bg-muted'
                        }`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-auto">
                  <span className="font-body text-ink-dim text-xs">Max results:</span>
                  <select
                    value={maxResults}
                    onChange={(e) => setMaxResults(Number(e.target.value))}
                    className="bg-card border border-border rounded-lg px-2 py-1 font-body text-ink text-xs outline-none"
                  >
                    {[5, 10, 20, 50].map((n) => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Results area */}
        <AnimatePresence mode="wait">
          {loading && (
            <motion.div
              key="loading"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <SummarySkeleton />
              <SkeletonGrid count={4} />
            </motion.div>
          )}

          {!loading && searched && (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {/* AI Summary */}
              {summary && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="summary-card rounded-2xl p-5 mb-6"
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-4 h-4 text-accent" />
                    <span className="font-display font-semibold text-accent text-sm">AI Summary</span>
                  </div>
                  <p className="font-body text-ink-muted text-sm leading-relaxed">{summary}</p>
                </motion.div>
              )}

              {/* Count */}
              {results.length > 0 && (
                <div className="flex items-center justify-between mb-4">
                  <p className="font-body text-ink-dim text-sm">
                    Found <span className="text-ink font-medium">{results.length}</span> result{results.length !== 1 ? 's' : ''}
                    {' '}for <span className="text-accent">"{query}"</span>
                  </p>
                </div>
              )}

              {/* Cards grid */}
              {results.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {results.map((m, i) => (
                    <MemoryCard
                      key={m.id}
                      memory={m}
                      onFavorite={handleFavorite}
                      onDelete={handleDelete}
                      delay={i * 0.05}
                      showScore={true}
                    />
                  ))}
                </div>
              ) : (
                <EmptyState
                  type="search"
                  title="No results found"
                  description={`No memories matched "${query}". Try different keywords or upload more content.`}
                />
              )}
            </motion.div>
          )}

          {!loading && !searched && (
            <motion.div
              key="idle"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-center py-12"
            >
              <div className="flex flex-wrap gap-2 justify-center">
                {['Show me my notes on AI', 'Find that PDF about marketing', 'What did I write about productivity?'].map((s) => (
                  <button
                    key={s}
                    onClick={() => { setQuery(s); setTimeout(handleSearch, 50) }}
                    className="btn-ghost px-4 py-2 rounded-xl font-body text-sm"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
