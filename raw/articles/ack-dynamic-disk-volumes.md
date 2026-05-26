---
title: 通过动态存储卷使用云盘进行持久化存储
source: https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-dynamically-provisioned-disk-volumes?spm=a2c4g.11186623.help-menu-85222.d_2_4_3_1.3bca47afACSfpF
author:
published:
created: 2026-05-26
description: 容器服务 Kubernetes 版（Container Service for Kubernetes，简称容器服务 ACK）提供高性能可伸缩的容器应用管理服务，支持企业级Kubernetes容器化应用的生命周期管理。
tags:
  - clippings
---
基于动态存储卷机制，可为每个应用副本自动创建并挂载一个独立的云盘，适用于数据库、中间件等等对 I/O 和延迟要求较高的场景，同时能够简化存储的生命周期管理。

## 工作原理

在StatefulSet中使用云盘动态存储卷的流程如下：

1. 定义模板  
	新建或使用默认 StorageClass，作为动态创建云盘的模板，规定其类型、性能、回收策略等关键参数。
2. 在应用中声明存储需求
	在StatefulSet中定义 `volumeClaimTemplates` ，并引用 StorageClass，声明Pod待使用的PVC的规格，如存储容量、访问模式等。
3. 自动化创建并挂载存储卷  
	StatefulSet 创建 Pod 时，系统会基于模板自动为其生成一个唯一的 PVC。CSI组件会根据 StorageClass 的规则创建 PV 并与 PVC 绑定，最终将该云盘挂载到 Pod 中。

## 适用范围

