"""
数据获取模块 - 获取大盘指数数据
支持多数据源：akshare(A股) / yfinance(全球) / 模拟数据(演示)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 尝试导入 akshare，如果失败则使用 yfinance
try:
    import akshare as ak
    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("[!] akshare 未安装，使用 yfinance 作为备选")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


def generate_mock_data(index_code="sh000001", days=30):
    """
    生成模拟股票数据（用于演示和测试）
    """
    # 设置随机种子，使数据可重复
    np.random.seed(hash(index_code) % 2**32)
    
    # 基础价格根据指数不同
    base_prices = {
        'sh000001': 2880,
        'sz399001': 8800,
        'sz399006': 1700,
        'sh000300': 3400
    }
    
    base_price = base_prices.get(index_code, 3000)
    
    # 生成日期序列
    dates = []
    current = datetime.now() - timedelta(days=days)
    for i in range(days):
        # 跳过周末
        if current.weekday() < 5:
            dates.append(current)
        current += timedelta(days=1)
    
    # 生成价格数据（随机游走）
    n = len(dates)
    returns = np.random.normal(0.001, 0.02, n)  # 日均收益0.1%，波动2%
    prices = base_price * np.exp(np.cumsum(returns))
    
    # 生成OHLC数据
    data = []
    for i, date in enumerate(dates):
        price = prices[i]
        high = price * (1 + abs(np.random.normal(0, 0.01)))
        low = price * (1 - abs(np.random.normal(0, 0.01)))
        open_price = price * (1 + np.random.normal(0, 0.005))
        volume = int(np.random.normal(300000000, 50000000))
        
        change = price - (prices[i-1] if i > 0 else price)
        change_pct = (change / (prices[i-1] if i > 0 else price)) * 100
        
        data.append({
            'date': date.strftime('%Y-%m-%d'),
            'open': round(open_price, 2),
            'close': round(price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'volume': max(volume, 100000000),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2)
        })
    
    df = pd.DataFrame(data)
    return df


def get_index_data_yfinance(symbol="^GSPC", days=30):
    """
    使用 yfinance 获取指数数据（美股指数）
    """
    if not YFINANCE_AVAILABLE:
        return None
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        ticker = yf.Ticker(symbol)
        df = ticker.history(start=start_date, end=end_date)
        
        if df.empty:
            return None
        
        df = df.reset_index()
        
        df = df.rename(columns={
            'Date': 'date',
            'Open': 'open',
            'Close': 'close',
            'High': 'high',
            'Low': 'low',
            'Volume': 'volume'
        })
        
        df['change'] = df['close'].diff()
        df['change_pct'] = df['close'].pct_change() * 100
        
        return df
    except Exception as e:
        print(f"yfinance 获取数据失败: {e}")
        return None


def get_index_data_akshare(index_code="sh000001", days=30):
    """
    使用 akshare 获取A股指数数据
    """
    if not AKSHARE_AVAILABLE:
        return None
    
    try:
        df = ak.index_zh_a_hist(
            symbol=index_code, 
            period="daily",
            start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
            end_date=datetime.now().strftime("%Y%m%d")
        )
        
        df = df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume',
            '涨跌幅': 'change_pct',
            '涨跌额': 'change'
        })
        
        return df
    except Exception as e:
        print(f"akshare 获取数据失败: {e}")
        return None


def get_index_data(index_code="sh000001", days=30):
    """
    统一的指数数据获取接口
    
    优先级：akshare > yfinance > 模拟数据
    """
    # 尝试 akshare
    if AKSHARE_AVAILABLE:
        df = get_index_data_akshare(index_code, days)
        if df is not None and not df.empty:
            return df
    
    # 尝试 yfinance
    if YFINANCE_AVAILABLE:
        yf_mapping = {
            'sh000001': '000001.SS',
            'sz399001': '399001.SZ',
            'sz399006': '399006.SZ',
            'sh000300': '000300.SS'
        }
        yf_symbol = yf_mapping.get(index_code, index_code)
        df = get_index_data_yfinance(yf_symbol, days)
        if df is not None and not df.empty:
            return df
    
    # 使用模拟数据
    print(f"[!] 使用模拟数据生成 {index_code} 的数据")
    return generate_mock_data(index_code, days)


def get_realtime_index():
    """
    获取实时指数数据（使用模拟数据演示）
    """
    indices = {
        'sh000001': {'name': '上证指数', 'base': 2880},
        'sz399001': {'name': '深证成指', 'base': 8800},
        'sz399006': {'name': '创业板指', 'base': 1700},
        'sh000300': {'name': '沪深300', 'base': 3400}
    }
    
    result = {}
    np.random.seed(int(datetime.now().timestamp()) % 1000)
    
    for code, info in indices.items():
        change_pct = np.random.normal(0, 1.5)  # 随机涨跌幅
        price = info['base'] * (1 + change_pct/100)
        change = price - info['base']
        
        result[code] = {
            'name': info['name'],
            'price': round(price, 2),
            'change': round(change, 2),
            'change_pct': round(change_pct, 2)
        }
    
    return result


def get_index_list():
    """获取支持的指数列表"""
    return {
        'sh000001': '上证指数',
        'sz399001': '深证成指',
        'sz399006': '创业板指',
        'sh000300': '沪深300'
    }


if __name__ == "__main__":
    print("=== 测试数据获取 ===")
    
    # 测试上证指数
    print("\n1. 上证指数:")
    df = get_index_data("sh000001", days=5)
    if df is not None:
        print(df[['date', 'close', 'change_pct', 'volume']].tail())
    
    # 测试深证成指
    print("\n2. 深证成指:")
    df = get_index_data("sz399001", days=5)
    if df is not None:
        print(df[['date', 'close', 'change_pct', 'volume']].tail())
    
    # 测试实时数据
    print("\n3. 实时数据:")
    realtime = get_realtime_index()
    if realtime:
        for code, data in realtime.items():
            print(f"{data['name']}({code}): {data['price']} ({data['change_pct']}%)")
