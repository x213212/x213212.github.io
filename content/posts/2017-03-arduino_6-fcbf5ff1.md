---
title: "nodemcu 接受紅外線控制"
date: "2017-03-06T23:25:00.000+08:00"
updated: "2019-09-13T08:56:03.267+08:00"
permalink: "/2017/03/arduino_6.html"
original_url: "https://x8795278.blogspot.com/2017/03/arduino_6.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3396742455982605238"
tags: ["Embedded", "esp8266", "IR Remote", "nodemcu", "Tutorial"]
layout: post
---

##

##

##

## 電路圖

##

##

## ---

[![](https://i.imgur.com/NQWYOrM.jpg)](https://i.imgur.com/NQWYOrM.jpg)
## 程式碼

## ---

```cpp
/*
 * IRremoteESP8266: IRrecvDemo - demonstrates receiving IR codes with IRrecv
 * An IR detector/demodulator must be connected to the input RECV_PIN.
 * Version 0.1 Sept, 2015
 * Based on Ken Shirriff's IrsendDemo Version 0.1 July, 2009, Copyright 2009 Ken Shirriff, http://arcfn.com
 */

#include <IRremoteESP8266.h>

int RECV_PIN = 2; //an IR detector/demodulatord is connected to GPIO pin 2
int tmp=255;

IRrecv irrecv(RECV_PIN);

decode_results results;
int counter=0;
void setup()
{
  Serial.begin(9600);
  irrecv.enableIRIn(); // Start the receiver
 pinMode(16, OUTPUT);
  pinMode(5, OUTPUT);
    pinMode(4, OUTPUT);

}

void loop() {
  if (irrecv.decode(&results)) {
      counter++;

if(counter==1)
{
      Serial.println(results.value, HEX);


if(results.value==2780520712){
   digitalWrite(16, tmp);
  digitalWrite(5, 0);
    digitalWrite(4, 0);}
if(results.value==1275988228){
     digitalWrite(16,0);
  digitalWrite(5, tmp);
    digitalWrite(4, 0);}
if(results.value==1440861668){
     digitalWrite(16, 0);
  digitalWrite(5, 0);
    digitalWrite(4, tmp);}
        Serial.println("44444");
  }
      else  if(counter==3)
  {counter=0;}


    irrecv.resume(); // Receive the next value
  }

}
```
