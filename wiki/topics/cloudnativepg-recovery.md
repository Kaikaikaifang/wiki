---
title: CloudNativePG 恢复与持久化策略
type: topic
tags: [CloudNativePG, PostgreSQL, Kubernetes, 数据恢复, 持久化存储]
source_count: 1
updated: 2026-05-26
---

> 我现在会把 CloudNativePG 这类数据库 Operator 理解成“会帮你调和资源状态的控制面”，而不是“替你判断数据权威性的保险箱”。事故恢复时最危险的错觉，就是看到 Pod 被重建、Cluster 变 Ready，就以为数据路径已经正确。

## 先判断权威数据，再让控制器动作

CNPG 的优势是能把 PostgreSQL 实例、Service、证书、replica、PVC 这些资源统一纳入调和。但当事故牵涉到 PVC 删除、PV 回收策略、旧副本盘、快照恢复和 Service selector 临时切换时，第一步不是让 Operator “自动修”，而是先回答：哪一份数据是完整的，哪一块云盘还存在，哪个实例可以作为恢复源。

我会把 CNPG 恢复拆成四个阶段：保全、临时恢复、规范迁回、恢复高可用。保全阶段优先给候选旧盘做快照，避免后续挂载或启动过程改变证据。临时恢复阶段可以用 snapshot clone 快速拉起 PostgreSQL，必要时让业务短期指向它。规范迁回阶段则用集群内 Job 执行 logical dump/restore，避免本地终端和网络成为长迁移链路的一部分。最后才恢复 CNPG 多副本，并验证每个 replica 的 WAL 状态。

## Pod 删除和 PVC 删除是两个完全不同的问题

Pod 被删除通常是控制器问题，不是数据问题。只要 PVC 还在，CNPG 或 Kubernetes 会重建 Pod 并重新挂载原盘；这时最该做的是检查 PVC/PV 是否 Bound，等 Pod Ready，而不是手动新建空盘。

PVC 被删除则进入数据生命周期问题。如果 PV 的 `reclaimPolicy` 是 `Delete`，底层云盘大概率会被连带删除；如果是 `Retain`，PV 会进入 Released，云盘仍在，但需要人工清理旧 `claimRef`，用同名 PVC 显式绑定旧 PV。这个动作必须在确认 CNPG 不会抢先创建新空 PVC 之后进行，所以我倾向先暂停调和，再恢复绑定。

## Service 切换要有“回切”意识

恢复 clone 可以临时救服务，但它不应该成为长期事实来源。临时把数据库 Service 指到 clone 时，要记录 selector、endpoint 和原 CNPG 实例关系；迁回时也要先停业务写入，再清空目标库、恢复数据、对比行数，最后把 Service 指回 CNPG primary / replica。

这里最容易出错的是把估算统计当成一致性校验。`pg_stat_user_tables` 的行数只是统计估算，刚恢复后可能严重失真。真正需要确认的是重要表或全部业务表的精确 `count(*)` 是否一致，尤其是大表。

## 副本健康要看 WAL，不只看 Cluster Ready

CNPG 显示 `READY=3` 不代表每个副本都能继续追主库。事故后我更信任这组检查：主库上看 `pg_stat_replication`，确认每个 replica 是 `streaming`；副本上看 `pg_stat_wal_receiver`，确认它真的连着主库；必要时比较 `sent_lsn`、`flush_lsn`、`replay_lsn` 的差距。

如果副本日志里出现请求的 WAL segment 已被移除，说明它已经错过普通 streaming 能追上的窗口。此时继续等待意义不大，应该删除坏副本的数据卷，让 CNPG 重新从当前 primary 做 basebackup。重建后的副本内存低，不一定是没接入业务；新副本缓存冷、连接少，应该用 Service endpoints 和 `pg_stat_activity` 判断它是否进入读流量池。

## 我会保留的操作原则

- 数据库类 PVC 默认应该使用 `Retain`，尤其是在开发环境也有真实业务数据时。
- `Retain` 只是防误删，不替代 VolumeSnapshot、WAL 归档或 PostgreSQL 备份。
- 迁移应尽量在集群内执行，减少本地终端、网络和长管道风险。
- 切服务前先停写入，切完后做精确数据校验，再恢复应用。
- Replica 重建后必须用 WAL 位置验证，而不是只相信 Operator 汇总状态。

来源：[[sources/cnpg-recovery-incident]]

相关页面：[[entities/cloudnativepg]] · [[entities/kubernetes]] · [[topics/kubernetes-persistent-storage]] · [[sources/ack-dynamic-disk-volumes]] · [[sources/ack-disk-volume-snapshots]]
