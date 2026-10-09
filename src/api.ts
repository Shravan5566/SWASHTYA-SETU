import { useCallback, useEffect, useState } from 'react'

const BASE: string = import.meta.env.VITE_API_BASE ?? ''

export async function api<T = any>(path: string, init?: RequestInit): Promise<T> {
  try {
    const r = await fetch(BASE + path, {
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
    if (!r.ok) {
      let msg = r.statusText
      try {
        const j = await r.json()
        msg = j.error || j.message || msg
      } catch {}
      throw new Error(msg || `Request failed with status ${r.status}`)
    }
    return r.status === 204 ? (undefined as T) : r.json()
  } catch (err: any) {
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      throw new Error('Backend server is offline. Please launch the backend server on http://127.0.0.1:5000.')
    }
    throw err
  }
}

export const post = <T = any>(path: string, body?: unknown) =>
  api<T>(path, { method: 'POST', body: JSON.stringify(body ?? {}) })

export function useFetch<T = any>(path: string | null, pollMs = 0) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(!!path)

  const load = useCallback(() => {
    if (!path) return
    api<T>(path)
      .then((d) => {
        setData(d)
        setError(null)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [path])

  useEffect(() => {
    load()
    if (!pollMs) return
    const i = setInterval(load, pollMs)
    return () => clearInterval(i)
  }, [load, pollMs])

  return { data, error, loading, reload: load }
}

/** Hook to monitor live connection to the Flask backend */
export function useBackendStatus() {
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => {
    let active = true
    const check = () => {
      api<{ status: string }>('/api/health')
        .then((res) => {
          if (active) setOnline(res.status === 'online')
        })
        .catch(() => {
          if (active) setOnline(false)
        })
    }
    check()
    const interval = setInterval(check, 10000)
    return () => {
      active = false
      clearInterval(interval)
    }
  }, [])

  return online
}
