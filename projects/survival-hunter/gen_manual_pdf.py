#!/usr/bin/env python3
"""Generate software manual PDF for software copyright application."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white, grey
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image as RLImage, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ---- Font Registration ----
# Try to register CJK fonts available on macOS
font_registered = False
cjk_font_paths = [
    ('/System/Library/Fonts/STHeiti Light.ttc', '/System/Library/Fonts/STHeiti Medium.ttc'),
    ('/System/Library/Fonts/PingFang.ttc', '/System/Library/Fonts/PingFang.ttc'),
]

for light_path, bold_path in cjk_font_paths:
    if os.path.exists(light_path):
        try:
            pdfmetrics.registerFont(TTFont('CJK', light_path, subfontIndex=0))
            if os.path.exists(bold_path):
                try:
                    pdfmetrics.registerFont(TTFont('CJK-Bold', bold_path, subfontIndex=1))
                except:
                    try:
                        pdfmetrics.registerFont(TTFont('CJK-Bold', bold_path, subfontIndex=0))
                    except:
                        pass
            else:
                pdfmetrics.registerFont(TTFont('CJK-Bold', light_path, subfontIndex=0))
            font_registered = True
            break
        except:
            try:
                pdfmetrics.registerFont(TTFont('CJK', light_path))
                pdfmetrics.registerFont(TTFont('CJK-Bold', light_path))
                font_registered = True
                break
            except:
                pass

if not font_registered:
    # Fallback
    try:
        pdfmetrics.registerFont(TTFont('CJK', '/System/Library/Fonts/Supplemental/Songti.ttc', subfontIndex=0))
        pdfmetrics.registerFont(TTFont('CJK-Bold', '/System/Library/Fonts/Supplemental/Songti.ttc', subfontIndex=1))
    except:
        pdfmetrics.registerFont(TTFont('CJK', '/System/Library/Fonts/Helvetica.ttc'))
        pdfmetrics.registerFont(TTFont('CJK-Bold', '/System/Library/Fonts/Helvetica.ttc'))

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), '秦始皇归来_软件说明书.pdf')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), 'assets')

# ---- Styles ----
styles = getSampleStyleSheet()

style_title = ParagraphStyle('Title_CN', parent=styles['Title'],
    fontName='CJK-Bold', fontSize=28, leading=40, alignment=TA_CENTER,
    textColor=HexColor('#1a1a2e'), spaceAfter=20)

style_subtitle = ParagraphStyle('Subtitle_CN', parent=styles['Normal'],
    fontName='CJK', fontSize=14, leading=20, alignment=TA_CENTER,
    textColor=HexColor('#555555'), spaceAfter=10)

style_cover_info = ParagraphStyle('CoverInfo', parent=styles['Normal'],
    fontName='CJK', fontSize=12, leading=22, alignment=TA_CENTER,
    textColor=HexColor('#333333'))

style_h1 = ParagraphStyle('H1_CN', parent=styles['Heading1'],
    fontName='CJK-Bold', fontSize=18, leading=28, alignment=TA_LEFT,
    textColor=HexColor('#1a1a2e'), spaceBefore=20, spaceAfter=12,
    borderPadding=4, borderWidth=0, borderColor=HexColor('#f9a825'))

style_h2 = ParagraphStyle('H2_CN', parent=styles['Heading2'],
    fontName='CJK-Bold', fontSize=14, leading=22, alignment=TA_LEFT,
    textColor=HexColor('#2d2d44'), spaceBefore=14, spaceAfter=8)

style_h3 = ParagraphStyle('H3_CN', parent=styles['Heading3'],
    fontName='CJK-Bold', fontSize=12, leading=18, alignment=TA_LEFT,
    textColor=HexColor('#3d3d55'), spaceBefore=10, spaceAfter=6)

style_body = ParagraphStyle('Body_CN', parent=styles['Normal'],
    fontName='CJK', fontSize=10.5, leading=18, alignment=TA_JUSTIFY,
    textColor=HexColor('#222222'), spaceAfter=6, firstLineIndent=21)

style_body_noindent = ParagraphStyle('BodyNoIndent', parent=style_body,
    firstLineIndent=0)

style_bullet = ParagraphStyle('Bullet_CN', parent=styles['Normal'],
    fontName='CJK', fontSize=10.5, leading=17, alignment=TA_LEFT,
    textColor=HexColor('#222222'), spaceAfter=4,
    leftIndent=25, bulletIndent=12)

style_note = ParagraphStyle('Note_CN', parent=styles['Normal'],
    fontName='CJK', fontSize=9, leading=14, alignment=TA_LEFT,
    textColor=HexColor('#666666'), spaceAfter=4)

style_table_header = ParagraphStyle('TableHeader', parent=styles['Normal'],
    fontName='CJK-Bold', fontSize=9.5, leading=14, alignment=TA_CENTER,
    textColor=white)

style_table_cell = ParagraphStyle('TableCell', parent=styles['Normal'],
    fontName='CJK', fontSize=9.5, leading=14, alignment=TA_CENTER,
    textColor=HexColor('#222222'))

style_table_cell_left = ParagraphStyle('TableCellLeft', parent=style_table_cell,
    alignment=TA_LEFT)


def make_table(data, col_widths=None):
    """Create a styled table."""
    # Wrap all cells in Paragraphs
    wrapped = []
    for i, row in enumerate(data):
        wrapped_row = []
        for j, cell in enumerate(row):
            if i == 0:
                wrapped_row.append(Paragraph(str(cell), style_table_header))
            else:
                style = style_table_cell_left if (j == 0 or j == len(row)-1) and len(str(cell)) > 10 else style_table_cell
                wrapped_row.append(Paragraph(str(cell), style))
        wrapped.append(wrapped_row)
    
    t = Table(wrapped, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2d2d44')),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, 0), 'CJK-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9.5),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f5f5f8')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [HexColor('#f5f5f8'), HexColor('#eaeaf0')]),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#cccccc')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    return t


def header_footer(canvas_obj, doc):
    """Draw header and footer on each page."""
    canvas_obj.saveState()
    
    # Header
    canvas_obj.setFont('CJK', 8)
    canvas_obj.setFillColor(HexColor('#888888'))
    canvas_obj.drawString(40, A4[1] - 25, "秦始皇归来 V1.0 — 软件说明书")
    canvas_obj.drawRightString(A4[0] - 40, A4[1] - 25, f"第 {doc.page} 页")
    canvas_obj.setStrokeColor(HexColor('#cccccc'))
    canvas_obj.setLineWidth(0.5)
    canvas_obj.line(40, A4[1] - 30, A4[0] - 40, A4[1] - 30)
    
    # Footer
    canvas_obj.setFont('CJK', 8)
    canvas_obj.setFillColor(HexColor('#888888'))
    canvas_obj.drawCentredString(A4[0] / 2, 25, "秦始皇归来 软件著作权登记 — 软件说明书")
    canvas_obj.line(40, 35, A4[0] - 40, 35)
    
    canvas_obj.restoreState()


def build_manual():
    doc = SimpleDocTemplate(
        OUTPUT_FILE, pagesize=A4,
        leftMargin=40, rightMargin=40,
        topMargin=45, bottomMargin=45,
        title="秦始皇归来 软件说明书",
        author="开发者"
    )
    
    story = []
    
    # ========== 封面 ==========
    story.append(Spacer(1, 120))
    story.append(Paragraph("秦始皇归来", style_title))
    story.append(Spacer(1, 10))
    story.append(Paragraph("软件说明书", ParagraphStyle('CoverSub', parent=style_subtitle,
        fontSize=20, textColor=HexColor('#f9a825'))))
    story.append(Spacer(1, 60))
    
    cover_table_data = [
        ['软件名称', '秦始皇归来'],
        ['软件简称', '秦始皇归来'],
        ['版本号', 'V1.0'],
        ['软件开发完成日期', '2026年7月'],
        ['软件类型', '休闲生存类游戏（HTML5）'],
        ['运行平台', 'Web浏览器 / 移动端浏览器'],
        ['编程语言', 'HTML5 + JavaScript + Canvas 2D'],
    ]
    cover_table = Table(cover_table_data, colWidths=[140, 250])
    cover_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'CJK'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), HexColor('#555555')),
        ('TEXTCOLOR', (1, 0), (1, -1), HexColor('#222222')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, HexColor('#dddddd')),
    ]))
    
    story.append(cover_table)
    story.append(Spacer(1, 80))
    story.append(Paragraph("本说明书用于计算机软件著作权登记申请", style_note))
    story.append(PageBreak())
    
    # ========== 目录 ==========
    story.append(Paragraph("目 录", style_h1))
    story.append(Spacer(1, 10))
    
    toc_data = [
        ["第一章", "软件概述", "3"],
        ["第二章", "运行环境", "4"],
        ["第三章", "功能介绍", "5"],
        ["第四章", "操作方法", "7"],
        ["第五章", "游戏机制详解", "9"],
        ["第六章", "技术特点", "11"],
        ["第七章", "界面说明", "13"],
        ["第八章", "数据存储与安全", "15"],
    ]
    toc_table = Table(toc_data, colWidths=[60, 350, 50])
    toc_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'CJK'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#333333')),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, HexColor('#eeeeee')),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # ========== 第一章 软件概述 ==========
    story.append(Paragraph("第一章 软件概述", style_h1))
    
    story.append(Paragraph("1.1 软件简介", style_h2))
    story.append(Paragraph(
        "「秦始皇归来」是一款基于 HTML5 Canvas 技术开发的像素风格生存猎手类网页游戏。"
        "玩家扮演秦始皇角色，在一个充满各种怪物的战场地图中进行生存挑战。"
        "游戏采用 Roguelike 武器系统，玩家通过击杀怪物获取经验值，升级后从随机强化选项中选择一个来增强自身实力。"
        "游戏的核心规则极为硬核——玩家仅有 1 点生命值，被任何怪物碰到一次即死亡，"
        "因此玩家需要通过精准的走位、冲刺闪避和合理的武器搭配来尽可能长时间地生存下去。",
        style_body))
    
    story.append(Paragraph("1.2 开发背景", style_h2))
    story.append(Paragraph(
        "本软件由个人开发者独立开发完成，旨在探索 HTML5 Canvas 2D 渲染技术在实时游戏场景中的应用潜力。"
        "游戏融合了经典像素美术风格与现代 Roguelike 游戏机制，通过自动攻击系统让玩家专注于走位和策略决策，"
        "降低了操作门槛的同时保持了高度的紧张感和可玩性。"
        "游戏支持桌面端键盘操作和移动端触屏操作，实现了跨平台的游戏体验。",
        style_body))
    
    story.append(Paragraph("1.3 软件特点", style_h2))
    features = [
        "<b>硬核生存</b>：玩家仅 1 点生命值，一次碰撞即死亡，极致紧张感",
        "<b>Roguelike 武器系统</b>：26 种独特武器，3 大武器类型（投射、环绕、磁场），每次升级随机选择强化",
        "<b>动态难度曲线</b>：三阶段难度设计，3 分钟后进入指数级难度爆炸阶段",
        "<b>皇冠奖励系统</b>：撑过 4 分钟获得皇冠，此后每 5 秒额外获得一个皇冠",
        "<b>像素风格美术</b>：全部武器和角色均采用手绘像素精灵图，支持多帧动画",
        "<b>跨平台支持</b>：同时支持桌面端（WASD 键盘 + 空格冲刺）和移动端（虚拟摇杆 + 冲刺按钮）",
        "<b>实时小地图</b>：右下角显示战场全局态势，辅助玩家进行战术决策",
        "<b>本地存档</b>：使用 localStorage 保存最高分和皇冠记录，无需联网",
    ]
    for f in features:
        story.append(Paragraph(f"• {f}", style_bullet))
    
    story.append(PageBreak())
    
    # ========== 第二章 运行环境 ==========
    story.append(Paragraph("第二章 运行环境", style_h1))
    
    story.append(Paragraph("2.1 硬件环境", style_h2))
    hw_data = [
        ["项目", "最低配置", "推荐配置"],
        ["CPU", "双核 1.5GHz", "四核 2.0GHz 及以上"],
        ["内存", "1GB RAM", "2GB RAM 及以上"],
        ["显卡", "支持 HTML5 Canvas", "独立显卡或集成显卡"],
        ["屏幕", "720p 及以上", "1080p 及以上"],
        ["存储空间", "10MB", "20MB（含资源文件）"],
    ]
    story.append(make_table(hw_data, col_widths=[100, 180, 200]))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.2 软件环境", style_h2))
    sw_data = [
        ["项目", "要求"],
        ["操作系统", "Windows 7+ / macOS 10.12+ / Android 7.0+ / iOS 12+"],
        ["浏览器", "Chrome 80+ / Firefox 75+ / Safari 13+ / Edge 80+"],
        ["运行时", "无需安装额外运行时，纯浏览器执行"],
        ["网络", "首次加载需网络，加载后可离线运行"],
        ["依赖库", "无第三方依赖（纯原生 JavaScript）"],
    ]
    story.append(make_table(sw_data, col_widths=[120, 360]))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.3 文件结构", style_h2))
    story.append(Paragraph("软件部署后包含以下文件结构：", style_body_noindent))
    file_data = [
        ["文件路径", "说明", "大小"],
        ["index.html", "游戏主文件（HTML + CSS + JavaScript）", "约 120KB"],
        ["assets/bg.png", "战场背景图片", "约 200KB"],
        ["assets/player.png", "玩家角色精灵图（4帧动画）", "约 15KB"],
        ["assets/projectiles.png", "投射类武器精灵表", "约 40KB"],
        ["assets/orbitals.png", "环绕类武器精灵表", "约 25KB"],
        ["assets/fields.png", "磁场类武器精灵表", "约 20KB"],
        ["assets/[武器名].png", "各武器独立精灵图（4帧动画）", "各约 5-15KB"],
    ]
    story.append(make_table(file_data, col_widths=[160, 240, 80]))
    
    story.append(PageBreak())
    
    # ========== 第三章 功能介绍 ==========
    story.append(Paragraph("第三章 功能介绍", style_h1))
    
    story.append(Paragraph("3.1 核心游戏循环", style_h2))
    story.append(Paragraph(
        "游戏采用经典的生存游戏循环：玩家在地图中移动 → 怪物自动生成并追踪玩家 → "
        "武器自动攻击最近敌人 → 击杀怪物获得经验 → 经验满后升级 → 从随机强化中选择一个 → "
        "继续生存。随着时间推移，怪物数量和强度不断增加，最终玩家死亡后进入结算界面。",
        style_body))
    
    story.append(Paragraph("3.2 武器系统", style_h2))
    story.append(Paragraph(
        "游戏包含 3 大武器类型，共 26 种独特武器，每种武器拥有独立的名字、属性和像素贴图：",
        style_body_noindent))
    story.append(Spacer(1, 6))
    
    weapon_data = [
        ["武器类型", "数量", "攻击方式", "代表武器"],
        ["投射类", "13种", "自动瞄准最近敌人发射弹丸", "火焰花、凤凰之火、地狱烈焰"],
        ["环绕类", "7种", "围绕玩家旋转的近战武器", "龟壳、链球、银河之盾"],
        ["磁场类", "8种", "以玩家为中心的范围伤害场", "磁力环、超新星、黑洞光环"],
    ]
    story.append(make_table(weapon_data, col_widths=[80, 60, 180, 160]))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "每种武器在升级时可获得以下强化类型之一：伤害提升、数量增加、速度加快、穿透能力、散射增强、风暴模式等。"
        "武器拥有普通、稀有、史诗、传说四种稀有度，稀有度越高属性越强。"
        "玩家最多可同时持有 6 件武器，需要在升级时做出策略性取舍。",
        style_body))
    
    story.append(Paragraph("3.3 怪物系统", style_h2))
    monster_data = [
        ["怪物名称", "基础血量", "移动速度", "经验值", "特点"],
        ["史莱姆", "5", "1.0", "1", "基础怪物，数量最多"],
        ["蝙蝠", "1", "2.2", "1", "极快速度，一击必杀"],
        ["僵尸", "7", "1.3", "2", "中等血量，稳定威胁"],
        ["幽灵", "3", "1.8", "2", "较快速度，中等血量"],
        ["恶魔", "8", "1.6", "3", "高血量高速度，危险"],
        ["BOSS", "35", "0.8", "10", "定时出现，高奖励"],
    ]
    story.append(make_table(monster_data, col_widths=[70, 65, 70, 55, 150]))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "怪物分为普通怪和精英怪两种。精英怪拥有更高的属性和特殊外观，"
        "随时间推移出现概率从 0% 逐渐提升至 20%。BOSS 怪物每隔一段时间定时出现，"
        "击杀后获得大量经验奖励。",
        style_body))
    
    story.append(PageBreak())
    
    story.append(Paragraph("3.4 难度系统", style_h2))
    story.append(Paragraph(
        "游戏采用三阶段动态难度曲线，确保游戏体验从始至终保持张力：",
        style_body_noindent))
    story.append(Spacer(1, 6))
    
    diff_data = [
        ["阶段", "时间范围", "怪物血量", "出怪间隔", "出怪数量", "特点"],
        ["开局缓压", "0-20秒", "1.0x", "40-35秒", "1只", "让玩家熟悉操作"],
        ["压力上升", "20-80秒", "1.0-1.96x", "35-14秒", "1-2只", "逐渐增加压力"],
        ["喘息期", "80-180秒", "1.96-2.41x", "14-10秒", "2-4只", "武器成型期"],
        ["指数爆炸", "180秒+", "10^n倍/分钟", "10-4秒", "4-6只", "极限挑战"],
    ]
    story.append(make_table(diff_data, col_widths=[60, 70, 80, 70, 60, 90]))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "<b>3 分钟后的指数爆炸机制</b>是本游戏的核心特色：游戏开始 3 分钟后，"
        "所有怪物血量每 60 秒在上分钟基础上翻 10 倍（即第 4 分钟 10x，第 5 分钟 100x，第 6 分钟 1000x……），"
        "同时所有怪物移动速度 +1。这意味着游戏不可能无限进行下去，"
        "玩家必须在有限时间内尽可能多地获取击杀数和皇冠。",
        style_body))
    
    story.append(Paragraph("3.5 皇冠奖励系统", style_h2))
    story.append(Paragraph(
        "为激励玩家挑战极限生存时间，游戏设有皇冠奖励系统：",
        style_body_noindent))
    crown_data = [
        ["条件", "奖励"],
        ["存活超过 4 分钟", "获得第一个皇冠"],
        ["此后每存活 5 秒", "额外获得 1 个皇冠"],
        ["死亡时结算", "皇冠数量显示在结算界面并保存到本地"],
    ]
    story.append(make_table(crown_data, col_widths=[200, 280]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "皇冠数量实时显示在游戏 HUD 右上角，并在死亡结算界面以金色高亮显示，"
        "同时通过 localStorage 持久化保存，作为玩家长期成就的记录。",
        style_body))
    
    story.append(Paragraph("3.6 冲刺闪避系统", style_h2))
    story.append(Paragraph(
        "玩家拥有冲刺技能，按空格键（桌面端）或点击冲刺按钮（移动端）可向当前移动方向快速冲刺一段距离，"
        "冲刺期间拥有短暂的无敌帧（约 0.3 秒），可以穿过怪物而不受到伤害。"
        "冲刺冷却时间约为 2 秒，冷却完毕后冲刺按钮会发光提示。"
        "冲刺是游戏中最重要的生存技能，合理使用冲刺是在高密度怪物群中存活的关键。",
        style_body))
    
    story.append(Paragraph("3.7 连杀经验倍率系统", style_h2))
    story.append(Paragraph(
        "连续击杀怪物会触发连杀倍率，在限定时间内连续击杀越多，经验倍率越高。"
        "连杀倍率显示在 HUD 右上角，超时后倍率重置。这一机制鼓励玩家积极进攻而非单纯躲避。",
        style_body))
    
    story.append(PageBreak())
    
    # ========== 第四章 操作方法 ==========
    story.append(Paragraph("第四章 操作方法", style_h1))
    
    story.append(Paragraph("4.1 桌面端操作", style_h2))
    desktop_data = [
        ["操作", "按键", "说明"],
        ["移动", "W / A / S / D", "上下左右移动角色"],
        ["移动（备选）", "方向键 ↑↓←→", "与 WASD 等效"],
        ["冲刺闪避", "空格键 SPACE", "向移动方向冲刺，带无敌帧"],
        ["暂停", "P 键", "打开暂停面板，查看武器详情"],
        ["暂停（备选）", "点击 ⏸ 按钮", "左上角暂停按钮"],
        ["音乐开关", "点击 🔇/🔊 按钮", "左上角音乐控制"],
    ]
    story.append(make_table(desktop_data, col_widths=[100, 140, 240]))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.2 移动端操作", style_h2))
    mobile_data = [
        ["操作", "手势", "说明"],
        ["移动", "屏幕任意位置拖动", "虚拟摇杆，拖动方向即为移动方向"],
        ["冲刺闪避", "点击 ⚡ 按钮", "右下角冲刺按钮，带冷却动画"],
        ["暂停", "点击 ⏸ 按钮", "左上角暂停按钮"],
        ["升级选择", "点击卡片", "点击期望的强化选项卡片"],
    ]
    story.append(make_table(mobile_data, col_widths=[100, 160, 220]))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.3 游戏流程", style_h2))
    story.append(Paragraph("游戏完整流程如下：", style_body_noindent))
    flow_data = [
        ["步骤", "操作", "说明"],
        ["1", "打开游戏页面", "显示主菜单，展示游戏标题和规则提示"],
        ["2", "点击「开始狩猎」", "进入游戏，玩家出现在地图中央"],
        ["3", "移动并躲避怪物", "武器自动攻击，专注走位闪避"],
        ["4", "击杀怪物获取经验", "经验条满后弹出升级选择面板"],
        ["5", "选择强化", "从两张随机卡片中选择一个武器或强化"],
        ["6", "持续生存", "难度逐渐提升，3分钟后进入指数爆炸"],
        ["7", "死亡结算", "显示存活时间、击杀数、皇冠数"],
        ["8", "重新开始或返回主菜单", "可选择再来一局或返回主界面"],
    ]
    story.append(make_table(flow_data, col_widths=[50, 160, 270]))
    
    story.append(PageBreak())
    
    # ========== 第五章 游戏机制详解 ==========
    story.append(Paragraph("第五章 游戏机制详解", style_h1))
    
    story.append(Paragraph("5.1 经验与升级系统", style_h2))
    story.append(Paragraph(
        "玩家初始等级为 1 级，升级所需经验公式为：所需经验 = 20 + (等级-1) × (等级+3)。"
        "即第 1 级升第 2 级需要 20 经验，第 2 级升第 3 级需要 25 经验，第 3 级需要 32 经验，以此类推。"
        "不同怪物提供的经验值不同，从史莱姆的 1 点到 BOSS 的 10 点不等。"
        "升级时游戏暂停，弹出两张随机强化卡片供玩家选择。",
        style_body))
    
    story.append(Paragraph("5.2 武器伤害计算", style_h2))
    story.append(Paragraph(
        "每种武器有基础伤害值，投射类基础伤害为 3，环绕类为 5，磁场类为 4。"
        "每种具体武器在此基础上进行加成修正（部分武器有额外伤害加成或冷却缩减）。"
        "升级强化时可选择伤害提升，每次伤害提升增加固定数值。"
        "怪物的实际血量为：基础血量 × 难度倍率，其中难度倍率随时间增长。",
        style_body))
    
    story.append(Paragraph("5.3 怪物生成机制", style_h2))
    story.append(Paragraph(
        "怪物在玩家视野范围外的随机位置生成，朝玩家方向移动。"
        "生成间隔和单次生成数量均随时间动态调整：",
        style_body_noindent))
    spawn_data = [
        ["时间段", "生成间隔", "单次数量", "说明"],
        ["0-20秒", "40→35秒", "1只", "极缓开局，让玩家适应"],
        ["20-80秒", "35→14秒", "1→2只", "压力逐渐增加"],
        ["80-200秒", "14→10秒", "2→4只", "中期挑战"],
        ["200秒+", "10→4秒", "4→6只", "极限压力"],
    ]
    story.append(make_table(spawn_data, col_widths=[80, 90, 80, 210]))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "地图最大同时存在怪物数为 200 只，超出后不再生成新怪物。"
        "精英怪的出现概率随时间从 0% 增长至 20%，BOSS 每 90 秒（后期缩短至 40 秒）出现一次。",
        style_body))
    
    story.append(Paragraph("5.4 地图与障碍物", style_h2))
    story.append(Paragraph(
        "游戏地图大小为 4000×4000 像素，地图中随机分布约 45 个障碍物（砖块和管道）。"
        "障碍物具有碰撞体积，玩家和怪物均无法穿过，可以利用障碍物进行卡位和绕怪策略。"
        "玩家初始位置在地图正中央，周围 200 像素为安全区，不会生成障碍物。"
        "摄像机跟随玩家移动，右下角小地图显示全局态势。",
        style_body))
    
    story.append(Paragraph("5.5 无敌帧机制", style_h2))
    story.append(Paragraph(
        "冲刺期间玩家拥有约 0.3 秒的无敌帧，在此期间可以穿过怪物而不受到伤害。"
        "这是游戏中最重要的生存机制——在怪物密集时，合理利用冲刺无敌帧穿过怪物群是高级技巧。"
        "冲刺冷却时间约为 2 秒，冷却期间冲刺按钮显示半透明遮罩动画。",
        style_body))
    
    story.append(PageBreak())
    
    # ========== 第六章 技术特点 ==========
    story.append(Paragraph("第六章 技术特点", style_h1))
    
    story.append(Paragraph("6.1 纯 Canvas 2D 渲染", style_h2))
    story.append(Paragraph(
        "游戏完全基于 HTML5 Canvas 2D API 进行渲染，未使用任何第三方游戏引擎（如 Phaser、PixiJS 等）。"
        "所有图形绘制均通过 Canvas Context 的 drawImage、fillRect、arc 等原生方法实现。"
        "这种方案的优点是文件体积小、加载速度快、兼容性极佳，适合在各种设备和网络条件下运行。",
        style_body))
    
    story.append(Paragraph("6.2 精灵图动画系统", style_h2))
    story.append(Paragraph(
        "游戏采用精灵表（Sprite Sheet）技术实现角色和武器的多帧动画。"
        "每个精灵表包含 4 帧动画，通过 game.frame 计数器每 6 帧切换一次，实现流畅的动态效果。"
        "所有武器贴图均为 112×112 像素的像素风格手绘精灵，角色贴图为 64×64 像素。"
        "渲染时使用 imageSmoothingEnabled = false 确保像素风格的清晰度。",
        style_body))
    
    story.append(Paragraph("6.3 动态难度曲线算法", style_h2))
    story.append(Paragraph(
        "游戏使用多段函数实现动态难度调节，包含以下核心函数：",
        style_body_noindent))
    algo_data = [
        ["函数名", "功能", "公式"],
        ["diffSpawnInterval(t)", "出怪间隔", "分段线性递减，40→35→14→10→4秒"],
        ["diffSpawnBatch(t)", "单次出怪数", "分段递增，1→2→4→6只"],
        ["diffHpMult(t)", "怪物血量倍率", "3分钟后指数爆炸：10^(1+⌊(t-180)/60⌋)"],
        ["diffSpeedBonus(t)", "怪物速度加成", "3分钟后固定+1"],
        ["diffEliteChance(t)", "精英怪概率", "线性增长，0%→7%→20%"],
        ["diffBossInterval(t)", "BOSS间隔", "90秒→40秒递减"],
    ]
    story.append(make_table(algo_data, col_widths=[130, 100, 230]))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("6.4 高 DPI 屏幕适配", style_h2))
    story.append(Paragraph(
        "游戏通过 devicePixelRatio 检测实现高 DPI 屏幕（如 Retina 显示屏）的清晰渲染。"
        "Canvas 实际像素尺寸为 CSS 尺寸乘以 DPR，再通过 setTransform 缩放回 CSS 坐标系，"
        "确保在所有设备上渲染清晰且坐标一致。",
        style_body))
    
    story.append(Paragraph("6.5 触摸输入处理", style_h2))
    story.append(Paragraph(
        "移动端采用虚拟摇杆方案：玩家在屏幕任意位置按下并拖动，按下点即为摇杆中心，"
        "拖动方向和距离决定移动方向和速度。同时设置了 touch-action: none 和 -webkit-tap-highlight-color: transparent "
        "来消除移动端默认手势干扰。冲刺按钮位于右下角，带有冷却进度环动画。",
        style_body))
    
    story.append(Paragraph("6.6 粒子系统", style_h2))
    story.append(Paragraph(
        "游戏内置粒子系统用于击杀特效、伤害数字、经验获取等视觉反馈。"
        "最多同时存在 400 个粒子，超出后自动回收最早的粒子。"
        "粒子具有位置、速度、生命周期、颜色等属性，每帧更新后自动渲染。",
        style_body))
    
    story.append(Paragraph("6.7 摄像机震动效果", style_h2))
    story.append(Paragraph(
        "当玩家受到伤害（冲刺无敌帧外被碰到即死亡，因此主要用于 BOSS 出现等场景）"
        "或发生重大事件时，摄像机会产生随机震动效果，增强视觉冲击力。"
        "震动幅度通过 game.shake 值控制，每帧逐渐衰减。",
        style_body))
    
    story.append(PageBreak())
    
    story.append(Paragraph("6.8 小地图渲染", style_h2))
    story.append(Paragraph(
        "右下角小地图使用独立的 Canvas 元素渲染，以 120×120 像素的尺寸显示整个 4000×4000 地图的缩略图。"
        "小地图上显示玩家位置（白色点）、怪物位置（红色点）、障碍物（灰色块）等信息，"
        "帮助玩家了解战场全局态势，做出战术决策。",
        style_body))
    
    story.append(Paragraph("6.9 性能优化", style_h2))
    story.append(Paragraph(
        "为保证在低端设备上的流畅运行，游戏采用了以下性能优化措施：",
        style_body_noindent))
    opt_items = [
        "视锥剔除：仅渲染屏幕可见范围内的怪物和障碍物",
        "粒子池：限制最大粒子数，超出自动回收",
        "精灵图合并：同类武器使用同一精灵表，减少 drawImage 调用次数",
        "离屏 Canvas：地图纹理预渲染到离屏 Canvas，避免每帧重绘",
        "碰撞检测优化：矩形-圆形碰撞使用最近点算法，避免复杂计算",
        "requestAnimationFrame：使用浏览器原生动画帧调度，与显示器刷新率同步",
    ]
    for item in opt_items:
        story.append(Paragraph(f"• {item}", style_bullet))
    
    # ========== 第七章 界面说明 ==========
    story.append(PageBreak())
    story.append(Paragraph("第七章 界面说明", style_h1))
    
    story.append(Paragraph("7.1 主菜单界面", style_h2))
    story.append(Paragraph(
        "游戏启动后首先显示主菜单界面。背景使用战场风格图片，叠加暗色渐变遮罩以突出前景内容。"
        "界面中央从上到下依次显示：",
        style_body_noindent))
    menu_items = [
        "<b>游戏标题</b>：「秦始皇归来！」，浅黄色内里（#fff9c4）配深黄色描边（#f9a825），加粗显示",
        "<b>副标题</b>：英文副标题「SURVIVAL HUNTER」",
        "<b>规则提示</b>：深红色背景上的血红文字「⚠ 你只有 1 点生命，被碰到一下就会死」，带有红色光晕脉动动画",
        "<b>历史最佳</b>：金色边框显示上一次的最佳成绩（存活时间、击杀数、皇冠数）",
        "<b>开始按钮</b>：红色按钮「开始狩猎」，点击后进入游戏",
    ]
    for item in menu_items:
        story.append(Paragraph(f"• {item}", style_bullet))
    
    story.append(Paragraph("7.2 游戏 HUD 界面", style_h2))
    story.append(Paragraph(
        "游戏中 HUD（抬头显示）位于屏幕上方，分为左右两部分：",
        style_body_noindent))
    hud_data = [
        ["位置", "元素", "说明"],
        ["左上", "等级显示", "Lv.X 格式，白色文字配深色描边"],
        ["左上", "经验条", "金色填充进度条，下方显示 X/Y 经验数值"],
        ["左上", "武器列表", "当前持有武器的名称标签列表"],
        ["右上", "存活时间", "M:SS 格式，白色大字"],
        ["右上", "击杀数", "当前击杀怪物总数"],
        ["右上", "皇冠数", "金色 👑 N 显示（4分钟后出现）"],
        ["右上", "连杀倍率", "连杀倍率显示（触发时出现）"],
        ["右上", "冲刺状态", "冲刺键提示和冷却状态"],
        ["右下", "小地图", "120×120 像素战场缩略图"],
        ["左上角", "暂停/音乐", "暂停按钮和音乐开关按钮"],
        ["右下角", "冲刺按钮", "移动端专用，带冷却环动画"],
    ]
    story.append(make_table(hud_data, col_widths=[70, 90, 300]))
    
    story.append(PageBreak())
    
    story.append(Paragraph("7.3 升级选择界面", style_h2))
    story.append(Paragraph(
        "当玩家经验值满时，游戏暂停并弹出升级选择界面。界面背景为半透明黑色遮罩，"
        "中央显示两张强化卡片并排排列。每张卡片包含以下信息：",
        style_body_noindent))
    card_items = [
        "<b>稀有度标签</b>：普通（棕褐色）、稀有（蓝色）、史诗（紫色）、传说（金色），卡片背景颜色随稀有度变化",
        "<b>武器图标</b>：大尺寸像素风格武器图标",
        "<b>武器名称</b>：中文武器名称",
        "<b>强化描述</b>：本次强化效果的文字说明",
        "<b>属性标签</b>：伤害、数量、速度等属性数值标签",
    ]
    for item in card_items:
        story.append(Paragraph(f"• {item}", style_bullet))
    story.append(Paragraph(
        "玩家点击其中一张卡片即完成选择，游戏继续。如果两张卡片都不想要，"
        "也无法跳过——必须选择其一，这增加了策略决策的权重。",
        style_body))
    
    story.append(Paragraph("7.4 暂停面板", style_h2))
    story.append(Paragraph(
        "按 P 键或点击暂停按钮可打开暂停面板。面板显示当前所有武器的详细信息卡片，"
        "包括武器名称、等级、类型、伤害、冷却、数量、速度等具体数值。"
        "面板底部提供「重新开始」和「主界面」两个按钮。",
        style_body))
    
    story.append(Paragraph("7.5 死亡结算界面", style_h2))
    story.append(Paragraph(
        "玩家死亡后，游戏画面渐变为半透明黑色遮罩，显示结算信息：",
        style_body_noindent))
    death_items = [
        "<b>标题</b>：「你 死 了」大字，红色描边配白色内里",
        "<b>新纪录提示</b>：如打破历史最佳，显示金色「★ 新纪录 ★」并带有发光动画",
        "<b>统计数据</b>：三列显示存活时间、击杀数、皇冠数",
        "<b>历史最佳</b>：底部显示历史最佳成绩对比",
    ]
    for item in death_items:
        story.append(Paragraph(f"• {item}", style_bullet))
    
    # ========== 第八章 数据存储与安全 ==========
    story.append(PageBreak())
    story.append(Paragraph("第八章 数据存储与安全", style_h1))
    
    story.append(Paragraph("8.1 本地数据存储", style_h2))
    story.append(Paragraph(
        "游戏使用浏览器的 localStorage API 进行本地数据持久化存储，存储内容包括：",
        style_body_noindent))
    storage_data = [
        ["存储键名", "存储内容", "说明"],
        ["qh_bestTime", "最佳存活时间（秒）", "用于主菜单显示和历史对比"],
        ["qh_bestKills", "最佳击杀数", "用于主菜单显示和历史对比"],
        ["qh_bestCrowns", "最佳皇冠数", "用于主菜单显示和历史对比"],
        ["qh_music", "音乐开关状态", "记忆玩家音乐偏好"],
    ]
    story.append(make_table(storage_data, col_widths=[120, 160, 180]))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(
        "所有数据仅存储在用户本地浏览器中，不上传至任何服务器，不存在隐私泄露风险。"
        "玩家清除浏览器缓存后数据将重置。",
        style_body))
    
    story.append(Paragraph("8.2 网络安全", style_h2))
    story.append(Paragraph(
        "游戏在首次加载时需要从服务器下载 HTML 文件和资源图片，加载完成后即可完全离线运行。"
        "游戏不进行任何网络请求（除首次资源加载外），不收集任何用户信息，不包含任何第三方分析或追踪代码。"
        "游戏代码完全开源，可审查无后门风险。",
        style_body))
    
    story.append(Paragraph("8.3 兼容性说明", style_h2))
    story.append(Paragraph(
        "游戏已在以下浏览器和设备上完成兼容性测试：",
        style_body_noindent))
    compat_data = [
        ["平台", "浏览器", "测试结果"],
        ["Windows 10/11", "Chrome 100+", "完美运行"],
        ["Windows 10/11", "Edge 100+", "完美运行"],
        ["Windows 10/11", "Firefox 100+", "完美运行"],
        ["macOS 12+", "Chrome 100+", "完美运行"],
        ["macOS 12+", "Safari 15+", "完美运行"],
        ["Android 10+", "Chrome 100+", "完美运行（触屏操作）"],
        ["iOS 15+", "Safari 15+", "完美运行（触屏操作）"],
    ]
    story.append(make_table(compat_data, col_widths=[120, 150, 190]))
    
    story.append(Spacer(1, 20))
    story.append(Paragraph("— 本说明书完 —", ParagraphStyle('End', parent=style_body,
        alignment=TA_CENTER, fontSize=12, textColor=HexColor('#888888'))))
    
    # Build
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"PDF saved to: {OUTPUT_FILE}")
    print(f"File size: {os.path.getsize(OUTPUT_FILE) / 1024:.1f} KB")

if __name__ == '__main__':
    build_manual()
