---
title: "自定義 Object_detection tensorflow 複習"
date: "2019-03-31T12:24:00.000+08:00"
updated: "2019-06-22T20:02:33.933+08:00"
permalink: "/2019/03/objectdetection-tensorflow.html"
original_url: "https://x8795278.blogspot.com/2019/03/objectdetection-tensorflow.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-590545939667942123"
tags: ["Python", "TensorFlow", "Tutorial"]
layout: post
---

[![](https://i.imgur.com/iw9jDg5.png)](https://i.imgur.com/iw9jDg5.png)
  

自定義 Object_detection   

  
## ---

朋友台中面試題目呢嗯嗯嗯，上一次電腦硬碟掛掉掛電今天來重寫一份，如何自定義 訓練
[Object_detectio](https://www.youtube.com/watch?v=Rgpfk6eYxJA)，那麼首先又是複雜的環境設定 今天目標  RUN起這份 source code
[TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10#1-install-tensorflow-gpu-15-skip-this-step-if-tensorflow-gpu-15-is-already-installed](https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10#1-install-tensorflow-gpu-15-skip-this-step-if-tensorflow-gpu-15-is-already-installed)

  

前置作業
## ---

額 由於呢，這份 source code 年代有點久遠，那麼大概會分成這幾個步驟  

  

1. Download anconda
2. git clone  [https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10.git](https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10#1-install-tensorflow-gpu-15-skip-this-step-if-tensorflow-gpu-15-is-already-installed)
3. Download tensorflow model
4. Download Faster-rcnn-inception-v2-coco model
5. folder  setting
6. Environment setting
7. Labelimg
8. Configure training
9. Training
10. python  Object_detection_webcam.py

Download [Anconda](https://www.anaconda.com/)
## ---

[![](https://i.imgur.com/szvxVNw.png)](https://i.imgur.com/szvxVNw.png)
  

自己去官網下載!  

  

Download tensorflow model
## ---

有裝過 git 的話 直接git clone 就可以了，沒有的話則  

[![](https://i.imgur.com/dExUWPe.png)](https://i.imgur.com/dExUWPe.png)

Download tensorflow model
## ---

作者的 github 的預設連結是連到 最新 model 版本，這邊我用 作者的方法run 不起來所以我去翻找 一個更久以前的model  

<https://github.com/Rmuli/models>，這邊作者有說到，在新的版本的model的話train.py的這個文件可以在legacy，被找到 不過，ㄏㄏ除了這個我還有其他函式會被衝突因為，不知是否是我使用的環境問題，還是pyhton 版本，先download  

  

Download Faster-rcnn-inception-v2-coco model
## ---

這邊的話，是該次主要訓練的 model設定，詳細看[github](https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10#1-install-tensorflow-gpu-15-skip-this-step-if-tensorflow-gpu-15-is-already-installed)  

  

Foldder setting
## ---

這邊我覺得我有點看不懂再說什麼，可能我英文真的濫倒爆炸，  

上述下載的檔案有三個  

分別是  

  

  

- github <https://github.com/EdjeElectronics/TensorFlow-Object-Detection-API-Tutorial-Train-Multiple-Objects-Windows-10.git>
- tensorflow model
- Faster-rcnn-inception-v2-coco model

  

那麼我來放置一下官網的設定
我們將在
C:\tensorflow1\models
[![](https://i.imgur.com/0qeNGdC.png)](https://i.imgur.com/0qeNGdC.png)
這邊就是放置  

- tensorflow model

然後research裡面! 的object_detection  

[![](https://i.imgur.com/qBnwlFr.png)](https://i.imgur.com/qBnwlFr.png)

完成!

Anconda Environment setting
## ---

在這邊的話就照官網  
#### 2d. Set up new Anaconda virtual environment

Next, we'll work on setting up a virtual environment in Anaconda for tensorflow-gpu. From the Start menu in Windows, search for the Anaconda Prompt utility, right click on it, and click “Run as Administrator”. If Windows asks you if you would like to allow it to make changes to your computer, click Yes.
In the command terminal that pops up, create a new virtual environment called “tensorflow1” by issuing the following command:
**這邊意思大概就是開一個環境裡面的pyhton 版本是3.5**

```
C:\> conda create -n tensorflow1 pip python=3.5
```

Then, activate the environment by issuing:
[![](https://i.imgur.com/PQbjRJV.png)](https://i.imgur.com/PQbjRJV.png)
  

  

```
C:\> activate tensorflow1
```

**啟動環境的一個概念，docker?**

  

Install tensorflow-gpu in this environment by issuing:
**這邊安裝 tensorflow 的步驟省略看下一章安裝**

```
(tensorflow1) C:\> pip install --ignore-installed --upgrade tensorflow-gpu
```
  

Install the other necessary packages by issuing the following commands:
  

這邊可以看到 conda 很方便的是它可以幫你把你的套件，自動匹配相對應的lib 不用再為 包安裝的很辛苦!  
```
(tensorflow1) C:\> conda install -c anaconda protobuf
(tensorflow1) C:\> pip install pillow
(tensorflow1) C:\> pip install lxml
(tensorflow1) C:\> pip install Cython
(tensorflow1) C:\> pip install jupyter
(tensorflow1) C:\> pip install matplotlib
(tensorflow1) C:\> pip install pandas
(tensorflow1) C:\> pip install opencv-python
```
(Note: The ‘pandas’ and ‘opencv-python’ packages are not needed by TensorFlow, but they are used in the Python scripts to generate TFRecords and to work with images, videos, and webcam feeds.)
#### 2e. Configure PYTHONPATH environment variable

**這邊可能是 tensorflow 需要抓到 models 的系統環境變數，每次 都要重新設定**
A PYTHONPATH variable must be created that points to the \models, \models\research, and \models\research\slim directories. Do this by issuing the following commands (from any directory):
```
(tensorflow1) C:\> set PYTHONPATH=C:\tensorflow1\models;C:\tensorflow1\models\research;C:\tensorflow1\models\research\slim
```
(Note: Every time the "tensorflow1" virtual environment is exited, the PYTHONPATH variable is reset and needs to be set up again.)
#### 2f. Compile Protobufs and run setup.py

Next, compile the Protobuf files, which are used by TensorFlow to configure model and training parameters. Unfortunately, the short protoc compilation command posted on TensorFlow’s Object Detection API [installation page](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/installation.md) does not work on Windows. Every .proto file in the \object_detection\protos directory must be called out individually by the command.
In the Anaconda Command Prompt, change directories to the \models\research directory and copy and paste the following command into the command line and press Enter:
**嗯嗯嗯  等級不夠以後再來研究**
```
protoc --python_out=. .\object_detection\protos\anchor_generator.proto .\object_detection\protos\argmax_matcher.proto .\object_detection\protos\bipartite_matcher.proto .\object_detection\protos\box_coder.proto .\object_detection\protos\box_predictor.proto .\object_detection\protos\eval.proto .\object_detection\protos\faster_rcnn.proto .\object_detection\protos\faster_rcnn_box_coder.proto .\object_detection\protos\grid_anchor_generator.proto .\object_detection\protos\hyperparams.proto .\object_detection\protos\image_resizer.proto .\object_detection\protos\input_reader.proto .\object_detection\protos\losses.proto .\object_detection\protos\matcher.proto .\object_detection\protos\mean_stddev_box_coder.proto .\object_detection\protos\model.proto .\object_detection\protos\optimizer.proto .\object_detection\protos\pipeline.proto .\object_detection\protos\post_processing.proto .\object_detection\protos\preprocessor.proto .\object_detection\protos\region_similarity_calculator.proto .\object_detection\protos\square_box_coder.proto .\object_detection\protos\ssd.proto .\object_detection\protos\ssd_anchor_generator.proto .\object_detection\protos\string_int_label_map.proto .\object_detection\protos\train.proto .\object_detection\protos\keypoint_box_coder.proto .\object_detection\protos\multiscale_anchor_generator.proto .\object_detection\protos\graph_rewriter.proto
```
This creates a name_pb2.py file from every name.proto file in the \object_detection\protos folder.
(Note: TensorFlow occassionally adds new .proto files to the \protos folder. If you get an error saying ImportError: cannot import name 'something_something_pb2' , you may need to update the protoc command to include the new .proto files.)
Finally, run the following commands from the C:\tensorflow1\models\research directory:
```
(tensorflow1) C:\tensorflow1\models\research> python setup.py build
(tensorflow1) C:\tensorflow1\models\research> python setup.py install
```

Anconda install tensorflow-gpu
## ---

額 由於呢，這份 source code 年代有點久遠，tensorflow 照他的流程 我會一一走下去  

不知道為什麼我按照他的指令下會更新到很舊的版本，反正我們強制指定
  

```
pip install tensorflow-gpu==1.5
```

  

這邊呢跟以前我發過的教學一樣，
  

選 windows 10  
1.5版（含以上）請參考：  

  

 [CUDA 9.0](https://developer.nvidia.com/cuda-90-download-archive?target_os=Windows&target_arch=x86_64&target_version=10&target_type=exelocal)  

[![](https://i.imgur.com/7UGiD1f.png)](https://i.imgur.com/7UGiD1f.png)
在CUDA 9.0 安裝過程中 有衝突的話 在安裝前 把推薦 選 自定義，把失敗的給勾掉就ok了!

[cuDNN 7.0](https://developer.nvidia.com/rdp/cudnn-download) 是需要加入nvdia 社群的 所以嗯嗯自己去加  

  

[![](https://i.imgur.com/BpnqQ1r.png)](https://i.imgur.com/BpnqQ1r.png)
  

下載玩呢先把 CUDA9.0給安裝完，再把 cudnn 解壓縮的東西 丟到
[![](https://i.imgur.com/4siNYbC.png)](https://i.imgur.com/4siNYbC.png)
  
```
C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v9.0
```
  

[![](https://i.imgur.com/1jBRctR.png)](https://i.imgur.com/1jBRctR.png)
  

完整的丟過去，嗯嗯 打開Anaconda Prompt
切去tensorflow1環境
```
import tensorflow as tf
hello = tf.constant('Hello, TensorFlow!')
sess = tf.Session()
print(sess.run(hello))
```
[![](https://i.imgur.com/44v4i3m.png)](https://i.imgur.com/44v4i3m.png)
  

labelimg
## ---

[![](https://i.imgur.com/ARWEDDl.png)](https://i.imgur.com/ARWEDDl.png)
  

  

  

大大門常常說的標記資料，就是這麼一回事，像google v2的驗證碼?標記完資料呢  

  
```
python generate_tfrecord.py --csv_input=images\train_labels.csv --image_dir=images\train --output_path=train.record
python generate_tfrecord.py --csv_input=images\test_labels.csv --image_dir=images\test --output_path=test.record
```
  

這兩行沒記錯的話應該是產生 像對應 資料集，並打亂?  

  

[![](https://i.imgur.com/87ptayd.png)](https://i.imgur.com/87ptayd.png)
  

  

後面的話 label map 則是， 根據你所標記的  資料集也就是

  

[![](https://i.imgur.com/FC5gFec.png)](https://i.imgur.com/FC5gFec.png)
返回的結果，進行 話框框 並 標註 類似
  

[![](https://i.imgur.com/udTwhgk.png)](https://i.imgur.com/udTwhgk.png)
  

那麼開始進行 training
Configure training
## ---

這邊跟官網比較不同的話，我可能是環境比較特殊，大家可以先做官網的教學不能再，可能情況像我一樣就學我修改
[![](https://i.imgur.com/5fV6qbT.png)](https://i.imgur.com/5fV6qbT.png)
下面兩個配置 倒是沒什麼問題
[![](https://i.imgur.com/QB83UZl.png)](https://i.imgur.com/QB83UZl.png)
  

我 <=====有問題的是這邊，請注意反斜線 和訓練 rate

[![](https://i.imgur.com/syOvv9n.png)](https://i.imgur.com/syOvv9n.png)
  

新的model，或者中間有更新，好像不支援 三個schedule 這樣子，這應該是 預計要訓練到 什麼時候
[![](https://i.imgur.com/kSWe7KC.png)](https://i.imgur.com/kSWe7KC.png)
就是裡面的loss，應該是每隔 幾萬步 學習 rate 就會再下降一點點，這邊的話可能要去找 周末凡老師 上一下課，反正就是，用下山來說，你每次都跨很大步，你以為是最佳路徑，而忽略鄉間小道可以更快下山，或者是 每次都走很小步，其實你很快就可以下山，這樣比喻會不會太籠統ㄏㄏ，是這樣嗎，這要視情況而定，各有利弊，這邊攸關訓練的時間哈哈，在其他種狀況，可能訓練跨太大步會梯度爆炸，攸關 你的 訓練模型，要自己寫的話還要考慮到，啟用函式等等，嗯嗯以後再來整理一下
[![](https://i.imgur.com/VrypeRb.png)](https://i.imgur.com/VrypeRb.png)
這邊照他說的，比較快一點的作法就是，先下載他的訓練包 也就是 Faster-rcnn-inception-v2-coco model  和作者 github 專案放置相對應位置，做到這邊的話， 那就大功告成囉
準備來訓練
  

Training!
## ---

```
python train.py --logtostderr --train_dir=training/ --pipeline_config_path=training/faster_rcnn_inception_v2_pets.config
```

沒意外的話 大概兩個小時  

[![](https://i.imgur.com/wRqpJT2.png)](https://i.imgur.com/wRqpJT2.png)
要看實際狀態可以用，不過我的 tensorboard 壞掉了，可以觀看學習曲線
[![](https://i.imgur.com/q0U7klK.png)](https://i.imgur.com/q0U7klK.png)
  
```
tensorboard --logdir=training
```
  

兩個小時 到了， 恩恩這邊的話，不爽等可以直接 ctrl - c
訓練完呢
  

接下來要產生 辨識模型
[![](https://i.imgur.com/CXPERzY.png)](https://i.imgur.com/CXPERzY.png)
  

```
python export_inference_graph.py --input_type image_tensor --pipeline_config_path training/faster_rcnn_inception_v2_pets.config --trained_checkpoint_prefix training/model.ckpt-XXXX --output_directory inference_graph
```

這邊我有遇到一個 bug
```
C:\tensorflow1\models\research\object_detection\utils\learning_schedules.py
```

[![](https://i.imgur.com/6RHg79B.png)](https://i.imgur.com/6RHg79B.png)
必須設定為
```
[i for i in range(num_boundaries)]
```

[![](https://i.imgur.com/4pRKxja.png)](https://i.imgur.com/4pRKxja.png)
  

裡面的 23419 目前中斷的地方為 23419 嗯嗯這樣的話會在 上一層的產生 辨識模型
```
python export_inference_graph.py --input_type image_tensor --pipeline_config_path training/faster_rcnn_inception_v2_pets.config --trained_checkpoint_prefix training/model.ckpt-XXXX --output_directory inference_graph
```

[![](https://i.imgur.com/CTRbFWG.png)](https://i.imgur.com/CTRbFWG.png)
好囉!  終於產生完模型
  

python object_detection webcam.py
## ---

對的，到了最後一步，先來運行一下， 兩小時而已，有點久，晚一點來發 yolo 物體辨識模型!

[![](https://i.imgur.com/iw9jDg5.png)](https://i.imgur.com/iw9jDg5.png)
