#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试三家银行外汇牌价抓取
"""
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def fetch_abc():
    """农业银行 - 结售汇牌价"""
    url = "https://ewealth.abchina.com/ForeignExchange/ListPrice/"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'lxml')
        
        # 查找更新时间
        time_elem = soup.find(text=lambda t: t and '更新时间' in t)
        update_time = time_elem.strip() if time_elem else "未知"
        
        # 查找表格
        tables = soup.find_all('table')
        print(f"农行找到 {len(tables)} 个表格")
        
        result = {'bank': '农业银行', 'update_time': update_time, 'rates': {}}
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 3:
                    text = cols[0].get_text(strip=True)
                    if '美元' in text or 'USD' in text:
                        result['rates']['USD'] = {
                            '现汇买入价': cols[1].get_text(strip=True) if len(cols) > 1 else '',
                            '现汇卖出价': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                        }
                    if '欧元' in text or 'EUR' in text:
                        result['rates']['EUR'] = {
                            '现汇买入价': cols[1].get_text(strip=True) if len(cols) > 1 else '',
                            '现汇卖出价': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                        }
        
        print(f"农行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        print(f"农行抓取失败: {e}")
        return None

def fetch_boc():
    """中国银行 - 外汇牌价"""
    url = "https://www.boc.cn/sourcedb/whpj/"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'lxml')
        
        tables = soup.find_all('table')
        print(f"中行找到 {len(tables)} 个表格")
        
        result = {'bank': '中国银行', 'update_time': '', 'rates': {}}
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 5:
                    text = cols[0].get_text(strip=True)
                    if '美元' in text or 'USD' in text:
                        result['rates']['USD'] = {
                            '现汇买入价': cols[1].get_text(strip=True) if len(cols) > 1 else '',
                            '现钞买入价': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            '现汇卖出价': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                            '现钞卖出价': cols[4].get_text(strip=True) if len(cols) > 4 else '',
                        }
                    if '欧元' in text or 'EUR' in text:
                        result['rates']['EUR'] = {
                            '现汇买入价': cols[1].get_text(strip=True) if len(cols) > 1 else '',
                            '现钞买入价': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            '现汇卖出价': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                            '现钞卖出价': cols[4].get_text(strip=True) if len(cols) > 4 else '',
                        }
        
        # 查找发布时间
        time_elem = soup.find(text=lambda t: t and ('发布时间' in t or '时间' in t))
        if time_elem:
            result['update_time'] = time_elem.strip()
        
        print(f"中行结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        print(f"中行抓取失败: {e}")
        return None

def fetch_cmbc():
    """民生银行 - 对公结售汇"""
    url = "http://www.cmbc.com.cn/sy/xqsj/wh/dgjsh/"
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'lxml')
        
        tables = soup.find_all('table')
        print(f"民生找到 {len(tables)} 个表格")
        
        result = {'bank': '民生银行', 'update_time': '', 'rates': {}}
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 4:
                    text = cols[0].get_text(strip=True)
                    if '美元' in text or 'USD' in text:
                        result['rates']['USD'] = {
                            '现汇卖出价': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            '现汇买入价': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                        }
                    if '欧元' in text or 'EUR' in text:
                        result['rates']['EUR'] = {
                            '现汇卖出价': cols[2].get_text(strip=True) if len(cols) > 2 else '',
                            '现汇买入价': cols[3].get_text(strip=True) if len(cols) > 3 else '',
                        }
        
        print(f"民生结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return result
    except Exception as e:
        print(f"民生抓取失败: {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("测试抓取三家银行外汇牌价")
    print("=" * 60)
    
    print("\n【1/3】农业银行...")
    fetch_abc()
    
    print("\n【2/3】中国银行...")
    fetch_boc()
    
    print("\n【3/3】民生银行...")
    fetch_cmbc()
    
    print("\n" + "=" * 60)
    print("测试完成")
