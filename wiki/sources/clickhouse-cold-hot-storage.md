---
title: ClickHouse 冷热分层实战
type: source
tags: [数据库, ClickHouse, 冷热分层, OSS]
source_count: 1
source_file: raw/articles/clickhouse-cold-hot-storage.md
author: 内部实践笔记
published: 2026-04-27
updated: 2026-04-27
---

来源：[[entities/clickhouse]]

## 核心结论

这篇笔记的价值不在于又证明了一次“ClickHouse 可以把冷数据放对象存储”，而是把这个能力落到了 Kubernetes、阿里云 OSS、`storage_policy`、TTL move 和查询验证这条完整链路上。

我会把它理解成一份很实用的生产前检查单：冷层不是一个抽象架构名词，而是一组必须同时成立的细节。OSS endpoint 要写成虚拟托管风格，ClickHouse 要能从环境变量拿到 AK / SK，`s3` disk 外面最好再包一层本地 `cache` disk，表必须显式挂上 storage policy，并用 TTL 把过期 part 移到 cold volume。

## 实施主线

这份方案把冷热分层拆成四层：

- 本地 `default` disk 作为热层；
- 阿里云 OSS 作为远端 `cold_oss` disk；
- `s3_cache` 作为冷层上的本地缓存；
- `hot_cold_policy` 把热卷和冷卷组合成表级存储策略。

这比“把 S3 配进 ClickHouse”更准确。真正被表使用的不是某个裸 disk，而是 policy；真正影响查询体感的也不是 OSS 是否可用，而是 cache disk 是否覆盖了会反复访问的冷数据工作集。

我尤其会记住两个配置判断。

第一，阿里云 OSS 的 S3 兼容访问应使用 virtual hosted style，也就是 bucket 作为域名的一部分，例如 `https://<bucket>.oss-cn-shanghai.aliyuncs.com/<prefix>/`。路径风格 endpoint 在 OSS 上不应作为最终配置。这个细节很容易被忽略，但它会直接决定 ClickHouse 是否能稳定访问对象存储。

第二，冷卷上设置 `perform_ttl_move_on_insert=false` 更像是生产保守默认：如果插入的 part 已经命中 TTL，不要让它在 INSERT 路径上直接写远端冷层，而是让后台 TTL move / merge 去完成迁移。对于 OSS 这类慢介质，我更倾向把这个成本移出写入路径。

## 验证方式

这篇笔记比较好的地方，是没有停在配置片段，而是给了可验证路径：

- 通过 `system.disks` 确认 `default`、`cold_oss`、`s3_cache` 是否加载；
- 通过 `system.storage_policies` 确认 `hot_cold_policy` 的卷顺序与 `perform_ttl_move_on_insert`；
- 对已有表执行 `MODIFY SETTING storage_policy = 'hot_cold_policy'`；
- 用 `MODIFY TTL` 按 `timestamp` 把旧数据迁到 cold volume；
- 用 `OPTIMIZE TABLE ... FINAL` 在测试中主动触发 TTL move；
- 通过 `system.parts.disk_name` 观察 part 是否从本地盘移到冷层。

这里有个小但重要的观念：TTL move 不是一条“立刻搬家”的命令，而是在后台 merge 过程中触发的存储落点变化。测试时可以用 `OPTIMIZE FINAL` 加速观察，但生产上不能把它当成日常运维按钮随便打。

## 性能含义

笔记里的 100 万行测试很符合我对冷热分层的直觉：热数据首次查询最快，冷数据首次查询明显慢，冷数据二次查询因为命中本地缓存而接近热数据。

具体数字不应该被当成通用 benchmark，因为它只对应这次表结构、内网 / 公网路径、数据量和缓存大小。但方向很有价值：

- 热数据查询约 `0.049s`；
- 内网冷数据首次查询约 `0.257s`；
- 内网冷数据二次查询约 `0.065s`；
- 公网冷数据首次查询约 `0.314s`。

我会从这里得出一个更工程化的结论：冷热分层不是为了让冷数据和热数据永远一样快，而是为了让大部分长期低频数据用对象存储承载，同时让被再次访问的冷数据能通过本地缓存回到可接受的速度区间。

## 对我的启发

这篇笔记把 [[sources/clickhouse-external-disks-for-storing-data]] 里的原语翻译成了可落地的 Kubernetes 配置。它提醒我，生产设计里最容易出问题的不是“ClickHouse 是否支持 S3”，而是这些边界是否逐个被验证：

- endpoint 风格是否符合云厂商实现；
- Secret 与 ConfigMap 是否真的进入 ClickHouse 进程；
- 表是否已经挂上新 policy；
- TTL 是否按照业务时间字段表达冷热窗口；
- part 是否真的迁到预期 disk；
- 冷数据首次查询和缓存后查询是否都在可接受范围内。

这也让我更倾向把冷热分层当成迁移后的长期成本控制能力，而不是回灌阶段的捷径。历史数据可以先完整进入新集群，再由 storage policy、TTL、后台 merge 和缓存逐步决定它们在热盘与冷层之间的真实落点。

---

相关页面：[[topics/clickhouse-deployment-topologies]] · [[topics/clickhouse-production-migration]] · [[sources/clickhouse-external-disks-for-storing-data]] · [[sources/clickhouse-separation-storage-compute]] · [[entities/clickhouse]]
