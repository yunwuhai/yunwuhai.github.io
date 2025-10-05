---
title: "MSP430在Energia上的使用（上）"
categories:
- Arduino
tags:
- Arduino
- MSP430
- Energia
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/108244072
date: 2020-08-26T17:32:10+08:00
draft: false
---


# MSP430 在 Energia 上的使用（上）

说实话我也不确定会不会有后面的笔记，但是这次实验的确相当于没有做完。

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [MSP430 在 Energia 上的使用（上）](#msp430-在-energia-上的使用上)
  - [准备工作](#准备工作)
  - [问题意义](#问题意义)
  - [实验一：测试传输接口](#实验一测试传输接口)
    - [实验现象：](#实验现象)
    - [实验结论：](#实验结论)
  - [实验二：移植到 ArduinoIDE](#实验二移植到-arduinoide)
  - [备注](#备注)

<!-- /code_chunk_output -->



## 准备工作

终于狠下心花了百元大洋买了块 MSP430F5529LP 板子，准备研究一下板载仿真器在 Energia 中是如何进行烧录的。

通过 TI 公司的官方文件《MSP430F5529 LaunchPad Development Kit……》，我们其实可以得到 LaunchPad 的原理图，因为整个原理图用了四页，这里就不详细展示了，有需要可以在 TI 官网找。我只截取板载仿真器和 MSP430F5529 芯片的接口部分的图

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ce2078a0f1addb14d8380c3564acccfa.png#pic_center)

其中板载仿真器被 TI 公司命名为 ezFET，应该是简版仿真器的意思，除去电源线部分，我们可以看到信息传输分为两部分——SBW 和 UART。其中 SBW 相当于两线 JTAG，可以当做仿真器接口，而 UART 则是使用的 MSP430 的 BSL 接口，其只能作为烧录口。

那么看到这其实问题就很简单了，我们需要确定 Energia 在烧录的时候具体是用的哪个接口。

## 问题意义

一般情况下，我们在使用 LaunchPad 时，是不需要管这个仿真器是如何工作的，但是如果当我们手里只有一块没有板载仿真器的开发板或者甚至只有一块芯片的时候，我们又该如何对其使用 Energia 呢，是应该用 JTAG 连接吗，还是使用 SBW，亦或是使用 BSL？我们是否能将 EnergiaIDE 的移植到 ArduinoIDE 上呢（因为 Energia 事实上能够使用的资源远远不及 Arduino，而且无法用 VSCode 这个大杀器）？

## 实验一：测试传输接口

这个工作其实很简单，因为板子在设计的时候就是通过跳线进行连接的，所以我们只需要调整跳线位置即可进行测试。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/441189fa41578c8341549dbe5ee0fbf8.jpeg#pic_center =500x)

### 实验现象：

1. 在安装好 Energia 以及板子驱动等之后，连接电脑 USB 与 ezFET 的 MicroUSB 接口，选择好端口和板子型号，选择示例程序 blink，直接点击上传程序。（上传成功，红灯闪烁）
2. 取下 RX 和 TX 跳线，剩下 SBWTCK 和 SBWTDIO，然后再次上传。（上传成功，红灯闪烁）
3. 取下 SBWTCK 和 SBWTDIO，剩下 RX 和 TX 跳线，然后再次上传。（上传失败，显示未检测到链接报错）

### 实验结论：

在 Energia 中，默认通过板载仿真器 ezFET 得 SBW 接口对 MSP430 芯片进行烧录。

## 实验二：移植到 ArduinoIDE

ArduinoIDE 本身自带了非常多的库，但是因为兼容性问题，并不支持直接移植到 Energia 上，所以 Energia 上目前可以直接使用的库可谓是非常少。而且无论是 ArduinoIDE 还是 EnergiaIDE 的代码辅助功能都非常垃圾，而如果能使用 VSCode 的 Arduino 插件就可以大大减轻这一问题。

移植方法很简单，打开 Energia 的目录，找到 hardware，把其中 Energia 文件夹复制到 ArduinoIDE 目录的 hardware 文件夹里。再把 Energia 的 tools 里的东西放在 ArduinoIDE 的 hardware-tools 里即可。这里需要说明的是，在复制完后可以点开 ArduinoIDE，简单做个 demo 或者直接用 energia 的 blink 作为测试，如果出现

```
exec: "/bin/msp430-g++": file does not exist
为开发板 MSP-EXP430F5529LP 编译时出错。
```

需要修改 hardware-energia-msp430 文件夹里的 Platform.txt 文件，这个文件定义了 CPU 体系结构等（包括编译器、生成过程参数、用于上载的工具等），可能和 ArduinoIDE 无法直接兼容。

具体修改规范可以参考 Arduino 官方的这个网址（需要科学上网）：https://arduino.github.io/arduino-cli/platform-specification/

如果暂时不想看这么麻烦的东西（像我一样），可以参考这个帖子：[[MSP]将 MSP430 纳入 ARDUINO IDE: 让 arduino 支持 MSP430F5438A](http://bbs.mydigit.cn/read.php?tid=1792962)

不过他里面给出的 Platform.txt 有点古老，ArduinoIDE 可能会给出警告，不过警告一般也可以不听，所以凑合着用吧。同时按照他的方法，可能无法完成直接烧录，因为我试了一下报错了。

移植并不算很成功，然后在 VSCode 里试了一下，一些定义会有点问题，暂时不确定是什么原因……说实话这个实验有点失败，还是能力欠缺了。

另外我也看了看 PlatformIO，里面对 MSP430 的支持同样很差，果然 MSP430 这种老古董还是有点过气了吗……

关于移植的方法我后面会再详细研究的（大概），如果研究好了再写这一篇的下章吧（意思是可 bi 能 si 会 qiang 没 po 有 zheng）。

## 备注

关于仿真器的问题，如果买到了没有仿真器的板子或者自己做板子，而手里又没有仿真器，除了 BSL 烧录的方法以外，也可以通过用 LaunchPad 板子直接把跳线那里外接出去，也可以当仿真器用。另外，ezFET 是一个开源硬件，详情可以参考[官方文件](https://processors.wiki.ti.com/index.php/EZ-FET_lite)，当然网上也有一些帖子讲了这个玩意的做法，同样可以参考。
