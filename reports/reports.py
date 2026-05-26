from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Flowable
from reportlab.lib.colors import HexColor
import os

# ── YC-inspired palette ──────────────────────────────────────────────────────
YC_ORANGE   = HexColor("#FF6600")
YC_BLACK    = HexColor("#1A1A1A")
YC_DARK     = HexColor("#2D2D2D")
YC_MID      = HexColor("#555555")
YC_LIGHT    = HexColor("#888888")
YC_RULE     = HexColor("#E8E8E8")
YC_BG_SOFT  = HexColor("#FFF9F5")
YC_BG_CODE  = HexColor("#F5F5F5")
YC_ACCENT   = HexColor("#FF8533")
YC_GREEN    = HexColor("#00A878")
YC_BLUE     = HexColor("#0066CC")
YC_RED      = HexColor("#CC0000")
WHITE       = colors.white

W, H = A4   # 595 x 842 pt
PAGE_W = W - 2*cm

# ── helpers ──────────────────────────────────────────────────────────────────
def c(hex_str):
    return HexColor(hex_str)

# ── custom flowables ─────────────────────────────────────────────────────────
class OrangeLine(Flowable):
    def __init__(self, width=PAGE_W, thickness=2.5):
        super().__init__()
        self.width, self.thickness = width, thickness
    def draw(self):
        self.canv.setFillColor(YC_ORANGE)
        self.canv.rect(0, 0, self.width, self.thickness, fill=1, stroke=0)
    def wrap(self, *args): return (self.width, self.thickness + 2)

class SectionRule(Flowable):
    def draw(self):
        self.canv.setStrokeColor(YC_RULE)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 0, PAGE_W, 0)
    def wrap(self, *args): return (PAGE_W, 2)

class TagPill(Flowable):
    """Pill-shaped tag label."""
    def __init__(self, text, bg=YC_ORANGE, fg=WHITE, font_size=7.5):
        super().__init__()
        self.text, self.bg, self.fg = text, bg, fg
        self.font_size = font_size
        self.pad_x, self.pad_y = 6, 3
        self._w = len(text) * font_size * 0.6 + 2 * self.pad_x
        self._h = font_size + 2 * self.pad_y
    def wrap(self, *args): return (self._w, self._h)
    def draw(self):
        c = self.canv
        r = self._h / 2
        c.setFillColor(self.bg)
        c.roundRect(0, 0, self._w, self._h, r, fill=1, stroke=0)
        c.setFillColor(self.fg)
        c.setFont("Helvetica-Bold", self.font_size)
        c.drawString(self.pad_x, self.pad_y + 1, self.text)

# ── styles ────────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    S = {}

    def s(name, **kw):
        parent = kw.pop("parent", "Normal")
        S[name] = ParagraphStyle(name, parent=base[parent], **kw)

    # Cover
    s("cover_title",    fontName="Helvetica-Bold",  fontSize=36, textColor=YC_BLACK,
      leading=42, spaceAfter=8, alignment=TA_LEFT)
    s("cover_sub",      fontName="Helvetica",        fontSize=16, textColor=YC_MID,
      leading=22, spaceAfter=6, alignment=TA_LEFT)
    s("cover_tag",      fontName="Helvetica-Bold",   fontSize=9,  textColor=YC_ORANGE,
      leading=14, spaceAfter=4, alignment=TA_LEFT)
    s("cover_meta",     fontName="Helvetica",         fontSize=10, textColor=YC_LIGHT,
      leading=14, alignment=TA_LEFT)

    # Headings
    s("h1", fontName="Helvetica-Bold",  fontSize=22, textColor=YC_BLACK,
      leading=28, spaceBefore=18, spaceAfter=6)
    s("h2", fontName="Helvetica-Bold",  fontSize=15, textColor=YC_DARK,
      leading=20, spaceBefore=14, spaceAfter=4)
    s("h3", fontName="Helvetica-Bold",  fontSize=11.5, textColor=YC_ORANGE,
      leading=16, spaceBefore=10, spaceAfter=3)
    s("h4", fontName="Helvetica-Bold",  fontSize=10,  textColor=YC_DARK,
      leading=14, spaceBefore=8,  spaceAfter=2)

    # Body
    s("body", fontName="Helvetica", fontSize=9.5, textColor=YC_DARK,
      leading=15, spaceAfter=6, alignment=TA_JUSTIFY)
    s("body_left", fontName="Helvetica", fontSize=9.5, textColor=YC_DARK,
      leading=15, spaceAfter=4)
    s("small", fontName="Helvetica", fontSize=8.5, textColor=YC_MID,
      leading=13, spaceAfter=4)
    s("caption", fontName="Helvetica-Oblique", fontSize=8, textColor=YC_LIGHT,
      leading=12, spaceAfter=6, alignment=TA_CENTER)

    # Special
    s("callout", fontName="Helvetica-Bold", fontSize=9.5, textColor=YC_DARK,
      leading=15, spaceAfter=4, leftIndent=10, rightIndent=10)
    s("code",    fontName="Courier",         fontSize=8.2, textColor=YC_DARK,
      leading=13, spaceAfter=0, leftIndent=8)
    s("bullet",  fontName="Helvetica",        fontSize=9.2, textColor=YC_DARK,
      leading=14, spaceAfter=3, leftIndent=12, bulletIndent=0)
    s("phase_label", fontName="Helvetica-Bold", fontSize=8, textColor=YC_ORANGE,
      leading=12, spaceAfter=2)
    s("orange_label", fontName="Helvetica-Bold", fontSize=9, textColor=YC_ORANGE,
      leading=13, spaceAfter=2)
    s("metric_big", fontName="Helvetica-Bold", fontSize=22, textColor=YC_ORANGE,
      leading=26, spaceAfter=2, alignment=TA_CENTER)
    s("metric_label", fontName="Helvetica", fontSize=8, textColor=YC_MID,
      leading=12, spaceAfter=0, alignment=TA_CENTER)
    s("toc_item", fontName="Helvetica", fontSize=10, textColor=YC_DARK,
      leading=18, leftIndent=0)
    s("toc_section", fontName="Helvetica-Bold", fontSize=11, textColor=YC_ORANGE,
      leading=20, spaceBefore=6)
    s("footer_text", fontName="Helvetica", fontSize=7.5, textColor=YC_LIGHT,
      leading=10, alignment=TA_CENTER)
    s("page_header", fontName="Helvetica-Bold", fontSize=8, textColor=YC_LIGHT,
      leading=10)

    return S

# ── table helpers ─────────────────────────────────────────────────────────────
def std_table(data, col_widths, header_bg=YC_ORANGE, alt_row=True):
    style = [
        ("BACKGROUND", (0,0), (-1,0), header_bg),
        ("TEXTCOLOR",  (0,0), (-1,0), WHITE),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,0), 8.5),
        ("ALIGN",      (0,0), (-1,0), "LEFT"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",(0,0),(-1,-1), 7),
        ("RIGHTPADDING",(0,0),(-1,-1), 7),
        ("FONTNAME",   (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",   (0,1), (-1,-1), 8.2),
        ("TEXTCOLOR",  (0,1), (-1,-1), YC_DARK),
        ("GRID",       (0,0), (-1,-1), 0.3, YC_RULE),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, HexColor("#FFF5EE")] if alt_row else [WHITE]),
    ]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle(style))
    return t

def callout_box(S, title, body_text, bg=YC_BG_SOFT, border=YC_ORANGE):
    """Returns a Table that looks like a highlighted callout card."""
    content = [
        [Paragraph(f"<b>{title}</b>", S["h4"])],
        [Paragraph(body_text, S["body_left"])],
    ]
    t = Table(content, colWidths=[PAGE_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING",(0,0), (-1,-1), 12),
        ("TOPPADDING",  (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LINEAFTER",  (0,0), (0,-1), 3, border),  # left border trick via right of col 0 — but we use LINEBEFORE
        ("LINEBEFORE", (0,0), (-1,-1), 3, border),
        ("BOX",        (0,0), (-1,-1), 0.4, YC_RULE),
        ("ROUNDEDCORNERS", [4]),
    ]))
    return t

def mini_metrics(S, items):
    """Row of metric cards. items = [(value, label), ...]"""
    cells = []
    for val, lbl in items:
        inner = Table([
            [Paragraph(val, S["metric_big"])],
            [Paragraph(lbl, S["metric_label"])],
        ], colWidths=[(PAGE_W - 6*(len(items)-1)) / len(items)])
        inner.setStyle(TableStyle([
            ("ALIGN",(0,0),(-1,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),10),
            ("BOTTOMPADDING",(0,0),(-1,-1),10),
            ("BACKGROUND",(0,0),(-1,-1),YC_BG_SOFT),
            ("BOX",(0,0),(-1,-1),0.5,YC_RULE),
        ]))
        cells.append(inner)
    row = Table([cells], colWidths=[(PAGE_W - 6*(len(items)-1)) / len(items)]*len(items),
                hAlign="LEFT")
    row.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),
                              ("RIGHTPADDING",(0,0),(-1,-1),0),
                              ("TOPPADDING",(0,0),(-1,-1),0),
                              ("BOTTOMPADDING",(0,0),(-1,-1),0)]))
    return row

