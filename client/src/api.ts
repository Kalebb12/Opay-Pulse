/**
 * api.ts — typed client for the OPay Pulse backend
 *
 * Set VITE_API_BASE in your .env files:
 *   .env              → http://localhost:8000   (local dev)
 *   .env.production   → https://opay-pulse.onrender.com
 *
 * CORS is open on the backend (allow_origins=["*"]), so direct requests work fine.
 */

const BASE = import.meta.env.VITE_API_BASE as string

// ─── Response shapes (matching FastAPI exactly) ───────────────────────────────

export interface TraderProfile {
  phone: string
  streak: number
  credit_score: number
  member_since: string
}

export interface ValidateResponse {
  trader: TraderProfile
}

export interface DayTotal {
  income: number
  expense: number
  profit: number
}

export interface PeriodSummary {
  income: number
  expense: number
  profit: number
  margin: number
  growth: number
  period: string
}

export interface ChartPoint {
  date: string        // "01 Jun"
  income: number
  expense: number
  profit: number
}

export interface Debtor {
  name: string
  owed: number
  paid: number
  balance: number
  status: string
  due_date: string | null
  overdue: boolean
}

export interface DebtorsResult {
  debtors: Debtor[]
  total_outstanding: number
  total_debtors: number
}

export interface StatsResponse {
  today: DayTotal
  week: PeriodSummary
  month: PeriodSummary
  chart_data: ChartPoint[]
  debtors: DebtorsResult
}

export interface TxItem {
  id: number
  type: 'income' | 'expense'
  amount: number
  category: string
  description: string | null
  logged_at: string
}

export interface TxResponse {
  trader_id: number
  data: TxItem[]
  total: number
  limit: number
  offset: number
}

// ─── Fetch helper ─────────────────────────────────────────────────────────────

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error((err as { detail?: string }).detail ?? `HTTP ${res.status}`)
  }
  return res.json() as Promise<T>
}

// ─── API surface ──────────────────────────────────────────────────────────────

export const api = {
  /**
   * GET /dashboard/validate?token=xxx
   * Validates the magic-link token and returns the trader profile.
   */
  validate(token: string) {
    return get<ValidateResponse>(`/dashboard/validate?token=${encodeURIComponent(token)}`)
  },

  /**
   * GET /dashboard/stats?token=xxx
   * Returns today/week/month P&L summaries, 30-day chart data, and debtors.
   */
  stats(token: string) {
    return get<StatsResponse>(`/dashboard/stats?token=${encodeURIComponent(token)}`)
  },

  /**
   * GET /api/dashboard/trader/{token}/transactions?limit=N&offset=N
   * Returns the trader's paginated transaction history.
   */
  transactions(token: string, limit = 10, offset = 0, type?: 'income' | 'expense') {
    const p = new URLSearchParams({ limit: String(limit), offset: String(offset) })
    if (type) p.set('tx_type', type)
    return get<TxResponse>(
      `/api/dashboard/trader/${encodeURIComponent(token)}/transactions?${p}`
    )
  },
}

// ─── Credit band helpers ──────────────────────────────────────────────────────

export function creditBand(score: number): { band: string; next: string; threshold: number } {
  if (score < 500) return { band: 'Poor',      next: 'Fair',      threshold: 500 }
  if (score < 620) return { band: 'Fair',      next: 'Good',      threshold: 620 }
  if (score < 740) return { band: 'Good',      next: 'Very Good', threshold: 740 }
  if (score < 800) return { band: 'Very Good', next: 'Excellent', threshold: 800 }
  return                   { band: 'Excellent', next: 'Excellent', threshold: 850 }
}

export function bandColor(band: string): string {
  if (band === 'Poor') return '#ef4444'
  if (band === 'Fair') return '#eab308'
  return '#00C853'
}

/** Humanise an ISO logged_at timestamp from the backend */
export function fmtDate(iso: string): string {
  const d = new Date(iso)
  const now = new Date()
  const time = d.toLocaleTimeString('en-NG', { hour: '2-digit', minute: '2-digit' })
  if (d.toDateString() === now.toDateString()) return `Today, ${time}`
  const yesterday = new Date(now); yesterday.setDate(now.getDate() - 1)
  if (d.toDateString() === yesterday.toDateString()) return `Yesterday, ${time}`
  return d.toLocaleDateString('en-NG', { day: 'numeric', month: 'short' }) + `, ${time}`
}
