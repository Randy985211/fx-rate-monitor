# 💹 外汇牌价实时监控系统

## 功能特点

- ✅ **云端24小时运行**：基于 GitHub Actions，无需本地开机
- ✅ **变化触发记录**：仅在价格变动时保存，避免冗余数据
- ✅ **多银行监控**：农业银行、民生银行、中国银行
- ✅ **双币种追踪**：美元 (USD)、欧元 (EUR)
- ✅ **Excel自动导出**：每个银行+币种独立Sheet，自动覆盖
- ✅ **可视化仪表盘**：实时价格卡片 + 历史趋势图表
- ✅ **带时间戳**：每条记录都有精确时间，保证数据可追溯

## 快速部署（5分钟搞定）

### 第一步：创建GitHub仓库

1. 登录 GitHub，新建一个仓库（建议公开仓库，免费额度无限）
2. 仓库名建议：`fx-rate-monitor`

### 第二步：上传文件

将以下文件上传到你的GitHub仓库：

```
fx-monitor/
├── .github/
│   └── workflows/
│       └── monitor.yml      # 定时任务配置
├── scripts/
│   ├── fetch_rates.py       # 数据抓取模块
│   ├── generate_excel.py    # Excel生成模块
│   ├── generate_chart_data.py  # 图表数据生成
│   └── run.py               # 主入口
├── data/                    # 数据目录（自动生成）
├── index.html               # 可视化页面
├── chart_data.json          # 图表数据（自动生成）
├── 外汇牌价监控数据.xlsx     # Excel文件（自动生成）
└── requirements.txt         # Python依赖
```

### 第三步：启用GitHub Pages

1. 进入仓库 Settings → Pages
2. Source 选择 `Deploy from a branch`
3. Branch 选择 `main` / `root`
4. 点击 Save
5. 等待几分钟后，就能通过 `https://你的用户名.github.io/fx-rate-monitor/` 访问可视化页面

### 第四步：启用GitHub Actions

1. 进入仓库 Actions 页面
2. 找到 "外汇牌价监控" 工作流
3. 点击 "Enable workflow" 启用
4. 可以手动点击 "Run workflow" 测试一次

## 工作原理

```
每2分钟触发一次 GitHub Actions
        ↓
抓取三家银行外汇牌价
        ↓
与上次数据对比 → 无变化 → 结束
        ↓ 有变化
记录到历史数据（带时间戳）
        ↓
生成Excel文件（6个Sheet）
        ↓
生成图表数据JSON
        ↓
自动Commit & Push到仓库
        ↓
GitHub Pages 自动更新可视化页面
```

## Excel文件说明

文件名：`外汇牌价监控数据.xlsx`

### Sheet结构

| Sheet名称 | 说明 |
|-----------|------|
| 实时汇总 | 所有银行最新价格一览 |
| 农业银行-美元 | 农行美元现汇买入价历史 |
| 农业银行-欧元 | 农行欧元现汇买入价历史 |
| 民生银行-美元 | 民生美元现汇买入价历史 |
| 民生银行-欧元 | 民生欧元现汇买入价历史 |
| 中国银行-美元 | 中行美元现汇买入价历史 |
| 中国银行-欧元 | 中行欧元现汇买入价历史 |

### 每个Sheet包含

- 序号
- 时间戳（精确到秒）
- 现汇买入价
- 变动值（涨/跌）
- 数据来源

## 自定义配置

### 修改监控频率

编辑 `.github/workflows/monitor.yml` 中的 cron 表达式：

```yaml
schedule:
  - cron: '*/2 * * * *'  # 每2分钟一次
```

常用cron表达式：
- 每1分钟：`*/1 * * * *`
- 每5分钟：`*/5 * * * *`
- 每10分钟：`*/10 * * * *`

> ⚠️ 注意：GitHub Actions 的 cron 可能有几分钟延迟，这是正常现象。

### 添加更多银行/币种

编辑 `scripts/fetch_rates.py` 中的配置：

```python
BANKS = {
    "新银行": {
        "url": "银行官网地址",
        "encoding": "gbk",  # 或 utf-8
        "source": "数据源",
    },
}

CURRENCIES = ["美元", "欧元", "英镑", "日元"]  # 添加更多币种
```

### 修改Excel文件名

编辑 `scripts/generate_excel.py` 中的 `EXCEL_FILE` 变量。

## 本地运行测试

```bash
# 安装依赖
pip install -r requirements.txt

# 运行一次
python scripts/run.py

# 查看结果
# 1. data/history.json - 历史数据
# 2. 外汇牌价监控数据.xlsx - Excel文件
# 3. 用浏览器打开 index.html - 可视化页面
```

## 数据来源说明

| 银行 | 数据源 | 更新频率 |
|------|--------|----------|
| 农业银行 | 5waihui.com | 实时同步 |
| 民生银行 | 5waihui.com | 实时同步 |
| 中国银行 | boc.cn 官网 | 实时同步 |

> 📌 数据仅供参考，实际汇率以银行柜台成交价为准。

## 成本说明

- **完全免费**：GitHub 公开仓库 Actions 无限分钟数
- **零维护**：全自动运行，无需人工干预
- **不占资源**：云端运行，本地电脑可以关机

## 常见问题

**Q: 数据准吗？**
A: 数据来源于银行官网或权威聚合网站，与银行官网保持同步。

**Q: 为什么是每2分钟检测一次，不是实时？**
A: 银行外汇牌价本身不是逐秒更新的，通常几分钟到几十分钟变动一次。每2分钟检测既能保证及时性，又不会浪费资源。检测到变化才会记录，效果等同于"变化即更新"。

**Q: Excel文件会越来越大吗？**
A: 会，但增长很慢。外汇牌价一天可能变动几十次，一年也就几万条记录，Excel完全能承载。

**Q: 可以监控更多银行吗？**
A: 可以，只需在 `fetch_rates.py` 中添加新的银行配置即可。

**Q: 怎么下载Excel？**
A: 在 GitHub 仓库页面直接点击 `外汇牌价监控数据.xlsx` 文件，然后点 Download 下载。

## 更新日志

### v1.0.0
- 初始版本
- 支持农行、民生、中行三家银行
- 支持美元、欧元两个币种
- Excel自动生成 + 可视化仪表盘
- GitHub Actions 云端定时运行
