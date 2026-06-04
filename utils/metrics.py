import streamlit as st
import pandas as pd


@st.cache_data
def compute_metrics(
    sales: pd.DataFrame,
    returns: pd.DataFrame,
    stock: pd.DataFrame,
) -> dict:
    min_date = sales["дата"].min().strftime("%Y-%m-%d")
    max_date = sales["дата"].max().strftime("%Y-%m-%d")
    period = f"{min_date} — {max_date}"

    # Per-SKU aggregation from sales
    sales_agg = (
        sales.groupby(["sku", "название_товара"])
        .agg(
            продано_штук_всего=("продано_штук", "sum"),
            выручка_всего=("выручка", "sum"),
            сессии_всего=("сессии", "sum"),
        )
        .reset_index()
    )

    returns_agg = (
        returns.groupby("sku")
        .agg(возвратов_всего=("количество_возвратов", "sum"))
        .reset_index()
    )

    sku_m = sales_agg.merge(returns_agg, on="sku", how="left")
    sku_m["возвратов_всего"] = sku_m["возвратов_всего"].fillna(0).astype(int)

    # Derived KPIs
    sold = sku_m["продано_штук_всего"].replace(0, float("nan"))
    sessions = sku_m["сессии_всего"].replace(0, float("nan"))

    sku_m["процент_возвратов"] = (sku_m["возвратов_всего"] / sold * 100).fillna(0)
    sku_m["конверсия"] = (sku_m["продано_штук_всего"] / sessions * 100).fillna(0)
    sku_m["средняя_цена"] = (sku_m["выручка_всего"] / sold).fillna(0)

    # Merge stock
    stock_agg = stock.groupby("sku")["остаток"].sum().reset_index()
    sku_m = sku_m.merge(stock_agg, on="sku", how="left")
    sku_m["остаток"] = sku_m["остаток"].fillna(0).astype(int)

    # Period aggregates
    total_revenue = float(sales["выручка"].sum())
    total_sold = int(sales["продано_штук"].sum())
    total_returns = int(returns["количество_возвратов"].sum())
    return_rate = total_returns / total_sold * 100 if total_sold > 0 else 0.0
    avg_conversion = float(sku_m["конверсия"].mean()) if len(sku_m) > 0 else 0.0

    top3_revenue = (
        sku_m.nlargest(3, "выручка_всего")[["sku", "название_товара", "выручка_всего"]]
        .rename(columns={"название_товара": "name", "выручка_всего": "revenue"})
        .to_dict("records")
    )
    top3_sold = (
        sku_m.nlargest(3, "продано_штук_всего")[["sku", "название_товара", "продано_штук_всего"]]
        .rename(columns={"название_товара": "name", "продано_штук_всего": "sold"})
        .to_dict("records")
    )

    return {
        "period": period,
        "total_revenue": total_revenue,
        "total_sold": total_sold,
        "total_returns": total_returns,
        "return_rate": return_rate,
        "avg_conversion": avg_conversion,
        "sku_count": len(sku_m),
        "top3_revenue": top3_revenue,
        "top3_sold": top3_sold,
        "sku_metrics": sku_m,
    }
