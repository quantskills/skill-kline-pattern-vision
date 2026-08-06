---
name: skill-kline-pattern-vision
description: 用截图或只读 PandaData 行情识别股票/期货K线趋势结构、蜡烛线和候选图表形态，支持日线与1/5/10/15/30/60分钟线，输出证据、确认条件、失效条件和不确定性。
argument-hint: "[截图] [股票/期货代码] [YYYYMMDD-YYYYMMDD] [周期]"
metadata:
  organization: QuantSkills
  organization_url: https://github.com/quantskills
  repository: skill-kline-pattern-vision
  repository_url: https://github.com/quantskills/skill-kline-pattern-vision
  project_type: skill
  collection: technical-analysis
  type: quant
  version: 1.0.0
  license: GPL-3.0-only
---

# K线形态识别（工程版）

> QuantSkills 社区项目，由 GitHub 用户 `cikeqi` 维护。项目尚未经过独立审核，不代表 QuantSkills 官方认证，也不承诺收益或生产环境适用性。

这是一个**只读**的K线形态识别 skill，支持三种模式：

1. **截图模式**：只分析用户提供的K线截图，不调用外部行情。
2. **PandaData数据模式**：获取并校验 PandaData 日线或分钟 OHLCV，必要时聚合为目标周期。
3. **混合模式**：同时分析截图和 PandaData，并把两者事实、差异和原因分开报告。

结果是市场结构与形态候选解读，不是保证性预测、回测胜率或交易指令。

## 绝对凭证安全规则

- 任何用户 PandaData 账号、密码、token、cookie、authorization header 或配置原文都**不得写入本 skill**。
- 不得把凭证写入 `SKILL.md`、Python代码、配置、测试样例、日志、JSON、CSV、图表、ZIP或回复。
- 本地 SDK 只允许在运行时从环境变量或 `~/.pandadata/pandadata.env` 读取；不要要求用户把凭证粘贴到聊天。
- MCP 模式由当前 Claude 会话使用已授权的 Pandadata MCP 调用；本地脚本只接收脱敏后的结构化数据 JSON，不保存认证信息。
- 错误信息必须脱敏；输出只记录 status、method、symbol、日期、频率、行数和 reason。

## 输入与周期门槛

- 股票代码使用交易所后缀，如 `603986.SH`；不能从名称唯一映射时先澄清，不猜代码。
- 期货完整合约直接查询；品种根代码先用批准的 dominant 能力解析，不拼接合约。
- 支持周期：`1m`、`5m`、`10m`、`15m`、`30m`、`60m`、`1d`。
- 截图模式至少需要20根清晰K线；要识别成交量或指标，截图必须包含对应区域和明确标签。
- 数据模式至少需要20根有效 OHLC bar 才能给出完整结构分析；不足时返回 `error: insufficient_valid_bars`，不补造数据。
- 日期统一为 `YYYYMMDD`，最终结论不得超出请求区间。
- 最后一根实时K线可能未收盘，必须显式标记。

## PandaData调用协议

### MCP优先（Claude会话中）

股票：

```text
get_stock_daily(symbol=[symbol], start_date="YYYYMMDD", end_date="YYYYMMDD", fields=[])
get_stock_min(symbol=[symbol], start_date="YYYYMMDD", end_date="YYYYMMDD", frequency="1m", fields=[])
get_stock_rt_min(symbol=[symbol], frequency="1m", fields=[])
```

期货：

```text
get_future_daily(symbol=[contract], start_date="YYYYMMDD", end_date="YYYYMMDD", fields=[])
get_future_min(symbol=[contract], start_date="YYYYMMDD", end_date="YYYYMMDD", frequency="1m", fields=[])
```

若实时接口只支持1分钟，先取1分钟再由 `scripts/resample_kline.py` 在内存中聚合；不得把失败的5分钟/10分钟接口静默替换成别的数据源。

### 本地SDK模式

