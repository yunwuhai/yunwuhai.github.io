---
date: 2025-10-05T19:28:13+08:00
draft: false
title: '使用IIS组件搭建服务器（Web）'
categories:
 - 网络协议学习
tags:
 - IIS
 - Web
 - 服务器
author: ["云雾海"]
description: "使用IIS组件搭建Web服务器"
license: CC-BY-SA 4.0
---

# 使用IIS组件搭建服务器（Web）

## 目标

使用IIS组件搭建一个Web服务器。

## 步骤

### 启用IIS功能

IIS在Windows中是默认关闭的，需要手动启用。

1. 打开控制面板，选择“程序”![image-20251006105646203](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251006105646203.png)

2. 进入程序界面，选择“程序和功能”。

   ![image-20251006105854994](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251006105854994.png)

3. 进入程序和功能界面，选择“启用或关闭Windows功能”

   ![image-20251006110019020](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251006110019020.png)

4. 勾选“Internet Information Services”旁边的复选框，这会默认勾选大部分子项，我们只需要这些默认的子项即可，不过你也可以检查一下是否和我的一样。注意下面的“可承载的Web核心”不需要勾选，这部分更加类似于一个可被编程调用的库，并非我们本次实验的目的。

   ![image-20251006110405143](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251006110405143.png)

   点击确定后等待系统自动安装所需文件，完成后点击关闭即可。

### 创建网站文件夹和内容

1. 在合适的地方创建一个文件夹用于管理你的网站，例如我的`C:\Workspace\Test\WebService`。

   ![image-20251007132358768](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007132358768.png)

2. 创建首页文件：在你创建的文件夹中创建一个名为`index.html`的文件，使用记事本或你的文本编辑器打开它并修改内容。你可以在其中添加一些简单的HTML内容，例如：

   ```html
   <!DOCTYPE html>
   <html>
   
   <head>
       <title>IIS Web服务测试</title>
       <meta charset="UTF-8">
       <meta lang="zh-CN">
   </head>
   
   <body>
       <h1>这是IIS Web服务测试</h1>
       <p>欢迎使用IIS Web服务</p>
   </body>
   
   </html>
   ```

   ![image-20251007135654725](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007135654725.png)

   ![image-20251007132754658](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007132754658.png)

### 在IIS管理器中创建网站

1. 现在使用IIS管理器来配置网站。按住`Win+R`，输入`inetmgr`，然后回车。也可以在开始菜单搜索“IIS”或“Internet Information Services(IIS)管理器”。

   ![image-20251007133034885](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007133034885.png)

   ![image-20251007133125211](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007133125211.png)

2. 展开左侧“连接”面板中计算机名称，然后右键点击站点，选择“添加网站”。

   ![](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007133342997.png)

3. 接下来在打开的网站信息填写界面，根据你的喜好输入一个网站名称，物理路径选择你刚才创建的文件夹。其他的暂时可以默认不变。不过需要注意你的端口可能会冲突，此时可以修改你的端口为`8080`或其它未被占用的端口。点击确定。你可以参考我的填写内容。

   ![image-20251007135013312](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007135013312.png)

   ![image-20251007134147029](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007134147029.png)

   ![image-20251007134211924](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007134211924.png)

4. 如无意外，你可以看到你的左侧网站界面多了一个你刚才创建的网站。点击它，中间的界面就会变成该网站的管理界面。

   ![image-20251007134421293](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007134421293.png)

   ![image-20251007135849126](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007135849126.png)

### 测试网站

现在我们可以测试这个网站了，打开一个浏览器，输入地址并在其后添加你刚刚选择的端口号，例如`http://localhost:8080`，你就可以打开刚才你的`index.html`网站。实验成功。

![image-20251007140127244](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007140127244.png)