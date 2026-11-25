#!/usr/bin/env python3
"""Generate a genuine ArchiMate capability-model SVG for ARC-001-BPCM.
Each L2 capability element carries the REAL ArchiMate capability corner icon
(extracted from plantuml.jar sprites/archimate/strategy-capability.svg); the
C3.4 gap element carries the real gap icon (gap-filled.svg).
"""
import html

# --- genuine ArchiMate icon path data (from plantuml.jar sprites) ---
# capability icon: drawn in local coords ~x=40..60,y=80..100; normalize via translate(-40.073,-80.025)
CAP_D = ("m51.99 82.389a0.50005 0.50005 0 0 0-0.50384 0.49971v4.5258l-4.5021-0.0217"
         "a0.50005 0.50005 0 0 0-0.50178 0.50023v4.5527h-4.5274a0.50005 0.50005 0 0 0"
         "-0.50023 0.50384l0.04703 4.9356a0.50005 0.50005 0 0 0 0.50023 0.49403h15.014"
         "a0.50005 0.50005 0 0 0 0.50023-0.50023l-0.02377-14.967a0.50005 0.50005 0 0 0"
         "-0.49816-0.50023zm0.49609 1.002 4.006 0.01964 0.0057 4.0271-4.0116-0.01964z"
         "m-5.0038 5.0038 4.0039 0.01964v4.0313h-4.0039zm5.0038 0.02326 4.006 0.01964"
         "v4.008h-4.006zm-10.027 5.0276h4.0235v3.9336h-3.9843zm5.0235 0h4.0039v3.9098"
         "h-4.0039zm5.0038 0h4.0215l0.0078 3.9336h-4.0292z")
GAP_D = ("m89.943 204.65a0.5 0.5 0 0 0-0.0217 0.01 0.5 0.5 0 0 0-0.01912-8e-3"
         "c-2.5971 0.0353-4.8062 1.6691-5.7004 3.9512l-3.0691-8e-3a0.5 0.5 0 0 0-0.5023"
         " 0.49816 0.5 0.5 0 0 0 0.50023 0.50178l2.774 7e-3c-0.08902 0.43017-0.13308"
         " 0.8759-0.12764 1.3327 0.0066 0.55221 0.08529 1.0874 0.22738 1.5958l-2.8717"
         "-8e-3a0.5 0.5 0 0 0-0.5023 0.50023 0.5 0.5 0 0 0 0.50023 0.49971l3.2499 9e-3"
         "c1.0104 2.1118 3.1796 3.5638 5.6699 3.5383 2.4331-0.0249 4.5303-1.4543 5.5273"
         "-3.5088l3.3771 9e-3a0.5 0.5 0 0 0 0.50178-0.49816 0.5 0.5 0 0 0-0.49971-0.50178"
         "l-2.9972-8e-3c0.15943-0.55793 0.24239-1.1471 0.2372-1.756-0.0034-0.40092"
         "-0.04466-0.79265-0.12092-1.172l2.8789 8e-3a0.5 0.5 0 0 0 0.50178-0.49971"
         "0.5 0.5 0 0 0-0.49971-0.50023l-3.1724-8e-3c-0.90295-2.3428-3.1871-4.0019"
         "-5.8415-3.9837zm-0.0021 0.99012a0.5 0.5 0 0 0 0.0098 0.01c2.0972-0.0144 3.9092"
         " 1.2048 4.7485 2.9807l-9.4139-0.0248c0.82764-1.728 2.5806-2.928 4.6302-2.9559"
         "a0.5 0.5 0 0 0 0.02532-0.01zm-5.0131 3.9646 10.124 0.0269c0.09143 0.37993"
         " 0.14121 0.77648 0.14469 1.1844 0.0052 0.61074-0.09414 1.1974-0.28164 1.743"
         "l-9.8655-0.0258c-0.17077-0.50619-0.26613-1.0479-0.27285-1.6118-0.0054-0.45442"
         " 0.04721-0.89555 0.1509-1.3167zm0.58394 3.9295 8.9359 0.0238c-0.90262 1.4916"
         "-2.5336 2.4928-4.409 2.512-1.9232 0.0196-3.6088-0.99917-4.5269-2.5358z")

def icon(path_d, norm_translate, x, y, size, color="#000"):
    """Embed an ArchiMate icon (local ~20px space) at (x,y) scaled to `size` px."""
    sc = size/20.0
    tx, ty = norm_translate
    return (f'<g transform="translate({x},{y}) scale({sc:.4f})">'
            f'<g transform="translate({tx},{ty})">'
            f'<path d="{path_d}" fill="{color}"/></g></g>')

