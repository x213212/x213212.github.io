---
title: "Google Cloud Platform 快速小紀錄 sshfs 掛載 gcp vm"
date: "2020-07-04T04:18:00.001+08:00"
updated: "2020-07-11T11:26:10.961+08:00"
permalink: "/2020/07/google-cloud-platform-sshfs-gcp-vm.html"
original_url: "https://x8795278.blogspot.com/2020/07/google-cloud-platform-sshfs-gcp-vm.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2400604708354573762"
tags: ["GCP", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/1200/1*HtV_Nxeu1POpiOmHwcv7fg.jpeg)

# install GCP Cloud Sdk
> gcloud init
>
https://cloud.google.com/sdk/docs/downloads-interactive?hl=zh-tw#mac
![](https://i.imgur.com/AH4nG62.png)
![](https://i.imgur.com/o8WKUIH.png)
![](https://i.imgur.com/Bn5DRhA.png)
![](https://i.imgur.com/ELe5AFr.png)
![](https://i.imgur.com/04rryct.png)
![](https://i.imgur.com/J1RZWxK.png)

輸入密碼
> ssh instance-1.asia-east1-b.hale-mantra-28171
>
![](https://i.imgur.com/YUsqFE9.png)

https://stackoverflow.com/questions/36984282/unable-to-mount-a-directory-on-google-compute-engine-using-sshfs

> sudo mkdir /mnt/gcp
> sudo chown x213212 /mnt/gcp
>
>
> sshfs -o IdentityFile=~/.ssh/google_compute_engine x213212@instance-1.asia-east1-b.hale-mantra-281716:/home/x213212  /mnt/gcp
>
> 安內是不行的
>
>
> sshfs -o IdentityFile=~/.ssh/google_compute_engine x213212@<把我換成 vm static ip>:/home/x213212  /mnt/gcp
>
>
>

![](https://i.imgur.com/tgY3i0i.png)

這樣就可以輕鬆 複製 我們的東西到我們 gcp 上囉

