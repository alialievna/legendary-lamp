import streamlit as st
import pandas as pd
import plotly.express as px

from utils.parser import parse_sales, parse_returns, parse_stock
from utils.metrics import compute_metrics
from utils.alerts import generate_alerts
from utils.summary import generate_summary
from utils.export import export_csv, export_pdf

st.set_page_config(
    page_title="Flowmetric Analytics",
    page_icon="■",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #F4F1EB !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: #FFFFFF !important;
    border-right: 1px solid #E8E4DC !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] div { color: #374151; }

/* Sidebar nav buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important;
    text-align: left !important; justify-content: flex-start !important;
    color: #4B5563 !important; padding: 7px 14px !important;
    border-radius: 6px !important; width: 100% !important;
    font-size: 0.83rem !important; font-weight: 500 !important;
    box-shadow: none !important; transition: background 0.1s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover { background: #F4F1EB !important; color: #111827 !important; }
section[data-testid="stSidebar"] .stButton > button:disabled { color: #D1D5DB !important; cursor: default !important; }

/* Sidebar search */
section[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    font-size: 0.8rem !important; border: 1px solid #E8E4DC !important;
    border-radius: 8px !important; background: #F9F8F5 !important;
    color: #374151 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important; border-bottom: 1px solid #E8E4DC !important;
    padding: 0 !important; gap: 0 !important; margin-bottom: 20px !important; box-shadow: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    border-bottom: 2px solid transparent !important; color: #6B7280 !important;
    font-size: 0.84rem !important; font-weight: 500 !important;
    padding: 10px 18px !important; border-radius: 0 !important; margin-bottom: -1px !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #111827 !important; border-bottom-color: #111827 !important; font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-border"], .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Bordered containers → white cards ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important; border: 1px solid #E8E4DC !important;
    border-radius: 12px !important; box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: #111827 !important; color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.84rem !important;
}

/* ── Success / info messages ── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── KPI card ── */
.kpi-card {
    background: white; border-radius: 12px; padding: 18px 20px;
    border: 1px solid #E8E4DC; box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.kpi-label { font-size: 0.67rem; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.09em; margin-bottom: 10px; }
.kpi-value { font-size: 1.55rem; font-weight: 700; color: #111827; margin-bottom: 10px; line-height: 1.1; }
.kpi-bar { height: 3px; background: #F0EDE8; border-radius: 2px; overflow: hidden; margin-bottom: 8px; }
.kpi-bar-fill { height: 100%; border-radius: 2px; }
.kpi-sub { font-size: 0.72rem; color: #9CA3AF; }

/* ── Alert table ── */
.alert-row {
    display: flex; align-items: center; padding: 11px 16px;
    border-bottom: 1px solid #F3F0EB; gap: 12px;
}
.alert-row:last-child { border-bottom: none; }
.a-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.a-dot-c { background: #EF4444; }
.a-dot-w { background: #F59E0B; }
.a-name { flex: 1; font-size: 0.84rem; font-weight: 600; color: #111827; min-width: 0; }
.a-cond { flex: 2; font-size: 0.79rem; color: #6B7280; padding: 0 8px; min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.a-badge { padding: 2px 8px; border-radius: 4px; font-size: 0.66rem; font-weight: 700; letter-spacing: 0.04em; white-space: nowrap; }
.a-firing { background: #FEE2E2; color: #DC2626; }
.a-warning { background: #FEF3C7; color: #D97706; }

/* ── Top-3 list ── */
.top3-row { display:flex; align-items:center; padding:10px 0; border-bottom:1px solid #F4F1EB; }
.top3-row:last-child { border-bottom:none; }
.top3-rank { width:24px; height:24px; border-radius:50%; background:#F4F1EB; color:#374151; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.72rem; flex-shrink:0; }
.top3-name { flex:1; padding:0 12px; color:#374151; font-size:0.82rem; line-height:1.3; }
.top3-sku-sub { color:#9CA3AF; font-size:0.71rem; }
.top3-val { font-weight:700; color:#111827; font-size:0.82rem; }

/* ── Section heading ── */
.sec-head { font-size:0.82rem; font-weight:700; color:#111827; margin-bottom:12px; }

/* ── Upload file card ── */
.ufc {
    background: white; border-radius: 12px; padding: 18px;
    border: 1px solid #E8E4DC;
}
.ufc-ok { border-color: #86EFAC; background: #F0FDF4; }
.ufc-err { border-color: #FCA5A5; background: #FEF2F2; }
.ufc-icon { font-size: 1.5rem; margin-bottom: 8px; }
.ufc-title { font-size: 0.88rem; font-weight: 700; color: #111827; margin-bottom: 4px; }
.ufc-badge-req { background: #FEF3C7; color: #92400E; padding: 1px 7px; border-radius: 4px; font-size: 0.66rem; font-weight: 700; display:inline-block; margin-bottom:6px; }
.ufc-badge-opt { background: #D1FAE5; color: #065F46; padding: 1px 7px; border-radius: 4px; font-size: 0.66rem; font-weight: 700; display:inline-block; margin-bottom:6px; }
.ufc-hint { font-size: 0.74rem; color: #9CA3AF; line-height: 1.5; margin-bottom: 10px; }
.ufc-ok-text { font-size: 0.76rem; font-weight: 600; color: #16A34A; margin-top: 6px; }
.ufc-err-text { font-size: 0.76rem; font-weight: 600; color: #DC2626; margin-top: 6px; }

/* ── Summary card ── */
.summary-card {
    background: white; border-radius: 12px; padding: 18px 22px;
    border: 1px solid #E8E4DC; border-left: 3px solid #111827;
    color: #1E293B; font-size: 0.88rem; line-height: 1.75; margin-bottom: 20px;
}
.summary-label { font-size: 0.65rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }

/* ── Nav active ── */
.nav-active {
    background: #F4F1EB; color: #111827 !important; padding: 7px 14px;
    border-radius: 6px; font-size: 0.83rem; font-weight: 700;
    display: block; margin-bottom: 2px;
}

/* ── New report button ── */
.btn-primary > button {
    background: #111827 !important; color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.84rem !important;
    padding: 8px 16px !important;
}
.btn-primary > button:hover { background: #1F2937 !important; }

/* ── Export button ── */
.btn-outline > button {
    background: white !important; color: #374151 !important;
    border: 1px solid #D1CCC4 !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 0.84rem !important;
}

/* ── Misc ── */
hr { border: none !important; border-top: 1px solid #E8E4DC !important; margin: 12px 0 !important; }
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #F4F1EB; }
::-webkit-scrollbar-thumb { background: #D1CCC4; border-radius: 2px; }
[data-testid="stPlotlyChart"] { border-radius: 10px !important; }
[data-testid="stDataFrame"] { border-radius: 10px !important; overflow: hidden !important; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
PALETTE = ["#374151","#6B7280","#9CA3AF","#3B82F6","#22C55E","#F59E0B","#EF4444","#8B5CF6"]


def _fmt_rev(v: float) -> str:
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M ₽"
    if v >= 1_000:     return f"{v/1_000:.0f}K ₽"
    return f"{v:,.0f} ₽"


def _chart(fig, title=""):
    if title:
        fig.update_layout(title=dict(text=title, font=dict(size=12, color="#111827", family="Inter"), pad=dict(b=10)))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#374151", size=11),
        xaxis=dict(gridcolor="#F4F1EB", zeroline=False, showline=False, tickfont=dict(size=10, color="#9CA3AF")),
        yaxis=dict(gridcolor="#F4F1EB", zeroline=False, showline=False, tickfont=dict(size=10, color="#9CA3AF")),
        margin=dict(l=8, r=8, t=36, b=8),
        hoverlabel=dict(bgcolor="white", bordercolor="#E8E4DC", font=dict(size=11, color="#111827")),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#E8E4DC", borderwidth=1, font=dict(size=10)),
        coloraxis_showscale=False,
    )
    return fig


def _kpi_cards(metrics, n_days):
    rr = metrics["return_rate"]
    rc = "#EF4444" if rr > 20 else "#F59E0B" if rr > 15 else "#22C55E"
    rp = min(rr / 30 * 100, 100)
    rev_pct = min(metrics["total_revenue"] / 30_000_000 * 100, 100)
    sold_pct = min(metrics["total_sold"] / 15_000 * 100, 100)
    conv_pct = min(metrics["avg_conversion"] / 5 * 100, 100)

    cards_html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px">'
    for label, value, pct, color in [
        ("Выручка",     _fmt_rev(metrics["total_revenue"]), rev_pct,  "#111827"),
        ("Продано",     f"{metrics['total_sold']:,} шт.",   sold_pct, "#374151"),
        ("% возвратов", f"{rr:.1f}%",                       rp,       rc),
        ("Конверсия",   f"{metrics['avg_conversion']:.2f}%",conv_pct, "#374151"),
    ]:
        cards_html += (
            f'<div class="kpi-card">'
            f'<div class="kpi-label">{label}</div>'
            f'<div class="kpi-value">{value}</div>'
            f'<div class="kpi-bar"><div class="kpi-bar-fill" style="width:{pct:.0f}%;background:{color}"></div></div>'
            f'<div class="kpi-sub">{metrics["period"]}</div>'
            f'</div>'
        )
    cards_html += '</div>'
    return cards_html


def _alerts_table(alerts):
    if not alerts:
        return '<div style="padding:20px;color:#22C55E;font-weight:600;text-align:center">✓ Все показатели в норме</div>'
    sorted_a = sorted(alerts, key=lambda a: 0 if a["level"] == "critical" else 1)
    header = (
        '<div style="display:flex;align-items:center;padding:8px 16px;'
        'border-bottom:1px solid #E8E4DC;gap:12px;">'
        '<div style="width:7px"></div>'
        '<div style="flex:1;font-size:0.67rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em">Алерт</div>'
        '<div style="flex:2;font-size:0.67rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em;padding:0 8px">Описание</div>'
        '<div style="font-size:0.67rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em">Статус</div>'
        '</div>'
    )
    rows = ""
    for a in sorted_a:
        dot_cls = "a-dot-c" if a["level"] == "critical" else "a-dot-w"
        badge_cls = "a-firing" if a["level"] == "critical" else "a-warning"
        badge_txt = "FIRING" if a["level"] == "critical" else "WARNING"
        rows += (
            f'<div class="alert-row">'
            f'<div class="a-dot {dot_cls}"></div>'
            f'<div class="a-name">{a["sku"]}</div>'
            f'<div class="a-cond">{a["message"]}</div>'
            f'<span class="a-badge {badge_cls}">{badge_txt}</span>'
            f'</div>'
        )
    return header + rows


def _top3_html(items, val_key, fmt):
    html = ""
    for i, item in enumerate(items, 1):
        html += (
            f'<div class="top3-row">'
            f'<div class="top3-rank">{i}</div>'
            f'<div class="top3-name">{item["name"]}<br>'
            f'<span class="top3-sku-sub">{item["sku"]}</span></div>'
            f'<div class="top3-val">{fmt(item[val_key])}</div></div>'
        )
    return html


def _topbar(breadcrumb: str, title: str, show_new_report_btn=True):
    bc_html = (
        f'<div style="background:white;border-bottom:1px solid #E8E4DC;padding:14px 32px;">'
        f'<div style="font-size:0.7rem;color:#9CA3AF;margin-bottom:2px">{breadcrumb}</div>'
        f'<div style="font-size:1.15rem;font-weight:700;color:#111827">{title}</div>'
        f'</div>'
    )
    if show_new_report_btn:
        col_l, col_r = st.columns([6, 1])
        with col_l:
            st.markdown(bc_html, unsafe_allow_html=True)
        with col_r:
            st.markdown(
                '<div style="background:white;border-bottom:1px solid #E8E4DC;'
                'padding:18px 16px 14px;display:flex;justify-content:flex-end">',
                unsafe_allow_html=True,
            )
            st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
            if st.button("□ New report", use_container_width=True, key="topbar_new"):
                st.session_state["show_upload"] = True
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(bc_html, unsafe_allow_html=True)


# ─── Session state ─────────────────────────────────────────────────────────────
for _k, _v in [("result", None), ("page", "overview"), ("show_upload", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:18px 14px 10px;display:flex;align-items:center;gap:9px">'
        '<div style="background:#111827;border-radius:6px;width:27px;height:27px;'
        'display:flex;align-items:center;justify-content:center;font-size:12px;'
        'color:white;font-weight:700;flex-shrink:0">F</div>'
        '<span style="font-weight:800;font-size:0.9rem;color:#111827;letter-spacing:-0.01em">FLOWMETRIC</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.text_input("", placeholder="🔍  Search...", label_visibility="collapsed", key="sb_search")
    st.markdown(
        '<div style="font-size:0.65rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;'
        'letter-spacing:0.1em;padding:10px 14px 4px">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    has_data = st.session_state["result"] is not None
    cur_page = st.session_state["page"]
    in_upload = st.session_state["show_upload"] or not has_data

    NAV = [
        ("overview",  "Overview"),
        ("products",  "Товары"),
        ("returns",   "Возвраты"),
        ("stock",     "Остатки"),
        ("alerts",    "Алерты"),
        ("export",    "Экспорт"),
    ]
    for pid, plabel in NAV:
        is_active = has_data and not in_upload and cur_page == pid
        if is_active:
            st.markdown(f'<div class="nav-active">● {plabel}</div>', unsafe_allow_html=True)
        else:
            if st.button(f"  {plabel}", key=f"nav_{pid}", disabled=not has_data, use_container_width=True):
                st.session_state["page"] = pid
                st.session_state["show_upload"] = False
                st.rerun()

    st.markdown('<hr>', unsafe_allow_html=True)

    if has_data:
        m = st.session_state["result"]["metrics"]
        st.markdown(
            f'<div style="padding:4px 14px 8px">'
            f'<div style="font-size:0.65rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;'
            f'letter-spacing:0.08em;margin-bottom:6px">ДАННЫЕ</div>'
            f'<div style="font-size:0.78rem;color:#374151;font-weight:600">{m["period"]}</div>'
            f'<div style="font-size:0.73rem;color:#9CA3AF">{m["sku_count"]} SKU</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="padding:4px 14px 8px;font-size:0.78rem;color:#9CA3AF">'
            'Загрузите данные для начала работы</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="margin-top:20px;padding:12px 14px;border-top:1px solid #E8E4DC;'
        'display:flex;align-items:center;gap:9px">'
        '<div style="background:#E5E7EB;border-radius:50%;width:27px;height:27px;'
        'display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#374151">A</div>'
        '<span style="font-size:0.8rem;font-weight:500;color:#374151">Аналитик</span>'
        '</div>',
        unsafe_allow_html=True,
    )

# ─── Main content padding wrapper ─────────────────────────────────────────────
# ─── Upload / Report builder ──────────────────────────────────────────────────
if in_upload:
    _topbar("REPORTS", "New report", show_new_report_btn=False)

    st.markdown('<div style="padding:28px 32px">', unsafe_allow_html=True)

    # Back button if data already exists
    if has_data:
        st.markdown('<div class="btn-outline">', unsafe_allow_html=True)
        if st.button("← Back to dashboard"):
            st.session_state["show_upload"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)

    # Stepper
    st.markdown("""
    <div style="display:flex;align-items:center;margin-bottom:28px">
        <div style="display:flex;align-items:center;gap:8px">
            <div style="background:#111827;color:white;border-radius:50%;width:26px;height:26px;
                        display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:700">1</div>
            <span style="font-size:0.82rem;font-weight:700;color:#111827">Upload data</span>
        </div>
        <div style="width:64px;height:1px;background:#D1CCC4;margin:0 10px"></div>
        <div style="display:flex;align-items:center;gap:8px">
            <div style="border:2px solid #D1CCC4;color:#9CA3AF;border-radius:50%;width:26px;height:26px;
                        display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:700">2</div>
            <span style="font-size:0.82rem;font-weight:500;color:#9CA3AF">Analyze</span>
        </div>
        <div style="width:64px;height:1px;background:#D1CCC4;margin:0 10px"></div>
        <div style="display:flex;align-items:center;gap:8px">
            <div style="border:2px solid #D1CCC4;color:#9CA3AF;border-radius:50%;width:26px;height:26px;
                        display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:700">3</div>
            <span style="font-size:0.82rem;font-weight:500;color:#9CA3AF">Results</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Two-column layout: file upload left, what you'll get right
    up_col, prev_col = st.columns([3, 2], gap="large")

    sales_ok = returns_ok = stock_ok = False
    sales_file = returns_file = stock_file = campaign_file = None

    with up_col:
        st.markdown('<div class="sec-head">Загрузите файлы с данными</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.8rem;color:#6B7280;margin-bottom:16px">Первые три файла обязательны. Четвёртый добавит описание кампании в сводку.</div>', unsafe_allow_html=True)

        row1_c1, row1_c2 = st.columns(2, gap="medium")
        row2_c1, row2_c2 = st.columns(2, gap="medium")

        # sales.csv
        with row1_c1:
            sales_file = st.file_uploader("sales", type=["csv"], key="sf", label_visibility="collapsed")
            if sales_file:
                try:
                    parse_sales(sales_file); sales_ok = True
                    st.markdown('<div class="ufc ufc-ok"><div class="ufc-icon">📈</div><div class="ufc-title">sales.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">дата · SKU · выручка · сессии</div><div class="ufc-ok-text">✓ Файл проверен</div></div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="ufc ufc-err"><div class="ufc-icon">📈</div><div class="ufc-title">sales.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">дата · SKU · выручка · сессии</div><div class="ufc-err-text">✗ {e}</div></div>', unsafe_allow_html=True)
                finally:
                    sales_file.seek(0)
            else:
                st.markdown('<div class="ufc"><div class="ufc-icon">📈</div><div class="ufc-title">sales.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">дата · SKU · выручка · сессии</div><div style="font-size:0.74rem;color:#D1D5DB">Ожидание файла</div></div>', unsafe_allow_html=True)

        # returns.csv
        with row1_c2:
            returns_file = st.file_uploader("returns", type=["csv"], key="rf", label_visibility="collapsed")
            if returns_file:
                try:
                    parse_returns(returns_file); returns_ok = True
                    st.markdown('<div class="ufc ufc-ok"><div class="ufc-icon">↩</div><div class="ufc-title">returns.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">дата · SKU · возвраты · причина</div><div class="ufc-ok-text">✓ Файл проверен</div></div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="ufc ufc-err"><div class="ufc-icon">↩</div><div class="ufc-title">returns.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">дата · SKU · возвраты · причина</div><div class="ufc-err-text">✗ {e}</div></div>', unsafe_allow_html=True)
                finally:
                    returns_file.seek(0)
            else:
                st.markdown('<div class="ufc"><div class="ufc-icon">↩</div><div class="ufc-title">returns.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">дата · SKU · возвраты · причина</div><div style="font-size:0.74rem;color:#D1D5DB">Ожидание файла</div></div>', unsafe_allow_html=True)

        # stock.csv
        with row2_c1:
            stock_file = st.file_uploader("stock", type=["csv"], key="stf", label_visibility="collapsed")
            if stock_file:
                try:
                    parse_stock(stock_file); stock_ok = True
                    st.markdown('<div class="ufc ufc-ok"><div class="ufc-icon">📦</div><div class="ufc-title">stock.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">SKU · остаток · склад</div><div class="ufc-ok-text">✓ Файл проверен</div></div>', unsafe_allow_html=True)
                except Exception as e:
                    st.markdown(f'<div class="ufc ufc-err"><div class="ufc-icon">📦</div><div class="ufc-title">stock.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">SKU · остаток · склад</div><div class="ufc-err-text">✗ {e}</div></div>', unsafe_allow_html=True)
                finally:
                    stock_file.seek(0)
            else:
                st.markdown('<div class="ufc"><div class="ufc-icon">📦</div><div class="ufc-title">stock.csv</div><div class="ufc-badge-req">Обязательный</div><div class="ufc-hint">SKU · остаток · склад</div><div style="font-size:0.74rem;color:#D1D5DB">Ожидание файла</div></div>', unsafe_allow_html=True)

        # campaign_info.txt
        with row2_c2:
            campaign_file = st.file_uploader("campaign", type=["txt"], key="cf", label_visibility="collapsed")
            if campaign_file:
                st.markdown('<div class="ufc ufc-ok"><div class="ufc-icon">📣</div><div class="ufc-title">campaign_info.txt</div><div class="ufc-badge-opt">Необязательный</div><div class="ufc-hint">Описание маркетинговой акции</div><div class="ufc-ok-text">✓ Файл загружен</div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ufc"><div class="ufc-icon">📣</div><div class="ufc-title">campaign_info.txt</div><div class="ufc-badge-opt">Необязательный</div><div class="ufc-hint">Описание маркетинговой акции</div><div style="font-size:0.74rem;color:#D1D5DB">Пропустить</div></div>', unsafe_allow_html=True)

        st.markdown('<div style="height:20px"></div>', unsafe_allow_html=True)

        can_run = bool(sales_file and returns_file and stock_file and sales_ok and returns_ok and stock_ok)
        if not can_run:
            missing = [n for n, ok in [("sales.csv", sales_ok), ("returns.csv", returns_ok), ("stock.csv", stock_ok)] if not ok]
            if missing:
                st.markdown(f'<div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:8px">Загрузите обязательные файлы: {", ".join(missing)}</div>', unsafe_allow_html=True)

        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        run_btn = st.button(
            "Continue →" if can_run else "⬆  Загрузите файлы выше",
            disabled=not can_run,
            use_container_width=False,
            key="run_btn",
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with prev_col:
        st.markdown("""
        <div style="background:white;border-radius:12px;border:1px solid #E8E4DC;padding:22px;margin-top:36px">
            <div style="font-size:0.67rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.09em;margin-bottom:16px">ЧТО ВЫ ПОЛУЧИТЕ</div>
            <div style="display:flex;flex-direction:column;gap:14px">
                <div style="display:flex;gap:12px;align-items:flex-start">
                    <div style="background:#F4F1EB;border-radius:8px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0">📊</div>
                    <div><div style="font-weight:600;font-size:0.84rem;color:#111827;margin-bottom:2px">KPI и метрики</div><div style="font-size:0.76rem;color:#6B7280;line-height:1.45">Выручка, продажи, конверсия, % возвратов по каждому SKU</div></div>
                </div>
                <div style="display:flex;gap:12px;align-items:flex-start">
                    <div style="background:#F4F1EB;border-radius:8px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0">📈</div>
                    <div><div style="font-weight:600;font-size:0.84rem;color:#111827;margin-bottom:2px">Интерактивные графики</div><div style="font-size:0.76rem;color:#6B7280;line-height:1.45">Динамика выручки, топ SKU, остатки, причины возвратов</div></div>
                </div>
                <div style="display:flex;gap:12px;align-items:flex-start">
                    <div style="background:#FEF3C7;border-radius:8px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0">🚨</div>
                    <div><div style="font-weight:600;font-size:0.84rem;color:#111827;margin-bottom:2px">Автоматические алерты</div><div style="font-size:0.76rem;color:#6B7280;line-height:1.45">7 типов проблем: критичные и предупреждения</div></div>
                </div>
                <div style="display:flex;gap:12px;align-items:flex-start">
                    <div style="background:#D1FAE5;border-radius:8px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0">📋</div>
                    <div><div style="font-weight:600;font-size:0.84rem;color:#111827;margin-bottom:2px">Текстовая сводка</div><div style="font-size:0.76rem;color:#6B7280;line-height:1.45">Связный отчёт без AI и сторонних API</div></div>
                </div>
                <div style="display:flex;gap:12px;align-items:flex-start">
                    <div style="background:#EDE9FF;border-radius:8px;width:34px;height:34px;display:flex;align-items:center;justify-content:center;font-size:15px;flex-shrink:0">📥</div>
                    <div><div style="font-weight:600;font-size:0.84rem;color:#111827;margin-bottom:2px">Экспорт PDF и CSV</div><div style="font-size:0.76rem;color:#6B7280;line-height:1.45">Скачайте готовый отчёт одним нажатием</div></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Run analysis
    if run_btn and can_run:
        with st.spinner("Анализирую данные…"):
            for f in (sales_file, returns_file, stock_file):
                f.seek(0)
            sales    = parse_sales(sales_file)
            returns  = parse_returns(returns_file)
            stock    = parse_stock(stock_file)
            campaign = campaign_file.read().decode("utf-8") if campaign_file else ""
            metrics  = compute_metrics(sales, returns, stock)
            alerts   = generate_alerts(metrics, sales)
            summary  = generate_summary(metrics, alerts, campaign)
            st.session_state["result"] = dict(
                metrics=metrics, alerts=alerts, summary=summary,
                sales=sales, returns=returns, stock=stock,
            )
            st.session_state["page"] = "overview"
            st.session_state["show_upload"] = False
        st.rerun()

# ─── Results pages ─────────────────────────────────────────────────────────────
else:
    res     = st.session_state["result"]
    metrics = res["metrics"]
    alerts  = res["alerts"]
    smry    = res["summary"]
    sales:   pd.DataFrame = res["sales"]
    returns: pd.DataFrame = res["returns"]
    stock:   pd.DataFrame = res["stock"]
    n_days  = sales["дата"].nunique()

    page = st.session_state["page"]

    PAGE_TITLES = {
        "overview":  ("Workspace / Home",    "Overview"),
        "products":  ("Workspace / Reports", "Товары"),
        "returns":   ("Workspace / Reports", "Возвраты"),
        "stock":     ("Workspace / Reports", "Остатки"),
        "alerts":    ("Workspace / Alerts",  "Alerts"),
        "export":    ("Workspace / Export",  "Экспорт"),
    }
    bc, title = PAGE_TITLES.get(page, ("Workspace", page.capitalize()))
    _topbar(bc, title, show_new_report_btn=True)

    st.markdown('<div style="padding:24px 32px">', unsafe_allow_html=True)

    # ── Overview ──────────────────────────────────────────────────────────────
    if page == "overview":
        st.markdown(_kpi_cards(metrics, n_days), unsafe_allow_html=True)

        ch_l, ch_r = st.columns([3, 2], gap="large")
        with ch_l:
            with st.container(border=True):
                st.markdown('<div class="sec-head">Sessions over time · Динамика выручки</div>', unsafe_allow_html=True)
                daily = sales.groupby("дата")["выручка"].sum().reset_index()
                fig = px.line(daily, x="дата", y="выручка", labels={"дата": "", "выручка": "Выручка (₽)"})
                fig.update_traces(line_color="#111827", line_width=2,
                                  fill="tozeroy", fillcolor="rgba(17,24,39,0.05)")
                st.plotly_chart(_chart(fig), use_container_width=True)

        with ch_r:
            with st.container(border=True):
                st.markdown('<div class="sec-head">By channel · По категориям</div>', unsafe_allow_html=True)
                if "категория" in sales.columns:
                    cat = sales.groupby("категория")["выручка"].sum().reset_index()
                    fig_p = px.pie(cat, names="категория", values="выручка",
                                   color_discrete_sequence=["#111827","#374151","#6B7280","#9CA3AF","#D1D5DB"],
                                   hole=0.5)
                    fig_p.update_traces(textposition="outside", textinfo="percent+label", textfont_size=10)
                    st.plotly_chart(_chart(fig_p), use_container_width=True)

        # Recent reports row
        tr_l, tr_r = st.columns(2, gap="large")
        with tr_l:
            with st.container(border=True):
                hdr_l, hdr_r = st.columns([3, 1])
                with hdr_l:
                    st.markdown('<div class="sec-head">Топ SKU по выручке</div>', unsafe_allow_html=True)
                with hdr_r:
                    st.markdown('<div style="font-size:0.72rem;color:#9CA3AF;padding-top:2px;text-align:right">VIEW ALL →</div>', unsafe_allow_html=True)
                st.markdown(_top3_html(metrics["top3_revenue"], "revenue", lambda v: f"{v:,.0f} ₽"),
                            unsafe_allow_html=True)

        with tr_r:
            with st.container(border=True):
                hdr_l, hdr_r = st.columns([3, 1])
                with hdr_l:
                    st.markdown('<div class="sec-head">Топ SKU по продажам</div>', unsafe_allow_html=True)
                with hdr_r:
                    st.markdown('<div style="font-size:0.72rem;color:#9CA3AF;padding-top:2px;text-align:right">VIEW ALL →</div>', unsafe_allow_html=True)
                st.markdown(_top3_html(metrics["top3_sold"], "sold", lambda v: f"{int(v):,} шт."),
                            unsafe_allow_html=True)

        # Summary
        st.markdown(
            f'<div class="summary-card"><div class="summary-label">Автоматическая сводка</div>{smry}</div>',
            unsafe_allow_html=True,
        )

    # ── Products ──────────────────────────────────────────────────────────────
    elif page == "products":
        sku_m = metrics["sku_metrics"]
        with st.container(border=True):
            st.markdown('<div class="sec-head">Топ-10 SKU по выручке</div>', unsafe_allow_html=True)
            top10 = sku_m.nlargest(10, "выручка_всего")
            fig_b = px.bar(top10, x="sku", y="выручка_всего",
                           labels={"sku": "", "выручка_всего": "Выручка (₽)"},
                           hover_data=["название_товара"],
                           color_discrete_sequence=["#374151"])
            st.plotly_chart(_chart(fig_b), use_container_width=True)

        with st.container(border=True):
            st.markdown('<div class="sec-head">Продажи vs Конверсия</div>', unsafe_allow_html=True)
            fig_sc = px.scatter(
                sku_m, x="продано_штук_всего", y="конверсия",
                hover_name="sku", hover_data=["название_товара"],
                size="выручка_всего", size_max=50,
                color="выручка_всего",
                color_continuous_scale=["#E5E7EB","#111827"],
                labels={"продано_штук_всего": "Продажи (шт.)", "конверсия": "Конверсия (%)"},
            )
            st.plotly_chart(_chart(fig_sc), use_container_width=True)

    # ── Returns ───────────────────────────────────────────────────────────────
    elif page == "returns":
        sku_m = metrics["sku_metrics"].copy()
        sku_m["статус"] = sku_m["процент_возвратов"].apply(
            lambda r: "Критично (>20%)" if r > 20 else "Внимание (15–20%)" if r >= 15 else "Норма")
        cmap = {"Критично (>20%)": "#EF4444", "Внимание (15–20%)": "#F59E0B", "Норма": "#374151"}
        col1, col2 = st.columns([3, 2], gap="large")
        with col1:
            with st.container(border=True):
                st.markdown('<div class="sec-head">% возвратов по SKU</div>', unsafe_allow_html=True)
                fig_r = px.bar(sku_m.sort_values("процент_возвратов", ascending=False),
                               x="sku", y="процент_возвратов", color="статус", color_discrete_map=cmap,
                               labels={"sku": "", "процент_возвратов": "% возвратов"})
                st.plotly_chart(_chart(fig_r), use_container_width=True)
        with col2:
            with st.container(border=True):
                st.markdown('<div class="sec-head">Причины возвратов</div>', unsafe_allow_html=True)
                if not returns.empty and "причина_возврата" in returns.columns:
                    rd = returns.groupby("причина_возврата")["количество_возвратов"].sum().reset_index()
                    fig_p = px.pie(rd, names="причина_возврата", values="количество_возвратов",
                                   color_discrete_sequence=["#111827","#374151","#6B7280","#9CA3AF","#D1D5DB"],
                                   hole=0.46)
                    fig_p.update_traces(textposition="outside", textinfo="percent+label", textfont_size=10)
                    st.plotly_chart(_chart(fig_p), use_container_width=True)

    # ── Stock ─────────────────────────────────────────────────────────────────
    elif page == "stock":
        stk = stock.copy()
        stk["статус"] = stk["остаток"].apply(
            lambda q: "Критично (<50)" if q < 50 else "Внимание (50–100)" if q <= 100 else "Норма")
        cmap_s = {"Критично (<50)": "#EF4444", "Внимание (50–100)": "#F59E0B", "Норма": "#374151"}
        col1, col2 = st.columns([3, 2], gap="large")
        with col1:
            with st.container(border=True):
                st.markdown('<div class="sec-head">Остатки по SKU</div>', unsafe_allow_html=True)
                fig_s = px.bar(stk.sort_values("остаток"), x="sku", y="остаток",
                               color="статус", color_discrete_map=cmap_s,
                               labels={"sku": "", "остаток": "Остаток (шт.)"}, hover_data=["склад"])
                st.plotly_chart(_chart(fig_s), use_container_width=True)
        with col2:
            with st.container(border=True):
                st.markdown('<div class="sec-head">По складам</div>', unsafe_allow_html=True)
                wh = stk.groupby("склад")["остаток"].sum().reset_index()
                fig_w = px.pie(wh, names="склад", values="остаток",
                               color_discrete_sequence=["#111827","#374151","#6B7280","#9CA3AF"],
                               hole=0.46)
                fig_w.update_traces(textposition="outside", textinfo="percent+label", textfont_size=10)
                st.plotly_chart(_chart(fig_w), use_container_width=True)

    # ── Alerts ────────────────────────────────────────────────────────────────
    elif page == "alerts":
        crit = [a for a in alerts if a["level"] == "critical"]
        warn = [a for a in alerts if a["level"] == "warning"]

        # Summary metrics
        mc1, mc2, mc3, _ = st.columns([1, 1, 1, 3])
        for col, label, val, clr in [
            (mc1, "ALL",     len(alerts), "#111827"),
            (mc2, "FIRING",  len(crit),   "#DC2626"),
            (mc3, "WARNING", len(warn),   "#D97706"),
        ]:
            col.markdown(
                f'<div style="background:white;border-radius:10px;padding:14px 18px;border:1px solid #E8E4DC">'
                f'<div style="font-size:0.65rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">{label}</div>'
                f'<div style="font-size:1.5rem;font-weight:700;color:{clr}">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:18px"></div>', unsafe_allow_html=True)

        # Tabs: All / Firing / Warning
        tab_all, tab_crit, tab_warn = st.tabs(["All", "Firing", "Warning"])
        with tab_all:
            with st.container(border=True):
                st.markdown(_alerts_table(alerts), unsafe_allow_html=True)
        with tab_crit:
            with st.container(border=True):
                st.markdown(_alerts_table(crit), unsafe_allow_html=True)
        with tab_warn:
            with st.container(border=True):
                st.markdown(_alerts_table(warn), unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────────
    elif page == "export":
        with st.container(border=True):
            st.markdown('<div class="sec-head">Скачать отчёт</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.82rem;color:#6B7280;margin-bottom:20px">Выберите формат для скачивания готового аналитического отчёта.</div>', unsafe_allow_html=True)
            slug = metrics["period"].replace(" — ", "_").replace("-", "")
            e1, e2, _ = st.columns([1, 1, 3])
            with e1:
                st.download_button("📊 Скачать CSV", data=export_csv(metrics),
                                   file_name=f"analytics_{slug}.csv", mime="text/csv",
                                   use_container_width=True)
            with e2:
                st.download_button("📄 Скачать PDF", data=export_pdf(metrics, alerts, smry),
                                   file_name=f"analytics_{slug}.pdf", mime="application/pdf",
                                   use_container_width=True)

        with st.container(border=True):
            st.markdown('<div class="sec-head">Сводка отчёта</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="font-size:0.88rem;color:#374151;line-height:1.75">{smry}</div>',
                        unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
