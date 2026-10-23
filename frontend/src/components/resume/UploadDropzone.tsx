import { useState } from 'react'
import { Upload } from 'lucide-react'
import { cn } from '@/lib/cn'

export function UploadDropzone({
  file,
  onFile,
  status,
}: {
  file: File | null
  onFile: (file: File) => void
  status?: string
}) {
  const [over, setOver] = useState(false)

  const take = (list: FileList | null) => {
    const next = list?.[0]
    if (next) onFile(next)
  }

  return (
    <label
      className={cn(
        'glass rounded-3xl p-8 grid place-items-center text-center cursor-pointer border-dashed border-2 min-h-48',
        over ? 'border-primary' : 'border-border',
      )}
    >
      <input
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        className="sr-only"
        onChange={(e) => take(e.target.files)}
      />
      <div
        onDragOver={(e) => {
          e.preventDefault()
          setOver(true)
        }}
        onDragLeave={() => setOver(false)}
        onDrop={(e) => {
          e.preventDefault()
          setOver(false)
          take(e.dataTransfer.files)
        }}
        className="flex flex-col items-center gap-3"
      >
        <Upload className="text-primary" />
        <p className="font-display">Drop a PDF or DOCX</p>
        <p className="text-sm text-muted">Max 5MB. We extract text only — files are not public.</p>
        {file ? (
          <p className="text-sm text-primary">
            {file.name} · {(file.size / 1024).toFixed(0)} KB
          </p>
        ) : null}
        {status ? <p className="text-xs text-muted">{status}</p> : null}
      </div>
    </label>
  )
}
