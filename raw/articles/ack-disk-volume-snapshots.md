---
title: 为单个云盘存储卷创建快照
source: https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-volume-snapshots-created-from-disks?spm=a2c4g.11186623.0.i7
author:
published:
created: 2026-05-26
description: 容器服务 Kubernetes 版（Container Service for Kubernetes，简称容器服务 ACK）提供高性能可伸缩的容器应用管理服务，支持企业级Kubernetes容器化应用的生命周期管理。
tags:
  - clippings
---
云盘存储快照可以帮助您实现应用数据的备份和恢复。本文介绍如何通过VolumeSnapshot资源为云盘存储卷创建快照，以及如何基于快照恢复数据。

## 前提条件

- [已创建ACK托管集群](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/create-an-ack-managed-cluster-2/#task-skz-qwk-qfb) ，且集群版本为1.18及以上版本。
- [已开通快照](https://help.aliyun.com/zh/ecs/user-guide/activate-ecs-snapshot#task-ojj-1tr-lgb) ，开通快照不收费，创建快照后才开始收费。

## 功能概述

在ACK集群中，通常使用云盘存储卷为StatefulSet提供持久化存储。基于云盘本身提供的快照功能，Kubernetes使用以下两个特性来实现云盘存储卷的数据备份和恢复能力。

- 通过VolumeSnapshot资源实现云盘数据的备份（快照功能）。
- 通过PVC的 [DataSource](https://kubernetes.io/docs/concepts/storage/volume-pvc-datasource/) 功能实现云盘数据的恢复。

## 计费说明

ACK的存储快照基于ECS快照实现。快照会收取存储费用，具体请参见 [快照计费](https://help.aliyun.com/zh/ecs/snapshots-1#concept-rq2-pcx-ydb) 。

## 使用说明

为了实现快照相关功能，ACK通过 [CRD](https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/#customresourcedefinitions) 定义了以下3个相关的资源类型。

<table><tbody><tr><td rowspan="1" colspan="1"><p><b>资源类型名称</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p>VolumeSnapshotContent</p></td><td rowspan="1" colspan="1"><p>存储后端的快照，由集群管理员创建维护，无NameSpace。类似PV概念。</p></td></tr><tr><td rowspan="1" colspan="1"><p>VolumeSnapshot</p></td><td rowspan="1" colspan="1"><p>声明一个快照，由操作人员创建维护，属于特定Namespace。类似PVC概念。</p></td></tr><tr><td rowspan="1" colspan="1"><p>VolumeSnapshotClass</p></td><td rowspan="1" colspan="1"><p>定义一个快照类，描述创建快照使用的参数、Controller。类似StorageClass概念。</p></td></tr></tbody></table>

绑定规则如下：

- 使用Snapshot资源类型时，类似PV和PVC，首先您需绑定VolumeSnapshot与VolumeSnapshotContent。
- 如果VolumeSnapshot正确配置了VolumeSnapshotClassName字段，集群会自动创建VolumeSnapshotContent。如果没有配置或者配置错误，则无法自动创建，您需要手动创建VolumeSnapshotContent，并绑定VolumeSnapshot。
- VolumeSnapshotContent与VolumeSnapshot绑定是一对一的关系。

**重要**

删除VolumeSnapshotContent时，后端的快照也会被删除。

## 动态创建快照

### 使用流程

ACK使用云盘动态创建快照使用流程如下图所示。 ![snapshot](https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/9998723061/p175481.png)

**重要**

使用PL0、PL1、PL2、PL3级别的ESSD云盘或ESSD AutoPL云盘时，动态创建的快照默认开启 [快照极速可用能力](https://help.aliyun.com/zh/ecs/user-guide/enable-or-disable-the-instant-access-feature#taskbody-xf9-uu1-bil) 。

使用流程说明如下：

<table><tbody><tr><td rowspan="1" colspan="1"><p><b>流程步骤</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p>①</p></td><td rowspan="1" colspan="1"><p>创建应用并使用云盘存储卷保存数据。</p></td></tr><tr><td rowspan="1" colspan="1"><p>②</p></td><td rowspan="1" colspan="1"><p>创建关联了VolumeSnapshotClass的VolumeSnapshot，此时集群会自动创建VolumeSnapshotContent和存储后端的快照。</p></td></tr><tr><td rowspan="1" colspan="1"><p>③</p></td><td rowspan="1" colspan="1"><p>创建新的应用，并配置PVC引用步骤②中创建的快照。</p></td></tr></tbody></table>

上述的三个步骤实现：

- 备份：Volume1的数据被备份到Snapshot1。
- 恢复：Snapshot1的数据（也就是Volume1的数据）被恢复成Volume2。

### 使用示例

1. 创建VolumeSnapshotClass。
	1. 使用以下YAML内容创建volumesnapshotclass.yaml文件。
		```yaml
		apiVersion: snapshot.storage.k8s.io/v1
		kind: VolumeSnapshotClass
		metadata:
		 name: default-snapclass
		driver: diskplugin.csi.alibabacloud.com
		parameters:
		  retentionDays: "5"
		  forceDelete: "true"
		deletionPolicy: Delete
		```
		<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>说明</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><code>retentionDays</code></p></td><td rowspan="1" colspan="1"><p>指定快照自动回收时间。单位为天。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>forceDelete</code></p></td><td rowspan="1" colspan="1"><p>当 <code>forceDelete</code> 配置为 <code>"true"</code> 时，表示使用强制删除快照功能。</p><p>自csi-provisioner组件v1.26.5-92f859a-aliyun版本起，默认使用强制删除且不可修改，此前默认为普通删除。</p><ul><li><p>强制删除：强制删除用户创建的所有已使用和未使用的快照。</p></li><li><p>普通删除：只删除未使用的快照。不删除已经使用过的快照。</p></li></ul></td></tr><tr><td rowspan="1" colspan="1"><p><code>deletionPolicy</code></p></td><td rowspan="1" colspan="1"><p>快照的回收策略。取值范围：</p><ul><li><p><code>Delete</code> ：删除VolumeSnapshot时，VolumeSnapshotContent以及关联的快照也会一起被删除。</p></li><li><p><code>Retain</code> ：删除VolumeSnapshot时，VolumeSnapshotContent以及关联的快照不会被删除。</p></li></ul></td></tr></tbody></table>
		2. 创建VolumeSnapshotClass。
		```bash
		kubectl apply -f volumesnapshotclass.yaml
		```
2. 创建应用并写入数据。
	1. 使用以下YAML内容创建nginx.yaml文件。
		```yaml
		apiVersion: apps/v1
		kind: StatefulSet
		metadata:
		  name: nginx
		spec:
		  selector:
		    matchLabels:
		      app: nginx
		  serviceName: "nginx"
		  replicas: 1
		  template:
		    metadata:
		      labels:
		        app: nginx
		    spec:
		      containers:
		      - name: nginx
		        image: anolis-registry.cn-zhangjiakou.cr.aliyuncs.com/openanolis/nginx:1.14.1-8.6
		        imagePullPolicy: IfNotPresent
		        volumeMounts:
		        - name: disk
		          mountPath: /data
		  volumeClaimTemplates:
		  - metadata:
		      name: disk
		    spec:
		      accessModes: [ "ReadWriteOnce" ]
		      storageClassName: "alicloud-disk-topology-alltype"
		      resources:
		        requests:
		          storage: 20Gi
		```
		2. 创建应用。
		```bash
		kubectl apply -f nginx.yaml
		```
		3. 查看Pod部署状态。
		```bash
		kubectl get pod -l app=nginx
		```
		预期返回：
		```bash
		NAME        READY   STATUS    RESTARTS   AGE
		nginx-0     1/1     Running   0          82s
		```
		4. 向挂载路径写入数据。
		```bash
		kubectl exec -it nginx-0 -- touch /data/test
		kubectl exec -it nginx-0 -- ls /data
		```
		预期返回：
		```
		lost+found test
		```
3. 创建VolumeSnapshot。
	**重要**
	- 如果CSI组件版本不低于v1.22.12-b797ad9-aliyun，则创建快照时，不依赖该是否有Running Pod在使用PVC，可对任意挂载过的云盘创建快照。
	- 如果CSI组件版本低于v1.22.12-b797ad9-aliyun，则创建快照时，需要保证有Running Pod正在使用当前PVC，即保证云盘处于挂载状态。
	1. 使用以下YAML内容创建snapshot-1.yaml文件。
		```yaml
		apiVersion: snapshot.storage.k8s.io/v1
		kind: VolumeSnapshot
		metadata:
		  name: new-snapshot-demo
		  namespace: default
		spec:
		  volumeSnapshotClassName: default-snapclass   # 关联VolumeSnapshotClass
		  source:
		    persistentVolumeClaimName: disk-nginx-0
		```
		2. 创建VolumeSnapshot。
		```bash
		kubectl apply -f snapshot-1.yaml
		```
4. 查看VolumeSnapshot和VolumeSnapshotContent。
	**说明**
	您也可以登录 [ECS控制台](https://ecs.console.aliyun.com/#/snapshot/region/cn-hangzhou) 查看VolumeSnapshotContent对应的快照。
	1. 查看VolumeSnapshot。
		```bash
		kubectl get volumesnapshots
		```
		预期返回：
		```
		NAME                READYTOUSE   SOURCEPVC      SOURCESNAPSHOTCONTENT   RESTORESIZE   SNAPSHOTCLASS       SNAPSHOTCONTENT                                    CREATIONTIME   AGE
		new-snapshot-demo   true         disk-nginx-0                           20Gi          default-snapclass   snapcontent-48b04625-679a-490f-9ef3-f04b2b8e6c57   28s            28s
		```
		2. 查看VolumeSnapshotContent。
		```bash
		kubectl get VolumeSnapshotContent
		```
		预期返回：
		```
		NAME                                               READYTOUSE   RESTORESIZE   DELETIONPOLICY   DRIVER                            VOLUMESNAPSHOTCLASS   VOLUMESNAPSHOT      VOLUMESNAPSHOTNAMESPACE   AGE
		snapcontent-48b04625-679a-490f-9ef3-f04b2b8e6c57   true         21474836480   Delete           diskplugin.csi.alibabacloud.com   default-snapclass     new-snapshot-demo   default                   49s
		```
5. （可选）使用VolumeSnapshot创建一个新的应用，以此恢复数据。
	1. 使用以下YAML内容创建nginx-restore文件。
		在 `volumeClaimTemplates` 中，需设置 `dataSource.kind` 为 `VolumeSnapshot` ，且 `dataSource.name` 为VolumeSnapshot名称。
		```yaml
		apiVersion: apps/v1
		kind: StatefulSet
		metadata:
		  name: nginx-restore
		spec:
		  selector:
		    matchLabels:
		      app: nginx
		  serviceName: "nginx"
		  replicas: 1
		  template:
		    metadata:
		      labels:
		        app: nginx
		    spec:
		      containers:
		      - name: nginx
		        image: anolis-registry.cn-zhangjiakou.cr.aliyuncs.com/openanolis/nginx:1.14.1-8.6
		        imagePullPolicy: IfNotPresent
		        volumeMounts:
		        - name: disk
		          mountPath: /data
		  volumeClaimTemplates:
		  - metadata:
		      name: disk
		    spec:
		      accessModes: [ "ReadWriteOnce" ]
		      storageClassName: "alicloud-disk-topology-alltype"
		      resources:
		        requests:
		          storage: 20Gi
		      dataSource:
		        name: new-snapshot-demo
		        kind: VolumeSnapshot
		        apiGroup: snapshot.storage.k8s.io
		```
		2. 创建应用。
		```bash
		kubectl apply -f nginx-restore.yaml
		```
		3. 查看挂载路径的数据，确认数据是否已经恢复。
		```bash
		kubectl exec -it nginx-restore-0 -- ls /data
		```
		返回示例：
		```bash
		lost+found test
		```
6. （可选）若您暂时不需要创建工作负载，可以使用VolumeSnapshot创建一个PVC。
	1. 使用以下YAML内容创建pvc-restore文件。
		需设置 `dataSource.kind` 为 `VolumeSnapshot` ，且 `dataSource.name` 为VolumeSnapshot名称。
		```yaml
		apiVersion: v1
		kind: PersistentVolumeClaim
		metadata:
		  name: pvc-disk
		  namespace: default
		spec:
		  accessModes:
		  - ReadWriteOnce
		  resources:
		    requests:
		      storage: 20Gi
		  dataSource:
		    name: new-snapshot-demo
		    kind: VolumeSnapshot
		    apiGroup: snapshot.storage.k8s.io
		  storageClassName: alicloud-disk-topology-alltype
		  volumeMode: Filesystem
		```
		2. 创建PVC。
		**说明**
		对于以alicloud-disk-topology-alltype为例的VolumeBindingMode类型为WaitForFirstConsumer的存储类，创建出的PVC会处于Pending状态，直到被第一次挂载，期间需要保证VolumeSnapshot、VolumeSnapshotContent资源及对应的ECS快照实例未被删除。
		```bash
		kubectl apply -f pvc-restore.yaml
		```

## 静态创建快照（使用已有ECS快照）

如果您已在ECS控制台基于云盘创建了快照，可参考以下步骤将ECS快照导入至ACK集群中。

1. 基于已有ECS快照创建VolumeSnapshotContent。
	1. 使用以下YAML内容创建snapshot-content.yaml文件。
		```yaml
		apiVersion: snapshot.storage.k8s.io/v1
		kind: VolumeSnapshotContent
		metadata:
		  name: new-snapshot-content-test
		spec:
		  deletionPolicy: Retain
		  driver: diskplugin.csi.alibabacloud.com
		  source:
		    snapshotHandle: <YOUR-SNAPSHOTID>
		  volumeSnapshotRef:
		    name: new-snapshot-demo
		    namespace: default
		```
		<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><code>snapshotHandle</code></p></td><td rowspan="1" colspan="1"><p>已有快照的ID。您可以在 <a href="https://ecs.console.aliyun.com/#/snapshot/region/cn-hangzhou">ECS控制台</a> 的 <b>快照</b> 页面获取快照ID。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>volumeSnapshotRef</code></p></td><td rowspan="1" colspan="1"><p>填写要创建的VolumeSnapshot的信息。</p><ul><li><p><code>name</code> ：将要创建的VolumeSnapshot的名称。</p></li><li><p><code>namespace</code> ：将要创建的VolumeSnapshot所在的命名空间。</p></li></ul></td></tr></tbody></table>
		2. 创建VolumeSnapshotContent。
		```bash
		kubectl apply -f snapshot-content.yaml
		```
2. 创建VolumeSnapshot，并绑定VolumeSnapshotContent。
	1. 使用以下YAML内容创建snapshot-2.yaml文件。
		```yaml
		apiVersion: snapshot.storage.k8s.io/v1
		kind: VolumeSnapshot
		metadata:
		  name: new-snapshot-demo
		  namespace: default
		spec:
		  source:
		    volumeSnapshotContentName: new-snapshot-content-test
		```
		<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><code>metadata.name</code></p></td><td rowspan="1" colspan="1"><p>VolumeSnapshot名称，需要和VolumeSnapshotContent中 <code>volumeSnapshotRef.name</code> 的配置一致。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>volumeSnapshotContentName</code></p></td><td rowspan="1" colspan="1"><p>要绑定的VolumeSnapshotContent的名称。</p></td></tr></tbody></table>
		2. 创建VolumeSnapshot。
		```bash
		kubectl apply -f snapshot-2.yaml
		```
3. （可选）使用VolumeSnapshot创建一个新的应用，以此恢复数据。
	1. 使用以下YAML内容创建nginx-restore文件。
		在 `volumeClaimTemplates` 中，需设置 `dataSource.kind` 为 `VolumeSnapshot` ，且 `dataSource.name` 为VolumeSnapshot名称。
		```yaml
		apiVersion: apps/v1
		kind: StatefulSet
		metadata:
		  name: nginx-restore
		spec:
		  selector:
		    matchLabels:
		      app: nginx
		  serviceName: "nginx"
		  replicas: 1
		  template:
		    metadata:
		      labels:
		        app: nginx
		    spec:
		      containers:
		      - name: nginx
		        image: anolis-registry.cn-zhangjiakou.cr.aliyuncs.com/openanolis/nginx:1.14.1-8.6
		        imagePullPolicy: IfNotPresent
		        volumeMounts:
		        - name: disk
		          mountPath: /data
		  volumeClaimTemplates:
		  - metadata:
		      name: disk
		    spec:
		      accessModes: [ "ReadWriteOnce" ]
		      storageClassName: "alicloud-disk-topology-alltype"
		      resources:
		        requests:
		          storage: 20Gi
		      dataSource:
		        name: new-snapshot-demo
		        kind: VolumeSnapshot
		        apiGroup: snapshot.storage.k8s.io
		```
		2. 创建应用。
		```bash
		kubectl apply -f nginx-restore.yaml
		```
		3. 查看挂载路径的数据，确认数据是否已经恢复。
		```bash
		kubectl exec -it nginx-restore-0 -- ls /data
		```
		返回示例：
		```bash
		lost+found test
		```