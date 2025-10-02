---
title: "C/C++中malloc的强制转换"
draft: false
categories: 
- 嵌入式/C_CPP
tags: 
- C
- C++
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/111765714
date: 2020-12-26T18:14:00+08:00
---


*因为数据结构课在使用malloc函数的时候一直很迷惑，为什么一定需要在前面加上一个强制转换语句，像是这样：`int *a = (int *)malloc(sizeof(int)*3);`*。

为此我在菜鸟教程的malloc()函数介绍中找到了关于malloc的声明：`void *malloc(size_t size)`，显然加上一个强制转换语句并不是标准语法必须的东西，但是在菜鸟教程下面的举例中是按照强制转换的写法来写的，可惜没有说为什么。为此我尝试了不加强制转换语句的malloc来直接分配空间，在gcc编译后并没有报错或者发出警告。

这就很神奇了，我换了多个姿势来对这两种用法进行测试，包括但不限于不同大小`long *a = malloc(sizeof(int)*2)`或者数组结构`int *b = malloc(size(int)*3)`，他们都没有报错或警告，而强制转换亦是如此。

就在我怀疑是某种错误的如同void main这种异类写法产生了曼德拉效应时，我看到了[另一篇博客](https://www.cnblogs.com/esta-pessoa/archive/2013/04/29/3051119.html)的记录：在ANSI/ISO标准C下，我们是可以不使用强制转换来直接使用malloc的，并且使用强制转换还可能掩盖malloc()声明错误时产生的重要警告，反而不如直接使用malloc。但是使用malloc强制转换的好处在于，可以更方便地移植到C++中，因为C++似乎并不支持这种隐式转换。

根据这个帖子我大概猜测了一下国内这种喜欢在malloc函数前加强制转换命令的原因，除了个别学校在教学生C语言的时候把C/C++混为一谈，导致学生用C++的语法来理解C语言（这种情况真的不少），还有很大原因是因为国内高校很喜欢用Dev-C++这类常年未更新用着远古标准的IDE。