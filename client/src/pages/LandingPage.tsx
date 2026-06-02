import { useRef } from "react";
import { QRCodeSVG } from "qrcode.react";
import {
  MessageCircle,
  TrendingUp,
  ShieldCheck,
  ChevronRight,
  Star,
  ArrowRight,
  Smartphone,
  Hash,
  BarChart3,
  Users,
  Lock,
  Zap,
} from "lucide-react";

const WA_LINK = "https://wa.me/+14155238886?text=brief-slight";

const c = {
  green: "#00C853",
  dim: "rgba(255,255,255,0.4)",
  muted: "rgba(255,255,255,0.25)",
  subtle: "rgba(255,255,255,0.55)",
  border: "rgba(255,255,255,0.08)",
  greenBg: "rgba(0,200,83,0.10)",
  greenBorder: "rgba(0,200,83,0.20)",
};

const STEPS = [
  {
    icon: MessageCircle,
    step: "01",
    title: "Log",
    desc: "Text your daily sales and expenses via WhatsApp — no app download, no data plan needed.",
  },
  {
    icon: TrendingUp,
    step: "02",
    title: "Build",
    desc: "Your Ledger Credit Score grows automatically as you log consistently. Every transaction counts.",
  },
  {
    icon: ShieldCheck,
    step: "03",
    title: "Borrow",
    desc: "Share your verified financial profile with lenders. Get working capital without collateral.",
  },
];

const QUOTES = [
  {
    quote:
      "Before this, I couldn't prove my shop makes money. The bank just said no. Now I have a score.",
    name: "Amaka O.",
    role: "Fabric Seller, Onitsha Main Market",
  },
  {
    quote:
      "I send my sales every night like sending a message to a friend. It takes 30 seconds.",
    name: "Tunde B.",
    role: "Phone Accessories Trader, Lagos Island",
  },
  {
    quote:
      "My credit score went from 0 to 620 in 6 weeks. I just texted my numbers every day.",
    name: "Chisom N.",
    role: "Food Vendor, Aba Market",
  },
];

const LENDER_FEATURES = [
  {
    icon: BarChart3,
    title: "Verified Financial Profiles",
    desc: "30+ days of real transaction data, not self-reported income. Every data point is timestamped and source-verified.",
  },
  {
    icon: Users,
    title: "Untapped Market",
    desc: "45M informal traders in Nigeria — 87% unbanked, 100% excluded from formal credit. First movers win.",
  },
  {
    icon: Lock,
    title: "Pay Per Report",
    desc: "Pull a Ledger Credit Report for ₦1,500. No monthly commitment. No minimum volume. Pay only for what you use.",
  },
  {
    icon: Zap,
    title: "Real-Time Access",
    desc: "Instant API access to trader profiles. Integrate our credit data into your existing loan workflow.",
  },
];

