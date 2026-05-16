# My Words - 每日 Newsletter & 个人日记

自动从多个技术新闻源抓取内容，使用 LLM 生成每日技术 Newsletter，并支持个人日记/复盘功能。

## 功能特性

- **每日技术 Newsletter**：自动从 AI News、GitHub Trending、少数派、V2EX、美团技术、36氪等渠道抓取并生成摘要
- **个人日记/复盘**：支持每日复盘日记，包含今日完成、学习、思考、问题、计划等模块
- **自动化运行**：通过 GitHub Actions 每日自动执行
- **本地存储**：所有内容保存在 Git 仓库中，便于版本管理和回溯

## 快速开始

### 1. 克隆仓库

```bash
git clone <your-repo-url>
cd my-words
```

### 2. 配置环境变量（可选）

在 `script/newsletter` 目录下创建 `.env` 文件，配置以下环境变量：

```env
# Newsletter 输出目录（可选，默认为项目根目录下的 newsletters）
# NEWSLETTER_DIR=/path/to/newsletters

# PushDeer 推送密钥（可选，用于发送推送通知）
# PUSH_DEER_KEY=your_push_deer_key
```

### 3. 安装依赖

```bash
# 使用 uv 安装（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 4. 运行

```bash
# 生成 newsletter + 空日记模板
uv run main.py

# 只生成 newsletter
uv run main.py newsletter

# 只生成日记模板
uv run main.py diary
```

## GitHub Actions 自动化

### 配置 Secrets

在 GitHub 仓库的 Settings -> Secrets and variables -> Actions 中添加以下 secrets：

| Secret 名称 | 说明 |
|-------------|------|
| `PAT` | GitHub Personal Access Token（需要 repo 权限） |
| `PUSH_DEER_KEY` | PushDeer 推送密钥（可选） |

### 工作流说明

- `generate-newsletter.yml`：每日北京时间 8:00 自动生成 newsletter 和日记模板

## 目录结构

```
my-words/
├── newsletters/              # Newsletter 和日记输出目录
│   ├── homepage.md          # Newsletter 主页
│   ├── diary_homepage.md    # 日记主页
│   └── 2025-06-22/          # 日期目录
│       ├── newsletter.md    # 当日 newsletter
│       ├── diary.md         # 当日日记
│       └── ...              # 各渠道原始内容
├── posts/                   # 博客文章
├── script/
│   └── newsletter/          # Newsletter 生成脚本
│       ├── main.py          # 主入口
│       ├── newsletter.py    # Newsletter 生成逻辑
│       ├── diary.py         # 日记生成逻辑
│       ├── config.py        # 配置管理
│       ├── push.py          # 推送通知
│       ├── news_utils.py    # 公共工具函数
│       └── news_*.py        # 各渠道抓取脚本
└── .github/
    └── workflows/           # GitHub Actions 配置
```

## 新闻源

| 渠道 | 说明 |
|------|------|
| AI News | AI 领域最新动态 |
| GitHub Trending | GitHub 热门项目 |
| 少数派 | 优质技术文章 |
| V2EX | 技术讨论社区 |
| 美团技术团队 | 美团技术博客 |
| 36kr | 科技新闻 |

## 自定义

### 修改新闻源

编辑 `script/newsletter/newsletter.py` 中的 `generate_newsletter` 函数，调整新闻源组合。

### 修改日记模板

编辑 `script/newsletter/diary.py` 中的 `get_diary_template` 函数。

### 添加新新闻源

1. 在 `script/newsletter/` 下创建新的 `news_xxx.py` 文件
2. 实现 `get_today_news_content()` 和 `get_today_news_file()` 函数
3. 在 `newsletter.py` 中引入并使用

## 许可证

MIT License