---
title: "MSP432在Energia上的使用（下）"
draft: false
categories:
- 嵌入式
tags:
- Arduino
- MSP432
- Energia
date: 2020-11-07T19:46:09+08:00
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/109551240
---


# MSP432 在 Energia 上的使用（下）

_其实我自己都没想到我居然会来填坑，不过说实话这好像也算不上填坑，毕竟之前在[MSP430 在 Energia 上的使用（上）](MSP430在Energia上的使用（上）.md)这个帖子里讲的是 MSP430，而且说的准备在 VSCode 里装 Energia 其实到现在还没弄，不过这里还是想介绍一下 Energia 的另一项功能，一个专属于 MSP432 的功能。_

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [MSP432 在 Energia 上的使用（下）](#msp432-在-energia-上的使用下)
  - [发现](#发现)
  - [使用方法](#使用方法)
      - [TASK1](#task1)
      - [TASK2](#task2)
      - [TASK3](#task3)

<!-- /code_chunk_output -->


## 发现

事实证明多看官网还是有好处的，之前我在使用 Energia 对 MSP430 进行编程时一直非常疑惑，为什么 TI 公司不直接使用 Arduino 已有的 IDE 而非要做个自己的 Energia 导致不为人知非常冷门，但是官网上的介绍回答了我这一点。打开[Energia 官网](https://energia.nu/)，进入 Guide 界面，翻阅一下可以看见一个名词——**MultiTasking**，即多任务。众所周知如果单片机想要实现多任务并行，一般需要自己搭建 RTOS 或者更复杂一点进行专门的时分复用设计，这些方法往往需要较丰富的知识才能实现。而 Energia 就可以非常简单地（其实如果进行一些复杂操作也是挺复杂的）实现多任务操作。而官网在这里其实也给出了关于 Multitasking 的[介绍](https://energia.nu/guide/foundations/programming_technique/multitasking/)，值得注意的是**目前该功能只能作用与 MSP432，MSP432E，CC3320 和 CC1310**几种芯片，这也是为什么我把这一章名字改成了 MSP432 而不是 MSP430。（说起来每次打开 Energia 它的启动显示里面也写到了 Energia MT，实际上就是说的这个功能，不过我一直没咋注意）

## 使用方法

其实官网原文就有一个大概介绍了，我这里就重复一下。关于 MultiTasking（以下简称 MT）的使用其实非常简单（如果不想做太复杂的话）。

每次新建工程后，我们会有一个初始界面，上面写的 void setup()和 void loop()（其实就是正常 Energia 或 Arduino IDE 在新建后的工程界面），我们可以把这个界面称之为工程主界面。如果只使用工程主界面写一个程序，那么它只是普通的单线程程序，但是如果你使用的是 MSP432 这类单片机，你可以点击 IDE 右上角的倒三角符号，新建一个 task，随便输入一个名字作为新任务（Task）的名字（注意不要输入后缀，IDE 会自动将其生成为 ino）然后你可以在里面写两个函数，他们便可以当成一个新的 setup 和 loop 函数了，此时如果烧录进芯片后，芯片便会同时运行两个任务（实际上并不是同时运行，只是通过快速转换两个任务的运行最后看上去是同时运行）。

示例程序有很多，这里介绍其中最简单的 MultiBlink 的程序。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/e7c8578e4b34b19fce183c3a6cf317c1.png#pic_center)

#### TASK1

```C++
#define LED BLUE_LED
void setup() {
 // initialize the digital pin as an output.
 pinMode(LED, OUTPUT);
}
void loop() {
 digitalWrite(LED, HIGH); //turn the LED on by making the voltage HIGH
 delay(100); // wait for a second
 digitalWrite(LED, LOW); //turn the LED off by making the voltage LOW
 delay(100); // wait for a second
}
```

#### TASK2

```C++
#define LED GREEN_LED
void setupGreenLed() {
 // initialize the digital pin as an output.
 pinMode(LED, OUTPUT);
}
void loopGreenLed() {
 digitalWrite(LED, HIGH); // turn the LED on
 delay(500);  // wait for half a second
 digitalWrite(LED, LOW); // turn the LED off
 delay(500); // wait for half a second
}
```

#### TASK3

```C++
#define LED RED_LED
void setupRedLed() {
 // initialize the digital pin as an output.
 pinMode(LED, OUTPUT);
}
void loopRedLed() {
digitalWrite(LED, HIGH); // turn the LED on
 delay(1000); // wait for 1/10 second
 digitalWrite(LED, LOW); // turn the LED off
 delay(1000); // wait for 1/10 second
}
```

该程序可以让 LaunchPad 上的三色 LED 以多种不同颜色的组合进行闪烁，有一说一还挺炫酷。