# --- model data ---
# status: aligned(green) | attention(yellow) | focus(red)
STATUS = {
    "aligned":   {"zone":"#E8F5E9","box":"#FFFFFF","boxborder":"#66BB6A","icon":"#1B5E20","tag":"ALIGNED","tagbg":"#C8E6C9"},
    "attention": {"zone":"#FFFDE7","box":"#FFFFFF","boxborder":"#F9A825","icon":"#F57F17","tag":"ATTENTION","tagbg":"#FFF9C4"},
    "focus":     {"zone":"#FFEBEE","box":"#FFFFFF","boxborder":"#E53935","icon":"#B71C1C","tag":"TRANSFORMATION FOCUS","tagbg":"#FFCDD2"},
}
DOMAINS = [
    ("TTCM-01  Architecture & Technology Portfolio","aligned",["01.01  Tech Strategy","01.02  Architecture Management","01.03  Portfolio"]),
    ("TTCM-02  Portfolio & Work Management","aligned",["02.01  Demand","02.02  Product Management","02.03  Delivery Planning"]),
    ("TTCM-03  Design & Development","aligned",["03.01  Source / Build","03.02  Code Quality","03.03  DevEx / AI"]),
    ("TTCM-04  Testing & Quality","attention",["04.01  Test Management","04.02  Test Automation","04.03  Test Environments & Data"]),
    ("TTCM-05  Release & Deployment","aligned",["05.01  Release / Deployment","05.02  Infrastructure & Config"]),
    ("TTCM-06  Operations & Service Management","aligned",["06.01  Service Catalogue","06.02  Incident & Change","06.03  Configuration","06.04  Observability","06.05  AIOps","06.06  Cloud & Capacity","06.07  Resilience & Backup"]),
    ("TTCM-07  Security & Risk","aligned",["07.01  Identity & PAM","07.02  Threat Detection & Response","07.03  Protection & Vulnerability","07.04  Data Security & Risk"]),
    ("TTCM-08  AI, Data & Automation","focus",["08.01  Data & Integration","08.02  Workflow & Analytics","08.03  AI Governance & Ops   [GAP C3.4]"]),
    ("TTCM-09  Collaboration & Productivity","aligned",["09.01  Collaboration & Knowledge","09.02  Endpoint & Workplace"]),
    ("TTCM-10  IT Asset & Financial Management","attention",["10.01  Financial / FinOps","10.02  Asset & Licence","10.03  Contract & Supplier"]),
]

# --- layout constants ---
COLW   = 470          # width of one column zone
BOXW   = 430          # width of an L2 capability bar
BOXH   = 32           # height of an L2 capability bar
BOXGAP = 6
TITLEH = 34           # domain title band height
ZONE_PAD = 12
COL_GAP = 30
X0 = 20              # left margin
TOP = 70             # top margin (title area)

def zone_height(n_l2): return TITLEH + ZONE_PAD + n_l2*(BOXH+BOXGAP) + ZONE_PAD

# assign domains to two columns
left  = DOMAINS[:5]
right = DOMAINS[5:]

colw_width = COLW
left_x  = X0
right_x = X0 + COLW + COL_GAP

out = []
W = 2*COLW + COL_GAP + 2*X0 + 10

def esc(s): return html.escape(s)

def draw_domain(x, top, name, status, l2list):
    S = STATUS[status]
    h = zone_height(len(l2list))
    # zone background (rounded rect)
    out.append(f'<rect x="{x}" y="{top}" width="{COLW}" height="{h}" rx="10" ry="10" '
               f'fill="{S["zone"]}" stroke="{S["boxborder"]}" stroke-width="1.5"/>')
    # status tag pill at top-right of zone
    tag = S["tag"]
    tagw = 8 + len(tag)*6.2
    out.append(f'<rect x="{x+COLW-tagw-10}" y="{top+6}" width="{tagw}" height="16" rx="8" ry="8" fill="{S["tagbg"]}" stroke="{S["boxborder"]}" stroke-width="0.75"/>')
    out.append(f'<text x="{x+COLW-tagw/2-10}" y="{top+17}" font-size="8.5" font-weight="bold" fill="#333" text-anchor="middle">{esc(tag)}</text>')
    # domain title (ArchiMate capability-group label)
    out.append(f'<text x="{x+14}" y="{top+23}" font-size="15" font-weight="bold" fill="#212121">{esc(name)}</text>')
    # L2 capability bars
    y = top + TITLEH + ZONE_PAD
    for lbl in l2list:
        is_gap = "[GAP" in lbl
        out.append(f'<rect x="{x+ (COLW-BOXW)//2 }" y="{y}" width="{BOXW}" height="{BOXH}" rx="6" ry="6" '
                   f'fill="{S["box"]}" stroke="{S["boxborder"]}" stroke-width="1.2"/>')
        # genuine ArchiMate icon in top-left corner
        ix = x + (COLW-BOXW)//2 + 5
        iy = y + 5
        if is_gap:
            out.append(icon(GAP_D, (-79.965,-200.08), ix, iy, 22, color=S["icon"]))
            # red "GAP" annotation after label
            clean = lbl.replace("   [GAP C3.4]","")
            out.append(f'<text x="{ix+30}" y="{y+BOXH/2+5}" font-size="12.5" fill="#B71C1C" font-weight="bold">{esc(clean)}</text>')
            out.append(f'<text x="{x+(COLW-BOXW)//2+BOXW-8}" y="{y+BOXH/2+5}" font-size="11" fill="#B71C1C" font-weight="bold" text-anchor="end">GAP</text>')
        else:
            out.append(icon(CAP_D, (-40.073,-80.025), ix, iy, 22, color=S["icon"]))
            out.append(f'<text x="{ix+30}" y="{y+BOXH/2+5}" font-size="12.5" fill="#212121">{esc(lbl)}</text>')
        y += BOXH + BOXGAP
    return h

