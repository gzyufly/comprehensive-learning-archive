# comprehensive-learning-archive · 项目式综合性学习课程

一个用于 **WorkBuddy** 的技能（Skill），帮助中小学老师按"年级组"快速查询、浏览和维护本校"综合性学习 / 综合实践"项目资料库。

> 本技能**不绑定任何学校**。归档根目录、年级列表、阶段划分全部通过 `config.json` 配置，复制到其他学校只需改这一份配置。

---

## 它能做什么

1. **按年级组 + 学年定位项目**：一键列出某校某年级历年所有综合实践项目（年份、主题、路径、文件数）。
2. **浏览项目内部结构**：打印某年级项目的完整目录树，快速定位开题方案、结题新闻稿、三角模型、展板、视频等。
3. **调整与维护**：新增 / 移动 / 重命名资料，或为新学年、新年级一键搭建标准"五阶段"文件夹骨架。
4. **课程设计与复盘工具引导**：告诉老师不同角色（年级组长 / 项目负责人）在课程设计、目标对齐、任务分解、进度统筹、结题复盘各环节该用哪张表、怎么填、填完归档到哪里，并提供**字段级填写要点**（见 `references/course-design-toolkit.md`）与**空白模板母版**（市场安装包内含 `assets/` 全套 19 个母版）。

---

## 模板库（assets/）与双轨分发

v1.2.0 起技能附带 **19 个空白母版**（`assets/` 扁平存放）：7 张课程设计表单、课程设计和实施结构图（xmind）、整体/单项目进度表、项目设计统筹表（培训版）、复盘纲要、基因卡三件套、3 个培训 PPT，另有《二年级三角模型清单更改》低年段已填范例（已脱敏）。

| 获取方式 | 内容 | 适用 |
|---|---|---|
| **市场安装版**（推荐） | 文档 + 脚本 + `assets/` 全套母版 | 外校老师一键安装，解压即用 |
| **Git 仓库版** | 仅文档 + 脚本 | 想改代码/看结构的开发者；二进制模板受作者本机安全策略限制无法入库 |

> 需要模板但只有仓库版的老师：安装市场版；或运行 `scripts/build_market_package.py` 从本校"综合性学习工具"文件夹重新生成完整包（详见「上架到 WorkBuddy 技能市场」一节）。字段级填写要点不依赖二进制，直接读 `references/course-design-toolkit.md` 第 5 节即可自行制表。

---

## 安装（外校老师）

安装 = 把技能文件夹放进 WorkBuddy 的技能目录 + 填一份 `config.json`。全程约 2 分钟，不需要装额外软件（有 Git 用 Git，没有就直接下载 zip）。

### 第 1 步：拿到技能文件夹

两种方式任选其一：

- **会用 Git（推荐）**，PowerShell 里执行（装到**用户级**目录，之后所有项目都能用）：

  ```powershell
  git clone https://github.com/gzyufly/comprehensive-learning-archive.git "$HOME\.workbuddy\skills\comprehensive-learning-archive"
  ```

