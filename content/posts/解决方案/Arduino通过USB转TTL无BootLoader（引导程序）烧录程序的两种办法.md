---
date: 2020-08-09T19:51:21+08:00
draft: false
title: "Arduino通过USB转TTL无BootLoader（引导程序）烧录程序的两种办法"
categories:
- 解决方案
tags:
- Arduino
- Bootloader
- STM32
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/107898812
---


# Arduino 通过 USB 转 TTL 无 BootLoader（引导程序）烧录程序的两种办法

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [Arduino 通过 USB 转 TTL 无 BootLoader（引导程序）烧录程序的两种办法](#arduino-通过-usb-转-ttl-无-bootloader引导程序烧录程序的两种办法)
  - [注意](#注意)
  - [于 BootLoader 的废话](#于-bootloader-的废话)
  - [通过 ArduinoIDE 的 Serial 模式烧录](#通过-arduinoide-的-serial-模式烧录)
  - [通过二进制文件烧录](#通过二进制文件烧录)
  - [总结](#总结)

<!-- /code_chunk_output -->


## 注意

（这个实验室基于 stm32duino 的，avr 单片机并不直接通用，不过如果你准备尝试使用串口来给 avr 单片机（_就是 Arduino 官方出的几款 Arduino_）烧录 Arduino 的 BootLoader，建议直接放弃因为 avr 单片机并不支持直接使用串口上传程序，而且 Arduino 的 BootLoader 好像目的也就是让 Arduino 能够直接串口烧录程序。

_也就是说你不能在没有 BootLoader 的情况下烧录 avr-Arduino 的 BootLoader，而当你可以用串口给 avr-Arduino 烧录 BootLoader 时就说明你已经有 BootLoader 了，可以不用再烧录一次了_）

## 于 BootLoader 的废话

因为准备参加电赛，想着如果比赛可以用 Arduino 或许会方便很多，所以准备研究一下 Arduino 的底层程序，学习一下如何把随便一块芯片都能做成 Arduino 来开发。不过这篇帖子和此并没有太大关系，只是属于机缘巧合做的一个小实验而已，对于已知 BootLoader 的原理或者想自己写 BootLoader 的朋友并无太大帮助。

最开始初学的时候，买了一块 nano 板，结果在我准备做点骚操作的时候（具体忘了做了啥了，好像是写错了个指针？），它被我搞废了，烧录不了程序。然后各种查资料，怀疑是 BootLoader 的问题，需要重新烧 BootLoader。（事实上现在我也不知道具体是不是真的，因为拖延症导致我很久没去碰这块板子，现在不知道扔哪去了。而且当时没有记录的习惯，这个世界又多了个未解之谜）

当时我并不清除 BootLoader 是个什么东西，毕竟年轻的我看见 hardware 文件夹里那一堆文件就头（tuo）疼（yan），但是总体印象大概就是 Arduino 的便捷和这玩意有很大关系。然后在我脑海中 Arduino 不能没有 BootLoader 这个想法就形成了，于是这次准备把 MSP430 做成 Arduino 的时候我就想到了是不是要烧 BootLoader？但是打开官方给出的 energia 软件，在其目录下并未发现 BootLoader 的文件，而且软件也没有给出烧录引导程序这一选项，所以我对我的认知产生了一丝丝怀疑。
![avr](https://i-blog.csdnimg.cn/blog_migrate/89700e50a16f79ed64fc41553b94362c.png)

![energia](https://i-blog.csdnimg.cn/blog_migrate/1faee740b48f0ec670aebde6bbf8f117.png)

于是，我选择再搜索一下 BootLoader 到底是什么，[百度的解释](https://baike.baidu.com/item/BootLoader/8733520?fr=aladdin)是可以把它当做一个启动引导程序，但是感觉这种解释有点抽象，然后我找到[另外一篇文章](https://www.cnblogs.com/anandexuechengzhangzhilu/p/10719808.html)是说把它当做一个系统，我们的程序就是运行在这个系统的软件，这种说法感觉有一定道理，但是感觉又不是那么对，因为平常如果我们没有 BootLoader，我们也可以对普通单片机烧录程序，但是如果软件没了系统，是无法直接在电脑裸机上运行的。但是这个文章还是给了我一定的思路，所以我搜索了一下“如何使用串口给 avr 烧录程序”，然后我找到了[这个](https://wenku.baidu.com/view/de9810795acfa1c7aa00ccd8.html)。然后结合我目前掌握的知识和已知条件：

1. 每次 Arduino 在上传程序时都会进行一次复位，我怀疑是为了让 Arduino 进入 BootLoader 模式
2. 没有 BootLoader 的 avr 单片机不能直接在 ArduinoIDE 上烧录程序，在如何使用串口给 avr 烧录程序那篇文章里，提到了需要给 avr 烧录 BootLoader 后才可以通过串口给 avr 直接烧录程序
3. Arduino UNO 的原理图中，官方最原版使用了一块 atmega16u2，而市面上常见的 UNO R3 都是使用的一块 ch340（USB 转串口芯片）来代替，说明 BootLoader 并没有直接让 avr 芯片拥有 USB 功能
4. Arduino Leonardo 的原理图就没有使用 ch340 或是其他芯片，而是直接用 USB 数据口连接 USB 接口，而 Leonardo 和 UNO 这些的区别在于其芯片 atmega32u4 可以作为 USB 设备来识别。

所以我姑且对 avr-Arduino 的 BootLoader 进行了这样的推测性理解：**Arduino 的 BootLoader 可以当做一段启动程序，它的作用是让 Arduino 可以拥有与电脑直接（如 Leonardo）（或间接（如 UNO）），然后烧录时会把程序发送给 BootLoader 处理，然后 BootLoader 将其放到指定的 ROM 地址作为起始地址。在烧录结束后，芯片将从 BootLoader 部分跳到程序部分。而普通使用时，因为没有复位进入烧录这一行为，BootLoader 会被直接运行到底然后跳到真正程序起始位。如果不烧录 BootLoader，可以节省出 BootLoader 的内存空间，但是需要比较麻烦的接线方式（如 JTAG，ISP 之类）**

当然以上为我的个人推理猜测，目前太忙（tuo）还没有专门系统地学习这一块知识（内容感觉太杂不确定学习路线，有点东学点西学点的样子，如果有大佬能够指导一下方向就太好了），如果有错误非常欢迎指正。

然后以下才进入正文……

## 通过 ArduinoIDE 的 Serial 模式烧录

因为没有找到 MSP430 的引导程序，而 avr 的引导程序又需要烧熔丝，和我的目的（研究 msp430 的 Arduino）有比较大的差别，所以我选择了 stm32 来做测试。

用的是 stm32f103c8t6 的小蓝板（blue pill），大概步骤为：

1. ArduinoIDE 安装开发板：http://dan.drown.org/stm32duino/package_STM32duino_index.json

![开发板管理](https://i-blog.csdnimg.cn/blog_migrate/70f01c9835cfe2792692c5f00555ede4.png)

2. stm32f103c8t6 调整好 boot 引脚，连接 usb 转 ttl，然后连接电脑

3. 随便写个程序，注意引脚名称修改，我这里使用了 blink 例程，把引脚改为了 PC13

```cpp
   void setup() {
     pinMode(PC13, OUTPUT);
   }

   void loop() {
     digitalWrite(PC13, HIGH);   // turn the LED on (HIGH is the voltage level)
     delay(1000);                       // wait for a second
     digitalWrite(PC13, LOW);    // turn the LED off by making the voltage LOW
     delay(1000);                       // wait for a second
   }
```

4. 选择好板子、端口，然后选择烧录模式为 serial

![Serial](https://i-blog.csdnimg.cn/blog_migrate/0c32af7676ee0b7015f5451cf51485f7.png)

5. 点击上传即可

详细步骤请参考帖子：http://www.elecfans.com/d/1002467.html

## 通过二进制文件烧录

这个方法需要下载软件，软件使用时只需要一路点 next 即可，不懂的地方直接用翻译软件翻译一下就懂了，stm32 的二进制烧录方式具体步骤可以参考这个帖子：https://www.cnblogs.com/wangguchao/p/7308657.html

而 Arduino 的二进制文件可以通过 ArduinoIDE 的项目-导出二进制文件获取，会导出到工作文件夹下。

![二进制](https://i-blog.csdnimg.cn/blog_migrate/209ec1bafe6ef1e59222db663663839c.png)

## 总结

这个帖子其实就是做个思路引导，同时也是自己的学习笔记，如果需要烧录 stm32 的 Arduino 程序，在暂时不知道 BootLoader 原理或怎么写的情况下，可以用这种方式凑合着下载，而同理，avr 可以用 isp 或 jtag，msp430 用 jtag 或 sbw 或 bsl 来下载。不过最好再深入学习一下吧……

以上内容如有错误或遗漏，欢迎指正！
