"""
📊 每日股票分析 - Web UI
基于 Gradio 构建的可视化界面
"""

import sys
import os
import io
import base64

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 强制使用模拟数据（非交易日/无网络时自动生效）
os.environ['STOCK_USE_MOCK'] = '1'

import gradio as gr
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import matplotlib.font_manager as fm
from datetime import datetime

from agents.report_summarizer import ReportSummarizer
from agents.market_analyzer import MarketAnalyzer
from agents.sector_analyzer import SectorAnalyzer
from agents.stock_analyzer import StockAnalyzer

# ── 中文字体 ─────────────────────────────────────
plt.rcParams['axes.unicode_minus'] = False
for fpath in [
    'C:/Windows/Fonts/msyh.ttc',
    'C:/Windows/Fonts/simhei.ttf',
    'C:/Windows/Fonts/SimSun.ttc',
]:
    if os.path.exists(fpath):
        prop = fm.FontProperties(fname=fpath)
        plt.rcParams['font.family'] = prop.get_name()
        break

# ── 全局变量 ─────────────────────────────────────
summarizer = ReportSummarizer()
market_analyzer = MarketAnalyzer()
sector_analyzer = SectorAnalyzer()
stock_analyzer = StockAnalyzer()


# ── 绘图函数 ─────────────────────────────────────
def plot_index_chart(index_code='sh000001', days=60):
    """画指数走势图"""
    from data.fetcher import get_index_data
    df = get_index_data(index_code, days)
    if df is None or len(df) < 5:
        return None

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5),
                                   gridspec_kw={'height_ratios': [3, 1]},
                                   sharex=True)
    fig.patch.set_facecolor('#f8f9fa')

    # ── 价格 + MA ──
    ax1.plot(df['date'], df['close'], linewidth=1.5, color='#1a73e8', label='收盘价')
    if 'MA5' in df.columns:
        ax1.plot(df['date'], df['MA5'], linewidth=0.8, color='#f9a825', alpha=0.8, label='MA5')
    if 'MA20' in df.columns:
        ax1.plot(df['date'], df['MA20'], linewidth=0.8, color='#e53935', alpha=0.8, label='MA20')
    ax1.fill_between(df['date'], df['close'], alpha=0.1, color='#1a73e8')
    ax1.set_ylabel('价格')
    ax1.legend(fontsize=8, loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.set_title(f'{index_code} 走势', fontsize=13, fontweight='bold')

    # ── 成交量 ──
    colors = ['#ef5350' if c < 0 else '#26a69a' for c in df['change_pct'].tail(len(df))]
    ax2.bar(df['date'], df['volume'], color=colors, alpha=0.6, width=0.6)
    ax2.set_ylabel('成交量')
    ax2.grid(True, alpha=0.3)

    plt.xticks(rotation=45, fontsize=7)
    plt.tight_layout()
    return fig


def plot_sector_chart():
    """板块涨跌排行柱状图"""
    result = sector_analyzer.analyze_sector_performance()
    if 'error' in result:
        return None

    gainers = result['top_gainers'][:8]
    losers = result['top_losers'][-8:]
    top = gainers + losers

    names = [s['板块'] for s in top]
    changes = [s['涨跌幅'] for s in top]
    colors = ['#ef5350' if c < 0 else '#26a69a' for c in changes]

    fig, ax = plt.subplots(figsize=(10, 4.5))
    fig.patch.set_facecolor('#f8f9fa')
    bars = ax.barh(names, changes, color=colors, alpha=0.75, height=0.6)
    for bar, v in zip(bars, changes):
        ax.text(bar.get_width() + 0.1 if v > 0 else bar.get_width() - 0.1,
                bar.get_y() + bar.get_height() / 2,
                f'{v:+.2f}%', va='center', fontsize=9,
                ha='left' if v > 0 else 'right')
    ax.axvline(0, color='gray', linewidth=0.8)
    ax.set_xlabel('涨跌幅 (%)')
    ax.set_title('板块涨跌排行 Top8', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    return fig


def plot_stock_chart():
    """个股 K 线/走势"""
    stocks = stock_analyzer.get_hot_stocks(top_n=5)
    fig, axes = plt.subplots(1, 5, figsize=(14, 3))
    fig.patch.set_facecolor('#f8f9fa')

    for i, code in enumerate(stocks[:5]):
        ax = axes[i]
        result = stock_analyzer.analyze_stock(code)
        if 'error' in result:
            ax.text(0.5, 0.5, 'N/A', ha='center', transform=ax.transAxes)
            continue

        # 用模拟数据画走势
        from data.mock_data import generate_stock_data
        df, name = generate_stock_data(code)
        prices = df['收盘'].values
        ax.plot(prices, linewidth=1.5, color='#1a73e8')
        ax.fill_between(range(len(prices)), prices, alpha=0.1, color='#1a73e8')
        ax.set_title(f'{result["name"]}\n{result["change_5d"]:+.1f}%', fontsize=8)
        ax.set_xticks([])
        ax.grid(True, alpha=0.2)

    plt.suptitle('热门个股走势', fontsize=13, fontweight='bold', y=1.05)
    plt.tight_layout()
    return fig


# ── 核心逻辑 ─────────────────────────────────────
def run_analysis():
    """运行全部分析，返回各模块结果"""
    print("🔍 正在运行分析...")

    # 综合日报
    report_text = summarizer.generate_daily_report()

    # 大盘图表
    idx_charts = {}
    for code in ['sh000001', 'sz399001', 'sz399006', 'sh000300']:
        fig = plot_index_chart(code)
        if fig:
            idx_charts[code] = fig
            plt.close(fig)

    # 板块图表
    sector_fig = plot_sector_chart()
    if sector_fig:
        plt.close(sector_fig)

    # 个股图表
    stock_fig = plot_stock_chart()
    if stock_fig:
        plt.close(stock_fig)

    return report_text, idx_charts, sector_fig, stock_fig


def get_dashboard():
    """首页看板"""
    report_text, idx_charts, sector_fig, stock_fig = run_analysis()

    # 提取关键指标
    market_report = market_analyzer.generate_report()
    sector_report = sector_analyzer.generate_report()
    stock_report = stock_analyzer.generate_report()

    return (
        report_text,           # 综合日报
        report_text[:500],     # 大盘摘要
        idx_charts.get('sh000001'),
        idx_charts.get('sz399001'),
        idx_charts.get('sz399006'),
        idx_charts.get('sh000300'),
        sector_fig,
        stock_fig,
    )


# ── 构建 UI ─────────────────────────────────────
CSS = """
.gradio-container { max-width: 1200px !important; }
.tab-nav { font-size: 16px !important; }
h1 span { background: linear-gradient(135deg, #1a73e8, #e53935); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
"""

with gr.Blocks(title="📊 每日股票分析系统") as demo:
    gr.HTML("""
    <div style="text-align:center; padding:20px 0 10px;">
        <h1 style="font-size:28px; font-weight:700; letter-spacing:1px;">
            📊 每日股票分析系统
        </h1>
        <p style="color:#666; font-size:14px;">
            基于多智能体协作的 A 股市场分析平台 · 
            <span id="gen-time" style="color:#1a73e8;">""" + datetime.now().strftime('%Y-%m-%d %H:%M') + """</span>
        </p>
    </div>
    """)

    with gr.Row():
        run_btn = gr.Button("🚀 运行分析", variant="primary", scale=1, size="lg")
        status = gr.Markdown("就绪 ✅")

    with gr.Tabs() as tabs:
        # ── Tab1: 综合日报 ──
        with gr.TabItem("📋 综合日报"):
            report_output = gr.Textbox(label="", lines=35, max_lines=50)

        # ── Tab2: 大盘分析 ──
        with gr.TabItem("📈 大盘分析"):
            with gr.Row():
                with gr.Column(scale=1):
                    market_summary = gr.Textbox(label="大盘摘要", lines=10)
                with gr.Column(scale=2):
                    with gr.Tabs():
                        with gr.TabItem("上证指数"):
                            idx1 = gr.Plot(label="上证指数")
                        with gr.TabItem("深证成指"):
                            idx2 = gr.Plot(label="深证成指")
                        with gr.TabItem("创业板指"):
                            idx3 = gr.Plot(label="创业板指")
                        with gr.TabItem("沪深300"):
                            idx4 = gr.Plot(label="沪深300")

        # ── Tab3: 板块分析 ──
        with gr.TabItem("🏭 板块分析"):
            sector_plot = gr.Plot(label="板块涨跌排行")

        # ── Tab4: 个股分析 ──
        with gr.TabItem("💎 个股分析"):
            stock_plot = gr.Plot(label="热门个股走势")

    # ── 按钮事件 ──
    def on_run():
        status_text = "⏳ 运行中..."
        r, ms, i1, i2, i3, i4, s, st = get_dashboard()
        status_text = "✅ 分析完成！"
        return r, ms, i1, i2, i3, i4, s, st, status_text

    run_btn.click(
        fn=on_run,
        outputs=[report_output, market_summary, idx1, idx2, idx3, idx4,
                 sector_plot, stock_plot, status],
    )

    # ── 自动加载 ──
    demo.load(
        fn=get_dashboard,
        outputs=[report_output, market_summary, idx1, idx2, idx3, idx4,
                 sector_plot, stock_plot],
    )

if __name__ == "__main__":
    print("=" * 50)
    print("📊 每日股票分析系统 - Web UI")
    print("=" * 50)
    print("启动中...")
    port = int(os.environ.get("GRADIO_SERVER_PORT", "7861"))
    demo.launch(server_name="0.0.0.0", server_port=port, share=False,
               css=CSS, theme=gr.themes.Soft())
