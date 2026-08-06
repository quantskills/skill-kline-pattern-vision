# PandaData数据契约

## 认证

只允许运行时读取：

- `PANDA_USERNAME`
- `PANDA_PASSWORD`
- `~/.pandadata/pandadata.env`

账号、密码、token、cookie和授权头不得进入 skill 文件、JSON、Markdown、日志、异常文本或图表。

## 方法路由

| 资产 | 日线 | 分钟 |
|---|---|---|
| 股票 | `get_stock_daily` | `get_stock_min` / `get_stock_rt_min` |
| 明确期货合约 | `get_future_daily` | `get_future_min` |
| 期货品种根代码 | 先用批准的 dominant 能力解析 | 再查询已解析合约 |

支持目标周期 `1m/5m/10m/15m/30m/60m/1d`。如果实时接口只接受1分钟，则取1分钟后在内存中用 `resample_kline.py` 聚合；不能调用网页、券商接口、其他数据源或声明外缓存。

## 标准字段

最低字段：`date` 或 `datetime`、`symbol`、`open`、`high`、`low`、`close`。可选字段：`minute`、`volume`、`amount`、`num_trades`。每个调用记录不含敏感信息的 status envelope：

```text
status, method, asset_type, requested_symbol, resolved_symbol,
start_date, end_date, frequency, returned_rows, valid_rows, reason
```

状态：

- `ok`：调用成功、校验通过且达到分析门槛；
- `empty`：没有返回行或过滤后没有行；
- `error`：鉴权、参数、字段、日期、OHLC、重复键错误，或不足20根有效bar；
- `unsupported`：未知资产、未批准方法、超出只读范围或不支持的频率。

## 时间边界

- 请求日期统一 `YYYYMMDD`，不得分析区间外数据。
- A股上午 `09:30–11:30`、下午 `13:00–15:00` 分开聚合。
- 不跨午休、不插值、不填补缺失分钟。
- 末根不足目标周期时设 `complete: false`；实时末根可能未收盘。
- 盘中实时数据不能冒充正式收盘数据；截图和数据末根有差异时分栏说明。

## 截图对齐

混合模式比较标的、周期、请求/可见日期、复权/价格模式、末根、关键高低点、K线方向和成交量。截图读数可以是近似，结构化数据可精确到返回字段；冲突可能来自周期边界、软件复权、缓存时间或未收盘状态，不能无声覆盖。

## 本地与MCP边界

Claude会话可以使用已授权的 PandaData MCP 获取原始数据，再传入 `analyze_kline.py --input`。本地Python只实现 SDK adapter和脱敏JSON处理，不伪造MCP客户端。历史接口为空或直取目标分钟失败时，若1分钟调用成功，只能本地内存聚合；若所有批准调用失败，报告 blocker，不换源。
