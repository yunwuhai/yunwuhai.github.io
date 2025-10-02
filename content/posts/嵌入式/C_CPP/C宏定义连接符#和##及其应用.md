---
title: "C宏定义连接符#和##及其应用"
draft: false
categories:
- 嵌入式/C_CPP
tags:
- C
- C++
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/117964250
date: 2021-06-16T18:22:21+08:00
---


在学习LwIP的时候，发现源码中出现了`#define LWIP_MEMPOOL(name, num, size, desc) MEMP_##name`这样的语句，了解到了C编译器中##这个连接符。顺便查了一下资料，还发现了#这个字符转换符。

## 功能

`##`可以作为宏定义中的变量替换，`#`则作为字符替换，一般他们都是用于带参宏定义中。

比如：

```c
#define func1(a) printf(#a"\n")
#define func(num, a) func##num(a)

int main()
{
    func1(hello);
    func(1, hello);
    return 0;
}
```

上述程序将会输出两个hello。

第一个hello源自于`func1(hello);`这句话因为宏定义将会变成`printf(“hello”);`其中hello之所以变成字符串，就是因为在宏定义的时候使用了`#`，另外相邻且未被任何字符隔开的两个字符串在C中会被合并在一起，故这里相当于还加上了一个回车。

第二个hello源自于`func(1, hello);`这句话因为宏定义首先会变成`func1(hello);`其中之所以参数1会出现在变量名中，就是因为在宏定义中使用了`##`，它相当于将宏定义中的参数num变成了真正Token中的内容。Token可以理解为我们在C语言中写的变量名、函数名等等。然后`func1(hello);`又变成`printf("hello");`。

## 应用

它们的应用不在于提高代码效率或缩减体积，而在于简化编程难度和提高易读性。

比如，我有一堆字符串口令，为了方便，我对它们进行了宏定义：

```c
#define TEST_HELLO 	"Hello"
#define TEST_BYE	"Bye"
#define TEST_NAME1	"Tom"
#define TEST_NAME2	"Jerry"
```

现在，我希望把这几个口令以一定的方式打印出来，最直接的方法就是如下：

```c
printf("%s %s %s %s", TEST_HELLO, TEST_NAME1, TEST_BYE, TEST_NAME2);
```

不过上述的方式太单一了，而且封装程度不好，如果我们未来想到一个新的问候词要替换呢？可能有人想到用这样的方法来替换：

```c
void SaySomething(char* sth1, char* sth2, char* name1, char* name2)
{
    printf("%s %s %s %s", sth1, name1, sth2, name2);
}
```

这样封装后我们使用：

```c
SaySomething(TEST_HELLO, TEST_NAME1, TEST_BYE, TEST_NAME2);
```

就可以完成上面的工作了，但是似乎还是太麻烦而且可扩展性以及封装度有点差，这时我们可以观察上面的所有问候语都是以`TEST_`开头的且后面的问候句与下划线后的文字直接相关，而人的名字则以`TEST_NAME`开头，然后接上一个数字编号，那么我们是否可以依靠这个来做点什么呢？

```c
#define SaySomething(sth1, sth2, name1, name2) printf(#sth1" %s "#sth2" %s", TEST_NAME##name1, TEST_NAME##name2)
```

通过这样一个封装，我们就可以实现前面的功能了，用法如下：

```c
SaySomething(Hello, Bye, 1, 2);
```

之所以它们可以连接在一起是因为C语言中直接相连的两个字符串是会被视为一个整体的。

由此可见当我们宏定义了一大堆功能类似名字类似且可以相互替换的常量时，`#`和`##`就变得非常有用了。

## 效果图

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/2f064b62237548df93038e322b1de940.png#pic_center)


![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/5cf23f0dcea0655e79b1b36e365ff762.png#pic_center)


