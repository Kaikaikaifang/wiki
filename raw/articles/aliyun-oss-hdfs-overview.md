---
title: "非EMR集群接入OSS-HDFS服务快速入门"
source: "https://help.aliyun.com/zh/oss/user-guide/oss-hdfs-overview?spm=a2c4g.11186623.help-menu-31815.d_0_15_2_0_0.3d897499Tnyyc3&scm=20140722.H_405089._.OR_help-T_cn~zh-V_1#38bdbb130eryx"
author:
published:
created: 2026-04-28
description: "想在非EMR集群中高效接入OSS-HDFS服务？本指南提供从环境准备到JindoSDK配置的完整步骤，并附有core-site.xml代码示例与HDFS Shell常用命令，助您在ECS上快速完成数据读写，轻松上手。"
tags:
  - "clippings"
---
OSS-HDFS服务（JindoFS服务）是一个云原生数据湖存储功能。基于统一的元数据管理能力，完全兼容HDFS文件系统接口，满足大数据和AI等领域的数据湖计算场景。

## 注意事项

**警告**

- 当您为某个Bucket开通OSS-HDFS服务后，OSS-HDFS服务数据将保留在Bucket的`.dlsdata/` 目录下。禁止以非OSS-HDFS提供的方式对该目录及其下的Object执行写入操作，如重命名、删除等，以避免影响服务或数据丢失。
- 若发生账户欠费、删除服务依赖的RAM角色 `AliyunOSSDlsDefaultRole` 等影响HDFS运行的情况，HDFS后台服务可能会进入安全模式。该模式下，后台服务将全部暂停（如审计日志、异步删除、冷热分层等）。当影响消失时，后台服务会在一段时间内自动恢复。

