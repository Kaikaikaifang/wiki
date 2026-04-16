---
title: PostgreSQL 索引 DDL 锁
type: topic
tags:
  - PostgreSQL
  - 索引
  - DDL
  - 锁
source_count: 0
updated: 2026-04-16
---

> 在 PostgreSQL 里，`CONCURRENTLY` 的核心价值不是“更快”，而是尽量避免索引 DDL 长时间挡住业务读写。

## 先说结论

- **`create index` 不带 `concurrently`**：会对目标表加 `SHARE` 级别锁；普通 `select` 通常还能继续，但 `insert`、`update`、`delete` 会被阻塞，直到建索引完成；
- **`drop index` 不带 `concurrently`**：阻塞更重，会挡住该表上的读写访问，因此在线上更容易被体感为“锁表”。

## 建索引时的具体表现

普通 `create index` 需要完整扫描表并构建新索引结构。若表很大，这个过程可能持续较久。

它的典型表现是：

- 读请求通常还能执行；
- 写请求会开始排队；
- 应用层会表现为写延迟飙升、连接堆积，严重时连带影响上游服务超时。

因此它更像是**“允许读、不允许写”**的表级阻塞，而不是所有访问都完全停住。

## 删索引时的具体表现

普通 `drop index` 虽然执行动作本身常常很快，但它为了安全地移除索引，会使用更强的锁。

它的典型表现是：

- 不只写请求，连读请求也可能被挡住；
- 若前面已经有长事务持有相关锁，`drop index` 会先等待；
- 一旦它在锁队列里排队，后续访问该表的请求也可能跟着堵住。

这也是为什么很多事故现场里，`drop index` 比 `create index` 更容易制造“整张表突然不可用”的体感。

## 为什么会出现“明明在等锁，却把后面也堵住了”

PostgreSQL 的锁等待不只是当前语句自己卡住那么简单。

如果一个需要强锁的 DDL 已经在前面排队，后续与它冲突的请求往往也不能直接穿过去，而是继续在后面排队。因此业务侧看到的常见现象是：

- 先出现一个等待中的索引 DDL；
- 随后普通查询或写入数量开始堆积；
- 最后表现为整条链路一起变慢。

## `concurrently` 解决的是什么

`concurrently` 的主要作用，是把索引创建或删除拆成更适合在线执行的流程，尽量避免长时间阻塞普通 `select`、`insert`、`update`、`delete`。

它换来的代价通常是：

- 执行时间更长；
- 过程更复杂；
- 有额外限制，例如不能放在显式事务块里。

所以它不是“免费优化”，而是**用更复杂的 DDL 流程，换业务可用性**。

## 实务建议

- 线上大表建索引，默认优先 `create index concurrently`；
- 线上删索引，默认优先 `drop index concurrently`；
- 执行前先排查长事务、锁等待与慢 SQL；
- 若必须使用普通 DDL，尽量放在低峰窗口，并提前准备回滚与观测手段。

---

来源：本次 `query` 归档，未新增外部来源

相关页面：[[topics/index-maintenance-tradeoffs]] · [[topics/sql-indexing]] · [[topics/sql-execution-plans]]
