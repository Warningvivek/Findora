export function CardSkeleton() {
  return (
    <div className="glass rounded-2xl p-5 animate-pulse">
      <div className="flex items-start gap-3">
        <div className="w-9 h-9 rounded-xl skeleton flex-shrink-0" />
        <div className="flex-1 space-y-2">
          <div className="h-4 skeleton rounded-lg w-3/4" />
          <div className="h-3 skeleton rounded-lg w-1/3" />
        </div>
      </div>
      <div className="mt-4 space-y-2">
        <div className="h-3 skeleton rounded w-full" />
        <div className="h-3 skeleton rounded w-5/6" />
        <div className="h-3 skeleton rounded w-4/6" />
      </div>
    </div>
  )
}

export function SkeletonGrid({ count = 4 }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  )
}

export function SummarySkeleton() {
  return (
    <div className="rounded-2xl border border-accent/20 bg-accent-glow/30 p-5 mb-6 animate-pulse">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-4 h-4 skeleton rounded" />
        <div className="h-3 skeleton rounded w-24" />
      </div>
      <div className="space-y-2">
        <div className="h-3 skeleton rounded w-full" />
        <div className="h-3 skeleton rounded w-5/6" />
        <div className="h-3 skeleton rounded w-4/6" />
      </div>
    </div>
  )
}
