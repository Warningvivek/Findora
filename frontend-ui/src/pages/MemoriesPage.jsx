import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, BookOpen } from 'lucide-react'
import { memoriesService } from '../services/api'
import MemoryCard from '../components/MemoryCard'
import EmptyState from '../components/EmptyState'
import { SkeletonGrid } from '../components/Skeleton'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function MemoriesPage() {
  const [memories, setMemories] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await memoriesService.getAll()
      setMemories(data.items || [])
    } catch {
      toast.error('Failed to load memories')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleFavorite(id) {
    try {
      await memoriesService.toggleFavorite(id)
      setMemories((prev) => prev.map((m) => m.id === id ? { ...m, is_favorite: !m.is_favorite } : m))
    } catch { toast.error('Failed to update') }
  }

  async function handleDelete(id) {
    try {
      await memoriesService.delete(id)
      setMemories((prev) => prev.filter((m) => m.id !== id))
      toast.success('Memory deleted')
    } catch { toast.error('Failed to delete') }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 pt-10 pb-12">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-8"
      >
        <div>
          <h1 className="font-display font-bold text-3xl text-ink mb-1">All Memories</h1>
          <p className="font-body text-ink-muted text-sm">
            {loading ? '...' : `${memories.length} item${memories.length !== 1 ? 's' : ''} stored`}
          </p>
        </div>
        <button
          onClick={load}
          disabled={loading}
          className="btn-ghost px-4 py-2 rounded-xl flex items-center gap-2 text-sm"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </motion.div>

      {loading ? (
        <SkeletonGrid count={6} />
      ) : memories.length === 0 ? (
        <EmptyState
          type="memories"
          title="No memories yet"
          description="Upload files or write notes to start building your second brain."
          action={
            <button
              onClick={() => navigate('/upload')}
              className="btn-primary px-6 py-2.5 rounded-xl text-sm font-display font-semibold"
            >
              Add your first memory
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {memories.map((m, i) => (
            <MemoryCard
              key={m.id}
              memory={m}
              onFavorite={handleFavorite}
              onDelete={handleDelete}
              delay={i * 0.04}
            />
          ))}
        </div>
      )}
    </div>
  )
}