- 可用区限制：除ESSD同城冗余云盘外，其他云盘类型无法跨可用区挂载，只能挂载到同一可用区下的Pod。
- 实例规格族限制：部分云盘类型仅支持挂载到特定的 [实例规格族](https://help.aliyun.com/zh/ecs/user-guide/overview-of-instance-families#concept-sx4-lxv-tdb) 。
- CSI组件限制：已安装csi-plugin组件和csi-provisioner组件。
	> CSI组件默认安装，请确保未手动卸载。可在 **组件管理** 页面查看安装情况。建议 [升级CSI组件](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/install-and-upgrade-the-csi-plug-in#section-csv-gvs-vdb) 至最新版本。
- 虚拟节点限制：如需在虚拟节点上使用云盘，需遵循集群和kube-scheduler版本要求。
	**展开查看版本要求**
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>集群版本</b></p></td><td rowspan="1" colspan="1"><p><b>kube-scheduler版本</b></p></td></tr><tr><td rowspan="1" colspan="1"><p>1.28及以上</p></td><td rowspan="1" colspan="1"><p>6.9.3及以上</p></td></tr><tr><td rowspan="1" colspan="1"><p>1.26</p></td><td rowspan="1" colspan="1"><p>6.8.7</p></td></tr><tr><td rowspan="1" colspan="1"><p>1.24</p></td><td rowspan="1" colspan="1"><p>6.4.7</p></td></tr><tr><td rowspan="1" colspan="1"><p>1.22</p></td><td rowspan="1" colspan="1"><p>6.4.5</p></td></tr></tbody></table>
- 灵骏节点限制：如需在灵骏节点上使用云盘，需满足以下要求。
	**展开查看**
	- CSI 组件：不低于 v1.34.3。
	- [为RAM角色授权](https://help.aliyun.com/zh/ram/user-guide/grant-permissions-to-a-ram-role) ：需为AliyunCCCSIPluginRole手动添加 `eflo:DescribeNode` 和 `eflo:DescribeNodeType` 权限。
	- 云盘标签：
		1. 访问 [ECS控制台-块存储-云盘](https://ecs.console.aliyun.com/disk/) 。
			2. 在创建云盘过程中（仅支持在创建时添加），为云盘添加 `createdByProduct:eflo` 标签。
			示例如下：
			![image](https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/1701668771/p1055258.png)
			> 如挂载时报错 `OperationDenied.HpnZoneMismatch` ，请参见 [灵骏节点中挂载云盘时，Pod Event 报错 OperationDenied.HpnZoneMismatch怎么办？](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-disk-volumes#b6742b336170v) 。
		创建后，使用该云盘来手动创建PV并通过PVC来绑定。该云盘可以且仅可以被调度到灵骏节点。

## 步骤一：选择StorageClass

为便于使用，ACK提供多种默认StorageClass。由于StorageClass创建后无法修改，若默认配置不满足需求，可通过新建。

使用默认StorageClass

手动创建StorageClass

可从以下默认StorageClass中选择一个，在应用的 `storageClassName` 字段中引用其名称即可。

<table><tbody><tr><td rowspan="1" colspan="1"><p><b>StorageClass名称</b></p></td><td rowspan="1" colspan="1"><p><b>动态创建的云盘类型</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><code>alicloud-disk-topology-alltype</code> （推荐）</p></td><td rowspan="1" colspan="1"><p>默认先调度Pod再创建云盘，避免因可用区不匹配导致挂载失败（ <code>volumeBindingMode: WaitForFirstConsumer</code> ）。Pod调度到的节点可用区和实例规格，会结合云盘库存情况，按ESSD、SSD、高效云盘的顺序尝试创建。默认优先创建ESSD PL1，容量大小最低为20 GiB。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>alicloud-disk-essd</code></p></td><td rowspan="1" colspan="1"><p>ESSD云盘，默认为PL1性能级别，云盘容量大小最低为20 GiB。</p><p><strong>重要</strong></p><p><a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-cloud-box-resources-in-ack-dedicated-clusters">云盒</a> 内的ESSD云盘仅支持PL0级别，需并指定 <code>performanceLevel</code> 为 <code>PL0</code> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>alicloud-disk-ssd</code></p></td><td rowspan="1" colspan="1"><p>SSD云盘，云盘容量大小最低为20 GiB。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>alicloud-disk-efficiency</code></p></td><td rowspan="1" colspan="1"><p>高效云盘，云盘容量大小最低为20 GiB。</p></td></tr></tbody></table>

> 可通过 `kubectl describe sc <storageclass-name>` 查看StorageClass详细配置。

kubectl

控制台

1. 创建 `disk-sc.yaml` 。
	示例以使用 `volumeBindingMode: WaitForFirstConsumer` 延迟绑定PV的StorageClass为例。
	```yaml
	apiVersion: storage.k8s.io/v1
	kind: StorageClass
	metadata:
	  # StorageClass名称
	  name: alicloud-disk-wait-for-first-consumer
	# 驱动类型，使用阿里云云盘CSI插件时固定为此值。
	provisioner: diskplugin.csi.alibabacloud.com
	parameters:
	  # 云盘类型，按优先级自适应选择
	  type: cloud_auto,cloud_essd,cloud_ssd  
	  # 文件系统类型
	  fstype: ext4
	  diskTags: "a:b,b:c"
	  encrypted: "false"
	  # ESSD云盘的性能级别
	  performanceLevel: PL1 
	  provisionedIops: "40000"
	  burstingEnabled: "false"
	# 绑定模式，多可用区场景下建议使用WaitForFirstConsumer
	volumeBindingMode: WaitForFirstConsumer
	# 回收策略
	reclaimPolicy: Retain
	# 是否允许存储卷扩容
	allowVolumeExpansion: true
	# 拓扑限制：限制云盘只能在指定的可用区创建
	allowedTopologies:
	- matchLabelExpressions:
	  - key: topology.diskplugin.csi.alibabacloud.com/zone
	    values:
	    # 替换为实际可用区
	    - cn-hangzhou-i
	    - cn-hangzhou-k
	```
	主要参数说明如下：
	<table><tbody><tr><td rowspan="1" colspan="2"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>说明</b></p></td></tr><tr><td rowspan="1" colspan="2"><p><code>provisioner</code></p></td><td rowspan="1" colspan="1"><p>驱动类型，必填参数。使用阿里云云盘CSI插件时固定为 <code>diskplugin.csi.alibabacloud.com</code> 。</p></td></tr><tr><td rowspan="12" colspan="1"><p><code>parameters</code></p></td><td rowspan="1" colspan="1"><p><code>type</code></p></td><td rowspan="1" colspan="1"><section><p>云盘类型，必填参数。可取值：</p><ul><li><p><code>cloud_essd</code> （默认值）： <a href="https://help.aliyun.com/zh/ecs/user-guide/essds#concept-727754">ESSD云盘</a></p></li><li><p><code>cloud_auto</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/essd-autopl-disks#concept-2156400">ESSD AutoPL云盘</a></p></li><li><p><code>cloud_essd_entry</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#83c1244d7b887">块存储概述</a></p></li><li><p><code>cloud_ssd</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#b3ce671b406uk">SSD云盘</a></p></li><li><p><code>cloud_efficiency</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#b3ce671b406uk">高效云盘</a></p></li><li><p><code>elastic_ephemeral_disk_standard</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-ephemeral-disks#c4dabe8b4epev">标准版弹性临时盘</a></p></li><li><p><code>elastic_ephemeral_disk_premium</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-ephemeral-disks#c4dabe8b4epev">高级版弹性临时盘</a></p></li><li><p><code>cloud_regional_disk_auto</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/regional-essd-disks/">ESSD同城冗余云盘</a></p></li></ul><p>支持任意组合，例如 <code>type: cloud_ssd,cloud_essd,cloud_auto</code> 。系统将按配置顺序依次尝试创建。最终创建的云盘类型受节点实例、所在可用区云盘支持情况等因素影响。</p></section></td></tr><tr><td rowspan="1" colspan="1"><p><code>resourceGroupId</code></p></td><td rowspan="1" colspan="1"><p>云盘所属资源组。默认为 <code>""</code> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>regionId</code></p></td><td rowspan="1" colspan="1"><p>云盘所在地域，与集群地域相同。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>fstype</code></p></td><td rowspan="1" colspan="1"><p>云盘使用的文件系统。可取值： <code>ext4</code> （默认）、 <code>xfs</code> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>mkfsOptions</code></p></td><td rowspan="1" colspan="1"><p>云盘格式化参数，如 <code>mkfsOptions: "-O project,quota"</code> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>diskTags</code></p></td><td rowspan="1" colspan="1"><p>云盘标签。例如 <code>diskTags: "a:b,b:c"</code> ，也可使用 <code>diskTags/a: b</code> 的格式指定。CSI组件需为v1.30.3及以上版本。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>encrypted</code></p></td><td rowspan="1" colspan="1"><p>云盘是否加密。默认为 <code>false</code> ，不加密。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>performanceLevel</code></p></td><td rowspan="1" colspan="1"><p><a href="https://help.aliyun.com/zh/ecs/user-guide/essds#d86567bd2dgzu">ESSD云盘性能级别</a> ，取值 <code>PL0</code> 、 <code>PL1</code> （默认）、 <code>PL2</code> 或 <code>PL3</code> 。</p><blockquote>通过云盒使用时需设置为 <code>PL0</code> 。</blockquote></td></tr><tr><td rowspan="1" colspan="1"><p><code>volumeExpandAutoSnapshot</code> 【废弃】</p></td><td rowspan="1" colspan="1"><p>自CSI 1.31.4版本起已废弃。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>provisionedIops</code></p></td><td rowspan="1" colspan="1"><p>使用ESSD AutoPL云盘时，配置云盘的 <a href="https://help.aliyun.com/zh/ecs/user-guide/essd-autopl-disks#section-way-q9k-oar">预配置性能（IOPS）</a> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>burstingEnabled</code></p></td><td rowspan="1" colspan="1"><p>使用ESSD AutoPL云盘时，是否开启 <a href="https://help.aliyun.com/zh/ecs/user-guide/essd-autopl-disks#section-way-q9k-oar">Burst（性能突发）</a> 。默认为 <code>false</code> ，不开启。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>multiAttach</code></p></td><td rowspan="1" colspan="1"><p>是否开启 <a href="https://help.aliyun.com/zh/ecs/user-guide/enable-multi-attach">云盘多重挂载功能</a> 。默认为 <code>false</code> ，不开启。</p></td></tr><tr><td rowspan="1" colspan="2"><p><code>volumeBindingMode</code></p></td><td rowspan="1" colspan="1"><section><p>云盘的绑定模式。可取值：</p><ul><li><p><code>Immediate</code> （默认）：先创建云盘再创建Pod。</p></li><li><p><code>WaitForFirstConsumer</code> ：延迟绑定，即先调度Pod，再根据Pod所在可用区创建云盘。</p><p>多可用区场景下，建议使用 <code>WaitForFirstConsumer</code> ，以优化因云盘和ECS节点不在同一可用区导致的挂载失败。</p><blockquote>如需调度到虚拟节点，采用特定调度方式或添加了特定Annotation时，不支持使用 <code>WaitForFirstConsumer</code> 类型的StorageClass，请参见。</blockquote></li></ul></section></td></tr><tr><td rowspan="1" colspan="2"><p><code>reclaimPolicy</code></p></td><td rowspan="1" colspan="1"><section><p>云盘回收策略。</p><ul><li><p><code>Delete</code> （默认）：删除PVC时，PV和云盘会一起删除。</p></li><li><p><code>Retain</code> ：删除PVC时，PV和云盘数据不会被删除，需手动删除。</p><p>对数据安全性要求高时，推荐使用 <code>Retain</code> ，以免误删数据。</p></li></ul></section></td></tr><tr><td rowspan="1" colspan="2"><p><code>allowVolumeExpansion</code></p></td><td rowspan="1" colspan="1"><p>配置为 <code>true</code> 时，允许 <a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/expand-a-disk-volume-without-service-interruptions">在线扩容云盘存储卷</a> 。</p></td></tr><tr><td rowspan="1" colspan="2"><p><code>allowedTopologies</code></p></td><td rowspan="1" colspan="1"><section><p>限制云盘只能在特定的拓扑域中创建。</p><ul><li><p><code>key</code> ：拓扑域标签。支持以下取值：</p><ul><li><p><code>topology.diskplugin.csi.alibabacloud.com/zone</code> ：阿里云 CSI 插件提供的专用拓扑 <code>key</code> 。</p></li><li><p><code>alibabacloud.com/ecs-instance-id</code> ：使用弹性临时盘时，支持指定节点。</p></li></ul></li><li><p><code>values</code> ：包含可用区或节点 ID 的列表。</p></li></ul></section></td></tr></tbody></table>
2. 创建StorageClass。
	```bash
	kubectl create -f disk-sc.yaml
	```
3. 查看StorageClass。
	```bash
	kubectl get sc
	```
	输出中，StorageClass已创建，处于 `WaitForFirstConsumer` 绑定模式。
	```bash
	NAME                                    PROVISIONER                       RECLAIMPOLICY   VOLUMEBINDINGMODE      ALLOWVOLUMEEXPANSION   AGE
	alicloud-disk-wait-for-first-consumer   diskplugin.csi.alibabacloud.com   Retain          WaitForFirstConsumer   true                   10s
	```

1. 在 [ACK集群列表](https://cs.console.aliyun.com/) 页面，单击目标集群名称，在集群详情页左侧导航栏，选择 **存储** > **存储类** 。
2. 单击 **创建** ，选择存储卷类型为 **云盘** ，完成参数配置，然后单击 **创建** 。
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><ul><li><p>默认参数： <code>type</code> 。</p><section><p>云盘类型，必填参数。可取值：</p><ul><li><p><code>cloud_essd</code> （默认值）： <a href="https://help.aliyun.com/zh/ecs/user-guide/essds#concept-727754">ESSD云盘</a></p></li><li><p><code>cloud_auto</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/essd-autopl-disks#concept-2156400">ESSD AutoPL云盘</a></p></li><li><p><code>cloud_essd_entry</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#83c1244d7b887">块存储概述</a></p></li><li><p><code>cloud_ssd</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#b3ce671b406uk">SSD云盘</a></p></li><li><p><code>cloud_efficiency</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#b3ce671b406uk">高效云盘</a></p></li><li><p><code>elastic_ephemeral_disk_standard</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-ephemeral-disks#c4dabe8b4epev">标准版弹性临时盘</a></p></li><li><p><code>elastic_ephemeral_disk_premium</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/elastic-ephemeral-disks#c4dabe8b4epev">高级版弹性临时盘</a></p></li><li><p><code>cloud_regional_disk_auto</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/regional-essd-disks/">ESSD同城冗余云盘</a></p></li></ul><p>支持任意组合，例如 <code>type: cloud_ssd,cloud_essd,cloud_auto</code> 。系统将按配置顺序依次尝试创建。最终创建的云盘类型受节点实例、所在可用区云盘支持情况等因素影响。</p></section></li><li><p></p><p><b>展开查看可选参数</b></p><p></p><div><ul><li><p><code>resourceGroupId</code> ：云盘所属资源组。默认为 <code>""</code> 。</p></li><li><p><code>regionId</code> ：云盘所在地域，与集群地域相同。</p></li><li><p><code>fstype</code> ：云盘使用的文件系统。可取值： <code>ext4</code> （默认）、 <code>xfs</code> 。</p></li><li><p><code>mkfsOptions</code> ：云盘格式化参数，如 <code>mkfsOptions: "-O project,quota"</code> 。</p></li><li><p><code>diskTags</code> ：云盘标签。例如 <code>diskTags: "a:b,b:c"</code> ，也可使用 <code>diskTags/a: b</code> 的格式指定。CSI组件需为v1.30.3及以上版本。</p></li><li><p><code>encrypted</code> ：云盘是否加密。默认为 <code>false</code> ，不加密。</p></li><li><p><code>performanceLevel</code> ： <a href="https://help.aliyun.com/zh/ecs/user-guide/essds#d86567bd2dgzu">ESSD云盘性能级别</a> ，取值 <code>PL0</code> 、 <code>PL1</code> （默认）、 <code>PL2</code> 或 <code>PL3</code> 。</p><blockquote>通过云盒使用时需设置为 <code>PL0</code> 。</blockquote></li><li><p><code>provisionedIops</code> ：使用ESSD AutoPL云盘时，配置云盘的 <a href="https://help.aliyun.com/zh/ecs/user-guide/essd-autopl-disks#section-way-q9k-oar">预配置性能（IOPS）</a> 。</p></li><li><p><code>burstingEnabled</code> ：使用ESSD AutoPL云盘时，是否开启 <a href="https://help.aliyun.com/zh/ecs/user-guide/essd-autopl-disks#section-way-q9k-oar">Burst（性能突发）</a> 。默认为 <code>false</code> ，不开启。</p></li><li><p><code>multiAttach</code> ：是否开启 <a href="https://help.aliyun.com/zh/ecs/user-guide/enable-multi-attach">云盘多重挂载功能</a> 。默认为 <code>false</code> ，不开启。</p></li></ul></div></li></ul></td></tr><tr><td rowspan="1" colspan="1"><p><b>回收策略</b></p></td><td rowspan="1" colspan="1"><section><p>云盘回收策略。</p><ul><li><p><code>Delete</code> （默认）：删除PVC时，PV和云盘会一起删除。</p></li><li><p><code>Retain</code> ：删除PVC时，PV和云盘数据不会被删除，需手动删除。</p><p>对数据安全性要求高时，推荐使用 <code>Retain</code> ，以免误删数据。</p></li></ul></section></td></tr><tr><td rowspan="1" colspan="1"><p><b>绑定模式</b></p></td><td rowspan="1" colspan="1"><section><p>云盘的绑定模式。可取值：</p><ul><li><p><code>Immediate</code> （默认）：先创建云盘再创建Pod。</p></li><li><p><code>WaitForFirstConsumer</code> ：延迟绑定，即先调度Pod，再根据Pod所在可用区创建云盘。</p><p>多可用区场景下，建议使用 <code>WaitForFirstConsumer</code> ，以优化因云盘和ECS节点不在同一可用区导致的挂载失败。</p><blockquote>如需调度到虚拟节点，采用特定调度方式或添加了特定Annotation时，不支持使用 <code>WaitForFirstConsumer</code> 类型的StorageClass，请参见。</blockquote></li></ul></section></td></tr></tbody></table>
	创建完成后，可在 **存储类** 页面查看新创建的StorageClass。

## 步骤二：创建应用并挂载云盘

以StatefulSet为例介绍如何挂载云盘存储卷。

**重要**

云盘为非共享存储，未开启多重挂载时一次只能挂载一个Pod。在多副本 Deployment 中共享PVC会导致新Pod无法挂载仍被旧Pod占用的云盘而启动失败。推荐使用StatefulSet或单独为Pod挂载云盘。

如仍需在Deployment中使用云盘，建议 [使用云盘作为临时存储卷](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/best-practices-for-using-deployment-for-temporary-storage) 。如需启用多重挂载，请参见 [使用NVMe云盘多重挂载及Reservation](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/multi-attach-and-reservation-of-nvme-cloud-disks) 。

1. 创建 `statefulset.yaml` 。
	> 以下示例创建了包含2个Pod的StatefulSet，使用 `volumeClaimTemplates` 来为每个 Pod 自动创建并绑定独立的持久化存储。
	```yaml
	apiVersion: apps/v1
	kind: StatefulSet
	metadata:
	  name: web
	spec:
	  serviceName: "nginx"
	  replicas: 2
	  selector:
	    matchLabels:
	      app: nginx
	  template:
	    metadata:
	      labels:
	        app: nginx
	    spec:
	      # 建议配置以下securityContext以优化挂载性能
	      securityContext:
	        fsGroup: 1000
	        fsGroupChangePolicy: "OnRootMismatch"
	      containers:
	      - name: nginx
	        image: anolis-registry.cn-zhangjiakou.cr.aliyuncs.com/openanolis/nginx:1.14.1-8.6
	        ports:
	        - containerPort: 80
	        volumeMounts:
	        # 将数据卷挂载到容器的/data目录
	        # name需与volumeClaimTemplates中定义的metadata.name一致
	        - name: pvc-disk
	          mountPath: /data
	  # 定义PVC模板
	  volumeClaimTemplates:
	  - metadata:
	      name: pvc-disk
	    spec:
	      # 访问模式
	      accessModes: [ "ReadWriteOnce" ]
	      # 关联此前创建的StorageClass
	      storageClassName: "alicloud-disk-wait-for-first-consumer"
	      resources:
	        requests:
	          # 申请的存储容量，即云盘大小
	          storage: 20Gi
	```
	**重要**
	在 Pod 中配置 `securityContext.fsgroup` 会导致kubelet在挂载卷时递归修改文件权限（ `chmod` / `chown` ）。若文件数量庞大，将显著延长挂载时间。
	对于1.20及以上版本的集群，建议将 `fsGroupChangePolicy` 配置为 `OnRootMismatch` ，仅在首次挂载且卷根目录权限不匹配时才执行递归的权限变更，以优化挂载性能。若性能仍不满足要求或需更精细的权限控制，建议使用 `initContainer` 在主应用容器启动前自行执行权限调整命令。
2. 创建StatefulSet。
	```bash
	kubectl create -f statefulset.yaml
	```
3. 确认Pod处于Running状态。
	```bash
	kubectl get pod -l app=nginx
	```
4. 查看挂载路径，确认已挂载云盘。
	> 本示例Pod名称为 `web-1` ，请按实际替换。
	```bash
	kubectl exec web-1 -- df -h /data
	```
	预期输出：
	```bash
	Filesystem      Size  Used Avail Use% Mounted on
	/dev/vdb         20G   24K   20G   1% /data
	```

## 步骤三：验证持久化存储

通过“写入数据 -> 删除 Pod -> 检查数据”的流程，来验证存储在云盘上的数据在 Pod 重建后是否仍然存在。

1. 在 Pod 中写入测试数据。
	以Pod `web-1` 为例，在其挂载的云盘路径 `/data` 下创建一个test文件。
	```bash
	kubectl exec web-1 -- touch /data/test
	kubectl exec web-1 -- ls /data
	```
	预期输出：
	```bash
	lost+found
	test
	```
2. 模拟 Pod 故障，删除 Pod。
	```bash
	kubectl delete pod web-1
	```
	再次执行 `kubectl get pod -l app=nginx` ，可以发现已自动创建一个同名的Pod `web-1` 。
3. 验证新 Pod 中的数据。
	在新Pod `web-1` 中再次检查 `/data` 目录。
	```bash
	kubectl exec web-1 -- ls /data
	```
	预期输出中，此前创建的 test 文件依然存在，表明即使 Pod 被删除重建，数据也实现了持久化存储。
	```bash
	lost+found
	test
	```

## 应用于生产环境

- 高可用性
	- 云盘选型
		需综合评估其 [性能](https://help.aliyun.com/zh/ecs/user-guide/block-storage-performance) 、 [计费](https://www.aliyun.com/price/product#/disk/detail) 以及节点的可用区和 [实例规格族](https://help.aliyun.com/zh/ecs/user-guide/overview-of-instance-families#concept-sx4-lxv-tdb) ，确保Pod能被调度至兼容的节点。
		选择 [云盘类型](https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#87438f9ee2d81) 时，SSD云盘、高效云盘已逐步停止售卖。建议选用ESSD PL0云盘或ESSD Entry云盘替换高效云盘，选用ESSD AutoPL云盘替换SSD云盘。
		- 构建跨可用区容灾方案
		- 应用层容灾： 对于数据库等关键业务，在多个可用区部署应用实例，并通过应用自身的数据同步机制实现高可用。
				- 存储层容灾：选用支持多可用区容灾的云盘类型，将数据实时同步写入同一地域的不同可用区，实现跨可用区的故障恢复，请参见 [使用ESSD同城冗余云盘](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-regional-essd-disks) 。
- 数据安全与备份
	- 防止意外删除数据：
		为防止数据丢失，建议将StorageClass的 `reclaimPolicy` 设置为 `Retain` ，PVC删除后，后端的云盘不会被删除，便于数据恢复。
		- 常态化备份
		动态卷简化了资源供给，但不能替代数据备份。对于核心业务，使用 [备份中心](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/backup-center-overview/) 进行数据的备份和恢复。
		- 启用静态加密：对于数据敏感型应用，在StorageClass中配置 `encrypted: "true"` 来 [加密云盘](https://help.aliyun.com/zh/ecs/user-guide/encryption-overview) 。
- 性能与成本优化
	- 启用并行挂载
		默认情况下，单个节点的云盘操作是串行的。可 [使用云盘并行挂载](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/attach-cloud-disks-in-parallel) ，加速Pod启动。
		- 启用存储卷在线扩容
		在StorageClass中设置 `allowVolumeExpansion: true` ，以便在未来存储需求增长时， [在线扩容云盘存储卷](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/expand-a-disk-volume-without-service-interruptions) 。
		- 配置存储监控与告警
		基于 [容器存储监控](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-csi-plugin-to-monitor-storage-resources-at-the-node-side) 配置告警，及时发现存储卷异常或性能瓶颈。

## 计费说明

通过StorageClass动态创建的云盘采用按量付费，请参见 [块存储计费](https://help.aliyun.com/zh/ecs/block-storage-devices) 、 [块存储价格](https://www.aliyun.com/price/product#/disk/detail) 。

## 资源释放指引

为避免产生预期外费用并确保数据安全，请遵循以下流程释放无需使用的资源。

1. 删除工作负载
	- 操作：删除所有使用相关PVC的应用，例如Deployment、StatefulSet等。此操作将停止运行的Pod并卸载存储卷。
		命令示例： `kubectl delete deployment <your-deployment-name>`
2. 删除PVC
	- 操作：删除应用关联的PVC。关联资源（PV和云盘）的释放取决于StorageClass的 `reclaimPolicy` 。
		- `Delete` ：删除PVC后，其绑定的PV以及后端的云盘会被自动删除。此操作不可逆，请谨慎操作。
			> 为防止数据意外丢失，可在执行删除前为云盘 [创建自动快照策略](https://help.aliyun.com/zh/ecs/user-guide/create-an-automatic-snapshot-policy-1) 进行备份。
				- `Retain` ：删除PVC后，其绑定的PV状态会变为 `Released` ，但PV对象和后端的云盘会被完整保留。如确认云盘及其上的所有数据无需使用，请参见 [释放云盘](https://help.aliyun.com/zh/ecs/user-guide/release-a-disk) 删除。此操作不可逆，请务必谨慎操作。
		命令示例： `kubectl delete pvc <your-pvc-name>`
3. 删除Kubernetes存储资源定义：此操作仅移除集群内的资源定义，不会删除后端的云盘实体。
	- 删除PV
		- 操作：手动删除处于 `Released` 状态的PV，可手动删除其定义。
				- 命令示例： `kubectl delete pv <your-pv-name>`
		- 删除StorageClass
		- 操作：如果不再需要该类型的存储，可以删除对应的StorageClass。
				- 命令示例： `kubectl delete sc <your-storageclass-name>`

## 常见问题

#### 挂载云盘的Pod调度至虚拟节点时，PVC一直处于Pending状态怎么办？

可能是使用了不支持虚拟节点调度场景的StorageClass。当通过特定标签（Label）或注解（Annotation）将Pod调度到虚拟节点时，不支持使用 `volumeBindingMode: WaitForFirstConsumer` 模式的StorageClass。

- 原因：  
	`WaitForFirstConsumer` 模式依赖kube-scheduler为Pod选择一个物理节点，从而确定其可用区，然后再根据可用区创建云盘。但虚拟节点的部分调度机制不遵循此流程，导致CSI无法获取可用区信息，继而无法创建PV，PVC便处于Pending状态。
- 如遇问题，请检查Pod或其命名空间中是否包含以下任意一种配置：
	- Label：
		- `alibabacloud.com/eci: "true"` ：调度至ECI Pod。
				- `alibabacloud.com/acs: "true"` ：调度至ACS Pod。
		- 指定节点：
		- 通过 `spec.nodeName` 直接指定一个节点（节点名称前缀为 `virtual-kubelet` ）。
		- Annotation：
		- `k8s.aliyun.com/eci-vswitch` ：指定ECI Pod的交换机。
				- `k8s.aliyun.com/eci-fail-strategy: "fail-fast"` ：ECI Pod的故障处理策略为快速失败。

#### 如何为单个Pod或单副本Deployment挂载云盘存储卷？

对于不需要多副本伸缩和稳定网络标识的简单应用，可手动创建PVC并将其挂载到Pod或Deployment，以实现持久化存储。

链路为：选择StorageClass -> 创建PVC -> 在应用中挂载PVC。

1. 。
2. 创建PVC，申请存储资源。
	kubectl
	控制台
	1. 创建 `disk-pvc.yaml` 。
		```yaml
		apiVersion: v1
		kind: PersistentVolumeClaim
		metadata:
		  name: disk-pvc
		spec:
		  # 访问模式
		  accessModes:
		  - ReadWriteOnce
		  volumeMode: Filesystem
		  resources:
		    requests:
		      # 申请的存储容量，即云盘大小
		      storage: 20Gi
		  # 关联此前创建的StorageClass
		  storageClassName: alicloud-disk-topology-alltype
		```
		相关参数说明如下：
		<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>说明</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><code>accessModes</code></p></td><td rowspan="1" colspan="1"><section><p>存储卷的 <a href="https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/storage-basics#cfb6394d6e6tw">访问模式</a> 。可取值： <code>ReadWriteOnce</code> 、 <code>ReadOnlyMany</code> 或 <code>ReadWriteMany</code> 。具体取决于StorageClass中的 <code>multiAttach</code> 配置以及PVC中的 <code>volumeMode</code> 配置。</p><blockquote><code>multiAttach</code> 表示是否开启 <a href="https://help.aliyun.com/zh/ecs/user-guide/enable-multi-attach">云盘多重挂载</a> 。默认为 <code>false</code> ，不开启。</blockquote><ul><li><p><code>multiAttach</code> 为 <code>false</code> ， <code>volumeMode</code> 配置为任意值时，访问模式仅支持 <code>ReadWriteOnce</code> 。</p></li><li><p><code>multiAttach</code> 为 <code>true</code> ， <code>volumeMode</code> 为 <code>Filesystem</code> 时，访问模式仅支持 <code>ReadWriteOnce</code> 和 <code>ReadOnlyMany</code> 。</p></li><li><p><code>multiAttach</code> 为 <code>true</code> ， <code>volumeMode</code> 为 <code>Block</code> 时，三种访问模式均支持。</p></li></ul></section><p><strong>重要</strong></p><p>此场景下，访问模式通常为 <code>ReadWriteOnce</code> (RWO) ，即同一时间只能被一个Pod挂载。因此Deployment副本数不能大于1。如尝试扩容，新Pod会因无法挂载已被占用的云盘而一直处于 <code>Pending</code> 状态。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>volumeMode</code></p></td><td rowspan="1" colspan="1"><section><p>存储卷的模式。可取值：</p><ul><li><p><code>Filesystem</code> （默认）：存储卷会被格式化并挂载为目录。</p></li><li><p><code>Block</code> ：存储卷以未格式化的块设备形式直接提供给 Pod。</p></li></ul></section></td></tr><tr><td rowspan="1" colspan="1"><p><code>storage</code></p></td><td rowspan="1" colspan="1"><p>申请的存储容量大小。不同云盘类型的 <a href="https://help.aliyun.com/zh/ecs/user-guide/block-storage-performance#section-0hu-6dh-p6f">容量范围</a> 不同。请确保 <code>storage</code> 取值符合其引用的 StorageClass 所对应的云盘类型的容量限制，以免云盘创建失败。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>storageClassName</code></p></td><td rowspan="1" colspan="1"><p>待绑定的StorageClass。</p></td></tr></tbody></table>
	2. 创建PVC。
		```bash
		kubectl create -f disk-pvc.yaml
		```
	3. 查看PVC。
		```bash
		kubectl get pvc
		```
		输出中，由于StorageClass使用 `WaitForFirstConsumer` 模式，此时PVC处于 `Pending` 状态，直到第一个使用它的 Pod 被成功调度。
		```bash
		NAME       STATUS    VOLUME   CAPACITY   ACCESS MODES   STORAGECLASS                            VOLUMEATTRIBUTESCLASS   AGE
		disk-pvc   Pending                                      alicloud-disk-wait-for-first-consumer   <unset>                 14s
		```
	1. 在集群管理页左侧导航栏，选择 **存储** > **存储声明** 。
	2. 在 **存储声明** 页面，单击 **创建** ，选择 **存储声明类型** 为 **云盘** ，按照页面提示完成参数的配置。
		<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><b>分配模式</b></p></td><td rowspan="1" colspan="1"><p>选择 <b>使用存储类动态创建</b> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>已有存储类</b></p></td><td rowspan="1" colspan="1"><p>默认创建或手动创建的StorageClass。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>总量</b></p></td><td rowspan="1" colspan="1"><p>申请的存储容量大小。不同云盘类型的 <a href="https://help.aliyun.com/zh/ecs/user-guide/block-storage-performance#section-0hu-6dh-p6f">容量范围</a> 不同。请确保 <code>storage</code> 取值符合其引用的 StorageClass 所对应的云盘类型的容量限制，以免云盘创建失败。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>访问模式</b></p></td><td rowspan="1" colspan="1"><p>当前场景仅支持 <b>ReadWriteOnce</b> ，表示卷只能被一个Pod以读写方式挂载。</p></td></tr></tbody></table>
		创建完成后，可在 **存储声明** 页面查看新创建的PVC。
3. 在应用中挂载PVC。
	1. 创建 `disk-deployment.yaml` 。
		**展开查看示例YAML**
		```yaml
		apiVersion: apps/v1
		kind: Deployment
		metadata:
		  name: single-pod-app
		spec:
		  # 确保副本数为1
		  replicas: 1
		  selector:
		    matchLabels:
		      app: nginx-single
		  template:
		    metadata:
		      labels:
		        app: nginx-single
		    spec:
		      containers:
		      - name: nginx
		        image: anolis-registry.cn-zhangjiakou.cr.aliyuncs.com/openanolis/nginx:1.14.1-8.6
		        ports:
		        - containerPort: 80
		        # 在容器内定义挂载点
		        volumeMounts:
		        - name: my-persistent-storage  # 必须与下面volumes中定义的name一致
		          mountPath: /data  # 挂载到容器内的/data目录
		      # 在Pod级别声明并引用PVC
		      volumes:
		      - name: my-persistent-storage # 供容器引用的卷
		        persistentVolumeClaim:
		          claimName: disk-pvc # 引用此前创建的PVC
		```
		2. 部署Deployment。
		```bash
		kubectl create -f disk-deployment.yaml
		```
4. 验证挂载结果。
	1. 确认Pod已经成功运行。
		```bash
		kubectl get pods -l app=nginx-single
		```
		2. 进入Pod内部，检查 `/data` 目录是否已成功挂载云盘。
		```bash
		# 获取Pod名称
		POD_NAME=$(kubectl get pods -l app=nginx-single -o jsonpath='{.items[0].metadata.name}')
		# 执行df -h命令
		kubectl exec $POD_NAME -- df -h /data
		```
		输出如下，表明20GiB的云盘已成功挂载。
		```
		Filesystem      Size  Used Avail Use% Mounted on
		/dev/vdb         20G   24K   20G   1% /data
		```

## 相关文档

- 云盘多可用区部署的配置优化建议，请参见 [云盘存储卷的高可用配置建议](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/recommended-storage-settings-for-cross-zone-deployment) 。
- 可参见 [创建有状态工作负载StatefulSet](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-a-statefulset-to-create-a-stateful-application-1) 、 [创建无状态工作负载Deployment](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/create-a-stateless-application-by-using-a-deployment) 了解工作负载配置参数。
- 如果不再使用某块云盘且希望云盘停止计费时，可 [释放云盘](https://help.aliyun.com/zh/ecs/user-guide/release-a-disk) 。释放后，云盘及存储在云盘上的数据会被删除、云盘停止计费。
- 使用云盘存储卷时如遇问题，请参见 [云盘存储卷FAQ](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-disk-volumes) 。
- 如集群仍在使用废弃的Flexvolume组件，请 [迁移Flexvolume至CSI](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/upgrade-from-flexvolume-to-csi/) 。