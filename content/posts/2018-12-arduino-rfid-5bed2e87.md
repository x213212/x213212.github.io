---
title: "nodemcu RFID 門禁卡"
date: "2017-03-06T23:14:00.000+08:00"
updated: "2018-12-06T23:38:55.197+08:00"
permalink: "/2018/12/arduino-rfid.html"
original_url: "https://x8795278.blogspot.com/2018/12/arduino-rfid.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-8147664595136416272"
tags: ["Embedded", "esp8266", "lua", "nodemcu", "RFID", "Tutorial"]
layout: post
---

## 電路圖

##

##

## ---

[![](https://i.imgur.com/Zv7Vr5a.jpg)](https://i.imgur.com/Zv7Vr5a.jpg)
## 程式碼

## ---

```lua
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN D4
#define RST_PIN D8

MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class

MFRC522::MIFARE_Key key;

// Init array that will store new NUID
byte nuidPICC[4];
byte ansidPICC[4] = {0xE5, 0x0F, 0x23, 0x77};
void setup() {
  Serial.begin(9600);
  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522

  for (byte i = 0; i < 6; i++) {
    key.keyByte[i] = 0xFF;
  }

  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);

  Serial.println(F("This code scan the MIFARE Classsic NUID."));
  Serial.print(F("Using the following key:"));
  printHex(key.keyByte, MFRC522::MF_KEY_SIZE);
}

void loop() {

  // Look for new cards
  if ( ! rfid.PICC_IsNewCardPresent())
    return;

  // Verify if the NUID has been readed
  if ( ! rfid.PICC_ReadCardSerial())
    return;

  Serial.print(F("PICC type: "));
  MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
  Serial.println(rfid.PICC_GetTypeName(piccType));

  // Check is the PICC of Classic MIFARE type
  if (piccType != MFRC522::PICC_TYPE_MIFARE_MINI &&
      piccType != MFRC522::PICC_TYPE_MIFARE_1K &&
      piccType != MFRC522::PICC_TYPE_MIFARE_4K) {
    Serial.println(F("Your tag is not of type MIFARE Classic."));
    return;
  }

  if (rfid.uid.uidByte[0] != nuidPICC[0] ||
      rfid.uid.uidByte[1] != nuidPICC[1] ||
      rfid.uid.uidByte[2] != nuidPICC[2] ||
      rfid.uid.uidByte[3] != nuidPICC[3] ) {
    Serial.println(F("A new card has been detected."));

    // Store NUID into nuidPICC array
    for (byte i = 0; i < 4; i++) {
      nuidPICC[i] = rfid.uid.uidByte[i];
    }

    Serial.println(F("The NUID tag is:"));
    Serial.print(F("In hex: "));
    printHex(rfid.uid.uidByte, rfid.uid.size);
    Serial.println();
    Serial.print(F("In dec: "));
    printDec(rfid.uid.uidByte, rfid.uid.size);
    Serial.println();
  }
  else Serial.println(F("Card read previously."));

  // Halt PICC
  rfid.PICC_HaltA();

  // Stop encryption on PCD
  rfid.PCD_StopCrypto1();
}


/**
   Helper routine to dump a byte array as hex values to Serial.
*/
void printHex(byte *buffer, byte bufferSize) {
  int ans_counter = 0;
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
    if (buffer[i] == ansidPICC[i])
      ans_counter++;
  }

  if (  ans_counter == 4)
  {
    digitalWrite(D1, 1);
        digitalWrite(D3, 1);
          delay(300);
     digitalWrite(D1, 0);
        digitalWrite(D3, 0);


  }
  else if (  ans_counter == 0)
  {
    for (int i = 0; i < 2; i++) {
      digitalWrite(D2, 1);
           digitalWrite(D3, 1);
      delay(50);
      digitalWrite(D2, 0);
                   digitalWrite(D3, 0);
      delay(50);
    }

  }
}

/**
   Helper routine to dump a byte array as dec values to Serial.
*/
void printDec(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], DEC);
  }

}
```
