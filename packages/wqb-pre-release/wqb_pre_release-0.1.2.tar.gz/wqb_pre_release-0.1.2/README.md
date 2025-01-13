# wqb-pre-release

- Rocky Haotian Du
- 2025-01-09

### 介绍

- 高兼容性、高可扩展性
  - wqb.WQBSession继承wqb.AutoAuthSession
  - wqb.AutoAuthSession继承requests.Session
  - 各种方法的返回值统一为requests.Response或多个requests.Respons
- wqb.AutoAuthSession
  - 过期自动重连
  - *定时重连功能待完成...*
- wqb.WQBSession
  - 异步simulate
  - 异步check submission
  - 查询datasets
  - 查询fields
  - 查询指定id的alpha
  - *生产者/消费者异步模式待完成...*
  - *其他请求待完成...*

### 基本用法

```Python
import wqb

wqbs = wqb.WQBSession(('xxx@mail.com', 'xxxxxx'))

resp = wqbs.auth_request()
print(resp.status_code)
print(resp.headers)
print(resp.text)

# 所有requests.Session的方法，wqb.WQBSession都有，如：
# wqbs.request(<METHOD>, <URL>)
# wqbs.get(url)

import asyncio

results = asyncio.run(wqbs.concurrent_simulate(
    [
        {...},
        {...},
        {...},
        {...},
        {...},
        {...},
    ],  # 可以是alpha组成的列表，也可以是multi alpha组成的列表
    3,  # 最大并行请求数
    return_exceptions=True,  # 异常作为结果返回
    max_tries=1200,  # 单个alpha或multi alpha最大尝试次数，一次retry一般是1s，1200是20mins
))
print(
    'exceptions:',
    *(res for res in results if isinstance(res, BaseException)),
    sep='\n',
)
# 除了异常，其他结果都是Response，可灵活根据需要进行后续处理

```
