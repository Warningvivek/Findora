import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { Star, RefreshCw } from 'lucide-react'
import { memoriesService } from '../services/api'
import MemoryCard from '../components/MemoryCard'
import EmptyState from '../components/EmptyState'
import { SkeletonGrid } from '../components/Skeleton'
import { useNavigate } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function FavoritesPage() {
  const [favorites, setFavorites] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const load = useCallback(async () => {
    setLoading(true)
    try {
      // getAll() returns a plain array — filter favorites client-side
      const data = await memoriesService.getAll()
      const all = Array.isArray(data) ? data : (data.items ?? data.memories ?? [])
      setFavorites(all.filter((m) => m.is_favorite === true))
    } catch {
      toast.error('Failed to load favorites')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  async function handleFavorite(id) {
    try {
      await memoriesService.toggleFavorite(id)
      setFavorites((prev) => prev.filter((m) => m.id !== id))
      toast.success('Removed from favorites')
    } catch {
      toast.error('Failed to update')
    }
  }

  async function handleDelete(id) {
    try {
      await memoriesService.delete(id)
      setFavorites((prev) => prev.filter((m) => m.id !== id))
      toast.success('Memory deleted')
    } catch {
      toast.error('Failed to delete')
    }
  }

  return (
    <div className="max-w-4xl mx-auto px-6 pt-10 pb-12">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between mb-8"
      >
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Star className="w-5 h-5 text-gold" fill="currentColor" />
            <h1 className="font-display font-bold text-3xl text-ink">Favorites</h1>
          </div>
          <p className="font-body text-ink-muted text-sm">
            {loading ? '...' : `${favorites.length} starred item${favorites.length !== 1 ? 's' : ''}`}
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
        <SkeletonGrid count={4} />
      ) : favorites.length === 0 ? (
        <EmptyState
          type="favorites"
          title="No favorites yet"
          description="Star any memory to pin it here for quick access."
          action={
            <button
              onClick={() => navigate('/memories')}
              className="btn-primary px-6 py-2.5 rounded-xl text-sm font-display font-semibold"
            >
              Browse memories
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {favorites.map((m, i) => (
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
