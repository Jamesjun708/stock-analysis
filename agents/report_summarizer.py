"""
报告汇总智能体
整合大盘、板块、个股三方报告，生成综合日报
"""

import sys
sys.path.append('..')

from agents.market_analyzer import MarketAnalyzer
from agents.sector_analyzer import SectorAnalyzer
from agents.stock_analyzer import StockAnalyzer
from datetime import datetime
import os


class ReportSummarizer:
    """
    报告汇总智能体
    
    职责：
    1. 调用三个分析智能体生成报告
    2. 整合三方报告内容
    3. 生成综合操作建议
    4. 输出最终日报
    """
    
    def __init__(self):
        self.name = "报告汇总"
        self.market_analyzer = MarketAnalyzer()
        self.sector_analyzer = SectorAnalyzer()
        self.stock_analyzer = StockAnalyzer()
    
    def generate_daily_report(self):
        """
        生成综合日报
        
        返回:
            str: 完整的日报内容
        """
        print("📊 正在生成综合日报...")
        print("  1/4 大盘分析...")
        market_report = self.market_analyzer.generate_report()
        
        print("  2/4 板块分析...")
        sector_report = self.sector_analyzer.generate_report()
        
        print("  3/4 个股分析...")
        stock_report = self.stock_analyzer.generate_report()
        
        print("  4/4 汇总整合...")
        
        # 整合报告
        report_lines = []
        report_lines.append("╔" + "=" * 58 + "╗")
        report_lines.append("║" + " " * 15 + "📊 每日股票分析综合日报" + " " * 18 + "║")
        report_lines.append("║" + f" 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".ljust(58) + "║")
        report_lines.append("╚" + "=" * 58 + "╝")
        report_lines.append("")
        
        # 添加各模块报告
        report_lines.append(market_report)
        report_lines.append("\n" + "=" * 60)
        report_lines.append(sector_report)
        report_lines.append("\n" + "=" * 60)
        report_lines.append(stock_report)
        
        # 综合操作建议
        report_lines.append("\n" + "╔" + "=" * 58 + "╗")
        report_lines.append("║" + " " * 18 + "💡 综合操作建议" + " " * 21 + "║")
        report_lines.append("╚" + "=" * 58 + "╝")
        report_lines.append("")
        report_lines.append("1. 大盘环境: 请参考大盘分析报告")
        report_lines.append("2. 关注板块: 请参考板块分析中的强势板块")
        report_lines.append("3. 个股机会: 请参考个股分析中的技术面强势股")
        report_lines.append("4. 风险提示: 以上分析仅供参考，不构成投资建议")
        report_lines.append("")
        report_lines.append("=" * 60)
        report_lines.append("📌 免责声明: 本报告由AI自动生成，仅供参考学习使用")
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def save_report(self, report, filename=None):
        """
        保存报告到文件
        
        参数:
            report: 报告内容
            filename: 文件名（可选）
        """
        if filename is None:
            filename = f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reports_dir = os.path.join(script_dir, 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        filepath = os.path.join(reports_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return filepath


if __name__ == "__main__":
    # 测试报告汇总
    print("正在初始化报告汇总智能体...")
    summarizer = ReportSummarizer()
    
    print("\n正在生成综合日报...")
    report = summarizer.generate_daily_report()
    
    # 保存报告
    filepath = summarizer.save_report(report)
    print(f"\n✅ 综合日报已保存到: {filepath}")
    
    # 打印摘要
    print("\n📋 报告摘要:")
    print("-" * 60)
    lines = report.split('\n')
    for line in lines[:30]:
        print(line)
    print("...")
