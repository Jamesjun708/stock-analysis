"""
个股分析智能体 - 孙烨负责
分析指定板块内的重点股票（自动降级到模拟数据）
"""

import sys
import os
import time
import importlib
sys.path.append('..')

import pandas as pd
import numpy as np
from datetime import datetime
from data.mock_data import generate_stock_data as mock_stock_data
from data.mock_data import generate_hot_stocks as mock_hot_stocks


class StockAnalyzer:
    """
    个股分析智能体
    
    职责：
    1. 获取个股历史数据
    2. 计算技术指标
    3. 筛选强势个股
    4. 生成个股分析报告
    """
    
    def __init__(self):
        self.name = "个股分析师"
    
    def calculate_indicators(self, df):
        """计算技术指标"""
        for period in [5, 10, 20, 60]:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
        
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        ema_fast = df['close'].ewm(span=12).mean()
        ema_slow = df['close'].ewm(span=26).mean()
        df['MACD'] = ema_fast - ema_slow
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()
        
        return df
    
    def analyze_stock(self, stock_code, days=60):
        """
        分析单只股票（自动降级到模拟数据）
        """
        use_mock = os.environ.get('STOCK_USE_MOCK', '').lower() in ('1', 'true', 'yes')
        
        if use_mock:
            return self._analyze_from_df(stock_code, days)
        
        for attempt in range(2):
            try:
                import akshare as ak
                raw = ak.stock_zh_a_hist(
                    symbol=stock_code, period="daily",
                    start_date=(datetime.now() - pd.Timedelta(days=days)).strftime("%Y%m%d"),
                    end_date=datetime.now().strftime("%Y%m%d"),
                )
                if raw is None or len(raw) < 20:
                    raise ValueError("数据不足")
                
                df = raw.rename(columns={
                    '日期': 'date', '收盘': 'close',
                    '涨跌幅': 'change_pct', '成交量': 'volume', '成交额': 'amount',
                })
                return self._analyze_from_df(stock_code, days, df)
            except Exception as e:
                if attempt == 0:
                    time.sleep(2)
                else:
                    print(f"  ⚠️ 真实个股数据获取失败，使用模拟数据")
                    return self._analyze_from_df(stock_code, days)
    
    def _analyze_from_df(self, stock_code, days=60, df=None):
        """从 DataFrame（真实或模拟）提取分析结果"""
        try:
            if df is None:
                df, stock_name = mock_stock_data(stock_code, days)
                df = df.rename(columns={'日期': 'date', '收盘': 'close', '涨跌幅': 'change_pct', '成交量': 'volume', '成交额': 'amount'})
            else:
                stock_info = __import__('akshare').stock_individual_info_em(symbol=stock_code)
                stock_name = stock_info['股票简称'].values[0] if not stock_info.empty else stock_code
            
            df = self.calculate_indicators(df)
            latest = df.iloc[-1]
            
            change_5d = (latest['close'] - df.iloc[-5]['close']) / df.iloc[-5]['close'] * 100
            change_20d = (latest['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close'] * 100
            
            return {
                'code': stock_code, 'name': stock_name,
                'close': round(latest['close'], 2),
                'change_pct': round(latest['change_pct'], 2),
                'change_5d': round(change_5d, 2),
                'change_20d': round(change_20d, 2),
                'volume': int(latest['volume']),
                'rsi': round(latest['RSI'], 2),
                'ma_bullish': latest['close'] > latest['MA20'],
                'macd_bullish': latest['MACD'] > latest['MACD_Signal'],
            }
        except Exception as e:
            return {'error': str(e), 'code': stock_code}
    
    def get_hot_stocks(self, sector=None, top_n=20):
        """
        获取热门股票列表（自动降级到模拟数据）
        """
        use_mock = os.environ.get('STOCK_USE_MOCK', '').lower() in ('1', 'true', 'yes')
        if use_mock:
            return mock_hot_stocks(top_n)
        
        try:
            import akshare as ak
            pool = ak.stock_zt_pool_em(date=datetime.now().strftime("%Y%m%d"))
            if pool is not None and not pool.empty:
                return pool['代码'].head(top_n).tolist()
            
            spot = ak.stock_zh_a_spot_em()
            spot = spot.sort_values('成交额', ascending=False)
            return spot['代码'].head(top_n).tolist()
        except Exception:
            return mock_hot_stocks(top_n)
    
    def generate_report(self, stock_list=None):
        """
        生成个股分析报告
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("📊 每日个股分析报告")
        report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 60)
        report_lines.append("")
        
        if stock_list is None:
            stock_list = self.get_hot_stocks()
        
        report_lines.append(f"分析股票数量: {len(stock_list)}只")
        report_lines.append("")
        
        all_analysis = []
        for code in stock_list:
            analysis = self.analyze_stock(code)
            if 'error' not in analysis:
                all_analysis.append(analysis)
        
        all_analysis.sort(key=lambda x: x['change_5d'], reverse=True)
        
        report_lines.append("\n【强势股排行】(按5日涨幅)")
        report_lines.append("-" * 60)
        for i, stock in enumerate(all_analysis[:10], 1):
            flag = "🚀" if stock['ma_bullish'] and stock['macd_bullish'] else ""
            report_lines.append(
                f"{i:2d}. {stock['name']}({stock['code']}) "
                f"收盘价: {stock['close']} "
                f"5日: {stock['change_5d']:+.2f}% "
                f"20日: {stock['change_20d']:+.2f}% "
                f"RSI: {stock['rsi']:.1f} {flag}"
            )
        
        strong = [s for s in all_analysis if s['ma_bullish'] and s['macd_bullish'] and s['rsi'] < 70]
        
        report_lines.append("\n" + "=" * 60)
        report_lines.append("🎯 技术面强势个股 (均线+MACD多头，RSI未超买)")
        report_lines.append("=" * 60)
        if strong:
            for s in strong[:5]:
                report_lines.append(f"• {s['name']}({s['code']}) - 5日涨幅: {s['change_5d']:+.2f}%, RSI: {s['rsi']:.1f}")
        else:
            report_lines.append("当前未发现符合技术面强势特征的个股")
        
        report_lines.append("")
        return "\n".join(report_lines)


if __name__ == "__main__":
    print("正在初始化个股分析智能体...")
    analyzer = StockAnalyzer()
    print("\n正在生成分析报告...")
    report = analyzer.generate_report()
    print(report)
    
    import os
    os.makedirs('../reports', exist_ok=True)
    with open(f'../reports/stock_report_{datetime.now().strftime("%Y%m%d")}.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\n✅ 报告已保存")
