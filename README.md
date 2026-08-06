# K线形态识别

简体中文 | [English](README.en.md)

> QuantSkills 社区项目，由 GitHub 用户 `cikeqi` 维护。项目尚未经过独立审核，不代表 QuantSkills 官方认证，也不承诺收益或生产环境适用性。

纯只读的 K 线分析 skill，支持三种模式：

1. **截图模式**：只凭用户提供的K线截图识别趋势和形态，不调用外部行情。
2. **PandaData数据模式**：获取并校验 PandaData 日线或分钟 OHLCV，自动聚合目标周期并生成图表。
3. **混合模式**：同时分析截图与结构化数据，单独列出事实、差异和不确定性。

> 这是研究与教育工具，不构成投资建议，不承诺收益，不执行交易。

## 目录

```text
skill-kline-pattern-vision/
├── SKILL.md                         # 触发、模式、硬规则和报告格式
├── README.md / README.en.md         # 使用说明
├── CLAUDE.md                        # Claude运行约束
├── LICENSE                          # GPL-3.0-only许可证
├── requirements.txt                 # Python依赖
├── agents/
│   ├── openai.yaml                  # agent元数据
│   ├── portable-loader.md           # Markdown agent便携入口
│   └── cursor-rule.mdc              # Cursor规则
├── references/
│   ├── methodology.md               # 形态识别方法
│   └── pandadata_contract.md        # 数据字段和时间边界
├── scripts/
│   ├── pandadata_runtime.py        # 本地SDK只读adapter
│   ├── ohlcv_validate.py            # OHLCV校验
│   ├── resample_kline.py            # 分钟聚合
│   ├── indicators.py                # MA/MACD/RSI/布林带
│   ├── pattern_detection.py         # HH/HL/LH/LL和候选形态
│   ├── generate_kline_chart.py      # K线+成交量图
│   └── analyze_kline.py             # 一键CLI
└── tests/                           # 单元测试
```

## 支持周期

- 日线：`1d`
- 分钟：`1m`、`5m`、`10m`、`15m`、`30m`、`60m`

分钟线聚合按A股上午和下午交易时段分开处理，不跨午休、不插值、不填补。一个周期内数据不足的末根会标记 `complete: false`，不伪装成完整收盘K线。

## 快速开始

### Claude + PandaData MCP

由当前 Claude 会话调用已授权的 PandaData MCP，拿到脱敏 dataframe JSON（包含 `columns` 和 `rows`），再交给本地脚本：

```bash
python3 scripts/analyze_kline.py \
  --input /path/to/pandadata_dataframe.json \
  --frequency 10m \
  --out /tmp/kline-analysis
```

输出：

```text
/tmp/kline-analysis/analysis.json
/tmp/kline-analysis/bars.json
/tmp/kline-analysis/kline_10m.png
```

### 本地 PandaData SDK

本地运行时从环境变量或 `~/.pandadata/pandadata.env` 读取认证，不把认证写入项目：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

SDK adapter 位于 `scripts/pandadata_runtime.py`。MCP 与本地Python脚本之间的边界是：MCP由宿主Claude调用，本地脚本接收脱敏结构化数据；不在Python代码中伪造MCP调用。

## 常用命令

```bash
python3 scripts/analyze_kline.py --help
python3 scripts/analyze_kline.py --input data.json --frequency 5m --out /tmp/kline-5m
python3 scripts/analyze_kline.py --input data.json --frequency 10m --out /tmp/kline-10m
python3 scripts/analyze_kline.py --input data.json --frequency 15m --out /tmp/kline-15m
```

## 凭证安全

- 项目文件夹不包含真实账号、密码、token、cookie或授权头。
- 只允许运行时读取环境变量 `PANDA_USERNAME` / `PANDA_PASSWORD`，或本地 `~/.pandadata/pandadata.env`。
- 不要把凭证粘贴到聊天、代码、README、JSON、Markdown、日志或图表中。
- 异常信息和分析输出必须脱敏。

## 测试

推荐安装依赖后运行：

```bash
python3 -m pytest -q
```

核心测试覆盖：

- OHLC关系、重复键、排序、负成交量和数据门槛；
- 5/10分钟聚合和午休边界；
- MA、EMA、MACD、RSI、布林带；
- HH、HL、LH、LL和形态候选；
- MCP JSON输入和敏感字段检查。

## 形态识别边界

- `HH` 是更高的高点，`HL` 是更高的低点；两者连续出现支持上升结构。
- `LH` 是更低的高点，`LL` 是更低的低点；两者连续出现支持下降结构。
- 十字、锤头、长影、吞没、箱体、双顶/双底等均先标记为候选，必须附上下文、确认条件、失效条件和替代解释。
- 单根K线不是确认信号；不计算未经验证的胜率；不输出直接买卖指令。
- 截图读数可能是近似值；截图指标和PandaData计算指标可能因口径不同而有差异。

## 数据边界

只使用获准 PandaData 数据或用户截图。不使用网页、券商接口、其他行情源、未声明缓存、合成数据或替代数据。数据不足、接口为空或失败时必须报告状态，不能静默补齐。
