仍需解决的问题有：

1. 生产环境资源应该如何分配，才能够使得 clickhouse 集群实现稳定运行？
	资源规格限制：几分片、几副本、单节点几核几G
2. 数据回灌应该如何设计，才能够平稳、用户无感且自动化的迁移生产环境数据？
3. 若采用异步副本的方案，不再需要分片，仍通过 `clickhouse-keeper` 管理，是否还需要建立 Distributed 表？数据库表由 `MergeTree` 切换为 `ReplicatedReplacingMergeTree` 能否直接将静态源 attach 到异步副本，而非按行写入？参考 wiki 及之前的迁移路径，在 /Users/kaikai/projects/test/test-migration/parallel-replicas 目录下设计一个验证方案（TODO.md）
4. 如何实现 clickhouse 集群的负载均衡？client 直接指向一个已经存在的 clickhouse 节点？如果这个节点挂了咋办？能否借助 traefik 实现一个类似 clickhouse cloud 的负载均衡方案？参考 wiki 以及原方案的 traefik 配置，在 /Users/kaikai/projects/deploy/charts 目录下设计一个验证方案（TODO.md）

## 集群架构方案

- 异步副本

## 数据库表方案

- Replicated 数据库引擎
- scalar 和 media 数据使用 ReplicatedReplacingMergeTree 表引擎
- log 使用 ReplicatedMergeTree 表引擎

## 数据回灌方案

数据回灌方案应尽可能的简单可控。

1. 通过快照建立静态数据源
2. 两个方案：
	1. 分批导出为 `Native` 文件，按行导入新集群
	2. `ATTACH PART`

## 负载均衡方案

1. Service DNS 而非 Pod DNS