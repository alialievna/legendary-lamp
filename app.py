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

/* Block container: give side padding so content doesn't touch edges */
.block-container {
    padding: 0 2rem 3rem !important;
    max-width: 100% !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div {
    background: #FFFFFF !important;
    border-right: 1px solid #E8E4DC !important;
    box-shadow: none !important;
    min-width: 220px !important; max-width: 220px !important;
}

/* Sidebar nav buttons — left-aligned */
section[data-testid="stSidebar"] .stButton { margin: 1px 0 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    width: 100% !important;
    padding: 7px 14px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    color: #4B5563 !important;
    box-shadow: none !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
}
section[data-testid="stSidebar"] .stButton > button > div {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    text-align: left !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button p {
    text-align: left !important;
    margin: 0 !important;
    width: 100% !important;
}
section[data-testid="stSidebar"] .stButton > button:hover:not(:disabled) {
    background: #F4F1EB !important; color: #111827 !important;
}
section[data-testid="stSidebar"] .stButton > button:disabled {
    color: #D1D5DB !important;
}

/* Sidebar search */
section[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    font-size: 0.8rem !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 8px !important;
    background: #F9F8F5 !important;
    color: #374151 !important;
}

/* ── Topbar row: white strip spanning full main-content width ── */
.topbar-row {
    background: white;
    border-bottom: 1px solid #E8E4DC;
    /* negative margins to cancel block-container side padding */
    margin: 0 -2rem 1.5rem -2rem;
    padding: 14px 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-crumb { font-size: 0.7rem; color: #9CA3AF; margin-bottom: 2px; }
.topbar-title { font-size: 1.15rem; font-weight: 700; color: #111827; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #E8E4DC !important;
    padding: 0 !important; gap: 0 !important;
    margin-bottom: 20px !important; box-shadow: none !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; border: none !important;
    border-bottom: 2px solid transparent !important;
    color: #6B7280 !important; font-size: 0.84rem !important;
    font-weight: 500 !important; padding: 10px 18px !important;
    border-radius: 0 !important; margin-bottom: -1px !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: #111827 !important;
    border-bottom-color: #111827 !important;
    font-weight: 700 !important;
}
.stTabs [data-baseweb="tab-border"],
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── White cards (bordered containers) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important;
    border: 1px solid #E8E4DC !important;
    border-radius: 12px !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: #111827 !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 0.84rem !important;
}

/* ── "New report" primary button in topbar ── */
.topbar-btn > button {
    background: #111827 !important; color: white !important;
    border: none !important; border-radius: 7px !important;
    font-weight: 600 !important; font-size: 0.82rem !important;
    padding: 6px 14px !important;
}
.topbar-btn > button:hover { background: #1F2937 !important; }

/* ── Back / outline button ── */
.btn-outline > button {
    background: white !important; color: #374151 !important;
    border: 1px solid #D1CCC4 !important; border-radius: 8px !important;
    font-weight: 500 !important; font-size: 0.83rem !important;
}

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
.a-cond { flex: 2; font-size: 0.79rem; color: #6B7280; padding: 0 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.a-badge { padding: 2px 8px; border-radius: 4px; font-size: 0.66rem; font-weight: 700; letter-spacing: 0.04em; white-space: nowrap; }
.a-firing { background: #FEE2E2; color: #DC2626; }
.a-warning { background: #FEF3C7; color: #D97706; }

/* ── Top-3 ── */
.top3-row { display:flex; align-items:center; padding:10px 0; border-bottom:1px solid #F4F1EB; }
.top3-row:last-child { border-bottom:none; }
.top3-rank { width:24px; height:24px; border-radius:50%; background:#F4F1EB; color:#374151; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.72rem; flex-shrink:0; }
.top3-name { flex:1; padding:0 12px; color:#374151; font-size:0.82rem; line-height:1.3; }
.top3-sku-sub { color:#9CA3AF; font-size:0.71rem; }
.top3-val { font-weight:700; color:#111827; font-size:0.82rem; }

/* ── Summary card ── */
.summary-card {
    background: white; border-radius: 12px; padding: 18px 22px;
    border: 1px solid #E8E4DC; border-left: 3px solid #111827;
    color: #1E293B; font-size: 0.88rem; line-height: 1.75; margin-bottom: 20px;
}
.summary-label { font-size: 0.65rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 8px; }

/* ── Section heading ── */
.sec-head { font-size: 0.82rem; font-weight: 700; color: #111827; margin-bottom: 12px; }

/* ── Nav active ── */
.nav-active {
    background: #F4F1EB; color: #111827 !important;
    padding: 7px 14px; border-radius: 6px;
    font-size: 0.83rem; font-weight: 700; display: block; margin: 1px 0;
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
def _fmt_rev(v: float) -> str:
    if v >= 1_000_000: return f"{v/1_000_000:.1f}M ₽"
    if v >= 1_000:     return f"{v/1_000:.0f}K ₽"
    return f"{v:,.0f} ₽"


def _chart(fig):
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
    rows = [
        ("Выручка",     _fmt_rev(metrics["total_revenue"]), min(metrics["total_revenue"]/30_000_000*100,100), "#111827"),
        ("Продано",     f"{metrics['total_sold']:,} шт.",   min(metrics["total_sold"]/15_000*100,100),        "#374151"),
        ("% возвратов", f"{rr:.1f}%",                       min(rr/30*100,100),                               rc),
        ("Конверсия",   f"{metrics['avg_conversion']:.2f}%",min(metrics["avg_conversion"]/5*100,100),         "#374151"),
    ]
    html = '<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:20px">'
    for label, value, pct, color in rows:
        html += (f'<div class="kpi-card">'
                 f'<div class="kpi-label">{label}</div>'
                 f'<div class="kpi-value">{value}</div>'
                 f'<div class="kpi-bar"><div class="kpi-bar-fill" style="width:{pct:.0f}%;background:{color}"></div></div>'
                 f'<div class="kpi-sub">{metrics["period"]}</div></div>')
    return html + '</div>'


def _alerts_table(alerts):
    if not alerts:
        return '<div style="padding:20px;color:#22C55E;font-weight:600;text-align:center">✓ Все показатели в норме</div>'
    header = (
        '<div style="display:flex;align-items:center;padding:8px 16px;'
        'border-bottom:1px solid #E8E4DC;gap:12px;">'
        '<div style="width:7px"></div>'
        '<div style="flex:1;font-size:0.66rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em">Алерт</div>'
        '<div style="flex:2;font-size:0.66rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em;padding:0 8px">Описание</div>'
        '<div style="font-size:0.66rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em">Статус</div>'
        '</div>'
    )
    rows = ""
    for a in sorted(alerts, key=lambda x: 0 if x["level"] == "critical" else 1):
        dc = "a-dot-c" if a["level"] == "critical" else "a-dot-w"
        bc = "a-firing" if a["level"] == "critical" else "a-warning"
        bt = "FIRING" if a["level"] == "critical" else "WARNING"
        rows += (f'<div class="alert-row">'
                 f'<div class="a-dot {dc}"></div>'
                 f'<div class="a-name">{a["sku"]}</div>'
                 f'<div class="a-cond">{a["message"]}</div>'
                 f'<span class="a-badge {bc}">{bt}</span></div>')
    return header + rows


def _top3_html(items, val_key, fmt):
    html = ""
    for i, item in enumerate(items, 1):
        html += (f'<div class="top3-row">'
                 f'<div class="top3-rank">{i}</div>'
                 f'<div class="top3-name">{item["name"]}<br>'
                 f'<span class="top3-sku-sub">{item["sku"]}</span></div>'
                 f'<div class="top3-val">{fmt(item[val_key])}</div></div>')
    return html


def _topbar(breadcrumb: str, title: str):
    """White full-width topbar. 'New report' button rendered separately."""
    st.markdown(
        f'<div class="topbar-row">'
        f'<div><div class="topbar-crumb">{breadcrumb}</div>'
        f'<div class="topbar-title">{title}</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _file_upload_card(col, icon: str, title: str, required: bool, hint: str,
                      key: str, ftype: str, parse_fn=None):
    """
    Renders a complete upload card inside `col`.
    Returns (file_object, is_valid).
    Element order: header HTML → file uploader widget → status HTML.
    """
    badge = (
        '<span style="background:#FEF3C7;color:#92400E;padding:2px 8px;border-radius:4px;'
        'font-size:0.65rem;font-weight:700;display:inline-block;margin-bottom:8px">Обязательный</span>'
        if required else
        '<span style="background:#D1FAE5;color:#065F46;padding:2px 8px;border-radius:4px;'
        'font-size:0.65rem;font-weight:700;display:inline-block;margin-bottom:8px">Необязательный</span>'
    )
    with col:
        with st.container(border=True):
            # 1. Header: icon, title, badge, hint
            st.markdown(
                f'<div style="padding:4px 0 2px">'
                f'<div style="font-size:1.6rem;margin-bottom:8px;line-height:1">{icon}</div>'
                f'<div style="font-weight:700;font-size:0.9rem;color:#111827;margin-bottom:4px">{title}</div>'
                f'{badge}'
                f'<div style="font-size:0.74rem;color:#9CA3AF;line-height:1.5;margin-bottom:4px">{hint}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            # 2. File uploader widget
            f = st.file_uploader("", type=[ftype], key=key, label_visibility="collapsed")
            # 3. Validation status below the uploader
            if f:
                if parse_fn:
                    try:
                        parse_fn(f)
                        f.seek(0)
                        st.markdown(
                            '<p style="color:#16A34A;font-size:0.76rem;font-weight:600;margin:4px 0 0">✓ Файл проверен</p>',
                            unsafe_allow_html=True,
                        )
                        return f, True
                    except Exception as e:
                        f.seek(0)
                        st.markdown(
                            f'<p style="color:#DC2626;font-size:0.76rem;font-weight:600;margin:4px 0 0">✗ Ошибка формата</p>',
                            unsafe_allow_html=True,
                        )
                        return f, False
                else:
                    st.markdown(
                        '<p style="color:#16A34A;font-size:0.76rem;font-weight:600;margin:4px 0 0">✓ Файл загружен</p>',
                        unsafe_allow_html=True,
                    )
                    return f, True
    return None, False


# ─── Session state ─────────────────────────────────────────────────────────────
for _k, _v in [("result", None), ("page", "overview"), ("show_upload", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="padding:18px 14px 12px;display:flex;align-items:center;gap:10px">'
        '<div style="background:#111827;border-radius:6px;width:28px;height:28px;'
        'display:flex;align-items:center;justify-content:center;font-size:12px;'
        'color:white;font-weight:800;flex-shrink:0">F</div>'
        '<span style="font-weight:800;font-size:0.9rem;color:#111827;letter-spacing:-0.01em">FLOWMETRIC</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.text_input("", placeholder="🔍  Search...", label_visibility="collapsed", key="sb_search")

    st.markdown(
        '<div style="font-size:0.65rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;'
        'letter-spacing:0.1em;padding:12px 14px 4px">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    has_data  = st.session_state["result"] is not None
    cur_page  = st.session_state["page"]
    in_upload = st.session_state["show_upload"] or not has_data

    NAV = [
        ("overview", "Overview"),
        ("products", "Товары"),
        ("returns",  "Возвраты"),
        ("stock",    "Остатки"),
        ("alerts",   "Алерты"),
        ("export",   "Экспорт"),
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
            f'<div style="padding:4px 14px 10px">'
            f'<div style="font-size:0.65rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;'
            f'letter-spacing:0.08em;margin-bottom:6px">ДАННЫЕ</div>'
            f'<div style="font-size:0.78rem;color:#374151;font-weight:600">{m["period"]}</div>'
            f'<div style="font-size:0.73rem;color:#9CA3AF">{m["sku_count"]} SKU</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div style="padding:4px 14px 10px;font-size:0.78rem;color:#9CA3AF;line-height:1.5">'
            'Загрузите данные<br>для начала работы</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<div style="margin-top:16px;padding:12px 14px;border-top:1px solid #E8E4DC;'
        'display:flex;align-items:center;gap:10px">'
        '<div style="background:#E5E7EB;border-radius:50%;width:28px;height:28px;'
        'display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:700;color:#374151">A</div>'
        '<span style="font-size:0.8rem;font-weight:500;color:#374151">Аналитик</span>'
        '</div>',
        unsafe_allow_html=True,
    )

# ─── Upload / Report builder ──────────────────────────────────────────────────
if in_upload:
    _topbar("REPORTS", "New report")

    # Back button (only if already have data)
    if has_data:
        st.markdown('<div class="btn-outline" style="display:inline-block;margin-bottom:16px">', unsafe_allow_html=True)
        if st.button("← Back to dashboard", key="back_btn"):
            st.session_state["show_upload"] = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Stepper
    st.markdown("""
    <div style="display:flex;align-items:center;margin-bottom:24px">
        <div style="display:flex;align-items:center;gap:8px">
            <div style="background:#111827;color:white;border-radius:50%;width:26px;height:26px;
                        display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:700">1</div>
            <span style="font-size:0.82rem;font-weight:700;color:#111827">Upload data</span>
        </div>
        <div style="width:60px;height:1px;background:#D1CCC4;margin:0 10px"></div>
        <div style="display:flex;align-items:center;gap:8px">
            <div style="border:2px solid #D1CCC4;color:#9CA3AF;border-radius:50%;width:26px;height:26px;
                        display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:700">2</div>
            <span style="font-size:0.82rem;font-weight:500;color:#9CA3AF">Analyze</span>
        </div>
        <div style="width:60px;height:1px;background:#D1CCC4;margin:0 10px"></div>
        <div style="display:flex;align-items:center;gap:8px">
            <div style="border:2px solid #D1CCC4;color:#9CA3AF;border-radius:50%;width:26px;height:26px;
                        display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:700">3</div>
            <span style="font-size:0.82rem;font-weight:500;color:#9CA3AF">Results</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout: file cards left, preview right ──────────────────────
    up_col, prev_col = st.columns([3, 2], gap="large")

    # ── Right preview panel (rendered first so it appears alongside cards) ──
    with prev_col:
        st.markdown("""
        <div style="background:white;border-radius:12px;border:1px solid #E8E4DC;padding:22px 24px;">
            <div style="font-size:0.67rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.09em;margin-bottom:18px">ЧТО ВЫ ПОЛУЧИТЕ</div>
            <div style="display:flex;flex-direction:column;gap:16px">
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
                    <div><div style="font-weight:600;font-size:0.84rem;color:#111827;margin-bottom:2px">Автоматические алерты</div><div style="font-size:0.76rem;color:#6B7280;line-height:1.45">7 типов проблем: критичные и предупреждения по каждому SKU</div></div>
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

    # ── Left column: file cards ──
    with up_col:
        st.markdown(
            '<p style="font-weight:700;font-size:0.88rem;color:#111827;margin-bottom:4px">Загрузите файлы с данными</p>'
            '<p style="font-size:0.8rem;color:#6B7280;margin-bottom:16px">Первые три файла обязательны. Четвёртый добавит описание кампании в сводку.</p>',
            unsafe_allow_html=True,
        )

        r1c1, r1c2 = st.columns(2, gap="medium")
        r2c1, r2c2 = st.columns(2, gap="medium")

        sales_file,   sales_ok   = _file_upload_card(r1c1, "📈", "sales.csv",         True,  "дата · SKU · выручка · сессии",         "sf",  "csv", parse_sales)
        returns_file, returns_ok = _file_upload_card(r1c2, "↩",  "returns.csv",        True,  "дата · SKU · возвраты · причина",       "rf",  "csv", parse_returns)
        stock_file,   stock_ok   = _file_upload_card(r2c1, "📦", "stock.csv",          True,  "SKU · остаток · склад",                 "stf", "csv", parse_stock)
        campaign_file, _         = _file_upload_card(r2c2, "📣", "campaign_info.txt",  False, "Описание маркетинговой акции (текст)",  "cf",  "txt", None)

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

        can_run = bool(sales_file and returns_file and stock_file and sales_ok and returns_ok and stock_ok)

        if not can_run:
            missing = [n for n, ok in [("sales.csv", bool(sales_file and sales_ok)),
                                        ("returns.csv", bool(returns_file and returns_ok)),
                                        ("stock.csv", bool(stock_file and stock_ok))] if not ok]
            if missing:
                st.markdown(
                    f'<p style="font-size:0.78rem;color:#9CA3AF;margin-bottom:8px">'
                    f'Нужно загрузить: {", ".join(missing)}</p>',
                    unsafe_allow_html=True,
                )

        run_btn = st.button(
            "Continue →" if can_run else "⬆  Загрузите файлы выше",
            disabled=not can_run,
            key="run_btn",
            type="primary",
        )

    if run_btn and can_run:
        with st.spinner("Анализирую данные…"):
            for f in (sales_file, returns_file, stock_file):
                f.seek(0)
            _sales    = parse_sales(sales_file)
            _returns  = parse_returns(returns_file)
            _stock    = parse_stock(stock_file)
            campaign  = campaign_file.read().decode("utf-8") if campaign_file else ""
            metrics   = compute_metrics(_sales, _returns, _stock)
            alerts    = generate_alerts(metrics, _sales)
            summary   = generate_summary(metrics, alerts, campaign)
            st.session_state["result"] = dict(
                metrics=metrics, alerts=alerts, summary=summary,
                sales=_sales, returns=_returns, stock=_stock,
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
    page    = st.session_state["page"]

    PAGE_META = {
        "overview": ("Workspace / Home",    "Overview"),
        "products": ("Workspace / Reports", "Товары"),
        "returns":  ("Workspace / Reports", "Возвраты"),
        "stock":    ("Workspace / Reports", "Остатки"),
        "alerts":   ("Workspace / Alerts",  "Alerts"),
        "export":   ("Workspace / Export",  "Экспорт"),
    }
    bc, title = PAGE_META.get(page, ("Workspace", page.capitalize()))

    # Topbar + New report button in same row (both in the topbar-row div area)
    tb_l, tb_r = st.columns([7, 1])
    with tb_l:
        st.markdown(
            f'<div class="topbar-row" style="padding-right:0">'
            f'<div><div class="topbar-crumb">{bc}</div>'
            f'<div class="topbar-title">{title}</div></div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with tb_r:
        st.markdown(
            '<div class="topbar-row" style="padding-left:0;justify-content:flex-end">',
            unsafe_allow_html=True,
        )
        st.markdown('<div class="topbar-btn">', unsafe_allow_html=True)
        if st.button("□ New report", key="topbar_new", use_container_width=True):
            st.session_state["show_upload"] = True
            st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)

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

        tr_l, tr_r = st.columns(2, gap="large")
        with tr_l:
            with st.container(border=True):
                hl, hr = st.columns([3, 1])
                with hl: st.markdown('<div class="sec-head">Топ SKU по выручке</div>', unsafe_allow_html=True)
                with hr: st.markdown('<div style="font-size:0.72rem;color:#9CA3AF;padding-top:2px;text-align:right">VIEW ALL →</div>', unsafe_allow_html=True)
                st.markdown(_top3_html(metrics["top3_revenue"], "revenue", lambda v: f"{v:,.0f} ₽"), unsafe_allow_html=True)
        with tr_r:
            with st.container(border=True):
                hl, hr = st.columns([3, 1])
                with hl: st.markdown('<div class="sec-head">Топ SKU по продажам</div>', unsafe_allow_html=True)
                with hr: st.markdown('<div style="font-size:0.72rem;color:#9CA3AF;padding-top:2px;text-align:right">VIEW ALL →</div>', unsafe_allow_html=True)
                st.markdown(_top3_html(metrics["top3_sold"], "sold", lambda v: f"{int(v):,} шт."), unsafe_allow_html=True)

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
        c1, c2 = st.columns([3, 2], gap="large")
        with c1:
            with st.container(border=True):
                st.markdown('<div class="sec-head">% возвратов по SKU</div>', unsafe_allow_html=True)
                fig_r = px.bar(sku_m.sort_values("процент_возвратов", ascending=False),
                               x="sku", y="процент_возвратов", color="статус", color_discrete_map=cmap,
                               labels={"sku": "", "процент_возвратов": "% возвратов"})
                st.plotly_chart(_chart(fig_r), use_container_width=True)
        with c2:
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
        c1, c2 = st.columns([3, 2], gap="large")
        with c1:
            with st.container(border=True):
                st.markdown('<div class="sec-head">Остатки по SKU</div>', unsafe_allow_html=True)
                fig_s = px.bar(stk.sort_values("остаток"), x="sku", y="остаток",
                               color="статус", color_discrete_map=cmap_s,
                               labels={"sku": "", "остаток": "Остаток (шт.)"}, hover_data=["склад"])
                st.plotly_chart(_chart(fig_s), use_container_width=True)
        with c2:
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

        mc1, mc2, mc3, _ = st.columns([1, 1, 1, 3])
        for col, label, val, clr in [
            (mc1, "ALL",     len(alerts), "#111827"),
            (mc2, "FIRING",  len(crit),   "#DC2626"),
            (mc3, "WARNING", len(warn),   "#D97706"),
        ]:
            col.markdown(
                f'<div style="background:white;border-radius:10px;padding:14px 18px;border:1px solid #E8E4DC;">'
                f'<div style="font-size:0.65rem;font-weight:700;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">{label}</div>'
                f'<div style="font-size:1.5rem;font-weight:700;color:{clr}">{val}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
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
            st.markdown('<p style="font-size:0.82rem;color:#6B7280;margin-bottom:20px">Выберите формат для скачивания готового аналитического отчёта.</p>', unsafe_allow_html=True)
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
            st.markdown(f'<div style="font-size:0.88rem;color:#374151;line-height:1.75">{smry}</div>', unsafe_allow_html=True)
