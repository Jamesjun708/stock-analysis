# 📊 每日股票分析系统

[![每日股票分析](https://github.com/zhujunhao/stock-analysis/actions/workflows/daily_analysis.yml/badge.svg)](https://github.com/zhujunhao/stock-analysis/actions/workflows/daily_analysis.yml)

## 项目信息

- **课程**: 高级数据结构与算法
- **小组**: 朱浩钧、张世勇、孙烨
- **主题**: 基于 OpenClaw 的多智能体协作系统 - 每日股票分析

## 系统架构

```
┌─────────────────────────────────────────┐
│           每日股票分析系统                │
├─────────────────────────────────────────┤
│  定时触发 (GitHub Actions) 每天 9:00    │
├─────────────────────────────────────────┤
│  ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│  │ 大盘分析 │ │ 板块分析 │ │ 个股分析 │  │
│  │ (朱浩钧)│ │ (张世勇)│ │ (孙烨)  │  │
│  └────┬────┘ └────┬────┘ └────┬────┘  │
│       └─────────────┼─────────────┘     │
│                     ▼                   │
│           ┌─────────────┐               │
│           │  报告汇总    │               │
│           │  生成日报    │               │
│           └──────┬──────┘               │
│                  ▼                      │
│           ┌─────────────┐               │
│           │  Web UI /   │               │
│           │  GitHub Pages│               │
│           └─────────────┘               │
└─────────────────────────────────────────┘
```

## 文件结构

```
stock-analysis/
├── main.py                      # 主程序入口（命令行运行）
├── webui.py                     # Web UI 界面（Gradio）
├── requirements.txt             # 依赖包
├── README.md                    # 项目说明
├── .github/workflows/
│   └── daily_analysis.yml       # GitHub Actions 定时任务
├── data/
│   ├── fetcher.py              # 数据获取（自动降级模拟数据）
│   └── mock_data.py            # 模拟数据生成器
├── agents/
│   ├── market_analyzer.py      # 大盘分析智能体 (朱浩钧)
│   ├── sector_analyzer.py      # 板块分析智能体 (张世勇)
│   ├── stock_analyzer.py       # 个股分析智能体 (孙烨)
│   └── report_summarizer.py    # 报告汇总智能体
└── reports/                     # 报告输出目录
```

## 智能体分工

| 智能体 | 负责人 | 职责 |
|--------|--------|------|
| 大盘分析师 | 朱浩钧 | 分析上证指数、深证成指、创业板指等主要指数 |
| 板块分析师 | 张世勇 | 分析热门行业板块资金流向 |
| 个股分析师 | 孙烨 | 分析指定板块内的重点股票 |
| 报告汇总 | 朱浩钧 | 整合三方报告，生成操作建议 |

## 技术栈

- **数据获取**: akshare（免费财经数据接口） + 模拟数据降级
- **数据分析**: pandas, numpy
- **技术指标**: 自定义实现（MA、MACD、RSI等）
- **可视化**: matplotlib, Gradio
- **定时任务**: GitHub Actions
- **Web UI**: Gradio
- **报告展示**: GitHub Pages

## 安装运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行分析（命令行）

```bash
# 真实数据模式（自动降级到模拟数据）
python main.py

# 强制模拟数据模式
STOCK_USE_MOCK=1 python main.py
```

### 3. 启动 Web UI

```bash
python webui.py
# 浏览器打开 http://localhost:7861
```

### 4. 查看报告

报告生成在 `reports/` 目录下，格式为 `daily_report_YYYYMMDD.txt`

## 数据源

- 上证指数 (sh000001)
- 深证成指 (sz399001)
- 创业板指 (sz399006)
- 沪深300 (sh000300)

## 模拟数据模式

当 akshare 数据源不可用时（非交易日、网络问题等），系统自动降级到模拟数据模式：

```bash
# 强制使用模拟数据
export STOCK_USE_MOCK=1   # Linux/Mac
$env:STOCK_USE_MOCK=1     # Windows PowerShell
```

模拟数据基于随机游走算法，走势真实，适合演示和测试。

## GitHub Actions 定时任务

系统每天 **北京时间 09:00** 自动运行分析，流程如下：

1. 检出代码
2. 安装 Python 依赖
3. 运行 `python main.py` 生成日报
4. 将报告提交到仓库
5. 部署到 GitHub Pages 展示

### 手动触发

前往 GitHub 仓库 → Actions → **每日股票分析** → **Run workflow**

### 查看历史报告

部署成功后，访问：

```
https://<你的用户名>.github.io/<仓库名>/
```

## 开发日志

### 2026-06-06
- 初始化项目结构
- 实现数据获取模块 (data/fetcher.py)
- 实现大盘分析智能体 (agents/market_analyzer.py) - 朱浩钧
- 实现主程序入口 (main.py)

### 2026-06-07
- 实现板块分析智能体 (agents/sector_analyzer.py) - 张世勇
- 实现个股分析智能体 (agents/stock_analyzer.py) - 孙烨
- 实现报告汇总智能体 (agents/report_summarizer.py)
- 实现模拟数据模式 (data/mock_data.py)
- 实现 Web UI 界面 (webui.py)
- 配置 GitHub Actions 定时任务
- 更新 README 文档

## 待完成

- [x] 大盘分析智能体
- [x] 板块分析智能体
- [x] 个股分析智能体
- [x] 报告汇总智能体
- [x] 模拟数据模式
- [x] Web UI 界面
- [x] GitHub Actions 定时任务
- [ ] 部署到云服务器
