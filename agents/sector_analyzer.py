"""
板块分析智能体 - 张世勇负责
分析热门行业板块资金流向、涨跌幅排行
"""

import sys
import os
sys.path.append('..')

import pandas as pd
import numpy as np
from datetime import datetime
from data.mock_data import generate_sector_performance, generate_sector_flow


class SectorAnalyzer:
    """
    板块分析智能体
    
    职责：
    1. 获取行业板块数据
    2. 分析板块涨跌幅排行
    3. 分析资金流向
    4. 生成板块分析报告
    """
    
    def __init__(self):
        self.name = "板块分析师"
    
    def analyze_sector_performance(self):
        """
        分析板块涨跌幅排行（自动降级到模拟数据）
        """
        use_mock = os.environ.get('STOCK_USE_MOCK', '').lower() in ('1', 'true', 'yes')
        
        if use_mock:
            df = generate_sector_performance()
        else:
            try:
                import akshare as ak
                df = ak.stock_sector_spot()
                df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
                df = df.dropna(subset=['涨跌幅'])
                df = df.sort_values('涨跌幅', ascending=False)
            except Exception as e:
                print(f"  ⚠️ 真实板块数据获取失败 ({e})，使用模拟数据")
                df = generate_sector_performance()
        
        top_gainers = df.head(10)[['板块', '涨跌幅', '总成交额']].to_dict('records')
        top_losers = df.tail(10)[['板块', '涨跌幅', '总成交额']].to_dict('records')
        top_losers.reverse()
        
        return {
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'total_sectors': len(df)
        }
    
    def analyze_sector_flow(self):
        """
        分析板块资金流向（自动降级到模拟数据）
        """
        use_mock = os.environ.get('STOCK_USE_MOCK', '').lower() in ('1', 'true', 'yes')
        if use_mock:
            df = generate_sector_flow()
        else:
            try:
                import akshare as ak
                df = ak.stock_sector_fund_flow_rank()
            except Exception as e:
                print(f"  ⚠️ 真实资金流向获取失败 ({e})，使用模拟数据")
                df = generate_sector_flow()
        
        # 资金流入前10
        inflow = df.head(10)[['名称', '主力净流入-净额', '主力净流入-净占比']].to_dict('records')
        # 资金流出前10
        outflow = df.tail(10)[['名称', '主力净流入-净额', '主力净流入-净占比']].to_dict('records')
        outflow.reverse()
        
        return {'inflow': inflow, 'outflow': outflow}
    
    def generate_report(self):
        """
        生成板块分析报告
        
        返回:
            str: 格式化的分析报告
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📊 每日板块分析报告")
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # 板块涨跌幅分析
        performance = self.analyze_sector_performance()
        if 'error' not in performance:
            report_lines.append(f"\n【板块涨跌排行】(共{performance['total_sectors']}个板块)")
            report_lines.append("-" * 40)
            
            report_lines.append("\n🔥 涨幅前10:")
            for i, sector in enumerate(performance['top_gainers'], 1):
                report_lines.append(f"  {i}. {sector['板块']}: +{sector['涨跌幅']:.2f}%")
            
            report_lines.append("\n❄️ 跌幅前10:")
            for i, sector in enumerate(performance['top_losers'], 1):
                report_lines.append(f"  {i}. {sector['板块']}: {sector['涨跌幅']:.2f}%")
        
        # 资金流向分析
        flow = self.analyze_sector_flow()
        if 'error' not in flow:
            report_lines.append("\n" + "=" * 60)
            report_lines.append("💰 板块资金流向")
            report_lines.append("=" * 60)
            
            report_lines.append("\n📈 资金流入前10:")
            for i, sector in enumerate(flow['inflow'], 1):
                amount = sector.get('主力净流入-净额', 0)
                pct = sector.get('主力净流入-净占比', 0)
                report_lines.append(f"  {i}. {sector['名称']}: {amount/10000:.0f}万 ({pct:.2f}%)")
            
            report_lines.append("\n📉 资金流出前10:")
            for i, sector in enumerate(flow['outflow'], 1):
                amount = sector.get('主力净流入-净额', 0)
                pct = sector.get('主力净流入-净占比', 0)
                report_lines.append(f"  {i}. {sector['名称']}: {amount/10000:.0f}万 ({pct:.2f}%)")
        
        # 综合判断
        report_lines.append("\n" + "=" * 60)
        report_lines.append("📋 板块综合判断")
        report_lines.append("=" * 60)
        
        if 'top_gainers' in performance and len(performance['top_gainers']) > 0:
            top_sector = performance['top_gainers'][0]
            report_lines.append(f"🔥 最强板块: {top_sector['板块']} (+{top_sector['涨跌幅']:.2f}%)")
        
        if 'inflow' in flow and len(flow['inflow']) > 0:
            top_inflow = flow['inflow'][0]
            report_lines.append(f"💰 资金最爱: {top_inflow['名称']}")
        
        report_lines.append("")
        
        return "\n".join(report_lines)


if __name__ == "__main__":
    # 测试板块分析
    print("正在初始化板块分析智能体...")
    analyzer = SectorAnalyzer()
    
    print("\n正在生成分析报告...")
    report = analyzer.generate_report()
    print(report)
    
    # 保存报告
    import os
    os.makedirs('../reports', exist_ok=True)
    with open(f'../reports/sector_report_{datetime.now().strftime("%Y%m%d")}.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 报告已保存到 reports/sector_report_{datetime.now().strftime('%Y%m%d')}.txt")
