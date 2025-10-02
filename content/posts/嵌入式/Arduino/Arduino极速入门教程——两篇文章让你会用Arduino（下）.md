---
title: "Arduino极速入门教程——两篇文章让你会用Arduino（下）"
draft: false
categories:
  - 嵌入式/Arduino
tags:
  - Arduino
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/113558575
date: 2021-02-02T15:17:03+08:00
---


*接[上篇](Arduino极速入门教程——两篇文章让你会用Arduino（上）.md)关于Arduino基础环境配置、界面介绍和C语言基础，这一篇的内容为具体如何在Arduino中进行编程。*

## 在VSCode上配置Arduino

### 什么是VSCode

VSCode，即Visual Studio Code，是微软制作的一个开源免费编辑器，当今始接最热门的主流代码编辑器之一。百度vscode或者点我给出的这个[链接](https://code.visualstudio.com/)，可以进到官网下载。编辑器与IDE（集成开发环境）不同，VSCode更加像一个可以加载插件的记事本，不过如果配置得当，VSCode也可以用来当作一个简陋的IDE使用。

### 为什么用VSCode

Arduino IDE本身其实只是一个非常简陋的IDE，没有代码补全、丰富的高亮、代码跳转重构等功能，而这些我们都可以在VSCode上进行实现，这可以是不必要的（如果你能力足够强用记事本直接写代码也是可行的），但是作为初学者或者开发者使用这些功能能够让你快速学习或者实现你想要实现的功能。

### 怎么配置

先下载并安装VSCode。

接着下载插件，在最左边选择扩展按钮，然后搜索并安装我标出的这几个插件，你就能有一个可以装Arduino的中文VSCode了（我的VSCode与你们的应该样式不同，因为我安装了样式的插件）：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/c7fc4b5633e0fc1458fc5acd5d2860b2.png#pic_center)


然后打开安装好的VSCode，左上角选择：文件-打开文件夹，然后选择一个你以后专门保存Arduino代码的文件夹打开。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/52016e4852c6b62c2703dc61160c1321.png#pic_center)


在左上角文件选项中选择首选项-设置。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/106e1e65d5a45b502d2f482a5a21e34c.png#pic_center)


然后设置界面的右上角，选择打开设置（json）

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/f37302a0a933a2447a87ac01aba3df89.png#pic_center)


然后我们就进入到了一个JSON文件界面，在原本的文件开头如下内容，不过需要**注意：下面第一行的path为你安装Arduino的位置，我安装在D:/Software/Arduino文件夹里的，如果设置自己的地址也请按照我这种双斜杠的格式来写。**

```json
    "arduino.path": "D:\\Software\\Arduino",
    "C_Cpp.intelliSenseEngine": "Tag Parser",
    "editor.insertSpaces": true,
    "files.autoGuessEncoding": true,
    "arduino.logLevel": "info",
    "explorer.confirmDelete": false,
    "editor.detectIndentation": false,
```

点击Ctrl+s保存JSON文件，然后重启VSCode，现在你的VSCode环境就配置好了。

## Arduino的程序内容

### 打开例程

现在我们先来打开一个官方例程，首先打开Arduino IDE，选择文件-示例-Basic-Blink，这是Arduino官方提供的一个灯光闪烁程序。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/09daac37204e1034f935706c1892f310.png#pic_center)


点开后按Ctrl+S，IDE会告诉你该文件处于只读状态，需要将项目保存在其它位置，点击确定，然后将文件保存在我们前面设置的VSCode工作文件夹里，然后我们就可以退出并通过VSCode打开它了。

例程将会是我们很好的学习资源，这些例程有些来自于开发板，有些来自于函数库，有些来自于官方，但是我们如果已经安装好的东西，找例程并且想要在VSCode中进行修改测试或者仅仅是查看，都可以通过这种方式来。

### 程序结构

我们现在可以发现其实这个Blink中有两个函数setup和loop，它们的功能我在下图中标示了：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/f5df60433d2ca2d95e1e3134913dece1.png#pic_center)


setup和loop是Arduino的逻辑核心，普通的Arduino程序都是基于这两个函数进行运行的，一般我们在setup中初始化环境，然后在loop区域写我们需要实现的功能。

如果想知道这两个函数是怎么实现的，可以查看`{你的Arduino安装地址}\hardware\arduino\avr\cores\arduino`中main.cpp和Arduino.h文件，大概意思就是我们在程序中实现的setup和loop函数将会通过Arduino.h被引用，然后在main.cpp中被执行，Arduino.h只是一个引用传递文件，这里我们重点关注main.cpp：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/931b69a6a1a66f5302b28401b63b14df.png#pic_center)


### 功能函数

现在我们再来看看Blink文件：

```cpp
// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
```

前面那一堆介绍注释我就不复制了，有兴趣自己看，我们现在关注程序中出现的功能函数：`pinMode()`、`digitalWrite()`、`delay()`。

根据注释其实我们可以知道它们的功能分别为初始化引脚功能，引脚电平改变，时间延迟，如果在VSCode中，我们可以按住Ctrl键然后鼠标单击该函数，即可进入该函数的定义界面。不过我们现在暂时不需要点击去知道这些功能，等以后你想自己实现一个Arduino的时候可以再尝试去看。

然后我们再看参数部分，OUTPUT、HIGH、LOW这些似乎比较好理解，但是LED_BUILTIN是什么东西？不用担心，我们同样Ctrl点击它，即可查看它的定义：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/52bb0868742053b303b2b91272870d20.png#pic_center)


它被宏定义为了1，现在我先告诉你这个1其实就是Arduino板子上标注了1的那个引脚，但是这个函数具体是怎么个原理呢？我们怎么知道一个函数需要怎么使用呢？

### 查看手册

对于上述两个问题，最好的方案当然是查看手册了。打开Arduino IDE，选择帮助-参考，然后我们就打开了我们的功能函数手册，一个保存在你电脑里的网页，参考手册看上去很多而且是全英语的，但是不用担心，我来告诉你怎么查看它。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/be4e29fe7e4bb3239f2d39f0ff567fd6.png#pic_center)


首先可以看到手册分成了三列，第一列的大标题是Structure（结构体），第二列是Variables（变量），第三列是Functions（函数）。

#### Structure

其中我们看第一列的Structure内容很多，但是除了setup和loop函数，其实就是C语言基础的东西。

#### Variables

##### Constants

而第二列变量里，第一个大类Constants（常量）（是的，他把常量划分到变量列里了，不过不影响，只是个分类方法而已），这些是一些宏定义的量，如果你需要知道他有什么用，点开查看即可，不过一般基础使用常用的内容有以下几个：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/a24cafad9d0e22d2c2096e0705348a38.png#pic_center)


不知道电平是什么的我们在后面讲。

##### Data Type

这个就是数据类型，C++与C之间的差别在于C++多了几个数据类型，其它没什么变化（不过不同芯片中同一类型占用的存储空间大小可能各自不同（也就是他的最大最小值可能会有差别），不过一般基础使用只要不遇到特别大或者特别小的一般不会遇到这些问题）我在这里标注了它们不同的地方：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/d3a6d198be7984e521491fa0e5e2a660.png#pic_center)


##### Conversion

这里面是一堆强制转换函数

##### Variable Scope & Qualifiers

变量作用域和限定符，主要用于限定作用域，其中static和const用法在基础阶段需要多练习掌握，而volatile则在真正开始做大项目之后开始慢慢掌握（提前掌握也挺好，只是怕你用不好）。

##### Utilities

公共功能，其中sizeof主要在于你不知道数据类型的大小的时候使用（就是我前面说的最大最小值可能存在差别的地方）。

而PROGMEM是一个内存控制标识，基础使用应该用不到，当你在存储处理大量数据时可以使用。

## 电路基础

在讲Function之前，我想先讲述以下电路基础，便于理解这些函数的功能，这里先假设你知道基础的电压（电平）、电流、电阻是什么，如果不知道还请去百度。

### 模拟电路

平常我们见到的像是音频波纹这些，都属于模拟信号，它们在时间上是连续的，一般来说我们正常制作和能感知到的电路都是模拟电路，我们可以把模拟电路某点的电压在时间上的改变用图像来标示，下面是一个模拟电路的波形示例：

![](https://i-blog.csdnimg.cn/blog_migrate/87df440dc801c80aae1089ce5f43937a.jpeg)

### 数字电路

数字电路其实是我们人为抽象出来的电路，也被称为逻辑电路。有一些半导体，比如LED二极管就有一个特性，当两引脚两端电压低于某个界限时它是相当于断路的，而如果高于这个电压，它又是相当于短路的，而断路和短路两种状态就可以等效为0和1两个数字，0表示其中电流不存在，断路，即低电平，而1表示电流存在，短路，即高电平。当然实际上的定义是一个数学上的概念，不过我们这里姑且这么理解就行了。而半导体因为这个特性就拥有了逻辑功能，加上一些特殊的半导体还有一些其它特性，人们把它们制作成了芯片。

所以我们平常使用的芯片之类的都是半导体元件，而在外界和内部的处理信息方式都是对数字电路的处理。

![](https://i-blog.csdnimg.cn/blog_migrate/ab0c76b24e577ddfc5a5b7404047c036.jpeg)

但是具体多高的电平是高电平多低是低电平呢。一般来说对于一个普通的芯片，它会有两种电源引脚，一个叫GND，一个叫VCC，GND作为参考基准电平，我们统一将其标定为0V，那么VCC和GND的电压差就是工作电压，我们可以直接用VCC的压值来直接表示。一般常见的工作电压有3.3V和5V，而UNO即为5V，在与UNO这类5V单片机定义电压分界的时候，往往定义的3V往上为1，往下为0，但是为了稳妥起见，芯片自身输出的1就是其工作电压，而0就是其GND的电压。

### 模数转换和数模转换

模拟电路和数字电路其实是可以相互转换的，一般我们如果需要从外界读取一个模拟量（就是我们不只是需要简单知道其电平为1还是0，而是需要知道具体电压），就可以使用模数转换然后得到结果。如果我们需要输出一个模拟量，就可以通过数模转换将数字信号生成模拟信号。

![](https://i-blog.csdnimg.cn/blog_migrate/59f0c1f4debbcd9e73d86f27167f084b.jpeg)

### PWM

这个属于数字信号的内容，因为我们知道输出电压在电路中其实等效于输出能量，而在周期时间内通过控制高低电平输出时间占比，就可以控制单位时间内能量的输出总量，实现脉冲调制的功能。当然这个功能不仅仅能用于控制能量，但是一般来说我们在基础阶段知道这一个功能即可。

## 接上面的功能函数

### Functions

这些功能函数其实就是Arduino官方设定的一些基础功能，而我们未来可能在使用途中会遇到更多的功能函数，但是从理论上那些功能大多数都是可以通过这些基础函数进行实现的，我接下来用图片罗列出它们的功能，不需要详细去记用法，如果需要用到的就直接再点开详细看就行，不然里面很多不常用的你记了后面也会忘，知道有些啥就行。

#### 普通引脚功能函数

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/928ec71e7a81a39151acd7da14dfd518.png#pic_center)


#### 时间函数

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/53e6bcfaf4757c926f8f14bfb84b8044.png#pic_center)


#### 数学函数

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/83055458ec6053dd60e03e7f7c7ddeb1.png#pic_center)


![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ba0f3a3ec5aaabbe1e4da94668689fb9.png#pic_center)


#### 字符判断函数

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/e12a692e5e3f7df829b9d166792e27f7.png#pic_center)


#### 随机数

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ed08e93c464bed7891b88924c01f87a4.png#pic_center)


#### 位操作

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/4794f6083da926f6bcc3e59b6dec5de7.png#pic_center)


#### 中断

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/4d7a674a1b2e9062d414907d168b81f6.png#pic_center)


#### 通信

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/36c3e79584e1750c2ca672cb6436c09e.png#pic_center)


不过上面其实只是一小部分，我们回到这个网页顶部，然后这里有个Libraries，点开它，里面罗列了一堆库的用法介绍。

## 我们现在究竟需要掌握些什么

相信你看到这么多功能感觉特别复杂了，不过不用担心，很多功能其实不太常用，我现在说一下一些比较常用的功能和函数，这些你去学习就好了。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/2d3673d1c2cd3162e1be37bd605ddd2b.png#pic_center)


1. 上面勾出来的三个库，你需要大概去掌握它们，其中SPI和I2C与前面Serial那个串口（UART）是非常常见而且重要的三种通信协议，你需要知道它们大概的通信流程。这些功能可以在Arduino IDE种官方提供的例程和这个参考手册综合学习。
2. EEPROM那个功能其实不是那么的重要，但是掌握它有助于你去理解芯片底层的存储机理。
3. 前面digital I/O和analog I/O的六个函数需要掌握，这是最基础的内容。
4. 掌握delay函数。
5. 掌握中断原理并能自己写一两个中断。

如果你可以使用我上面写的这五条里的功能，配合我前面讲的这些学习方法，Arduino的基础内容就基本难不倒你了。

## 后记

说来惭愧，我本以为会语言精炼地讲通这些，但是还是存在很多没讲好的地方，还请多多包含。本教程为一个入门教程，重点在于告诉你该如何快速去掌握Arduino这个平台并在后期深入学习，但是真正要学会还是得自己去深入了解掌握，毕竟你永远不可能通过一本书甚至这么一篇文章就成为高手。

其实之所以我在里面并没有怎么讲具体你要去实现什么怎么做，而是从底层原理和学习方法来讲，是因为每个人想要做的事是不同的，我如果将每个功能挨个讲完，那复杂程度就配不上Arduino这种专门为简化编程而生的平台了。