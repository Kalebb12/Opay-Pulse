import { useEffect, useState, useRef } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { TrendingUp, TrendingDown, MessageCircle, Flame, Calendar, AlertTriangle, ArrowUpRight, ArrowDownRight, Clock, User, RefreshCw } from 'lucide-react'
import { api, creditBand, bandColor, fmtDate, type TraderProfile, type StatsResponse, type TxItem } from '../api'

const GREEN = '#00C853'

function CustomTooltip({ active, payload, label }: any) {
  if (!active || !payload?.length) return null
  return (
    <div className="glass-bright" style={{ borderRadius: 12, padding: '10px 14px', fontSize: 13 }}>
      <div style={{ color: 'rgba(255,255,255,0.5)', marginBottom: 8 }}>{label}</div>
      {payload.map((p: any) => (
        <div key={p.name} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ width: 8, height: 8, borderRadius: '50%', background: p.color, display: 'inline-block' }} />
          <span style={{ color: 'rgba(255,255,255,0.6)', textTransform: 'capitalize' }}>{p.name}:</span>
          <span style={{ fontWeight: 600 }}>₦{Number(p.value).toLocaleString()}</span>
        </div>
      ))}
    </div>
  )
}

function AnimatedScore({ target }: { target: number }) {
  const [display, setDisplay] = useState(300)
  const frame = useRef<number | undefined>(undefined)
  const start = useRef<number | undefined>(undefined)
  useEffect(() => {
    const animate = (ts: number) => {
      if (!start.current) start.current = ts
      const p = Math.min((ts - start.current) / 1400, 1)
      setDisplay(Math.round(300 + (target - 300) * (1 - Math.pow(1 - p, 3))))
      if (p < 1) frame.current = requestAnimationFrame(animate)
    }
    frame.current = requestAnimationFrame(animate)
    return () => { if (frame.current) cancelAnimationFrame(frame.current) }
  }, [target])
  return <>{display}</>
}

