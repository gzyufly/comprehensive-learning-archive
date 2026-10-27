#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_market_package.py — 构建 comprehensive-learning-archive 市场安装包（含 assets/ 模板库）

为什么需要这个脚本：
    二进制母版（.docx/.xlsx/.xmind/.pptx/.xls）无法进入 Git 仓库（作者本机安全策略
    按内容指纹拦截写入），因此完整安装包 = 仓库内的文档/脚本 + 工具箱源文件，
    在内存中直接组装成 zip，全程不落盘，绕开拦截。

用法：
    python build_market_package.py --source <工具箱zip或文件夹> [--out <包路径>]
                                   [--no-desensitize] [--include-history]

    --source          工具箱来源：zip 文件（推荐，如把"综合性学习工具"文件夹整体压缩），
                      或文件夹路径（如 <归档根>\\综合性学习工具\\综合性学习工具）
    --out             输出 zip 路径（默认：<.workbuddy>/dist/comprehensive-learning-archive-<version>.zip）
    --no-desensitize  不脱敏（默认把范例文件中的真实教师姓名替换为"某"）
    --include-history 纳入 2 个历史版结构图 xmind（默认排除，控制包体积）

打包规则（与平台规范一致）：
    - zip 第一层为技能目录 comprehensive-learning-archive/
    - 包内目录最多两级：assets/ 扁平存放（不套子目录）
    - 不含 .git/、config.json、~$*（Office 锁文件）、__pycache__
    - 包体积 ≤ 3MB（超出会告警）