export default function LandingPage() {
  const lenderRef = useRef<HTMLDivElement>(null);
  const scrollToLenders = () =>
    lenderRef.current?.scrollIntoView({ behavior: "smooth" });

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0a0a0a",
        color: "#fff",
        overflowX: "hidden",
      }}
    >
      {/* ── NAV ── */}
      <nav
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 50,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "1rem 1.5rem",
          borderBottom: "1px solid rgba(255,255,255,0.06)",
          background: "rgba(10,10,10,0.85)",
          backdropFilter: "blur(20px)",
          WebkitBackdropFilter: "blur(20px)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <div
            style={{
              width: 28,
              height: 28,
              borderRadius: 8,
              background: c.green,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <span
              className="font-display"
              style={{ color: "#000", fontWeight: 700, fontSize: 11 }}
            >
              CL
            </span>
          </div>
          <span
            className="font-display"
            style={{ fontWeight: 600, fontSize: 14 }}
          >
            Credit <span style={{ color: c.green }}>Ledger</span>
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <div className="hidden md:flex" style={{ gap: "1.5rem" }}>
            {["#how-it-works", "#qr", "#lenders"].map((href, i) => (
              <a
                key={href}
                href={href}
                onClick={
                  i === 2
                    ? (e) => {
                        e.preventDefault();
                        scrollToLenders();
                      }
                    : undefined
                }
                style={{
                  color: "rgba(255,255,255,0.55)",
                  fontSize: 14,
                  textDecoration: "none",
                  transition: "color 0.2s",
                }}
                onMouseEnter={(e) => (e.currentTarget.style.color = "#fff")}
                onMouseLeave={(e) =>
                  (e.currentTarget.style.color = "rgba(255,255,255,0.55)")
                }
              >
                {["How it works", "Get started", "For lenders"][i]}
              </a>
            ))}
          </div>
          <a
            href={WA_LINK}
            target="_blank"
            rel="noopener noreferrer"
            className="btn-green"
            style={{ padding: "0.5rem 1rem", borderRadius: 10, fontSize: 14 }}
          >
            Start Tracking
          </a>
        </div>
      </nav>

      {/* ── HERO ── */}
      <section
        style={{
          position: "relative",
          paddingTop: 112,
          paddingBottom: 96,
          textAlign: "center",
          overflow: "hidden",
        }}
      >
        {/* Orbs */}
        <div
          style={{
            position: "absolute",
            top: 80,
            left: "50%",
            transform: "translateX(-50%)",
            width: 600,
            height: 600,
            borderRadius: "50%",
            background: "rgba(0,200,83,0.05)",
            filter: "blur(120px)",
            pointerEvents: "none",
          }}
        />

        <div
          style={{
            position: "relative",
            maxWidth: 900,
            margin: "0 auto",
            padding: "0 1.5rem",
          }}
        >
          {/* Badge */}
          <div
            className="anim-0"
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 8,
              padding: "6px 14px",
              borderRadius: 999,
              background: "rgba(0,200,83,0.1)",
              border: "1px solid rgba(0,200,83,0.2)",
              color: c.green,
              fontSize: 12,
              fontWeight: 500,
              marginBottom: 24,
            }}
          >
            <span
              style={{
                width: 6,
                height: 6,
                borderRadius: "50%",
                background: c.green,
                display: "inline-block",
              }}
              className="pulse-dot"
            />
            Built for Nigeria's 45M informal traders
          </div>

          <h1
            className="font-display anim-1"
            style={{
              fontWeight: 800,
              fontSize: "clamp(2.5rem, 7vw, 4.5rem)",
              lineHeight: 1.06,
              letterSpacing: "-0.02em",
              marginBottom: 24,
            }}
          >
            Your daily sales are
            <br />
            <span className="text-glow-green" style={{ color: c.green }}>
              your credit score.
            </span>
          </h1>

          <p
            className="anim-2"
            style={{
              color: "rgba(255,255,255,0.58)",
              fontSize: "clamp(1rem, 2vw, 1.2rem)",
              maxWidth: 600,
              margin: "0 auto 40px",
              lineHeight: 1.7,
            }}
          >
            Credit Ledger turns WhatsApp sales logs into a verified financial
            identity. No collateral. No bank account. No paperwork. Just your
            numbers.
          </p>

          <div
            className="anim-3"
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 16,
              justifyContent: "center",
            }}
          >
            <a
              href={WA_LINK}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-green"
              style={{ padding: "14px 28px", borderRadius: 14, fontSize: 16 }}
            >
              <MessageCircle size={18} />
              Start Tracking Free
              <ArrowRight size={16} />
            </a>
            <button
              onClick={scrollToLenders}
              className="btn-outline"
              style={{ padding: "14px 28px", borderRadius: 14, fontSize: 16 }}
            >
              For Lenders
              <ChevronRight size={16} />
            </button>
          </div>

          {/* Stats */}
          <div
            className="anim-4"
            style={{
              display: "flex",
              justifyContent: "center",
              gap: "clamp(2rem, 6vw, 5rem)",
              marginTop: 64,
            }}
          >
            {[
              ["45M+", "Informal traders"],
              ["₦0", "Cost to traders"],
              ["30s", "Daily log time"],
            ].map(([v, l]) => (
              <div key={l} style={{ textAlign: "center" }}>
                <div
                  className="font-display"
                  style={{
                    fontWeight: 700,
                    fontSize: "clamp(1.8rem, 4vw, 2.5rem)",
                    color: c.green,
                  }}
                >
                  {v}
                </div>
                <div
                  style={{
                    color: "rgba(255,255,255,0.38)",
                    fontSize: 11,
                    marginTop: 4,
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}
                >
                  {l}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" style={{ padding: "96px 1.5rem" }}>
        <div style={{ maxWidth: 1024, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <p
              style={{
                color: c.green,
                fontSize: 12,
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
                marginBottom: 12,
              }}
            >
              Process
            </p>
            <h2
              className="font-display"
              style={{
                fontWeight: 700,
                fontSize: "clamp(2rem, 5vw, 3rem)",
                marginBottom: 16,
              }}
            >
              Three steps to credit.
            </h2>
            <p
              style={{
                color: "rgba(255,255,255,0.5)",
                fontSize: 18,
                maxWidth: 480,
                margin: "0 auto",
              }}
            >
              No paperwork. No branch visits. Just WhatsApp.
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
              gap: 24,
            }}
          >
            {STEPS.map((step) => (
              <div
                key={step.step}
                className="glass hover-lift"
                style={{
                  borderRadius: 20,
                  padding: 32,
                  position: "relative",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: 0,
                    right: 0,
                    width: 120,
                    height: 120,
                    borderRadius: "50%",
                    background: "rgba(0,200,83,0.06)",
                    filter: "blur(40px)",
                  }}
                />
                <div
                  className="font-display"
                  style={{
                    color: "rgba(0,200,83,0.25)",
                    fontWeight: 700,
                    fontSize: 52,
                    marginBottom: 16,
                    lineHeight: 1,
                  }}
                >
                  {step.step}
                </div>
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: "rgba(0,200,83,0.1)",
                    border: "1px solid rgba(0,200,83,0.2)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: 20,
                  }}
                >
                  <step.icon size={22} color={c.green} />
                </div>
                <h3
                  className="font-display"
                  style={{ fontWeight: 700, fontSize: 24, marginBottom: 12 }}
                >
                  {step.title}
                </h3>
                <p
                  style={{ color: "rgba(255,255,255,0.55)", lineHeight: 1.65 }}
                >
                  {step.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── QR CODE ── */}
      <section id="qr" style={{ padding: "96px 1.5rem", position: "relative" }}>
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(to bottom, transparent, rgba(0,200,83,0.03), transparent)",
            pointerEvents: "none",
          }}
        />
        <div
          style={{
            maxWidth: 600,
            margin: "0 auto",
            textAlign: "center",
            position: "relative",
          }}
        >
          <p
            style={{
              color: c.green,
              fontSize: 12,
              fontWeight: 600,
              textTransform: "uppercase",
              letterSpacing: "0.12em",
              marginBottom: 12,
            }}
          >
            Get Started Now
          </p>
          <h2
            className="font-display"
            style={{
              fontWeight: 700,
              fontSize: "clamp(2rem, 5vw, 3rem)",
              marginBottom: 16,
            }}
          >
            Scan to start tracking
          </h2>
          <p
            style={{
              color: "rgba(255,255,255,0.5)",
              fontSize: 18,
              marginBottom: 48,
            }}
          >
            Opens WhatsApp directly — no app download, no sign-up form.
          </p>

          {/* QR card */}
          <div
            className="glass-bright glow-green animate-float"
            style={{
              display: "inline-flex",
              flexDirection: "column",
              alignItems: "center",
              borderRadius: 28,
              padding: 40,
            }}
          >
            <div style={{ position: "relative" }}>
              <div
                style={{
                  position: "absolute",
                  inset: -12,
                  borderRadius: 20,
                  background: "rgba(0,200,83,0.1)",
                  filter: "blur(20px)",
                }}
              />
              <div
                style={{
                  position: "relative",
                  background: "#fff",
                  borderRadius: 16,
                  padding: 20,
                }}
              >
                <QRCodeSVG
                  value={WA_LINK}
                  size={200}
                  level="H"
                  fgColor="#000"
                  bgColor="#fff"
                />
              </div>
            </div>
            <div
              style={{
                marginTop: 24,
                display: "flex",
                alignItems: "center",
                gap: 8,
                color: c.green,
                fontWeight: 500,
              }}
            >
              <MessageCircle size={18} />
              <span>Opens WhatsApp chat</span>
            </div>
            <p
              style={{
                color: "rgba(255,255,255,0.35)",
                fontSize: 12,
                marginTop: 6,
              }}
            >
              wa.me/+14155238886 · message: brief-slight
            </p>
          </div>

          {/* Divider */}
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 16,
              margin: "40px 0",
            }}
          >
            <div
              style={{
                flex: 1,
                height: 1,
                background: "rgba(255,255,255,0.08)",
              }}
            />
            <span style={{ color: "rgba(255,255,255,0.3)", fontSize: 13 }}>
              No smartphone? No problem.
            </span>
            <div
              style={{
                flex: 1,
                height: 1,
                background: "rgba(255,255,255,0.08)",
              }}
            />
          </div>

          {/* Alternatives */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
              gap: 16,
              textAlign: "left",
            }}
          >
            {[
              {
                icon: Smartphone,
                label: "SMS Shortcode",
                tag: "Phase 2 · Coming soon",
                main: "Text PULSE",
                sub: "to 38282",
                note: "Works on any phone with SMS",
              },
              {
                icon: Hash,
                label: "USSD Code",
                tag: "Phase 2 · Coming soon",
                main: "Dial *347*89#",
                sub: "",
                note: "Works on every phone — even basic Nokia",
              },
            ].map((alt) => (
              <div
                key={alt.label}
                className="glass hover-lift"
                style={{ borderRadius: 20, padding: 24 }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    marginBottom: 12,
                  }}
                >
                  <div
                    style={{
                      width: 40,
                      height: 40,
                      borderRadius: 10,
                      background: "rgba(255,255,255,0.05)",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <alt.icon size={18} color="rgba(255,255,255,0.6)" />
                  </div>
                  <div>
                    <div
                      style={{
                        fontSize: 10,
                        color: "rgba(255,255,255,0.4)",
                        textTransform: "uppercase",
                        letterSpacing: "0.08em",
                      }}
                    >
                      {alt.label}
                    </div>
                    <div
                      style={{ fontSize: 11, color: "rgba(255,255,255,0.55)" }}
                    >
                      {alt.tag}
                    </div>
                  </div>
                </div>
                <div
                  className="font-display"
                  style={{
                    fontWeight: 700,
                    fontSize: 22,
                    marginBottom: alt.sub ? 4 : 0,
                  }}
                >
                  {alt.main.split(" ").map((word, i) =>
                    word === "PULSE" ||
                    word === "*347*89#" ||
                    word === "38282" ? (
                      <span key={i} style={{ color: c.green }}>
                        {word}{" "}
                      </span>
                    ) : (
                      <span key={i}>{word} </span>
                    ),
                  )}
                </div>
                {alt.sub && (
                  <div
                    className="font-display"
                    style={{ fontWeight: 700, fontSize: 22 }}
                  >
                    to <span style={{ color: c.green }}>38282</span>
                  </div>
                )}
                <p
                  style={{
                    color: "rgba(255,255,255,0.38)",
                    fontSize: 12,
                    marginTop: 12,
                  }}
                >
                  {alt.note}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── SOCIAL PROOF ── */}
      <section style={{ padding: "96px 1.5rem" }}>
        <div style={{ maxWidth: 1024, margin: "0 auto" }}>
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <p
              style={{
                color: c.green,
                fontSize: 12,
                fontWeight: 600,
                textTransform: "uppercase",
                letterSpacing: "0.12em",
                marginBottom: 12,
              }}
            >
              Traders
            </p>
            <h2
              className="font-display"
              style={{ fontWeight: 700, fontSize: "clamp(2rem, 5vw, 3rem)" }}
            >
              From the market floor.
            </h2>
          </div>
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
              gap: 24,
            }}
          >
            {QUOTES.map((q, i) => (
              <div
                key={i}
                className="glass hover-lift"
                style={{
                  borderRadius: 20,
                  padding: 28,
                  display: "flex",
                  flexDirection: "column",
                }}
              >
                <div style={{ display: "flex", gap: 4, marginBottom: 20 }}>
                  {Array.from({ length: 5 }).map((_, j) => (
                    <Star key={j} size={14} color={c.green} fill={c.green} />
                  ))}
                </div>
                <p
                  style={{
                    color: "rgba(255,255,255,0.78)",
                    lineHeight: 1.65,
                    flex: 1,
                    fontSize: 15,
                  }}
                >
                  &ldquo;{q.quote}&rdquo;
                </p>
                <div
                  style={{
                    marginTop: 24,
                    paddingTop: 20,
                    borderTop: "1px solid rgba(255,255,255,0.07)",
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: 14 }}>{q.name}</div>
                  <div
                    style={{
                      color: "rgba(255,255,255,0.4)",
                      fontSize: 12,
                      marginTop: 2,
                    }}
                  >
                    {q.role}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── LENDERS ── */}
      <section
        ref={lenderRef}
        id="lenders"
        style={{
          padding: "96px 1.5rem",
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            position: "absolute",
            inset: 0,
            background:
              "linear-gradient(to bottom, transparent, rgba(0,200,83,0.04), transparent)",
            pointerEvents: "none",
          }}
        />
        <div style={{ maxWidth: 1024, margin: "0 auto", position: "relative" }}>
          <div style={{ textAlign: "center", marginBottom: 64 }}>
            <div
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 6,
                padding: "6px 14px",
                borderRadius: 999,
                background: "rgba(0,200,83,0.1)",
                border: "1px solid rgba(0,200,83,0.2)",
                color: c.green,
                fontSize: 12,
                fontWeight: 500,
                marginBottom: 24,
              }}
            >
              <ShieldCheck size={12} />
              Lender Partners
            </div>
            <h2
              className="font-display"
              style={{
                fontWeight: 700,
                fontSize: "clamp(2rem, 5vw, 3rem)",
                marginBottom: 16,
                lineHeight: 1.1,
              }}
            >
              The credit data layer
              <br />
              you've been missing.
            </h2>
            <p
              style={{
                color: "rgba(255,255,255,0.55)",
                fontSize: 18,
                maxWidth: 580,
                margin: "0 auto",
              }}
            >
              Access verified financial profiles of informal traders — a market
              with ₦15T in annual transaction volume and near-zero credit
              penetration.
            </p>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
              gap: 20,
              marginBottom: 40,
            }}
          >
            {LENDER_FEATURES.map((f, i) => (
              <div
                key={i}
                className="glass hover-lift"
                style={{
                  borderRadius: 20,
                  padding: 28,
                  display: "flex",
                  gap: 20,
                }}
              >
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: 12,
                    background: "rgba(0,200,83,0.1)",
                    border: "1px solid rgba(0,200,83,0.2)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  <f.icon size={22} color={c.green} />
                </div>
                <div>
                  <h3
                    style={{ fontWeight: 600, fontSize: 15, marginBottom: 8 }}
                  >
                    {f.title}
                  </h3>
                  <p
                    style={{
                      color: "rgba(255,255,255,0.5)",
                      fontSize: 14,
                      lineHeight: 1.6,
                    }}
                  >
                    {f.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* Pricing callout */}
          <div
            className="glass-bright glow-green"
            style={{ borderRadius: 28, padding: 48, textAlign: "center" }}
          >
            <div
              className="font-display"
              style={{
                fontWeight: 700,
                fontSize: 64,
                color: c.green,
                lineHeight: 1,
              }}
            >
              ₦1,500
            </div>
            <div
              style={{
                color: "rgba(255,255,255,0.6)",
                fontSize: 18,
                marginTop: 8,
                marginBottom: 32,
              }}
            >
              per Ledger Credit Report
            </div>
            <div
              style={{
                display: "flex",
                justifyContent: "center",
                gap: 48,
                marginBottom: 36,
              }}
            >
              {[
                ["500", "Active traders"],
                ["3×", "Avg reports pulled"],
                ["₦2.25M", "Month 1 revenue"],
              ].map(([v, l]) => (
                <div key={l} style={{ textAlign: "center" }}>
                  <div
                    className="font-display"
                    style={{ fontWeight: 700, fontSize: 28 }}
                  >
                    {v}
                  </div>
                  <div
                    style={{
                      color: "rgba(255,255,255,0.4)",
                      fontSize: 12,
                      marginTop: 4,
                    }}
                  >
                    {l}
                  </div>
                </div>
              ))}
            </div>
            <a
              href="mailto:lenders@opaypulse.ng"
              className="btn-green"
              style={{ padding: "14px 32px", borderRadius: 14, fontSize: 16 }}
            >
              Become a Partner Lender
              <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer
        style={{
          borderTop: "1px solid rgba(255,255,255,0.07)",
          padding: "48px 1.5rem",
        }}
      >
        <div
          style={{
            maxWidth: 1024,
            margin: "0 auto",
            display: "flex",
            flexWrap: "wrap",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 24,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: 8,
                background: c.green,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              <span
                className="font-display"
                style={{ color: "#000", fontWeight: 700, fontSize: 11 }}
              >
                CL
              </span>
            </div>
            <span
              className="font-display"
              style={{ fontWeight: 600, fontSize: 14 }}
            >
              Credit <span style={{ color: c.green }}>Ledger</span>
            </span>
          </div>
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 24,
              fontSize: 14,
              color: "rgba(255,255,255,0.4)",
            }}
          >
            <a
              href="mailto:hello@opaypulse.ng"
              style={{ color: "inherit", textDecoration: "none" }}
            >
              hello@opaypulse.ng
            </a>
            <a
              href={WA_LINK}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: "inherit", textDecoration: "none" }}
            >
              WhatsApp
            </a>
            <span>Lagos, Nigeria</span>
          </div>
          <p style={{ color: "rgba(255,255,255,0.22)", fontSize: 12 }}>
            © 2024 Credit Ledger. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
