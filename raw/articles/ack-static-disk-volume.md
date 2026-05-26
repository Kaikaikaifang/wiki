---
title: 使用静态存储卷挂载云盘
source: https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-a-statically-provisioned-disk-volume?spm=a2c4g.11186623.help-menu-85222.d_2_4_3_0.534b1578qpg8lb
author:
published:
created: 2026-05-26
description: 容器服务 Kubernetes 版（Container Service for Kubernetes，简称容器服务 ACK）提供高性能可伸缩的容器应用管理服务，支持企业级Kubernetes容器化应用的生命周期管理。
tags:
  - clippings
---
通过手动创建PV、PVC，可将云盘以静态存储卷的方式挂载到Pod上，以满足持久化存储需求，适用于对磁盘 I/O 性能和低延迟要求高、无数据共享需求的场景

云盘适用于以下存储场景：

- 对磁盘I/O要求高的应用，且没有共享数据的需求，如MySQL、Redis等数据存储服务。
- 高速写日志。
- 持久化存储数据，不会因Pod生命周期的结束而消失。

## 流程指引

1. 创建PV  
	在集群中“注册”一个已有的云盘，声明云盘的ID、容量、访问模式、可用区亲和性等，确保Pod能够被调度到正确的节点。
2. 创建PVC  
	应用通过PVC来“申请”使用已注册的存储资源。PVC会与符合条件的PV进行绑定。
3. 在应用中挂载  
	将已绑定的PVC挂载到应用Pod中，作为容器内的一个持久化目录。

## 适用范围

