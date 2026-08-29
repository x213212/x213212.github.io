---
title: "初探 DEVOPS 本地 CICD 部屬 使用 Docker 快速架設 GitLab (三)"
date: "2020-07-10T07:55:00.003+08:00"
updated: "2020-07-11T11:25:15.056+08:00"
permalink: "/2020/07/blog-post.html"
original_url: "https://x8795278.blogspot.com/2020/07/blog-post.html"
blogger_id: "tag:blogger.com,1999:blog-4768376178408509094.post-665118757740147924"
tags: ["Docker", "Tutorial"]
layout: post
---

![](https://miro.medium.com/max/5064/1*YjOtv5OOEP744YTdzBxWsw.png)

# 使用 Docker 快速構建 GitLab
# .env
```
# setting gitlab
GITLAB_SERVER=172.24.229.236
GITLAB_WEB_PORT=10080
GITLAB_SSH_PORT=10022

# setting postgresql
DB_USER=gitlab
DB_PASS=x12345
DB_NAME=gitlabhq_production

```
# docker.yml
```yml
version: '2'

services:
  redis:
    restart: always
    image: sameersbn/redis:4.0.9-2
    container_name: gitlab-redis
    command:
    - --loglevel warning
    volumes:
    - ./gitlab/redis:/var/lib/redis:Z

  postgresql:
    restart: always
    image: sameersbn/postgresql:10-2
    container_name: gitlab-postgresql
    volumes:
    - ./gitlab/postgresql:/var/lib/postgresql:Z
    environment:
    - DB_USER=${DB_USER}
    - DB_PASS=${DB_PASS}
    - DB_NAME=${DB_NAME}
    - DB_EXTENSION=pg_trgm

  # default username "root"
  # default password "5iveL!fe"
  gitlab:
    restart: always
    image: sameersbn/gitlab:12.2.1-1
    container_name: gitlab-web
    extra_hosts:
     - "activate.adobe.com:172.24.229.236"
    depends_on:
    - redis
    - postgresql
    ports:
    - "${GITLAB_WEB_PORT}:80"
    - "${GITLAB_SSH_PORT}:22"
    volumes:
    - ./gitlab/gitlab:/home/git/data:Z
    environment:
    - DEBUG=false

    - DB_ADAPTER=postgresql
    - DB_HOST=postgresql
    - DB_PORT=5432
    - DB_USER=${DB_USER}
    - DB_PASS=${DB_PASS}
    - DB_NAME=${DB_NAME}

    - REDIS_HOST=redis
    - REDIS_PORT=6379

    - TZ=Asia/Kolkata
    - GITLAB_TIMEZONE=Kolkata

    - GITLAB_HTTPS=false
    - SSL_SELF_SIGNED=false

    - GITLAB_HOST=${GITLAB_SERVER}
    - GITLAB_PORT=${GITLAB_WEB_PORT}
    - GITLAB_SSH_PORT=${GITLAB_SSH_PORT}
    - GITLAB_RELATIVE_URL_ROOT=
    - GITLAB_SECRETS_DB_KEY_BASE=long-and-random-alphanumeric-string
    - GITLAB_SECRETS_SECRET_KEY_BASE=long-and-random-alphanumeric-string
    - GITLAB_SECRETS_OTP_KEY_BASE=long-and-random-alphanumeric-string

    - GITLAB_ROOT_PASSWORD=
    - GITLAB_ROOT_EMAIL=

    - GITLAB_NOTIFY_ON_BROKEN_BUILDS='true'
    - GITLAB_NOTIFY_PUSHER=false

    - GITLAB_EMAIL=notifications@example.com
    - GITLAB_EMAIL_REPLY_TO=noreply@example.com
    - GITLAB_INCOMING_EMAIL_ADDRESS=reply@example.com

    - GITLAB_BACKUP_SCHEDULE=daily
    - GITLAB_BACKUP_TIME=01:00

    - SMTP_ENABLED=false
    - SMTP_DOMAIN=www.example.com
    - SMTP_HOST=smtp.gmail.com
    - SMTP_PORT=587
    - SMTP_USER=mailer@example.com
    - SMTP_PASS=password
    - SMTP_STARTTLS='true'
    - SMTP_AUTHENTICATION=login

    - IMAP_ENABLED=false
    - IMAP_HOST=imap.gmail.com
    - IMAP_PORT=993
    - IMAP_USER=mailer@example.com
    - IMAP_PASS=password
    - IMAP_SSL='true'
    - IMAP_STARTTLS=false

    - OAUTH_ENABLED=false
    - OAUTH_AUTO_SIGN_IN_WITH_PROVIDER=
    - OAUTH_ALLOW_SSO=
    - OAUTH_BLOCK_AUTO_CREATED_USERS='true'
    - OAUTH_AUTO_LINK_LDAP_USER=false
    - OAUTH_AUTO_LINK_SAML_USER=false
    - OAUTH_EXTERNAL_PROVIDERS=

    - OAUTH_CAS3_LABEL=cas3
    - OAUTH_CAS3_SERVER=
    - OAUTH_CAS3_DISABLE_SSL_VERIFICATION=false
    - OAUTH_CAS3_LOGIN_URL=/cas/login
    - OAUTH_CAS3_VALIDATE_URL=/cas/p3/serviceValidate
    - OAUTH_CAS3_LOGOUT_URL=/cas/logout

    - OAUTH_GOOGLE_API_KEY=
    - OAUTH_GOOGLE_APP_SECRET=
    - OAUTH_GOOGLE_RESTRICT_DOMAIN=

    - OAUTH_FACEBOOK_API_KEY=
    - OAUTH_FACEBOOK_APP_SECRET=

    - OAUTH_TWITTER_API_KEY=
    - OAUTH_TWITTER_APP_SECRET=

    - OAUTH_GITHUB_API_KEY=
    - OAUTH_GITHUB_APP_SECRET=
    - OAUTH_GITHUB_URL=
    - OAUTH_GITHUB_VERIFY_SSL=

    - OAUTH_GITLAB_API_KEY=
    - OAUTH_GITLAB_APP_SECRET=

    - OAUTH_BITBUCKET_API_KEY=
    - OAUTH_BITBUCKET_APP_SECRET=

    - OAUTH_SAML_ASSERTION_CONSUMER_SERVICE_URL=
    - OAUTH_SAML_IDP_CERT_FINGERPRINT=
    - OAUTH_SAML_IDP_SSO_TARGET_URL=
    - OAUTH_SAML_ISSUER=
    - OAUTH_SAML_LABEL="Our SAML Provider"
    - OAUTH_SAML_NAME_IDENTIFIER_FORMAT=urn:oasis:names:tc:SAML:2.0:nameid-format:transient
    - OAUTH_SAML_GROUPS_ATTRIBUTE=
    - OAUTH_SAML_EXTERNAL_GROUPS=
    - OAUTH_SAML_ATTRIBUTE_STATEMENTS_EMAIL=
    - OAUTH_SAML_ATTRIBUTE_STATEMENTS_NAME=
    - OAUTH_SAML_ATTRIBUTE_STATEMENTS_USERNAME=
    - OAUTH_SAML_ATTRIBUTE_STATEMENTS_FIRST_NAME=
    - OAUTH_SAML_ATTRIBUTE_STATEMENTS_LAST_NAME=

    - OAUTH_CROWD_SERVER_URL=
    - OAUTH_CROWD_APP_NAME=
    - OAUTH_CROWD_APP_PASSWORD=

    - OAUTH_AUTH0_CLIENT_ID=
    - OAUTH_AUTH0_CLIENT_SECRET=
    - OAUTH_AUTH0_DOMAIN=

    - OAUTH_AZURE_API_KEY=
    - OAUTH_AZURE_API_SECRET=
    - OAUTH_AZURE_TENANT_ID=

```
https://www.jianshu.com/p/c2b7b5491289

![](https://i.imgur.com/jD3AZoh.png)

預設 帳號是 root
![](https://i.imgur.com/qbaDEaK.png)

去 System OAuth applications
![](https://i.imgur.com/zXP3hOQ.png)
依序輸入

* Name: 可以自行定義
* Redirect URI: 表示驗證通過後，會倒轉置 Drone的 login 頁面，需填入 http://YOUR_DRONE_HOST/login
* Scopes: 選項記得要勾選 api，使 Drone可以有權限操作GitLab API

![](https://i.imgur.com/bs8MjKO.png)
得到id和密鑰，填入我們上方 .env 檔案
![](https://i.imgur.com/Vpy3Eed.png)