# title
out.append(f'<text x="{W/2}" y="28" font-size="19" font-weight="bold" fill="#111" text-anchor="middle">TTCM v1.3 &#8212; Australia Post Technology Capability Model</text>')
out.append(f'<text x="{W/2}" y="50" font-size="12.5" fill="#555" text-anchor="middle">ArchiMate capability view &#183; 10 L1 domains &#215; 33 L2 capability groups (86 L3 capabilities) &#183; status-coloured &#183; C3.4 = SPP headline gap</text>')

# left column
y = TOP
for name, status, l2 in left:
    h = draw_domain(left_x, y, name, status, l2)
    y += h + COL_GAP
# right column
y2 = TOP
for name, status, l2 in right:
    h = draw_domain(right_x, y2, name, status, l2)
    y2 += h + COL_GAP

max_bottom = max(y, y2)

# legend
ly = max_bottom + 16
out.append(f'<rect x="{X0}" y="{ly}" width="{2*COLW+COL_GAP}" height="58" rx="8" ry="8" fill="#FAFAFA" stroke="#999" stroke-width="1"/>')
out.append(f'<text x="{X0+14}" y="{ly+18}" font-size="12" font-weight="bold" fill="#333">Legend (ArchiMate capability icons from plantuml.jar ArchiMate-Strategy layer)</text>')
# three legend items
lx = X0 + 14
# aligned
out.append(f'<rect x="{lx}" y="{ly+28}" width="150" height="20" rx="4" ry="4" fill="#FFFFFF" stroke="#66BB6A" stroke-width="1.2"/>')
out.append(icon(CAP_D, (-40.073,-80.025), lx+5, ly+31, 16, color="#1B5E20"))
out.append(f'<text x="{lx+28}" y="{ly+42}" font-size="10.5" fill="#333">Aligned / mature</text>')
# attention
lx2 = lx + 170
out.append(f'<rect x="{lx2}" y="{ly+28}" width="210" height="20" rx="4" ry="4" fill="#FFFFFF" stroke="#F9A825" stroke-width="1.2"/>')
out.append(icon(CAP_D, (-40.073,-80.025), lx2+5, ly+31, 16, color="#F57F17"))
out.append(f'<text x="{lx2+28}" y="{ly+42}" font-size="10.5" fill="#333">Attention &#8212; gaps / decisions</text>')
# focus (gap)
lx3 = lx2 + 225
out.append(f'<rect x="{lx3}" y="{ly+28}" width="260" height="20" rx="4" ry="4" fill="#FFFFFF" stroke="#E53935" stroke-width="1.2"/>')
out.append(icon(GAP_D, (-79.965,-200.08), lx3+5, ly+31, 16, color="#B71C1C"))
out.append(f'<text x="{lx3+28}" y="{ly+42}" font-size="10.5" fill="#333">Transformation focus &#8212; SPP headline gap (C3.4)</text>')

H = ly + 58 + 20
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="DejaVu Sans, Arial, sans-serif" style="background:#FFFFFF;">\n'
       + "\n".join(out) + "\n</svg>")

out_path = "/home/terry/workspace/arckit/projects/001/diagrams/ARC-001-BPCM-archimate-capability-model.svg"
open(out_path,"w").write(svg)
print(f"Wrote {out_path}  ({W}x{H}, {len(out)} elements)")
