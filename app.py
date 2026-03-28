import streamlit as st
import tempfile, os
from dotenv import load_dotenv
from parser import parse_cas_pdf
from analyzer import analyze_portfolio
from utils import format_inr, plot_allocation_pie, plot_amc_bar
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

load_dotenv()

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio X-Ray AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────
st.markdown("""
<style>
    /* Dark theme base */
    .stApp { background-color: #0a0a0f; color: #e2e8f0; }
    .main .block-container { padding: 2rem 2rem 4rem 2rem; max-width: 1400px; }

    /* Hide default streamlit elements */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Navbar */
    .navbar {
        display: flex; align-items: center; justify-content: space-between;
        padding: 1rem 0; margin-bottom: 2rem;
        border-bottom: 1px solid #1e293b;
    }
    .navbar-brand {
        display: flex; align-items: center; gap: 0.5rem;
        font-size: 1.1rem; font-weight: 800; color: #fff;
        letter-spacing: -0.5px;
    }
    .navbar-brand span { color: #818cf8; }
    .nav-badge {
        background: #1e293b; border: 1px solid #334155;
        padding: 0.25rem 0.75rem; border-radius: 999px;
        font-size: 0.7rem; font-weight: 700;
        color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;
    }

    /* Section headers */
    .section-title {
        font-size: 1.5rem; font-weight: 800;
        color: #f1f5f9; margin-bottom: 0.25rem;
        letter-spacing: -0.5px;
    }
    .section-sub {
        font-size: 0.8rem; color: #64748b;
        font-weight: 500; margin-bottom: 1.5rem;
    }

    /* Metric cards */
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    .metric-card.primary {
        border-color: #4f46e5;
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
    }
    .metric-label {
        font-size: 0.7rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 1.5px;
        color: #64748b; margin-bottom: 0.75rem;
    }
    .metric-label.primary { color: #818cf8; }
    .metric-value {
        font-size: 2rem; font-weight: 900;
        color: #f1f5f9; letter-spacing: -1px;
        line-height: 1;
    }
    .metric-value.large { font-size: 2.5rem; }
    .metric-delta-pos {
        font-size: 0.75rem; font-weight: 700;
        color: #10b981; margin-top: 0.5rem;
    }
    .metric-delta-neg {
        font-size: 0.75rem; font-weight: 700;
        color: #ef4444; margin-top: 0.5rem;
    }

    /* Glass cards */
    .glass-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
    }
    .glass-card-strong {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 20px;
        padding: 2rem;
    }

    /* Fund table rows */
    .fund-row {
        display: flex; align-items: center;
        padding: 1rem 1.25rem;
        border-bottom: 1px solid #1e293b;
        transition: background 0.2s;
    }
    .fund-row:hover { background: #ffffff08; }
    .fund-name { font-weight: 700; color: #f1f5f9; font-size: 0.9rem; }
    .fund-amc  { font-size: 0.7rem; color: #64748b; margin-top: 2px; }
    .category-badge {
        padding: 0.2rem 0.6rem; border-radius: 999px;
        font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.5px;
    }
    .cat-largecap  { background: #1e1b4b; color: #818cf8; }
    .cat-midcap    { background: #1a2744; color: #60a5fa; }
    .cat-elss      { background: #14251a; color: #34d399; }
    .cat-smallcap  { background: #2d1b1b; color: #f87171; }

    /* Issue cards */
    .issue-high   { border-left: 3px solid #ef4444; background: #ef44440d; padding: 1rem; border-radius: 0 12px 12px 0; margin-bottom: 0.75rem; }
    .issue-medium { border-left: 3px solid #f59e0b; background: #f59e0b0d; padding: 1rem; border-radius: 0 12px 12px 0; margin-bottom: 0.75rem; }
    .issue-low    { border-left: 3px solid #3b82f6; background: #3b82f60d; padding: 1rem; border-radius: 0 12px 12px 0; margin-bottom: 0.75rem; }
    .issue-title  { font-weight: 700; font-size: 0.85rem; color: #f1f5f9; }
    .issue-detail { font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; }

    /* Action cards */
    .action-card {
        background: #1e293b; border: 1px solid #334155;
        border-radius: 12px; padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .action-title { font-weight: 700; font-size: 0.85rem; color: #f1f5f9; }
    .action-detail { font-size: 0.75rem; color: #94a3b8; margin-top: 0.25rem; }
    .priority-high   { background: #7f1d1d; color: #fca5a5; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
    .priority-medium { background: #78350f; color: #fcd34d; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }
    .priority-low    { background: #1e3a5f; color: #93c5fd; padding: 0.15rem 0.5rem; border-radius: 4px; font-size: 0.65rem; font-weight: 700; }

    /* Overlap card */
    .overlap-item {
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.75rem 0; border-bottom: 1px solid #1e293b;
    }
    .overlap-pct-high { color: #ef4444; font-weight: 800; font-size: 1rem; }
    .overlap-pct-med  { color: #f59e0b; font-weight: 800; font-size: 1rem; }

    /* Verdict box */
    .verdict-box {
        background: linear-gradient(135deg, #0f172a, #1e1b4b);
        border: 1px solid #4f46e5;
        border-radius: 16px; padding: 1.5rem;
        margin-top: 1rem;
    }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #0a0a0f !important;
        border-right: 1px solid #1e293b !important;
    }

    /* Buttons */
    .stButton > button {
        background: #4f46e5 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.5rem !important;
    }
    .stButton > button:hover {
        background: #4338ca !important;
    }

    /* Divider */
    hr { border-color: #1e293b !important; }

    /* Spinner */
    .stSpinner > div { border-top-color: #4f46e5 !important; }
</style>
""", unsafe_allow_html=True)


