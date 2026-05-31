import { useEffect, useState, useRef } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import {
  TrendingUp, TrendingDown, MessageCircle, Flame, Calendar,
  AlertTriangle, ArrowUpRight, ArrowDownRight, Clock, User, RefreshCw,
} from 'lucide-react'

const GREEN = '#00C853'

interface Trader { name: string; phone: string; member_since: string; streak: number }
interface ChartPoint { date: string; revenue: number; expenses: number }
interface Debtor { id: string; name: string; amount: number; days_overdue: number }
interface Transaction { id: string; type: 'credit' | 'debit'; description: string; amount: number; date: string }
interface Stats {
  credit_score: number; credit_band: string; next_band: string; next_band_threshold: number;
  today_profit: number; week_revenue: number; month_margin: number;
  chart_data: ChartPoint[]; debtors: Debtor[]; transactions: Transaction[];
}

function genChart(): ChartPoint[] {
  const data: ChartPoint[] = []
  const now = new Date()
  for (let i = 29; i >= 0; i--) {
    const d = new Date(now); d.setDate(d.getDate() - i)
    const base = 45000 + Math.random() * 30000
    data.push({ date: d.toLocaleDateString('en-NG', { month: 'short', day: 'numeric' }), revenue: Math.round(base), expenses: Math.round(base * (0.4 + Math.random() * 0.25)) })
  }
  return data
}

const MOCK_TRADER: Trader = { name: 'Amaka Okonkwo', phone: '+234 803 XXX XXXX', member_since: 'March 2024', streak: 23 }
const MOCK_STATS: Stats = {
  credit_score: 647, credit_band: 'Fair', next_band: 'Good', next_band_threshold: 700,
  today_profit: 12450, week_revenue: 284000, month_margin: 34.7,
  chart_data: genChart(),
  debtors: [
    { id: '1', name: 'Chukwudi Eze', amount: 45000, days_overdue: 12 },
    { id: '2', name: 'Fatima Bello', amount: 18500, days_overdue: 0 },
    { id: '3', name: 'Seun Adebayo', amount: 67000, days_overdue: 31 },
    { id: '4', name: 'Ngozi Williams', amount: 9800, days_overdue: 5 },
  ],
  transactions: [
    { id: 't1', type: 'credit', description: 'Sales — fabrics (wholesale)', amount: 85000, date: 'Today, 2:14 PM' },
    { id: 't2', type: 'debit',  description: 'Supplier payment — Eko Fabrics', amount: 42000, date: 'Today, 10:30 AM' },
    { id: 't3', type: 'credit', description: 'Sales — retail customers', amount: 23500, date: 'Yesterday, 4:45 PM' },
    { id: 't4', type: 'credit', description: 'Debt collection — Adaeze', amount: 15000, date: 'Yesterday, 1:20 PM' },
    { id: 't5', type: 'debit',  description: 'Market stall rent', amount: 8000, date: 'May 28, 9:00 AM' },
    { id: 't6', type: 'credit', description: 'Sales — fabrics', amount: 62000, date: 'May 28, 6:30 PM' },
    { id: 't7', type: 'debit',  description: 'Transport & logistics', amount: 4500, date: 'May 27, 8:15 AM' },
    { id: 't8', type: 'credit', description: 'Sales — accessories', amount: 18900, date: 'May 27, 3:00 PM' },
    { id: 't9', type: 'debit',  description: 'Packaging materials', amount: 6200, date: 'May 26, 11:45 AM' },
    { id: 't10', type: 'credit', description: 'Sales — bulk order', amount: 110000, date: 'May 26, 2:30 PM' },
  ],
}