- **不会 Git**：在仓库页面点 `Code → Download ZIP`，解压后把里面的 `comprehensive-learning-archive-main` 文件夹**改名为 `comprehensive-learning-archive`**，整体复制到 `C:\Users\你的用户名\.workbuddy\skills\` 下。

> 用户级 = `C:\Users\<你>\.workbuddy\skills\`（所有项目可用）；项目级 = `<你的项目>\.workbuddy\skills\`（仅当前工作区）。普通老师用用户级即可。

### 第 2 步：填 `config.json`（唯一需要动手改的地方）

```powershell
cd "$HOME\.workbuddy\skills\comprehensive-learning-archive"
Copy-Item config.example.json config.json
notepad config.json
```

打开后只改 `root`：把它换成本校"综合性学习"资料的总文件夹，例如 `"D:\\综合性学习"`。其余字段按学校实际情况改（见下方"配置"表）。

> 注意：JSON 里 Windows 路径的反斜杠要**写成双斜杠**（`D:\\综合性学习`），写成单斜杠会让脚本读不到路径。

### 第 3 步：重启 WorkBuddy，直接用自然语言提问

重新打开 WorkBuddy（或新建一个会话），直接说人话即可触发，例如：

> "帮我找一下八年级近几年的综合实践项目，分别在哪个学年、主题是什么"

> WorkBuddy 会自动加载 `~/.workbuddy/skills/` 与项目 `.workbuddy/skills/` 下的技能；若装完没反应，先重启软件再试。

### 验证是否装好了

```powershell
# WorkBuddy 自带 Python（无全局 python 时用这个）
$py = "C:\Users\<你>\.workbuddy\binaries\python\versions\3.13.12\python.exe"
& $py "$HOME\.workbuddy\skills\comprehensive-learning-archive\scripts\index_projects.py" --index
```

能打印出按年级/学年分组的项目清单 = 安装成功。若报错，先检查 `config.json` 里的 `root` 是否写成了真实存在的目录。

### 开发者 / 想改代码

```powershell
git clone https://github.com/gzyufly/comprehensive-learning-archive.git "$HOME\.workbuddy\skills\comprehensive-learning-archive"
cd "$HOME\.workbuddy\skills\comprehensive-learning-archive"
Copy-Item config.example.json config.json   # 再按需编辑
```

---

## 配置（config.json）

技能根目录下的 `config.json` 决定"哪份资料库、怎么识别年级"。从 `config.example.json` 复制后修改：

```json
{
  "root": "H:\\综合性学习",
  "grades": ["九年级","八年级","七年级","六年级","五年级","四年级","三年级","二年级","一年级"],
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

> 以下用 WorkBuddy 受管 Python 演示，`<你>` 换成你自己的 Windows 用户名；如环境有全局 `python`，把 `$py` 直接换成 `python` 即可。

```powershell
$py = "C:\Users\<你>\.workbuddy\binaries\python\versions\3.13.12\python.exe"
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

### 自然语言示例（直接在 WorkBuddy 里说）

- "帮我找一下八年级近几年的综合实践项目，分别在哪个学年、主题是什么"
- "打开 2024—2025 第二学期 三年级 的复盘反思表"
- "**三年级主题课程怎么设计？第一步该填什么表**"
- "**项目任务怎么分解？目标对齐表、统筹表、三角模型分别怎么填**"
- "**项目结题了，复盘反思怎么做、课程基因怎么沉淀**"
- "**有没有空白的大概念表述表 / 对齐表 / 统筹表 / 进度表模板**"

> 后四类问题由 `references/course-design-toolkit.md`（课程设计与复盘工具箱导航）回答：内含 21 个工具文件逐个说明（每张表的关键栏目与母版自带填写说明）、工具 ↔ 归档五阶段对位表、组长线 / 项目负责人线 / 进度线 / 复盘线四条工作主线；空白母版在市场安装包的 `assets/` 内。

**不知道该怎么提问？** 发给老师 `references/prompt-cheatsheet.md`（提示词速查卡）：按年级组长 / 项目负责人 / 结题复盘 / 资料管理员四种角色，各整理了一列可直接复制的提问句式，附"提问技巧"与常见问题。

---

## 跨校适配小贴士

- **年级分段不同**（高中 / 幼儿园 / 国际部）：改 `grades` 即可，例如 `["小班","中班","大班"]`（数字简写会自动支持）。
- **学年文件夹命名特殊**（如 `2025级`、`七年级上`）：调整 `year_keywords` 或在脚本 `is_year_folder` 处自定义正则。
- **阶段划分不同**：改 `stages` 数组。
- **主题总表**（历年主题 `.doc`/`.docx`）：请用 Word/WPS 手动维护，脚本不读取二进制总表。
- **课程设计工具母版**（`综合性学习工具` 文件夹）：可按本校学情修改后使用，技能不绑定学校；工具箱文件名与归档成品高度同源，是"某张表长什么样"的最佳参照。

---

## 发布到远程仓库（开源给外校老师）

本仓库已 `git init` 并提交（首次提交含 7 个文件，`config.json` 故意不纳入版本库，避免泄露各校私有路径）。下面把"推到 Gitee / GitHub"的完整步骤补齐，照做即可让外校老师 `git clone` 安装。

### 第 1 步：在 Gitee / GitHub 网页上新建一个空仓库

- **Gitee**：<https://gitee.com> → 右上角「+」→「新建仓库」→ 仓库名建议 `comprehensive-learning-archive` → 可见性选「公开」→ **不要**勾选「使用 README 初始化仓库」（保持空仓库）→ 创建。
- **GitHub**：<https://github.com> → 右上角「New」→ Repository name 填 `comprehensive-learning-archive` → 选 **Public** → 不勾 Add README → Create repository。

创建后会得到仓库地址（HTTPS 形如 `https://gitee.com/你的名/comprehensive-learning-archive.git` 或 `https://github.com/你的名/comprehensive-learning-archive.git`）。

### 第 2 步：本地关联远程并推送

在本仓库目录下执行（把 `<仓库URL>` 换成你刚拿到的地址）：

```powershell
cd 路径\to\comprehensive-learning-archive
git branch -M main          # 把本地 master 改名为开源惯例的 main
git remote add origin <仓库URL>
git push -u origin main
```

- 公开仓库（`Public`）用 HTTPS 地址即可，推送时按提示输入**账号 + 密码 / 个人访问令牌（PAT）**即可。
- GitHub 自 2021 年起**不再接受账户密码**，请用 **Personal Access Token** 代替密码（Gitee 仍可用密码，也推荐用令牌）。
- 推送成功后，仓库页面就能看到全部文件，把链接（设为 Public）发到教师群即可。

### 第 3 步：把安装说明转给外校老师

仓库设为 Public 后，直接把链接（如 <https://github.com/gzyufly/comprehensive-learning-archive>）发到教师群即可，对方照本文顶部的**「安装（外校老师）」**三步操作：clone 或下载 zip → 复制 `config.example.json` 为 `config.json` 并改 `root` → 重启 WorkBuddy 用自然语言提问。

Windows 一行命令版（对方是 PowerShell 环境时）：

```powershell
git clone <仓库URL> "$HOME\.workbuddy\skills\comprehensive-learning-archive"
cd "$HOME\.workbuddy\skills\comprehensive-learning-archive"; Copy-Item config.example.json config.json
# 编辑 config.json 里的 root 为本校归档根目录，重启 WorkBuddy 即可触发
```

### 私有仓库怎么办（可选）

若资料含敏感信息需私有，把仓库设为 **Private**，外校老师安装时需在 `git clone` 时用 **PAT（勾选 read 权限）** 鉴权；也可直接把仓库打包成 zip 通过企业微信 / 微盘发给对方，对方解压到 `.workbuddy/skills/` 即可，无需 git 账号。

---

## 上架到 WorkBuddy 技能市场（让外校老师一键安装）

如果希望外校老师不用 clone、直接在 WorkBuddy 左侧菜单【专家·技能·连接器】→【技能】→【技能市场】里**搜到并一键安装**，需要把技能提交到腾讯开放平台 / SkillHub 审核，通过后即上架。

### 第 1 步：准备账号

- 打开 <https://open.workbuddy.cn/>，按页面提示完成**入驻、认证与开发者信息审核**；开发者主页建议上传头像、写 20~120 字简介。
- 走 SkillHub 通道则访问 <https://skillhub.cn>，用团队账号点右上角「发布团队 Skill」。

### 第 2 步：准备符合规范的 zip 包

平台规范（据官方技能文档）：

| 项 | 要求 |
|---|---|
| 包结构 | zip 内第一层必须是技能目录：`comprehensive-learning-archive/SKILL.md` |
| 目录层级 | 最多两级（`SKILL.md`、`references/xx.md`、`scripts/xx.py` 均合规） |
| 体积 | ≤ 3MB（v1.3.0 含 `assets/` 模板文件，约 1.9MB，仍在限内但余量有限） |
| 禁止带入 | `.git/`、`config.json`（含本校真实路径）、`~$*`（Office 临时锁文件）、API Key / 密码等隐私信息 |
| 隐私 | 范例文件中的真实教师姓名已在打包时脱敏（替换为"某"） |

本仓库已备好可直接上传的包：`comprehensive-learning-archive-1.3.0.zip`（含 `SKILL.md`、`references/`、`scripts/`、`config.example.json`、`assets/` 19 个母版），已通过官方校验器 `validate_skill` 校验（结果：Skill is valid!）。

**含 `assets/` 的完整包必须用构建脚本生成**（二进制母版不在 Git 仓库里，无法用 Copy-Item 收集）：

```powershell
$py = "C:\Users\<你>\.workbuddy\binaries\python\versions\3.13.12\python.exe"
& $py "路径\to\comprehensive-learning-archive\scripts\build_market_package.py" `
    --source "C:\Users\<你>\AppData\Local\Temp\cla.zip" `
    --out   "路径\to\comprehensive-learning-archive-1.3.0.zip"
```

`--source` 接受两种输入：① 工具箱打包成的 zip（推荐——把本校"综合性学习工具"文件夹整体压缩即可，脚本内存解压、不落盘）；② 工具箱文件夹路径。脚本自动完成：取仓库文档/脚本 → 母版扁平放入 `assets/` → 默认脱敏范例文件中的真实姓名（`--no-desensitize` 可关闭）→ 排除 `~$` 锁文件与 2 个历史版结构图（`--include-history` 可纳入）→ 生成 `assets/母版清单.txt` → 打包后自查（第一层目录、层级、体积、脱敏校验）。

**只打文档版**（不含 assets，体积约 30KB）才用 Compress-Archive，注意此时**没有** `assets` 一行可复制：

```powershell
$src   = "路径\to\comprehensive-learning-archive"
$stage = "$env:TEMP\skillhub\comprehensive-learning-archive"
Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path (Split-Path $stage) -Force | Out-Null
Copy-Item "$src\SKILL.md", "$src\config.example.json", "$src\README.md", "$src\LICENSE" $stage
Copy-Item "$src\references", "$src\scripts" $stage -Recurse
# 注意：-Path 必须指向技能目录本身（不是它的父目录），否则 zip 会多套一层目录导致解析失败
Compress-Archive -Path $stage -DestinationPath "$env:TEMP\comprehensive-learning-archive-1.3.0.zip" -Force
```

### 第 3 步：SKILL.md 必填字段（已按平台规范补齐）

| 字段 | 必填 | 本仓库当前值 |
|---|---|---|
| `name` | 否 | `comprehensive-learning-archive` |
| `display_name` / `display_name_en` | 否 | 项目式综合性学习课程 / Project-Based Comprehensive Learning |
| `description` | **是** | 用途 + 触发词（务必写清"何时触发"，含"可能/也许"等模糊词易被驳回） |
| `description_zh` / `description_en` | **是** | 中英文简短介绍 |
| `version` | **是** | `1.3.0` |
| `author` | **是** | `广州番禺京师奥园南奥实验学校唐术才` |

### 第 4 步：提交审核

1. 在开放平台找到「提交 / 发布 Skill」入口（SkillHub 为右上角「发布团队 Skill」）。
2. 填写标题、简介、分类、触发词预览等元信息，上传 zip 包。
3. 等待审核：**平台安全审核 →（企业账号还需管理员审核）**，通常 1~3 个工作日。
4. 审核通过后在【技能列表】点「上架」，即可在 WorkBuddy 技能市场被搜索、安装。

### 第 5 步：常见驳回原因（提前规避）

- `description` 写成"一个很有用的工具"这类没有触发条件的描述。
- 压缩包里混入 `.git`、缓存文件，或含真实路径的 `config.json`。
- 脚本含网络请求却未在说明中写清域名与用途（**本技能纯本地运行，无任何网络请求**）。
- 缺少使用示例（本技能 SKILL.md 的"何时使用"已内置问答示例）。

---

## 自己更新版本（改内容 → 升版本号 → 重新打包上传）

平台规则：**每次上传的版本号必须严格大于线上最新版本号**。版本号相同或更低会直接报

> 解析失败：包内版本号 "1.0.1" 必须大于当前最新版本 "1.0.1"：请将 SKILL.md 中的 version 递增后重新打包上传

### 1. 版本号怎么升（语义化版本 X.Y.Z）

| 改动类型 | 升哪一位 | 示例 |
|---|---|---|
| 改文案、改署名、修错别字、仅重新打包 | 第三位 Z +1 | 1.0.2 → 1.0.3 |
| 新增能力或参考资料（如新增工具箱引导、新增 references 文档） | 第二位 Y +1，Z 归 0 | 1.0.3 → 1.1.0 |
| 不兼容的结构性改动（改配置字段名、改脚本参数） | 第一位 X +1，Y/Z 归 0 | 1.1.0 → 2.0.0 |

### 2. 四步流程

1. **改内容**：编辑技能目录下的 `SKILL.md` / `scripts/index_projects.py` / `references/folder-structure.md` / `references/course-design-toolkit.md`。
2. **升版本**：把 `SKILL.md` frontmatter 里的 `version` 按上表加一（只改这一处）。
3. **重新打包**：
   - **完整包（含 assets/，外校老师要用的就是这个）**：用构建脚本，一条命令（详见「上架」一节的说明）：

     ```powershell
     & $py "路径\to\comprehensive-learning-archive\scripts\build_market_package.py" --source <工具箱zip或文件夹>
     ```

   - **文档版（不含 assets，约 30KB）**：Compress-Archive，注意**没有** `assets` 一行可复制：

     ```powershell
     $src   = "路径\to\comprehensive-learning-archive"
     $stage = "$env:TEMP\skillhub\comprehensive-learning-archive"
     Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
     New-Item -ItemType Directory -Path (Split-Path $stage) -Force | Out-Null
     Copy-Item "$src\SKILL.md", "$src\config.example.json", "$src\README.md", "$src\LICENSE" $stage
     Copy-Item "$src\references", "$src\scripts" $stage -Recurse
     # 注意：-Path 必须指向技能目录本身，指向父目录会让 zip 多套一层，导致解析失败
     Compress-Archive -Path $stage -DestinationPath "$env:TEMP\comprehensive-learning-archive-<新版本号>.zip" -Force
     ```

4. **自查后上传**：
   - 打开 `SKILL.md` 确认 `version` 已是新号；
   - 双击生成的 zip，确认第一层是 `comprehensive-learning-archive\` 文件夹（不是 `skillhub\` 或 Temp 目录）；
   - 确认包里没有 `.git`、`config.json`、`~$*`；
   - 到开放平台提交新 zip，审核通过后上架。
5. **清理旧包**：新版本上架后，删除本地上一版 zip（如 `comprehensive-learning-archive-1.0.3.zip`），只保留当前版本，避免误传旧包。

### 3. 常见报错对照

| 报错 | 原因 | 处理 |
|---|---|---|
| 包内版本号必须大于当前最新版本 | 版本号没升，或升得不够 | 按上表升一位，改 `SKILL.md` 的 `version` 后重打 |
| 解析失败（结构类） | zip 第一层不是技能目录，或包内混入 `.git` / `config.json` / `~$*` | 用上面的命令重打，别用"直接压缩整个仓库文件夹"的方式 |
| 解析失败（体积类） | 超过 3MB | 裁剪 `assets/`（先删历史版结构图，再删培训 PPT） |
| description 相关驳回 | 触发条件写得含糊 | 保留 `SKILL.md` 现有的 description 写法（已按平台规范写过） |

> 想让 GitHub 上的开源仓库与上架版本保持一致，改完再执行 `git add . ; git commit -m "..." ; git push` 即可；这一步不影响上架审核，可只做上架、不同步仓库。

---

## 许可证

[MIT](LICENSE) —— 可自由用于任何学校，欢迎修改与再分发。
