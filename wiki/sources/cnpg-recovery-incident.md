---
title: CNPG 事故恢复与存储策略复盘
type: source
tags: [Kubernetes, CloudNativePG, PostgreSQL, 数据恢复, 持久化存储]
source_count: 0
updated: 2026-05-26
---

> 这次复盘真正教我的不是某条 `kubectl` 命令，而是有状态系统里最容易被低估的一件事：控制器可以自动重建 Pod，但它不能替我判断哪块盘才是权威数据。

## 事故主线

这次问题从 CloudNativePG 管理的 PostgreSQL 实例磁盘空间不足开始。数据库实例因为低磁盘空间拒绝启动，随后又叠加了集群对象被重建、旧主库云盘使用 `Delete` 回收策略、部分旧副本盘仍被 `Retain` 保存等多个状态。真正的恢复入口不是“让 Operator 再试一次”，而是先确认哪些 PV 还存在、哪些 PVC 已经失效、哪一份数据可以作为恢复候选。

我更愿意把这个过程拆成三层：第一层是保全证据，先给仍在的旧副本盘做快照；第二层是临时恢复服务，用快照恢复出的 clone 承接数据库连接；第三层才是规范迁回，把恢复 clone 里的数据通过 in-cluster logical dump/restore 迁回新的 CNPG 管理实例。

## 恢复路径

比较关键的动作顺序是：先确认存储类支持扩容，再把 CNPG 期望容量提升到更安全的 80Gi；对旧副本 PV 标注来源并创建 forensic PVC；在挂载和启动恢复 clone 前创建 CSI snapshot；确认恢复 clone 的 `app` 数据库可读且不处于 recovery；短期把数据库 Service 指向恢复 clone，让业务先恢复读写。

规范迁回时，我没有继续依赖本地 `kubectl exec` 管道，而是使用集群内 Job 执行 `pg_dump -Fc | pg_restore`。这个选择的核心原因是减少本地网络、终端断开和长管道的脆弱性。迁移前先把业务写入服务缩到 0，避免恢复 clone 与目标 CNPG 之间继续分叉；迁移后用精确行数对比所有业务表，而不是只看 `pg_stat_user_tables` 的估算行数。

## 主从同步不是看 Ready 就结束

一个很值得记录的细节是，CNPG 集群一度显示健康，但其中一个 replica 已经落后到请求的 WAL segment 被主库清理。只看 `READY=3` 会给人一种错误安全感。真正可靠的检查应该从主库看 `pg_stat_replication`，确认每个 replica 都在 `streaming`，并且 `sent_lsn`、`write_lsn`、`flush_lsn`、`replay_lsn` 没有不可接受的差距；再到副本看 `pg_stat_wal_receiver` 是否真的连着主库。

当副本日志出现“requested WAL segment has already been removed”时，这不是等待就能自然恢复的慢同步，而是副本已经错过了追赶窗口。正确动作是删除坏副本的 Pod 和 PVC，让 CNPG 以主库为准重新做 basebackup。重建后的新副本内存显著低于老副本，也不一定说明未接流量；刚重建的实例 page cache 冷、连接少，RSS 低是正常现象，应该用 Service endpoints 和 `pg_stat_activity` 验证是否接入。

## Retain 是防误删刹车，不是备份

这次最大的存储策略补丁，是把业务 PostgreSQL 数据盘的 PV 回收策略从 `Delete` 改为 `Retain`，并把 CNPG manifest 的 `storageClass` 切到已有的 Retain 版 StorageClass。这里我会特别强调一个区别：`Retain` 只能防止“PVC 被删时云盘也被连带删除”，不能防止数据被错误写入、逻辑损坏、主从一起复制坏数据，也不能替代快照或 PostgreSQL 备份。

当前最稳妥的恢复心法是：Pod 被删，优先相信控制器会用原 PVC 重建；PVC 被删，先暂停调和，找到 `Released` 的 Retain PV，清理旧 `claimRef` 后用同名 PVC 重新绑定；如果 PV 也没了，才进入 snapshot、备份或云厂商控制台层面的恢复路径。

来源：本次 CNPG / PostgreSQL 事故恢复会话

相关页面：[[topics/cloudnativepg-recovery]] · [[topics/kubernetes-persistent-storage]] · [[entities/cloudnativepg]] · [[entities/kubernetes]]
