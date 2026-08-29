---
title: "install k8s on centos7"
date: "2024-04-17T06:36:00.001+08:00"
updated: "2024-04-17T06:36:17.313+08:00"
permalink: "/2024/04/install-k8s-on-centos7.html"
original_url: "https://x8795278.blogspot.com/2024/04/install-k8s-on-centos7.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-4451166422817639740"
tags: ["centos7", "Kubernetes"]
layout: post
---

![](https://hackmd.io/_uploads/B1yP6dnlC.png)

# install k8s
整體還是在vm 上面centos 模擬集群
![image](https://hackmd.io/_uploads/H1OBQdhgA.png)
先在master 上先裝好環境再複製兩個node1 , node2
VirtualBox 上面用以前的方式背景執行
```
C:\Program Files\Oracle\VirtualBox>VBoxManage.exe startvm "centos" --type headless
```
master
```
yum -y install vim
yum -y install wget
mv /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.repo.backup
wget -O /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo
```
創建後要換hostname
```
#master
hostnamectl set-hostname master
#node1
hostnamectl set-hostname node1
#node2
hostnamectl set-hostname node2
```
修改hosts
```
[root@localhost ~]# vim /etc/hosts

192.168.19.128 master
192.168.19.129 node1
192.168.19.130 node2
```
ntpdate同步時間
```
yum -y install ntpdate
ntpdate ntp1.aliyun.com
systemctl start ntpdate
sustemctl enable ntpdate
systemctl status ntpdate
```
關閉防火牆
```
systemctl stop firewalld.service 
systemctl disable firewalld.service
```

關閉selinux
```
sed -i 's/enforcing/disabled/' /etc/selinux/config
```

關閉 swap
```
free -h
sudo swapoff -a
sudo sed -i 's/.*swap.*/#&/' /etc/fstab
free -h
```
# install k8s 1.26.x
## install containerd
```
yum install -y yum-utils device-mapper-persistent-data lvm2
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo 
sudo yum install -y containerd.io

systemctl stop containerd.service

cp /etc/containerd/config.toml /etc/containerd/config.toml.bak
sudo containerd config default > $HOME/config.toml
sudo cp $HOME/config.toml /etc/containerd/config.toml

sudo sed -i "s#registry.k8s.io/pause#registry.cn-hangzhou.aliyuncs.com/google_containers/pause#g" /etc/containerd/config.toml
# https://kubernetes.io/zh-cn/docs/setup/production-environment/container-runtimes/#containerd-systemd

sudo sed -i "s#SystemdCgroup = false#SystemdCgroup = true#g" /etc/containerd/config.toml

systemctl start containerd.service
systemctl status containerd.service
```

橋接網路處理 IPv4
```
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
modprobe br_netfilter
echo 1 > /proc/sys/net/ipv4/ip_forward
```

# install kubeadm kubelet kubectl
```
sudo yum install -y kubelet-1.26.0-0 kubeadm-1.26.0-0 kubectl-1.26.0-0 --disableexcludes=kubernetes --nogpgcheck

systemctl daemon-reload
sudo systemctl restart kubelet
sudo systemctl enable kubelet
```
# docker to containerd
假設舊版的 k8s 要從docker 換成 containerd就按照這篇文章進行操作
```
systemctl stop kubelet
systemctl stop docker.socket
systemctl stop docker
```
containerd setting
```
yum install  containerd.io cri-tools  -y 
mkdir -p /etc/containerd
crictl config runtime-endpoint unix:///var/run/containerd/containerd.sock
containerd config default     
 
```
橋接網路處理 IPv4
```
cat << EOF > /etc/modules-load.d/containerd.conf
overlay
br_netfilter
EOF
 
modprobe overlay
modprobe br_netfilter
lsmod | egrep 'overlay|br_netfilter'

cat <<EOF > /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF
sysctl -p /etc/sysctl.d/k8s.conf
systemctl enable containerd  ; systemctl restart containerd
systemctl status containerd
```
# rewrite kubelet setting
```
cat /etc/sysconfig/kubelet
KUBELET_EXTRA_ARGS="--container-runtime=remote --runtime-request-timeout=15m --container-runtime-endpoint=unix:///run/containerd/containerd.sock"  https://kubernetes.io/zh-cn/docs/reference/command-line-tools-reference/kubelet/
systemctl restart kubelet
systemctl status kubelet
```
# init kubeadm init
```
kubeadm init \
 --apiserver-advertise-address=192.168.209.111 \
 --pod-network-cidr=192.168.0.0/16\
```
master 要下者兩行
```
Your Kubernetes control-plane has initialized successfully!

To start using your cluster, you need to run the following as a regular user:

  mkdir -p $HOME/.kube
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

Alternatively, if you are the root user, you can run:

  export KUBECONFIG=/etc/kubernetes/admin.conf

You should now deploy a pod network to the cluster.
Run "kubectl apply -f [podnetwork].yaml" with one of the options listed at:
  https://kubernetes.io/docs/concepts/cluster-administration/addons/

Then you can join any number of worker nodes by running the following on each as root:

```
# create node1 node2
將當前master vm 進行關機 透過 vm 去複製
node1, node2 ,
並且按照前面的方式 修改host name
![image](https://hackmd.io/_uploads/B1XFwu3xA.png)

分別在node1, node2下這行指令加入節點
```
kubeadm join 192.168.209.111:6443 --token nsd7j4.9nd50e4hxy2x0u4k \
        --discovery-token-ca-cert-hash sha256:7ac122dbc8b68f8a37c2fdd8089c46cee1862d4d1f83a7c70a6048ba17efae8d
```
回到master觀察節點
```
kubectl get node
```
![image](https://hackmd.io/_uploads/H1IWUO2gC.png)
maste 網路設定 calico
```
wget --no-check-certificate https://projectcalico.docs.tigera.io/archive/v3.25/manifests/calico.yaml

vim calico.yaml
```
```
       # Cluster type to identify the deployment type
            - name: CLUSTER_TYPE
              value: "k8s,bgp"
            - name: IP_AUTODETECTION_METHOD
              value: "interface=enp0s3"
              # INTERFACE_NAME=ens33
```
![image](https://hackmd.io/_uploads/SyoOUO2lA.png)

# kubectl apply
```
kubectl apply -f calico.yaml
```
等待幾分鐘應該可以看到ready
![image](https://hackmd.io/_uploads/BypoId2gA.png)
# export KUBECONFIG
```
kubectl get nodes  --kubeconfig=/etc/kubernetes/admin.conf
```
![image](https://hackmd.io/_uploads/B1Xh5unl0.png)

# tmux 管理其他 ssh
```
ctrl +b c create new windows
ctrl +b , rename
ctrl +b 0 1 2 switch windows
ctrl +b  d Detach
tmux ls
tmux attach  [id]
```
到這邊實驗環境就搭建完了
![image](https://hackmd.io/_uploads/B1yP6dnlC.png)

