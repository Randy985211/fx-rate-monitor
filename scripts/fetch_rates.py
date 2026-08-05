#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外汇牌价监控 - 数据抓取模块
抓取农行、民生、中行的美元/欧元现汇买入价
变化触发记录，仅在数据变化时保存
"""
import requests
from bs4 import BeautifulSoup
import json
import os
import time
from datetime import datetime
from pathlib import Path

# 配置
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "history.json"
LAST_RATES_FILE = DATA_DIR / "last_rates.json"

# 银行配置
BANKS = {
    "农业银行": {
        "url": "https://www.5waihui.com/abc/",
        "encoding": "gbk",
        "source": "5waihui.com",
    },
    "民生银行": {
        "url": "https://www.5waihui.com/cmbc/",
        "encoding": "gbk",
        "source": "5waihui.com",
    },
    "中国银行": {
        "url": "https://www.boc.cn/sourcedb/whpj/",
        "encoding": "utf-8",
        "source": "boc.cn",
    },
}

# 监控的币种
CURRENCIES = ["美元", "欧元"]

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def fetch_5waihui(url, encoding="gbk"):
    """从5waihui.com抓取外汇牌价"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.encoding = encoding
        soup = BeautifulSoup(resp.text, "lxml")
        
        result = {}
        table = soup.find("table")
        if not table:
            return result
        
        rows = table.find_all("tr")
        for row in rows[1:]:  # 跳过表头
            cols = row.find_all("td")
            if len(cols) >= 5:
                currency = cols[0].get_text(strip=True)
                if currency in CURRENCIES:
                    result[currency] = {
                        "现汇买入价": cols[1].get_text(strip=True),
                        "现钞买入价": cols[2].get_text(strip=True),
                        "现汇卖出价": cols[3].get_text(strip=True),
                        "现钞卖出价": cols[4].get_text(strip=True),
                    }
        return result
    except Exception as e:
        print(f"  抓取5waihui失败: {e}")
        return {}


def fetch_boc(url, encoding="utf-8"):
    """从中行官网抓取外汇牌价"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.encoding = encoding
        soup = BeautifulSoup(resp.text, "lxml")
        
        result = {}
        tables = soup.find_all("table")
        
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 5:
                    currency_text = cols[0].get_text(strip=True)
                    # 中行的货币名称可能是英文缩写
                    for curr in CURRENCIES:
                        curr_code = "USD" if curr == "美元" else "EUR"
                        if curr_code in currency_text or curr in currency_text:
                            result[curr] = {
                                "现汇买入价": cols[1].get_text(strip=True),
                                "现钞买入价": cols[2].get_text(strip=True),
                                "现汇卖出价": cols[3].get_text(strip=True),
                                "现钞卖出价": cols[4].get_text(strip=True),
                            }
        return result
    except Exception as e:
        print(f"  抓取中行失败: {e}")
        return {}


def fetch_all_rates():
    """抓取所有银行的外汇牌价"""
    all_rates = {}
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for bank_name, config in BANKS.items():
        print(f"  抓取 {bank_name}...")
        
        if config["source"] == "5waihui.com":
            rates = fetch_5waihui(config["url"], config["encoding"])
        elif config["source"] == "boc.cn":
            rates = fetch_boc(config["url"], config["encoding"])
        else:
            rates = {}
        
        all_rates[bank_name] = {
            "rates": rates,
            "source": config["source"],
            "fetch_time": timestamp,
        }
        
        # 打印结果
        for curr, data in rates.items():
            print(f"    {curr}: 现汇买入价 = {data['现汇买入价']}")
    
    return all_rates


def load_last_rates():
    """加载上一次的牌价数据"""
    if LAST_RATES_FILE.exists():
        with open(LAST_RATES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_last_rates(rates):
    """保存当前牌价作为下次对比基准"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(LAST_RATES_FILE, "w", encoding="utf-8") as f:
        json.dump(rates, f, ensure_ascii=False, indent=2)


def load_history():
    """加载历史数据"""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_history(history):
    """保存历史数据"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def detect_changes(current_rates, last_rates):
    """检测数据变化，返回变化的条目"""
    changes = []
    
    for bank_name, bank_data in current_rates.items():
        if bank_name not in last_rates:
            # 新银行，全部算变化
            for curr, data in bank_data["rates"].items():
                changes.append({
                    "bank": bank_name,
                    "currency": curr,
                    "old_value": None,
                    "new_value": data["现汇买入价"],
                    "timestamp": bank_data["fetch_time"],
                    "source": bank_data["source"],
                })
            continue
        
        last_bank = last_rates[bank_name]
        for curr, data in bank_data["rates"].items():
            old_value = last_bank["rates"].get(curr, {}).get("现汇买入价")
            new_value = data["现汇买入价"]
            
            if old_value != new_value:
                changes.append({
                    "bank": bank_name,
                    "currency": curr,
                    "old_value": old_value,
                    "new_value": new_value,
                    "timestamp": bank_data["fetch_time"],
                    "source": bank_data["source"],
                })
    
    return changes


def update_history(changes):
    """更新历史数据"""
    history = load_history()
    
    for change in changes:
        key = f"{change['bank']}_{change['currency']}"
        if key not in history:
            history[key] = []
        
        history[key].append({
            "timestamp": change["timestamp"],
            "value": change["new_value"],
            "old_value": change["old_value"],
            "source": change["source"],
        })
    
    save_history(history)
    return history


def main():
    """主函数"""
    print("=" * 60)
    print(f"外汇牌价监控 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 1. 抓取当前牌价
    print("\n【1/4】抓取外汇牌价...")
    current_rates = fetch_all_rates()
    
    # 2. 加载上次牌价
    print("\n【2/4】对比上次数据...")
    last_rates = load_last_rates()
    
    # 3. 检测变化
    changes = detect_changes(current_rates, last_rates)
    
    if changes:
        print(f"  检测到 {len(changes)} 条变化:")
        for change in changes:
            old = change["old_value"] or "首次记录"
            print(f"    {change['bank']} - {change['currency']}: {old} → {change['new_value']}")
        
        # 4. 更新历史数据
        print("\n【3/4】更新历史数据...")
        update_history(changes)
        
        # 5. 保存当前牌价
        print("\n【4/4】保存当前牌价...")
        save_last_rates(current_rates)
        
        print(f"\n✓ 完成，共记录 {len(changes)} 条变化数据")
    else:
        print("  数据无变化，无需更新")
        save_last_rates(current_rates)  # 仍更新时间戳
    
    print("=" * 60)
    return len(changes)


if __name__ == "__main__":
    main()
