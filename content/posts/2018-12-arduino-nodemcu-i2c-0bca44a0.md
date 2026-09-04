---
title: "arduino 與 nodemcu 透過i2c溝通"
date: "2017-03-06T23:30:00.000+08:00"
updated: "2018-12-06T23:36:44.984+08:00"
permalink: "/2018/12/arduino-nodemcu-i2c.html"
original_url: "https://x8795278.blogspot.com/2018/12/arduino-nodemcu-i2c.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-240884333457905351"
tags: ["arduino", "Embedded", "esp8266", "lua", "nodemcu", "Tutorial"]
layout: post
---

## 程式碼

## ---

**`arduino_i2c.ino`**

```cpp
#include <Wire.h>
const byte SLAVE_ADDRESS = 0x15;
void setup() {
  Wire.begin(0x15);                // join i2c bus with address #8
  Wire.onReceive(receiveEvent); // register event
  Serial.begin(9600);           // start serial for output
}

void loop() {
  delay(100);
}

// function that executes whenever data is received from master
// this function is registered as an event, see setup()
void receiveEvent(int howMany) {
  while (1 < Wire.available()) { // loop through all but the last
    char c = Wire.read(); // receive byte as a character
    Serial.print(c);         // print the character
  }
  int x = Wire.read();    // receive byte as an integer
  Serial.println(x);         // print the integer
}
```

**`nodemcu_i2c.lua`**

```lua
id=0
sda=1
scl=2
ARDUINO_I2C = 0x15
tmp=0
i2c.setup(id,sda,scl,i2c.SLOW)

print("I2C demo")
while 1 do
       i2c.start(id)
       i2c.address(id, 0x15,i2c.TRANSMITTER)
        i2c.write(id,tmp)
         i2c.stop(id)
        print("write",tmp)
        tmr.delay(1000000)
                if tmp ==34 then
        tmp=0
        else
         tmp=tmp+1
        end
       

end
```
