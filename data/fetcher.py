"""
数据获取模块 - 获取大盘指数数据
使用 akshare 免费库，自动降级到模拟数据模式
"""

import os
import time
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
from data.mock_data import generate_index_data as mock_index_data

# 通过环境变量强制模拟模式（方便测试）
USE_MOCK = os.environ.get('STOCK_USE_MOCK', '').lower() in ('1', 'true', 'yes')


def get_index_data(index_code="sh000001", days=30):
    """
    获取指数历史数据（自动降级到模拟数据）
    
    参数:
        index_code: 指数代码
        days: 获取最近多少天的数据
    
    返回:
        DataFrame: 包含日期、开盘、收盘、最高、最低、成交量
    """
    # 如果强制 mock 模式，直接返回模拟数据
    if USE_MOCK:
        print(f"  ℹ️ [模拟] {index_code}")
        return mock_index_data(index_code, days)
    
    # 尝试真实数据（最多重试2次）
    for attempt in range(3):
        try:
            raw = ak.index_zh_a_hist(
                symbol=index_code, period="daily",
                start_date=(datetime.now() - timedelta(days=days)).strftime("%Y%m%d"),
                end_date=datetime.now().strftime("%Y%m%d"),
            )
            if raw is None or raw.empty:
                raise ValueError("返回数据为空")

            df = raw.rename(columns={
                '日期': 'date', '开盘': 'open', '收盘': 'close',
                '最高': 'high', '最低': 'low', '成交量': 'volume',
                '成交额': 'amount', '振幅': 'amplitude',
                '涨跌幅': 'change_pct', '涨跌额': 'change',
                '换手率': 'turnover',
            })
            return df

        except Exception as e:
            if attempt < 2:
                print(f"  重试 {attempt+1}/3...", end="")
                time.sleep(2)
            else:
                print(f"  ⚠️ 真实数据获取失败 ({e})，使用模拟数据")
                return mock_index_data(index_code, days)


def get_realtime_index():
    """
    获取实时大盘指数数据（失败时返回模拟数据）
    """
    try:
        df = ak.stock_zh_index_spot()
        main_codes = ['sh000001', 'sz399001', 'sz399006', 'sh000300']
        result = {}
        for _, row in df.iterrows():
            code = row['代码']
            if code in main_codes:
                result[code] = {
                    'name': row['名称'],
                    'price': row['最新价'],
                    'change': row['涨跌额'],
                    'change_pct': row['涨跌幅'],
                    'volume': row['成交量'],
                    'amount': row['成交额'],
                }
        if result:
            return result
        raise ValueError("未找到主要指数")
    except Exception as e:
        print(f"  ⚠️ 实时数据获取失败 ({e})，返回默认值")
        return None


def get_index_list():
    """获取支持的指数列表"""
    return {
        'sh000001': '上证指数', 'sz399001': '深证成指',
        'sz399006': '创业板指', 'sh000300': '沪深300',
        'sh000016': '上证50',  'sh000905': '中证500',
        'sz399005': '中小板指',
    }


if __name__ == "__main__":
    print("=== 真实模式 ===")
    df = get_index_data("sh000001", days=5)
    if df is not None:
        print(df[['date', 'close', 'change_pct', 'volume']].to_string(index=False))
    
    print("\n=== 强制模拟模式 ===")
    os.environ['STOCK_USE_MOCK'] = '1'
    from importlib import reload
    reload(__import__('sys').modules[__name__+'__'])
    df = get_index_data("sh000001", days=5)
    if df is not None:
        print(df[['date', 'close', 'change_pct', 'volume']].head().to_string(index=False))
