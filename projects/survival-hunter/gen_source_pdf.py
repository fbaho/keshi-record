#!/usr/bin/env python3
"""Generate source code PDF for software copyright application."""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os, math

# Register a CJK-capable font for the header
# Use system font on macOS
cjk_font_paths = [
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
]
cjk_font_name = None
for fp in cjk_font_paths:
    if os.path.exists(fp):
        try:
            pdfmetrics.registerFont(TTFont('CJK', fp, subfontIndex=0))
            cjk_font_name = 'CJK'
            break
        except:
            try:
                pdfmetrics.registerFont(TTFont('CJK', fp))
                cjk_font_name = 'CJK'
                break
            except:
                pass

# Also try STSong
if not cjk_font_name:
    try:
        pdfmetrics.registerFont(TTFont('CJK', '/System/Library/Fonts/Supplemental/Songti.ttc', subfontIndex=0))
        cjk_font_name = 'CJK'
    except:
        pass

SOFTWARE_NAME = "秦始皇归来 V1.0"
SOURCE_FILE = os.path.join(os.path.dirname(__file__), 'index.html')
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '秦始皇归来_源代码.pdf')

# Page layout
PAGE_W, PAGE_H = A4  # 595 x 842 points
MARGIN_LEFT = 40
MARGIN_RIGHT = 40
MARGIN_TOP = 55
MARGIN_BOTTOM = 40
FONT_SIZE = 7.5
LINE_HEIGHT = 9.5
CHARS_PER_LINE = 98  # max chars per line before wrapping

def read_source(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def wrap_line(line, max_chars):
    """Wrap a long line into multiple lines."""
    if len(line) <= max_chars:
        return [line]
    lines = []
    while len(line) > max_chars:
        lines.append(line[:max_chars])
        line = line[max_chars:]
    if line:
        lines.append(line)
    return lines

def generate_pdf():
    source = read_source(SOURCE_FILE)
    raw_lines = source.split('\n')
    
    # Wrap long lines and add line numbers
    numbered_lines = []
    for i, line in enumerate(raw_lines, 1):
        wrapped = wrap_line(line, CHARS_PER_LINE - 6)  # -6 for line number prefix
        for j, wl in enumerate(wrapped):
            if j == 0:
                numbered_lines.append(f"{i:4d}  {wl}")
            else:
                numbered_lines.append(f"      {wl}")
    
    # Calculate pages
    usable_height = PAGE_H - MARGIN_TOP - MARGIN_BOTTOM
    lines_per_page = int(usable_height / LINE_HEIGHT)
    print(f"Total lines: {len(numbered_lines)}, Lines per page: {lines_per_page}")
    
    total_pages = math.ceil(len(numbered_lines) / lines_per_page)
    print(f"Total pages: {total_pages}")
    
    # Software copyright rule: if total > 60 pages, submit first 30 + last 30
    # If total <= 60, submit all
    if total_pages > 60:
        page_indices = list(range(30)) + list(range(total_pages - 30, total_pages))
        print(f"Submitting first 30 + last 30 = {len(page_indices)} pages")
    else:
        page_indices = list(range(total_pages))
        print(f"Submitting all {total_pages} pages (less than 60)")
    
    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)
    
    for page_idx in page_indices:
        start = page_idx * lines_per_page
        end = min(start + lines_per_page, len(numbered_lines))
        page_lines = numbered_lines[start:end]
        
        # Draw header
        if cjk_font_name:
            c.setFont(cjk_font_name, 9)
        else:
            c.setFont('Helvetica', 9)
        
        header_y = PAGE_H - 30
        c.drawString(MARGIN_LEFT, header_y, SOFTWARE_NAME)
        
        # Page number (sequential, not original page number)
        seq_num = page_indices.index(page_idx) + 1
        page_label = f"第 {seq_num} 页 / 共 {len(page_indices)} 页"
        c.drawRightString(PAGE_W - MARGIN_RIGHT, header_y, page_label)
        
        # Header line
        c.setStrokeColorRGB(0.6, 0.6, 0.6)
        c.setLineWidth(0.5)
        c.line(MARGIN_LEFT, header_y - 6, PAGE_W - MARGIN_RIGHT, header_y - 6)
        
        # Draw code lines
        c.setFont('Courier', FONT_SIZE)
        y = PAGE_H - MARGIN_TOP - 5
        for line in page_lines:
            c.drawString(MARGIN_LEFT, y, line)
            y -= LINE_HEIGHT
        
        # Footer line
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.setLineWidth(0.3)
        c.line(MARGIN_LEFT, MARGIN_BOTTOM - 5, PAGE_W - MARGIN_RIGHT, MARGIN_BOTTOM - 5)
        
        c.showPage()
    
    c.save()
    print(f"PDF saved to: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")

if __name__ == '__main__':
    generate_pdf()
