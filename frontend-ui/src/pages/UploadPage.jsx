import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload, FileText, Image, File, X, CheckCircle, AlertCircle, Plus, Loader } from 'lucide-react'
import { memoriesService } from '../services/api'
import toast from 'react-hot-toast'
import clsx from 'clsx'

const ACCEPTED = {
  'application/pdf': ['.pdf'],
  'image/*': ['.jpg', '.jpeg', '.png', '.webp', '.gif'],
  'text/plain': ['.txt'],
}

function FileIcon({ type }) {
  if (type.startsWith('image')) return <Image className="w-4 h-4 text-teal" />
  if (type === 'application/pdf') return <File className="w-4 h-4 text-coral" />
  return <FileText className="w-4 h-4 text-accent" />
}

function FilePill({ file, status, onRemove }) {
  const sizeKB = (file.size / 1024).toFixed(1)
  return (
    <div className="flex items-center gap-3 glass rounded-xl px-4 py-3">
      <FileIcon type={file.type} />
      <div className="flex-1 min-w-0">
        <p className="font-body text-ink text-sm truncate">{file.name}</p>
        <p className="font-body text-ink-dim text-xs">{sizeKB} KB</p>
      </div>
      {status === 'pending' && (
        <button onClick={() => onRemove(file.name)} className="text-ink-dim hover:text-coral transition-colors">
          <X className="w-3.5 h-3.5" />
        </button>
      )}
      {status === 'uploading' && <Loader className="w-3.5 h-3.5 text-accent animate-spin" />}
      {status === 'done'      && <CheckCircle className="w-3.5 h-3.5 text-teal" />}
      {status === 'error'     && <AlertCircle className="w-3.5 h-3.5 text-coral" />}
    </div>
  )
}

