---
title: "How to Use ReplicatedReplacingMergeTree in ClickHouse"
source: "https://oneuptime.com/blog/post/2026-03-31-clickhouse-replicated-replacingmergetree/view"
author: Nawaz Dhandala
published: 2026-03-31
created: 2026-04-27
description: "OneUptime tutorial on using ReplicatedReplacingMergeTree for replicated upsert-like tables in ClickHouse."
tags:
  - "clippings"
  - "clickhouse"
  - "tutorial"
---

## Metadata

- Site: OneUptime
- Title: `How to Use ReplicatedReplacingMergeTree in ClickHouse`
- Author: Nawaz Dhandala
- Published: `2026-03-31`
- URL: `https://oneuptime.com/blog/post/2026-03-31-clickhouse-replicated-replacingmergetree/view`

## Captured Summary

The article explains `ReplicatedReplacingMergeTree` as the replicated counterpart of `ReplacingMergeTree`. It combines two ideas:

- rows with the same `ORDER BY` key are eventually deduplicated during background merges;
- data is replicated across replicas using ZooKeeper or ClickHouse Keeper.

The suggested use cases are mutable analytical datasets that still need high availability, such as user profiles, order status, or product inventory. The key modeling idea is to use `ORDER BY` as the deduplication identity and a separate version column to decide which row wins.

## Macros and Table Shape

The article starts with replica macros, usually placed in a ClickHouse server config file:

```xml
<clickhouse>
  <macros>
    <shard>01</shard>
    <replica>replica-01</replica>
  </macros>
</clickhouse>
```

It then shows a replicated replacing table shaped roughly like:

```sql
CREATE TABLE user_profiles
(
    user_id UInt64,
    username String,
    email String,
    plan LowCardinality(String),
    country LowCardinality(String),
    updated_at DateTime,
    version UInt64
)
ENGINE = ReplicatedReplacingMergeTree(
    '/clickhouse/tables/{shard}/user_profiles',
    '{replica}',
    version
)
PARTITION BY toYYYYMM(updated_at)
ORDER BY user_id;
```

The article emphasizes that `ORDER BY user_id` controls which rows are considered duplicates, while `version` controls which duplicate survives after a merge.

## Update and Read Pattern

To update a logical row, insert a new row with the same `ORDER BY` key and a higher `version`. Until background merges run, both physical rows may be present.

For immediate deduplicated reads, the article uses:

```sql
SELECT ...
FROM user_profiles FINAL
ORDER BY user_id;
```

For bulk updates, it sketches an insert-select pattern that reads the current state using `FINAL`, joins with an update source, and writes rows with `version + 1`.

## Operational Checks

The article includes several operational patterns:

- query `system.replicas` to inspect `replica_name`, `is_leader`, `absolute_delay`, `queue_size`, and `parts_to_check`;
- use `OPTIMIZE TABLE ... PARTITION ... FINAL` to force eager deduplication for a partition;
- use `FINAL` or a deduplication-aware query when counting unique logical rows before merges have caught up;
- expose a `Distributed` table over local replicated tables for cluster-wide querying.

## Limitations Captured

The article highlights four main limitations:

- `FINAL` has a read-time performance cost;
- deduplication is eventual until background merges run;
- replicated tables require ZooKeeper or ClickHouse Keeper;
- the `ORDER BY` key is a table-design decision and cannot be casually changed after creation.

## Captured Lesson

The tutorial is useful as a straightforward happy-path introduction. Read together with the ClickHouse issue on `ReplicatedReplacingMergeTree`, the practical rule becomes sharper: the standard pattern is `ORDER BY` for identity, `version` for recency, Keeper for replication, and `FINAL` only when the query needs a deduplicated view before merges finish.
