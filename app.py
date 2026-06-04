import streamlit as st
import pandas as pd
import plotly.express as px

from utils.parser import parse_sales, parse_returns, parse_stock
from utils.metrics import compute_metrics
from utils.alerts import generate_alerts
from utils.summary import generate_summary
from utils.export import export_csv, export_pdf

st.set_page_config(
    page_title="Analytics Workflow",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #F1F5F9 !important; }
.block-container { padding: 2rem 2.5rem !important; max-width: 1400px !important; }

/* ── Sidebar dark ── */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div { background: #0F172A !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span:not([data-testid]),
section[data-testid="stSidebar"] div { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] label { color: #94A3B8 !important; font-size: 0.78rem !important; font-weight: 500 !important; }
section[data-testid="stSidebar"] hr { border-color: #1E293B !important; margin: 14px 0 !important; }

/* File uploader drop zone */
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: #1E293B !important; border: 1px dashed #334155 !important; border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] *,
section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] svg { color: #64748B !important; fill: #64748B !important; }

/* Uploaded file chip */
section[data-testid="stSidebar"] [data-testid="stFileUploaderFile"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderFileData"] {
    background: #1E293B !important; border-color: #334155 !important; border-radius: 6px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploaderFileName"],
section[data-testid="stSidebar"] [data-testid="stFileUploaderFileData"] * { color: #CBD5E1 !important; }

/* Run button */
section[data-testid="stSidebar"] .stButton > button {
    background: #3B82F6 !important; color: #fff !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.88rem !important;
    padding: 10px !important; transition: background 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover:not(:disabled) { background: #2563EB !important; }
section[data-testid="stSidebar"] .stButton > button:disabled { background: #1E293B !important; color: #475569 !important; cursor: not-allowed !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: white !important; border-radius: 10px !important; padding: 4px !important;
    gap: 2px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.07) !important; margin-bottom: 16px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important; color: #64748B !important; font-weight: 500 !important;
    font-size: 0.85rem !important; padding: 7px 16px !important; background: transparent !important; border: none !important;
}
.stTabs [data-baseweb="tab"][aria-selected="true"] { background: #3B82F6 !important; color: white !important; }
.stTabs [data-baseweb="tab-border"], .stTabs [data-baseweb="tab-highlight"] { display: none !important; }

/* ── Cards (bordered containers) ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white !important; border: 1px solid #F1F5F9 !important;
    border-radius: 14px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04) !important;
}

/* ── Download buttons ── */
.stDownloadButton > button {
    background: #0F172A !important; color: white !important; border: none !important;
    border-radius: 8px !important; font-weight: 600 !important; font-size: 0.88rem !important;
}
.stDownloadButton > button:hover { background: #1E293B !important; color: white !important; }

/* ── KPI grid ── */
.kpi-grid { display: grid; grid-template-columns: repeat(6,1fr); gap: 14px; margin-bottom: 20px; }
@media(max-width:1100px){ .kpi-grid { grid-template-columns: repeat(3,1fr); } }
.kpi-card {
    background: white; border-radius: 14px; padding: 18px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid #F8FAFC; transition: box-shadow .15s, transform .15s;
}
.kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.09); transform: translateY(-1px); }
.kpi-icon { width:38px; height:38px; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:17px; margin-bottom:12px; }
.kpi-value { font-size:1.45rem; font-weight:700; color:#0F172A; line-height:1.1; margin-bottom:4px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.kpi-label { font-size:0.68rem; color:#94A3B8; font-weight:600; text-transform:uppercase; letter-spacing:0.07em; }

/* ── Summary card ── */
.summary-card {
    background: white; border-radius: 14px; padding: 18px 22px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); border-left: 4px solid #3B82F6;
    margin-bottom: 20px; color: #1E293B; font-size: 0.9rem; line-height: 1.75;
}
.summary-label { font-size:0.67rem; font-weight:700; color:#3B82F6; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px; }

/* ── Alert items ── */
.alert-item {
    display:flex; align-items:flex-start; gap:12px; background:white; border-radius:10px;
    padding:12px 16px; box-shadow:0 1px 2px rgba(0,0,0,0.04); border:1px solid #F1F5F9; margin-bottom:8px;
}
.badge { padding:3px 10px; border-radius:20px; font-size:0.68rem; font-weight:700; white-space:nowrap; flex-shrink:0; margin-top:2px; }
.badge-crit { background:#FEF2F2; color:#DC2626; border:1px solid #FECACA; }
.badge-warn { background:#FFFBEB; color:#D97706; border:1px solid #FDE68A; }
.alert-sku { font-weight:700; color:#0F172A; font-size:0.84rem; }
.alert-msg { color:#64748B; font-size:0.81rem; margin-top:1px; }

/* ── Top-3 list ── */
.top3-row { display:flex; align-items:center; padding:10px 0; border-bottom:1px solid #F8FAFC; }
.top3-row:last-child { border-bottom:none; }
.top3-rank { width:26px; height:26px; border-radius:50%; background:#EFF6FF; color:#3B82F6; display:flex; align-items:center; justify-content:center; font-weight:700; font-size:0.76rem; flex-shrink:0; }
.top3-name { flex:1; padding:0 12px; color:#374151; font-size:0.83rem; line-height:1.3; }
.top3-sku-sub { color:#94A3B8; font-size:0.73rem; }
.top3-val { font-weight:700; color:#0F172A; font-size:0.83rem; }

/* ── Section heading ── */
.sec-head { font-size:0.88rem; font-weight:700; color:#0F172A; margin-bottom:14px; }

/* ── Page header ── */
.page-title { font-size:1.4rem; font-weight:800; color:#0F172A; margin:0 0 3px; }
.page-sub { font-size:0.85rem; color:#64748B; margin-bottom:20px; }

/* ── Footer ── */
.footer { text-align:center; color:#94A3B8; font-size:0.75rem; padding:20px 0 6px; }

/* ── Misc ── */
hr { border:none !important; border-top:1px solid #E2E8F0 !important; margin:16px 0 !important; }
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#F1F5F9; }
::-webkit-scrollbar-thumb { background:#CBD5E1; border-radius:3px; }
[data-testid="stPlotlyChart"] { border-radius:10px !important; }
[data-testid="stDataFrame"] { border-radius:10px !important; overflow:hidden !important; }
</style>
""", unsafe_allow_html=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
PALETTE = ["#3B82F6","#8B5CF6","#22C55E","#F59E0B","#EF4444","#06B6D4","#EC4899","#14B8A6"]


def _fmt_rev(v: float) -> str:
    if v >= 1_000_000:
        return f"{v/1_000_000:.1f}M ₽"
    if v >= 1_000:
        return f"{v/1_000:.0f}K ₽"
    return f"{v:,.0f} ₽"


def _chart(fig):
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#374151", size=11),
        xaxis=dict(gridcolor="#F1F5F9", zeroline=False, showline=False, tickfont=dict(size=10, color="#94A3B8")),
        yaxis=dict(gridcolor="#F1F5F9", zeroline=False, showline=False, tickfont=dict(size=10, color="#94A3B8")),
        margin=dict(l=10, r=10, t=40, b=10),
        title_font=dict(size=13, color="#0F172A", family="Inter"),
        hoverlabel=dict(bgcolor="white", bordercolor="#E2E8F0", font=dict(size=11, color="#0F172A")),
        legend=dict(bgcolor="rgba(255,255,255,0.95)", bordercolor="#E2E8F0", borderwidth=1, font=dict(size=10)),
    )
    return fig


def _kpi_html(metrics: dict, n_days: int) -> str:
    rr = metrics["return_rate"]
    rc, rbg = (("#EF4444","#FEF2F2") if rr > 20 else ("#F59E0B","#FFFBEB") if rr > 15 else ("#22C55E","#F0FDF4"))
    cards = [
        ("💰","#3B82F6","#EFF6FF","Выручка",         _fmt_rev(metrics["total_revenue"])),
        ("📦","#22C55E","#F0FDF4","Продано",          f"{metrics['total_sold']:,} шт."),
        ("↩", rc,       rbg,     "% возвратов",      f"{rr:.1f}%"),
        ("🎯","#8B5CF6","#F5F3FF","Конверсия",        f"{metrics['avg_conversion']:.2f}%"),
        ("🏷","#06B6D4","#ECFEFF","Позиций SKU",      str(metrics["sku_count"])),
        ("📅","#EC4899","#FDF2F8","Дней данных",      str(n_days)),
    ]
    html = '<div class="kpi-grid">'
    for icon, color, bg, label, value in cards:
        html += (f'<div class="kpi-card">'
                 f'<div class="kpi-icon" style="background:{bg};color:{color}">{icon}</div>'
                 f'<div class="kpi-value">{value}</div>'
                 f'<div class="kpi-label">{label}</div>'
                 f'</div>')
    return html + '</div>'


def _summary_html(text: str) -> str:
    return (f'<div class="summary-card">'
            f'<div class="summary-label">📋 Автоматическая сводка</div>'
            f'{text}</div>')


def _alerts_html(alerts: list) -> str:
    if not alerts:
        return '<div style="color:#22C55E;font-weight:600;padding:12px 0">✓ Все показатели в норме</div>'
    sorted_a = sorted(alerts, key=lambda a: 0 if a["level"] == "critical" else 1)
    html = ""
    for a in sorted_a:
        bc = "badge-crit" if a["level"] == "critical" else "badge-warn"
        bt = "КРИТИЧНО" if a["level"] == "critical" else "ВНИМАНИЕ"
        html += (f'<div class="alert-item">'
                 f'<span class="badge {bc}">{bt}</span>'
                 f'<div><div class="alert-sku">{a["sku"]}</div>'
                 f'<div class="alert-msg">{a["message"]}</div></div></div>')
    return html


def _top3_html(items: list, val_key: str, fmt) -> str:
    html = ""
    for i, item in enumerate(items, 1):
        html += (f'<div class="top3-row">'
                 f'<div class="top3-rank">{i}</div>'
                 f'<div class="top3-name">{item["name"]}<br>'
                 f'<span class="top3-sku-sub">{item["sku"]}</span></div>'
                 f'<div class="top3-val">{fmt(item[val_key])}</div></div>')
    return html


# ─── Session state ─────────────────────────────────────────────────────────────
if "result" not in st.session_state:
    st.session_state["result"] = None

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="display:flex;align-items:center;gap:10px;padding:8px 4px 20px">'
        '<div style="background:#3B82F6;border-radius:10px;width:34px;height:34px;'
        'display:flex;align-items:center;justify-content:center;font-size:17px;flex-shrink:0">📊</div>'
        '<div><div style="color:#F8FAFC;font-weight:700;font-size:1rem;line-height:1.1">Analytics</div>'
        '<div style="color:#475569;font-size:0.71rem;margin-top:1px">Workflow</div></div></div>'
        '<div style="color:#475569;font-size:0.66rem;font-weight:700;text-transform:uppercase;'
        'letter-spacing:0.1em;border-top:1px solid #1E293B;padding-top:14px;margin-bottom:10px">Загрузка данных</div>',
        unsafe_allow_html=True,
    )

    sales_file   = st.file_uploader("sales.csv",         type="csv", key="sf")
    returns_file = st.file_uploader("returns.csv",        type="csv", key="rf")
    stock_file   = st.file_uploader("stock.csv",          type="csv", key="stf")
    campaign_file= st.file_uploader("campaign_info.txt",  type="txt", key="cf")

    sales_ok = returns_ok = stock_ok = False
    status_parts = []

    for f, label, parse_fn, flag_attr in [
        (sales_file,   "sales.csv",   parse_sales,   "sales_ok"),
        (returns_file, "returns.csv", parse_returns, "returns_ok"),
        (stock_file,   "stock.csv",   parse_stock,   "stock_ok"),
    ]:
        if f:
            try:
                parse_fn(f)
                status_parts.append(f'<div style="color:#4ADE80;font-size:0.77rem;margin:2px 0">✓ {label}</div>')
                if flag_attr == "sales_ok":   sales_ok   = True
                if flag_attr == "returns_ok": returns_ok = True
                if flag_attr == "stock_ok":   stock_ok   = True
            except Exception as e:
                status_parts.append(f'<div style="color:#F87171;font-size:0.77rem;margin:2px 0">✗ {label}: {e}</div>')
            finally:
                f.seek(0)

    if campaign_file:
        status_parts.append('<div style="color:#4ADE80;font-size:0.77rem;margin:2px 0">✓ campaign_info.txt</div>')

    if status_parts:
        st.markdown(f'<div style="margin:8px 0 14px">{"".join(status_parts)}</div>', unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid #1E293B;margin:4px 0 12px"></div>', unsafe_allow_html=True)

    can_run = bool(sales_file and returns_file and stock_file and sales_ok and returns_ok and stock_ok)
    run_btn = st.button("▶  Запустить анализ", disabled=not can_run, use_container_width=True)

# ─── Run analysis ─────────────────────────────────────────────────────────────
if run_btn and can_run:
    with st.spinner("Обрабатываю данные…"):
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

# ─── Results ──────────────────────────────────────────────────────────────────
if st.session_state["result"] is not None:
    res     = st.session_state["result"]
    metrics = res["metrics"]
    alerts  = res["alerts"]
    smry    = res["summary"]
    sales:   pd.DataFrame = res["sales"]
    returns: pd.DataFrame = res["returns"]
    stock:   pd.DataFrame = res["stock"]
    n_days  = sales["дата"].nunique()

    # Header
    st.markdown(
        f'<div class="page-title">Аналитика маркетплейса</div>'
        f'<div class="page-sub">Период: {metrics["period"]} · {metrics["sku_count"]} SKU · {n_days} дней</div>',
        unsafe_allow_html=True,
    )

    # KPI cards
    st.markdown(_kpi_html(metrics, n_days), unsafe_allow_html=True)

    # Summary
    st.markdown(_summary_html(smry), unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Обзор", "🛍 Товары", "↩ Возвраты", "📦 Остатки", "🚨 Алерты"]
    )

    # ── Tab 1 ────────────────────────────────────────────────────────────────
    with tab1:
        with st.container(border=True):
            st.markdown('<div class="sec-head">Динамика выручки</div>', unsafe_allow_html=True)
            daily = sales.groupby("дата")["выручка"].sum().reset_index()
            fig = px.line(daily, x="дата", y="выручка",
                          labels={"дата": "", "выручка": "Выручка (₽)"})
            fig.update_traces(line_color="#3B82F6", line_width=2.5,
                              fill="tozeroy", fillcolor="rgba(59,130,246,0.07)")
            st.plotly_chart(_chart(fig), use_container_width=True)

        cl, cr = st.columns(2)
        with cl:
            with st.container(border=True):
                st.markdown('<div class="sec-head">Топ-3 по выручке</div>', unsafe_allow_html=True)
                st.markdown(_top3_html(metrics["top3_revenue"], "revenue", lambda v: f"{v:,.0f} ₽"),
                            unsafe_allow_html=True)
        with cr:
            with st.container(border=True):
                st.markdown('<div class="sec-head">Топ-3 по продажам</div>', unsafe_allow_html=True)
                st.markdown(_top3_html(metrics["top3_sold"], "sold", lambda v: f"{int(v):,} шт."),
                            unsafe_allow_html=True)

    # ── Tab 2 ────────────────────────────────────────────────────────────────
    with tab2:
        sku_m = metrics["sku_metrics"]
        with st.container(border=True):
            st.markdown('<div class="sec-head">Топ-10 SKU по выручке</div>', unsafe_allow_html=True)
            top10 = sku_m.nlargest(10, "выручка_всего")
            fig_b = px.bar(top10, x="sku", y="выручка_всего",
                           labels={"sku": "", "выручка_всего": "Выручка (₽)"},
                           hover_data=["название_товара"],
                           color_discrete_sequence=[PALETTE[0]])
            st.plotly_chart(_chart(fig_b), use_container_width=True)

        with st.container(border=True):
            st.markdown('<div class="sec-head">Продажи vs Конверсия</div>', unsafe_allow_html=True)
            fig_sc = px.scatter(
                sku_m, x="продано_штук_всего", y="конверсия",
                hover_name="sku", hover_data=["название_товара"],
                size="выручка_всего", size_max=55,
                color="выручка_всего", color_continuous_scale=["#BFDBFE","#1D4ED8"],
                labels={"продано_штук_всего": "Продажи (шт.)", "конверсия": "Конверсия (%)"},
            )
            fig_sc.update_layout(coloraxis_showscale=False)
            st.plotly_chart(_chart(fig_sc), use_container_width=True)

    # ── Tab 3 ────────────────────────────────────────────────────────────────
    with tab3:
        sku_m = metrics["sku_metrics"].copy()
        sku_m["статус"] = sku_m["процент_возвратов"].apply(
            lambda r: "Критично (>20%)" if r > 20 else "Внимание (15–20%)" if r >= 15 else "Норма")
        cmap = {"Критично (>20%)": "#EF4444", "Внимание (15–20%)": "#F59E0B", "Норма": "#22C55E"}

        col1, col2 = st.columns([3, 2])
        with col1:
            with st.container(border=True):
                st.markdown('<div class="sec-head">% возвратов по SKU</div>', unsafe_allow_html=True)
                fig_r = px.bar(
                    sku_m.sort_values("процент_возвратов", ascending=False),
                    x="sku", y="процент_возвратов", color="статус",
                    color_discrete_map=cmap,
                    labels={"sku": "", "процент_возвратов": "% возвратов"},
                )
                st.plotly_chart(_chart(fig_r), use_container_width=True)
        with col2:
            with st.container(border=True):
                st.markdown('<div class="sec-head">Причины возвратов</div>', unsafe_allow_html=True)
                if not returns.empty and "причина_возврата" in returns.columns:
                    rd = returns.groupby("причина_возврата")["количество_возвратов"].sum().reset_index()
                    fig_p = px.pie(rd, names="причина_возврата", values="количество_возвратов",
                                   color_discrete_sequence=PALETTE, hole=0.46)
                    fig_p.update_traces(textposition="outside", textinfo="percent+label",
                                        textfont_size=10)
                    st.plotly_chart(_chart(fig_p), use_container_width=True)

    # ── Tab 4 ────────────────────────────────────────────────────────────────
    with tab4:
        stk = stock.copy()
        stk["статус"] = stk["остаток"].apply(
            lambda q: "Критично (<50)" if q < 50 else "Внимание (50–100)" if q <= 100 else "Норма")
        cmap_s = {"Критично (<50)": "#EF4444", "Внимание (50–100)": "#F59E0B", "Норма": "#22C55E"}

        col1, col2 = st.columns([3, 2])
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
                               color_discrete_sequence=PALETTE, hole=0.46)
                fig_w.update_traces(textposition="outside", textinfo="percent+label", textfont_size=10)
                st.plotly_chart(_chart(fig_w), use_container_width=True)

    # ── Tab 5 ────────────────────────────────────────────────────────────────
    with tab5:
        crit = [a for a in alerts if a["level"] == "critical"]
        warn = [a for a in alerts if a["level"] == "warning"]

        a1, a2, a3 = st.columns(3)
        a1.metric("Всего алертов",     len(alerts))
        a2.metric("🔴 Критических",    len(crit))
        a3.metric("🟡 Предупреждений", len(warn))

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        if not alerts:
            with st.container(border=True):
                st.success("✅ Все показатели в норме. Критических проблем не обнаружено.")
        else:
            st.markdown(_alerts_html(alerts), unsafe_allow_html=True)

            st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown('<div class="sec-head">Сводная таблица</div>', unsafe_allow_html=True)
                df_a = pd.DataFrame(alerts)
                df_a["Уровень"] = df_a["level"].map({"critical": "🔴 Критично", "warning": "🟡 Внимание"})
                st.dataframe(
                    df_a[["Уровень", "sku", "message"]].rename(columns={"sku": "SKU", "message": "Описание"}),
                    use_container_width=True, hide_index=True,
                )

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="sec-head">📥 Экспорт отчёта</div>', unsafe_allow_html=True)
        slug = metrics["period"].replace(" — ", "_").replace("-", "")
        ec1, ec2, _ = st.columns([1, 1, 3])
        with ec1:
            st.download_button("📊 CSV", data=export_csv(metrics),
                               file_name=f"analytics_{slug}.csv", mime="text/csv",
                               use_container_width=True)
        with ec2:
            st.download_button("📄 PDF", data=export_pdf(metrics, alerts, smry),
                               file_name=f"analytics_{slug}.pdf", mime="application/pdf",
                               use_container_width=True)

    st.markdown('<div class="footer">Сформировано автоматически · Analytics Workflow</div>',
                unsafe_allow_html=True)

# ─── Welcome screen ───────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div style="max-width:660px;margin:60px auto;text-align:center">
        <div style="background:#3B82F6;border-radius:18px;width:68px;height:68px;
                    display:flex;align-items:center;justify-content:center;
                    font-size:30px;margin:0 auto 22px">📊</div>
        <div style="font-size:1.9rem;font-weight:800;color:#0F172A;margin-bottom:8px">Analytics Workflow</div>
        <div style="color:#64748B;font-size:0.95rem;line-height:1.65;margin-bottom:32px">
            Аналитический сервис для данных маркетплейса.<br>
            Загрузите файлы в панели слева и нажмите <strong>Запустить анализ</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    features = [
        ("📈","#EFF6FF","#3B82F6","KPI и динамика",   "Выручка, продажи, конверсия по дням"),
        ("🚨","#FEF2F2","#EF4444","Алерты",            "Автоматическое выявление проблем"),
        ("📋","#F5F3FF","#8B5CF6","Сводка",            "Связный текст без AI"),
        ("📥","#F0FDF4","#22C55E","Экспорт",           "CSV и PDF для скачивания"),
    ]
    for col, (icon, bg, color, title, desc) in zip(cols, features):
        with col:
            with st.container(border=True):
                st.markdown(
                    f'<div style="padding:4px">'
                    f'<div style="background:{bg};color:{color};border-radius:10px;width:38px;height:38px;'
                    f'display:flex;align-items:center;justify-content:center;font-size:17px;margin-bottom:12px">{icon}</div>'
                    f'<div style="font-weight:700;color:#0F172A;font-size:0.88rem;margin-bottom:4px">{title}</div>'
                    f'<div style="color:#64748B;font-size:0.79rem;line-height:1.45">{desc}</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown('<div class="footer">Сформировано автоматически · Analytics Workflow</div>',
                unsafe_allow_html=True)
