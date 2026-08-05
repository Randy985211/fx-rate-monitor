#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成可视化页面所需的JSON数据
供HTML页面读取展示
"""
import json
from pathlib import Path
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "history.json"
LAST_RATES_FILE = DATA_DIR / "last_rates.json"
CHART_DATA_FILE = BASE_DIR / "chart_data.json"


def load_history():
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def load_last_rates():
    if LAST_RATES_FILE.exists():
        with open(LAST_RATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def generate_chart_data():
    """生成图表数据"""
    history = load_history()
    last_rates = load_last_rates()
    
    chart_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current": {},
        "history": {},
        "stats": {},
    }
    
    # 当前价格
    for bank, data in last_rates.items():
        chart_data["current"][bank] = {}
        for curr, rate in data.get("rates", {}).items():
            chart_data["current"][bank][curr] = {
                "现汇买入价": rate["现汇买入价"],
                "现汇卖出价": rate["现汇卖出价"],
                "fetch_time": data["fetch_time"],
            }
    
    # 历史数据（用于图表）
    for key, records in history.items():
        bank, currency = key.split("_", 1)
        if bank not in chart_data["history"]:
            chart_data["history"][bank] = {}
        
        # 取最近200条记录用于图表
        recent = records[-200:]
        chart_data["history"][bank][currency] = [
            {"time": r["timestamp"], "value": float(r["value"])}
            for r in recent
        ]
        
        # 统计数据
        values = [float(r["value"]) for r in records if r["value"]]
        if values:
            if bank not in chart_data["stats"]:
                chart_data["stats"][bank] = {}
            chart_data["stats"][bank][currency] = {
                "latest": values[-1],
                "high": max(values),
                "low": min(values),
                "count": len(records),
                "first_time": records[0]["timestamp"],
            }
    
    # 保存
    with open(CHART_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(chart_data, f, ensure_ascii=False, indent=2)
    
    print(f"图表数据已生成: {CHART_DATA_FILE}")
    return chart_data


if __name__ == "__main__":
    generate_chart_data()
