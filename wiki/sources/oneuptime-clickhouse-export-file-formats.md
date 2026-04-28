---
title: ClickHouse 导出文件格式
type: source
tags: [数据库, ClickHouse, 导出, 对象存储, 数据格式]
source_count: 1
source_file: raw/articles/oneuptime-clickhouse-export-file-formats.md
author: Nawaz Dhandala
published: 2026-03-31
updated: 2026-04-28
---

来源：[[entities/clickhouse]] · [原文](https://oneuptime.com/blog/post/2026-03-31-clickhouse-export-file-formats/view)

## 核心结论

OneUptime 这篇文章把 ClickHouse 导出数据的几条常见路径摆在一起：SQL 的 `FORMAT` 子句、`INTO OUTFILE`、`clickhouse-client` 标准输出、HTTP 接口，以及 `INSERT INTO FUNCTION s3(...)` 直接写对象存储。

我会把它记成一个很实用的边界：ClickHouse 的导出能力不是单一命令，而是“结果格式 + 输出通道 + 下游消费者”三件事的组合。格式选错，会让后续导入、分析或迁移变慢；通道选错，则会把文件落点、权限和失败恢复搞复杂。

## `FORMAT` 是最底层的输出协议

`FORMAT` 子句可以追加在 `SELECT` 后面，把查询结果输出成 CSV、Parquet、JSONEachRow、Native 等格式。它本身不关心结果写到哪里，只决定 ClickHouse 如何序列化结果。

这个心智很重要。很多导出方案表面看起来不同，本质都是同一个查询结果被不同通道拿走：

- `clickhouse-client` 把 `FORMAT` 输出重定向到本地文件；
- HTTP 接口把 `FORMAT` 输出作为 response body；
- `INTO OUTFILE` 把结果写到客户端机器上的文件；
- `s3()` 表函数则把结果写到对象存储。

所以排查导出问题时，我会先拆成两个问题：结果格式是否适合下游，输出通道是否适合这次作业。

## `INTO OUTFILE` 的文件落点在客户端

文章明确提醒：`INTO OUTFILE` 是客户端侧能力，文件写在运行 `clickhouse-client` 或 `clickhouse-local` 的机器上，不是 ClickHouse server 所在机器。它也不适用于 HTTP 接口；HTTP 导出应该直接把响应体保存成文件。

这个细节很容易在生产脚本里踩坑。尤其是在 Kubernetes 或跳板机环境里，人会自然以为 SQL 里的路径是服务端路径，但实际落点可能是执行客户端的临时容器、运维机或 CI runner。

因此，我会把 `INTO OUTFILE` 看成适合本地操作、一次性导出、小批数据和明确客户端磁盘位置的工具，而不是默认生产管道。

## 格式选择应该从消费者倒推

文章给出的格式建议很朴素，但足够有用：

- 数据湖和对象存储归档优先 `Parquet + zstd`；
- Hive / Presto 生态可以考虑 `ORC`；
- Python / Spark 分析链路可以用 `Arrow` 或 `Parquet`；
- 电子表格和 BI 工具更适合 `CSVWithNames`；
- 事件流或行式文本交换适合 `JSONEachRow`；
- ClickHouse 到 ClickHouse 迁移优先 `Native`；
- 自定义二进制管道可以考虑 `RowBinary`。

我喜欢这个判断方式，因为它没有把“文件格式”当成格式之争，而是回到消费者模型。Parquet 适合列式分析和数据湖，不代表它适合所有导出；CSV 易读，不代表它适合百亿行迁移；Native 对人不友好，但对 ClickHouse 回灌最自然。

## 大表导出必须批次化

文章用按月份并行导出的例子说明大表不应该指望一条巨型查询完成。这个方向和我在 [[topics/clickhouse-production-migration]] 里形成的判断一致：生产级导出必须拆成可重试、可对账、可限流的批次。

在真实迁移里，我会把“按分区或时间窗口并行导出”再往前推进一步：批次不能只是 for loop 里的字符串，而应该进入状态表，记录路径、行数、错误、重试次数和对账结果。这样即使作业失败，也能精确恢复，而不是重新扫整张表。

## 对我的启发

这篇文章最有价值的地方，是把 ClickHouse 导出从“会不会写命令”拉回到工程边界：文件在哪里生成，格式服务谁，压缩在哪一层做，失败后怎么续跑，大表怎么切分，云对象存储由谁写入。

对生产迁移来说，我会继续坚持 `Native + zstd` 作为 ClickHouse 到 ClickHouse 回灌的优先格式；对长期数据湖和跨系统消费，才把 `Parquet + zstd` 放到第一位。导出格式不是审美选择，而是后续导入路径、校验成本和存储成本的前置设计。

---

相关页面：[[topics/clickhouse-data-export]] · [[topics/clickhouse-production-migration]] · [[entities/clickhouse]]
