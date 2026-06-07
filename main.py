"""
股票分析系统主程序
每日自动运行，生成分析报告
"""

from agents.market_analyzer import MarketAnalyzer
from datetime import datetime
import os


def main():
    """
    主函数 - 运行所有分析
    """
    print("=" * 60)
    print("🚀 股票分析系统启动")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print("")
    
    # 创建报告目录
    os.makedirs('reports', exist_ok=True)
    
    # 1. 大盘分析
    print("📊 正在运行大盘分析...")
    market_analyzer = MarketAnalyzer()
    market_report = market_analyzer.generate_report()
    
    # 保存报告
    report_date = datetime.now().strftime("%Y%m%d")
    report_path = f'reports/daily_report_{report_date}.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(market_report)
    
    print(f"✅ 大盘分析完成，报告已保存: {report_path}")
    print("")
    
    # 打印报告摘要
    print("📋 报告摘要:")
    print("-" * 60)
    # 只打印前20行作为摘要
    lines = market_report.split('\n')
    for line in lines[:25]:
        print(line)
    print("...")
    print("")
    
    print("=" * 60)
    print("✨ 分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
