"""
大盘分析智能体 - 朱浩钧负责
分析上证指数、深证成指、创业板指等主要指数
"""

import sys
sys.path.append('..')

from data.fetcher import get_index_data, get_realtime_index, get_index_list
import pandas as pd
import numpy as np
from datetime import datetime


class MarketAnalyzer:
    """
    大盘分析智能体
    
    职责：
    1. 获取主要指数数据
    2. 计算技术指标（均线、MACD、RSI等）
    3. 分析市场趋势
    4. 生成大盘分析报告
    """
    
    def __init__(self):
        self.name = "大盘分析师"
        self.indices = {
            'sh000001': '上证指数',
            'sz399001': '深证成指',
            'sz399006': '创业板指',
            'sh000300': '沪深300'
        }
    
    def calculate_ma(self, df, periods=[5, 10, 20, 60]):
        """计算移动平均线"""
        for period in periods:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    def calculate_rsi(self, df, period=14):
        """计算RSI指标"""
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        return df
    
    def calculate_macd(self, df, fast=12, slow=26, signal=9):
        """计算MACD指标"""
        ema_fast = df['close'].ewm(span=fast).mean()
        ema_slow = df['close'].ewm(span=slow).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=signal).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        return df
    
    def analyze_trend(self, df):
        """分析趋势"""
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 价格趋势
        price_trend = "上涨" if latest['close'] > prev['close'] else "下跌"
        
        # 均线判断
        ma_bullish = latest['close'] > latest.get('MA20', 0)
        
        # RSI判断
        rsi = latest.get('RSI', 50)
        if rsi > 70:
            rsi_signal = "超买"
        elif rsi < 30:
            rsi_signal = "超卖"
        else:
            rsi_signal = "中性"
        
        # MACD判断
        macd_hist = latest.get('MACD_Hist', 0)
        macd_signal = "多头" if macd_hist > 0 else "空头"
        
        return {
            'price_trend': price_trend,
            'ma_bullish': ma_bullish,
            'rsi': rsi,
            'rsi_signal': rsi_signal,
            'macd_signal': macd_signal,
            'volume_trend': "放量" if latest['volume'] > prev['volume'] * 1.2 else "缩量"
        }
    
    def analyze_index(self, index_code='sh000001', days=60):
        """
        分析单个指数
        
        参数:
            index_code: 指数代码
            days: 分析最近多少天
            
        返回:
            dict: 分析结果
        """
        # 获取数据
        df = get_index_data(index_code, days)
        if df is None or len(df) < 20:
            return {'error': '数据获取失败或数据不足'}
        
        # 计算指标
        df = self.calculate_ma(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        
        # 分析趋势
        trend = self.analyze_trend(df)
        
        # 最新数据
        latest = df.iloc[-1]
        
        # 涨跌幅统计
        change_5d = (latest['close'] - df.iloc[-5]['close']) / df.iloc[-5]['close'] * 100 if len(df) >= 5 else 0
        change_20d = (latest['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close'] * 100 if len(df) >= 20 else 0
        
        return {
            'index_name': self.indices.get(index_code, index_code),
            'index_code': index_code,
            'date': latest['date'],
            'close': round(latest['close'], 2),
            'change': round(latest['change'], 2),
            'change_pct': round(latest['change_pct'], 2),
            'volume': int(latest['volume']),
            'trend': trend,
            'change_5d': round(change_5d, 2),
            'change_20d': round(change_20d, 2),
            'ma5': round(latest.get('MA5', 0), 2),
            'ma20': round(latest.get('MA20', 0), 2),
            'rsi': round(latest.get('RSI', 0), 2),
            'macd_signal': trend['macd_signal']
        }
    
    def generate_report(self):
        """
        生成大盘分析报告
        
        返回:
            str: 格式化的分析报告
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📊 每日大盘分析报告")
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        # 分析主要指数
        all_analysis = []
        for code in ['sh000001', 'sz399001', 'sz399006', 'sh000300']:
            analysis = self.analyze_index(code)
            if 'error' not in analysis:
                all_analysis.append(analysis)
        
        # 生成报告内容
        for analysis in all_analysis:
            report_lines.append(f"\n【{analysis['index_name']}】({analysis['index_code']})")
            report_lines.append("-" * 40)
            report_lines.append(f"最新收盘: {analysis['close']}")
            report_lines.append(f"今日涨跌: {analysis['change']} ({analysis['change_pct']}%)")
            report_lines.append(f"5日涨跌: {analysis['change_5d']}%")
            report_lines.append(f"20日涨跌: {analysis['change_20d']}%")
            report_lines.append(f"成交量: {analysis['volume']:,}")
            report_lines.append("")
            report_lines.append(f"技术指标:")
            report_lines.append(f"  - 均线趋势: {'多头排列' if analysis['trend']['ma_bullish'] else '空头排列'}")
            report_lines.append(f"  - RSI(14): {analysis['rsi']} ({analysis['trend']['rsi_signal']})")
            report_lines.append(f"  - MACD: {analysis['trend']['macd_signal']}")
            report_lines.append(f"  - 量能: {analysis['trend']['volume_trend']}")
            report_lines.append("")
        
        # 综合判断
        report_lines.append("\n" + "=" * 60)
        report_lines.append("📈 综合判断")
        report_lines.append("=" * 60)
        
        # 简单判断逻辑
        bullish_count = sum(1 for a in all_analysis if a['trend']['ma_bullish'])
        if bullish_count >= 3:
            market_view = "强势市场 - 多数指数站上20日均线，建议积极配置"
        elif bullish_count >= 2:
            market_view = "震荡偏强 - 市场分化，建议精选板块"
        else:
            market_view = "弱势市场 - 多数指数承压，建议谨慎观望"
        
        report_lines.append(f"市场观点: {market_view}")
        report_lines.append("")
        
        return "\n".join(report_lines)


if __name__ == "__main__":
    # 测试大盘分析
    print("正在初始化大盘分析智能体...")
    analyzer = MarketAnalyzer()
    
    print("\n正在生成分析报告...")
    report = analyzer.generate_report()
    print(report)
    
    # 保存报告
    import os
    os.makedirs('../reports', exist_ok=True)
    with open(f'../reports/market_report_{datetime.now().strftime("%Y%m%d")}.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 报告已保存到 reports/market_report_{datetime.now().strftime('%Y%m%d')}.txt")
