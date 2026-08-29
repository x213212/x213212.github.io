---
title: "python chatgpt"
date: "2023-02-06T01:39:00.002+08:00"
updated: "2023-02-06T01:39:16.660+08:00"
permalink: "/2023/02/python-chatgpt.html"
original_url: "https://x8795278.blogspot.com/2023/02/python-chatgpt.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-2357475419868934691"
tags: ["chatgpt"]
layout: post
---

![](https://i.imgur.com/PT2NwTh.png)

# chatgpt
目前收費最貴的是
https://openai.com/api/pricing/
davinci,openai已經封裝好了
https://dev.to/codemee/yong-python-chuan-jie-openai-mo-ni-chatgpt-liao-tian-ji-qi-ren-2fh6
```python
import os
import openai
import unicodedata

openai.api_key = "youkey"

prev_prompt = ''
prev_ans = ''

while True:
    # Read a message from the user
    message = input("You: ")

    # Use GPT-3 to generate a response
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prev_prompt + "\n"+ prev_ans + "\n" + message,
        max_tokens=2048,
        temperature=0.9,
    )

    # Print GPT-3's response
    print("Bot: ", response.choices[0].text)
    prev_prompt = message
    prev_ans = response.choices[0].text
```
文中也有提出了節省資料量的話就是在叫ai再重新把自己的歷史紀錄做摘要.
![](https://i.imgur.com/PT2NwTh.png)

