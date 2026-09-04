---
title: "Ardunino 倒車雷達"
date: "2017-03-01T23:05:00.000+08:00"
updated: "2018-12-06T23:38:38.535+08:00"
permalink: "/2017/03/ardunino.html"
original_url: "https://x8795278.blogspot.com/2017/03/ardunino.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2881685507961898447"
tags: ["arduino", "Embedded", "Tutorial"]
layout: post
---

## 電路圖

##

## ---

[![](https://i.imgur.com/i4Uswbl.png)](https://i.imgur.com/i4Uswbl.png)
  

  
## 影片

## ---

##

<iframe allowfullscreen="" class="YOUTUBE-iframe-video" data-thumbnail-src="https://i.ytimg.com/vi/TzS55d1RH3A/0.jpg" frameborder="0" height="266" src="https://www.youtube.com/embed/TzS55d1RH3A?feature=player_embedded" width="320"></iframe>

  
## 程式碼

##

## ---

```cpp
const int trig = 5;
const int echo = 4;
int buzzerPin = 3;//蜂鳴器
const int inter_time = 100;
int time = 0;

void setup() {
  Serial.begin(9600);
  pinMode (trig, OUTPUT);
  pinMode (echo, INPUT);
    pinMode (buzzerPin, OUTPUT); 
}

void loop() {
  float duration, distance;
  digitalWrite(trig, HIGH);
  delayMicroseconds(100);
  digitalWrite(trig, LOW);
  duration = pulseIn (echo, HIGH);
  distance = (duration/2)/29;
  Serial.print("Data:");
  Serial.print (time/100);
  Serial.print(", d = ");
  Serial.print(distance);
  if(distance<10){
     digitalWrite (buzzerPin, HIGH);
  delay (5);
  digitalWrite (buzzerPin, LOW);
  delay (5);
  }
  else
{   
  digitalWrite (buzzerPin, HIGH);
  delay (100);
  digitalWrite (buzzerPin, LOW);
  delay (100);
}
  Serial.println(" cm");
  time = time + inter_time;
  delay(inter_time);
}
```
