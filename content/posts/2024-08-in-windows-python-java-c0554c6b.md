---
title: "in windows python 與 java 溝通"
date: "2024-08-21T00:31:00.002+08:00"
updated: "2024-08-21T02:19:20.096+08:00"
permalink: "/2024/08/in-windows-python-java.html"
original_url: "https://x8795278.blogspot.com/2024/08/in-windows-python-java.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-6551743725558593010"
tags: ["Java", "Python", "sharedmemory"]
layout: post
---

![](https://hackmd.io/_uploads/Hyfaj4GiR.png)

# in windows python 與 java 溝通
https://github.com/java-native-access/jna

Maven Central jna-platform-5.14.0.jar jna-platform-jpms-5.14.0.jar

# SharedMemoryWriter
build command : javac -cp jna-jpms-5.14.0.jar;jna-platform-5.14.0.jar SharedMemoryWriter.java
run command: java -cp .;jna-jpms-5.14.0.jar;jna-platform-5.14.0.jar SharedMemoryWriter

```java
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import com.sun.jna.platform.win32.Kernel32;
import com.sun.jna.platform.win32.WinNT.HANDLE;
import com.sun.jna.win32.W32APIOptions;

public class SharedMemoryWriter {

    public static void main(String[] args) {
        String shmName = "MySharedMemory";
        int shmSize = 1024; 

        Kernel32 kernel32 = Native.load("kernel32", Kernel32.class, W32APIOptions.DEFAULT_OPTIONS);
        HANDLE hMapFile = kernel32.CreateFileMapping(
                Kernel32.INVALID_HANDLE_VALUE, 
                null, 
                Kernel32.PAGE_READWRITE, 
                0, 
                shmSize, 
                shmName);

        if (hMapFile == null || Kernel32.INVALID_HANDLE_VALUE.equals(hMapFile)) {
            System.out.println("Could not create or open file mapping object");
            return;
        }

        Pointer pBuf = kernel32.MapViewOfFile(hMapFile, Kernel32.FILE_MAP_WRITE, 0, 0, shmSize);

        if (pBuf == null) {
            System.out.println("Could not map view of file");
            kernel32.CloseHandle(hMapFile);
            return;
        }

        String message = "Hello from Java!";
        pBuf.setString(0, message);

        System.out.println("Message written to shared memory: " + message);

        kernel32.UnmapViewOfFile(pBuf);
        kernel32.CloseHandle(hMapFile);
    }
}

```

# Received message
run command: python test.py
```python
import mmap
import time

shm_name = "MySharedMemory"
shm_size = 1024  

shm = mmap.mmap(-1, shm_size, tagname=shm_name)

print("Waiting for message...")

while True:
    shm.seek(0) 
    message = shm.read(shm_size).decode().strip('\x00')
    if message:
        print(f"Received message: {message}")
        
        shm.seek(0)
        shm.write(b'\x00' * shm_size)
    time.sleep(1)  

```

![image](https://hackmd.io/_uploads/Hyfaj4GiR.png)
![image](https://hackmd.io/_uploads/Bk5aj4zs0.png)

# 來用一下以前的windows api 發送
```python
import ctypes
import threading
import time
from ctypes import wintypes

WM_USER = 0x0400
NULL = 0

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def message_loop():
    msg = wintypes.MSG()
    thread_id = kernel32.GetCurrentThreadId()
    print(f"Python thread ID: {thread_id}")

    while True:
        if user32.GetMessageW(ctypes.byref(msg), NULL, 0, 0) > 0:
            if msg.message == WM_USER:
                print(f"Received message: {msg.wParam}")
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

thread = threading.Thread(target=message_loop, daemon=True)
thread.start()

print("Waiting for messages...")
thread.join()

```

```java
import com.sun.jna.Native;
import com.sun.jna.Pointer;
import com.sun.jna.platform.win32.WinDef.*;
import com.sun.jna.win32.StdCallLibrary;
import com.sun.jna.win32.W32APIOptions;
import java.util.Scanner;

public class PostMessageSender {

 
    public interface MyUser32 extends StdCallLibrary {
        MyUser32 INSTANCE = Native.load("user32", MyUser32.class, W32APIOptions.DEFAULT_OPTIONS);
        
        boolean PostThreadMessage(DWORD idThread, int msg, WPARAM wParam, LPARAM lParam);
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.print("Enter Python thread ID: ");
        int pythonThreadId = scanner.nextInt(); 

        MyUser32 user32 = MyUser32.INSTANCE;

  
        DWORD threadId = new DWORD(pythonThreadId);
        int message = 123; 
        boolean result = user32.PostThreadMessage(threadId, 0x0400, new WPARAM(message), new LPARAM(0));

        if (result) {
            System.out.println("Message sent successfully");
        } else {
            System.out.println("Failed to send message");
        }
    }
}

```
![image](https://hackmd.io/_uploads/SynGEBfiC.png)
![image](https://hackmd.io/_uploads/r1-SNBGsR.png)