function getBandColor(band: string) {
  if (band === 'Poor') return '#ef4444'
  if (band === 'Good' || band === 'Excellent') return GREEN
  return '#eab308' // Fair
}

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-bright" style={{ borderRadius: 12, padding: '10px 14px', fontSize: 13 }}>
      <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: 8 }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, display: 'inline-block' }} />
          <span style={{ color: 'rgba(255,255,255,0.6)', textTransform: 'capitalize' }}>{p.name}:</span>
          <span style={{ fontWeight: 600 }}>₦{p.value.toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

function AnimatedScore({ target }: { target: number }) {
  const [display, setDisplay] = useState(300)
  const frameRef = useRef<number | undefined>(undefined)
  const startRef = useRef<number | undefined>(undefined)
  useEffect(() => {
    const duration = 1400, start = 300
    const animate = (ts: number) => {
      if (!startRef.current) startRef.current = ts
      const p = Math.min((ts - startRef.current) / duration, 1)
      const eased = 1 - Math.pow(1 - p, 3)
      setDisplay(Math.round(start + (target - start) * eased))
      if (p < 1) frameRef.current = requestAnimationFrame(animate)
    }
    frameRef.current = requestAnimationFrame(animate)
    return () => { if (frameRef.current) cancelAnimationFrame(frameRef.current) }
  }, [target])
  return <>{display}</>
}

export default function Dashboard() {
  const [_sessionToken, setSessionToken] = useState<string | null>(null)
  const [trader, setTrader] = useState<Trader | null>(null)
  const [stats, setStats] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [useMock, setUseMock] = useState(false)

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get('token')
    if (!token) {
      setUseMock(true); setTrader(MOCK_TRADER); setStats(MOCK_STATS); setLoading(false); return
    }
    fetch(`/dashboard/validate?token=${token}`)
      .then(r => { if (!r.ok) throw new Error('invalid'); return r.json() })
      .then(data => { setSessionToken(data.session_token); setTrader(data.trader); return fetch(`/dashboard/stats?session_token=${data.session_token}`) })
      .then(r => { if (!r.ok) throw new Error('stats'); return r.json() })
      .then(data => { setStats(data); setLoading(false) })
      .catch(() => { setError('expired'); setLoading(false) })
  }, [])

  if (loading) return <LoadingScreen />
  if (error === 'expired') return <ExpiredScreen />

  const score = stats!.credit_score
  const band = stats!.credit_band
  const bandColor = getBandColor(band)
  const scoreProgress = ((score - 300) / (stats!.next_band_threshold - 300)) * 100

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', color: '#fff' }}>
      {/* Header */}
      <header style={{
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        padding: '1rem 1.5rem',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        position: 'sticky', top: 0, zIndex: 40,
        background: 'rgba(10,10,10,0.92)', backdropFilter: 'blur(20px)', WebkitBackdropFilter: 'blur(20px)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: GREEN, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span className="font-display" style={{ color: '#000', fontWeight: 700, fontSize: 11 }}>OP</span>
          </div>
          <span className="font-display" style={{ fontWeight: 600, fontSize: 14 }}>OPay <span style={{ color: GREEN }}>Pulse</span></span>
          {useMock && (
            <span style={{ marginLeft: 8, padding: '2px 10px', borderRadius: 999, background: 'rgba(234,179,8,0.12)', border: '1px solid rgba(234,179,8,0.25)', color: '#eab308', fontSize: 11, fontWeight: 600 }}>
              Demo Mode
            </span>
          )}
        </div>
        <a href="https://wa.me/+14155238886?text=DASHBOARD" target="_blank" rel="noopener noreferrer"
          style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'rgba(255,255,255,0.45)', textDecoration: 'none', transition: 'color 0.2s' }}
          onMouseEnter={e => (e.currentTarget.style.color = GREEN)}
          onMouseLeave={e => (e.currentTarget.style.color = 'rgba(255,255,255,0.45)')}>
          <RefreshCw size={12} /> Refresh via WhatsApp
        </a>
      </header>

      {/* Main grid */}
      <main style={{ maxWidth: 1280, margin: '0 auto', padding: '2rem 1.5rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 20, alignItems: 'start' }}>

        {/* ── LEFT COLUMN ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* Profile */}
          <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
            <div style={{ display: 'flex', gap: 16 }}>
              <div style={{ width: 56, height: 56, borderRadius: 14, background: 'rgba(0,200,83,0.12)', border: '1px solid rgba(0,200,83,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <User size={24} color={GREEN} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <h2 className="font-display" style={{ fontWeight: 700, fontSize: 18, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{trader?.name}</h2>
                <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13, marginTop: 2 }}>{trader?.phone}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'rgba(255,255,255,0.45)', marginTop: 10 }}>
                  <Calendar size={12} /> Member since {trader?.member_since}
                </div>
              </div>
            </div>
            <div style={{ marginTop: 20, display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', borderRadius: 12, background: 'rgba(0,200,83,0.08)', border: '1px solid rgba(0,200,83,0.14)' }}>
              <Flame size={20} color={GREEN} />
              <span className="font-display" style={{ fontWeight: 700, fontSize: 22, color: GREEN }}>{trader?.streak}</span>
              <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: 14 }}>day logging streak 🔥</span>
            </div>
          </div>

          {/* Credit Score */}
          <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 20 }}>Ledger Credit Score</div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 16, marginBottom: 24 }}>
              <div className="font-display" style={{ fontWeight: 800, fontSize: 72, lineHeight: 1, color: bandColor, textShadow: `0 0 30px ${bandColor}50` }}>
                <AnimatedScore target={score} />
              </div>
              <div style={{ marginBottom: 8 }}>
                <div style={{ display: 'inline-flex', padding: '4px 12px', borderRadius: 999, background: `${bandColor}18`, border: `1px solid ${bandColor}40`, color: bandColor, fontSize: 13, fontWeight: 600 }}>
                  {band}
                </div>
                <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 11, marginTop: 4 }}>out of 900</div>
              </div>
            </div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span>Progress to {stats?.next_band}</span>
              <span>{stats?.next_band_threshold} needed</span>
            </div>
            <div className="progress-bar"><div className="progress-fill" style={{ width: `${Math.min(scoreProgress, 100)}%` }} /></div>
            <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12, marginTop: 8 }}>
              {stats!.next_band_threshold - score} points to unlock <span style={{ color: GREEN }}>{stats?.next_band}</span>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 20 }}>Quick Stats</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                { label: "Today's profit", value: `₦${stats!.today_profit.toLocaleString()}`, trend: 'up' as const, sub: '+12% vs yesterday' },
                { label: "This week's revenue", value: `₦${stats!.week_revenue.toLocaleString()}`, trend: 'up' as const, sub: '+8% vs last week' },
                { label: "This month's margin", value: `${stats!.month_margin}%`, trend: 'down' as const, sub: '-2.1% vs last month' },
              ].map((s, i) => (
                <div key={i}>
                  {i > 0 && <div style={{ height: 1, background: 'rgba(255,255,255,0.06)', marginBottom: 16 }} />}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ color: 'rgba(255,255,255,0.44)', fontSize: 12 }}>{s.label}</div>
                      <div className="font-display" style={{ fontWeight: 700, fontSize: 22, marginTop: 2 }}>{s.value}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: s.trend === 'up' ? GREEN : '#f87171' }}>
                      {s.trend === 'up' ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
                      {s.sub}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ── RIGHT COLUMN ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

          {/* Chart */}
          <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 24, flexWrap: 'wrap', gap: 12 }}>
              <div>
                <h3 className="font-display" style={{ fontWeight: 600, fontSize: 15 }}>Revenue vs Expenses</h3>
                <p style={{ color: 'rgba(255,255,255,0.4)', fontSize: 12, marginTop: 2 }}>Last 30 days</p>
              </div>
              <div style={{ display: 'flex', gap: 16, fontSize: 12, color: 'rgba(255,255,255,0.5)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: GREEN, display: 'inline-block' }} /> Revenue</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: 'rgba(255,255,255,0.3)', display: 'inline-block' }} /> Expenses</div>
              </div>
            </div>
            <div style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats?.chart_data} margin={{ top: 0, right: 4, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }} axisLine={false} tickLine={false} interval={5} />
                  <YAxis tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `₦${(v / 1000).toFixed(0)}k`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="revenue" stroke={GREEN} strokeWidth={2} dot={false} activeDot={{ r: 4, fill: GREEN, strokeWidth: 0 }} />
                  <Line type="monotone" dataKey="expenses" stroke="rgba(255,255,255,0.25)" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#fff', strokeWidth: 0 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Bottom grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>

            {/* Debtors */}
            <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                <h3 className="font-display" style={{ fontWeight: 600, fontSize: 14 }}>Outstanding Debtors</h3>
                <span style={{ color: GREEN, fontSize: 12 }}>{stats?.debtors.length} total</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {stats?.debtors.map((d) => (
                  <div key={d.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                      <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.6)', flexShrink: 0 }}>
                        {d.name.charAt(0)}
                      </div>
                      <div>
                        <div style={{ fontSize: 13, fontWeight: 500, color: 'rgba(255,255,255,0.85)' }}>{d.name}</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: d.days_overdue > 0 ? '#f87171' : 'rgba(255,255,255,0.35)', marginTop: 2 }}>
                          {d.days_overdue > 0 ? <AlertTriangle size={10} /> : <Clock size={10} />}
                          {d.days_overdue > 0 ? `${d.days_overdue}d overdue` : 'Due soon'}
                        </div>
                      </div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontWeight: 600, fontSize: 13 }}>₦{d.amount.toLocaleString()}</div>
                      <span className={`badge ${d.days_overdue > 14 ? 'badge-overdue' : d.days_overdue > 0 ? 'badge-pending' : 'badge-good'}`} style={{ marginTop: 4 }}>
                        {d.days_overdue > 14 ? 'Overdue' : d.days_overdue > 0 ? 'Late' : 'Active'}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Transactions */}
            <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                <h3 className="font-display" style={{ fontWeight: 600, fontSize: 14 }}>Recent Transactions</h3>
                <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12 }}>Last 10</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 2, maxHeight: 340, overflowY: 'auto' }}>
                {stats?.transactions.map((tx) => (
                  <div key={tx.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '9px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ width: 28, height: 28, borderRadius: '50%', background: tx.type === 'credit' ? 'rgba(0,200,83,0.1)' : 'rgba(239,68,68,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      {tx.type === 'credit' ? <ArrowUpRight size={13} color={GREEN} /> : <ArrowDownRight size={13} color="#f87171" />}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.8)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{tx.description}</div>
                      <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.32)', marginTop: 2 }}>{tx.date}</div>
                    </div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: tx.type === 'credit' ? GREEN : '#f87171', flexShrink: 0 }}>
                      {tx.type === 'credit' ? '+' : '-'}₦{tx.amount.toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

function LoadingScreen() {
  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ width: 56, height: 56, borderRadius: 16, background: 'rgba(0,200,83,0.12)', border: '1px solid rgba(0,200,83,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
          <span className="font-display" style={{ color: GREEN, fontWeight: 700, fontSize: 18 }}>OP</span>
        </div>
        <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: 14 }}>Loading your dashboard…</div>
        <div style={{ display: 'flex', gap: 6, justifyContent: 'center', marginTop: 16 }}>
          <div className="pulse-dot" style={{ width: 6, height: 6, borderRadius: '50%', background: GREEN }} />
          <div className="pulse-dot-2" style={{ width: 6, height: 6, borderRadius: '50%', background: GREEN }} />
          <div className="pulse-dot-3" style={{ width: 6, height: 6, borderRadius: '50%', background: GREEN }} />
        </div>
      </div>
    </div>
  )
}

function ExpiredScreen() {
  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '1.5rem' }}>
      <div className="glass" style={{ borderRadius: 28, padding: 48, maxWidth: 420, width: '100%', textAlign: 'center' }}>
        <div style={{ width: 56, height: 56, borderRadius: 16, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px' }}>
          <AlertTriangle size={24} color="#f87171" />
        </div>
        <h1 className="font-display" style={{ fontWeight: 700, fontSize: 26, marginBottom: 12 }}>Link Expired</h1>
        <p style={{ color: 'rgba(255,255,255,0.55)', lineHeight: 1.65, marginBottom: 32 }}>
          This link has expired. Text <span style={{ color: GREEN, fontWeight: 600 }}>DASHBOARD</span> to OPay Pulse on WhatsApp to get a new one.
        </p>
        <a href="https://wa.me/+14155238886?text=DASHBOARD" target="_blank" rel="noopener noreferrer"
          className="btn-green" style={{ width: '100%', padding: '14px', borderRadius: 14, fontSize: 16 }}>
          <MessageCircle size={18} />
          Get New Link on WhatsApp
        </a>
      </div>
    </div>
  )
}
