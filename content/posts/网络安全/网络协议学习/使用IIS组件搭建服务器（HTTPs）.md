---
date: 2025-10-05T19:28:38+08:00
draft: false
title: '使用IIS组件搭建服务器（HTTPs）'
categories:
 - 网络协议学习
tags:
 - IIS
 - HTTPS
 - 服务器
author: ["云雾海"]
description: "将原本HTTP网站改为HTTPS网站"
license: CC-BY-SA 4.0
---

# 使用IIS组件搭建服务器（HTTPs）

## 目标

根据《[使用IIS组件搭建服务器（Web）](https://yunwuhai.github.io/posts/%E7%BD%91%E7%BB%9C%E5%AE%89%E5%85%A8/%E7%BD%91%E7%BB%9C%E5%8D%8F%E8%AE%AE%E5%AD%A6%E4%B9%A0/%E4%BD%BF%E7%94%A8iis%E7%BB%84%E4%BB%B6%E6%90%AD%E5%BB%BA%E6%9C%8D%E5%8A%A1%E5%99%A8web/)》，将原本HTTP网站改为HTTPS网站，注意你应该已经完成了该文章所述的所有步骤。

## 步骤

### 创建签名

因为HTTPS需要安全签名，所以我们要创建一个，如果你需要将其应用于公网，也可以自行申请一个。不过我们只是实验，创建一个本地用就够了。

1. 在IIS管理器中，选择计算机名称（不是某个网站），然后在中间的功能视图中，双击服务器证书。

   ![image-20251007161123837](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007161123837.png)

2. 在右侧选择“创建自签名证书”。

   ![image-20251007161206222](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007161206222.png)

3. 输入证书名称，然后确定。

   ![image-20251007161303242](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007161303242.png)

### 绑定HTTPS

1. 右键点击你原本的HTTP网站，然后选择编辑绑定。

   ![image-20251007161721535](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007161721535.png)

2. 点击添加。

   ![image-20251007161818440](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007161818440.png)

3. 类型选择`https`，SSL证书选择刚刚创建的证书，其它全部保持默认即可。然后点击确定。你网站的https就配置好了。

   ![image-20251007162143260](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007162143260.png)

### 测试

直接访问`https://localhost`，你可能收到浏览器的警告，这是因为我们的SSL是自己创建的，并不被公共认可，浏览器认为其可能不安全。此时强制访问即可。

![image-20251007162618807](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007162618807.png)