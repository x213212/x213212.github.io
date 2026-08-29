---
title: "Creating jenkins tasklets to k8s"
date: "2024-04-28T19:03:00.005+08:00"
updated: "2024-04-28T19:03:47.180+08:00"
permalink: "/2024/04/creating-jenkins-tasklets-to-k8s.html"
original_url: "https://x8795278.blogspot.com/2024/04/creating-jenkins-tasklets-to-k8s.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-496584705129950941"
tags: ["jenkins", "Kubernetes"]
layout: post
---

![](https://hackmd.io/_uploads/SyH5hiiWC.png)

# vm using static ip
上次沒考慮好，我的vm又是吃網卡，所以斷線ip會浮動
這邊直接建立一張
VirtualBox Host-Only Ethernet Adapter #2
![image](https://hackmd.io/_uploads/H1B5pwjZ0.png)
之後在每一台server都要多一張網卡
![image](https://hackmd.io/_uploads/r1wyRDo-0.png)
照理說應該會多出一個網卡enp0s8
這邊在linux 要額外設定一下
```
cp /etc/sysconfig/network-scripts/ifcfg-enp0s3 /etc/sysconfig/network-scripts/ifcfg-enp0s8
```
重新調整網卡
vim /etc/sysconfig/network-scripts/ifcfg-enp0s8
記得調整成靜態
```
TYPE="Ethernet"
PROXY_METHOD="none"
BROWSER_ONLY="no"
BOOTPROTO="static"
DEFROUTE="yes"
IPV4_FAILURE_FATAL="no"
IPV6INIT="yes"
IPV6_AUTOCONF="yes"
IPV6_DEFROUTE="yes"
IPV6_FAILURE_FATAL="no"
IPV6_ADDR_GEN_MODE="stable-privacy"
NAME="enp0s8"
DEVICE="enp0s8"
ONBOOT="yes"
IPADDR=192.168.1.101
NETMASK=255.255.255.0
GATEWAY=192.168.1.1
DNS1=8.8.8.8
```
這樣內網溝通就沒什麼問題了
# disable ipv6
vim /etc/sysctl.conf
```
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
sudo systemctl restart network
sudo sysctl -p
```
![image](https://hackmd.io/_uploads/HJhjCwoZ0.png)

# calico.yaml
上次忘記看實際calico.yaml是否有正確啟動所有相關pods，這邊要注意pod 和 api server 網段要分開
```
kubeadm reset
kubeadm init --apiserver-advertise-address=192.168.1.100 --pod-network-cidr=192.169.0.0/16
 kubectl apply -f calico.yaml
 kubectl get pods -n kube-system
```

```
[root@master ~]# kubectl get pods -n kube-system
NAME                                      READY   STATUS              RESTARTS        AGE
calico-kube-controllers-57b57c56f-dw87n   0/1     ContainerCreating   0               38m
calico-node-47jfl                         0/1     Init:1/3            2 (28s ago)     2m6s
calico-node-kcxmw                         0/1     Init:1/3            2 (42s ago)     2m14s
calico-node-n69vd                         1/1     Running             0               38m
coredns-787d4945fb-9mkkh                  1/1     Running             0               44m
coredns-787d4945fb-cq99b                  1/1     Running             0               44m
etcd-master                               1/1     Running             7               44m
kube-apiserver-master                     1/1     Running             7               44m
kube-controller-manager-master            1/1     Running             4 (31m ago)     44m
kube-proxy-7b7vh                          1/1     Running             1 (3m33s ago)   43m
kube-proxy-wmm8f                          1/1     Running             0               44m
kube-proxy-zcqhk                          1/1     Running             1 (3m32s ago)   43m
kube-scheduler-master                     1/1     Running             30              44m

```
排查錯誤，可以看到RESTARTS 2次
```
kubectl describe pod -n kube-system calico-node-47jfl
```

```
2024-04-27 18:12:33.296 [INFO][1] cni-installer/<nil> <nil>: CNI plugin version: v3.25.0

2024-04-27 18:12:33.296 [INFO][1] cni-installer/<nil> <nil>: /host/secondary-bin-dir is not writeable, skipping
W0427 18:12:33.454506       1 client_config.go:617] Neither --kubeconfig nor --master was specified.  Using the inClusterConfig.  This might not work.
2024-04-27 18:13:03.606 [ERROR][1] cni-installer/<nil> <nil>: Unable to create token for CNI kubeconfig error=Post "https://10.96.0.1:443/api/v1/namespaces/kube-system/serviceaccounts/calico-node/token": dial tcp 10.96.0.1:443: i/o timeout
2024-04-27 18:13:03.606 [FATAL][1] cni-installer/<nil> <nil>: Unable to create token for CNI kubeconfig error=Post "https://10.96.0.1:443/api/v1/namespaces/kube-system/serviceaccounts/calico-node/token": dial tcp 10.96.0.1:443: i/o timeout
```

 kubectl describe pod -n kube-system nginx-deployment-6b7f675859-t6rtg

基本上這樣就可以解決cni 找不到 master 節點的問題

![image](https://hackmd.io/_uploads/HyznVT9WR.png)
# nginx-deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
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
        image: docker.io/nginx:latest
        ports:
        - containerPort: 80

```
# nginx-service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  type: LoadBalancer
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80

```

```
kubectl apply -f nginx-deployment.yaml
kubectl apply -f nginx-service.yaml
kubectl get pods
kubectl get svc
```

![image](https://hackmd.io/_uploads/B1FqPbsZR.png)
![image](https://hackmd.io/_uploads/HkbivWsZR.png)

# jenkins to k8s

![image](https://hackmd.io/_uploads/rJmvy_ob0.png)
![image](https://hackmd.io/_uploads/r1v38ojb0.png)
這邊需要Master 的 ~/.kube/config 先把它複製到 jenkins的
/var/lib/jenkins/k8s.yaml
這邊本來打算透過 token方式去請求，不過遇到蠻多問題的以後再補，這邊先應急的方法用admin
```
apiVersion: v1
clusters:
- cluster:
    certificate-authority-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJME1EUXlOekU0TWpRMU1Wb1hEVE0wTURReU5URTRNalExTVZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTkNYCkF5ZWJxRlJsZCtkVDNkTWozMDBnTmVSY3kxN2xUNHRIMkUxMzJPMzcvMjVvQ3NuZ0lLUm1pbkpYbkpnUUYySC8KWHc2b3lCRUxBbldFU0JFM0N2bEN3Vk1HRG9pL0krckVPajZTU04zekxyNEQ3TzF6YkJ0Z2l2UEJyU1BBcS9COQpnenp6NUttSWQ2RWtYcmJTbW1DcncxRlROTGUvL0lqSVVtakZ3YURwV2N5bVViTG50V2poNG1HR3lXY3VkcXFZCjlsc3k4Y2VXdlRaQU91VVpxazF1Wi9BMW1FbXZIbVVzbyszenpWWFI2L3dWU0ZacXlCeERyOXVSY1VWMDJaWkcKSnF6MUhQaHdiNG1CTmcvdnk5U0pZNVFoaU5rOXdJdytWdkoxdjY4NndzaVd6U2hINmZ6VkU4WHNJa3JSeSs1egprTCt5bmw1U2VzOGJRTTlFK2M4Q0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZNaFF1OStBU0xlUlVJbVRIUDNtb25TekVDTXJNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBTVdtMktXVFc1MVNHdmhERHBCawpteG45bG0wM2JydkFKRXhHRWRmSWlyLzlpR1JIQkc5M0dvV2g1K1FkY3N5aGhKTzJuK3owQlJCdnl1UmhLaCt1CnhQUlA5MGtMWG11UzFHeXZOcStEaWM0bm9JejZ2aG5DZ3BIMC9icTFnU3A1QlRHSlR3OEdVdGlzbjliZmc4a3YKb3E4SnpOWmhnb2FDTHEzaHl6ZmRBazhPMFBUVlU5N2FHbG5rekc2V3hlZFNzVTdPWVV2eGtsRCtCSGNrQmtiMQplT3ExNFNKMUs3d3BYWXMrZVNmRGhzSFVhc2srZzRCSkZKdytBNmFQMUwzY0lHSXAxV1JmT252VmhrZXZIVmxlCmZFdHdNNmswZlhXTjUwbklDYlVOa2pySzFTQ21rUFZhWVl3K0NPOEc2OWpmWWt5cUtyMnp4ZVhQdkdrdmlKZDYKeTJRPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
    server: https://192.168.1.100:6443
  name: kubernetes
contexts:
- context:
    cluster: kubernetes
    user: kubernetes-admin
  name: kubernetes-admin@kubernetes
current-context: kubernetes-admin@kubernetes
kind: Config
preferences: {}
users:
- name: jenkins
  user:
    token: YWRtaW4tdG9rZW4tMTcxNDI5MDY4Ng==
- name: kubernetes-admin
  user:
    client-certificate-data: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURJVENDQWdtZ0F3SUJBZ0lJUFJXeUl3LzQrZzR3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TkRBME1qY3hPREkwTlRGYUZ3MHlOVEEwTWpjeE9ESTBOVFJhTURReApGekFWQmdOVkJBb1REbk41YzNSbGJUcHRZWE4wWlhKek1Sa3dGd1lEVlFRREV4QnJkV0psY201bGRHVnpMV0ZrCmJXbHVNSUlCSWpBTkJna3Foa2lHOXcwQkFRRUZBQU9DQVE4QU1JSUJDZ0tDQVFFQXdZVjhDWEp4dlJ3RXFmVGsKMUJ4RStKMzZjMFVWZ0d1ZTNma21NZy9lVnR4aXE4a3lGcVNuQTZiSDhJZFo4cXRnaTdycStiSkJITG9DbCtnVwpNRHlhbVRPWkdxSmc5YVRka1ZJQXNMbS80TXZibTU0Z0hKL2w3UjZMeHQxL254Y1oybXFzdjVmQmF5RkY3ZG0vCnVHVUZrRFM3MmY5SkNPUzJiMWo3YjJycUtnQlFyTThtaU9KTHlOelFQTEFrS3pOTC9kVU9jRk9rblZDRkRiNUMKRTFpQU1VYzVIRy8yd2hHbWZzc0p1UTNpZVovNFo2TW1TRGxOMVRreFRoREFYNGo5OGdFekduSnc3WHBjejNFZwpNb25xTVA3TTBMVksxTzhUSG9ZQUQxaGZPREw2Z245OGcvYjFsZzhCM1E3aHJ4SGgrbWEzV0NRaG5iT3BhRHEvClJWMFV6d0lEQVFBQm8xWXdWREFPQmdOVkhROEJBZjhFQkFNQ0JhQXdFd1lEVlIwbEJBd3dDZ1lJS3dZQkJRVUgKQXdJd0RBWURWUjBUQVFIL0JBSXdBREFmQmdOVkhTTUVHREFXZ0JUSVVMdmZnRWkza1ZDSmt4ejk1cUowc3hBagpLekFOQmdrcWhraUc5dzBCQVFzRkFBT0NBUUVBSzhWUGRuOEFzRFFjV3c1OFpaNFI2cnJCRlJ6enErR0VGZXlxCkZZVGRXdWRoYUdKZnczTTlwMUI3Sy80SGpKKytKTzl6ZkhCby9CZmNSbXgrbUZqV2haeTNFZkgrZTVaK2xEU0IKbEl1dVBOTG10SDdEV1o3ekcvL3lTL3pWT25Md2dlT1V0OHdHMEFudEVaTGkyS3Q1bm9zTTBHM2hrc0RxeTFiVQphSGlURGJTclVpUWVGRk1mTWoxSTRxMmx0cXlQODZwV1ZEb0k1NXI0c1Jnd05MZkYwakJtNE9CQlllWjlhWXUvCk1EbjlEWTZLbk1NZ2Y0cXg4QzBwaU1qWElpZ2RCajZBK3lXUUtDQlZqa2xzdmx3V04yZk43TFhXUHM3RXphcDYKUmpvMVkxVXJQUlpXV1BwNDBLMytRQndFVGpOUU0ydW90bGRNRDZHb0hySkdSemJ3Wnc9PQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
client-key-data: LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBd1lWOENYSnh2UndFcWZUazFCeEUrSjM2YzBVVmdHdWUzZmttTWcvZVZ0eGlxOGt5CkZxU25BNmJIOElkWjhxdGdpN3JxK2JKQkhMb0NsK2dXTUR5YW1UT1pHcUpnOWFUZGtWSUFzTG0vNE12Ym01NGcKSEovbDdSNkx4dDEvbnhjWjJtcXN2NWZCYXlGRjdkbS91R1VGa0RTNzJmOUpDT1MyYjFqN2IycnFLZ0JRck04bQppT0pMeU56UVBMQWtLek5ML2RVT2NGT2tuVkNGRGI1Q0UxaUFNVWM1SEcvMndoR21mc3NKdVEzaWVaLzRaNk1tClNEbE4xVGt4VGhEQVg0ajk4Z0V6R25KdzdYcGN6M0VnTW9ucU1QN00wTFZLMU84VEhvWUFEMWhmT0RMNmduOTgKZy9iMWxnOEIzUTdocnhIaCttYTNXQ1FobmJPcGFEcS9SVjBVendJREFRQUJBb0lCQUdXNTExUFg5dlhqam9nUQpsV0R5WTBjVk5CdjN5cSt3NHRmb0tpM1NyWnVYU2I3bmlnN2hDbkllNzZiK1gwZnkwbE5oTkRlQmZqeXRnc043ClduNk12TytmY2ZIUVBZdWkyRjJWYjR0MmVPaWdBSmF5N2twZHV5MkVDeEhFU1Z2RmR1K2JkNmRYREhOV0VENVIKWWpoNTBnelZ5NUZ5WWwvc2FnSHFFbkdsRCtaM1RINmEyQklNdytudktuQldxWDJ2dFdJL3JPdytNcS9ONHlJTQpTK2ZCQ3NQSU5DUFJPbzZ4NHhVQllpOERKR1AxRVdVVDlPOGtYcjFPMDdOSnJPcC82bDJnMy84SHdoOGIxVTdXCkNTaDJ0aGZrMllWOWs5UkU4cUFGb2ZzcTF0OUF0amZKM05SeDk5dm5QUm5DNHB3dm9pVlVQdlBtSnpDRkV2N1oKNXQ5RVhTRUNnWUVBK0xYYWFKMVg0dW14Yy9WQmM1dlo2b2lkSjZ5ZkdQT2t1blRSd2FSNTF0NjNwRER2YTFiMQprclltZzNpUWl2Qk80bVhpWnJ0WEN5ZXI3S1E3eGp6bHA0dmtYMXJvaEdKS0xxYmM3SmtOOFZxdUNaL29yNlNhCmNKVnU4UmlzVDJXaEsrb2JaRjdPWlpQVk5nemc2SWkwcFc5cnAwZWZwUEtLQ0RTMlUvRExVZWNDZ1lFQXh6R0kKVlNLd0VnNlNUcjVLbXhFV0pzQzVsRjZYQmNGTUxTblZiNStuc291Mm9BV1RNWnR3SDh6ekFKK29JbWszOVh6SgpUd2t5SFpIU2hLaXBsOUl5dExlZlFvZjRtOGJKSDQ4V2U2SHRTcUkvR0lMeTZUT0JYUDBLMjB3QkdrRkxvY3dRCjVENk5SK1lOeS92dkMxVklPQS92TDVJMkJaTE5PSHU1d3U4UkdOa0NnWUVBbWFscHJ0Yi8xTStEOXR2aHUzYmcKTlhxQWRtRzl6bUhDTmYwMUY0bnlTU0pEbmVzcUVVeWgzeW94TTJ0TENyeWNVRjZZZWRabldob0JxK3h3amZOVQpCS2QyeXI5VkIyM2UzV0gwL3kwMUl4aGVqTTNDcXJwdFBQL21rb2ttOU1zYXdCSWRLRzgyNENWdFJyN0FPb3N6CjZUNms2YTVqNFRxRXM3czFwemtQdGFNQ2dZQTBteVJDTjdNQVVkRFo4dStKSEc0Wk5mVE05bDQwS3VTUFdPa0IKWGN6UUhvM1FuU2hPaFpxTEMzbHh4TGlHdmZzRlhqdGNJRFdZRVpiamFoZS8vTWRmYXM4b3B2aEZTNjU2SXpQdwoyc2JzV3dVRzJDNkc0QTllRzRYdWZKZ2Q4dmlpZGw1UHFTVnV3NWNKTkRQaGJsaHdWZVQ1VDBmdEdPUVI4cnNRCmZFcXJvUUtCZ0JGaU8vNlhCaTFEMjU5c3hPUTh6NUFHcGpJRnQ3a2crUExiUEhvL0VGR1A3QlYxRjNDSjk1QzIKNEJVT1dka0hleCtnQTROZ0MvdEZQbEl2dEVmUGthZk5JUWo4TmVoRmM5Y0NLcVJyK2pzVzAvczRhNVRqM05VaQpKek1OWXVaQXJDdXVNTDlxeWVxRENMQWdVNzJMVFJuZDVHUWlWa09SMHMveEpRZjlZdDJBCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0tCg==
    token: YWRtaW4tdG9rZW4tMTcxNDI5MDY4Ng==

```

```pepeline
pipeline {
    agent any
    environment {
        KUBECONFIG = '/var/lib/jenkins/k8s.yaml' // Kubernetes 配置文件的路徑
        NAMESPACE = 'default' // 要部署的 Kubernetes 命名空間
        NGINX_IMAGE = 'docker.io/nginx:latest' // 使用的 Nginx 鏡像
        BUILD_NUMBER = "${BUILD_NUMBER}" // Jenkins 構建編號
        NGINX_NAME = "nginx-${BUILD_NUMBER}" // Nginx 部署和服務的名稱
        SERVICE_NAME = "nginx-svc-${BUILD_NUMBER}" // 服務的名稱
        PORT = 80 // 暴露的端口號
        HTML_CONTENT = "<h1>Hello from Jenkins Build #${BUILD_NUMBER}</h1>" // 帶有構建編號的 HTML 內容
        DEPLOYMENT_YAML = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${NGINX_NAME}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-${BUILD_NUMBER}
  template:
    metadata:
      labels:
        app: nginx-${BUILD_NUMBER}
    spec:
      containers:
      - name: nginx
        image: ${NGINX_IMAGE}
        ports:
        - containerPort: ${PORT}
        volumeMounts:
        - name: nginx-html
          mountPath: /usr/share/nginx/html
          readOnly: true
      volumes:
      - name: nginx-html
        configMap:
          name: nginx-html-${BUILD_NUMBER}
"""
    }
    stages {
        stage('Deploy Nginx') {
            steps {
                script {
                    // 刪除現有的 ConfigMap（如果存在）
                    sh "kubectl --kubeconfig ${KUBECONFIG} delete configmap nginx-html-${BUILD_NUMBER} --namespace=${NAMESPACE} --ignore-not-found"
                    // 使用 HTML 內容創建 ConfigMap
                    sh "kubectl --kubeconfig ${KUBECONFIG} create configmap nginx-html-${BUILD_NUMBER} --from-literal=index.html='${HTML_CONTENT}' --namespace=${NAMESPACE}"
                    // 應用部署 YAML
                    sh "echo '''${DEPLOYMENT_YAML}''' > nginx-deployment.yaml"
                    sh "kubectl --kubeconfig ${KUBECONFIG} apply -f nginx-deployment.yaml --namespace=${NAMESPACE}"
                    // 將 Nginx 部署暴露為服務
                    sh "kubectl --kubeconfig ${KUBECONFIG} expose deployment ${NGINX_NAME} --name=${SERVICE_NAME} --port=${PORT} --namespace=${NAMESPACE}"
                }
            }
        }
    }
}

```
遇到太多服務和pod要刪除可以透過下列指令
```
 kubectl delete services 
 kubectl delete pod <pod-name> --namespace=default
```

```
mkdir /usr/share/nginx/
mkdir /usr/share/nginx/html
```
準備就緒後就可以透過svc 去觀察是否啟動
```
kubectl get svc
kubectl get pods
```
![image](https://hackmd.io/_uploads/SyH5hiiWC.png)