export default function Dashboard() {
  const [trader, setTrader] = useState<TraderProfile | null>(null)
  const [stats, setStats] = useState<StatsResponse | null>(null)
  const [txs, setTxs] = useState<TxItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<'expired' | 'notoken' | null>(null)

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get('token')
    if (!token) { setError('notoken'); setLoading(false); return }
    Promise.all([api.validate(token), api.stats(token), api.transactions(token, 10)])
      .then(([v, s, tx]) => {
        setTrader(v.trader)
        setStats(s)
        setTxs(tx.data)
        setLoading(false)
      })
      .catch(() => { setError('expired'); setLoading(false) })
  }, [])

  if (loading) return <LoadingScreen />
  if (error) return <ExpiredScreen />

  const score = trader!.credit_score
  const { band, next, threshold } = creditBand(score)
  const bc = bandColor(band)
  const scoreProgress = ((score - 300) / (threshold - 300)) * 100

  const S = (v: number) => `₦${v.toLocaleString()}`

  return (
    <div style={{ minHeight: '100vh', background: '#0a0a0a', color: '#fff' }}>
      {/* Header */}
      <header style={{ borderBottom: '1px solid rgba(255,255,255,0.06)', padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 40, background: 'rgba(10,10,10,0.92)', backdropFilter: 'blur(20px)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 28, height: 28, borderRadius: 8, background: GREEN, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span className="font-display" style={{ color: '#000', fontWeight: 700, fontSize: 11 }}>OP</span>
          </div>
          <span className="font-display" style={{ fontWeight: 600, fontSize: 14 }}>OPay <span style={{ color: GREEN }}>Pulse</span></span>
        </div>
        <a href={`https://wa.me/+14155238886?text=DASHBOARD`} target="_blank" rel="noopener noreferrer"
          style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'rgba(255,255,255,0.45)', textDecoration: 'none' }}>
          <RefreshCw size={12} /> Refresh via WhatsApp
        </a>
      </header>

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
                <h2 className="font-display" style={{ fontWeight: 700, fontSize: 18, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{trader!.phone}</h2>
                <div style={{ color: 'rgba(255,255,255,0.4)', fontSize: 13, marginTop: 2 }}>Verified trader</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: 'rgba(255,255,255,0.45)', marginTop: 10 }}>
                  <Calendar size={12} /> Member since {trader!.member_since}
                </div>
              </div>
            </div>
            <div style={{ marginTop: 20, display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px', borderRadius: 12, background: 'rgba(0,200,83,0.08)', border: '1px solid rgba(0,200,83,0.14)' }}>
              <Flame size={20} color={GREEN} />
              <span className="font-display" style={{ fontWeight: 700, fontSize: 22, color: GREEN }}>{trader!.streak}</span>
              <span style={{ color: 'rgba(255,255,255,0.6)', fontSize: 14 }}>day logging streak 🔥</span>
            </div>
          </div>

          {/* Credit Score */}
          <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 20 }}>Ledger Credit Score</div>
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 16, marginBottom: 24 }}>
              <div className="font-display" style={{ fontWeight: 800, fontSize: 72, lineHeight: 1, color: bc, textShadow: `0 0 30px ${bc}50` }}>
                <AnimatedScore target={score} />
              </div>
              <div style={{ marginBottom: 8 }}>
                <div style={{ display: 'inline-flex', padding: '4px 12px', borderRadius: 999, background: `${bc}18`, border: `1px solid ${bc}40`, color: bc, fontSize: 13, fontWeight: 600 }}>{band}</div>
                <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 11, marginTop: 4 }}>out of 850</div>
              </div>
            </div>
            <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span>Progress to {next}</span><span>{threshold} needed</span>
            </div>
            <div className="progress-bar"><div className="progress-fill" style={{ width: `${Math.min(scoreProgress, 100)}%` }} /></div>
            <div style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12, marginTop: 8 }}>
              {threshold - score} points to unlock <span style={{ color: GREEN }}>{next}</span>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
            <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 20 }}>Quick Stats</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[
                { label: "Today's profit",      value: S(stats!.today.profit),   trend: stats!.today.profit >= 0,   sub: `Income ${S(stats!.today.income)}` },
                { label: "This week's revenue", value: S(stats!.week.income),    trend: stats!.week.growth >= 0,    sub: `${stats!.week.growth >= 0 ? '+' : ''}${stats!.week.growth}% vs last week` },
                { label: "Month margin",        value: `${stats!.month.margin}%`, trend: stats!.month.margin >= 20, sub: `Profit ${S(stats!.month.profit)}` },
              ].map((s, i) => (
                <div key={i}>
                  {i > 0 && <div style={{ height: 1, background: 'rgba(255,255,255,0.06)', marginBottom: 16 }} />}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ color: 'rgba(255,255,255,0.44)', fontSize: 12 }}>{s.label}</div>
                      <div className="font-display" style={{ fontWeight: 700, fontSize: 22, marginTop: 2 }}>{s.value}</div>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 12, color: s.trend ? GREEN : '#f87171', textAlign: 'right' }}>
                      {s.trend ? <TrendingUp size={13} /> : <TrendingDown size={13} />}
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
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: GREEN, display: 'inline-block' }} /> Income</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}><span style={{ width: 8, height: 8, borderRadius: '50%', background: 'rgba(255,255,255,0.3)', display: 'inline-block' }} /> Expense</div>
              </div>
            </div>
            <div style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={stats!.chart_data} margin={{ top: 0, right: 4, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                  <XAxis dataKey="date" tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }} axisLine={false} tickLine={false} interval={5} />
                  <YAxis tick={{ fill: 'rgba(255,255,255,0.3)', fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={v => `₦${(v / 1000).toFixed(0)}k`} />
                  <Tooltip content={<CustomTooltip />} />
                  <Line type="monotone" dataKey="income" stroke={GREEN} strokeWidth={2} dot={false} activeDot={{ r: 4, fill: GREEN, strokeWidth: 0 }} />
                  <Line type="monotone" dataKey="expense" stroke="rgba(255,255,255,0.25)" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: '#fff', strokeWidth: 0 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Debtors + Transactions */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>

            {/* Debtors */}
            <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                <h3 className="font-display" style={{ fontWeight: 600, fontSize: 14 }}>Outstanding Debtors</h3>
                <span style={{ color: GREEN, fontSize: 12 }}>{stats!.debtors.total_debtors} total</span>
              </div>
              {stats!.debtors.debtors.length === 0 ? (
                <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>No outstanding debtors 🎉</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {stats!.debtors.debtors.map((d, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                        <div style={{ width: 32, height: 32, borderRadius: '50%', background: 'rgba(255,255,255,0.06)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12, fontWeight: 600, color: 'rgba(255,255,255,0.6)', flexShrink: 0 }}>
                          {d.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 500 }}>{d.name}</div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 4, fontSize: 11, color: d.overdue ? '#f87171' : 'rgba(255,255,255,0.35)', marginTop: 2 }}>
                            {d.overdue ? <AlertTriangle size={10} /> : <Clock size={10} />}
                            {d.overdue ? `Overdue${d.due_date ? ` · ${d.due_date}` : ''}` : d.due_date ? `Due ${d.due_date}` : 'No due date'}
                          </div>
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>₦{d.balance.toLocaleString()}</div>
                        <span className={`badge ${d.overdue ? 'badge-overdue' : d.status === 'partially_paid' ? 'badge-pending' : 'badge-good'}`} style={{ marginTop: 4 }}>
                          {d.overdue ? 'Overdue' : d.status === 'partially_paid' ? 'Partial' : 'Active'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
              {stats!.debtors.total_outstanding > 0 && (
                <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                  <span style={{ color: 'rgba(255,255,255,0.4)' }}>Total outstanding</span>
                  <span style={{ fontWeight: 700, color: '#f87171' }}>₦{stats!.debtors.total_outstanding.toLocaleString()}</span>
                </div>
              )}
            </div>

            {/* Transactions */}
            <div className="glass hover-lift" style={{ borderRadius: 20, padding: 24 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                <h3 className="font-display" style={{ fontWeight: 600, fontSize: 14 }}>Recent Transactions</h3>
                <span style={{ color: 'rgba(255,255,255,0.3)', fontSize: 12 }}>Last 10</span>
              </div>
              {txs.length === 0 ? (
                <p style={{ color: 'rgba(255,255,255,0.3)', fontSize: 13, textAlign: 'center', padding: '20px 0' }}>No transactions yet. Start logging!</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 2, maxHeight: 340, overflowY: 'auto' }}>
                  {txs.map((tx) => (
                    <div key={tx.id} style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '9px 0', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <div style={{ width: 28, height: 28, borderRadius: '50%', background: tx.type === 'income' ? 'rgba(0,200,83,0.1)' : 'rgba(239,68,68,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        {tx.type === 'income' ? <ArrowUpRight size={13} color={GREEN} /> : <ArrowDownRight size={13} color="#f87171" />}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontSize: 12, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{tx.description || tx.category}</div>
                        <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.32)', marginTop: 2 }}>{fmtDate(tx.logged_at)}</div>
                      </div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: tx.type === 'income' ? GREEN : '#f87171', flexShrink: 0 }}>
                        {tx.type === 'income' ? '+' : '-'}₦{tx.amount.toLocaleString()}
                      </div>
                    </div>
                  ))}
                </div>
              )}
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
          {[0,1,2].map(i => <div key={i} className={`pulse-dot${i > 0 ? `-${i+1}` : ''}`} style={{ width: 6, height: 6, borderRadius: '50%', background: GREEN }} />)}
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
