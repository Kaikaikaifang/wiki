---
title: ClickHouse 数据导出
type: topic
tags: [数据库, ClickHouse, 导出, 数据格式, 对象存储]
source_count: 1
updated: 2026-04-28
---

> 我现在会把 ClickHouse 数据导出理解成一个三元组：**导出通道、文件格式、下游消费者**。只讨论 `FORMAT CSV` 或 `INTO OUTFILE` 太容易把问题看小；真正决定导出方案质量的，是这三者是否匹配。

## 先拆开格式和通道

[[sources/oneuptime-clickhouse-export-file-formats]] 给了一个很好的基础框架。`FORMAT` 子句决定结果如何序列化，通道决定结果写到哪里。

常见通道大致有四类：

- SQL 直接 `FORMAT`，让结果输出到客户端；
- `clickhouse-client` 执行查询，再把 stdout 重定向成本地文件；
- HTTP 接口返回 response body，由 `curl -o` 或调用方保存；
- `INSERT INTO FUNCTION s3(...)` 让 ClickHouse 把结果写到对象存储。

这个拆分能避免很多误判。比如 `FORMAT Parquet` 只是说结果是 Parquet，不代表文件一定在服务端；`INTO OUTFILE` 看起来像服务端写文件，但实际是客户端侧能力；HTTP 接口不支持 `INTO OUTFILE`，但可以把 response body 直接保存成文件。

## 文件落点是生产边界

导出脚本最容易出问题的地方，不是 SQL 写错，而是“文件到底落在哪里”没有被说清楚。

如果用 `INTO OUTFILE`，文件在运行 `clickhouse-client` 或 `clickhouse-local` 的机器上。这个机器可能是开发者电脑、跳板机、Kubernetes Job 容器，也可能是一次性 CI runner。路径、磁盘容量、权限、清理策略都跟 ClickHouse server 没有天然关系。

如果走 HTTP，文件在调用方保存。这个模型更直观，但认证、超时、网络中断和大响应流式处理要自己承担。

如果走 `s3()` 表函数，ClickHouse 直接写对象存储。这对生产管道更自然，尤其是导出目标本来就是 OSS / S3 中转层时。但这也意味着 ClickHouse 侧必须有对象存储 endpoint、凭证、路径规划和失败重试纪律。

我会把这条规则放在导出方案最前面：先确定文件落点，再写 SQL。

## 格式从下游倒推

格式选择不应该从“哪个更常见”开始，而应该从下游消费开始。

`Parquet + zstd` 很适合数据湖、对象存储归档和跨系统分析，因为它列式、压缩友好，也被 Spark、Trino、Hive 等生态广泛理解。`CSVWithNames` 适合人工检查、表格工具和轻量 BI，但不适合大规模精确回灌。`JSONEachRow` 适合事件流、日志式交换和便于逐行处理的文本管道。

`Native` 则更像 ClickHouse 自己的内部高速通道。它不适合人读，也不适合作为通用数据湖格式，但在 ClickHouse 到 ClickHouse 的迁移、回灌和补跑里非常有价值。只要两端 ClickHouse 版本和 schema 兼容，它通常比文本格式更少浪费 CPU 和解析成本。

所以我会这样记：

- 给人看，优先 CSV；
- 给数据湖，优先 Parquet；
- 给事件管道，优先 JSONEachRow；
- 给 ClickHouse 回灌，优先 Native；
- 给自定义高性能管道，再考虑 RowBinary、Arrow 或更专门的格式。

## 大表导出不是一条命令

大表导出最危险的想象，是一条 `SELECT * FROM huge_table FORMAT ...` 跑到底。它看起来简单，实际把扫描压力、网络传输、文件写入、失败恢复和目标容量都压在一次执行里。

更稳的做法是批次化：按分区、时间窗口、业务 key 或目标 shard 维度切分，让每个批次都有独立路径、状态、重试和对账结果。并行可以有，但并发要受控，不能把源端 merge、磁盘、网络和对象存储写入同时打满。

这也解释了为什么 [[topics/clickhouse-production-migration]] 里的历史回灌不能只是一组 shell 循环。循环能跑 demo，状态表才能跑生产。导出批次需要成为系统事实，而不是终端历史。

## 和生产迁移的关系

对 ClickHouse 生产迁移来说，我会把导出格式判断压成一句话：**面向 ClickHouse 回灌优先 `Native + zstd`，面向数据湖交换优先 `Parquet + zstd`。**

这条判断直接影响回灌主路径。对象存储中转不是为了把历史数据“归档掉”，而是为了把源端读和目标端写解耦。只要目标仍是 ClickHouse 集群，导出格式就应该服务于高效导入、批次对账和失败补跑，而不是为了让文件本身更通用。

---

来源：[[sources/oneuptime-clickhouse-export-file-formats]]

相关页面：[[entities/clickhouse]] · [[topics/clickhouse-production-migration]] · [[sources/oneuptime-clickhouse-export-file-formats]]
