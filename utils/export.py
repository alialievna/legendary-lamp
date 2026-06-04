import io
import os
from typing import List, Dict

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─── Font setup ───────────────────────────────────────────────────────────────

_FONT_REGISTERED = False
_FONT_NAME = "Helvetica"

_FONT_SEARCH_PATHS = [
    "fonts/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/Library/Fonts/Arial Unicode MS.ttf",
    "/System/Library/Fonts/Supplemental/Arial Unicode MS.ttf",
]

_FONT_BOLD_PATHS = [
    "fonts/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _setup_fonts() -> str:
    global _FONT_REGISTERED, _FONT_NAME
    if _FONT_REGISTERED:
        return _FONT_NAME

    for path in _FONT_SEARCH_PATHS:
        if not os.path.exists(path):
            continue
        try:
            pdfmetrics.registerFont(TTFont("UniFont", path))
            _FONT_NAME = "UniFont"
            # Try to register bold variant
            for bp in _FONT_BOLD_PATHS:
                if os.path.exists(bp):
                    try:
                        pdfmetrics.registerFont(TTFont("UniFont-Bold", bp))
                        pdfmetrics.registerFontFamily(
                            "UniFont", normal="UniFont", bold="UniFont-Bold"
                        )
                    except Exception:
                        pass
                    break
            _FONT_REGISTERED = True
            return _FONT_NAME
        except Exception:
            continue

    _FONT_REGISTERED = True
    return _FONT_NAME


# ─── CSV export ───────────────────────────────────────────────────────────────


def _return_status(rate: float) -> str:
    if rate > 20:
        return "Критично"
    elif rate >= 15:
        return "Внимание"
    return "Норма"


def _stock_status(qty: int) -> str:
    if qty < 50:
        return "Критично"
    elif qty <= 100:
        return "Внимание"
    return "Норма"


def export_csv(metrics: dict) -> bytes:
    df = metrics["sku_metrics"].copy()
    df["статус_возвратов"] = df["процент_возвратов"].apply(_return_status)
    df["статус_остатка"] = df["остаток"].apply(_stock_status)

    col_order = [
        "sku",
        "название_товара",
        "продано_штук_всего",
        "выручка_всего",
        "возвратов_всего",
        "процент_возвратов",
        "конверсия",
        "средняя_цена",
        "остаток",
        "статус_возвратов",
        "статус_остатка",
    ]
    existing = [c for c in col_order if c in df.columns]
    df = df[existing]

    buf = io.StringIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig", float_format="%.2f")
    return buf.getvalue().encode("utf-8-sig")


# ─── PDF export ───────────────────────────────────────────────────────────────


def _make_styles(font: str):
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "rTitle",
        fontName=font,
        fontSize=18,
        spaceAfter=10,
        textColor=colors.HexColor("#1a1a1a"),
    )
    h2 = ParagraphStyle(
        "rH2",
        fontName=font,
        fontSize=13,
        spaceAfter=6,
        spaceBefore=12,
        textColor=colors.HexColor("#1a1a1a"),
    )
    body = ParagraphStyle(
        "rBody",
        fontName=font,
        fontSize=9,
        spaceAfter=4,
        leading=13,
    )
    small = ParagraphStyle(
        "rSmall",
        fontName=font,
        fontSize=8,
        textColor=colors.grey,
        alignment=1,
    )
    return title, h2, body, small


def export_pdf(metrics: dict, alerts: List[Dict], summary: str) -> bytes:
    font = _setup_fonts()
    title_s, h2_s, body_s, small_s = _make_styles(font)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    story = []

    # ── Title ──────────────────────────────────────────────────────────────────
    story.append(Paragraph(f"Аналитический отчёт {metrics['period']}", title_s))
    story.append(Spacer(1, 5 * mm))

    # ── KPI block ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Ключевые показатели", h2_s))
    kpi_rows = [
        ["Показатель", "Значение"],
        ["Период", metrics["period"]],
        ["Общая выручка", f"{metrics['total_revenue']:,.0f} руб."],
        ["Продано товаров", f"{metrics['total_sold']:,} шт."],
        ["Возвратов", f"{metrics['total_returns']:,} шт."],
        ["Процент возвратов", f"{metrics['return_rate']:.1f}%"],
        ["Средняя конверсия", f"{metrics['avg_conversion']:.2f}%"],
        ["Уникальных SKU", str(metrics["sku_count"])],
    ]
    kpi_table = Table(kpi_rows, colWidths=[85 * mm, 85 * mm])
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8f8f8")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(kpi_table)
    story.append(Spacer(1, 5 * mm))

    # ── Summary ───────────────────────────────────────────────────────────────
    story.append(Paragraph("Автоматическая сводка", h2_s))
    story.append(Paragraph(summary, body_s))
    story.append(Spacer(1, 5 * mm))

    # ── Alerts ────────────────────────────────────────────────────────────────
    if alerts:
        story.append(Paragraph("Алерты", h2_s))
        for a in alerts:
            level_label = "КРИТИЧНО" if a["level"] == "critical" else "ВНИМАНИЕ"
            hex_color = "#e74c3c" if a["level"] == "critical" else "#d68910"
            alert_style = ParagraphStyle(
                "alert",
                fontName=font,
                fontSize=8,
                spaceAfter=3,
                textColor=colors.HexColor(hex_color),
            )
            story.append(
                Paragraph(f"[{level_label}] {a['sku']}: {a['message']}", alert_style)
            )
        story.append(Spacer(1, 5 * mm))

    # ── SKU table ─────────────────────────────────────────────────────────────
    story.append(Paragraph("Таблица по SKU", h2_s))
    sku_df = metrics["sku_metrics"]

    header = ["SKU", "Название", "Продано", "Выручка", "% Возвр.", "Конверсия", "Остаток"]
    rows = [header]
    for _, r in sku_df.iterrows():
        name_trunc = str(r["название_товара"])[:28]
        rows.append(
            [
                str(r["sku"]),
                name_trunc,
                str(int(r["продано_штук_всего"])),
                f"{r['выручка_всего']:,.0f}",
                f"{r['процент_возвратов']:.1f}%",
                f"{r['конверсия']:.2f}%",
                str(int(r["остаток"])),
            ]
        )

    col_w = [22 * mm, 48 * mm, 18 * mm, 26 * mm, 18 * mm, 20 * mm, 18 * mm]
    sku_table = Table(rows, colWidths=col_w, repeatRows=1)
    sku_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a1a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), font),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8f8f8")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cccccc")),
                ("PADDING", (0, 0), (-1, -1), 3),
                ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ]
        )
    )
    story.append(sku_table)

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph("Сформировано автоматически · Analytics Workflow", small_s))

    doc.build(story)
    buf.seek(0)
    return buf.read()
