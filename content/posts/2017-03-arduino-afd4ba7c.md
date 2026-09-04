---
title: "nodemcu 溫溼度監控"
date: "2017-03-06T23:19:00.000+08:00"
updated: "2018-12-06T23:39:05.261+08:00"
permalink: "/2017/03/arduino.html"
original_url: "https://x8795278.blogspot.com/2017/03/arduino.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8125473496557507329"
tags: ["Embedded", "esp8266", "lua", "nodemcu", "Tutorial"]
layout: post
---

## 網頁

##

##

##

## ---

## [![](https://i.imgur.com/Jk3untr.png)](https://i.imgur.com/Jk3untr.png)

## 電路圖

##

##

## ---

[![](https://i.imgur.com/ND4XDv1.jpg)](https://i.imgur.com/ND4XDv1.jpg)
## 程式碼

## ---

```lua

// WiFi Weather Station
// Required libraries
#include <ESP8266WiFi.h>
// Libraries
#include <dht.h>   
// Pin
#define dht_dpin 16 //定義訊號要從Pin A0 進來  
#define  sensorPin  0
dht DHT;  
// WiFi parameters
int value = 0; 
int counter = 0;
String tmp="";
String tmp2="";
const char* ssid = "AP";
const char* password = "123456789";
// Create an instance of the server
WiFiServer server(80);
void setup() {
  // Start Serial
  Serial.begin(115200);
  delay(10);
  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
  // Start the server
  server.begin();
  Serial.println("Server started");
  // Print the IP address
  Serial.println(WiFi.localIP());
  //光敏
    pinMode(0, INPUT);
}
void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
  // Wait until the client sends some data
  Serial.println("new client");
  while(!client.available()){
    delay(1);
  }
  // Read the first line of the request
  String req = client.readStringUntil('\r');
  Serial.println(req);
  client.flush();
  counter++;
  if(counter%2==0)
  {
    value = analogRead(0);
 
     if(value<204){
  tmp2="Very bright";
Serial.println("Very bright");

}
else if (value > 204 && value <=408){
Serial.println("Ordinary bright");
  tmp2="Ordinary bright";

    
}
else if (value > 408 && value <=612){
Serial.println("Medium light");
  tmp2="Medium light";


}
else if (value > 612 && value <=816){
Serial.println("Dark");
  tmp2="Dark";


}
else if (value > 816 && value <=1020){
Serial.println("Very Dark");
  tmp2="Very Dark";
}
   Serial.println(  tmp2 );
      DHT.read11(dht_dpin);   //去library裡面找DHT.read11 
  // Prepare the response
  String s = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n";
  s += "<head>";
  s += "<meta http-equiv=\"refresh\" content=\"1\">";
  s += "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
  //s += "<meta http-equiv=\"refresh\" content=\"60\" />";
  s += "<script src=\"https://code.jquery.com/jquery-2.1.3.min.js\"></script>";
  s += "<link rel=\"stylesheet\" href=\"https://maxcdn.bootstrapcdn.com/bootstrap/3.3.4/css/bootstrap.min.css\">";
  s += "<style>body{font-size: 12px;} .voffset {margin-top: 30px;}</style>";
  s += "</head>";
  s += "<div class=\"container\">";
  s += "<h1>WiFi Weather Station</h1>";
  s += "<div class=\"row voffset\">";
  
  tmp+= "<div class=\"col-md-3\">Temperature: </div><div class=\"col-md-3\">" + String(DHT.temperature) + "&nbsp;&nbsp;&nbsp;&nbsp&nbsp;&nbsp;&nbsp;&nbsplight: "+tmp2+ "</div>";
  tmp+="<div class=\"col-md-3\">Humidity: </div><div class=\"col-md-3\">" + String(DHT.humidity) + "</div>"+"</br>";

  s += tmp;
  

  s += "</div>";
  s += "</div>";
  // Send the response to the client
  
  client.print(s);
  delay(1);
  Serial.println("Client disconnected");
  // The client will actually be disconnected
  // when the function returns and 'client' object is detroyed
  }
  if(counter>=16)
  {
    counter=0;
    tmp="";
    }
}
```
