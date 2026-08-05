#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外汇牌价监控 - 主入口
抓取数据 → 检测变化 → 更新历史 → 生成Excel
"""
import sys
from pathlib import Path

# 添加scripts目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from fetch_rates import main as fetch_main
from generate_excel import generate_excel


def main():
    """主函数"""
    # 1. 抓取数据并更新历史
    changes_count = fetch_main()
    
    # 2. 生成Excel（无论是否有变化都更新，确保时间戳最新）
    print()
    generate_excel()
    
    print()
    print("=" * 60)
    print("✓ 外汇牌价监控任务完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