export default function UploadPage() {
  const [files, setFiles]             = useState([])
  const [uploading, setUploading]     = useState(false)
  const [noteMode, setNoteMode]       = useState(false)
  const [noteTitle, setNoteTitle]     = useState('')
  const [noteContent, setNoteContent] = useState('')
  const [noteLoading, setNoteLoading] = useState(false)

  const onDrop = useCallback((accepted) => {
    setFiles((prev) => [...prev, ...accepted.map((f) => ({ file: f, status: 'pending' }))])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    multiple: true,
  })

  function removeFile(name) {
    setFiles((prev) => prev.filter((f) => f.file.name !== name))
  }

  async function uploadAll() {
    if (!files.length) return
    setUploading(true)
    for (const item of files) {
      if (item.status !== 'pending') continue
      setFiles((prev) => prev.map((f) => f.file.name === item.file.name ? { ...f, status: 'uploading' } : f))
      try {
        const fd = new FormData()
        fd.append('file', item.file)
        await memoriesService.create(fd)
        setFiles((prev) => prev.map((f) => f.file.name === item.file.name ? { ...f, status: 'done' } : f))
      } catch {
        setFiles((prev) => prev.map((f) => f.file.name === item.file.name ? { ...f, status: 'error' } : f))
      }
    }
    setUploading(false)
    toast.success('Upload complete!')
  }

  async function submitNote(e) {
    e.preventDefault()
    if (!noteContent.trim()) { toast.error('Note content is required'); return }
    setNoteLoading(true)
    try {
      // ✅ JSON to /api/memories/notes — NOT FormData to /api/memories/upload
      await memoriesService.createNote({
        title:   noteTitle.trim() || 'Untitled Note',
        content: noteContent.trim(),
      })
      toast.success('Note saved!')
      setNoteTitle('')
      setNoteContent('')
    } catch (err) {
      const detail = err.response?.data?.detail
      const msg = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map(d => d.msg).join(', ')
          : 'Failed to save note'
      toast.error(msg)
    } finally {
      setNoteLoading(false)
    }
  }

  const pendingCount = files.filter((f) => f.status === 'pending').length

  return (
    <div className="max-w-3xl mx-auto px-6 pt-10 pb-12">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-display font-bold text-3xl text-ink mb-1">Upload</h1>
        <p className="font-body text-ink-muted text-sm">Add files or write notes to your memory vault</p>
      </motion.div>

      {/* Mode tabs */}
      <div className="flex rounded-xl bg-muted/30 p-1 mb-8 w-fit">
        <button
          onClick={() => setNoteMode(false)}
          className={clsx(
            'px-5 py-2 rounded-lg font-body text-sm transition-all',
            !noteMode ? 'bg-card text-ink shadow-card' : 'text-ink-muted hover:text-ink'
          )}
        >
          File Upload
        </button>
        <button
          onClick={() => setNoteMode(true)}
          className={clsx(
            'px-5 py-2 rounded-lg font-body text-sm transition-all',
            noteMode ? 'bg-card text-ink shadow-card' : 'text-ink-muted hover:text-ink'
          )}
        >
          Write a Note
        </button>
      </div>

      <AnimatePresence mode="wait">
        {/* File upload mode */}
        {!noteMode && (
          <motion.div key="file" initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }}>
            <div
              {...getRootProps()}
              className={clsx(
                'border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-all duration-200',
                isDragActive
                  ? 'border-accent bg-accent-glow scale-[1.01]'
                  : 'border-border hover:border-accent/40 hover:bg-accent-glow/30'
              )}
            >
              <input {...getInputProps()} />
              <motion.div animate={isDragActive ? { scale: 1.1 } : { scale: 1 }} transition={{ type: 'spring' }}>
                <Upload className={clsx('w-10 h-10 mx-auto mb-4', isDragActive ? 'text-accent' : 'text-ink-dim')} />
              </motion.div>
              <p className="font-display font-semibold text-ink mb-1">
                {isDragActive ? 'Drop to upload' : 'Drag & drop files here'}
              </p>
              <p className="font-body text-ink-dim text-sm mb-3">
                or <span className="text-accent">browse from your computer</span>
              </p>
              <div className="flex gap-2 justify-center flex-wrap">
                {['PDF', 'Images', 'TXT'].map((t) => (
                  <span key={t} className="tag-chip text-ink-dim">{t}</span>
                ))}
              </div>
            </div>

            {files.length > 0 && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 space-y-2">
                <div className="flex items-center justify-between mb-3">
                  <p className="font-body text-ink-muted text-sm">{files.length} file{files.length !== 1 ? 's' : ''} selected</p>
                  <button onClick={() => setFiles([])} className="font-body text-ink-dim text-xs hover:text-coral transition-colors">Clear all</button>
                </div>
                {files.map(({ file, status }) => (
                  <FilePill key={file.name} file={file} status={status} onRemove={removeFile} />
                ))}
                <button
                  onClick={uploadAll}
                  disabled={uploading || pendingCount === 0}
                  className="btn-primary w-full mt-4 py-3 rounded-xl font-display font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {uploading
                    ? <><Loader className="w-4 h-4 animate-spin" /> Uploading...</>
                    : <><Upload className="w-4 h-4" /> Upload {pendingCount} file{pendingCount !== 1 ? 's' : ''}</>
                  }
                </button>
              </motion.div>
            )}
          </motion.div>
        )}

        {/* Note writing mode */}
        {noteMode && (
          <motion.div key="note" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -10 }}>
            <form onSubmit={submitNote} className="space-y-4">
              <div>
                <label className="block font-body text-ink-muted text-xs mb-1.5 ml-1">Title (optional)</label>
                <input
                  type="text"
                  value={noteTitle}
                  onChange={(e) => setNoteTitle(e.target.value)}
                  placeholder="Give your note a title..."
                  className="input-focus w-full rounded-xl px-4 py-3 text-sm"
                />
              </div>
              <div>
                <label className="block font-body text-ink-muted text-xs mb-1.5 ml-1">Content</label>
                <textarea
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  placeholder="Write your thoughts here... Use natural language, AI will understand."
                  rows={12}
                  className="input-focus w-full rounded-xl px-4 py-3 text-sm resize-none leading-relaxed"
                />
              </div>
              <button
                type="submit"
                disabled={noteLoading || !noteContent.trim()}
                className="btn-primary w-full py-3 rounded-xl font-display font-semibold text-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {noteLoading
                  ? <><Loader className="w-4 h-4 animate-spin" /> Saving...</>
                  : <><Plus className="w-4 h-4" /> Save Note</>
                }
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
