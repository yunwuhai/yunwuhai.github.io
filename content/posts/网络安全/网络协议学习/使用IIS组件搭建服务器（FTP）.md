---
date: 2025-10-05T19:28:30+08:00
draft: false
title: '使用IIS组件搭建服务器（FTP）'
categories:
 - 网络协议学习
tags:
 - IIS
 - FTP
 - 服务器
author: ["云雾海"]
description: "使用IIS组件搭建服务器（FTP）"
license: CC-BY-SA 4.0

---

# 使用IIS组件搭建服务器（FTP）

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

4. 展开“Internet Information Services”，将“FTP服务器”中的所有选项勾上。

   ![image-20251007142242849](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007142242849.png)

   点击确定后等待系统自动安装所需文件，完成后点击关闭即可。

### 添加FTP站点

1. 按`Win+R`，输入`inetmgr`，然后打开“IIS管理器”。在左侧连接框中展开计算机，然后右键点击站点，选择“添加FTP站点”。![image-20251007142749525](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007142749525.png)

2. 在信息填写界面，根据你的喜好输入一个网站名称，物理路径你可以根据需要在一个地址创建一个文件夹并选中，这会是你的FTP根目录，例如我的`C:\Workspace\Test\FTPService`。你可以在这个路径下创建一些文件，你可以随意在文件中写一些东西，以便于等会测试用。之后点击下一页。

   ![image-20251007143208027](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007143208027.png)

   ![image-20251007154822707](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007154822707.png)

   ![image-20251007155050879](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007155050879.png)

3. IP地址选择“全部未分配”（这样我们可以直接使用环回地址`127.0.0.1`来进行测试），端口使用默认的21端口，SSL选择“无SSL”（因为我们没有SSL，而且只是测试用，没必要设置）。点击下一页。

   ![image-20251007143821970](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007143821970.png)

4. 身份验证我们选择基本，这样需要输入用户名和密码，然后再授权中选择所有用户，并给他们权限。这里其实无所谓如何设置，因为只是我们自己测试使用。设置完成后点击完成即可。

   ![image-20251007143934538](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007143934538.png)

5. 如无意外，你可以看到你左侧网站界面多了一个你刚才创建的FTP网站，点击它，中间的界面就会变成FTP的管理界面。

   ![image-20251007151159539](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007151159539.png)

### 使用命令行访问FTP

现在你已经可以访问FTP了，打开一个命令行，例如Powershell，然后导航到一个你希望下载文件的路径。例如`C:\Workspace\Test\FTPDownload`。使用指令`ftp 127.0.0.1`访问FTP服务器。然后输入用户名和密码，这个用户名和密码就是你当前登录的Windows账户的用户名和登录密码。此时你就可以登录到FTP服务器中了，此时输入`ls`即可查看当前FTP服务器中的文件，使用`get "文件名" ["重命名"]`即可将获取文件。使用完毕后，输入`quit`即可退出访问。

![image-20251007155649315](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007155649315.png)

此时我们的路径下就获得了FTP中的文件。

![image-20251007155740570](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251007155740570.png)