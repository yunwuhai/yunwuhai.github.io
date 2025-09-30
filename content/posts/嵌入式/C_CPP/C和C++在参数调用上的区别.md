---
title: "C和C++在参数调用上的区别"
draft: false
categories:
- 嵌入式
tags:
- C/C++
license: "CC-BY-SA 4.0"
description: "本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/109561677"
date: "2020-11-08T17:10:52+08:00"
---


_在学习 C 语言的数据结构时，我发现教科书上出现的一些代码实际上并不能很好地在 C 语言环境中运行，而需要改成 C++才可以，在网上搜了一下，这里记录 C 和 C++在函数传参上的区别_

C++的形参有三种写法：

```cpp
void example_CPP(&a, *b, c){
	/*a为引用传参*/
	/*b为指针传参*/
	/*c为直接传参*/
}
```

三种写法各有用处，这里我们以实例进行研究——

首先我们打开自己的 IDE，我用的 CodeBlocks，然后输入一下程序：

```cpp
#include <iostream>

using namespace std;

void example_CPP(int &a,int *b,int c);

int main(){
    /*定义三个变量并输出其值和地址*/
    int x,y,z;
    x = y = z = 0;
    example_CPP(x, &y, z);
    cout<<"x的值:"<<x<<"\nx的地址"<<&x<<"\n";
    cout<<"y的值:"<<y<<"\ny的地址"<<&y<<"\n";
    cout<<"z的值:"<<z<<"\nz的地址"<<&z<<"\n";
}

void example_CPP(int &a,int *b,int c){
    /*将3个数分别加一*/
    a += 1;
    *b += 1;
    c += 1;
	/*a为引用传参，传的是引用值*/
    cout<<"a的值:"<<a<<"\na的地址"<<&a<<"\n";
	/*b为指针传参，传的是地址*/
    cout<<"b的值:"<<*b<<"\nb的地址"<<b<<"\n";
	/*c为直接传参，传的是实际值*/
    cout<<"c的值:"<<c<<"\nc的地址"<<&c<<"\n";
}

```

输出结果如下：
![C++测试结果](https://i-blog.csdnimg.cn/blog_migrate/925a891acf596a733db3fb59b898353d.png#pic_center)

当我们使用直接传参时，实际过程可以理解为我们把原来 z 的值赋值给一个新的变量 c，在对 c 进行了一堆操作后释放 c 的空间，而 z 实际上并没有参与到函数中，而仅仅起到一个赋初值的作用。

而当我们进行指针传递时，可以理解为我们把 y 的地址赋值给一个指针变量 b，而通过指针 b 对其指向的 y 的存储空间进行操作，我们没有直接对 y 进行操作，但是通过指针 b 我们可以间接修改 y 的值。

至于我方在使用引用传参时，可以理解为直接传参和指针传参的结合版，我们申请了一个新的变量 a，类似于直接传参的变量 c，但是这个变量的地址被赋值为 x 的指针，从效果上来看就有点类似于把 x 临时当成全局变量传递进函数了。这种传参方式非常优秀，相比直接传参可以修改实参真实值，而相比指针传参则不用担心在调用时漏掉了取地址符。

不过值得注意的是，这种传参方式并不能在 C 语言中使用，至少目前常用的 C99 标准和 C11 标准里我还没看见可以使用的。以下是我在 C 语言里面进行的测试：

```c
#include <stdio.h>
#include <stdlib.h>

void example_CPP(int &a,int *b,int c);

int main(){
    /*定义三个变量并输出其值和地址*/
    int x,y,z;
    x = y = z = 0;
    example_CPP(x, &y, z);
}

void example_CPP(int &a,int *b,int c){
	/*a为引用传参，传的是引用值*/
	/*b为指针传参，传的是地址*/
	/*c为直接传参，传的是实际值*/
}

```

编译器报错：

![C测试编译器报错](https://i-blog.csdnimg.cn/blog_migrate/86ace46f0a427868daad34a4ecf4e3fc.png#pic_center)

_这两个错误分别报的函数声明和函数定义_
