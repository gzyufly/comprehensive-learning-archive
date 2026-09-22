#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
综合性学习 / 综合实践 资料库 —— 索引 / 查询 / 搭建骨架脚本（通用版）

本脚本不绑定任何学校。所有"本校专属"信息都通过同目录下的 config.json 配置：
  - root            归档根目录
  - grades          年级全称列表（如 ["一年级", ..., "九年级"] 或 ["高一","高二","高三"]）
  - year_keywords   学年文件夹识别关键词（默认 ["学年","学期","续期"]）
  - project_template 新项目文件夹命名模板（默认 "{theme}——{grade}综合性学习"）
  - stages          五阶段骨架（默认见 DEFAULT_STAGES）

若未提供 config.json，可用 --root 直接指定根目录；--grades 可临时覆盖年级列表。

年级识别规则（避免误判）：
  - 优先匹配"完整年级名"（如 八年级 / 高一 / 小班）。
  - 其次匹配数字简写：中文/阿拉伯数字 + 可选[上下] + 可选"年级"（如 八下 / 三 / 3年级）。
  - 仅当以上都不匹配时才认为该文件夹不是年级项目。这样"一花一世界""千年羊城"里的"一"
    不会误判成一年级。

用法示例（PowerShell，使用 WorkBuddy 受管 Python）：
  $py = "C:\Users\tang\.workbuddy\binaries\python\versions\3.13.12\python.exe"
  & $py index_projects.py --root "<归档根目录>" --index
  & $py index_projects.py --root "<归档根目录>" --grade 八年级 --json
  & $py index_projects.py --root "<归档根目录>" --tree "<某年级项目文件夹路径>"
  & $py index_projects.py --root "<归档根目录>" --scaffold --grade 三年级 --theme 奇石妙想 --year 2025—2026第二学期

功能：
  --index      扫描归档根目录，识别各学年文件夹下的年级项目，输出
               「学年 | 年级 | 主题 | 文件夹路径 | 文件数」索引表。
  --grade G    仅显示指定年级（支持 八年级 / 八 / 五年级 / 五 / 三下 等写法）。
  --year Y     仅显示指定学年文件夹（子串匹配，如 2024—2025第二学期 / 2024）。
  --json       以 JSON 形式输出（便于二次处理）。
  --tree PATH  打印 PATH（通常是一个年级项目文件夹）的目录树，
               目录带 [N文件] 标注，限制深度避免照片刷屏。
  --scaffold   在 root/year/ 下新建「主题——X年级综合性学习」及标准五阶段骨架。
               需配合 --grade --theme --year。
