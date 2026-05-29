from __future__ import annotations

from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT
FONT_PATH = Path("/System/Library/Fonts/Hiragino Sans GB.ttc")

INK = "#17202a"
MUTED = "#5d6878"
LINE = "#d8e0e8"
PAPER = "#f3f6f4"
PANEL = "#ffffff"
BLUE = "#1f63d6"
TEAL = "#13857f"
GREEN = "#238553"
AMBER = "#c47612"
CORAL = "#bd3b2d"
PURPLE = "#6a55b8"
NAV = "#0e2336"
SOFT_BLUE = "#eef4ff"
SOFT_TEAL = "#eaf8f6"
SOFT_AMBER = "#fff4dd"
SOFT_CORAL = "#fff0ed"
SOFT_GREEN = "#eefaf2"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    index = 1 if bold else 0
    return ImageFont.truetype(str(FONT_PATH), size=size, index=index)


def canvas(w: int, h: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    img = Image.new("RGB", (w, h), PAPER)
    d = ImageDraw.Draw(img)
    for x in range(0, w, 64):
        d.line((x, 0, x, h), fill="#e7ecef", width=1)
    for y in range(0, h, 64):
        d.line((0, y, w, y), fill="#e7ecef", width=1)
    d.rounded_rectangle((32, 32, w - 32, h - 32), radius=28, fill=PANEL, outline=LINE, width=2)
    return img, d


def text(d: ImageDraw.ImageDraw, xy, value: str, size: int, fill=INK, bold=False, anchor=None, max_width=None, line_gap=8):
    f = font(size, bold)
    if not max_width:
        d.text(xy, value, font=f, fill=fill, anchor=anchor)
        return
    lines: list[str] = []
    current = ""
    for char in value:
        candidate = current + char
        if d.textbbox((0, 0), candidate, font=f)[2] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = char
    if current:
        lines.append(current)
    x, y = xy
    line_h = d.textbbox((0, 0), "国", font=f)[3] + line_gap
    for idx, line in enumerate(lines):
        d.text((x, y + idx * line_h), line, font=f, fill=fill, anchor=anchor)


def title(d, title_value: str, sub: str, w: int):
    text(d, (78, 70), title_value, 34, NAV, True)
    text(d, (78, 122), sub, 20, MUTED, False)
    d.line((78, 164, w - 78, 164), fill=LINE, width=2)


def arrow(d, start, end, color=MUTED, width=4):
    x1, y1 = start
    x2, y2 = end
    d.line((x1, y1, x2, y2), fill=color, width=width)
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 >= x1 else -1
        pts = [(x2, y2), (x2 - 18 * direction, y2 - 10), (x2 - 18 * direction, y2 + 10)]
    else:
        direction = 1 if y2 >= y1 else -1
        pts = [(x2, y2), (x2 - 10, y2 - 18 * direction), (x2 + 10, y2 - 18 * direction)]
    d.polygon(pts, fill=color)


def card(d, box, heading, body, color, fill):
    d.rounded_rectangle(box, radius=20, fill=fill, outline=color, width=3)
    x1, y1, x2, _ = box
    text(d, (x1 + 28, y1 + 28), heading, 26, color, True)
    text(d, (x1 + 28, y1 + 78), body, 18, INK, False, max_width=x2 - x1 - 56, line_gap=7)


def save(img: Image.Image, name: str):
    img.save(OUT / name, "WEBP", quality=92, method=6)


def core_loop():
    w, h = 1600, 720
    img, d = canvas(w, h)
    title(d, "具身智能系统的核心闭环", "现场数据不是附属品，而是机器人从演示走向长期运营的持续迭代系统。", w)
    nodes = [
        ((92, 240, 338, 428), "现场输入", "摄像头、深度、触觉、语音、业务系统状态", BLUE, SOFT_BLUE),
        ((386, 222, 632, 410), "感知理解", "识别物体、人员、空间、异常和任务上下文", TEAL, SOFT_TEAL),
        ((680, 222, 926, 410), "决策规划", "VLA / 世界模型把目标转成可控动作意图", AMBER, SOFT_AMBER),
        ((974, 222, 1220, 410), "身体行动", "移动、抓取、巡检、清洁、配送或操作", GREEN, SOFT_GREEN),
        ((1268, 240, 1514, 428), "学习回流", "失败样本、接管过程、结果数据回到训练集", CORAL, SOFT_CORAL),
    ]
    for b, heading, body, color, fill in nodes:
        card(d, b, heading, body, color, fill)
    for box, next_node in zip([n[0] for n in nodes[:-1]], [n[0] for n in nodes[1:]]):
        arrow(d, (box[2] + 16, 326), (next_node[0] - 16, 326), MUTED)
    d.arc((170, 392, 1440, 664), start=8, end=176, fill="#8c98aa", width=4)
    arrow(d, (210, 534), (150, 424), "#8c98aa", 4)
    text(d, (800, 608), "数据回流驱动模型、控制和流程同步升级", 22, NAV, True, anchor="mm")
    insights = [
        ("价值判断", "能否连续运转，而不是一次演示能否成功"),
        ("管理抓手", "任务成功率、接管次数、失败原因、复训改善曲线"),
        ("落地原则", "先做数据闭环，再谈多门店复制"),
    ]
    x = 128
    for k, v in insights:
        d.rounded_rectangle((x, 488, x + 380, 586), radius=16, fill="#fbfdff", outline=LINE, width=2)
        text(d, (x + 24, 512), k, 19, BLUE, True)
        text(d, (x + 24, 546), v, 17, MUTED, False, max_width=330)
        x += 440
    save(img, "core-loop-system.webp")


def industry_chain():
    w, h = 1600, 720
    img, d = canvas(w, h)
    title(d, "产业链五层地图", "从核心零部件到场景交付，壁垒来自成本、可靠性、模型、数据和业务流程的组合能力。", w)
    layers = [
        ("核心零部件", "电机 / 减速器\n关节 / 灵巧手\n传感器 / 控制器", "决定成本与可靠性", BLUE, SOFT_BLUE),
        ("机器人本体", "人形 / 四足\n轮式双臂 / AMR\n服务机器人", "决定进入什么环境", TEAL, SOFT_TEAL),
        ("模型与智能", "VLA / 世界模型\n任务规划\n异常处理", "理解任务并转成动作", AMBER, SOFT_AMBER),
        ("数据与仿真", "遥操作数据\n失败样本\n仿真评估", "决定迭代速度", PURPLE, "#f0edf5"),
        ("场景交付", "仓储 / 制造\n巡检 / 零售\n酒店 / 康养", "嵌入业务流程", GREEN, SOFT_GREEN),
    ]
    x0, gap, bw = 82, 22, 278
    for i, (name, items, note, color, fill) in enumerate(layers):
        x = x0 + i * (bw + gap)
        d.rounded_rectangle((x, 230, x + bw, 500), radius=22, fill=fill, outline=color, width=3)
        d.rounded_rectangle((x + 22, 208, x + 92, 260), radius=16, fill=color)
        text(d, (x + 57, 234), f"0{i+1}", 20, "white", True, anchor="mm")
        text(d, (x + 28, 286), name, 27, color, True)
        for line_i, line in enumerate(items.split("\n")):
            text(d, (x + 30, 338 + line_i * 34), line, 19, INK)
        d.line((x + 28, 442, x + bw - 28, 442), fill=LINE, width=2)
        text(d, (x + 30, 462), note, 17, MUTED, False, max_width=bw - 60)
        if i < len(layers) - 1:
            arrow(d, (x + bw + 4, 364), (x + bw + gap - 6, 364), MUTED, 3)
    d.rounded_rectangle((118, 542, 1482, 628), radius=18, fill="#fbfdff", outline=LINE, width=2)
    text(d, (150, 570), "管理层读法", 20, NAV, True)
    text(d, (286, 570), "左侧决定成本下限，中段决定能力上限，右侧决定商业价值上限。投资和试点不应只看本体形态。", 20, MUTED)
    save(img, "industry-chain-map.webp")


def three_layer():
    w, h = 1600, 800
    img, d = canvas(w, h)
    title(d, "大脑 / 小脑 / 本体三层架构", "大脑决定泛化，小脑守住实时安全，本体决定可靠性下限；三层共同形成可部署产品。", w)
    d.rounded_rectangle((78, 215, 300, 610), radius=22, fill="#fbfdff", outline=LINE, width=2)
    text(d, (112, 252), "输入", 26, BLUE, True)
    for i, line in enumerate(["视觉 / 深度", "语音 / 文本", "关节 / IMU", "力觉 / 触觉", "业务系统"]):
        text(d, (116, 304 + i * 48), line, 20, INK)
    layer_boxes = [
        ((380, 205, 1200, 325), "大脑：端到端模型", "理解任务 · 生成动作意图 · VLA / 世界模型", "输入多模态上下文，输出末端轨迹或动作策略", BLUE, SOFT_BLUE),
        ((380, 365, 1200, 485), "小脑：运动控制系统", "稳定控制 · 安全约束 · 实时执行 · 平衡避障", "把上层意图转成毫秒级控制信号", TEAL, SOFT_TEAL),
        ((380, 525, 1200, 645), "本体：机械身体", "关节 · 手爪 · 电池 · 结构 · 传感器 · 散热", "真实执行移动、抓取、搬运、按压", AMBER, SOFT_AMBER),
    ]
    for box, head, body, note, color, fill in layer_boxes:
        d.rounded_rectangle(box, radius=20, fill=fill, outline=color, width=3)
        x1, y1, x2, _ = box
        text(d, (x1 + 30, y1 + 24), head, 27, color, True)
        text(d, (x1 + 30, y1 + 64), body, 20, INK)
        text(d, (x2 - 30, y1 + 64), note, 17, MUTED, False, anchor="ra")
    arrow(d, (300, 408), (370, 408), BLUE, 4)
    arrow(d, (790, 325), (790, 360), MUTED, 4)
    arrow(d, (790, 485), (790, 520), MUTED, 4)
    d.rounded_rectangle((1280, 215, 1508, 610), radius=22, fill="#fbfdff", outline=LINE, width=2)
    text(d, (1312, 252), "输出与反馈", 26, GREEN, True)
    for i, line in enumerate(["动作执行", "任务结果", "失败样本", "人工接管", "复训数据"]):
        text(d, (1316, 304 + i * 48), line, 20, INK)
    arrow(d, (1208, 408), (1272, 408), GREEN, 4)
    d.arc((448, 120, 1390, 728), start=35, end=325, fill="#8c98aa", width=4)
    text(d, (920, 707), "状态 · 失败 · 接管 · 数据持续回流", 19, MUTED, True, anchor="mm")
    save(img, "three-layer-architecture.webp")


def model_timeline():
    w, h = 1600, 900
    img, d = canvas(w, h)
    title(d, "端到端模型路线：数据飞轮与十年时间线", "短期是混合系统和数据争夺，中期出现行业模型包，长期进入部分行业的常规劳动力补充。", w)
    wheel_center = (360, 350)
    wheel_nodes = [
        ("采集示范", 360, 220, BLUE, SOFT_BLUE),
        ("清洗标注", 520, 320, TEAL, SOFT_TEAL),
        ("模型训练", 460, 500, AMBER, SOFT_AMBER),
        ("安全上线", 260, 500, GREEN, SOFT_GREEN),
        ("失败回流", 200, 320, CORAL, SOFT_CORAL),
    ]
    d.ellipse((250, 240, 470, 460), outline=LINE, width=10)
    text(d, wheel_center, "数据\n飞轮", 30, NAV, True, anchor="mm")
    for label, x, y, color, fill in wheel_nodes:
        d.rounded_rectangle((x - 72, y - 34, x + 72, y + 34), radius=18, fill=fill, outline=color, width=3)
        text(d, (x, y), label, 19, color, True, anchor="mm")
    for a, b in zip(wheel_nodes, wheel_nodes[1:] + wheel_nodes[:1]):
        arrow(d, (a[1], a[2] + 45), (b[1], b[2] - 45), "#8c98aa", 3)
    d.rounded_rectangle((650, 210, 1485, 550), radius=24, fill="#fbfdff", outline=LINE, width=2)
    phases = [
        ("2026", "数据争夺", "真机数据集、遥操作平台、VLA 模型密集出现", BLUE),
        ("2027-2028", "限定试点", "半结构化任务试点增多，数据采集标准化", TEAL),
        ("2029-2031", "行业模型包", "拣选、补货、清洁、巡检形成可复用能力", GREEN),
        ("2032-2034", "开放场景探索", "家庭和办公试点升温，合规与成本仍是约束", AMBER),
        ("2035-2036", "常规补充", "平台公司与场景公司分化，进入部分劳动力体系", CORAL),
    ]
    x_positions = [760, 925, 1095, 1268, 1410]
    d.line((750, 356, 1428, 356), fill="#bcc8d6", width=6)
    for (year, stage, desc, color), x in zip(phases, x_positions):
        d.ellipse((x - 18, 338, x + 18, 374), fill=color, outline="white", width=3)
        text(d, (x, 296), year, 20, color, True, anchor="mm")
        text(d, (x, 410), stage, 22, NAV, True, anchor="mm")
        text(d, (x - 70, 448), desc, 15, MUTED, max_width=140)
    cards = [
        ("中国路线", "真机数据、供应链、场景密度更强；关键是客户侧指标和持续运营证据。", TEAL, SOFT_TEAL),
        ("海外路线", "基础模型、仿真平台、工具链更强；关键是部署成本和场景规模化。", BLUE, SOFT_BLUE),
        ("会合点", "高质量真实任务数据、失败回流、安全兜底和正 ROI。", AMBER, SOFT_AMBER),
    ]
    x = 118
    for head, body, color, fill in cards:
        d.rounded_rectangle((x, 640, x + 430, 785), radius=20, fill=fill, outline=color, width=3)
        text(d, (x + 28, 670), head, 24, color, True)
        text(d, (x + 28, 718), body, 18, INK, max_width=360)
        x += 500
    save(img, "model-roadmap-timeline.webp")


def company_quadrant():
    w, h = 1600, 900
    img, d = canvas(w, h)
    title(d, "Top20 公司格局象限图", "按技术平台能力与商业落地程度分层，避免把通用人形、服务商用、工业巡检和上游能力混成一个赛道。", w)
    plot = (140, 195, 1160, 745)
    x1, y1, x2, y2 = plot
    d.rounded_rectangle(plot, radius=20, fill="#fbfdff", outline=LINE, width=2)
    d.line((x1 + 70, y2 - 70, x2 - 40, y2 - 70), fill="#b9c6d4", width=3)
    d.line((x1 + 70, y1 + 40, x1 + 70, y2 - 40), fill="#b9c6d4", width=3)
    d.line(((x1 + x2) // 2, y1 + 40, (x1 + x2) // 2, y2 - 70), fill="#d8e0e8", width=2)
    d.line((x1 + 70, (y1 + y2) // 2, x2 - 40, (y1 + y2) // 2), fill="#d8e0e8", width=2)
    text(d, ((x1 + x2) // 2, y2 - 22), "技术平台能力 →", 20, MUTED, True, anchor="mm")
    text(d, (82, (y1 + y2) // 2), "商业落地程度 →", 20, MUTED, True, anchor="mm")
    text(d, (375, 255), "高潜力 · 待验证", 24, "#c7d0dc", True, anchor="mm")
    text(d, (870, 255), "平台型领导者", 24, "#c7d0dc", True, anchor="mm")
    text(d, (375, 682), "场景深耕者", 24, "#c7d0dc", True, anchor="mm")
    text(d, (870, 682), "商用规模化", 24, "#c7d0dc", True, anchor="mm")
    companies = [
        ("智元", 405, 335, BLUE), ("宇树", 360, 385, BLUE), ("优必选", 455, 365, BLUE),
        ("银河", 430, 305, BLUE), ("傅利叶", 305, 355, BLUE), ("逐际", 250, 425, BLUE),
        ("乐聚", 285, 400, BLUE), ("众擎", 395, 465, BLUE), ("星尘", 320, 500, BLUE),
        ("开普勒", 235, 315, BLUE), ("小鹏", 560, 285, BLUE), ("帕西尼", 365, 535, PURPLE),
        ("普渡", 825, 515, TEAL), ("擎朗", 775, 550, TEAL),
        ("云深处", 725, 570, AMBER), ("越疆", 730, 602, AMBER), ("优艾智合", 790, 625, AMBER),
        ("梅卡曼德", 900, 485, AMBER), ("非夕", 595, 455, AMBER), ("斯坦德", 850, 650, AMBER),
    ]
    for name, x, y, color in companies:
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=color, outline="white", width=3)
        d.rounded_rectangle((x + 16, y - 18, x + 100, y + 18), radius=9, fill="white", outline=color, width=2)
        text(d, (x + 58, y), name, 16, color, True, anchor="mm")
    legend = [(BLUE, "人形/通用"), (TEAL, "服务商用"), (AMBER, "工业/巡检"), (PURPLE, "上游能力")]
    d.rounded_rectangle((1200, 220, 1490, 520), radius=20, fill="#fbfdff", outline=LINE, width=2)
    text(d, (1230, 254), "图例与读法", 24, NAV, True)
    for i, (color, label) in enumerate(legend):
        y = 305 + i * 48
        d.ellipse((1230, y - 10, 1250, y + 10), fill=color)
        text(d, (1264, y - 15), label, 19, INK, True)
    text(d, (1230, 525), "右上不等于一定胜出，仍需核验客户公告、持续运营、付费和复购。", 18, MUTED, max_width=250)
    d.rounded_rectangle((1200, 620, 1490, 745), radius=20, fill=SOFT_BLUE, outline=BLUE, width=2)
    text(d, (1230, 650), "管理层重点", 22, BLUE, True)
    text(d, (1230, 690), "先按公司类型筛选，再看商业证据；不要只被演示视频带偏", 18, INK, max_width=245)
    save(img, "company-quadrant.webp")


def store_funnel():
    w, h = 1600, 900
    img, d = canvas(w, h)
    title(d, "门店机器人试点 ROI 漏斗", "用任务筛选漏斗决定先做什么，再用工时、错误、客流和数据资产分项核算回报。", w)
    d.rounded_rectangle((90, 215, 455, 745), radius=24, fill="#fbfdff", outline=LINE, width=2)
    text(d, (125, 255), "门店现场", 28, NAV, True)
    d.rectangle((145, 340, 405, 555), fill="#eef2f5", outline="#ccd6df", width=3)
    d.rectangle((170, 380, 245, 520), fill="#ffffff", outline=LINE, width=2)
    d.rectangle((275, 380, 375, 520), fill="#ffffff", outline=LINE, width=2)
    d.rounded_rectangle((205, 580, 330, 680), radius=30, fill=SOFT_BLUE, outline=BLUE, width=3)
    d.ellipse((242, 604, 292, 654), fill=BLUE)
    text(d, (267, 704), "机器人", 18, BLUE, True, anchor="mm")
    for label, y in [("迎宾", 310), ("巡店", 560), ("盘点", 705)]:
        d.rounded_rectangle((105, y, 175, y + 34), radius=8, fill=SOFT_TEAL, outline=TEAL, width=2)
        text(d, (140, y + 17), label, 16, TEAL, True, anchor="mm")
    funnel_x = 560
    steps = [
        ("高频任务", "每天足够多可重复操作", BLUE),
        ("环境可控", "变化不超过感知和控制能力", TEAL),
        ("失败风险低", "出错不影响客户体验和安全", GREEN),
        ("数据可采集", "每次执行沉淀运营数据", AMBER),
        ("ROI 可核算", "工时、错误、转化可量化", CORAL),
        ("可复制多店", "区域扩张无需重新开发", PURPLE),
    ]
    widths = [640, 570, 500, 430, 360, 290]
    for i, (head, desc, color) in enumerate(steps):
        top = 225 + i * 78
        bw = widths[i]
        left = funnel_x + (640 - bw) // 2
        d.rounded_rectangle((left, top, left + bw, top + 54), radius=16, fill=color, outline=color, width=2)
        text(d, (left + 28, top + 27), f"{i+1}. {head}", 20, "white", True, anchor="lm")
        text(d, (left + bw - 24, top + 27), desc, 16, "white", False, anchor="rm")
    d.rounded_rectangle((600, 720, 1140, 780), radius=18, fill=SOFT_GREEN, outline=GREEN, width=3)
    text(d, (870, 750), "优先试点：巡店 · 迎宾 · 导购辅助 · 库存盘点 · 取放货辅助", 20, GREEN, True, anchor="mm")
    d.rounded_rectangle((1240, 215, 1490, 745), radius=24, fill="#fbfdff", outline=LINE, width=2)
    text(d, (1272, 255), "ROI 核算卡", 27, NAV, True)
    roi = [
        ("运营收益", "节省工时、降低差错"),
        ("营销收益", "吸引客流、提高转化"),
        ("战略收益", "沉淀任务和失败数据"),
        ("成本项", "设备、部署、云端、培训、售后"),
    ]
    colors = [TEAL, BLUE, AMBER, CORAL]
    for i, ((head, body), color) in enumerate(zip(roi, colors)):
        y = 305 + i * 94
        d.rounded_rectangle((1272, y, 1458, y + 68), radius=14, fill="#ffffff", outline=color, width=2)
        text(d, (1294, y + 16), head, 18, color, True)
        text(d, (1294, y + 42), body, 15, MUTED, max_width=142)
    text(d, (1272, 700), "验收指标：日均任务数、成功率、接管次数、员工采纳率、故障响应。", 16, MUTED, max_width=190)
    save(img, "store-roi-funnel.webp")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    core_loop()
    industry_chain()
    three_layer()
    model_timeline()
    company_quadrant()
    store_funnel()


if __name__ == "__main__":
    main()
