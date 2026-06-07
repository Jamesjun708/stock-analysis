"""
股票分析系统主程序
每日自动运行，生成分析报告
"""

from agents.report_summarizer import ReportSummarizer
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
    
    # 生成综合日报
    print("📊 正在生成综合日报...")
    summarizer = ReportSummarizer()
    report = summarizer.generate_daily_report()
    
    # 保存报告
    report_date = datetime.now().strftime("%Y%m%d")
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, f'daily_report_{report_date}.txt')
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✅ 综合日报已保存: {report_path}")
    print("")
    
    # 打印报告摘要
    print("📋 报告摘要:")
    print("-" * 60)
    # 只打印前30行作为摘要
    lines = report.split('\n')
    for line in lines[:30]:
        print(line)
    print("...")
    print("")
    
    print("=" * 60)
    print("✨ 分析完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