"""

import argparse
import io
import json
import os
import re
import sys

# 强制 stdout 以 UTF-8 输出（Windows 控制台默认 GBK，管道/重定向后会乱码）
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    else:  # Python <3.7 兜底
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

# 技能根目录（脚本位于 <skill>/scripts/ 下，config.json 在 <skill>/ 根目录）
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# 默认值（可被 config.json / 命令行覆盖）
# ---------------------------------------------------------------------------
DEFAULT_GRADES = ["九年级", "八年级", "七年级", "六年级", "五年级",
                  "四年级", "三年级", "二年级", "一年级"]
DEFAULT_YEAR_KEYWORDS = ["学年", "学期", "续期"]
DEFAULT_PROJECT_TEMPLATE = "{theme}——{grade}综合性学习"
DEFAULT_STAGES = [
    ("一、课程设计", ["1、主题课程设计", "2、项目课程设计与实施设计"]),
    ("二、开题资料", []),
    ("三、项目实施", ["1、子课题项目资料", "2、综合实践资料"]),
    ("四、结题资料", ["1、结题方案", "2、结题素材", "3、复盘反思表", "4、结题新闻稿"]),
    ("五、教师总结性材料", []),
]

NUMERALS = "一二三四五六七八九十"


def load_config(args):
    """读取技能根目录下的 config.json（若存在）。返回 dict。"""
    cfg_path = args.config or os.path.join(SKILL_DIR, "config.json")
    cfg = {}
    if os.path.exists(cfg_path):
        try:
            with open(cfg_path, encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception as e:
            print(f"[警告] 读取配置失败 {cfg_path}: {e}", file=sys.stderr)
    return cfg


def build_grade_matcher(grades):
    """构造年级正则与 数字->完整年级 映射。
    返回 (regex, num_to_full)：
      - 优先匹配完整年级名（group 'full'）
      - 其次匹配简写：阿拉伯/中文数字 + 可选[上下] + 可选'年级'（group 'num'）
    注意：不做"裸单字"匹配，避免把"一花一世界"里的"一"误判成一年级。
    """
    full_alt = "|".join(re.escape(g) for g in sorted(set(grades), key=len, reverse=True))
    rx = re.compile(
        r"(?P<full>" + full_alt + r")|"
        r"(?P<num>[0-9" + NUMERALS + r"]+)[上下]?年级?"
    )
    # 数字 -> 完整年级（取每条年级名开头的数字段）
    num_to_full = {}
    for g in grades:
        m = re.match(r"^([0-9" + NUMERALS + r"]+)", g)
        if m:
            num_to_full.setdefault(m.group(1), g)
    return rx, num_to_full


def detect_grade(name, rx, num_to_full):
    """从文件夹名中识别年级，返回如 '八年级' 或 None。"""
    m = rx.search(name)
    if not m:
        return None
    if m.group("full"):
        return m.group("full")
    if m.group("num"):
        return num_to_full.get(m.group("num"), m.group("num") + "年级")
    return None


def grade_short(grade, num_to_full):
    """返回年级的简写形态，如 '八年级' -> '八'。"""
    return {v: k for k, v in num_to_full.items()}.get(grade, grade)


_THEME_CLEAN = re.compile(
    r"[“”\"'（）()\[\]【】\s]+|"
    r"——+|--+|—+-|"                                  # 破折号
    r"(综合性学习|综合实践|资料集|资料夹|资料|课程|文件夹|项目|活动|学习资料|课程资料).*?$"
)


def clean_theme(name, grade):
    """从文件夹名中抽取主题（去掉年级与修饰）。"""
    s = name
    # 去掉已识别的年级关键词（含周围可能的 '下/上'）
    s = re.sub(re.escape(grade) + r"[上下]?", "", s)
    s = _THEME_CLEAN.sub("", s)
    s = s.strip("—-–·. ")
    return s or "(未命名主题)"


def is_year_folder(name, year_keywords):
    """顶层文件夹是否"学年/学期"归档文件夹。"""
    if re.match(r"^\d{4}[—-]\d{4}", name):
        return True
    return any(k in name for k in year_keywords)


def count_files(path):
    n = 0
    for _, _, files in os.walk(path):
        n += len(files)
    return n


def scan(root, grades, year_keywords):
    """返回 [(year, grade, theme, abspath, file_count), ...]。"""
    rx, num_to_full = build_grade_matcher(grades)
    rows = []
    try:
        top = sorted(os.listdir(root))
    except OSError as e:
        print(f"[错误] 无法读取根目录: {e}", file=sys.stderr)
        return rows

    for yname in top:
        ypath = os.path.join(root, yname)
        if not os.path.isdir(ypath) or not is_year_folder(yname, year_keywords):
            continue
        for cname in sorted(os.listdir(ypath)):
            cpath = os.path.join(ypath, cname)
            if not os.path.isdir(cpath):
                continue
            # 跳过嵌套的"学年"文件夹（历史迁移残留）
            if is_year_folder(cname, year_keywords):
                continue
            grade = detect_grade(cname, rx, num_to_full)
            if not grade:
                continue
            theme = clean_theme(cname, grade)
            rows.append((yname, grade, theme, cpath, count_files(cpath)))
    return rows


def print_index(rows):
    if not rows:
        print("未找到任何年级项目文件夹。请确认 root 路径与 grades 配置。")
        return
    header = f"{'学年/学期':<22} {'年级':<6} {'主题':<22} {'文件数':>6}  路径"
    print(header)
    print("-" * len(header))
    for y, g, t, p, c in rows:
        print(f"{y:<22} {g:<6} {t:<22} {c:>6}  {p}")


def print_tree(path, max_depth=3):
    if not os.path.isdir(path):
        print(f"[错误] 路径不存在或不是目录: {path}")
        return

    def walk(cur, depth):
        if depth > max_depth:
            fc = count_files(cur)
            if fc:
                print("    " * max_depth + f"…(含 {fc} 个文件，已折叠)")
            return
        try:
            entries = sorted(os.listdir(cur))
        except OSError:
            return
        dirs = [e for e in entries if os.path.isdir(os.path.join(cur, e))]
        files = [e for e in entries if not os.path.isdir(os.path.join(cur, e))]
        for d in dirs:
            dp = os.path.join(cur, d)
            fc = count_files(dp)
            print("    " * depth + f"📁 {d}  [{fc} 文件]")
            walk(dp, depth + 1)
        if files:
            print("    " * depth + f"📄 文件 {len(files)} 个（如 *.docx/*.pptx/*.jpg/*.mp4 等）")

    print(f"📦 {path}")
    walk(path, 0)


def scaffold(root, year, grade, theme, grades, stages, project_template):
    rx, num_to_full = build_grade_matcher(grades)
    g = detect_grade(grade, rx, num_to_full) or grade
    single = grade_short(g, num_to_full)
    proj_name = project_template.format(theme=theme, grade=g)
    ypath = os.path.join(root, year)
    if not os.path.isdir(ypath):
        print(f"[错误] 学年文件夹不存在: {ypath}", file=sys.stderr)
        return None
    proj_path = os.path.join(ypath, proj_name)

    os.makedirs(proj_path, exist_ok=True)
    created = [proj_path]
    for stage, subs in stages:
        sp = os.path.join(proj_path, stage)
        os.makedirs(sp, exist_ok=True)
        created.append(sp)
        for sub in subs:
            subp = os.path.join(sp, sub)
            os.makedirs(subp, exist_ok=True)
            created.append(subp)
    print(f"[完成] 已搭建骨架：{proj_path}")
    print(f"        年级：{g}（简写 {single}）  学年：{year}  主题：{theme}")
    return proj_path


def main():
    ap = argparse.ArgumentParser(description="综合性学习资料库索引/查询/搭建骨架（通用版）")
    ap.add_argument("--root", help="归档根目录（也可用 config.json 配置）")
    ap.add_argument("--config", help="自定义配置文件路径（默认同目录 config.json）")
    ap.add_argument("--index", action="store_true", help="输出全部年级项目索引")
    ap.add_argument("--grade", help="按年级过滤（八年级 / 八 / 五年级 / 五 / 三下）")
    ap.add_argument("--grades", help="临时覆盖年级列表，逗号分隔，如 高一,高二,高三")
    ap.add_argument("--year", help="按学年文件夹名子串过滤")
    ap.add_argument("--json", action="store_true", help="JSON 输出")
    ap.add_argument("--tree", metavar="PATH", help="打印某路径的目录树")
    ap.add_argument("--scaffold", action="store_true", help="搭建新年级项目骨架")
    ap.add_argument("--theme", help="--scaffold 用的主题名")
    args = ap.parse_args()

    cfg = load_config(args)

    root = args.root or cfg.get("root")
    if not root:
        print("[错误] 未指定根目录。请在 config.json 设置 root，或用 --root 指定。",
              file=sys.stderr)
        return

    grades = (args.grades.split(",") if args.grades
              else cfg.get("grades", DEFAULT_GRADES))
    year_keywords = cfg.get("year_keywords", DEFAULT_YEAR_KEYWORDS)
    stages = cfg.get("stages", DEFAULT_STAGES)
    project_template = cfg.get("project_template", DEFAULT_PROJECT_TEMPLATE)

    # --tree 优先（独立操作）
    if args.tree:
        print_tree(args.tree)
        return

    # --scaffold
    if args.scaffold:
        if not (args.grade and args.theme and args.year):
            print("[错误] --scaffold 需同时提供 --grade --theme --year",
                  file=sys.stderr)
            return
        scaffold(root, args.year, args.grade, args.theme,
                 grades, stages, project_template)
        return

    # 索引类
    rows = scan(root, grades, year_keywords)
    if args.grade:
        rx, num_to_full = build_grade_matcher(grades)
        g = detect_grade(args.grade, rx, num_to_full) or args.grade
        rows = [r for r in rows if r[1] == g]
    if args.year:
        rows = [r for r in rows if args.year in r[0]]

    if args.json:
        out = [
            {"year": y, "grade": g, "theme": t, "path": p, "files": c}
            for (y, g, t, p, c) in rows
        ]
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print_index(rows)
        print(f"\n共 {len(rows)} 个年级项目。")


if __name__ == "__main__":
    main()
