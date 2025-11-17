---
date: 2025-11-17T18:31:28+08:00
draft: false
title: '蓝牙协议HCI抓包实验'
categories:
 - 网络协议学习
tags:
 - Bluetooth
 - HCI
author: ["云雾海"]
description: "本文示范了如何抓包手机和手环之间的蓝牙通信数据，以此为例可以抓包其他蓝牙通信，可用于协议的分析和故障排除等"
license: CC-BY-SA 4.0
---

# 蓝牙协议HCI抓包实验

## 实验准备

### 实验硬件

- 一台电脑
- 一台安卓手机（以VIVO手机为例）
- 一个蓝牙设备（以小米手环为例）
- 一根手机数据线

### 实验软件

- [安卓调试桥（ADB工具）](https://developer.android.google.cn/tools/releases/platform-tools?hl=zh-cn)

## 实验步骤

### 软件安装

#### 下载ADB工具

访问链接后，根据电脑平台选择软件包![image-20251117183731056](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117183731056.png)

#### 解压文件

下载得到一个压缩包，将其解压缩到一个文件夹中，并打开该文件夹

![image-20251117184035148](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117184035148.png)

![image-20251117184350656](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117184350656.png)

#### 检查下载

在该目录下右键选择在终端中打开，或可以先行打开终端然后跳转到该目录。

![image-20251117184436327](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117184436327.png)

输入`.\adb.exe --version`来检查是否可用，如果正常，应该会显示版本号。

![image-20251117185501167](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117185501167.png)

### 手机设置

#### 打开开发者模式

现在的安卓手机，开发者选项是隐藏的，需要手动打开开发者模式才能看到。

根据不同手机，可能有不同打开开发者模式的方法，vivo手机的方式是进入`设置-关于手机-版本信息`，连续点击软件版本号，即可开启开发者模式。大部分手机应该也是类似的方式，如果该操作不行，请自行搜索自己手机的开启方式。

![ab4198ebaed6d20d10ee83711c66b7da](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/ab4198ebaed6d20d10ee83711c66b7da.jpg)

#### 开启日志功能

进入设置中，选择开发者选项，并将`启用蓝牙HCI信息收集日志`选项设置为启用。**注意：如果此时蓝牙已经启动，应该将其关闭后重启，然后蓝牙日志就将开始记录。**

![85ecdf4b9a96df9ffb096d142be7bf55](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/85ecdf4b9a96df9ffb096d142be7bf55.jpg)

#### 开启USB调试功能

为了电脑能够读取日志，需要开启USB调试功能。

![0d63412e35d35021c1d5172f4b2785e2](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/0d63412e35d35021c1d5172f4b2785e2.jpg)

#### 完成一次数据传输

正常情况下，手环只要是用过的，在手机蓝牙开启后都会自动连接到手机上，不过为了测试，我们可以手动打开手环软件，比如小米的运动健康，然后刷新手环数据。此时理论上我们的手机和手环会进行如下通信：手机告知手环自己需要的数据，手环将数据传输给手机，当然它们可能还会参杂一些其他相关的认证消息，但是总体内容应该差不多就是这些。

![10bedddd5a0ce8cfad0be2d2b47de836](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/10bedddd5a0ce8cfad0be2d2b47de836.jpg)

在完成了这个操作后，为了数据干净，就可以选择关闭蓝牙了，我们的通信日志已经被记录下来了。

### 开始调试

#### 连接电脑

我们现在需要的工作就是将通信日志保存到电脑中，此时就需要用到我们的ADB调试工具了。首先将手机通过数据线连接电脑。

因为开启了USB调试模式，此时会弹窗问是否允许该电脑进行调试，选择允许即可。

![ce5bee27055c32a4712b02fccfca0d6f](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/ce5bee27055c32a4712b02fccfca0d6f.jpg)

然后选择传输模式为管理文件。

![9adc00c77d4d63f6da7ad58484c76d77](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/9adc00c77d4d63f6da7ad58484c76d77.jpg)

此时，我们的电脑已经可以对其进行调试了。

#### ADB读取报告

通过`.\adb.exe bugreport`然后加压缩包文件名的方式，可以将日志下载到一个压缩包中，该过程需要一两分钟。

![image-20251117192226872](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117192226872.png)

下载完成后就可以解压缩该压缩包，然后通过访问这个路径，可以找到蓝牙日志。如果是其他手机，不确定是不是一样的，但是可以通过搜索`hci`和`log`两个关键字来查找。

![image-20251117192405842](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117192405842.png)

![image-20251117192505861](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117192505861.png)

其中`btsnoop_hci.log.last`就是我们的目标文件了，当然根据实际情况可能没有`.last`文件，此时只有`.log`文件大概率也是对的。

### 查看抓包内容

#### 找到连接

打开WireShark，将`btsnoop_hci.log.last`拖拽进去打开。

![image-20251117192819626](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117192819626.png)

现在我们关注`Source`和`Destination`，只要其中出现了我们的设备名，就说明抓包成功了。

![image-20251117193059622](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117193059622.png)

可以发现，我们的手机先给手环发送了一个L2CAP发送包，然后手环回了一个L2CAP的接收包。我们知道L2CAP是用于蓝牙协议中建立连接的，故此可以知道我们的通信成功了。

#### 观察数据

我们继续往下观察，可以发现RFCOMM协议的几个包，我们知道RFCOMM协议是用于构建虚拟串口的，显然这里是在构建通信连接。

![image-20251117200144842](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117200144842.png)

而后我们继续观察，可以发现过了一段时间后，突然出现了大量的SPP包，我们知道这个包适用于规范RFCOMM传输内容的，而且通过数据包长度也可以知晓，这显然就是在传输我们的手环数据给手机。

![image-20251117200315178](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117200315178.png)

让我们点开其中的一个看一下里面的数据：

![image-20251117200450721](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251117200450721.png)

这部分数据是data部分的内容，而具体内容则是非常杂乱的，我们在此可以猜测这个数据大概率是加密的数据，需要在手机软件中才会解密，防止被中间截获。

