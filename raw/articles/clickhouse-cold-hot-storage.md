# 目标

本文档用于在 Kubernetes 中部署的 ClickHouse 上，为现有 `MergeTree` 表接入阿里云 OSS（S3 兼容）作为冷存储，依据业务数据的 `timestamp` 字段实现：

- 热数据保留在本地盘
- 冷数据自动迁移到 OSS
- 业务查询仍然访问同一张表，用户无感

# 一、方案概览

整体方案如下：

- 默认盘 `default` 作为热层
- 阿里云 OSS 作为冷层磁盘 `cold_oss`
- 通过 `hot_cold_policy` 将两者组织成一个存储策略
- 对已有表 `app.log` 执行：
    - `MODIFY SETTING storage_policy = 'hot_cold_policy'`
    - `MODIFY TTL ... TO VOLUME 'cold'`

# 二、阿里云 OSS 前置要求

阿里云官方说明，OSS 兼容 S3 API，但**仅支持虚拟托管风格（Virtual Hosted Style）访****问**，也就是 Bucket 名必须作为子域名的一部分；路径风格在 OSS 上不应作为最终配置使用。([阿里云](https://www.alibabacloud.com/help/zh/oss/developer-reference/compatibility-with-amazon-s3?utm_source=chatgpt.com))

因此，**正确 endpoint 形式**应为：

```Plain
https://<bucket>.oss-cn-shanghai.aliyuncs.com/<prefix>/
```

例如：

```Plain
https://clickhouse-cold-001.oss-cn-shanghai.aliyuncs.com/clickhouse/log/
```

而不是：

```Plain
https://s3.oss-cn-shanghai.aliyuncs.com/clickhouse-cold-001/clickhouse/log/
```

# 三、Kubernetes 侧配置

**OSS** **Secret**

```YAML
apiVersion: v1
kind: Secret
metadata:
  name: clickhouse-oss-secret
  namespace: default
type: Opaque
stringData:
  OSS_S3_ENDPOINT: "https://clickhouse-cold-001.oss-cn-shanghai.aliyuncs.com/clickhouse/log/"
  OSS_S3_ACCESS_KEY_ID: "你的AK"
  OSS_S3_ACCESS_KEY_SECRET: "你的SK"
```

**ClickHouse 存储配置 ConfigMap**

可用配置如下：

- `<s3_cache>`是 S3 中数据的一个本地磁盘缓冲，冷数据查询后会被放入缓冲中，下一次查询会直接从缓冲区查询，大大加快查询速率
- 这里 `perform_ttl_move_on_insert=false` 的含义是：如果插入的数据 part 已经命中 TTL move，不要在 INSERT 时直接写到冷层。官方说明默认情况下命中 TTL 的 part 可能在插入时就直接进入目标卷；对 S3 这类慢存储，关闭这个选项通常更稳。([ClickHouse](https://clickhouse.com/docs/zh/operations/system-tables/storage_policies?utm_source=chatgpt.com))

```YAML
apiVersion: v1
kind: ConfigMap
metadata:
  name: clickhouse-storage-config
  namespace: default
data:
  storage.xml: |
    <clickhouse>
      <storage_configuration>
        <disks>
          <default>
            <keep_free_space_bytes>0</keep_free_space_bytes>
          </default>

          <cold_oss>
            <type>s3</type>
            <endpoint from_env="OSS_S3_ENDPOINT"/>
            <access_key_id from_env="OSS_S3_ACCESS_KEY_ID"/>
            <secret_access_key from_env="OSS_S3_ACCESS_KEY_SECRET"/>
          </cold_oss>

          <s3_cache>
            <type>cache</type>
            <disk>cold_oss</disk>
            <path>/var/lib/clickhouse/disks/s3_cache/</path>
            <max_size>10737418240</max_size>
          </s3_cache>
        </disks>

        <policies>
          <hot_cold_policy>
            <volumes>
              <default>
                <disk>default</disk>
              </default>
              <cold>
                <disk>s3_cache</disk>
                <perform_ttl_move_on_insert>false</perform_ttl_move_on_insert>
              </cold>
            </volumes>
          </hot_cold_policy>
        </policies>
      </storage_configuration>
    </clickhouse>
```

**StatefulSet 挂载**

确保容器里挂载了：

- `/etc/clickhouse-server/config.d/storage.xml`
- OSS Secret 对应的环境变量

```YAML
env:
  - name: OSS_S3_ENDPOINT
    valueFrom:
      secretKeyRef:
        name: clickhouse-oss-secret
        key: OSS_S3_ENDPOINT
  - name: OSS_S3_ACCESS_KEY_ID
    valueFrom:
      secretKeyRef:
        name: clickhouse-oss-secret
        key: OSS_S3_ACCESS_KEY_ID
  - name: OSS_S3_ACCESS_KEY_SECRET
    valueFrom:
      secretKeyRef:
        name: clickhouse-oss-secret
        key: OSS_S3_ACCESS_KEY_SECRET

volumeMounts:
  - mountPath: /etc/clickhouse-server/config.d/storage.xml
    name: storage-config
    subPath: storage.xml
```

如果要对已有的 ClickHouse 加这个配置，直接注入 `/etc/clickhouse-server/config.d/storage.xml` 然后写入相关配置即可，这个配置会自动加载，不需要重启 ClickHouse。

# 四、启动验证

Pod 启动后，进入 ClickHouse client，先验证磁盘和策略是否已加载。

**查看磁盘**

```SQL
SELECT
    name,
    type,
    is_remote,
    path
FROM system.disks
ORDER BY name;
```

**查看策略**

```SQL
SELECT
    policy_name,
    volume_name,
    disks,
    volume_priority,
    perform_ttl_move_on_insert
FROM system.storage_policies
WHERE policy_name = 'hot_cold_policy'
ORDER BY volume_priority;
```

# 五、修改已有表

以 `app.log` 为例，本次方案中，原本 `app.log` 已经存在于 ClickHouse 中。

**给表挂上新策略**

```SQL
ALTER TABLE app.log
MODIFY SETTING storage_policy = 'hot_cold_policy';
```

**添加** **TTL**

测试时先用 1 分钟，方便快速验证，下面的意思是 timestamp 距今小于 1 分钟的数据会存入 default 也就是原来的磁盘中，timestamp 距今大于 1 分钟的数据会存入 s3 中：

```SQL
ALTER TABLE app.log
MODIFY TTL
    toDateTime(timestamp) TO VOLUME 'default',
    toDateTime(timestamp) + INTERVAL 1 MINUTE TO VOLUME 'cold';
```

正式环境再改成实际窗口，例如 30 天：

```SQL
ALTER TABLE app.log
MODIFY TTL
    toDateTime(timestamp) TO VOLUME 'default',
    toDateTime(timestamp) + INTERVAL 30 DAY TO VOLUME 'cold';
```

# 六、测试数据与验证方法

**插入测试数据**

插入一条旧数据和一条新数据：

```SQL
INSERT INTO app.log
    (uid, projectId, experimentId, epoch, level, message, tag, timestamp)
VALUES
    (1, 'p1', 'exp1', 1, 'INFO', 'old log should move to cold', 'test', now64(3) - INTERVAL 5 MINUTE),
    (2, 'p1', 'exp1', 2, 'INFO', 'new log should stay hot first', 'test', now64(3));
```

**触发** **TTL** **move**

TTL move 默认在后台 merge 时触发，不一定立刻发生。官方文档说明 TTL 事件是在合并期间触发的。为了测试，可以手工执行：

```SQL
OPTIMIZE TABLE app.log FINAL;
```

**查看 part 是否迁移到冷盘**

```SQL
SELECT
    name,
    disk_name,
    rows,
    bytes_on_disk,
    modification_time
FROM system.parts
WHERE active
  AND database = 'app'
  AND table = 'log'
ORDER BY modification_time DESC;
```

成功的标志就是 `disk_name` 从 `default` 变成 `cold_oss`。

**在** **OSS** **查看数据**

![](https://rcnpx636fedp.feishu.cn/space/api/box/stream/download/asynccode/?code=MGQxMzk0MTFiZTliOGVkYzY4NzQyYzM3MTcxYmFjM2ZfbWZLd0IwSFN5aHM4UEVaOXdKTmdTT1FIWWU0YmJiQlVfVG9rZW46UVBDWWJEUndNb0Y4TEl4cDZtRGM5eUdlbndnXzE3NzcyODUwOTc6MTc3NzI4ODY5N19WNA)

# 七、冷热数据查询速率测试

OSS 与 ClickHouse 使用同一内网

将 TTL 设置成 5 分钟

```SQL
ALTER TABLE app.log
MODIFY TTL
    toDateTime(timestamp) TO VOLUME 'default',
    toDateTime(timestamp) + INTERVAL 5 MINUTE TO VOLUME 'cold';
```

插入 100 万冷数据

```SQL
INSERT INTO app.log
    (uid, projectId, experimentId, epoch, level, message, tag, timestamp)
SELECT
    number + 900000,
    'bench_project',
    'cold_exp',
    number,
    'INFO',
    concat('cold log ', toString(number)),
    'bench',
    now64(3) - INTERVAL 6 MINUTE
FROM numbers(1000000);
```

插入 100 万热数据

```SQL
INSERT INTO app.log
    (uid, projectId, experimentId, epoch, level, message, tag, timestamp)
SELECT
    number + 900000,
    'bench_project',
    'hot_exp',
    number,
    'INFO',
    concat('hot log ', toString(number)),
    'bench',
    now64(3)
FROM numbers(1000000);
```

查询热数据

```SQL
SELECT
    uid,
    message,
    timestamp
FROM app.log
WHERE projectId = 'bench_project'
  AND experimentId = 'hot_exp'
ORDER BY uid
LIMIT 80000;
```

```YAML
80000 rows in set. Elapsed: 0.049 sec. Processed 1.00 million rows, 76.89 MB (20.39 million rows/s., 1.57 GB/s.)
Peak memory usage: 56.18 MiB.
```

查询冷数据

```SQL
SELECT
    uid,
    message,
    timestamp
FROM app.log
WHERE projectId = 'bench_project'
  AND experimentId = 'cold_exp'
ORDER BY uid
LIMIT 80000;
```

```YAML
80000 rows in set. Elapsed: 0.257 sec. Processed 1.00 million rows, 78.89 MB (3.89 million rows/s., 306.89 MB/s.)
Peak memory usage: 84.08 MiB.
```

再查询一遍冷数据

```SQL
SELECT
    uid,
    message,
    timestamp
FROM app.log
WHERE projectId = 'bench_project'
  AND experimentId = 'cold_exp'
ORDER BY uid
LIMIT 80000;
```

```YAML
80000 rows in set. Elapsed: 0.065 sec. Processed 1.00 million rows, 78.89 MB (15.31 million rows/s., 1.21 GB/s.)
Peak memory usage: 83.23 MiB.
```

结果汇总

|                       |           |                 |             |           |                   |
| --------------------- | --------- | --------------- | ----------- | --------- | ----------------- |
| 查询类型                  | 耗时        | 处理速度 (行/秒)      | 处理速度 (数据量)  | 峰值内存      | 说明                |
| **热数据**               | 0.049 sec | 20.39 million/s | 1.57 GB/s   | 56.18 MiB | 首次查询，性能最佳         |
| **冷数据（内网首次）**         | 0.257 sec | 3.89 million/s  | 306.89 MB/s | 84.08 MiB | 冷数据从OSS加载，走内网端点，慢 |
| **冷数据（内网二次）**         | 0.065 sec | 15.31 million/s | 1.21 GB/s   | 83.23 MiB | 数据已缓存，速度提升        |
| **冷数据（****公网****首次）** | 0.314 sec | 3.19 million/s  | 251.63 MB/s | 80.31 MiB | 冷数据从OSS加载，走公网端点，慢 |