- CSI组件限制：已安装csi-plugin组件和csi-provisioner组件。
	> CSI组件默认安装，请确保未手动卸载。可在 **组件管理** 页面查看安装情况。建议 [升级CSI组件](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/install-and-upgrade-the-csi-plug-in#section-csv-gvs-vdb) 至最新版本。
- 云盘为 **待挂载** 状态，且满足以下要求：
	- 可用区限制：除ESSD同城冗余云盘外，其他云盘类型无法跨可用区挂载，只能挂载到同一可用区下的Pod。
		- 实例规格族限制：部分云盘类型仅支持挂载到特定的 [实例规格族](https://help.aliyun.com/zh/ecs/user-guide/overview-of-instance-families#concept-sx4-lxv-tdb) 。
- 虚拟节点限制：如需在虚拟节点上使用云盘，需遵循集群和kube-scheduler版本要求。
	**展开查看版本要求**
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>集群版本</b></p></td><td rowspan="1" colspan="1"><p><b>kube-scheduler版本</b></p></td></tr><tr><td rowspan="1" colspan="1"><p>1.28及以上</p></td><td rowspan="1" colspan="1"><p>6.9.3及以上</p></td></tr><tr><td rowspan="1" colspan="1"><p>1.26</p></td><td rowspan="1" colspan="1"><p>6.8.7</p></td></tr><tr><td rowspan="1" colspan="1"><p>1.24</p></td><td rowspan="1" colspan="1"><p>6.4.7</p></td></tr><tr><td rowspan="1" colspan="1"><p>1.22</p></td><td rowspan="1" colspan="1"><p>6.4.5</p></td></tr></tbody></table>
- 灵骏节点限制：如需在灵骏节点上使用云盘，需满足以下要求。
	**展开查看**
	- CSI 组件：不低于 v1.34.3。
	- 云盘标签：
		1. 访问 [ECS控制台-块存储-云盘](https://ecs.console.aliyun.com/disk/) 。
			2. 在创建云盘过程中（仅支持在创建时添加），为云盘添加 `createdByProduct:eflo` 标签。
			示例如下：
			![image](https://help-static-aliyun-doc.aliyuncs.com/assets/img/zh-CN/1701668771/p1055258.png)
			> 如挂载时报错 `OperationDenied.HpnZoneMismatch` ，请参见 [灵骏节点中挂载云盘时，Pod Event 报错 OperationDenied.HpnZoneMismatch怎么办？](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-disk-volumes#b6742b336170v) 。
		创建后，使用该云盘来手动创建PV并通过PVC来绑定。该云盘可以且仅可以被调度到灵骏节点。

## 步骤一：创建PV

创建 PV，将已有云盘声明为集群中的一个可用存储资源。

kubectl

控制台

1. 参见以下内容，创建disk-pv.yaml。
	> 需提前获取云盘ID、云盘大小、可用区ID、云盘类型等信息，将YAML中的变量替换为实际值。
	```yaml
	apiVersion: v1
	kind: PersistentVolume
	metadata:
	  # 已有云盘ID，如d-uf628m33r5rsbi******
	  name: "<YOUR-DISK-ID>"
	  annotations:
	    # 推荐配置，以确保Pod调度到支持该云盘类型的节点上
	    # <YOUR-DISK-CATEGORY>为已有云盘的类型，支持cloud_essd_entry、cloud_auto、cloud_essd、cloud_ssd、cloud_efficiency、cloud_regional_disk_auto
	    csi.alibabacloud.com/volume-topology: '{"nodeSelectorTerms":[{"matchExpressions":[{"key":"node.csi.alibabacloud.com/disktype.<YOUR-DISK-CATEGORY>","operator":"In","values":["available"]}]}]}'
	spec:
	  capacity:
	    # 已有云盘大小，如 20Gi
	    storage: "<YOUR-DISK-SIZE>"
	  claimRef:
	    apiVersion: v1
	    kind: PersistentVolumeClaim
	    namespace: default
	    name: disk-pvc
	  accessModes:
	    - ReadWriteOnce
	  persistentVolumeReclaimPolicy: Retain
	  csi:
	    driver: diskplugin.csi.alibabacloud.com
	    # 已有云盘ID，如d-uf628m33r5rsbi******
	    volumeHandle: "<YOUR-DISK-ID>"
	  nodeAffinity:
	    required:
	      nodeSelectorTerms:
	      - matchExpressions:
	        - key: topology.diskplugin.csi.alibabacloud.com/zone
	          operator: In
	          values:
	          # 已有云盘所在的可用区，例如cn-shanghai-f
	          - "<YOUR-DISK-ZONE-ID>"
	  storageClassName: alicloud-disk-topology-alltype
	  volumeMode: Filesystem
	```
	相关参数说明如下：
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>说明</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><code>csi.alibabacloud.com/volume-topology</code></p></td><td rowspan="1" colspan="1"><section><p>此Annotation用于为云盘设置节点亲和性，确保使用该云盘的 Pod能够被调度到支持对应云盘类型的节点上，避免因节点不匹配导致挂载失败。</p><p>为确保调度准确性，建议配置云盘类型。支持的类型如下：</p><ul><li><p>ESSD Entry云盘： <code>cloud_essd_entry</code></p></li><li><p>ESSD AutoPL云盘： <code>cloud_auto</code></p></li><li><p>ESSD云盘： <code>cloud_essd</code></p></li><li><p>SSD云盘： <code>cloud_ssd</code></p></li><li><p>高效云盘： <code>cloud_efficiency</code></p></li><li><p>同城冗余云盘： <code>cloud_regional_disk_auto</code> （还需参见调整配置）</p></li></ul></section></td></tr><tr><td rowspan="1" colspan="1"><p><code>claimRef</code></p></td><td rowspan="1" colspan="1"><p>指定PV所能绑定的PVC。如果希望PV可被任意PVC绑定，请删除该配置。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>accessModes</code></p></td><td rowspan="1" colspan="1"><section><p>访问模式。取决于是否启用 <a href="https://help.aliyun.com/zh/ecs/user-guide/enable-multi-attach">云盘多重挂载功能</a> 。</p><ul><li><p>未启用多重挂载：仅支持 <code>ReadWriteOnce</code> （RWO），该云盘一次只能被一个节点以读写方式挂载。</p></li><li><p>已启用多重挂载：</p><ul><li><p>将其作为标准文件系统使用（即已格式化）：支持 <code>ReadWriteOnce</code> （RWO）和 <code>ReadOnlyMany</code> （ROX）。</p><blockquote>为防止文件系统（如ext4）在多节点并发写入时数据损坏，不支持 <code>ReadWriteMany</code> （RWX）模式。</blockquote></li><li><p>将其作为裸设备使用（即未格式化）：支持 <code>ReadWriteOnce</code> （RWO）、 <code>ReadOnlyMany</code> （ROX）和 <code>ReadWriteMany</code> （RWX）。</p></li></ul></li></ul></section></td></tr><tr><td rowspan="1" colspan="1"><p><code>persistentVolumeReclaimPolicy</code></p></td><td rowspan="1" colspan="1"><section><p>PV的回收策略，决定了绑定的PVC被删除后，PV及后端云盘的生命周期。</p><ul><li><p><code>Delete</code> ：删除PVC时，PV和云盘会一起删除。请谨慎配置。</p><blockquote>为防止数据意外丢失，可在执行删除前为云盘 <a href="https://help.aliyun.com/zh/ecs/user-guide/create-an-automatic-snapshot-policy-1">创建自动快照策略</a> 进行备份。</blockquote></li><li><p><code>Retain</code> ：删除PVC时，PV和云盘不会被删除，需手动释放。</p></li></ul></section></td></tr><tr><td rowspan="1" colspan="1"><p><code>driver</code></p></td><td rowspan="1" colspan="1"><p>使用阿里云云盘时，固定为 <code>diskplugin.csi.alibabacloud.com</code> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>nodeAffinity</code></p></td><td rowspan="1" colspan="1"><p>节点亲和性配置。除ESSD同城冗余云盘外，其他云盘类型无法跨可用区挂载，只能挂载到同一可用区下的Pod。该配置可确保Pod调度到云盘所在可用区对应的ECS节点。</p><section><p>对于同城冗余云盘，请将其改为以下内容，以允许云盘挂载到该地域中的任意可用区。</p><blockquote>其中 <code><YOUR-DISK-REGION-ID></code> 为云盘所在地域，例如 <code>cn-shanghai</code> 。</blockquote><div><pre><code>nodeAffinity:
	  required:
	    nodeSelectorTerms:
	    - matchExpressions:
	      - key: topology.kubernetes.io/region
	        operator: In
	        values:
	        - "<YOUR-DISK-REGION-ID>"</code></pre></div></section></td></tr><tr><td rowspan="1" colspan="1"><p><code>storageClassName</code></p></td><td rowspan="1" colspan="1"><p>该配置对静态卷无意义，无需预先创建对应的StorageClass，但需确保PV和PVC中的该配置项取值保持一致。</p></td></tr></tbody></table>
2. 创建PV。
	```bash
	kubectl create -f disk-pv.yaml
	```
3. 查看PV状态，确认为 `Available` 。
	```bash
	kubectl get pv
	```
	预期返回：
	```bash
	NAME                     CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS      CLAIM              STORAGECLASS                             VOLUMEATTRIBUTESCLASS   REASON   AGE
	d-uf628m33r5rsbi******   20Gi       RWO            Retain           Available   default/disk-pvc   alicloud-disk-topology-alltype           <unset>                          1m36s
	```

1. 在 [ACK集群列表](https://cs.console.aliyun.com/) 页面，单击目标集群名称，在集群详情页左侧导航栏，选择 **存储** > **存储卷** 。
2. 在 **存储卷** 页面，单击 **创建** ，选择 **存储卷类型** 为 **云盘** ，按照页面提示完成PV的配置。
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><b>访问模式</b></p></td><td rowspan="1" colspan="1"><p>仅支持ReadWriteOnce。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>云盘ID</b></p></td><td rowspan="1" colspan="1"><p>单击 <b>选择云盘</b> ，选择与节点处于同一地域可用区下的待挂载的云盘。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>文件系统类型</b></p></td><td rowspan="1" colspan="1"><p>选择以何种数据类型将数据存储到云盘上。支持 <b>文件系统类型</b> 包括ext4、ext3、xfs、vfat。</p></td></tr></tbody></table>

## 步骤二：创建PVC

创建 PVC，绑定上一步创建的 PV。

kubectl

控制台

1. 参见以下内容，创建disk-pvc.yaml。
	```yaml
	apiVersion: v1
	kind: PersistentVolumeClaim
	metadata:
	  name: disk-pvc
	spec:
	  accessModes:
	  - ReadWriteOnce
	  resources:
	    requests:
	      # 申请的存储容量，需与PV容量保持一致
	      storage: "<YOUR-DISK-SIZE>"
	  # 与PV中定义的 storageClassName 保持一致
	  storageClassName: alicloud-disk-topology-alltype
	  # 指定待绑定的 PV
	  volumeName: "<YOUR-DISK-ID>"
	```
	相关参数说明如下：
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>说明</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><code>accessModes</code></p></td><td rowspan="1" colspan="1"><p>访问模式，需与PV的配置保持一致。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>storage</code></p></td><td rowspan="1" colspan="1"><p>分配给Pod的存储容量，需与PV容量保持一致。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>storageClassName</code></p></td><td rowspan="1" colspan="1"><p>该配置对静态卷无意义，无需预先创建对应的StorageClass，但需确保PV和PVC中的该配置项取值保持一致。</p></td></tr><tr><td rowspan="1" colspan="1"><p><code>volumeName</code></p></td><td rowspan="1" colspan="1"><p>指定待绑定的PV。如期望PVC可绑定任意PV，可删除此参数。</p></td></tr></tbody></table>
2. 创建PVC。
	```bash
	kubectl create -f disk-pvc.yaml
	```
3. 查看PVC状态，确认为 `Bound` 。
	```bash
	kubectl get pvc
	```
	预期返回如下，可以看到PVC已关联云盘PV。
	```bash
	NAME                       STATUS   VOLUME                                     CAPACITY   ACCESS MODES   STORAGECLASS                     VOLUMEATTRIBUTESCLASS   AGE
	disk-pvc                   Bound    d-bp1ff1mn65jk8s******                     20Gi       RWO            alicloud-disk-topology-alltype   <unset>                 6s
	```

1. 在集群管理页左侧导航栏，选择 **存储** > **存储声明** 。
2. 在 **存储声明** 页面，单击 **创建** ，选择 **存储声明类型** 为 **云盘** ，按照页面提示完成PVC的创建。
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><b>分配模式</b></p></td><td rowspan="1" colspan="1"><p>选择 <b>已有存储卷</b> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>已有存储卷</b></p></td><td rowspan="1" colspan="1"><p>选择此前创建的PV。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>总量</b></p></td><td rowspan="1" colspan="1"><p>分配给Pod的存储容量，不超过云盘容量上限。</p></td></tr></tbody></table>

## 步骤三：创建应用并挂载云盘

创建工作负载，并通过挂载 PVC 来使用云盘。

**重要**

云盘为非共享存储，未开启多重挂载时一次只能挂载一个Pod。在多副本 Deployment 中共享PVC会导致新Pod无法挂载仍被旧Pod占用的云盘而启动失败。推荐使用StatefulSet或单独为Pod挂载云盘。

如仍需在Deployment中使用云盘，建议 [使用云盘作为临时存储卷](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/best-practices-for-using-deployment-for-temporary-storage) 。如需启用多重挂载，请参见 [使用NVMe云盘多重挂载及Reservation](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/multi-attach-and-reservation-of-nvme-cloud-disks) 。

kubectl

控制台

1. 参见以下内容，创建disk-test.yaml。
	> 以下示例创建了一个副本数为1的StatefulSet，Pod通过名为 `disk-pvc` 的PVC申请存储资源，挂载路径为 `/data` 。
	```yaml
	apiVersion: apps/v1
	kind: StatefulSet
	metadata:
	  name: disk-test
	spec:
	  replicas: 1
	  selector:
	    matchLabels:
	      app: nginx
	  template:
	    metadata:
	      labels:
	        app: nginx
	    spec:
	      containers:
	      - name: nginx
	        image: anolis-registry.cn-zhangjiakou.cr.aliyuncs.com/openanolis/nginx:1.14.1-8.6
	        ports:
	        - containerPort: 80
	        volumeMounts:
	        - name: pvc-disk
	          mountPath: /data
	      volumes:
	        - name: pvc-disk
	          persistentVolumeClaim:
	            claimName: disk-pvc
	```
	**重要**
	- 在 Pod 中配置 `securityContext.fsgroup` 会导致kubelet在挂载卷时递归修改文件权限（ `chmod` / `chown` ）。若文件数量庞大，将显著延长挂载时间。
		对于1.20及以上版本的集群，建议将 `fsGroupChangePolicy` 配置为 `OnRootMismatch` ，仅在首次挂载且卷根目录权限不匹配时才执行递归的权限变更，以优化挂载性能。若性能仍不满足要求或需更精细的权限控制，建议使用 `initContainer` 在主应用容器启动前自行执行权限调整命令。
	- Pod重建时会重新挂载原有云盘。如果由于其他限制导致Pod无法调度到原可用区，Pod会因无法挂载云盘而一直处于Pending状态。
2. 创建StatefulSet并挂载云盘。
	```bash
	kubectl create -f disk-test.yaml
	```
3. 查看 Pod 状态，确认为 `Running` 。
	```bash
	kubectl get pod -l app=nginx
	```
	预期输出：
	```bash
	NAME          READY   STATUS    RESTARTS   AGE
	disk-test-0   1/1     Running   0          14s
	```
4. 查看挂载路径，确认已挂载云盘。
	```bash
	kubectl exec disk-test-0 -- df -h /data
	```
	预期输出：
	```bash
	Filesystem      Size  Used Avail Use% Mounted on
	/dev/vdb         20G   24K   20G   1% /data
	```

1. 在集群管理页左侧导航栏，选择 **工作负载** > **有状态** 。
2. 在 **有状态** 页面，单击 **使用镜像创建** 。
3. 在 **有状态** 页面，单击 **使用镜像创建** ，按照页面提示完成StatefulSet的参数配置。
	主要配置项如下，详细配置项说明请参见 [创建有状态工作负载StatefulSet](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-a-statefulset-to-create-a-stateful-application-1) 。
	<table><tbody><tr><td rowspan="1" colspan="1"><p><b>配置页</b></p></td><td rowspan="1" colspan="1"><p><b>参数</b></p></td><td rowspan="1" colspan="1"><p><b>描述</b></p></td></tr><tr><td rowspan="1" colspan="1"><p><b>应用基本信息</b></p></td><td rowspan="1" colspan="1"><p><b>副本数量</b></p></td><td rowspan="1" colspan="1"><p>配置StatefulSet的副本数量。</p></td></tr><tr><td rowspan="3" colspan="1"><p><b>容器配置</b></p></td><td rowspan="1" colspan="1"><p><b>镜像名称</b></p></td><td rowspan="1" colspan="1"><p>输入用于部署应用的镜像地址，如 <code>anolis-registry.cn-zhangjiakou.cr.aliyuncs.com/openanolis/nginx:1.14.1-8.6</code> 。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>所需资源</b></p></td><td rowspan="1" colspan="1"><p>设置所需的vCPU、内存和临时存储资源。</p><p>本示例配置CPU为0.25 Core，内存为512 MiB。</p></td></tr><tr><td rowspan="1" colspan="1"><p><b>数据卷</b></p></td><td rowspan="1" colspan="1"><p>单击 <b>增加云存储声明（PersistentVolumeClaim）</b> ，然后完成参数配置。</p><ul><li><p><b>挂载源</b> ：选择此前创建的PVC。</p></li><li><p><b>容器路径</b> ：输入云盘要挂载到的容器路径，如/data。</p></li></ul></td></tr></tbody></table>
4. 查看应用部署情况。
	1. 在 **有状态** 页面，单击应用名称。
		2. 在 **容器组** 页签下，确认Pod已正常运行（状态为Running）。

## 验证数据持久化存储

通过“写入数据 -> 删除 Pod -> 检查数据”的流程，来验证存储在云盘上的数据在 Pod 重建后是否仍然存在。

1. 在 Pod 中写入测试数据。
	1. 查看挂载路径，即查看云盘中的数据。
		```bash
		kubectl exec disk-test-0 -- ls /data
		```
		预期输出：
		```bash
		lost+found
		```
		2. 在 Pod 中写入测试数据。
		以Pod `disk-test-0` 为例，在其挂载的云盘路径 `/data` 下创建一个test文件。
		```bash
		kubectl exec disk-test-0 -- touch /data/test
		```
2. 模拟 Pod 故障，删除 Pod。
	```bash
	kubectl delete pod disk-test-0
	```
	再次执行 `kubectl get pod -l app=nginx` ，可以发现已自动创建一个同名的Pod。
3. 验证新 Pod 中的数据。
	在新Pod `disk-test-0` 中再次检查 `/data` 目录。
	```bash
	kubectl exec disk-test-0 -- ls /data
	```
	预期输出中，此前创建的 test 文件依然存在，表明即使 Pod 被删除重建，数据也实现了持久化存储。
	```bash
	lost+found  
	test
	```

## 应用于生产环境

- 高可用性
	- Pod调度策略
		在PV中正确配置 `nodeAffinity` 和 `csi.alibabacloud.com/volume-topology` ，确保Pod在重建后能够成功调度并重新挂载云盘。
		- 云盘选型
		需综合评估其 [性能](https://help.aliyun.com/zh/ecs/user-guide/block-storage-performance) 、 [计费](https://www.aliyun.com/price/product#/disk/detail) 以及节点的可用区和 [实例规格族](https://help.aliyun.com/zh/ecs/user-guide/overview-of-instance-families#concept-sx4-lxv-tdb) ，确保Pod能被调度至兼容的节点。
		选择 [云盘类型](https://help.aliyun.com/zh/ecs/user-guide/elastic-block-storage-devices#87438f9ee2d81) 时，SSD云盘、高效云盘已逐步停止售卖。建议选用ESSD PL0云盘或ESSD Entry云盘替换高效云盘，选用ESSD AutoPL云盘替换SSD云盘。
		- 构建跨可用区容灾方案
		- 应用层容灾： 对于数据库等关键业务，在多个可用区部署应用实例，并通过应用自身的数据同步机制实现高可用。
				- 存储层容灾：选用支持多可用区容灾的云盘类型，将数据实时同步写入同一地域的不同可用区，实现跨可用区的故障恢复，请参见 [使用ESSD同城冗余云盘](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-regional-essd-disks) 。
- 数据安全：
	- 常态化备份：通过 [自动快照](https://help.aliyun.com/zh/ecs/user-guide/create-an-automatic-snapshot-policy-1) 为云盘创建自动快照，以便数据备份和恢复。
- 性能与成本优化
	- 启用并行挂载
		默认情况下，单个节点的云盘操作是串行的。可 [使用云盘并行挂载](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/attach-cloud-disks-in-parallel) ，加速Pod启动。
		- 配置存储监控与告警
		基于 [容器存储监控](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/use-csi-plugin-to-monitor-storage-resources-at-the-node-side) 配置告警，及时发现存储卷异常或性能瓶颈。

## 资源释放指引

为避免产生预期外的费用并确保数据安全，请遵循以下流程释放无需使用的资源。

1. 删除工作负载
	- 操作：删除所有使用相关PVC的应用，例如Deployment、StatefulSet等。此操作将停止运行的Pod并卸载存储卷。
		命令示例： `kubectl delete deployment <your-deployment-name>`
2. 删除PVC
	- 操作：删除应用关联的PVC。删除后，其绑定PV的后续行为取决于该PV的 `persistentVolumeReclaimPolicy` 。
		- 回收策略说明：
		- `Retain` ：删除PVC后，其绑定的PV状态会变为 `Released` ，但PV对象和后端的云盘会被完整保留。如确认云盘及其上的所有数据无需使用，请参见 [释放云盘](https://help.aliyun.com/zh/ecs/user-guide/release-a-disk) 删除。此操作不可逆，请务必谨慎操作。
				- `Delete` ：删除PVC后，PV对象和后端的云盘会被删除。云盘上的数据将永久丢失且无法恢复，请谨慎使用。
			> 为防止数据意外丢失，可在执行删除前为云盘 [创建自动快照策略](https://help.aliyun.com/zh/ecs/user-guide/create-an-automatic-snapshot-policy-1) 进行备份。
		- 命令示例： `kubectl delete pvc <your-pvc-name>`
3. 删除PV对象：此操作仅移除集群内的资源定义，不会删除后端的云盘实体。
	- 操作：手动删除处于 `Released` 状态的PV。
		- 命令示例： `kubectl delete pv <your-pv-name>`

## 相关文档

- 云盘多可用区部署的配置优化建议，请参见 [云盘存储卷的高可用配置建议](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/recommended-storage-settings-for-cross-zone-deployment) 。
- 云盘容量不足或磁盘已满，请参见 [扩容云盘存储卷](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/expand-a-disk-volume/) 进行扩容。
- 如果不再使用某块云盘且希望云盘停止计费时，可 [释放云盘](https://help.aliyun.com/zh/ecs/user-guide/release-a-disk) 。释放后，云盘及存储在云盘上的数据会被删除、云盘停止计费。
- 使用云盘存储卷时如遇问题，请参见 [云盘存储卷FAQ](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/faq-about-disk-volumes) 。
- 如集群仍在使用废弃的FlexVolume组件，请 [迁移FlexVolume至CSI](https://help.aliyun.com/zh/ack/ack-managed-and-ack-dedicated/user-guide/upgrade-from-flexvolume-to-csi/) 。