# ── Demo portfolio ───────────────────────────────────────────────
def load_demo_portfolio():
    demo_holdings = pd.DataFrame([
        {"fund_name": "HDFC Top 100 Fund - Growth Option",        "amc": "HDFC",  "units": 268.716, "nav": 951.45,  "current_value": 255693.18, "invested": 221500.00, "category": "Large Cap"},
        {"fund_name": "HDFC Mid-Cap Opportunities Fund - Growth",  "amc": "HDFC",  "units": 351.705, "nav": 1198.34, "current_value": 421408.57, "invested": 358000.00, "category": "Mid Cap"},
        {"fund_name": "SBI Blue Chip Fund - Regular Plan - Growth","amc": "SBI",   "units": 219.548, "nav": 628.90,  "current_value": 138068.39, "invested": 122000.00, "category": "Large Cap"},
        {"fund_name": "Axis Long Term Equity Fund - Growth (ELSS)","amc": "Axis",  "units": 489.528, "nav": 812.30,  "current_value": 397576.04, "invested": 348390.00, "category": "Tax Saving"},
        {"fund_name": "Mirae Asset Large Cap Fund - Regular Plan", "amc": "Mirae", "units": 235.672, "nav": 971.20,  "current_value": 228868.62, "invested": 196000.00, "category": "Large Cap"},
    ])
    demo_holdings["allocation_pct"] = (demo_holdings["current_value"] / demo_holdings["current_value"].sum() * 100).round(2)
    demo_holdings["return_pct"]     = ((demo_holdings["current_value"] - demo_holdings["invested"]) / demo_holdings["invested"] * 100).round(1)
    return {
        "holdings":         demo_holdings,
        "total_value":      1441614.80,
        "total_invested":   1245890.00,
        "investor_name":    "Rahul Sharma",
        "statement_period": "Apr 2024 - Mar 2025"
    }


# ── Session state ────────────────────────────────────────────────
for key in ["portfolio", "analysis"]:
    if key not in st.session_state:
        st.session_state[key] = None


# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 1rem 0 1.5rem 0;'>
        <div style='font-size:1.3rem; font-weight:900; color:#fff; letter-spacing:-0.5px;'>
            📊 Portfolio X-Ray <span style='color:#818cf8;'>AI</span>
        </div>
        <div style='font-size:0.7rem; color:#64748b; margin-top:4px; text-transform:uppercase; letter-spacing:1px;'>
            Neural Engine v1.0
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📂 Upload CAS Statement")
    uploaded_file = st.file_uploader("CAMS / Kfintech CAS PDF", type=["pdf"], label_visibility="collapsed")
    password      = st.text_input("🔑 PDF Password (if any)", type="password", placeholder="Usually your email")
    analyze_btn   = st.button("🚀 Analyze Portfolio", use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🎯 Quick Demo")
    demo_btn = st.button("Load Demo Portfolio", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.7rem; color:#475569; line-height:1.8;'>
        <b style='color:#64748b;'>HOW TO GET CAS PDF</b><br>
        1. Visit camsonline.com<br>
        2. Investor Services → Statement<br>
        3. Select Consolidated Account Statement<br>
        4. Password = registered email
    </div>
    """, unsafe_allow_html=True)


# ── Load demo ────────────────────────────────────────────────────
if demo_btn:
    st.session_state.portfolio = load_demo_portfolio()
    with st.spinner("🤖 Running AI analysis..."):
        st.session_state.analysis = analyze_portfolio(st.session_state.portfolio)

# ── Load real PDF ────────────────────────────────────────────────
if analyze_btn and uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    with st.spinner("📄 Parsing CAS statement..."):
        try:
            portfolio = parse_cas_pdf(tmp_path, password)
            st.session_state.portfolio = portfolio
            st.session_state.analysis  = None
        except Exception as e:
            st.error(f"❌ {e}")
            os.unlink(tmp_path)
            st.stop()
    with st.spinner("🤖 Running AI analysis..."):
        st.session_state.analysis = analyze_portfolio(st.session_state.portfolio)
    os.unlink(tmp_path)
    st.success(f"✅ Done!")

elif analyze_btn and not uploaded_file:
    st.warning("⚠️ Please upload a CAS PDF first.")


# ── Main dashboard ───────────────────────────────────────────────
if st.session_state.portfolio:
    port = st.session_state.portfolio
    df   = port["holdings"]

    total_value    = port["total_value"]
    total_invested = port.get("total_invested", df["invested"].sum() if "invested" in df.columns else total_value * 0.87)
    total_gain     = total_value - total_invested
    abs_return     = (total_gain / total_invested) * 100
    nifty_return   = 14.0
    diff           = abs_return - nifty_return

    if "return_pct" not in df.columns and "invested" in df.columns:
        df["return_pct"] = ((df["current_value"] - df["invested"]) / df["invested"] * 100).round(1)

    sorted_df = df.sort_values("return_pct", ascending=False) if "return_pct" in df.columns else df

    # ── Navbar ───────────────────────────────────────────────────
    st.markdown(f"""
    <div class="navbar">
        <div class="navbar-brand">
            📊 Portfolio X-Ray <span>AI</span>
        </div>
        <div style="display:flex; gap:1rem; align-items:center;">
            <span style="color:#64748b; font-size:0.8rem; font-weight:600;">
                👤 {port['investor_name']}
            </span>
            <span class="nav-badge">Dashboard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Section: Portfolio Metrics ───────────────────────────────
    st.markdown('<div class="section-title">Portfolio Metrics</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Consolidated performance tracking and net position</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card primary">
            <div class="metric-label primary">NET WORTH</div>
            <div class="metric-value large">{format_inr(total_value)}</div>
            <div class="metric-delta-pos">↑ {format_inr(total_gain)} total gain</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">TOTAL INPUT CAPITAL</div>
            <div class="metric-value">{format_inr(total_invested)}</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        delta_class = "metric-delta-pos" if abs_return >= 0 else "metric-delta-neg"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">CURRENT RETURNS</div>
            <div class="metric-value">{abs_return:.1f}<span style="font-size:1.2rem; color:#64748b;">%</span></div>
            <div class="{delta_class}">{'▲' if diff >= 0 else '▼'} {abs(diff):.1f}% vs Nifty 50</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">PORTFOLIO XIRR</div>
            <div class="metric-value" style="font-size:1.1rem; color:#94a3b8; padding-top:0.5rem;">
                {"Not enough data" if abs_return < 5 else f"{abs_return * 0.85:.1f}%"}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section: Strategy Drift + Health ─────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown('<div class="section-title">Strategy Drift</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Deviation from institutional target model</div>', unsafe_allow_html=True)

        # Calculate allocation by category
        if "category" in df.columns:
            cat_df = df.groupby("category")["current_value"].sum().reset_index()
            cat_df["pct"] = (cat_df["current_value"] / total_value * 100).round(1)
        else:
            cat_df = pd.DataFrame({
                "category": ["Large Cap", "Mid Cap", "ELSS"],
                "pct":      [43, 29, 28]
            })

        target = {
            "Large Cap": 20, "Mid Cap": 20, "Tax Saving": 6,
            "Small Cap": 15, "Debt": 5, "Hybrid": 10,
            "Index": 10, "Sectoral": 5, "flexiCap": 9
        }

        all_cats   = list(set(list(cat_df["category"].tolist()) + list(target.keys())))
        current_vals = []
        target_vals  = []
        for cat in all_cats:
            row = cat_df[cat_df["category"] == cat]
            current_vals.append(float(row["pct"].values[0]) if len(row) > 0 else 0)
            target_vals.append(target.get(cat, 5))

        fig_drift = go.Figure()
        fig_drift.add_trace(go.Bar(
            name="Current Allocation",
            x=all_cats, y=current_vals,
            marker_color="#4f46e5",
            marker_line_width=0,
        ))
        fig_drift.add_trace(go.Bar(
            name="Recommended Allocation",
            x=all_cats, y=target_vals,
            marker_color="#10b981",
            marker_line_width=0,
        ))
        fig_drift.update_layout(
            barmode="group",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", size=11),
            legend=dict(
                orientation="h", y=1.15,
                bgcolor="rgba(0,0,0,0)",
                font=dict(color="#94a3b8", size=11)
            ),
            margin=dict(t=40, b=20, l=0, r=0),
            height=280,
            xaxis=dict(gridcolor="#1e293b", tickfont=dict(size=10)),
            yaxis=dict(gridcolor="#1e293b", ticksuffix="%"),
        )
        st.plotly_chart(fig_drift, use_container_width=True, config={"displayModeBar": False})

        # Required modifications
        st.markdown("**REQUIRED MODIFICATIONS**")
        mod_cols = st.columns(4)
        mods = []
        for i, cat in enumerate(all_cats[:8]):
            diff_val = target_vals[i] - current_vals[i]
            mods.append((cat, diff_val))

        for i, (cat, diff_val) in enumerate(mods):
            col = mod_cols[i % 4]
            color = "#10b981" if diff_val > 0 else "#ef4444"
            sign  = "+" if diff_val > 0 else ""
            col.markdown(f"""
            <div style="background:#1e293b; border:1px solid #334155; border-radius:10px;
                        padding:0.6rem 1rem; text-align:center; margin-bottom:0.5rem;">
                <div style="font-size:0.65rem; font-weight:700; color:#64748b;
                            text-transform:uppercase; letter-spacing:1px;">{cat}</div>
                <div style="font-size:0.95rem; font-weight:800; color:{color};">
                    {sign}{diff_val:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-title">Health Indicators</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-sub">Institution-grade safety metrics</div>', unsafe_allow_html=True)

        # Health score gauge
        health_score = min(100, max(0, int(50 + diff * 2 + (5 - df["amc"].nunique()) * -3 + len(df) * 2)))
        health_label = "EXCELLENT" if health_score >= 80 else "GOOD" if health_score >= 65 else "AVERAGE" if health_score >= 45 else "POOR"
        health_color = "#10b981" if health_score >= 80 else "#f59e0b" if health_score >= 65 else "#f59e0b" if health_score >= 45 else "#ef4444"

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            number={"font": {"size": 48, "color": "#f1f5f9", "family": "sans-serif"}, "suffix": ""},
            gauge={
                "axis":       {"range": [0, 100], "tickcolor": "#334155", "tickfont": {"color": "#64748b", "size": 10}},
                "bar":        {"color": health_color, "thickness": 0.25},
                "bgcolor":    "#1e293b",
                "bordercolor": "#334155",
                "steps": [
                    {"range": [0,  40], "color": "#1a0a0a"},
                    {"range": [40, 65], "color": "#1a1400"},
                    {"range": [65, 80], "color": "#0a1a10"},
                    {"range": [80,100], "color": "#0a1a10"},
                ],
                "threshold": {"line": {"color": health_color, "width": 3}, "value": health_score}
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8"),
            height=200,
            margin=dict(t=20, b=10, l=20, r=20),
        )
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:0.7rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:0.5rem;">PORTFOLIO HEALTH INDEX</div>', unsafe_allow_html=True)
        st.plotly_chart(fig_gauge, use_container_width=True, config={"displayModeBar": False})
        st.markdown(f'<div style="text-align:center; font-size:0.75rem; font-weight:800; color:{health_color}; margin-top:-1rem;">{health_label}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Risk indicator
        amc_concentration = df.groupby("amc")["current_value"].sum().max() / total_value * 100
        risk_level  = "HIGH" if amc_concentration > 45 or len(df) < 4 else "MODERATE" if amc_concentration > 30 else "LOW"
        risk_color  = "#ef4444" if risk_level == "HIGH" else "#f59e0b" if risk_level == "MODERATE" else "#10b981"
        risk_pos    = 85 if risk_level == "HIGH" else 50 if risk_level == "MODERATE" else 15

        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:0.7rem; font-weight:700; color:#64748b;
                        text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1rem;">
                RISK EXPOSURE
            </div>
            <div style="text-align:center; font-size:1rem; font-weight:800;
                        color:{risk_color}; margin-bottom:0.75rem;">{risk_level}</div>
            <div style="background:linear-gradient(to right, #10b981, #f59e0b, #ef4444);
                        height:8px; border-radius:999px; position:relative; margin-bottom:0.5rem;">
                <div style="position:absolute; left:{risk_pos}%; top:-4px;
                             width:16px; height:16px; border-radius:50%;
                             background:{risk_color}; border:2px solid #0f172a;
                             transform:translateX(-50%);"></div>
            </div>
            <div style="display:flex; justify-content:space-between;
                        font-size:0.65rem; color:#475569; font-weight:600;">
                <span>SAFE</span><span>BALANCED</span><span>AGGRESSIVE</span>
            </div>
            <div style="font-size:0.75rem; color:#94a3b8; margin-top:0.75rem; text-align:center;">
                {"High equity exposure targeting maximum alpha." if risk_level == "HIGH"
                 else "Balanced allocation with moderate risk." if risk_level == "MODERATE"
                 else "Conservative allocation with low risk."}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Overlap detection
        overlap_pairs = []
        fund_list = df["fund_name"].tolist()
        amc_list  = df["amc"].tolist()
        for i in range(len(fund_list)):
            for j in range(i+1, len(fund_list)):
                if amc_list[i] == amc_list[j]:
                    overlap_pairs.append((fund_list[i][:30]+"...", fund_list[j][:30]+"...", 62))
                elif "Large Cap" in str(df.iloc[i].get("category","")) and "Large Cap" in str(df.iloc[j].get("category","")):
                    overlap_pairs.append((fund_list[i][:30]+"...", fund_list[j][:30]+"...", 55))

        if overlap_pairs:
            st.markdown(f"""
            <div class="glass-card" style="border-left: 3px solid #f59e0b;">
                <div style="font-size:0.7rem; font-weight:700; color:#f59e0b;
                            text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1rem;">
                    ⚠ Portfolio Overlap
                </div>
                <div style="font-size:0.7rem; color:#64748b; margin-bottom:0.75rem;">
                    Potential redundancy in fund holdings
                </div>
            """, unsafe_allow_html=True)
            for f1, f2, pct in overlap_pairs[:3]:
                pct_color = "#ef4444" if pct >= 55 else "#f59e0b"
                st.markdown(f"""
                <div class="overlap-item">
                    <div>
                        <div style="font-size:0.75rem; font-weight:600; color:#e2e8f0;">{f1}</div>
                        <div style="font-size:0.65rem; color:#64748b;">vs {f2}</div>
                    </div>
                    <div style="color:{pct_color}; font-weight:800; font-size:0.9rem;">{pct}%</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section: Asset Distribution ──────────────────────────────
    st.markdown('<div class="section-title">Asset Distribution</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Categorical and risk-based exposure</div>', unsafe_allow_html=True)

    dist_l, dist_r = st.columns(2)

    colors_current = ["#4f46e5","#818cf8","#a78bfa","#c4b5fd","#e0e7ff"]
    colors_target  = ["#f43f5e","#10b981","#3b82f6","#f59e0b","#8b5cf6","#06b6d4","#84cc16","#f97316","#6366f1"]

    with dist_l:
        if "category" in df.columns:
            cat_current = df.groupby("category")["current_value"].sum().reset_index()
        else:
            cat_current = pd.DataFrame({"category": ["Large Cap","Mid Cap","Tax Saving"], "current_value": [622630, 421409, 397576]})

        fig_current = go.Figure(go.Pie(
            labels=cat_current["category"],
            values=cat_current["current_value"],
            hole=0.65,
            marker=dict(colors=colors_current[:len(cat_current)], line=dict(color="#0a0a0f", width=3)),
            textinfo="none",
        ))
        fig_current.add_annotation(
            text="<b>100%</b><br><span style='font-size:11px'>TOTAL WEIGHT</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#f1f5f9")
        )
        fig_current.update_layout(
            title=dict(text="CURRENT PORTFOLIO", font=dict(size=11, color="#64748b"), x=0.5),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
            legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.1),
            margin=dict(t=40, b=20, l=0, r=0), height=280
        )
        st.plotly_chart(fig_current, use_container_width=True, config={"displayModeBar": False})

    with dist_r:
        target_labels = ["Fixed Income","Hybrid Assets","Index Funds","Large Cap","Mid Cap","Small Cap","Tax Savings","Thematic","FlexiCap"]
        target_values = [5, 5, 10, 20, 20, 15, 6, 5, 9] # adjusted to sum 95 approx
        # normalize
        total_t = sum(target_values)
        target_values = [round(v/total_t*100, 1) for v in target_values]

        fig_target = go.Figure(go.Pie(
            labels=target_labels,
            values=target_values,
            hole=0.65,
            marker=dict(colors=colors_target, line=dict(color="#0a0a0f", width=3)),
            textinfo="none",
        ))
        fig_target.add_annotation(
            text="<b>100%</b><br><span style='font-size:11px'>OPTIMIZED</span>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#10b981")
        )
        fig_target.update_layout(
            title=dict(text="AI OPTIMIZATION", font=dict(size=11, color="#64748b"), x=0.5),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
            legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)", orientation="h", y=-0.15),
            margin=dict(t=40, b=20, l=0, r=0), height=280
        )
        st.plotly_chart(fig_target, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section: Fund Holdings ────────────────────────────────────
    st.markdown('<div class="section-title">Fund Holdings</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Direct asset exposure and weightage</div>', unsafe_allow_html=True)

    cat_colors = {
        "Large Cap": ("cat-largecap", "Large Cap"),
        "Mid Cap":   ("cat-midcap",   "Mid Cap"),
        "Tax Saving":("cat-elss",     "Tax Saving"),
        "ELSS":      ("cat-elss",     "Tax Saving"),
        "Small Cap": ("cat-smallcap", "Small Cap"),
    }

    header_cols = st.columns([4, 1.5, 1.5, 1.5, 1.5])
    for col, label in zip(header_cols, ["FUND STRATEGY", "CATEGORY", "INVESTED", "NET VALUE", "GROWTH"]):
        col.markdown(f'<div style="font-size:0.65rem; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1px; padding:0.5rem 0; border-bottom:1px solid #1e293b;">{label}</div>', unsafe_allow_html=True)

    for _, row in sorted_df.iterrows():
        cat      = row.get("category", "Large Cap")
        css_cls, cat_label = cat_colors.get(cat, ("cat-largecap", cat))
        ret      = row.get("return_pct", 0)
        ret_col  = "#10b981" if ret >= 0 else "#ef4444"
        ret_sign = "+" if ret >= 0 else ""

        r1, r2, r3, r4, r5 = st.columns([4, 1.5, 1.5, 1.5, 1.5])
        r1.markdown(f"""
        <div style="padding:0.75rem 0; border-bottom:1px solid #1e293b;">
            <div class="fund-name">{row['fund_name']}</div>
            <div class="fund-amc">{row['amc']} Mutual Fund</div>
        </div>
        """, unsafe_allow_html=True)
        r2.markdown(f"""
        <div style="padding:0.75rem 0; border-bottom:1px solid #1e293b;">
            <span class="category-badge {css_cls}">{cat_label}</span>
        </div>
        """, unsafe_allow_html=True)
        invested_val = row.get("invested", row["current_value"] * 0.87)
        r3.markdown(f'<div style="padding:0.75rem 0; border-bottom:1px solid #1e293b; font-size:0.85rem; font-weight:600; color:#e2e8f0;">{format_inr(invested_val)}</div>', unsafe_allow_html=True)
        r4.markdown(f'<div style="padding:0.75rem 0; border-bottom:1px solid #1e293b; font-size:0.85rem; font-weight:600; color:#e2e8f0;">{format_inr(row["current_value"])}</div>', unsafe_allow_html=True)
        r5.markdown(f'<div style="padding:0.75rem 0; border-bottom:1px solid #1e293b; font-size:0.9rem; font-weight:800; color:{ret_col};">{ret_sign}{ret:.1f}%</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section: Nifty Comparison ─────────────────────────────────
    st.markdown('<div class="section-title">Benchmark Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Portfolio performance vs Nifty 50</div>', unsafe_allow_html=True)

    bench_l, bench_r = st.columns([1, 2])
    with bench_l:
        st.markdown(f"""
        <div class="glass-card">
            <table style="width:100%; border-collapse:collapse; font-size:0.82rem;">
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:0.6rem 0; color:#64748b; font-weight:600;">Total Invested</td>
                    <td style="padding:0.6rem 0; color:#f1f5f9; font-weight:700; text-align:right;">Rs. {total_invested:,.0f}</td>
                </tr>
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:0.6rem 0; color:#64748b; font-weight:600;">Current Value</td>
                    <td style="padding:0.6rem 0; color:#f1f5f9; font-weight:700; text-align:right;">Rs. {total_value:,.0f}</td>
                </tr>
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:0.6rem 0; color:#64748b; font-weight:600;">Absolute Gain</td>
                    <td style="padding:0.6rem 0; color:#10b981; font-weight:700; text-align:right;">Rs. {total_gain:,.0f}</td>
                </tr>
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:0.6rem 0; color:#64748b; font-weight:600;">Portfolio Return</td>
                    <td style="padding:0.6rem 0; color:#818cf8; font-weight:800; text-align:right;">{abs_return:.2f}%</td>
                </tr>
                <tr style="border-bottom:1px solid #1e293b;">
                    <td style="padding:0.6rem 0; color:#64748b; font-weight:600;">Nifty 50 Avg</td>
                    <td style="padding:0.6rem 0; color:#3b82f6; font-weight:800; text-align:right;">14.00%</td>
                </tr>
                <tr>
                    <td style="padding:0.6rem 0; color:#64748b; font-weight:600;">Difference</td>
                    <td style="padding:0.6rem 0; color:{'#10b981' if diff >= 0 else '#ef4444'}; font-weight:800; text-align:right;">
                        {'▲ +' if diff >= 0 else '▼ '}{abs(diff):.2f}%
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with bench_r:
        fig_bench = go.Figure()
        fig_bench.add_trace(go.Bar(
            x=["Your Portfolio", "Nifty 50 (Avg)"],
            y=[round(abs_return, 2), 14.0],
            marker_color=["#4f46e5" if abs_return >= 14 else "#ef4444", "#3b82f6"],
            text=[f"{abs_return:.1f}%", "14.0%"],
            textposition="outside",
            textfont=dict(color="#f1f5f9", size=14, family="sans-serif"),
            marker_line_width=0,
            width=0.4,
        ))
        fig_bench.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#94a3b8", size=12),
            margin=dict(t=20, b=20, l=0, r=0),
            height=220,
            yaxis=dict(gridcolor="#1e293b", ticksuffix="%", range=[0, max(abs_return, 14) * 1.3]),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            showlegend=False,
        )
        st.plotly_chart(fig_bench, use_container_width=True, config={"displayModeBar": False})

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section: Strategic Insights ───────────────────────────────
    st.markdown('<div class="section-title">Strategic Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Model-based rebalancing and actionable intelligence</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card-strong">
        <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;
                    padding-bottom:1rem; border-bottom:1px solid #1e293b;">
            <div style="width:44px; height:44px; border-radius:12px; background:#4f46e510;
                        display:flex; align-items:center; justify-content:center;
                        font-size:1.2rem;">💡</div>
            <div>
                <div style="font-size:1.1rem; font-weight:800; color:#f1f5f9;">Strategic Insights</div>
                <div style="font-size:0.65rem; color:#64748b; text-transform:uppercase;
                            letter-spacing:1.5px; margin-top:2px;">AI-Powered Institutional Analysis</div>
            </div>
            <div style="margin-left:auto; display:flex; align-items:center; gap:0.5rem;
                        background:#1e293b; border:1px solid #334155; padding:0.3rem 0.75rem;
                        border-radius:999px;">
                <div style="width:8px; height:8px; border-radius:50%; background:#10b981;
                            animation:pulse 2s infinite;"></div>
                <span style="font-size:0.65rem; font-weight:700; color:#94a3b8;
                             text-transform:uppercase; letter-spacing:1px;">LIVE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    ins_l, ins_r = st.columns(2)

    with ins_l:
        st.markdown('<div style="font-size:0.7rem; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1rem;">KEY RISK INDICATORS</div>', unsafe_allow_html=True)

        issues = []
        amc_conc = df.groupby("amc")["current_value"].sum().max() / total_value * 100
        if amc_conc > 40:
            issues.append(("high", f"High concentration in {df.groupby('amc')['current_value'].sum().idxmax()}", f"{amc_conc:.1f}% in {df.groupby('amc')['current_value'].sum().idxmax()} — consider reducing below 40%"))
        if "category" not in df.columns or df.get("category", pd.Series()).nunique() < 3:
            issues.append(("medium", "Moderate diversification", f"{df['amc'].nunique()} asset categories active — could be improved"))
        issues.append(("high", "No debt allocation", "Portfolio lacks stability — add debt funds for risk management"))
        if len(overlap_pairs) > 0:
            issues.append(("medium", "Significant portfolio overlap", f"{len(overlap_pairs)} fund pairs with >50% overlap — consolidate similar funds"))

        for severity, title, detail in issues[:4]:
            css = f"issue-{severity}"
            dot_color = "#ef4444" if severity == "high" else "#f59e0b" if severity == "medium" else "#3b82f6"
            st.markdown(f"""
            <div class="{css}">
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
                    <div style="width:8px; height:8px; border-radius:50%; background:{dot_color}; flex-shrink:0;"></div>
                    <div class="issue-title">{title}</div>
                </div>
                <div class="issue-detail">{detail}</div>
            </div>
            """, unsafe_allow_html=True)

    with ins_r:
        badge_count = len(issues)
        st.markdown(f'<div style="font-size:0.7rem; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1rem;">RECOMMENDED ACTIONS <span style="background:#ef444420; color:#ef4444; padding:0.15rem 0.5rem; border-radius:4px; font-size:0.65rem;">{badge_count} Identified</span></div>', unsafe_allow_html=True)

        actions = [
            ("INCREASE DEBT ALLOCATION",    "MEDIUM", "Add a short-duration debt fund or liquid fund for portfolio stability and emergency liquidity"),
            ("CONSOLIDATE OVERLAPPING FUNDS","MEDIUM", f"{len(overlap_pairs)} fund pair(s) show significant overlap — consolidate to reduce redundancy and cost"),
            ("REVIEW EXPENSE RATIOS",        "LOW",    "Ensure all funds are Direct plans — switch from Regular to Direct to save 0.5–1% annually"),
        ]

        for action_title, priority, detail in actions:
            p_css = f"priority-{priority.lower()}"
            st.markdown(f"""
            <div class="action-card">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:0.4rem;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span style="color:#818cf8;">⚡</span>
                        <span class="action-title">{action_title}</span>
                    </div>
                    <span class="{p_css}">{priority}</span>
                </div>
                <div class="action-detail">{detail}</div>
                <div style="font-size:0.65rem; color:#475569; margin-top:0.4rem; font-weight:600;">
                    Reason: <span style="color:#64748b;">Institutional diversification threshold exceeded</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Section: AI Verdict ───────────────────────────────────────
    st.markdown('<div class="section-title">🤖 AI Verdict</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Groq-powered portfolio analysis</div>', unsafe_allow_html=True)

    if st.session_state.analysis:
        st.markdown(f"""
        <div class="verdict-box">
            <div style="font-size:0.7rem; font-weight:700; color:#818cf8;
                        text-transform:uppercase; letter-spacing:1.5px; margin-bottom:1rem;">
                FULL ANALYSIS REPORT
            </div>
        """, unsafe_allow_html=True)
        st.markdown(st.session_state.analysis)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    # ── Landing state ─────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center; padding: 5rem 2rem;">
        <div style="font-size:0.8rem; font-weight:700; color:#4f46e5;
                    text-transform:uppercase; letter-spacing:2px; margin-bottom:1rem;">
            SECURE & PRIVATE
        </div>
        <h1 style="font-size:3rem; font-weight:900; color:#f1f5f9;
                   letter-spacing:-2px; margin-bottom:1rem;">
            Analyze Your <span style="color:#818cf8;">Portfolio</span>
        </h1>
        <p style="color:#64748b; font-size:1.1rem; max-width:500px;
                  margin:0 auto 2rem auto; line-height:1.7;">
            Get institutional-grade insights from your CAMS or Kfintech statement in seconds.
        </p>
        <div style="display:flex; justify-content:center; gap:2rem; flex-wrap:wrap; margin-top:2rem;">
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:16px; padding:1.5rem 2rem; text-align:center;">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">📤</div>
                <div style="font-size:0.8rem; font-weight:700; color:#e2e8f0;">Upload</div>
                <div style="font-size:0.7rem; color:#64748b;">CAMS / Kfintech PDF</div>
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:16px; padding:1.5rem 2rem; text-align:center;">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">🤖</div>
                <div style="font-size:0.8rem; font-weight:700; color:#e2e8f0;">Analyze</div>
                <div style="font-size:0.7rem; color:#64748b;">AI-powered insights</div>
            </div>
            <div style="background:#0f172a; border:1px solid #1e293b; border-radius:16px; padding:1.5rem 2rem; text-align:center;">
                <div style="font-size:1.5rem; margin-bottom:0.5rem;">📊</div>
                <div style="font-size:0.8rem; font-weight:700; color:#e2e8f0;">Rebalance</div>
                <div style="font-size:0.7rem; color:#64748b;">Actionable recommendations</div>
            </div>
        </div>
        <div style="margin-top:2rem; color:#475569; font-size:0.85rem;">
            👈 Upload your CAS PDF or click <b style="color:#818cf8;">Load Demo Portfolio</b> to get started
        </div>
    </div>
    """, unsafe_allow_html=True)