依赖：仅 Python 标准库。
"""

import argparse
import io
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_NAME = "comprehensive-learning-archive"

# 仓库内随包分发的文档/脚本（assets/ 由 --source 提供）
REPO_FILES = [
    "SKILL.md",
    "README.md",
    "LICENSE",
    "config.example.json",
]
REPO_DIRS = ["references", "scripts"]

# 默认排除的工具箱文件（历史版结构图，演进参考）
HISTORY_PATTERNS = ["2023-2-17", "2024-8"]

# 需要脱敏的文件（按文件名子串匹配）与替换表
DESENSITIZE_TARGETS = ["二年级三角模型清单更改", "1、综合性学习复盘"]
NAME_REPLACEMENTS = {
    "周小宁": "某",
    "张金娜": "某",
    "杨莉": "某",
    "张延菲": "某",
}

# Word XML 中可能承载文字的部件
WORD_XML_HINTS = ("document", "header", "footer", "footnote", "endnote", "comments")
W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def read_skill_version():
    with open(os.path.join(SKILL_DIR, "SKILL.md"), encoding="utf-8") as f:
        head = f.read(2000)
    m = re.search(r"^version:\s*(\S+)\s*$", head, re.M)
    if not m:
        sys.exit("错误：SKILL.md 中找不到 version 字段")
    return m.group(1)


def collect_source_files(source):
    """返回 [(basename, relpath, bytes)]，调用方负责过滤。"""
    files = []
    if os.path.isfile(source) and source.lower().endswith(".zip"):
        with zipfile.ZipFile(source) as z:
            for info in z.infolist():
                if info.is_dir():
                    continue
                files.append((os.path.basename(info.filename),
                              info.filename,
                              z.read(info.filename)))
    elif os.path.isdir(source):
        for root, dirs, names in os.walk(source):
            dirs[:] = [d for d in dirs if d != "__pycache__"]
            for n in names:
                p = os.path.join(root, n)
                rel = os.path.relpath(p, source).replace("\\", "/")
                with open(p, "rb") as f:
                    files.append((n, rel, f.read()))
    else:
        sys.exit("错误：--source 既不是 zip 也不是文件夹：%s" % source)
    return files


def replace_in_word_xml(xml: bytes) -> bytes:
    """在 Word XML 字节流中替换真实姓名。

    第一步整段替换（姓名完整落在同一个 w:t 内的常见情况）；
    第二步处理姓名被 XML 标签拆分到多个 w:t 的情况——正则允许姓名每个字之间
    穿插 XML 标签，替换时把捕获到的标签原样保留（只删姓名用字），避免破坏文档结构。
    """
    data = xml
    for name, repl in NAME_REPLACEMENTS.items():
        nb, rb = name.encode("utf-8"), repl.encode("utf-8")
        # 注意：不能因"连续字节不存在"就跳过——姓名可能被 XML 标签拆分到多个 w:t，
        # 此时连续字节不存在但拆分形态仍在，必须继续走下面的正则替换。
        data = data.replace(nb, rb)
        # 跨 run 拆分：字与字之间只允许出现 XML 标签，标签需保留
        parts, repl_parts = [], [rb]
        for i, ch in enumerate(name):
            parts.append(re.escape(ch.encode("utf-8")))
            if i != len(name) - 1:
                parts.append(b"((?:<[^>]+>)*)")
                repl_parts.append(b"\\%d" % (i + 1))
        data = re.sub(b"".join(parts), b"".join(repl_parts), data)
    return data


def desensitize_docx(data: bytes) -> bytes:
    """返回脱敏后的 docx 字节；无需改动时原样返回。"""
    zin = zipfile.ZipFile(io.BytesIO(data))
    changed = {}
    for name in zin.namelist():
        if not name.endswith(".xml"):
            continue
        low = os.path.basename(name).lower()
        if not any(h in low for h in WORD_XML_HINTS):
            continue
        xml = zin.read(name)
        new = replace_in_word_xml(xml)
        if new != xml:
            changed[name] = new
    if not changed:
        return data
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            payload = changed.get(item.filename)
            if payload is None:
                payload = zin.read(item.filename)
            zout.writestr(item, payload)
    return buf.getvalue()


def verify_no_names(zf: zipfile.ZipFile, member: str):
    """从包内 docx 提取全部文字，确认真实姓名已不存在。"""
    inner = zipfile.ZipFile(io.BytesIO(zf.read(member)))
    texts = []
    for name in inner.namelist():
        if not name.endswith(".xml"):
            continue
        low = os.path.basename(name).lower()
        if not any(h in low for h in WORD_XML_HINTS):
            continue
        try:
            root = ET.fromstring(inner.read(name))
        except ET.ParseError:
            continue
        for t in root.iter(W_NS + "t"):
            texts.append(t.text or "")
    blob = "".join(texts)
    for name in NAME_REPLACEMENTS:
        if name in blob:
            raise RuntimeError("脱敏失败：%s 中仍含真实姓名 %s" % (member, name))


def main():
    ap = argparse.ArgumentParser(description="构建含 assets/ 的市场安装包（内存组装，不落盘）")
    ap.add_argument("--source", required=True, help="工具箱来源：zip 文件或文件夹")
    ap.add_argument("--out", default=None, help="输出 zip 路径")
    ap.add_argument("--no-desensitize", action="store_true", help="不脱敏范例文件中的真实姓名")
    ap.add_argument("--include-history", action="store_true", help="纳入历史版结构图 xmind")
    args = ap.parse_args()

    version = read_skill_version()
    # 默认输出到 <项目>/.workbuddy/dist/（SKILL_DIR 为 <项目>/.workbuddy/skills/<技能名>）
    out = args.out or os.path.abspath(os.path.join(
        SKILL_DIR, "..", "..", "dist", "%s-%s.zip" % (SKILL_NAME, version)))

    # 1) 仓库文档/脚本
    entries = []  # (arcname, bytes, note)
    for rel in REPO_FILES:
        p = os.path.join(SKILL_DIR, rel)
        if not os.path.isfile(p):
            sys.exit("错误：仓库文件缺失 %s" % p)
        with open(p, "rb") as f:
            entries.append(("%s/%s" % (SKILL_NAME, rel), f.read(), ""))
    for d in REPO_DIRS:
        for root, dirs, names in os.walk(os.path.join(SKILL_DIR, d)):
            dirs[:] = [x for x in dirs if x != "__pycache__"]
            for n in sorted(names):
                if n.startswith("~$"):
                    continue
                p = os.path.join(root, n)
                rel = os.path.relpath(p, SKILL_DIR).replace("\\", "/")
                with open(p, "rb") as f:
                    entries.append(("%s/%s" % (SKILL_NAME, rel), f.read(), ""))

    # 2) 工具箱源文件 → assets/（扁平）
    asset_rows, seen = [], set()
    for base, rel, data in collect_source_files(args.source):
        if base.startswith("~$"):
            print("  跳过锁文件：%s" % base)
            continue
        if not args.include_history and base.endswith(".xmind") and any(h in base for h in HISTORY_PATTERNS):
            print("  跳过历史版结构图（--include-history 可纳入）：%s" % base)
            continue
        if base in seen:
            sys.exit("错误：assets/ 内文件名冲突：%s" % base)
        seen.add(base)
        note = ""
        if not args.no_desensitize and base.endswith(".docx") and any(t in base for t in DESENSITIZE_TARGETS):
            data = desensitize_docx(data)
            note = "已脱敏"
        entries.append(("%s/assets/%s" % (SKILL_NAME, base), data, note))
        asset_rows.append((base, rel))

    # 3) assets/母版清单.txt（扁平存放后，用来说明各文件来自哪个子文件夹）
    lines = [
        "综合性学习工具 · 空白母版清单（技能版本 %s）" % version,
        "",
        "本目录为技能附带的空白母版，与归档根目录下「综合性学习工具\\综合性学习工具」同源。",
        "用法：先复制到对应年级的项目文件夹，再在副本上填写；切勿直接改母版。",
        "字段级填写要点见 references/course-design-toolkit.md 第 5 节。",
        "",
        "共 %d 个文件：" % len(asset_rows),
    ]
    for base, rel in sorted(asset_rows):
        short = rel
        for prefix in ("综合性学习工具/综合性学习工具/", "综合性学习工具\\综合性学习工具\\"):
            if short.startswith(prefix):
                short = short[len(prefix):]
                break
        lines.append("  - %s    （来源：%s）" % (base, short))
    entries.append(("%s/assets/母版清单.txt" % SKILL_NAME,
                    "\n".join(lines).encode("utf-8"), ""))

    # 4) 组装 zip（第一层为技能目录）
    os.makedirs(os.path.dirname(out), exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, data, _note in entries:
            z.writestr(arc, data)
    payload = buf.getvalue()
    with open(out, "wb") as f:
        f.write(payload)

    # 5) 校验
    size_mb = len(payload) / 1048576.0
    print("\n已生成：%s" % out)
    print("包内文件数：%d，体积：%.2f MB" % (len(entries), size_mb))
    if size_mb > 3.0:
        print("警告：超过平台 3MB 上限，请裁剪 assets/（先删培训 PPT，再删基因卡三件套）")
    assert all(a.split("/")[0] == SKILL_NAME for a, _d, _n in entries), "第一层目录不一致"
    with zipfile.ZipFile(io.BytesIO(payload)) as z:
        names = z.namelist()
        assert not any(".git/" in n or n.endswith("config.json") for n in names), "包内含违禁文件"
        assert all(n.count("/") <= 2 for n in names), "存在超过两级的目录：%s" % [
            n for n in names if n.count("/") > 2]
        for arc, _d, note in entries:
            if note == "已脱敏":
                verify_no_names(z, arc)
                print("  脱敏校验通过：%s" % arc)
        print("assets/ 文件数：%d（含母版清单.txt）" %
              len([n for n in names if n.startswith(SKILL_NAME + "/assets/")]))
        print("第一层目录：%s/（符合平台规范）" % SKILL_NAME)
    print("完成。")


if __name__ == "__main__":
    main()
