from typing import List, Dict


def generate_summary(metrics: dict, alerts: List[Dict], campaign: str = "") -> str:
    period = metrics["period"]
    total_rev = metrics["total_revenue"]
    total_sold = metrics["total_sold"]
    return_rate = metrics["return_rate"]
    top3_revenue = metrics["top3_revenue"]

    critical = [a for a in alerts if a["level"] == "critical"]
    warnings = [a for a in alerts if a["level"] == "warning"]

    lines = []

    # Block 1 — general results
    lines.append(
        f"За период {period} общая выручка составила {total_rev:,.0f} ₽, "
        f"продано {total_sold:,} единиц товара."
    )

    # Block 2 — revenue leader
    if top3_revenue:
        top = top3_revenue[0]
        lines.append(
            f"Лидер по выручке — {top['sku']} ({top['name']}): "
            f"{top['revenue']:,.0f} ₽."
        )

    # Block 3 — return rate
    if return_rate > 20:
        lines.append(
            f"Процент возвратов критически высок: {return_rate:.1f}%. "
            "Требуется срочное вмешательство."
        )
    elif return_rate > 15:
        lines.append(
            f"Процент возвратов повышен: {return_rate:.1f}%. Ситуация под наблюдением."
        )
    else:
        lines.append(f"Процент возвратов в норме: {return_rate:.1f}%.")

    # Block 4 — alerts summary
    if critical:
        lines.append(
            f"Выявлено {len(critical)} критических проблем и {len(warnings)} предупреждений."
        )
    elif warnings:
        lines.append(
            f"Критических проблем нет. Требуют внимания: {len(warnings)} позиций."
        )
    else:
        lines.append("Все показатели в норме. Критических проблем не обнаружено.")

    # Block 5 — campaign context
    if campaign:
        first_line = campaign.strip().split("\n")[0]
        lines.append(f"Контекст периода: {first_line}.")

    return " ".join(lines)
