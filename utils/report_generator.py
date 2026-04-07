"""
utils/report_generator.py
Generate professional PDF reports using reportlab.
"""

import io
import os
from datetime import datetime
from typing import Optional


def generate_pdf_report(
    file_name: str,
    resume_text: str,
    ats_result: dict,
    skills: list,
    contact_info: dict,
    ai_analysis: Optional[dict] = None,
    job_match: Optional[dict] = None,
) -> bytes:
    """
    Generate a comprehensive PDF report of the resume analysis.

    Returns bytes of the PDF file.
    """
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.colors import HexColor, black, white, grey
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            HRFlowable, PageBreak
        )
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=50,
            leftMargin=50,
            topMargin=50,
            bottomMargin=50,
        )

        # Colors
        PURPLE = HexColor("#7C3AED")
        DARK = HexColor("#1A1A2E")
        LIGHT_BG = HexColor("#F8F7FF")
        GREEN = HexColor("#10B981")
        ORANGE = HexColor("#F97316")
        RED = HexColor("#EF4444")

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Title"],
            fontSize=24,
            textColor=white,
            spaceAfter=6,
            fontName="Helvetica-Bold",
        )
        heading_style = ParagraphStyle(
            "Heading",
            parent=styles["Heading1"],
            fontSize=16,
            textColor=PURPLE,
            spaceAfter=8,
            spaceBefore=16,
            fontName="Helvetica-Bold",
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            textColor=DARK,
            spaceAfter=4,
            leading=14,
        )
        small_style = ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontSize=9,
            textColor=grey,
            spaceAfter=2,
        )

        elements = []

        # --- Header Banner ---
        header_data = [[
            Paragraph(f"<font size=20><b>AI Resume Analysis Report</b></font>", title_style),
            Paragraph(
                f"<font size=10 color='white'>Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}</font>",
                ParagraphStyle("sub", fontSize=10, textColor=white, fontName="Helvetica"),
            ),
        ]]
        header_table = Table(header_data, colWidths=[380, 150])
        header_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), PURPLE),
            ("PADDING", (0, 0), (-1, -1), 16),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))

        # --- Score Summary ---
        score = ats_result.get("total_score", 0)
        grade = ats_result.get("grade", "N/A")
        grade_label = ats_result.get("grade_label", "")

        score_color = GREEN if score >= 80 else ORANGE if score >= 60 else RED

        elements.append(Paragraph("📊 ATS Score Summary", heading_style))

        score_data = [
            ["File", "ATS Score", "Grade", "Assessment"],
            [file_name[:40], f"{score}/100", grade, grade_label],
        ]
        score_table = Table(score_data, colWidths=[200, 80, 60, 130])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("BACKGROUND", (1, 1), (1, 1), score_color),
            ("TEXTCOLOR", (1, 1), (1, 1), white),
            ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
            ("FONTSIZE", (1, 1), (1, 1), 14),
            ("GRID", (0, 0), (-1, -1), 0.5, grey),
            ("PADDING", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, white]),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 12))

        # --- Category Breakdown ---
        elements.append(Paragraph("📋 Category Breakdown", heading_style))
        cat_scores = ats_result.get("category_scores", {})

        cat_data = [["Category", "Score", "Max Score", "Status"]]
        for cat, data in cat_scores.items():
            s = data["score"]
            m = data["max"]
            pct = (s / m * 100) if m > 0 else 0
            status = "✓ Good" if pct >= 80 else "⚠ Fair" if pct >= 50 else "✗ Needs Work"
            cat_data.append([cat, str(s), str(m), status])

        cat_table = Table(cat_data, colWidths=[220, 60, 70, 120])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (1, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, grey),
            ("PADDING", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [LIGHT_BG, white]),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 12))

        # --- Skills Found ---
        if skills:
            elements.append(Paragraph("🛠️ Skills Detected", heading_style))
            skills_text = " • ".join(skills[:25])
            elements.append(Paragraph(skills_text, body_style))
            elements.append(Spacer(1, 8))

        # --- Feedback / Improvements ---
        improvements = ats_result.get("improvements", [])
        positives = ats_result.get("positives", [])

        if positives:
            elements.append(Paragraph("✅ Strengths", heading_style))
            for pos in positives:
                elements.append(Paragraph(f"  {pos}", body_style))
            elements.append(Spacer(1, 8))

        if improvements:
            elements.append(Paragraph("⚠️ Areas for Improvement", heading_style))
            for imp in improvements:
                elements.append(Paragraph(f"  {imp}", body_style))
            elements.append(Spacer(1, 8))

        # --- AI Analysis (if available) ---
        if ai_analysis:
            elements.append(PageBreak())
            elements.append(Paragraph("🤖 AI-Powered Insights", heading_style))

            if ai_analysis.get("overall_assessment"):
                elements.append(Paragraph("<b>Overall Assessment:</b>", body_style))
                elements.append(Paragraph(ai_analysis["overall_assessment"], body_style))
                elements.append(Spacer(1, 8))

            if ai_analysis.get("suggested_roles"):
                elements.append(Paragraph("<b>Suggested Job Roles:</b>", body_style))
                roles = ", ".join(ai_analysis["suggested_roles"])
                elements.append(Paragraph(roles, body_style))
                elements.append(Spacer(1, 8))

            if ai_analysis.get("summary_rewrite"):
                elements.append(Paragraph("<b>Suggested Summary Rewrite:</b>", body_style))
                elements.append(Paragraph(ai_analysis["summary_rewrite"], body_style))

        # --- Footer ---
        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=PURPLE))
        elements.append(Paragraph(
            "Generated by AI Resume Analyzer | For career advancement purposes only",
            ParagraphStyle("footer", fontSize=8, textColor=grey, alignment=1),
        ))

        doc.build(elements)
        return buffer.getvalue()

    except ImportError:
        return _generate_simple_report(file_name, ats_result, skills)
    except Exception as e:
        return _generate_simple_report(file_name, ats_result, skills)


def _generate_simple_report(file_name: str, ats_result: dict, skills: list) -> bytes:
    """Fallback simple text report if reportlab not available."""
    score = ats_result.get("total_score", 0)
    grade = ats_result.get("grade", "N/A")
    improvements = ats_result.get("improvements", [])
    positives = ats_result.get("positives", [])

    lines = [
        "=" * 60,
        "AI RESUME ANALYSIS REPORT",
        f"Generated: {datetime.now().strftime('%B %d, %Y')}",
        "=" * 60,
        "",
        f"File: {file_name}",
        f"ATS Score: {score}/100",
        f"Grade: {grade}",
        "",
        "STRENGTHS:",
        *[f"  {p}" for p in positives],
        "",
        "IMPROVEMENTS NEEDED:",
        *[f"  {i}" for i in improvements],
        "",
        "SKILLS DETECTED:",
        f"  {', '.join(skills[:20])}",
        "",
        "=" * 60,
    ]

    return "\n".join(lines).encode("utf-8")
