import pandas as pd
from typing import List, Dict


def generate_alerts(metrics: dict, sales: pd.DataFrame) -> List[Dict]:
    alerts: List[Dict] = []
    sku_m = metrics["sku_metrics"]

    dates = sorted(sales["дата"].unique())
    last_7 = set(dates[-7:]) if len(dates) >= 7 else set(dates)
    first_5 = dates[:5] if len(dates) >= 5 else dates
    last_5 = dates[-5:] if len(dates) >= 5 else dates
    enough_for_trend = len(dates) >= 10

    for _, row in sku_m.iterrows():
        sku: str = row["sku"]
        name: str = row["название_товара"]
        ret_rate: float = row["процент_возвратов"]
        stock: int = row["остаток"]
        conv: float = row["конверсия"]

        # ── Return rate ──────────────────────────────────────────────────────
        if ret_rate > 20:
            alerts.append({
                "level": "critical",
                "sku": sku,
                "message": f"{name}: % возвратов критически высок ({ret_rate:.1f}%)",
            })
        elif ret_rate >= 15:
            alerts.append({
                "level": "warning",
                "sku": sku,
                "message": f"{name}: % возвратов повышен ({ret_rate:.1f}%)",
            })

        # ── Stock ────────────────────────────────────────────────────────────
        if stock < 50:
            alerts.append({
                "level": "critical",
                "sku": sku,
                "message": f"{name}: критически низкий остаток ({stock} шт.)",
            })
        elif stock <= 100:
            alerts.append({
                "level": "warning",
                "sku": sku,
                "message": f"{name}: остаток на складе низкий ({stock} шт.)",
            })

        # ── Sales last 7 days ─────────────────────────────────────────────────
        sku_sales = sales[sales["sku"] == sku]
        last7_sold = int(sku_sales[sku_sales["дата"].isin(last_7)]["продано_штук"].sum())

        if last7_sold == 0:
            alerts.append({
                "level": "critical",
                "sku": sku,
                "message": f"{name}: нет продаж за последние 7 дней",
            })
        elif enough_for_trend:
            # Sales drop > 40 % (last 5 days vs first 5 days)
            first5_sold = int(sku_sales[sku_sales["дата"].isin(first_5)]["продано_штук"].sum())
            last5_sold = int(sku_sales[sku_sales["дата"].isin(last_5)]["продано_штук"].sum())
            if first5_sold > 0:
                drop_pct = (first5_sold - last5_sold) / first5_sold * 100
                if drop_pct > 40:
                    alerts.append({
                        "level": "warning",
                        "sku": sku,
                        "message": (
                            f"{name}: продажи упали на {drop_pct:.1f}% "
                            f"(последние 5 дней vs первые 5 дней)"
                        ),
                    })

        # ── Conversion ───────────────────────────────────────────────────────
        if conv < 2:
            alerts.append({
                "level": "warning",
                "sku": sku,
                "message": f"{name}: низкая конверсия ({conv:.2f}%)",
            })

    return alerts
