---
title: "Kubernetes auto scaling"
date: "2021-05-08T13:28:00.004+08:00"
updated: "2021-05-08T13:31:18.043+08:00"
permalink: "/2021/05/kubernetes-auto-scaling.html"
original_url: "https://x8795278.blogspot.com/2021/05/kubernetes-auto-scaling.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3044722157319834098"
tags: ["auto scaling", "Kubernetes"]
layout: post
---

![](https://miro.medium.com/max/3840/0*CmyuLdGdOQJLKS5t.png)

# Kubernetes auto scaling
整體在Hyper-v 上實作，可以把我們之前的 service 部屬到 container pod 管理很多 service 可以配合 k8s 去進行集群的控管，因為負載不同也可以自行擴容等等，可能後續會再加入 aws 進行其他研究，
![](https://i.imgur.com/nXqvLVu.png)
基本上跟以前hadoop 差不多灌完環境在複製一份虛擬機就好

master
![](https://i.imgur.com/frUSeAx.png)
node
![](https://i.imgur.com/eLcjFmL.png)

個別下指令
#hostname 方便區別

```shell
# sudo hostnamectl set-hostname <name>
# hostname
```
![](https://i.imgur.com/0hgQTRH.png)

![](https://i.imgur.com/dUJtSqj.png)

# 設定docker開機自動啟動，跟查看啟動狀

```shell
# sudo systemctl enable docker
# sudo systemctl start docker
# sudo systemctl status docker
```

# 強制關閉 swap
![](https://i.imgur.com/4Ignfn2.png)
這樣可以kubelet重新開機服務不會開不起來
```shell
# sudo swapoff -a
註解掉有swap 
vim /etc/fstab 
```

# kubeadm、kubelet 和 kubectl 安裝
```shell

sudo apt-get update && sudo apt-get install -y apt-transport-https curl

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -

cat <<EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF

sudo apt-get update

sudo apt-get install -y kubelet kubeadm kubectl
```

# Master 端執行
```shell
export KUBECONFIG=/etc/kubernetes/admin.conf
sudo systemctl daemon-reload
sudo systemctl restart kubelet
```

```shell
# sudo kubeadm init --pod-network-cidr=10.244.0.0/16 --service-cidr=10.245.0.0/16 --
apiserver-advertise-address=<master_IP>
```
![](https://i.imgur.com/OQIJztR.png)

```shell
# mkdir -p $HOME/.kube
# sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
# sudo chown $(id -u):$(id -g) $HOME/.kube/config
```
```
$ mkdir -p $HOME/.kube
$ sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
$ sudo chown $(id -u):$(id -g) $HOME/.kube/config
```

# Kubeadm - flannel
讓所有pod都可以加入到區域網
![](https://i.imgur.com/VX5nunV.jpg)

```shell
 sudo kubectl apply -f 
https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
```

# node 端執行
加入節點到master
![](https://i.imgur.com/TvVZC7f.png)
master 檢查節點
![](https://i.imgur.com/DezVlDY.png)

# Master 端執行
```shell
 sudo kubectl apply -f https://k8s.io/examples/application/deployment.yaml
```
注意這兩個label
```ymal
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  selector:
    matchLabels:
      app: nginx <=== 注意要與service 匹配
  replicas: 2 # tells deployment to run 2 pods matching the template
  template:
    metadata:
      labels:
        app: nginx <=== 注意要與service 匹配
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80

```

```shell
 sudo kubectl get pod,deploy
```
![](https://i.imgur.com/0awY8GN.png)

# 觀察指令
```shell
sudo kubectl describe pod <pod_ID>
sudo kubectl describe service_ID <service_ID>
sudo kubectl describe hpa_ID <hpa_ID>
sudo kubectl describe deploy <deploy_ID>
```
# service

```shell
 wget 
https://raw.githubusercontent.com/kubernetes/website/master/content/zh/examples/service/netw
orking/nginx-svc.yaml

```

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nginx
  labels:
    app: nginx  <===注意要與service 匹配
spec:
  ports:
  - port: 80
    protocol: TCP
  selector:
    app: nginx  <===注意要與service 匹配
```
![](https://i.imgur.com/rZXevoG.png)
執行

# Kubernetes auto scaling
官方文檔案
 https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/

## install Metrics Server
Metric-Server 是 in memory 的 monitor，他不會將監控的資料儲存到Disk或
掛載的Volume，所以無法獲得過去的監控資料。
```
# wget https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

```
下載並修改yaml 檔案
```yaml
- --kubelet-preferred-address-types=InternalIP
- --kubelet-insecure-tls
```
![](https://i.imgur.com/kfbk0Vr.png)
這邊是當你的 HPA  auto scaling run 起來的要抓取 pod 裡面的硬體資訊 memory or packet or cpu 使用率等等
沒有的話k8s hpa target 會呈現unknown
![](https://i.imgur.com/IHpJs3q.png)
# nginx-hpa.yaml
```yaml
apiVersion: autoscaling/v1
kind: HorizontalPodAutoscaler
metadata:
  name: helloworld-hpa
  namespace: default
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2
  maxReplicas: 7
  targetCPUUtilizationPercentage: 20
```

```shell
 sudo kubectl create –f nginx-hpa.yaml
```
![](https://i.imgur.com/KWGJVYD.png)

# 增加負載
![](https://i.imgur.com/GT6etR9.png)
類似壓力測試
```shell

kubectl run -i --tty load-generator --rm --image=busybox --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://php-apache; done"
```
# 負載增加 pod 狀況
![](https://i.imgur.com/5TEqu5e.png)
# 負載減少 pod 狀況
過幾分鐘才會平衡
![](https://i.imgur.com/Q3WuA6V.png)

kubeadm join 172.22.219.214:6443 --token tv1in7.ts67215bd2n3ovci \
	--discovery-token-ca-cert-hash sha256:c9df78252d6080855853d5bde5f73ea4e89bc0619a72b33cc73072efbc8b4e2c

    
    
sudo    kubeadm join 172.30.124.19:6443 --token 1wquun.s2xs7qu72riy05sb \
	--discovery-token-ca-cert-hash sha256:cd3167bc76d52aef14a26a034979648d79150cd3a2f1b4e0ed1c9d79b0887753

