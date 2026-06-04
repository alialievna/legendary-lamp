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

if "result" not in st.session_state:
    st.session_state["result"] = None

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("📊 Analytics Workflow")
    st.markdown("---")
    st.subheader("Загрузка файлов")

    sales_file = st.file_uploader("📁 sales.csv", type="csv", key="sf")
    returns_file = st.file_uploader("📁 returns.csv", type="csv", key="rf")
    stock_file = st.file_uploader("📁 stock.csv", type="csv", key="stf")
    campaign_file = st.file_uploader("📁 campaign_info.txt", type="txt", key="cf")

    sales_ok = returns_ok = stock_ok = False

    if sales_file:
        try:
            parse_sales(sales_file)
            st.success("✅ sales.csv")
            sales_ok = True
        except Exception as e:
            st.error(f"❌ sales.csv: {e}")
        finally:
            sales_file.seek(0)

    if returns_file:
        try:
            parse_returns(returns_file)
            st.success("✅ returns.csv")
            returns_ok = True
        except Exception as e:
            st.error(f"❌ returns.csv: {e}")
        finally:
            returns_file.seek(0)

    if stock_file:
        try:
            parse_stock(stock_file)
            st.success("✅ stock.csv")
            stock_ok = True
        except Exception as e:
            st.error(f"❌ stock.csv: {e}")
        finally:
            stock_file.seek(0)

    if campaign_file:
        st.success("✅ campaign_info.txt")

    st.markdown("---")
    can_run = bool(
        sales_file and returns_file and stock_file and sales_ok and returns_ok and stock_ok
    )
    run_btn = st.button("🚀 Запустить анализ", disabled=not can_run, use_container_width=True)

# ─── Run analysis ─────────────────────────────────────────────────────────────
if run_btn and can_run:
    with st.spinner("Анализирую данные..."):
        for f in (sales_file, returns_file, stock_file):
            f.seek(0)

        sales = parse_sales(sales_file)
        returns = parse_returns(returns_file)
        stock = parse_stock(stock_file)
        campaign = campaign_file.read().decode("utf-8") if campaign_file else ""

        metrics = compute_metrics(sales, returns, stock)
        alerts = generate_alerts(metrics, sales)
        summary = generate_summary(metrics, alerts, campaign)

        st.session_state["result"] = {
            "metrics": metrics,
            "alerts": alerts,
            "summary": summary,
            "sales": sales,
            "returns": returns,
            "stock": stock,
        }