在 skill 目录安装依赖后运行：

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/analyze_kline.py --input /path/to/mcp_or_data.json --frequency 10m --out /tmp/kline-analysis
```

`--input` 接收脱敏后的 PandaData dataframe JSON（`columns` + `rows`）或行数组。SDK adapter 位于 `scripts/pandadata_runtime.py`，仅运行时读凭证。

## 数据管线

固定顺序：

1. 获取原始数据（PandaData只读）或读取脱敏 MCP JSON。
2. `ohlcv_validate.py` 校验日期、必需字段、有限值、OHLC关系、非负成交量、重复键和排序。
3. `resample_kline.py` 聚合分钟线。A股上午 `09:30–11:30`、下午 `13:00–15:00` 分开处理；不跨午休、不插值、不填补；不足一个周期的末根标记 `complete: false`。
4. `indicators.py` 计算可选 MA、EMA、MACD、RSI、Bollinger；窗口不足返回 unknown/None，不能从颜色猜指标。
5. `pattern_detection.py` 识别 HH/HL/LH/LL、趋势阶段、蜡烛线候选、箱体/双顶双底/突破回踩等，并保留证据与置信度。
6. `generate_kline_chart.py` 生成K线+成交量 PNG；图表不写入凭证。
7. `analyze_kline.py` 输出 `analysis.json`、`bars.json` 和结构化摘要。

可直接运行模块帮助：

```bash
python scripts/analyze_kline.py --help
python scripts/analyze_kline.py --input data.json --frequency 5m --out /tmp/kline-5m
python scripts/analyze_kline.py --input data.json --frequency 10m --out /tmp/kline-10m
```

## 形态分析规则

先看波段高低点，再看单根K线：

- `HH`：更高的高点；`HL`：更高的低点；两者连续出现支持上升结构。
- `LH`：更低的高点；`LL`：更低的低点；两者连续出现支持下降结构。
- 高低点混合表示震荡或趋势转换，不应强行归类。
- 单根十字、锤头、长影、吞没只能是候选；必须写上下文、确认条件、失效条件和替代解释。
- 箱体、双顶/双底、头肩、三角、旗形、楔形、突破回踩均使用“候选/疑似”，除非结构证据完整。
- 支撑/压力使用数据支持的区域，不把区域直接变成目标价或止损价。
- 不输出“立即买入/卖出”“必然上涨/下跌”“保证收益”，不计算未经验证的胜率。

## 固定中文报告结构

```markdown
# K线形态识别报告
## 1. 请求与分析模式
## 2. 数据与来源
## 3. 输入与可读性
## 4. PandaData校验
## 5. 截图观察
## 6. 截图与数据对齐（无截图时写未提供）
## 7. 趋势与市场结构
## 8. 蜡烛线信号
## 9. 图表形态候选
## 10. 成交量与可见指标
## 11. 关键价位与验证条件
## 12. 条件化建议
## 13. 调用状态与降级说明
## 14. 不确定性与风险边界
## 15. 结论
```

数据记录至少包含：原始标识、解析标的、日期区间、周期、复权/价格模式、PandaData方法、返回/有效行数、字段、数据状态、最后一根是否可能未收盘。混合模式必须用表格分别列截图观察和 PandaData 事实，不得用一方无声覆盖另一方。

## 状态定义

- `ok`：调用成功、标准化和校验通过，并达到至少20根有效bar。
- `empty`：无行或过滤后无行。
- `error`：认证/参数/字段/日期/OHLC/重复键错误，或有效bar少于20根。
- `unsupported`：未知资产、超出只读范围或未支持频率。

失败不得静默fallback。截图可用时可降级到截图-only；数据可用时可降级到data-only；必须说明降级原因和未使用替代数据源。

## 测试与边界

在 skill 目录运行：

```bash
python -m pytest -q
```

测试覆盖 OHLCV校验、重复和排序、分钟聚合、午休边界、partial末根、指标窗口、HH/HL/LH/LL、候选形态和 JSON CLI。测试数据仅为本地单元测试数据，不得当作市场数据。

本 skill 只能读取并分析获准的行情数据和用户截图，不下单、不修改账户/持仓、不回测、不优化策略、不登录注册、不刷新凭证、不写凭证，不使用网页或其他行情源替代 PandaData。分析不构成投资建议。
