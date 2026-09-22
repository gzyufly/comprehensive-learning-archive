# comprehensive-learning-archive · 综合性学习资料库管理技能

一个用于 **WorkBuddy** 的技能（Skill），帮助中小学老师按"年级组"快速查询、浏览和维护本校"综合性学习 / 综合实践"项目资料库。

> 本技能**不绑定任何学校**。归档根目录、年级列表、阶段划分全部通过 `config.json` 配置，复制到其他学校只需改这一份配置。

---

## 它能做什么

1. **按年级组 + 学年定位项目**：一键列出某校某年级历年所有综合实践项目（年份、主题、路径、文件数）。
2. **浏览项目内部结构**：打印某年级项目的完整目录树，快速定位开题方案、结题新闻稿、三角模型、展板、视频等。
3. **调整与维护**：新增 / 移动 / 重命名资料，或为新学年、新年级一键搭建标准"五阶段"文件夹骨架。

---

## 安装

### 方式一：直接用 WorkBuddy 打开（推荐给普通老师）
1. 下载本仓库（Git 克隆或下载 zip 解压）。
2. 把整个 `comprehensive-learning-archive` 文件夹复制到：
   - **项目级**（仅当前工作区）：`<你的项目>/.workbuddy/skills/`
   - **用户级**（所有项目可用）：`C:\Users\<你>\.workbuddy\skills\`（Windows）/ `~/.workbuddy/skills/`（macOS/Linux）
3. 在技能目录里把 `config.example.json` 复制为 `config.json`，填好你的归档根目录（见下方"配置"）。
4. 在 WorkBuddy 中直接说"找一下八年级近几年的综合实践项目"即可触发。

### 方式二：开发者 / 想自己改
```bash
git clone <本仓库地址> ~/.workbuddy/skills/comprehensive-learning-archive
cd ~/.workbuddy/skills/comprehensive-learning-archive
cp config.example.json config.json   # 然后编辑 config.json
```

---

## 配置（config.json）

技能根目录下的 `config.json` 决定"哪份资料库、怎么识别年级"。从 `config.example.json` 复制后修改：

```json
{
  "root": "H:\\综合性学习",
  "grades": ["九年级","八年级","七年级","六年级","五年级","四年级","三年级","二年级","一年级"],
  "grade_aliases": ["九","八","七","六","五","四","三","二","一"],
  "year_keywords": ["学年","学期","续期"],
  "project_template": "{theme}——{grade}综合性学习",
  "stages": [
    ["一、课程设计", ["1、主题课程设计","2、项目课程设计与实施设计"]],
    ["二、开题资料", []],
    ["三、项目实施", ["1、子课题项目资料","2、综合实践资料"]],
    ["四、结题资料", ["1、结题方案","2、结题素材","3、复盘反思表","4、结题新闻稿"]],
    ["五、教师总结性材料", []]
  ]
}
```

| 字段 | 说明 |
|------|------|
| `root` | 资料库归档根目录（绝对路径）。也可每次用 `--root` 临时传入。 |
| `grades` | 年级**全称**列表，如 `["高一","高二","高三"]` 或 `["小班","中班","大班"]`。脚本靠这些词识别年级；数字简写（八下/三上/3年级）会被自动支持。 |
| `year_keywords` | 学年文件夹识别关键词，默认 `["学年","学期","续期"]`。 |
| `project_template` | 新项目文件夹命名模板，默认 `{theme}——{grade}综合性学习`。 |
| `stages` | `--scaffold` 生成的五阶段骨架，可改成贵校实际阶段。 |

> 没配置 `config.json` 时，脚本也能跑，但必须用 `--root` 指定根目录，且年级/阶段用内置默认值（九年制九级 + 五阶段）。

---

## 使用（命令示例）

> 以下用 WorkBuddy 受管 Python 演示；如环境有全局 `python3` 可直接替换。

```powershell
$py = "C:\Users\tang\.workbuddy\binaries\python\versions\3.13.12\python.exe"
$skill = "路径\to\comprehensive-learning-archive\scripts\index_projects.py"

# 1) 列出全部年级项目索引
& $py $skill --index
# 2) 只看八年级
& $py $skill --grade 八年级
# 3) 八年级 + 指定学年
& $py $skill --grade 八年级 --year 2024—2025第二学期
# 4) 机器可读 JSON
& $py $skill --grade 八年级 --json
# 5) 打印某年级项目的目录树
& $py $skill --tree "H:\综合性学习\2024—2025第二学期\“AI未来”——八年级综合性学习"
# 6) 为新年级搭建标准五阶段骨架
& $py $skill --scaffold --grade 三年级 --theme 奇石妙想 --year 2025—2026第二学期
```

> 已配置 `config.json` 时，上面的 `--root` 可省略。临时换学校可用 `--root "其他路径"` 或 `--grades 高一,高二,高三`。

---

## 跨校适配小贴士

- **年级分段不同**（高中 / 幼儿园 / 国际部）：改 `grades` 即可，例如 `["小班","中班","大班"]`（数字简写会自动支持）。
- **学年文件夹命名特殊**（如 `2025级`、`七年级上`）：调整 `year_keywords` 或在脚本 `is_year_folder` 处自定义正则。
- **阶段划分不同**：改 `stages` 数组。
- **主题总表**（历年主题 `.doc`/`.docx`）：请用 Word/WPS 手动维护，脚本不读取二进制总表。

---

## 许可证

[MIT](LICENSE) —— 可自由用于任何学校，欢迎修改与再分发。