# ─── Results ──────────────────────────────────────────────────────────────────
if st.session_state["result"] is not None:
    res = st.session_state["result"]
    metrics: dict = res["metrics"]
    alerts: list = res["alerts"]
    summary: str = res["summary"]
    sales: pd.DataFrame = res["sales"]
    returns: pd.DataFrame = res["returns"]
    stock: pd.DataFrame = res["stock"]

    # Summary block
    st.markdown("### 📋 Автоматическая сводка")
    st.info(summary)
    st.markdown("---")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 Обзор", "🛍️ Товары", "↩️ Возвраты", "📦 Остатки", "🚨 Алерты"]
    )

    # ── Tab 1: Overview ───────────────────────────────────────────────────────
    with tab1:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Выручка", f"{metrics['total_revenue']:,.0f} ₽")
        c2.metric("Продано", f"{metrics['total_sold']:,} шт.")
        c3.metric("% возвратов", f"{metrics['return_rate']:.1f}%")
        c4.metric("Ср. конверсия", f"{metrics['avg_conversion']:.2f}%")
        c5.metric("SKU", str(metrics["sku_count"]))
        c6.metric("Дней данных", str(sales["дата"].nunique()))

        daily = sales.groupby("дата")["выручка"].sum().reset_index()
        fig_line = px.line(
            daily,
            x="дата",
            y="выручка",
            title="Динамика выручки по дням",
            labels={"дата": "Дата", "выручка": "Выручка (₽)"},
        )
        fig_line.update_traces(line_color="#1a1a1a", line_width=2)
        fig_line.update_layout(hovermode="x unified", plot_bgcolor="white")
        st.plotly_chart(fig_line, use_container_width=True)

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("**Топ-3 по выручке**")
            for i, t in enumerate(metrics["top3_revenue"], 1):
                st.write(f"{i}. {t['sku']} — {t['revenue']:,.0f} ₽")
        with col_r:
            st.markdown("**Топ-3 по продажам**")
            for i, t in enumerate(metrics["top3_sold"], 1):
                st.write(f"{i}. {t['sku']} — {t['sold']:,} шт.")

    # ── Tab 2: Products ───────────────────────────────────────────────────────
    with tab2:
        sku_m = metrics["sku_metrics"]

        top10 = sku_m.nlargest(10, "выручка_всего")
        fig_bar = px.bar(
            top10,
            x="sku",
            y="выручка_всего",
            title="Топ-10 SKU по выручке",
            labels={"sku": "SKU", "выручка_всего": "Выручка (₽)"},
            color="выручка_всего",
            color_continuous_scale="Blues",
            hover_data=["название_товара"],
        )
        fig_bar.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
        st.plotly_chart(fig_bar, use_container_width=True)

        fig_sc = px.scatter(
            sku_m,
            x="продано_штук_всего",
            y="конверсия",
            hover_name="sku",
            hover_data=["название_товара", "выручка_всего"],
            size="выручка_всего",
            size_max=50,
            title="Продажи vs Конверсия (размер пузыря = выручка)",
            labels={
                "продано_штук_всего": "Продажи (шт.)",
                "конверсия": "Конверсия (%)",
            },
        )
        fig_sc.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig_sc, use_container_width=True)

    # ── Tab 3: Returns ────────────────────────────────────────────────────────
    with tab3:
        sku_m = metrics["sku_metrics"].copy()

        def _ret_status(r: float) -> str:
            if r > 20:
                return "Критично (>20%)"
            elif r >= 15:
                return "Внимание (15–20%)"
            return "Норма (<15%)"

        sku_m["статус"] = sku_m["процент_возвратов"].apply(_ret_status)
        cmap_ret = {
            "Критично (>20%)": "#e74c3c",
            "Внимание (15–20%)": "#f39c12",
            "Норма (<15%)": "#2ecc71",
        }
        fig_ret = px.bar(
            sku_m.sort_values("процент_возвратов", ascending=False),
            x="sku",
            y="процент_возвратов",
            color="статус",
            color_discrete_map=cmap_ret,
            title="% возвратов по SKU",
            labels={"sku": "SKU", "процент_возвратов": "% возвратов"},
            hover_data=["название_товара"],
        )
        fig_ret.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig_ret, use_container_width=True)

        if not returns.empty and "причина_возврата" in returns.columns:
            reason_df = (
                returns.groupby("причина_возврата")["количество_возвратов"]
                .sum()
                .reset_index()
            )
            fig_pie = px.pie(
                reason_df,
                names="причина_возврата",
                values="количество_возвратов",
                title="Причины возвратов",
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    # ── Tab 4: Stock ──────────────────────────────────────────────────────────
    with tab4:
        stk = stock.copy()

        def _stk_status(q: int) -> str:
            if q < 50:
                return "Критично (<50)"
            elif q <= 100:
                return "Внимание (50–100)"
            return "Норма (>100)"

        stk["статус"] = stk["остаток"].apply(_stk_status)
        cmap_stk = {
            "Критично (<50)": "#e74c3c",
            "Внимание (50–100)": "#f39c12",
            "Норма (>100)": "#2ecc71",
        }
        fig_stk = px.bar(
            stk.sort_values("остаток"),
            x="sku",
            y="остаток",
            color="статус",
            color_discrete_map=cmap_stk,
            title="Остатки по SKU",
            labels={"sku": "SKU", "остаток": "Остаток (шт.)"},
            hover_data=["склад"],
        )
        fig_stk.update_layout(plot_bgcolor="white")
        st.plotly_chart(fig_stk, use_container_width=True)

        wh = stk.groupby("склад")["остаток"].sum().reset_index()
        fig_wh = px.bar(
            wh,
            x="склад",
            y="остаток",
            title="Остатки по складам",
            labels={"склад": "Склад", "остаток": "Остаток (шт.)"},
            color="остаток",
            color_continuous_scale="Greens",
        )
        fig_wh.update_layout(coloraxis_showscale=False, plot_bgcolor="white")
        st.plotly_chart(fig_wh, use_container_width=True)

    # ── Tab 5: Alerts ─────────────────────────────────────────────────────────
    with tab5:
        crit = [a for a in alerts if a["level"] == "critical"]
        warn = [a for a in alerts if a["level"] == "warning"]

        if not alerts:
            st.success("✅ Все показатели в норме. Критических проблем не обнаружено.")
        else:
            if crit:
                st.markdown("### 🔴 Критические проблемы")
                for a in crit:
                    st.error(f"**{a['sku']}** — {a['message']}")

            if warn:
                st.markdown("### 🟡 Предупреждения")
                for a in warn:
                    st.warning(f"**{a['sku']}** — {a['message']}")

            st.markdown("### Сводная таблица проблемных позиций")
            df_a = pd.DataFrame(alerts)
            df_a["Уровень"] = df_a["level"].map(
                {"critical": "🔴 Критично", "warning": "🟡 Внимание"}
            )
            st.dataframe(
                df_a[["Уровень", "sku", "message"]].rename(
                    columns={"sku": "SKU", "message": "Описание"}
                ),
                use_container_width=True,
                hide_index=True,
            )

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📥 Экспорт отчёта")
    period_slug = metrics["period"].replace(" — ", "_").replace("-", "")
    ec1, ec2 = st.columns(2)

    with ec1:
        csv_bytes = export_csv(metrics)
        st.download_button(
            "📊 Скачать CSV",
            data=csv_bytes,
            file_name=f"analytics_{period_slug}.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with ec2:
        pdf_bytes = export_pdf(metrics, alerts, summary)
        st.download_button(
            "📄 Скачать PDF",
            data=pdf_bytes,
            file_name=f"analytics_{period_slug}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:gray;font-size:0.85em;'>"
        "Сформировано автоматически · Analytics Workflow</p>",
        unsafe_allow_html=True,
    )

# ─── Welcome screen ───────────────────────────────────────────────────────────
else:
    st.title("📊 Analytics Workflow")
    st.markdown("""
### Добро пожаловать!

Автоматический аналитический сервис для данных маркетплейса.
Загрузите файлы в боковой панели слева и нажмите **Запустить анализ**.

---

**Необходимые файлы:**

| Файл | Обязательные колонки |
|------|----------------------|
| `sales.csv` | дата, sku, название_товара, категория, продано_штук, выручка, сессии |
| `returns.csv` | дата, sku, количество_возвратов, причина_возврата |
| `stock.csv` | sku, остаток, склад |

**Опциональный файл:** `campaign_info.txt` — произвольный текст с описанием акции.

---

**Что вы получите:**
- 📈 Динамика выручки и 6 KPI-карточек
- 🛍️ Топ-10 SKU + scatter продажи vs конверсия
- ↩️ Анализ возвратов и причин
- 📦 Контроль остатков по SKU и складам
- 🚨 Автоматические алерты о проблемных позициях
- 📋 Текстовая сводка периода (без AI)
- 📥 Отчёты CSV и PDF для скачивания
""")
    st.markdown("---")
    st.markdown(
        "<p style='text-align:center;color:gray;font-size:0.85em;'>"
        "Сформировано автоматически · Analytics Workflow</p>",
        unsafe_allow_html=True,
    )
