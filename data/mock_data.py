"""
模拟数据模块
当真实数据源不可用时，提供合理的模拟数据用于演示和测试
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)  # 固定种子，每次生成的模拟数据一致


def _random_walk(base_price, days, volatility=0.015):
    """生成随机游走的价格序列"""
    returns = np.random.randn(days) * volatility
    prices = base_price * np.cumprod(1 + returns)
    return prices


def generate_index_data(index_code="sh000001", days=60):
    """
    生成模拟的指数历史数据
    格式与 akshare 的 index_zh_a_hist 返回一致（已重命名列）
    """
    now = datetime.now()
    
    # 各指数基准参数
    configs = {
        'sh000001': {'name': '上证指数', 'base': 3100, 'vol': 0.012},
        'sz399001': {'name': '深证成指', 'base': 9800, 'vol': 0.015},
        'sz399006': {'name': '创业板指', 'base': 1950, 'vol': 0.018},
        'sh000300': {'name': '沪深300',  'base': 3800, 'vol': 0.013},
    }
    
    cfg = configs.get(index_code, {'base': 3000, 'vol': 0.015})
    
    # 生成日期序列（跳过周末）
    dates = []
    d = now - timedelta(days=days)
    while len(dates) < days:
        if d.weekday() < 5:  # 周一到周五
            dates.append(d)
        d += timedelta(days=1)
    
    n = len(dates)
    
    # 收盘价（随机游走）
    close_prices = _random_walk(cfg['base'], n, cfg['vol'])
    
    # 开盘价、最高、最低基于收盘价生成
    daily_returns = np.diff(close_prices, prepend=close_prices[0])
    change_pcts = daily_returns / close_prices * 100
    
    opens = close_prices * (1 + np.random.randn(n) * 0.003)
    highs = np.maximum(opens, close_prices) * (1 + abs(np.random.randn(n)) * 0.005)
    lows  = np.minimum(opens, close_prices) * (1 - abs(np.random.randn(n)) * 0.005)
    volumes = (np.random.rand(n) * 0.5 + 0.5) * 1e8
    
    df = pd.DataFrame({
        'date':      dates,
        'open':      np.round(opens, 2),
        'close':     np.round(close_prices, 2),
        'high':      np.round(highs, 2),
        'low':       np.round(lows, 2),
        'volume':    volumes.astype(int),
        'amount':    (volumes * close_prices * 10).astype(int),
        'amplitude': np.round(abs(highs - lows) / opens * 100, 2),
        'change_pct': np.round(change_pcts, 2),
        'change':    np.round(daily_returns, 2),
        'turnover':  np.round(np.random.rand(n) * 2, 2),
    })
    
    return df


def generate_sector_performance():
    """生成模拟的板块涨跌幅数据"""
    sectors = [
        '飞机制造', '陶瓷行业', '纺织机械', '物资外贸', '食品行业',
        '塑料制品', '交通运输', '商业百货', '酒店旅游', '化纤行业',
        '家电行业', '钢铁行业', '供水供气', '电器行业', '有色金属',
        '电子器件', '机械行业', '船舶制造', '发电设备', '电力行业',
        '金融行业', '房地产', '石油行业', '化工行业', '生物制药',
        '医疗器械', '环保行业', '农药化肥', '水泥行业', '玻璃行业',
        '造纸行业', '印刷包装', '纺织行业', '服装鞋类', '仪器仪表',
        '电子信息', '软件服务', '文化传媒', '工艺商品', '装修装饰',
    ]
    
    # 一部分涨、一部分跌
    n = len(sectors)
    changes = np.concatenate([
        np.random.uniform(0.5, 3.0, n // 2),
        np.random.uniform(-4.5, -0.5, n - n // 2),
    ])
    np.random.shuffle(changes)
    
    data = []
    for i, name in enumerate(sectors):
        data.append({
            'label': f'new_{name[:4]}',
            '板块': name,
            '公司家数': np.random.randint(8, 80),
            '平均价格': round(np.random.uniform(5, 50), 2),
            '涨跌额': round(changes[i] * np.random.uniform(0.3, 0.8), 2),
            '涨跌幅': round(changes[i], 2),
            '总成交量': int(np.random.uniform(1e7, 5e8)),
            '总成交额': int(np.random.uniform(1e8, 1e10)),
        })
    
    df = pd.DataFrame(data)
    df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce')
    df = df.dropna(subset=['涨跌幅'])
    df = df.sort_values('涨跌幅', ascending=False).reset_index(drop=True)
    return df


def generate_sector_flow():
    """生成模拟的板块资金流向数据"""
    sectors = [
        '金融行业', '房地产', '石油行业', '化工行业', '生物制药',
        '医疗器械', '环保行业', '农药化肥', '水泥行业', '玻璃行业',
        '造纸行业', '印刷包装', '纺织行业', '服装鞋类', '仪器仪表',
        '电子信息', '软件服务', '文化传媒', '工艺商品', '装修装饰',
        '飞机制造', '陶瓷行业', '纺织机械', '物资外贸', '食品行业',
        '塑料制品', '交通运输', '商业百货', '酒店旅游', '化纤行业',
        '家电行业', '钢铁行业', '供水供气', '电器行业', '有色金属',
        '电子器件', '机械行业', '船舶制造', '发电设备', '电力行业',
    ]
    
    data = []
    for name in sectors:
        net_amount = np.random.uniform(-5e8, 5e8)  # -5亿 ~ 5亿
        net_ratio  = net_amount / 1e9 * 100  # 净占比
        data.append({
            '名称': name,
            '主力净流入-净额': int(net_amount),
            '主力净流入-净占比': round(net_ratio, 2),
        })
    
    df = pd.DataFrame(data)
    return df


def generate_stock_data(stock_code="000001", days=60):
    """
    生成模拟的个股历史数据
    格式与 akshare 的 stock_zh_a_hist 返回一致（已重命名列）
    """
    now = datetime.now()
    
    # 用股票代码后三位做种子，让每只股票走势不一样
    seed = int(stock_code[-3:]) if stock_code[-3:].isdigit() else 42
    rng = np.random.RandomState(seed)
    
    # 生成日期
    dates = []
    d = now - timedelta(days=days)
    while len(dates) < days:
        if d.weekday() < 5:
            dates.append(d)
        d += timedelta(days=1)
    
    n = len(dates)
    base_price = rng.uniform(8, 80)
    vol = rng.uniform(0.015, 0.025)
    
    close_prices = base_price * np.cumprod(1 + rng.randn(n) * vol)
    daily_returns = np.diff(close_prices, prepend=close_prices[0])
    change_pcts = daily_returns / close_prices * 100
    
    # 一些常见股票名称映射
    stock_names = {
        '000001': '平安银行', '000002': '万科A', '600519': '贵州茅台',
        '000858': '五粮液',   '002594': '比亚迪', '300750': '宁德时代',
        '000333': '美的集团', '002415': '海康威视', '600036': '招商银行',
        '601318': '中国平安',
    }
    
    df = pd.DataFrame({
        '日期': dates,
        '开盘': np.round(close_prices * (1 + rng.randn(n) * 0.003), 2),
        '收盘': np.round(close_prices, 2),
        '最高': np.round(close_prices * (1 + abs(rng.randn(n)) * 0.005), 2),
        '最低': np.round(close_prices * (1 - abs(rng.randn(n)) * 0.005), 2),
        '成交量': (rng.rand(n) * 0.5 + 0.5).astype(int) * 1000000,
        '成交额': (rng.rand(n) * 0.5 + 0.5).astype(int) * 100000000,
        '涨跌幅': np.round(change_pcts, 2),
        '涨跌额': np.round(daily_returns, 2),
        '换手率': np.round(rng.rand(n) * 3, 2),
        '振幅': np.round(abs(rng.randn(n)) * 2, 2),
    })
    
    return df, stock_names.get(stock_code, stock_code)


def generate_hot_stocks(top_n=20):
    """生成模拟的热门股票列表"""
    stocks = [
        '000001', '000002', '600519', '000858', '002594',
        '300750', '000333', '002415', '600036', '601318',
        '600900', '002475', '000725', '601012', '300059',
        '600276', '002714', '000651', '601166', '600585',
        '002352', '600887', '000568', '002230', '600809',
    ]
    return stocks[:top_n]


def get_index_info():
    """获取指数基本信息"""
    return {
        'sh000001': '上证指数',
        'sz399001': '深证成指',
        'sz399006': '创业板指',
        'sh000300': '沪深300',
    }
