---
title: "使用 CircleCI 部署 Node.jS App 到 GCP App Engine CICD (二)"
date: "2020-07-05T08:03:00.008+08:00"
updated: "2020-07-07T08:51:34.861+08:00"
permalink: "/2020/07/circleci-nodejs-app-gcp-app-engine-cd.html"
original_url: "https://x8795278.blogspot.com/2020/07/circleci-nodejs-app-gcp-app-engine-cd.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-3736559944491785953"
tags: ["CircleCI", "Tutorial"]
layout: post
---

![](https://nplll-static.s3-ap-northeast-1.amazonaws.com/assets/2019/06/circleci.png)

# 使用 CircleCI 部署 Node.jS App 到 GCP App Engine (二)

# GCP
我們將使用功能十分強大的 Google App Engine(GAE)進行部署，GAE 在處理大流量(load)時，例如訂票系統或是物流系統時非常適合。不但不用自己管理 load balance 的問題。Google 還會幫你自動開關 instances，使用者付費原則，用多少就付多少。
因為 GAE 是 Google Cloud Platform（GCP）下的一個服務所以若還沒有 GCP 先註冊註起來！新註冊的人可以享有一年 300 美金的試用，注意註冊時需要輸入一張信用卡才能開始使用，在試用階段 Google 並不會為向你收費，除非你主動跟他說要訂閱方案才會開啟收費流程。
註冊完後我們就能夠開始使用 GCP 了，進到 Google App Engine(GAE) 畫面，接下來點擊 建立應用程式。

![](https://i.imgur.com/HobeZCM.png)

# 部屬
# add  app.yaml
```yaml
runtime: nodejs # Name of the App Engine language runtime used by this application
env: flex # Select the flexible environment

manual_scaling: # Enable manual scaling for a service
  instances: 1 # 1 instance assigned to the service

resources: # Control the computing resources
  cpu: 1
  memory_gb: 0.5
  disk_size_gb: 10

skip_files: # Specifies which files in the application directory are not to be uploaded to App Engine
# We just need build/server.js to deploy
  - node_modules/
  - .gitignore
  - .git/
  - .circleci/
  - src/
  - test/
  - .eslintrc.js
  - .huskyrc.js
  - .eslintignore
  - .prettierrc
  - babel.config.js
  - lint-staged.config.js
  - nodemon.json
```

>gcloud app deploy
>
![](https://i.imgur.com/KkvBZ5M.png)

# 沒有指定 在 package.json nodejs 版本
![](https://i.imgur.com/3BlsfIl.png)

#  沒有在  package.json指定  start 指令
>...
Step #0: Application detection failed: Error: node.js checker: Neither "start" in the "scripts" section of "package.json" nor the "server.js" file were found.
>
# add package.json
```json
....
"scripts": {
    "lint": "eslint . --fix",
    "dev": "nodemon",
    "test": "jest",
    "build": "rm -rf build && babel src -d build --copy-files",
    "start": "node src\\server.js"
  }

```
![](https://i.imgur.com/rFH10Eq.png)

>rm -rf node_modules package-lock.json && npm install && npm start
>yarn install --ignore-engines
>

# bug 太多 我們升級為 babel  
# package.json
```jsonld
{
  "name": "demo-server",
  "version": "1.0.0",
  "main": "index.js",
  "license": "MIT",
  "dependencies": {
    "express": "^4.17.1",
    "format": "^0.2.2"
  },
  "devDependencies": {
    "@babel/cli": "^7.10.4",
    "@babel/core": "^7.10.4",
    "@babel/node": "^7.10.4",
    "@babel/preset-env": "^7.10.4",
    "babel-eslint": "^10.1.0",
    "babel-jest": "^26.1.0",
    "eslint": "^7.4.0",
    "eslint-config-airbnb-base": "^14.2.0",
    "eslint-config-prettier": "^6.11.0",
    "eslint-plugin-import": "^2.22.0",
    "eslint-plugin-jest": "^23.17.1",
    "eslint-plugin-prettier": "^3.1.4",
    "jest": "^26.1.0",
    "nodemon": "^2.0.4",
    "prettier": "^2.0.5",
    "supertest": "^4.0.2"
  },
  "scripts": {
    "lint": "eslint . --fix",
    "dev": "nodemon",
    "test": "jest ",
    "build": "rm -rf build && babel src -d build --copy-files",
    "start": "babel-node src/server.js"
  }
}

```
# src/server.js
```javascript
import express from 'express';

const app = express();
const { PORT = 3000 } = process.env;

const IS_TEST = !!module.parent; // If there's another file imports server.js, then module.parent will become true

app.get('/', (req, res) => {
  res.status(200).send('Hello!CI/CD!2');
});

if (!IS_TEST) {
  app.listen(PORT, () => {
    console.log('Server is running on PORT:', PORT);
  });
}

export default app;

```
# test/server.test.js
```javascript
import supertest from 'supertest';
import app from '../src/server';

const PORT = 3001;
let listener;
let request;

beforeAll(() => {
  listener = app.listen(PORT);
  request = supertest(listener);
});
afterAll(async () => {
  await listener.close();
});

test('Server Health Check', async () => {
  const res = await request.get('/');
  expect(res.status).toEqual(200);
  expect(res.text).toBe('Hello!CI/CD!2');
});

test('Server Health Check2', async () => {
  const res = await request.get('/');
  expect(res.status).toEqual(200);
  expect(res.text).toBe('Hello!CI/CD!2');
});

```
# 根目錄新增babel.config.js
```
module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: {
          node: 'current',
        },
      },
    ],
  ],
};

```
# run
測試 ok
![](https://i.imgur.com/hmYzxp7.png)

# 部屬
# add package.json
都沒說這個 找有夠久
```jsonld
.....
    "start": "node build/server.js"
```
![](https://i.imgur.com/SA2ZErB.png)

等到往生
![](https://i.imgur.com/JJQAjze.png)
![](https://i.imgur.com/Qgef2vB.png)

# 整合CircleCI deploy
# add config.yml
```
version: 2.1
jobs:
  build:
    docker:
      - image: circleci/node:latest
    steps:
      - checkout
      - run:
          name: Check Node.js version
          command: node -v
      - run:
          name: Install yarn
          command: 'curl -o- -L https://yarnpkg.com/install.sh | bash'
      - restore_cache:
          name: Restore dependencies from cache
          key: dependency-cache-{{ checksum "yarn.lock" }}
      - run:
          name: Install dependencies if needed
          command: |
            if [ ! -d node_modules ]; then
              yarn install --frozen-lockfile
            fi
      - save_cache:
          name: Cache dependencies
          key: dependency-cache-{{ checksum "yarn.lock" }}
          paths:
            - ./node_modules
      - run:
          name: Lint
          command: yarn eslint . --quiet
      - run:
          name: Test
          command: yarn jest --ci --maxWorkers=2
      - run:
          name: Build
          command: npm run build
      - persist_to_workspace:
          root: .
          paths:
            - build
            - package.json
            - yarn.lock
            - app.yaml
  deploy:
    docker:
      - image: google/cloud-sdk
    steps:
      - attach_workspace:
          at: .
      - run:
          name: ls
          command: ls -al
      - run:
          name: Setup gcloud env
          command: |
            echo $GCP_KEY > gcloud-service-key.json
            gcloud auth activate-service-account --key-file=gcloud-service-key.json
            gcloud --quiet config set project ${GCP_PROJECT_ID}
            gcloud --quiet config set compute/zone ${GCP_REGION}
      - run:
          name: Deploy to App Engine
          command: gcloud app deploy

workflows:
  version: 2
  build-deploy:
    jobs:
      - build
      - deploy:
          requires:
            - build
          filters:
            branches:
              only: master
```
![](https://i.imgur.com/d5q6gXZ.png)

# 填入 環境變數

進入申請金鑰 [ Cloud IAM ](https://cloud.google.com/iam/?hl=zh-tw)
![](https://i.imgur.com/2PX5sGI.png)

記得 GCP_KEY 是下載下來的 json 檔案
>GCP_KEY	xxxxm" }
GCP_PROJECT_ID	xxxx1716
GCP_REGION	xxxxt1-b
>

# 啟用App Engine Admin API
![](https://i.imgur.com/SLRntEQ.png)

![](https://i.imgur.com/C41hxky.png)

# commit 部屬一次
![](https://i.imgur.com/qvEITbn.png)
可以看到有再跑了
![](https://i.imgur.com/7OvqLF4.png)
等10分左右
![](https://i.imgur.com/E9Io8qx.png)
![](https://i.imgur.com/WttwJv4.png)

總算好囉 CD