开通OSS-HDFS服务后，您在使用涉及`.dlsdata/` 目录写入操作的OSS其他功能时，可能存在数据丢失、数据污染、数据无法正常访问等风险。更多信息，请参见 [使用前须知](https://help.aliyun.com/zh/oss/user-guide/notice-before-using-oss-hdfs-service#concept-2213062) 。

## 费用说明

- 元数据管理费用
	暂不计费。
- 数据使用费用
	使用OSS-HDFS服务时，数据块采用了OSS的存储方式。因此，OSS的计量计费方式适用于OSS-HDFS服务中的数据块。更多信息，请参见 [计费概述](https://help.aliyun.com/zh/oss/billing-overview#concept-n4t-mwg-tdb) 。

## 功能优势

通过OSS-HDFS服务，无需对现有的Hadoop、Spark大数据分析应用做任何修改。通过简单的配置即可像在原生HDFS中那样管理和访问数据，同时获得OSS无限容量、弹性扩展、更高的安全性、可靠性和可用性支撑。

作为云原生数据湖基础，OSS-HDFS在满足EB 、亿级文件管理服务、TB级吞吐量的同时，全面融合大数据存储生态，除提供对象存储扁平命名空间之外，还提供了分层命名空间服务。分层命名空间支持将对象组织到一个目录层次结构中进行管理，并能通过统一元数据管理能力进行内部自动转换。同时相较于传统HDFS的元数据管理节点NameNode的主备冗余方式，OSS-HDFS的元数据管理采用多节点多活冗余机制，具备更好的数据冗余能力。对Hadoop用户而言，无需做数据复制或转换就可以实现像访问本地HDFS一样高效的数据访问，极大提升整体作业性能，降低了维护成本。

## 功能特性

<table><tbody><tr><td rowspan="1" colspan="1"><p><b>功能特性</b></p></td><td rowspan="1" colspan="1"><p><b>说明</b></p></td><td rowspan="1" colspan="1"><p><b>参考文档</b></p></td></tr><tr><td rowspan="1" colspan="1"><p>回收站</p></td><td rowspan="1" colspan="1"><p>当您从OSS-HDFS服务误删除文件时，文件不会立即被彻底删除，而是转至回收站。回收站中的数据保存时间默认是3天，支持自定义数据保存时间为1~14天。在回收站数据保存时间到期前，您可以从回收站恢复已删除的文件。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-the-trash-bin-feature-of-oss-hdfs">使用回收站</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>导出清单</p></td><td rowspan="1" colspan="1"><p>使用清单导出功能，您可以将某个Bucket下的OSS-HDFS服务的文件清单导出到某个特定路径，格式为JSON文件，方便您对元数据进行统计分析。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/export-object-metadata-from-oss-hdfs-buckets">导出元数据清单</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>导出审计日志</p></td><td rowspan="1" colspan="1"><p>OSS-HDFS服务端记录了客户端请求的查询、修改、删除文件元数据的操作审计日志。 您可以通过审计日志，了解OSS-HDFS服务操作审计、访问统计以及异常请求等情况。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/oss-hdfs-service-audit-logs">导出审计日志</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>冷热分层存储</p></td><td rowspan="1" colspan="1"><p>并不是所有OSS-HDFS中存储的数据都需要频繁访问，但基于数据合规或者存档等原因，部分数据仍然需要继续保存。针对以上问题，OSS-HDFS服务支持数据的冷热分层存储，对于经常需要访问的数据以标准类型进行存储，对于较少访问的数据以低频、归档以及冷归档类型进行存储，从而降低总存储成本。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/enable-the-automatic-storage-tiering-feature-for-the-oss-hdfs-service">使用冷热分层存储</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>元数据转换</p></td><td rowspan="1" colspan="1"><p>OSS-HDFS服务支持在未部署任何导入和导出工具的情况下，直接将OSS元数据转换为OSS-HDFS元数据。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/metadata-conversion-of-oss-hdfs">转换元数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>RootPolicy</p></td><td rowspan="1" colspan="1"><p>您可以通过RootPolicy为OSS-HDFS服务设置自定义前缀，在无需修改原有访问 <code>hdfs://</code> 前缀作业的基础上，将作业直接运行在OSS-HDFS服务上。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/access-oss-hdfs-by-using-rootpolicy">通过RootPolicy访问</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>ProxyUser</p></td><td rowspan="1" colspan="1"><p>ProxyUser命令用于授权一个用户代表其他用户进行文件系统操作。例如，某些敏感数据只允许授权的特定用户代表其他用户进行访问和操作。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/proxyuser">ProxyUser（配置代理用户）</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>UserGroupsMapping</p></td><td rowspan="1" colspan="1"><p>UserGroupsMapping用于配置用户和用户组之间的映射关系。</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/usergroupsmapping">UserGroupsMapping（管理用户和用户组映射）</a></p></td></tr></tbody></table>

## 应用场景

OSS-HDFS服务提供全面的大数据和AI生态支持，其主要应用场景如下：

Hive、Spark离线数仓

OLAP

HBase存储与计算分离

实时计算

数据迁移

OSS-HDFS服务提供append、truncate、flush、sync、pwrite等基础文件操作。通过JindoFuse充分支持POSIX，可以在ClickHouse这类OLAP场景中替换本地磁盘来实现存储与计算分离方案。同时，得益于缓存系统进行加速，达到较优性价比。

## 引擎支持列表

<table><tbody><tr><td rowspan="1" colspan="1"><p>生态类型</p></td><td rowspan="1" colspan="1"><p>引擎/平台</p></td><td rowspan="1" colspan="1"><p>参考文档</p></td></tr><tr><td rowspan="8" colspan="1"><p>开源生态</p></td><td rowspan="1" colspan="1"><p>Flink</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-jindosdk-with-apache-flink-to-process-data-stored-in-oss-hdfs#task-2204153">开源Flink使用JindoSDK处理OSS-HDFS服务的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Flume</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-jindosdk-with-apache-flume-to-write-data-to-oss-hdfs#task-2269428">Flume使用JindoSDK写入OSS-HDFS服务</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Hadoop</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-self-managed-hadoop-to-access-oss-hdfs-by-using-jindosdk">Hadoop使用JindoSDK访问OSS-HDFS服务</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>HBase</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-oss-hdfs-as-the-underlying-storage-of-hbase#task-2203090">HBase使用OSS-HDFS服务作为底层存储</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Hive</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-jindosdk-with-hive-to-process-data-stored-in-oss-hdfs#task-2203104">Hive使用JindoSDK处理OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Impala</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-jindosdk-with-impala-to-query-data-stored-in-oss-hdfs#task-2203324">Impala使用JindoSDK查询OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Presto</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-jindosdk-with-trino-to-query-data-stored-in-oss-hdfs#task-2203371">Trino使用JindoSDK查询OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Spark</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-jindosdk-with-spark-to-query-data-stored-in-oss-hdfs#task-2203395">Spark使用JindoSDK查询OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="9" colspan="1"><p>阿里云生态</p></td><td rowspan="1" colspan="1"><p>EMR</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-oss-hdfs-in-emr-hive-or-spark#task-2213487">在EMR Hive或Spark中访问OSS-HDFS</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Flink</p></td><td rowspan="1" colspan="1"><ul><li><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-apache-flink-on-an-emr-cluster-to-write-data-to-oss-hdfs-in-a-resumable-manner#task-2249032">EMR Flink可恢复性写入OSS-HDFS服务</a></p></li><li><p><a href="https://help.aliyun.com/zh/oss/user-guide/alibaba-cloud-realtime-compute-reads-and-writes-data-from-oss-or-oss-hdfs">实时计算Flink读写OSS或者OSS-HDFS</a></p></li></ul></td></tr><tr><td rowspan="1" colspan="1"><p>Flume</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-flume-to-synchronize-data-from-an-emr-kafka-cluster-to-oss#task-2269744">使用Flume同步EMR Kafka集群的数据至OSS-HDFS服务</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>HBase</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-oss-hdfs-as-the-underlying-storage-of-hbase-on-an-emr-cluster#task-2249382">HBase以EMR集群的方式使用OSS-HDFS服务作为底层存储</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Hive</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-hive-on-an-emr-cluster-to-process-data-stored-in-oss-hdfs#task-2249677">Hive以EMR集群的方式处理OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Impala</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-impala-on-an-emr-cluster-to-query-data-stored-in-oss-hdfs#task-2249684">Impala以EMR集群的方式查询OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Presto</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-trino-on-an-emr-cluster-to-query-data-stored-in-oss-hdfs#task-2249784">Trino以EMR集群的方式查询OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Spark</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-spark-on-an-emr-cluster-to-process-data-stored-in-oss-hdfs#task-2249747">Spark以EMR集群的方式处理OSS-HDFS服务中的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>Sqoop</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/use-apache-sqoop-on-an-emr-cluster-to-implement-read-and-write-access-to-data-stored-in-oss-hdfs#task-2249838">Sqoop以EMR集群的方式读写OSS-HDFS服务的数据</a></p></td></tr><tr><td rowspan="1" colspan="1"><p>第三方生态</p></td><td rowspan="1" colspan="1"><p>SeaTunnel</p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/oss/user-guide/write-data-to-oss-hdfs-by-using-apache-seatunnel">通过SeaTunnel集成平台将数据写入OSS-HDFS服务</a></p></td></tr></tbody></table>

## 更多参考

您可以通过云起实验室，快速体验存算分离架构下的EMR集群结合OSS-HDFS服务进行数据湖分析。更多信息，请参见 [使用EMR+DLF+OSS-HDFS进行数据湖分析](https://developer.aliyun.com/article/1328987?spm=5176.28426678.J_HeJR_wZokYt378dwP-lLl.139.50c05181AZSOyp&scm=20140722.S_community@@%E6%96%87%E7%AB%A0@@1328987._.ID_community@@%E6%96%87%E7%AB%A0@@1328987-RL_%E4%BD%BF%E7%94%A8EMRDLFOSS~DAS~HDFS%E8%BF%9B%E8%A1%8C%E6%95%B0%E6%8D%AE%E6%B9%96%E5%88%86%E6%9E%90-LOC_llm-OR_ser-V_3-RE_new2-P0_1) 。