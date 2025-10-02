---
title: "C的main函数解析"
draft: false
categories:
- 嵌入式/C_CPP
tags:
- C
- C++
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/111412695
date: 2020-12-20T00:14:50+08:00
---


*终于开始学习Linux的C语言编程了~嘤嘤嘤，有种终于入门的感动~*

*关于Linux中C语言编程包括vim、gcc、makefile这些工具的用法这些不是本次的主题，我在这里就不详细展开了，本文只阐述一下main函数的参数调用问题。*

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [工具](#工具)
- [基本原理](#基本原理)
- [实现与解析](#实现与解析)

<!-- /code_chunk_output -->

## 工具

VirtualBox 6.1.12，Ubuntu 20.04，Code::Blocks，C

## 基本原理

众所周知，main函数对于系统来说其实也只是一个普通的函数，它作为一个接口与系统进行连接，每次系统调用main函数生成的程序文件。而Linux系统其实又是通过C语言写出来的，本质上其实也只是一个C程序。而调用C生成的程序文件其实就等同于将Linux的一个程序运行指针调用这个程序的地址，然后这个程序就执行起来了，而我们可以通过main函数的两个参数接口在调用这个程序的时候进行传参。

## 实现与解析

```c
// Hello.c，用于测试main参数传递
#include <stdio.h>
#include <string.h>

int main(int argc, char *argv[])
{
    printf("程序地址为：%s\n", argv[0]);
    printf("本次传入参数共有%d个\n", argc - 1);
    int i = 1;
    while(i < argc)	// 通过循环遍历传入所有参数
    {
        switch(argv[i][0])	// 通过首字母进行快速定位
        {
            case 'w':
            case 'W':
                {
                    if(strcmp(argv[i], "World") == 0)
                    {
                        printf("Hello World!\n");
                        break;
                    }
                    else printf("Is W/w but not World~\tHello %s\n", argv[i]);	// 是W/w但是并非World
                    break;
                }
            case 'l':
            case 'L':
                {
                    if(strcmp(argv[i], "Linux") == 0)
                    {
                        printf("Hello Linux!\n");
                        break;
                    }
                    else printf("Is W/w but not World~\tHello %s\n", argv[i]);	// 是L/l但是并非Liunx
                    break;
                }
            default:
                printf("This is %s\n", argv[i]);
                break;
        }
        i++
    }
    return 0;
}
```

这里我们可以看到main函数中有两个参数，分别是int类型的argc和char\*\*类型的argv两个参数，当然这两个参数的名字可以变换，就像普通函数的形参一样，但是通常大家都用这两个，相当于约定俗成了。可以看出argv是一个指向char数组的指针数组的数组指针，听上去有点绕，但是用char \* argv[]应该就比较好理解了，或者说甚至可以直接当成一个二维数组，其中第一维是一堆地址，每个地址分别指向一个char数组的首地址，而char数组则构成了第二维。而argc则记录了其中第一维的指针argv[]的个数。

不过值得注意的是，argv有一个默认值argv[0]为程序自身所处地址，比如说如果我们在Windows下检测一个在D:\Code下的test.exe函数，其argv[0]的值就为：D:\Code\test.exe。

我用如下程序进行了测试：

```c
#include <stdio.h>

int main(int argc, char * argv[])
{
    printf("当前文件的路径：%s\n", argv[0]);
    return 0;
}
```

输出结果如下：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/c652d7de2b3a300b16e91dc881ec14ee.png#pic_center)


而我们刚才说过argc记录的argv[]的个数，所以同理，我们知道argc的默认值为1。

所以我们其实就可以把\*argv[] 当成一堆指令，每个指令argv[i]在传入到程序中后就是一个char数组的形式。用归类拓展的方式去理解，其实我们平时在cmd中使用的help xx也许其实也相当于是一个程序，help是函数名而xx则是一个参数（当然事实上是不是这样我也不知道，只是做一个例子便于理解，不过想来相差不大）。

而有了这些认识，我们再看一下上面的程序，就不难理解我的操作了：

在输出了地址和本次传入参数个数后，程序将会从我传入的第一个参数（也就是argv[1]）开始，一直到最后一个参数，分别将其作为指令进行判断，如果为Linux或World则输出Hello World，其他指令则以This is xx进行输出，而如果判断出首字母为L/l或W/w的指令则会多输出一句Is W/w but not World~\t，最终运行结果如下：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/bb2e858a090083f04784b70b68370c65.png#pic_center)