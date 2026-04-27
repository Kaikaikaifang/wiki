---
title: "ReplicatedReplacingMergeTree replaces only when the new value is bigger"
source: "https://github.com/ClickHouse/ClickHouse/issues/20867"
author: iameugenejo
published: 2021-02-18
created: 2026-04-27
description: "GitHub issue discussion about ReplicatedReplacingMergeTree, ReplacingMergeTree version semantics, sorting key duplicates, and replicated insert deduplication."
tags:
  - "clippings"
  - "clickhouse"
  - "github-issue"
---

## Metadata

- Repository: `ClickHouse/ClickHouse`
- Issue: `#20867`
- Title: `ReplicatedReplacingMergeTree replaces only when the new value is bigger`
- State: closed
- Labels: `question`, `question-answered`
- Created: `2021-02-18T02:29:01Z`
- Closed: `2021-02-18T19:15:25Z`
- Last updated: `2025-02-25T12:04:29Z`
- Reported ClickHouse version: `20.8.11.17`

## Issue Summary

The reporter observed behavior that looked like a bug in `ReplicatedReplacingMergeTree`: after inserting rows with the same `account_number` and day-level `timestamp`, `OPTIMIZE FINAL` kept the lexicographically larger `account_name` value instead of the last inserted value. The reporter noted that the same symptom did not appear with plain `ReplacingMergeTree`.

The original table used:

```sql
create table tmp.rep_repl
(
    `timestamp` DateTime,
    `account_number` UInt64,
    `account_name` String
) Engine = ReplicatedReplacingMergeTree('/clickhouse/tables/{layer}-{shard}/tmp.rep_repl', '{replica}', timestamp)
PARTITION BY formatDateTime(timestamp, '%Y%m%d')
ORDER BY (account_number, timestamp)
TTL timestamp + toIntervalDay(1);
```

The repro repeatedly inserted rows like:

```sql
insert into tmp.rep_repl select toStartOfDay(now()), 1, 'test';
insert into tmp.rep_repl select toStartOfDay(now()), 1, 'test2';
insert into tmp.rep_repl select toStartOfDay(now()), 1, 'test';
insert into tmp.rep_repl select toStartOfDay(now()), 1, 'test3';
insert into tmp.rep_repl select toStartOfDay(now()), 1, 'test2';
```

After `OPTIMIZE TABLE ... FINAL`, the row with the apparently largest string value remained, which made the reporter think non-key fields were participating in replacement order.

## Key Comments Captured

Contributor `den-crane` first pointed out that the table definition mixed two separate concepts:

- `ReplicatedReplacingMergeTree(..., timestamp)` makes `timestamp` the version column used to choose the surviving row during replacement.
- `ORDER BY (account_number, timestamp)` makes `(account_number, timestamp)` the replacement key, meaning only one row for each unique pair should remain.

Because the same `timestamp` appeared in the replacement key and as the version, the version did not actually create a newer row when all inserted rows used `toStartOfDay(now())`.

The reporter then removed the version argument and still saw confusing behavior on `ReplicatedReplacingMergeTree`. The discussion moved to the replicated insert deduplication mechanism. `den-crane` suggested trying:

```sql
SET insert_deduplicate = 0;
```

The important clarification was that replicated insert deduplication skips repeated insert blocks, not duplicate logical rows. It is a different layer from `ReplacingMergeTree` replacement. If a workload naturally repeats the same insert payload from cron jobs or multiple servers, replicated insert deduplication can prevent a later identical block from ever reaching the replacing merge logic.

The final suggested modeling direction was to add a source-generated unique insert identifier or a higher-resolution `created_at` / `timestamp`, so repeated business snapshots are physically distinct insert blocks while the replacing key still expresses the desired logical state.

The reporter revised the schema to separate the snapshot date from the higher-resolution timestamp:

```sql
create table tmp.rep_repl
(
    `timestamp` DateTime,
    `date` Date,
    `account_number` UInt64,
    `account_name` String
) Engine = ReplicatedReplacingMergeTree('/clickhouse/tables/{layer}-{shard}/tmp.rep_repl', '{replica}')
PARTITION BY date
ORDER BY (account_number, date);
```

With inserts using `now()` for `timestamp` and `toDate(now())` for `date`, the behavior matched the reporter's intended daily-account-state model.

## Captured Lesson

This issue is useful because it compresses three ClickHouse concepts that are easy to confuse:

- the `ORDER BY` expression defines the replacement key for `ReplacingMergeTree` family tables;
- the optional version column defines which row wins among rows with the same replacement key;
- replicated insert deduplication operates before replacement by skipping repeated insert blocks.

If these three layers are not modeled separately, a table can look as if it is replacing by string order or ignoring the latest row, while the real problem is that the schema gives ClickHouse no unique version signal, or the replicated insert deduplication path prevents a repeated block from entering the table at all.