# ── page templates ────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    # Header rule
    canvas.setStrokeColor(YC_RULE)
    canvas.setLineWidth(0.5)
    canvas.line(cm, H - 1.2*cm, W - cm, H - 1.2*cm)
    # Header text
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(YC_ORANGE)
    canvas.drawString(cm, H - 1.0*cm, "Syntro")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(YC_LIGHT)
    canvas.drawRightString(W - cm, H - 1.0*cm, "Technical Roadmap & Architecture — Confidential")
    # Footer
    canvas.setStrokeColor(YC_RULE)
    canvas.line(cm, 1.4*cm, W - cm, 1.4*cm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(YC_LIGHT)
    canvas.drawCentredString(W/2, 0.9*cm, f"Page {doc.page}")
    canvas.drawString(cm, 0.9*cm, "Internal — Do Not Distribute")
    canvas.drawRightString(W - cm, 0.9*cm, "May 2026")
    canvas.restoreState()

def on_first_page(canvas, doc):
    canvas.saveState()
    canvas.restoreState()

# ── DOCUMENT BUILD ────────────────────────────────────────────────────────────
def build():
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Syntro_Technical_Roadmap.pdf")
    doc = SimpleDocTemplate(
        out, pagesize=A4,
        leftMargin=cm, rightMargin=cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Syntro — Technical Roadmap",
        author="Syntro Engineering Team",
    )
    S = make_styles()
    story = []

    # ── COVER PAGE ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 1.2*cm))
    story.append(OrangeLine(PAGE_W, 4))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Syntro", S["cover_title"]))
    story.append(Paragraph("Technical Roadmap & Architecture Blueprint", S["cover_sub"]))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("MVP → Scale  ·  v1.0  ·  May 2026  ·  Internal Engineering Document", S["cover_meta"]))
    story.append(Spacer(1, 0.8*cm))
    story.append(OrangeLine(PAGE_W, 1))
    story.append(Spacer(1, 0.6*cm))

    # Tagline box
    tl = Table([
        [Paragraph(
            '"The user brings the content. The platform brings the trend."',
            ParagraphStyle("ql", fontName="Helvetica-BoldOblique", fontSize=13,
                           textColor=YC_ORANGE, leading=18, alignment=TA_LEFT))
        ]
    ], colWidths=[PAGE_W])
    tl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), YC_BG_SOFT),
        ("LEFTPADDING",(0,0),(-1,-1),14),
        ("RIGHTPADDING",(0,0),(-1,-1),14),
        ("TOPPADDING",(0,0),(-1,-1),12),
        ("BOTTOMPADDING",(0,0),(-1,-1),12),
        ("LINEBEFORE",(0,0),(-1,-1),4,YC_ORANGE),
    ]))
    story.append(tl)
    story.append(Spacer(1, 0.7*cm))

    # Cover metric pills
    story.append(mini_metrics(S, [
        ("<b>10</b>", "Day MVP Sprint"),
        ("<b>~$15</b>", "Est. Month 1 Cost"),
        ("<b>2 min</b>", "Generation Target"),
        ("<b>5+</b>", "Beta Users Goal"),
    ]))
    story.append(Spacer(1, 0.8*cm))

    # Cover description
    story.append(Paragraph(
        "This document is the single source of truth for the Syntro engineering team. "
        "It covers product vision, system architecture, data pipelines, technology stack with "
        "cost breakdown, MVP sprint plan (10 days), and the scaling roadmap including SOTA "
        "video/AI model integration. Written from a CTO-level perspective for a student-founded "
        "startup targeting creators and clothing brands in emerging markets.",
        S["body"]))
    story.append(Spacer(1, 0.4*cm))

    # Team info table
    team_data = [
        ["Team", "Stack", "Stage", "Market"],
        ["2 Engineers (Full-Stack)", "Next.js · FastAPI · Supabase", "Pre-seed / MVP", "Nepal → South Asia → Global"],
    ]
    story.append(std_table(team_data, [PAGE_W*0.25]*4))
    story.append(Spacer(1, 1.5*cm))
    story.append(OrangeLine(PAGE_W, 1))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Confidential — Internal Engineering Document — Do Not Distribute", S["caption"]))
    story.append(PageBreak())

    # ── TABLE OF CONTENTS ────────────────────────────────────────────────────
    story.append(Paragraph("Table of Contents", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.3*cm))
    toc = [
        ("01", "Product Vision & Problem Statement"),
        ("02", "Core Architecture Overview"),
        ("03", "Technology Stack & Rationale"),
        ("04", "System Data Flow & Pipelines"),
        ("05", "Database Schema (Supabase / PostgreSQL)"),
        ("06", "Editing & AI Media Pipeline"),
        ("07", "Trend Intelligence Engine"),
        ("08", "Security & Infrastructure"),
        ("09", "MVP Sprint Plan — 10 Days"),
        ("10", "Cost Breakdown (MVP & Scale)"),
        ("11", "Success Metrics & KPIs"),
        ("12", "Scaling Roadmap — Phase 2 & Beyond"),
        ("13", "SOTA Video & AI Model Integration"),
        ("14", "Engineering Rules & CTO Notes"),
    ]
    for num, title in toc:
        row = Table(
            [[Paragraph(f"<font color='#FF6600'><b>{num}</b></font>", S["body_left"]),
              Paragraph(title, S["toc_item"])]],
            colWidths=[0.8*cm, PAGE_W - 0.8*cm]
        )
        row.setStyle(TableStyle([
            ("TOPPADDING",(0,0),(-1,-1),4),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("LEFTPADDING",(0,0),(-1,-1),0),
            ("LINEBELOW",(0,0),(-1,-1),0.3,YC_RULE),
        ]))
        story.append(row)
    story.append(PageBreak())

    # ── SECTION 01: PRODUCT VISION ───────────────────────────────────────────
    story.append(Paragraph("01 — Product Vision & Problem Statement", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("What We Are Building", S["h2"]))
    story.append(Paragraph(
        "Syntro is a trend-aware media editing platform built for clothing brands, solo creators, "
        "and social-first businesses. The platform detects what is visually trending on Instagram and "
        "TikTok right now, then automatically edits the user's own photos and videos to match those trends — "
        "color grading, filters, captions, aspect ratios, and transitions. No generative AI creating fake "
        "images. Real media. Real brands. Trend-optimized automatically.", S["body"]))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("The Core Problem", S["h2"]))

    prob_data = [
        ["Pain Point", "Reality", "Impact"],
        ["Slow trend response", "Trends peak in 24–72 hours; editing takes days", "Missed virality windows"],
        ["High editing cost", "Hiring editors is $500–2000/month for SMBs", "Unaffordable for small brands"],
        ["AI feels fake", "Generated images lack real products and people", "Low engagement & trust"],
        ["No integrated workflow", "Trend spotting and editing are completely separate", "Friction kills momentum"],
        ["Inconsistent brand", "Quick edits break brand identity", "Diluted brand equity"],
    ]
    story.append(std_table(prob_data, [PAGE_W*0.28, PAGE_W*0.45, PAGE_W*0.27]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Our Solution — The 5-Step Loop", S["h2"]))
    story.append(Paragraph(
        "Every user interaction follows a single, repeatable loop designed to be completed in under 2 minutes:",
        S["body"]))
    steps = [
        ("Upload", "User uploads raw photo or video (JPG, PNG, MP4, MOV). Max 500 MB. Stored in Supabase Storage / Cloudflare R2."),
        ("Detect", "Platform shows trending visual styles scraped from Instagram & TikTok — color palettes, caption styles, audio trends, aspect ratios."),
        ("Edit", "AI applies trend-style editing to the user's media: color grading (LUT-based), filters, caption overlay, aspect ratio conversion."),
        ("Export", "One-click export as MP4 or JPG/PNG. Output optimized per platform: 9:16 Reels/TikTok, 1:1 feed, 4:5 portrait."),
        ("Analyze", "After posting, track engagement per trend style. Platform learns what works for each brand over time."),
    ]
    for i, (step, desc) in enumerate(steps):
        row = Table([
            [Paragraph(f"<font color='#FF6600'><b>{i+1}</b></font>", S["h3"]),
             Paragraph(f"<b>{step}</b>", S["h4"]),
             Paragraph(desc, S["body_left"])]
        ], colWidths=[0.7*cm, 1.6*cm, PAGE_W - 2.3*cm])
        row.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("TOPPADDING",(0,0),(-1,-1),5),
            ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("LEFTPADDING",(0,0),(-1,-1),4),
            ("BACKGROUND",(0,0),(-1,-1), YC_BG_SOFT if i%2==0 else WHITE),
            ("LINEBELOW",(0,0),(-1,-1),0.3,YC_RULE),
        ]))
        story.append(row)
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("What We Are NOT Building (Scope Guard)", S["h2"]))
    nope = [
        "❌  Generative AI image tool — no creating images from scratch",
        "❌  Canva clone — no complex drag-and-drop design editor",
        "❌  Full video production suite — no timeline editors or keyframing",
        "❌  Social media scheduler — Phase 1 is export only",
        "❌  Marketplace or collaboration system — Phase 4+",
    ]
    for n in nope:
        story.append(Paragraph(n, S["bullet"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Target Market", S["h2"]))
    mkt_data = [
        ["Segment", "Profile", "Primary Need", "Geography"],
        ["Clothing brands", "Small–medium, IG/TikTok focused", "Product showcases, lookbooks", "Nepal → India → SE Asia"],
        ["Solo creators", "Fashion, lifestyle, streetwear", "Daily trend-matching content", "Tier 1–2 cities"],
        ["Agencies", "Managing 5–20 brand accounts", "High-volume editing at speed", "Urban centers"],
        ["Social commerce", "Sell via Instagram / TikTok Shop", "Shoppable content, quick edits", "Emerging markets"],
    ]
    story.append(std_table(mkt_data, [PAGE_W*0.2, PAGE_W*0.28, PAGE_W*0.28, PAGE_W*0.24]))
    story.append(PageBreak())

    # ── SECTION 02: ARCHITECTURE ─────────────────────────────────────────────
    story.append(Paragraph("02 — Core Architecture Overview", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Architectural Philosophy", S["h2"]))
    story.append(Paragraph(
        "We use a modular monolith for the MVP. This is the correct choice for a 2-person student team: "
        "single codebase, easy debugging, low infrastructure cost, and zero distributed systems overhead. "
        "The monolith is organized into clearly separated modules (auth, trends, editing, analytics, exports) "
        "so that microservice extraction is clean when traffic demands it. We never pay for complexity we haven't earned.",
        S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("System Architecture Diagram", S["h2"]))
    # ASCII-style architecture as a styled table
    arch_layers = [
        ["Layer", "Component", "Technology", "Responsibility"],
        ["Frontend", "Dashboard / UI", "Next.js 14 + TailwindCSS + shadcn/ui", "Upload, trend browse, preview, export, analytics"],
        ["API Gateway", "REST API", "FastAPI + Pydantic (Python 3.11)", "Auth, routing, validation, business logic"],
        ["Job Queue", "Async Workers", "Celery + Redis (Upstash free tier)", "Editing jobs, trend scraping, background tasks"],
        ["AI Editing", "Media Processor", "FFmpeg + Pillow (+ Replicate optional)", "Color grade, captions, resize, format convert"],
        ["Trend Engine", "Scraper + Scorer", "Custom scrapers + heuristic scoring", "Detect, rank, categorize trending styles"],
        ["Storage", "Object Store", "Supabase Storage (S3-compatible)", "Raw uploads + edited outputs + CDN delivery"],
        ["Database", "Persistent State", "PostgreSQL via Supabase", "Users, brand kits, trends, jobs, analytics"],
        ["Auth", "Identity", "Supabase Auth (JWT)", "Registration, login, session, protected routes"],
        ["Monitoring", "Observability", "UptimeRobot + Flower", "Uptime alerts, queue dashboard"],
        ["Deployment", "Hosting", "Vercel (FE) + Railway (BE + Workers)", "Auto-deploy from GitHub, managed Redis"],
    ]
    story.append(std_table(arch_layers, [PAGE_W*0.13, PAGE_W*0.17, PAGE_W*0.35, PAGE_W*0.35]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Request Flow — High Level", S["h2"]))
    story.append(Paragraph(
        "Every user action follows a predictable path through the system. Understanding this flow is essential "
        "for debugging and performance optimization:", S["body"]))

    flow_steps = [
        ("Browser", "User action in Next.js dashboard (upload, edit, export)"),
        ("HTTPS + JWT", "Authenticated request sent to FastAPI backend on Railway"),
        ("FastAPI", "Route handler validates request, calls appropriate service module"),
        ("Redis Queue", "Heavy jobs (editing, trend scraping) are enqueued immediately — API returns job_id"),
        ("Celery Worker", "Worker picks up job, downloads media, runs FFmpeg/Pillow pipeline"),
        ("Supabase Storage", "Edited file uploaded to Supabase Storage, CDN URL returned"),
        ("PostgreSQL", "CDN URL and job metadata saved to database"),
        ("Frontend Poll", "Next.js polls /jobs/{id}/status every 3s, displays result on completion"),
    ]
    fd = [["Step", "Component", "Action"]] + [
        [str(i+1), comp, action] for i, (comp, action) in enumerate(flow_steps)
    ]
    story.append(std_table(fd, [0.7*cm, PAGE_W*0.22, PAGE_W - 0.7*cm - PAGE_W*0.22]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Backend Module Structure", S["h2"]))
    story.append(Paragraph(
        "The FastAPI backend is organized as a modular monolith. Each module owns its routes, services, "
        "and models. Shared code lives in /core. This structure allows future extraction into microservices "
        "without a rewrite:", S["body"]))
    code_struct = """backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Login, register, refresh
│   │       ├── brand_kit.py     # CRUD for brand identities
│   │       ├── trends.py        # Trend feed, categories
│   │       ├── editing.py       # Submit edit jobs, status
│   │       ├── exports.py       # Signed download URLs
│   │       └── analytics.py    # Engagement tracking
│   ├── services/
│   │   ├── editing_service.py   # FFmpeg + Pillow orchestration
│   │   ├── trend_service.py     # Trend scoring + categorization
│   │   ├── storage_service.py   # Supabase Storage upload/download
│   │   └── ai_service.py        # Replicate/Veo API calls (Phase 2)
│   ├── workers/
│   │   ├── edit_worker.py       # Celery task: process media
│   │   └── trend_worker.py      # Celery task: scrape trends
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Pydantic request/response schemas
│   ├── core/
│   │   ├── config.py            # Settings from .env
│   │   ├── security.py          # JWT verification
│   │   └── database.py          # DB session factory
│   └── main.py                  # FastAPI app factory
├── alembic/                     # DB migrations
├── tests/
└── Dockerfile"""
    ct = Table([[Paragraph(code_struct, S["code"])]], colWidths=[PAGE_W])
    ct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),YC_BG_CODE),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("BOX",(0,0),(-1,-1),0.5,YC_RULE),
    ]))
    story.append(ct)
    story.append(PageBreak())

    # ── SECTION 03: TECH STACK ───────────────────────────────────────────────
    story.append(Paragraph("03 — Technology Stack & Rationale", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Every technology choice is optimized for two constraints: (1) a 2-person student team with "
        "limited time, and (2) a near-zero budget for MVP. We default to managed services, free tiers, "
        "and battle-tested libraries. We only self-host when there is no other option.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    stack_data = [
        ["Layer", "Technology", "Why We Chose It", "Free Tier / Cost"],
        ["Frontend", "Next.js 14 + TypeScript", "App Router, SSR, great DX, huge ecosystem", "Free on Vercel"],
        ["UI Components", "TailwindCSS + shadcn/ui", "Fast beautiful UI without custom CSS", "Free / OSS"],
        ["Backend", "FastAPI (Python 3.11)", "Async, fast, Pydantic validation, ML-friendly", "Free (Railway ~$5/mo)"],
        ["ORM", "SQLAlchemy 2.0 + Alembic", "Type-safe queries, clean migrations", "Free / OSS"],
        ["Database", "Supabase (PostgreSQL)", "Managed DB + Auth + Storage in one, generous free tier", "Free up to 500 MB"],
        ["Auth", "Supabase Auth", "Built into Supabase, handles JWT, sessions, OAuth", "Free up to 50K MAU"],
        ["Storage", "Supabase Storage", "S3-compatible, CDN delivery, same dashboard as DB", "1 GB free"],
        ["Job Queue", "Celery + Redis (Upstash)", "Battle-tested async processing, free Redis tier", "$0 (10K cmds/day)"],
        ["Image Editing", "Pillow (PIL)", "Filters, color grading, overlays, captions", "Free / OSS"],
        ["Video Editing", "FFmpeg", "Industry standard, LUTs, captions, resize, format", "Free / OSS"],
        ["AI (optional MVP)", "Replicate API", "Pay-per-use, no GPU setup, Flux/SDXL access", "~$0.003–0.05/call"],
        ["Video AI (Phase 2)", "Google Veo 3 API", "SOTA video gen, cheaper than self-hosting", "$0.35–0.70/video"],
        ["Frontend Deploy", "Vercel", "Auto-deploy from GitHub, edge CDN, free tier", "Free hobby plan"],
        ["Backend Deploy", "Railway", "Simple Python deploy, env vars, managed services", "$5/mo starter"],
        ["Monitoring", "UptimeRobot + Flower", "Uptime alerts + Celery queue dashboard", "Free tiers"],
        ["CI/CD", "GitHub Actions", "Auto-test on push, free for public repos", "Free 2K min/mo"],
    ]
    story.append(std_table(stack_data, [PAGE_W*0.14, PAGE_W*0.22, PAGE_W*0.38, PAGE_W*0.26]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Why Supabase Over Separate Services", S["h2"]))
    story.append(Paragraph(
        "For a student team, Supabase is a force multiplier. It replaces four separate services "
        "(PostgreSQL hosting, Auth service, Object Storage, and Realtime subscriptions) with a single "
        "dashboard and SDK. The free tier is generous enough to cover the entire MVP phase. "
        "Migration to dedicated services (Neon DB, Clerk, Cloudflare R2) is straightforward if needed at scale.", S["body"]))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Why FFmpeg + Pillow Before AI Models", S["h2"]))
    story.append(Paragraph(
        "The editing quality needed for MVP is achievable with deterministic processing. "
        "FFmpeg LUT color grading + Pillow filter overlays produce professional-looking results at "
        "exactly $0 compute cost. AI style transfer via Replicate is a Phase 2 upgrade, not a starting point. "
        "This approach keeps the job completion time under 30 seconds and cost near zero per edit.", S["body"]))
    story.append(PageBreak())

    # ── SECTION 04: DATA FLOW & PIPELINES ────────────────────────────────────
    story.append(Paragraph("04 — System Data Flow & Pipelines", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("4.1 — Media Upload Pipeline", S["h2"]))
    story.append(Paragraph(
        "Media upload is designed to never proxy large files through the FastAPI backend. "
        "The backend only generates a signed URL; the browser uploads directly to Supabase Storage. "
        "This keeps the backend stateless and prevents memory overflow on large video files.", S["body"]))

    upload_flow = [
        ["Step", "Actor", "Action", "Technology"],
        ["1", "Frontend", "User selects file, client requests upload URL", "Next.js fetch()"],
        ["2", "FastAPI", "Validate file type/size, generate signed upload URL", "Supabase Storage SDK"],
        ["3", "Browser", "Upload file directly to Supabase Storage", "Direct PUT to signed URL"],
        ["4", "FastAPI", "Receive upload confirmation, create media_asset record in DB", "SQLAlchemy + Supabase"],
        ["5", "FastAPI", "Enqueue preprocessing job, return asset_id to frontend", "Celery task"],
        ["6", "Worker", "Download file, extract metadata (resolution, fps, duration, mime)", "FFprobe + Pillow"],
        ["7", "Worker", "Update media_asset record with metadata, set status=ready", "SQLAlchemy"],
        ["8", "Frontend", "Display uploaded file preview with metadata", "Next.js state update"],
    ]
    story.append(std_table(upload_flow, [0.6*cm, PAGE_W*0.13, PAGE_W*0.50, PAGE_W*0.28]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4.2 — Editing Job Pipeline", S["h2"]))
    story.append(Paragraph(
        "The editing pipeline is the core of the product. Every step is independently retryable via Celery. "
        "If a step fails, the job returns to the queue with exponential backoff — no manual intervention needed.", S["body"]))

    edit_flow = [
        ["Step", "Stage", "Tool", "Description"],
        ["1", "Enqueue", "FastAPI + Celery", "POST /edit receives brand_kit_id + trend_id + asset_id, returns job_id immediately"],
        ["2", "Download", "Supabase Storage SDK", "Worker fetches raw media from storage to temp disk"],
        ["3", "Preprocess", "FFprobe + Pillow", "Extract resolution, duration, FPS, color profile, orientation"],
        ["4", "Trend Map", "Trend Service", "Load trend parameters: LUT file, filter settings, caption style, aspect ratio target"],
        ["5", "Color Grade", "FFmpeg LUTs", "Apply 3D LUT matching trend's color palette (warm/cool/moody/Y2K/minimal)"],
        ["6", "Filter Overlay", "Pillow", "Apply grain, vignette, light leak effects; adjust brightness/contrast/saturation"],
        ["7", "Caption Burn", "FFmpeg drawtext", "Render trend-style caption with brand font and colors onto image or video"],
        ["8", "Aspect Ratio", "FFmpeg", "Auto-crop/pad to target: 9:16 (Reels/TikTok), 1:1 (Feed), 4:5 (Portrait)"],
        ["9", "Render", "FFmpeg", "Final encode: MP4 (H.264, AAC) for video; JPEG/WebP for images"],
        ["10", "Optimize", "FFmpeg", "Compress to platform-optimal bitrate; strip metadata for privacy"],
        ["11", "Upload", "Supabase Storage", "Upload edited file to /edited/ path, get CDN URL"],
        ["12", "Complete", "FastAPI + Redis", "Update edit_job status=complete, store CDN URL; frontend notified"],
    ]
    story.append(std_table(edit_flow, [0.6*cm, PAGE_W*0.15, PAGE_W*0.22, PAGE_W - 0.6*cm - PAGE_W*0.37]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("4.3 — Trend Detection Dataflow", S["h2"]))
    story.append(Paragraph(
        "The trend pipeline runs as a background Celery beat job every 6 hours. In MVP, we seed the database "
        "with 5 hardcoded trend categories and supplement with lightweight scraping. The full automated "
        "pipeline deploys in Phase 2.", S["body"]))

    trend_flow = [
        ["Step", "Process", "Source / Tool", "Output"],
        ["1", "Ingest", "Instagram/TikTok API or lightweight scraper", "Raw hashtags, audio names, caption samples"],
        ["2", "Score", "Heuristic formula (see Section 07)", "Trend score 0.0–1.0 per style"],
        ["3", "Categorize", "Rule-based tagging", "Aesthetic labels: moody, Y2K, minimal, bright, cottagecore"],
        ["4", "Deduplicate", "PostgreSQL UPSERT", "Remove duplicate trends across scraping runs"],
        ["5", "Store", "PostgreSQL trends table", "Scored, labeled trend records with TTL (expires_at)"],
        ["6", "Serve", "FastAPI /trends endpoint", "Ranked trend cards displayed in the dashboard"],
        ["7", "Map to LUT", "Trend Service", "Link trend aesthetic to FFmpeg LUT file + Pillow settings"],
    ]
    story.append(std_table(trend_flow, [0.6*cm, PAGE_W*0.15, PAGE_W*0.32, PAGE_W - 0.6*cm - PAGE_W*0.47]))
    story.append(PageBreak())

    # ── SECTION 05: DATABASE SCHEMA ──────────────────────────────────────────
    story.append(Paragraph("05 — Database Schema (Supabase / PostgreSQL)", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "All tables live in a single PostgreSQL database on Supabase. Supabase Row Level Security (RLS) "
        "is enabled on all user-owned tables. The schema is designed for MVP simplicity with clear "
        "extension points for Phase 2 features.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    tables = [
        ("users", [
            ("id", "UUID PRIMARY KEY", "Supabase Auth user ID"),
            ("email", "TEXT UNIQUE NOT NULL", "User email address"),
            ("name", "TEXT", "Display name"),
            ("subscription_tier", "TEXT DEFAULT 'free'", "free | starter | pro"),
            ("created_at", "TIMESTAMPTZ DEFAULT NOW()", "Registration timestamp"),
            ("updated_at", "TIMESTAMPTZ", "Last profile update"),
        ]),
        ("brand_kits", [
            ("id", "UUID PRIMARY KEY DEFAULT gen_random_uuid()", "Unique brand kit ID"),
            ("user_id", "UUID REFERENCES users(id)", "Owner user"),
            ("name", "TEXT NOT NULL", "Brand name"),
            ("logo_url", "TEXT", "CDN URL of logo asset"),
            ("primary_color", "TEXT", "Hex color #RRGGBB"),
            ("secondary_color", "TEXT", "Hex color #RRGGBB"),
            ("font_name", "TEXT", "Font family name"),
            ("tone", "TEXT", "Brand tone: bold | minimal | playful | luxury"),
            ("created_at", "TIMESTAMPTZ DEFAULT NOW()", "Creation timestamp"),
        ]),
        ("media_assets", [
            ("id", "UUID PRIMARY KEY DEFAULT gen_random_uuid()", "Asset ID"),
            ("user_id", "UUID REFERENCES users(id)", "Uploader"),
            ("storage_key", "TEXT NOT NULL", "Supabase Storage path"),
            ("cdn_url", "TEXT", "Public CDN URL"),
            ("mime_type", "TEXT", "video/mp4 | image/jpeg | etc."),
            ("duration_sec", "FLOAT", "Video duration in seconds (null for images)"),
            ("resolution_w", "INT", "Width in pixels"),
            ("resolution_h", "INT", "Height in pixels"),
            ("fps", "FLOAT", "Frames per second (video only)"),
            ("file_size_bytes", "BIGINT", "File size"),
            ("status", "TEXT DEFAULT 'pending'", "pending | ready | error"),
            ("created_at", "TIMESTAMPTZ DEFAULT NOW()", "Upload timestamp"),
        ]),
        ("trends", [
            ("id", "UUID PRIMARY KEY DEFAULT gen_random_uuid()", "Trend ID"),
            ("name", "TEXT NOT NULL", "Trend name e.g. Soft Moody Film"),
            ("category", "TEXT", "Aesthetic category label"),
            ("platform", "TEXT", "instagram | tiktok | both"),
            ("aesthetic_tags", "TEXT[]", "Array of style tags"),
            ("score", "FLOAT", "Heuristic score 0.0–1.0"),
            ("lut_file", "TEXT", "Filename of FFmpeg LUT to apply"),
            ("pillow_settings", "JSONB", "JSON: brightness, contrast, saturation, grain"),
            ("caption_style", "JSONB", "JSON: font_size, position, color, opacity"),
            ("detected_at", "TIMESTAMPTZ", "When trend was identified"),
            ("expires_at", "TIMESTAMPTZ", "Auto-expire stale trends"),
        ]),
        ("edit_jobs", [
            ("id", "UUID PRIMARY KEY DEFAULT gen_random_uuid()", "Job ID"),
            ("user_id", "UUID REFERENCES users(id)", "Requester"),
            ("media_asset_id", "UUID REFERENCES media_assets(id)", "Input media"),
            ("brand_kit_id", "UUID REFERENCES brand_kits(id)", "Brand to apply"),
            ("trend_id", "UUID REFERENCES trends(id)", "Trend style to apply"),
            ("status", "TEXT DEFAULT 'queued'", "queued | processing | complete | failed"),
            ("edited_url", "TEXT", "CDN URL of output file"),
            ("aspect_ratio", "TEXT", "9:16 | 1:1 | 4:5"),
            ("error_message", "TEXT", "Error detail if failed"),
            ("celery_task_id", "TEXT", "Celery task UUID for polling"),
            ("started_at", "TIMESTAMPTZ", "Worker pick-up time"),
            ("completed_at", "TIMESTAMPTZ", "Completion time"),
            ("created_at", "TIMESTAMPTZ DEFAULT NOW()", "Submission time"),
        ]),
        ("exports", [
            ("id", "UUID PRIMARY KEY DEFAULT gen_random_uuid()", "Export ID"),
            ("edit_job_id", "UUID REFERENCES edit_jobs(id)", "Source edit job"),
            ("format", "TEXT", "mp4 | jpg | png | webp"),
            ("resolution", "TEXT", "e.g. 1080x1920"),
            ("aspect_ratio", "TEXT", "9:16 | 1:1 | 4:5"),
            ("file_url", "TEXT", "Signed download URL"),
            ("downloaded_at", "TIMESTAMPTZ", "When user downloaded"),
            ("created_at", "TIMESTAMPTZ DEFAULT NOW()", "Export creation time"),
        ]),
        ("analytics", [
            ("id", "UUID PRIMARY KEY DEFAULT gen_random_uuid()", "Record ID"),
            ("user_id", "UUID REFERENCES users(id)", "User"),
            ("edit_job_id", "UUID REFERENCES edit_jobs(id)", "Source edit"),
            ("trend_id", "UUID REFERENCES trends(id)", "Trend used"),
            ("platform_posted", "TEXT", "instagram | tiktok | youtube"),
            ("likes", "INT DEFAULT 0", "Engagement: likes"),
            ("views", "INT DEFAULT 0", "Engagement: views"),
            ("shares", "INT DEFAULT 0", "Engagement: shares"),
            ("comments", "INT DEFAULT 0", "Engagement: comments"),
            ("recorded_at", "TIMESTAMPTZ DEFAULT NOW()", "When data was logged"),
        ]),
    ]

    for tname, cols in tables:
        story.append(Paragraph(f"Table: {tname}", S["h3"]))
        tdata = [["Column", "Type / Constraint", "Description"]] + list(cols)
        story.append(std_table(tdata, [PAGE_W*0.24, PAGE_W*0.38, PAGE_W*0.38]))
        story.append(Spacer(1, 0.25*cm))

    story.append(PageBreak())

    # ── SECTION 06: EDITING PIPELINE ─────────────────────────────────────────
    story.append(Paragraph("06 — Editing & AI Media Pipeline", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "The editing pipeline is the product's core value delivery mechanism. Phase 1 uses entirely "
        "deterministic processing — no AI API calls required. This keeps cost at $0 per edit and "
        "latency under 30 seconds for images, under 90 seconds for videos under 60 seconds.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Phase 1 Editing Capabilities (Deterministic — $0 Cost)", S["h2"]))
    edit_caps = [
        ["Edit Type", "Tool", "Description", "Est. Time"],
        ["Color Grading", "FFmpeg LUTs", "Apply 3D Look-Up Tables matching trend palette: warm film, moody blue, Y2K vivid, soft vintage", "2–5 sec"],
        ["Filter Overlay", "Pillow", "Grain texture, vignette edges, light leak, halation effects popular in current aesthetics", "1–3 sec"],
        ["Caption Burn", "FFmpeg drawtext", "Overlay trend-style text with brand font, position, color, and opacity onto image or video", "1–4 sec"],
        ["Aspect Ratio", "FFmpeg scale+pad", "Smart crop or letterbox to 9:16 (Reels/TikTok), 1:1 (Feed), 4:5 (Portrait feed)", "2–8 sec"],
        ["Brightness/Contrast", "Pillow", "Match luminance profile of trending aesthetic; apply curves adjustment", "1 sec"],
        ["Saturation/Tone", "Pillow ImageEnhance", "Desaturate for moody look; boost for vibrant Y2K aesthetic", "1 sec"],
        ["Video Fade", "FFmpeg", "Fade-in / fade-out transitions for video clips", "2–5 sec"],
        ["Optimize & Compress", "FFmpeg", "H.264 MP4 at platform-optimal bitrate (8–12 Mbps for 1080p)", "5–15 sec"],
    ]
    story.append(std_table(edit_caps, [PAGE_W*0.18, PAGE_W*0.18, PAGE_W*0.50, PAGE_W*0.14]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Key FFmpeg Commands (Reference)", S["h2"]))
    ffmpeg_examples = [
        ("Apply LUT + resize to 9:16", 'ffmpeg -i input.mp4 -vf "lut3d=warm_film.cube,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:-1:-1" -c:v libx264 -crf 18 out.mp4'),
        ("Burn caption text", 'ffmpeg -i input.mp4 -vf "drawtext=text=\'Trending Now\':fontfile=brand.ttf:fontsize=48:fontcolor=white:x=(w-text_w)/2:y=h*0.85" out.mp4'),
        ("Fade in/out", 'ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=0.5,fade=t=out:st=4.5:d=0.5" out.mp4'),
        ("Convert to 1:1 square", 'ffmpeg -i input.mp4 -vf "crop=min(iw\\,ih):min(iw\\,ih),scale=1080:1080" out.mp4'),
    ]
    for desc, cmd in ffmpeg_examples:
        story.append(Paragraph(f"<b>{desc}:</b>", S["h4"]))
        ct = Table([[Paragraph(cmd, S["code"])]], colWidths=[PAGE_W])
        ct.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),YC_BG_CODE),
            ("LEFTPADDING",(0,0),(-1,-1),8),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("BOX",(0,0),(-1,-1),0.5,YC_RULE),
        ]))
        story.append(ct)
        story.append(Spacer(1, 0.15*cm))

    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Phase 2 AI Upgrades (API-Based, Pay-Per-Use)", S["h2"]))
    story.append(Paragraph(
        "These capabilities are NOT in the MVP. They are integrated in Phase 2 once FFmpeg/Pillow "
        "edits are proven insufficient for user retention. Always API-based — never self-hosted GPU.", S["body"]))
    ai_caps = [
        ["Capability", "API", "Cost Estimate", "Phase"],
        ["AI Style Transfer", "Replicate (SDXL Style)", "~$0.05–0.15 per image", "Phase 2"],
        ["Background Removal", "Replicate (RMBG-2.0)", "~$0.005 per image", "Phase 2"],
        ["Auto Subtitles", "OpenAI Whisper API", "~$0.006 per minute audio", "Phase 2"],
        ["AI Video Generation", "Google Veo 3 API", "~$0.35–0.70 per 5-sec clip", "Phase 3"],
        ["Video Enhancement", "Topaz Video AI API", "~$0.02–0.10 per minute", "Phase 3"],
        ["Face Enhancement", "CodeFormer via Replicate", "~$0.01–0.03 per image", "Phase 3"],
    ]
    story.append(std_table(ai_caps, [PAGE_W*0.28, PAGE_W*0.28, PAGE_W*0.22, PAGE_W*0.22]))
    story.append(PageBreak())

    # ── SECTION 07: TREND ENGINE ─────────────────────────────────────────────
    story.append(Paragraph("07 — Trend Intelligence Engine", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "The trend intelligence system is the product's competitive moat. Editing quality is commodity — "
        "FFmpeg filters are free and open source. What competitors cannot easily replicate is a proprietary "
        "trend detection and scoring system trained on thousands of data points from real user engagement. "
        "We start simple and compound.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Trend Score Formula", S["h2"]))
    formula_text = "trend_score = (engagement_velocity × 0.35) + (hashtag_growth × 0.25) + (audio_reuse × 0.20) + (caption_similarity × 0.20)"
    ct = Table([[Paragraph(formula_text, ParagraphStyle("formula",
        fontName="Courier-Bold", fontSize=9, textColor=YC_DARK, leading=14))
    ]], colWidths=[PAGE_W])
    ct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), YC_BG_SOFT),
        ("LEFTPADDING",(0,0),(-1,-1),12),
        ("TOPPADDING",(0,0),(-1,-1),10),
        ("BOTTOMPADDING",(0,0),(-1,-1),10),
        ("LINEBEFORE",(0,0),(-1,-1),4,YC_ORANGE),
        ("BOX",(0,0),(-1,-1),0.5,YC_RULE),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.2*cm))

    score_data = [
        ["Signal", "Weight", "Source", "How Measured"],
        ["Engagement Velocity", "35%", "Platform metrics", "Likes + shares per hour / follower count"],
        ["Hashtag Growth", "25%", "Hashtag tracking", "% increase in hashtag uses over 24h window"],
        ["Audio Reuse", "20%", "Audio fingerprint", "Number of videos using same audio track in 48h"],
        ["Caption Similarity", "20%", "NLP / pattern match", "Semantic similarity of captions to template patterns"],
    ]
    story.append(std_table(score_data, [PAGE_W*0.25, PAGE_W*0.10, PAGE_W*0.25, PAGE_W*0.40]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("MVP Trend Categories (Hardcoded — Phase 1)", S["h2"]))
    story.append(Paragraph(
        "For the MVP, we hardcode 5–8 trend categories manually curated by the team. Each category "
        "maps directly to an FFmpeg LUT file and Pillow settings JSON. This gives immediate value "
        "without requiring a scraping infrastructure:", S["body"]))
    cat_data = [
        ["Category", "Aesthetic", "LUT File", "Pillow Settings", "Typical Platform"],
        ["Soft Moody Film", "Low saturation, warm shadows, grain", "soft_film.cube", "sat:0.7, grain:0.4, vignette:0.3", "Instagram"],
        ["Y2K Vivid", "High saturation, cyan/magenta boost", "y2k_vivid.cube", "sat:1.6, brightness:1.1, sharpen:1.2", "TikTok"],
        ["Minimal Clean", "Bright, high contrast, desaturated", "minimal_clean.cube", "sat:0.5, contrast:1.3, brightness:1.15", "Both"],
        ["Golden Hour", "Warm orange tones, soft highlights", "golden_hour.cube", "sat:1.1, warmth:+30, vignette:0.2", "Instagram"],
        ["Dark Academia", "Cool shadows, muted colors, vintage", "dark_academia.cube", "sat:0.6, coolness:+20, grain:0.5", "TikTok"],
    ]
    story.append(std_table(cat_data, [PAGE_W*0.18, PAGE_W*0.25, PAGE_W*0.18, PAGE_W*0.25, PAGE_W*0.14]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Phase 2 — Automated Trend Ingestion", S["h2"]))
    story.append(Paragraph(
        "In Phase 2, a Celery beat scheduler runs trend ingestion every 6 hours. We use a combination "
        "of lightweight scrapers (Instagram Explore, TikTok trending page) and official APIs where "
        "available. The scoring formula is applied automatically and results stored with a 72-hour TTL.", S["body"]))

    story.append(Paragraph("Phase 3 — Embedding-Based Intelligence", S["h2"]))
    story.append(Paragraph(
        "In Phase 3, we introduce pgvector in Supabase to store aesthetic embeddings. Every trend "
        "is encoded as a vector using CLIP or a fine-tuned visual encoder. This enables: (1) semantic "
        "trend similarity search, (2) personalized trend recommendations per brand, (3) regional "
        "trend segmentation (Nepal trends differ from India trends), and (4) virality prediction "
        "models trained on our accumulated engagement data. This is the point where the data moat becomes unassailable.", S["body"]))
    story.append(PageBreak())

    # ── SECTION 08: SECURITY ─────────────────────────────────────────────────
    story.append(Paragraph("08 — Security & Infrastructure", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))

    sec_data = [
        ["Security Layer", "Implementation", "Why It Matters"],
        ["Authentication", "Supabase Auth JWT tokens on all API routes", "Prevents unauthorized API access"],
        ["Row Level Security", "Supabase RLS policies: users see only their data", "Database-level data isolation"],
        ["Signed Upload URLs", "Signed URLs for direct-to-storage uploads", "Backend never handles large file bytes"],
        ["FFmpeg Sandboxing", "Workers run in Docker containers with limited syscalls", "Prevents malicious media exploits"],
        ["Upload Validation", "MIME type check + magic byte verification + size limit", "Prevents malware disguised as media"],
        ["Rate Limiting", "10 edit jobs/min per user via FastAPI middleware", "Prevents API abuse and cost explosion"],
        ["Worker Isolation", "Celery workers run in separate containers", "Job failures don't crash the API"],
        ["Temp File Cleanup", "Workers delete temp files after job completion", "Prevents disk exhaustion and data leaks"],
        ["HTTPS Only", "Vercel + Railway enforce TLS, no HTTP fallback", "Encrypts all data in transit"],
        ["Environment Secrets", "All API keys in Railway/Vercel env vars, never in code", "No credential leakage in GitHub"],
        ["CORS", "FastAPI CORS middleware restricted to frontend origin", "Prevents cross-origin attacks"],
    ]
    story.append(std_table(sec_data, [PAGE_W*0.25, PAGE_W*0.42, PAGE_W*0.33]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Critical Rule: Never Proxy Media Through the Backend", S["h2"]))
    story.append(Paragraph(
        "Large media files (videos up to 500 MB) must NEVER pass through the FastAPI process. "
        "The backend generates signed URLs and clients upload/download directly to Supabase Storage. "
        "Violating this rule causes memory exhaustion, slow response times, and Railway cost spikes. "
        "This is the single most common mistake in media platform architecture.", S["body"]))
    story.append(PageBreak())

    # ── SECTION 09: MVP SPRINT ───────────────────────────────────────────────
    story.append(Paragraph("09 — MVP Sprint Plan (10 Days)", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Two engineers. Ten days. One working product with real users. This plan is aggressive but "
        "achievable if scope is ruthlessly defended. Every day has a specific deliverable. If a task "
        "is not done by end of day, it either gets cut or moved — never expanded.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    sprint_data = [
        ["Day", "YOU — Backend / Infra", "FRIEND — Frontend / UI", "✓ Deliverable"],
        ["1", "GitHub monorepo setup, .env structure, Docker Compose, CI via GitHub Actions, pre-commit hooks (black, isort)",
         "Next.js 14 scaffold, TypeScript, TailwindCSS, shadcn/ui setup, folder structure /app /components /lib /hooks",
         "Clean monorepo. Both devs run locally."],
        ["2", "Provision Supabase project. Write all SQLAlchemy models. Run Alembic migrations. Configure Supabase Auth JWT in FastAPI.",
         "Integrate Supabase Auth in Next.js. Build login + signup pages. Setup protected route middleware.",
         "Auth works end-to-end. DB tables created."],
        ["3", "FastAPI routes: /auth, /brand-kit CRUD, /trends (static seed data), /health. Freeze Pydantic schemas.",
         "API client layer (axios wrappers with JWT headers). Brand kit creation form UI (logo, colors, font).",
         "All API routes documented. Brand kit creation works."],
        ["4", "Mock trend data endpoint. Seed DB with 5 trend categories + LUT mappings. Build trend scoring stub.",
         "Sidebar navigation. Dashboard home with stats cards. Trend feed card grid. Asset gallery page.",
         "Full dashboard navigable with mock data."],
        ["5", "File upload endpoint: validate MIME + size. Generate signed Supabase Storage URL. Save media_asset to DB. Enqueue preprocessing.",
         "Upload UI: drag-and-drop zone, progress bar, file preview, metadata display.",
         "User can upload image/video. Asset visible in gallery."],
        ["6", "Image editing pipeline: FFmpeg LUT color grade + Pillow filters + caption burn. Wrap in Celery task.",
         "Edit preview UI: before/after slider. Trend style selector. Brand kit selector. Aspect ratio picker.",
         "Image editing pipeline functional end-to-end."],
        ["7", "Video editing pipeline: FFmpeg color grade + caption + aspect ratio resize + encode. Test with multiple formats.",
         "Video player component. Video preview before/after. Export format selector (MP4/JPG/PNG).",
         "Video editing pipeline functional. Full media type support."],
        ["8", "Celery + Upstash Redis integration. Convert all edit calls to async tasks. Implement /jobs/{id}/status polling endpoint.",
         "Job status polling (3s interval). Loading skeleton states. Toast notification on completion. Progress indicator.",
         "Async pipeline works. No blocking HTTP calls."],
        ["9", "Export endpoint: generate signed download URL from Supabase Storage. Rate limiting middleware (10 req/min/user).",
         "Export button + format selector. Download flow. Error boundary components. Responsive layout audit.",
         "Full export pipeline works. App is mobile-responsive."],
        ["10", "End-to-end integration bugs. Input validation on all endpoints. Basic analytics event logging (generation, export events).",
         "UI polish: empty states, error messages, loading skeletons. Final UX review walk-through.",
         "Bug-free MVP. Generation < 2 min confirmed."],
        ["11–12", "Deploy backend to Railway: configure env vars, Supabase URL, Redis URL. Deploy Celery worker as separate Railway service. Custom domain optional.",
         "Deploy frontend to Vercel: connect GitHub repo, set env vars (API URL, Supabase keys). Setup UptimeRobot monitor.",
         "Live production URLs. Smoke test passes."],
        ["13–14", "Analytics endpoint: log edit_jobs count, export count per user. Fix any production bugs found by beta users.",
         "In-app feedback button (Typeform link). Simple onboarding walkthrough for beta users. Loom demo video.",
         "5 beta users onboarded. First real feedback collected."],
    ]
    story.append(std_table(sprint_data, [0.65*cm, PAGE_W*0.30, PAGE_W*0.30, PAGE_W - 0.65*cm - PAGE_W*0.60]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Sprint Engineering Rules", S["h2"]))
    rules = [
        ("No Microservices", "Monolithic FastAPI only. Split later when you have actual scaling pain, not before."),
        ("No Self-Hosted AI", "Use Replicate or API-based models. Never manage GPU infrastructure in MVP."),
        ("No Premature Optimization", "Ship working code first. Profile and optimize in Phase 2."),
        ("Speed > Perfection", "A working ugly edit beats a perfect non-existent one every time."),
        ("2-Minute Hard Limit", "Every editing flow must complete in under 2 minutes. Non-negotiable."),
        ("Flag Blockers Fast", "If you're stuck > 2 hours, communicate immediately. Don't suffer in silence."),
        ("Validate on Day 13", "Beta users on Day 13–14 are the only true success metric."),
    ]
    rd = [["Rule", "Reasoning"]] + [[f"■ {r}", d] for r, d in rules]
    story.append(std_table(rd, [PAGE_W*0.30, PAGE_W*0.70]))
    story.append(PageBreak())

    # ── SECTION 10: COST BREAKDOWN ───────────────────────────────────────────
    story.append(Paragraph("10 — Cost Breakdown", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "Cost discipline is a survival skill for student-founded startups. Every dollar spent before "
        "product-market fit is a dollar that could fund another month of runway. The MVP runs on "
        "approximately $5–20/month — less than a Netflix subscription.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Phase 1 — MVP (Month 1–2)", S["h2"]))
    cost1 = [
        ["Service", "Plan", "Cost/Month", "Limit / Notes"],
        ["Supabase (DB + Auth + Storage)", "Free tier", "$0", "500 MB DB, 1 GB storage, 50K MAU — plenty for MVP"],
        ["Railway (FastAPI backend)", "Starter", "$5", "512 MB RAM, enough for FastAPI + 1 Celery worker"],
        ["Upstash (Redis)", "Free tier", "$0", "10,000 commands/day — enough for MVP job queue"],
        ["Vercel (Next.js frontend)", "Hobby", "$0", "Free for personal projects, auto-deploy from GitHub"],
        ["UptimeRobot (monitoring)", "Free", "$0", "5-minute interval uptime checks"],
        ["GitHub Actions (CI/CD)", "Free", "$0", "2,000 minutes/month for free accounts"],
        ["Domain (Namecheap)", "Annual", "~$1.25", "$15/year billed annually"],
        ["Replicate API (optional AI)", "Pay-per-use", "$0–15", "Only if FFmpeg edits insufficient; ~$0.05 per AI call"],
        ["TOTAL", "", "$5–20/mo", "Less than a coffee a week"],
    ]
    story.append(std_table(cost1, [PAGE_W*0.32, PAGE_W*0.13, PAGE_W*0.13, PAGE_W*0.42],
                            header_bg=YC_ORANGE))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Phase 2 — Beta Growth (Month 3–4, ~20–50 users)", S["h2"]))
    cost2 = [
        ["Service", "Plan", "Cost/Month", "Trigger to Upgrade"],
        ["Supabase", "Pro ($25/mo)", "$25", "When DB hits 400 MB or auth exceeds 48K MAU"],
        ["Railway (Backend + Workers)", "Pro", "$20–40", "When CPU > 80% consistently for 48h+"],
        ["Upstash (Redis)", "Pay-as-you-go", "$2–5", "When queue exceeds 10K commands/day"],
        ["Vercel (Frontend)", "Hobby → Pro ($20)", "$0–20", "When bandwidth exceeds 100 GB/month"],
        ["Replicate API (AI edits)", "Higher volume", "$20–60", "When AI style transfer becomes default edit mode"],
        ["TOTAL", "", "$67–150/mo", "Upgrade only when metrics justify it"],
    ]
    story.append(std_table(cost2, [PAGE_W*0.32, PAGE_W*0.18, PAGE_W*0.13, PAGE_W*0.37]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Phase 3 — Scale (Month 5–6, SOTA AI Models, 100+ users)", S["h2"]))
    cost3 = [
        ["Service", "Plan", "Cost/Month", "Notes"],
        ["Supabase Pro", "Managed PostgreSQL", "$25", "pgvector enabled for embeddings"],
        ["Railway Pro (2+ workers)", "Multiple services", "$40–80", "Horizontal Celery worker scaling"],
        ["Cloudflare R2 (overflow storage)", "Usage-based", "$5–15", "If Supabase Storage limits hit"],
        ["Google Veo 3 API", "Per video generated", "$50–200", "$0.35–0.70 per 5-sec clip; only on-demand"],
        ["OpenAI Whisper API", "Per minute audio", "$10–30", "Auto-subtitles for video content"],
        ["Replicate (style transfer)", "Volume", "$30–100", "Background removal + AI style edits"],
        ["Clerk (Auth upgrade)", "Pro if needed", "$25", "Only if Supabase Auth limits hit"],
        ["CDN / Bandwidth", "Cloudflare", "$0–10", "Cloudflare proxy is free, R2 egress is free"],
        ["TOTAL", "", "$185–485/mo", "Covered by ~20–30 paying users at $15–20/mo"],
    ]
    story.append(std_table(cost3, [PAGE_W*0.32, PAGE_W*0.20, PAGE_W*0.13, PAGE_W*0.35]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Golden Rule: Never Upgrade Before the Metric", S["h2"]))
    story.append(Paragraph(
        "Do not spend money on infrastructure before 50+ active users. Do not upgrade Supabase "
        "until DB is over 400 MB. Do not add Railway workers until CPU stays above 80% for 48+ hours. "
        "Do not use expensive AI APIs until deterministic FFmpeg edits are proven insufficient. "
        "Every premature infrastructure spend is runway burned before product-market fit.", S["body"]))
    story.append(PageBreak())

    # ── SECTION 11: METRICS ──────────────────────────────────────────────────
    story.append(Paragraph("11 — Success Metrics & KPIs", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))

    story.append(mini_metrics(S, [
        ("<b>&lt;2</b> min", "Max Edit Time"),
        ("<b>5+</b>", "Beta Users Day 14"),
        ("<b>&lt;10%</b>", "Job Failure Rate"),
        ("<b>&gt;98%</b>", "Uptime Target"),
    ]))
    story.append(Spacer(1, 0.3*cm))

    kpi_data = [
        ["Metric", "Phase 1 Target", "Phase 2 Target", "Phase 3 Target", "How to Measure"],
        ["Edit completion time", "< 2 minutes", "< 90 seconds", "< 45 seconds", "Celery task duration logging"],
        ["Active beta users", "5 brands/creators", "20–30 users", "100+ users", "Daily active users in analytics table"],
        ["Daily edits generated", "Team internal use", "50+ edits/day", "500+ edits/day", "COUNT(edit_jobs) per day"],
        ["Job failure rate", "< 10%", "< 3%", "< 1%", "COUNT(status=failed)/COUNT(total)"],
        ["Deployment uptime", "> 98%", "> 99.5%", "> 99.9%", "UptimeRobot alerts"],
        ["User retention (W2)", "N/A", "> 60% return", "> 75% return", "Users active in week 2 / week 1"],
        ["Willingness to pay", "Qualitative signal", "1–3 paying users", "20+ paying users", "Stripe conversion rate"],
        ["Cost per edit", "< $0.10", "< $0.05", "< $0.02", "Monthly infra cost / total edits"],
        ["Engagement lift", "N/A (track manually)", "2–3x vs pre-tool", "3–5x vs baseline", "User-reported analytics input"],
    ]
    story.append(std_table(kpi_data, [PAGE_W*0.22, PAGE_W*0.16, PAGE_W*0.16, PAGE_W*0.16, PAGE_W*0.30]))
    story.append(PageBreak())

    # ── SECTION 12: SCALING ROADMAP ──────────────────────────────────────────
    story.append(Paragraph("12 — Scaling Roadmap — Phase 2 & Beyond", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))

    phases = [
        ("Phase 1 — MVP (Days 1–14)", "Ship the core loop", YC_ORANGE, [
            "Upload → Detect → Edit → Export → Analyze functional",
            "5 hardcoded trend categories with LUT mappings",
            "Deterministic editing: FFmpeg + Pillow (zero AI cost)",
            "Supabase DB + Auth + Storage fully integrated",
            "5 beta users editing daily by Day 14",
            "Deployed to Vercel + Railway with CI/CD",
        ]),
        ("Phase 2 — Automation (Weeks 3–6)", "Automate trends + improve quality", YC_GREEN, [
            "Automated trend ingestion via Celery beat (every 6h)",
            "Hashtag and audio trend scraping pipeline",
            "Improved prompt engineering for AI-assisted edits",
            "Analytics dashboard: engagement per trend style",
            "20–30 active beta users; early revenue signal ($10–15/mo)",
            "Queue optimization: target < 90s edit time",
            "Publishing workflow: export + platform guide",
        ]),
        ("Phase 3 — Intelligence (Month 2–3)", "Build the defensible moat", YC_BLUE, [
            "pgvector in Supabase: trend aesthetic embeddings",
            "CLIP-based visual similarity search for trends",
            "Personalized trend recommendations per brand",
            "Regional trend segmentation: Nepal vs India vs SE Asia",
            "Virality prediction model (trained on our engagement data)",
            "AI style transfer via Replicate (optional upgrade path)",
            "Background removal + auto-subtitles via API",
        ]),
        ("Phase 4 — Scale & Monetize (Month 4–6)", "Build the business", c("#8800CC"), [
            "Stripe subscription billing: Free / Starter $10 / Pro $20",
            "Rate limiting and quota enforcement per tier",
            "Multi-brand support and team collaboration (Pro tier)",
            "Horizontal Celery worker scaling on Railway",
            "Observability stack: Sentry + Datadog or Grafana",
            "100+ active creators, first recurring revenue",
            "Creator marketplace foundations (Phase 5 preview)",
        ]),
        ("Phase 5 — Platform (Month 6+)", "Become infrastructure", c("#004488"), [
            "Creator marketplace: sell preset packs and brand kits",
            "B2B API: agencies integrate Syntro into their workflow",
            "White-label solution for social media agencies",
            "Regional expansion: dedicated trend models per country",
            "Acquisition potential from trend analytics companies",
            "$500K+ ARR target; Series A readiness",
        ]),
    ]

    for phase_name, tagline, color, bullets in phases:
        header = Table([[
            Paragraph(f"<font color='white'><b>{phase_name}</b></font>", S["body_left"]),
            Paragraph(f"<font color='white'>{tagline}</font>", S["small"]),
        ]], colWidths=[PAGE_W*0.6, PAGE_W*0.4])
        header.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),color),
            ("LEFTPADDING",(0,0),(-1,-1),10),
            ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,0),(-1,-1),7),
            ("BOTTOMPADDING",(0,0),(-1,-1),7),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ]))
        story.append(header)
        brows = []
        for i in range(0, len(bullets), 2):
            row = [Paragraph(f"• {bullets[i]}", S["small"])]
            if i+1 < len(bullets):
                row.append(Paragraph(f"• {bullets[i+1]}", S["small"]))
            else:
                row.append(Paragraph("", S["small"]))
            brows.append(row)
        bt = Table(brows, colWidths=[PAGE_W*0.50, PAGE_W*0.50])
        bt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),YC_BG_SOFT),
            ("LEFTPADDING",(0,0),(-1,-1),10),
            ("RIGHTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,0),(-1,-1),4),
            ("BOTTOMPADDING",(0,0),(-1,-1),4),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("BOX",(0,0),(-1,-1),0.4,YC_RULE),
        ]))
        story.append(bt)
        story.append(Spacer(1, 0.2*cm))

    story.append(PageBreak())

    # ── SECTION 13: SOTA MODELS ──────────────────────────────────────────────
    story.append(Paragraph("13 — SOTA Video & AI Model Integration", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        "This section covers our strategy for integrating state-of-the-art generative AI models "
        "as the product scales. The core principle: use APIs, never self-host. A student team "
        "cannot manage GPU infrastructure. Pay-per-use APIs give access to the best models without "
        "DevOps overhead. We integrate SOTA only when deterministic editing is proven insufficient.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Why API-First for AI Models", S["h2"]))
    story.append(Paragraph(
        "Running SOTA video generation models (Veo 3, Wan 2.1, Kling 3.0) requires H100 GPUs at "
        "$2–8/hour per GPU. For a 5-second video clip, you might need 30–120 seconds of GPU time. "
        "Self-hosting at any reasonable scale costs $3,000–15,000/month before break-even. "
        "Google Veo 3 API charges ~$0.35–0.70 per 5-second clip. At 100 clips/day, that's "
        "$35–70/day — still affordable. The API model wins at every scale until you exceed 10,000 "
        "clips/day, at which point you negotiate enterprise GPU contracts.", S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("SOTA Model Evaluation Matrix", S["h2"]))
    model_data = [
        ["Model", "Provider", "API Available", "Cost/Output", "Best For", "Integration Phase"],
        ["Veo 3", "Google DeepMind", "Yes (Vertex AI)", "$0.35–0.70/5s clip", "Cinematic video generation", "Phase 3"],
        ["Wan 2.1", "Alibaba Cloud", "Yes (via Replicate)", "$0.05–0.15/clip", "Cost-effective video gen", "Phase 3"],
        ["Kling 3.0", "Kuaishou", "Yes (kling.ai API)", "$0.10–0.30/clip", "High quality video gen", "Phase 3"],
        ["Flux Schnell", "Black Forest Labs", "Yes (Replicate/fal.ai)", "$0.003/image", "Fast image generation", "Phase 2"],
        ["SDXL", "Stability AI", "Yes (Replicate)", "$0.005/image", "Style transfer, quality images", "Phase 2"],
        ["Whisper v3", "OpenAI", "Yes (OpenAI API)", "$0.006/min audio", "Auto-subtitles for video", "Phase 2"],
        ["RMBG-2.0", "BRIA AI", "Yes (Replicate)", "$0.005/image", "Background removal", "Phase 2"],
        ["Claude 3.5 Sonnet", "Anthropic", "Yes", "$3/M input tokens", "Caption generation, trend copy", "Phase 2"],
        ["Gemini Flash 2.0", "Google", "Yes", "$0.075/M tokens", "Fast caption + trend description", "Phase 2"],
    ]
    story.append(std_table(model_data, [PAGE_W*0.12, PAGE_W*0.16, PAGE_W*0.10, PAGE_W*0.14, PAGE_W*0.26, PAGE_W*0.14],
                            header_bg=YC_DARK))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("SOTA Video Pipeline Architecture (Phase 3)", S["h2"]))
    story.append(Paragraph(
        "When we integrate video generation, the pipeline extends the existing editing pipeline "
        "with an optional generation step. The user can choose: (A) edit their existing video, "
        "or (B) generate a trend-matching video clip from a text prompt + brand kit, then apply "
        "editing. Option B is always more expensive and slower — it's a premium upsell.", S["body"]))

    video_pipeline = [
        ["Step", "Option A (Edit)", "Option B (Generate + Edit)", "Tool"],
        ["1", "User uploads existing video", "User inputs prompt + selects trend", "Next.js UI"],
        ["2", "Preprocess: extract metadata", "Build optimized prompt with brand context + trend keywords", "FastAPI service"],
        ["3", "Skip generation", "Call Veo 3 / Kling API: generate 5-sec clip matching trend aesthetic", "Veo 3 / Kling API"],
        ["4", "Apply color grade (LUT)", "Apply color grade to generated clip", "FFmpeg"],
        ["5", "Apply filter overlay", "Apply filter overlay", "Pillow"],
        ["6", "Burn captions with brand font", "Burn trend-style captions", "FFmpeg drawtext"],
        ["7", "Resize to target aspect ratio", "Resize to 9:16", "FFmpeg"],
        ["8", "Optimize + upload to storage", "Optimize + upload to storage", "FFmpeg + Supabase Storage"],
        ["9", "User previews + exports", "User previews + exports", "Next.js"],
    ]
    story.append(std_table(video_pipeline, [0.6*cm, PAGE_W*0.28, PAGE_W*0.38, PAGE_W - 0.6*cm - PAGE_W*0.66]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("AI-Powered Caption Generation (Phase 2)", S["h2"]))
    story.append(Paragraph(
        "Instead of users writing captions manually, we use Claude 3.5 Haiku or Gemini Flash to "
        "generate trend-optimized captions based on: (1) the selected trend aesthetic, (2) the brand's "
        "tone from their brand kit, and (3) the platform (Instagram vs TikTok caption conventions differ). "
        "Cost: ~$0.001–0.005 per caption generation. High value, negligible cost.", S["body"]))

    caption_prompt = '''System: You generate short social media captions.
User: Generate a caption for a clothing brand Instagram post.
  Trend: Soft Moody Film (low saturation, vintage feel)
  Brand tone: Minimal, luxury
  Platform: Instagram
  Max length: 150 characters
  Include: 3 relevant hashtags

Output: "quiet luxury, redefined. ✦\\n\\n#softaesthetic #minimalstyle #slowfashion"'''
    ct = Table([[Paragraph(caption_prompt, S["code"])]], colWidths=[PAGE_W])
    ct.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),YC_BG_CODE),
        ("LEFTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
        ("BOX",(0,0),(-1,-1),0.5,YC_RULE),
    ]))
    story.append(ct)
    story.append(PageBreak())

    # ── SECTION 14: CTO NOTES ─────────────────────────────────────────────────
    story.append(Paragraph("14 — Engineering Rules & CTO Notes", S["h1"]))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))

    notes = [
        ("The Moat Is Trend Intelligence, Not Editing",
         "FFmpeg filters are free. Pillow is free. Anyone can copy your editing pipeline in a weekend. "
         "What they cannot copy is 12 months of accumulated engagement data showing exactly which trend "
         "aesthetics drive the most views for Nepali clothing brands in September. Build the analytics "
         "instrumentation from Day 1. Every engagement data point makes trend detection smarter. "
         "This data compound is the only defensible moat."),
        ("Editing Real Media Beats Generating Fake Media",
         "Brands want their actual products, their actual models, and their actual spaces in content. "
         "AI-generated images of generic clothing on generic people perform worse than a real product "
         "photo with a trend-optimized filter. This is not a philosophical choice — it is a product "
         "decision validated by engagement data. Editing user-owned media is the right call for this market."),
        ("FFmpeg First. Always.",
         "Do not reach for Replicate AI models until FFmpeg + Pillow edits are proven insufficient by user feedback. "
         "Deterministic edits are faster (< 30s vs 60–120s for AI), cheaper ($0 vs $0.05–0.70), and more "
         "predictable (no hallucinations, no prompt engineering required). AI generation is a Phase 2 "
         "upsell, not a Phase 1 requirement."),
        ("Ship in 10 Days or It Doesn't Matter",
         "The largest engineering mistake at this stage is overbuilding before validating demand. "
         "A working MVP that 5 real users touch in 10 days is worth more than a perfect platform "
         "that ships in 3 months to zero users. Speed of execution is the only metric that matters "
         "right now. 80% quality shipped beats 100% quality delayed every time."),
        ("Never Upgrade Infrastructure Before the Metric",
         "Railway, Supabase, and Upstash free tiers will handle your first 50 users without breaking a sweat. "
         "Don't upgrade to paid tiers before you hit the specific limit. Don't add Celery worker "
         "replicas before CPU is consistently above 80%. Premature infrastructure spend burns runway "
         "that should fund user acquisition."),
        ("The Student Budget Advantage",
         "Being a student team is actually an advantage: GitHub Education gives free Pro accounts and "
         "partner credits (Railway, Render, MongoDB Atlas). Apply for Google for Startups ($1,000–10,000 "
         "in GCP credits). Apply for AWS Activate ($5,000 credits). Apply for Anthropic startup credits. "
         "These programs can fund your entire Phase 2–3 infrastructure cost at zero cash spend."),
        ("Analytics Is the Flywheel",
         "Instrument every user action from Day 1: uploads, edits, exports, downloads. "
         "Even if users manually input their engagement data (likes, views, shares) for Phase 1, "
         "that data becomes the training signal for Phase 3 trend prediction models. "
         "The longer you wait to instrument, the longer the flywheel takes to spin up."),
        ("Communicate Blockers in Under 2 Hours",
         "A 2-person team with a 10-day deadline has zero margin for silent struggling. "
         "If either engineer is blocked for more than 2 hours, communicate immediately. "
         "Cut scope rather than miss the deadline. A delivered MVP with 80% of features "
         "beats a planned MVP with 100% of features that is never shipped."),
    ]

    for title, body in notes:
        nt = Table([
            [Paragraph(f"■ {title}", S["h3"])],
            [Paragraph(body, S["body_left"])],
        ], colWidths=[PAGE_W])
        nt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), YC_BG_SOFT),
            ("LEFTPADDING",(0,0),(-1,-1),12),
            ("RIGHTPADDING",(0,0),(-1,-1),12),
            ("TOPPADDING",(0,0),(-1,-1),8),
            ("BOTTOMPADDING",(0,0),(-1,-1),8),
            ("LINEBEFORE",(0,0),(-1,-1),3,YC_ORANGE),
            ("BOX",(0,0),(-1,-1),0.4,YC_RULE),
        ]))
        story.append(nt)
        story.append(Spacer(1, 0.2*cm))

    story.append(Spacer(1, 0.3*cm))
    story.append(OrangeLine(PAGE_W, 2))
    story.append(Spacer(1, 0.2*cm))

    closing = Table([[Paragraph(
        "The platform wins by being the fastest path from<br/>"
        "<font color='#FF6600'><b>Trend Emergence → Edited Content → Published → Engaged Audience</b></font><br/><br/>"
        "Build this. Ship in 10 days. Get 5 real users. Listen to them. Iterate.",
        ParagraphStyle("closing", fontName="Helvetica", fontSize=11, textColor=YC_DARK,
                       leading=18, alignment=TA_CENTER))
    ]], colWidths=[PAGE_W])
    closing.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), YC_BG_SOFT),
        ("LEFTPADDING",(0,0),(-1,-1),20),
        ("RIGHTPADDING",(0,0),(-1,-1),20),
        ("TOPPADDING",(0,0),(-1,-1),16),
        ("BOTTOMPADDING",(0,0),(-1,-1),16),
        ("BOX",(0,0),(-1,-1),0.5,YC_ORANGE),
    ]))
    story.append(closing)

    # ── BUILD ─────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=on_first_page, onLaterPages=on_page)
    print(f"PDF written to {out}")
    return out

if __name__ == "__main__":
    build()