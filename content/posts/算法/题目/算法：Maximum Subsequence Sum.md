---
title: "算法：Maximum Subsequence Sum"
draft: false
categories:
- 题目
tags:
- 题目
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/123927121
date: 2022-04-02T19:09:57+08:00
---

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [题目来源](#题目来源)
- [题目内容](#题目内容)
- [分析](#分析)
- [我的程序](#我的程序)
- [运行结果](#运行结果)

<!-- /code_chunk_output -->


## 题目来源

浙大数据结构MOOC-PTA的课后题

## 题目内容

![](https://i-blog.csdnimg.cn/blog_migrate/818138394d250650e19decb33b707299.png)

## 分析

这一题时最大子列和问题的变形，需要输出最大子列和的子列首项与末项，且在数列全为负的情况下，最大子列和为0，且需要输出首尾。而且如果出现了前后有相同都是最大子列的情况，选择前面的那一个。

我继续沿用了最大子列和问题中的在线处理算法，但是加上了对子列首尾的处理。

说实话这题有点难，我的做法也稍微有点取巧，使用专门的标志来处理非正有0的情况，不过总体来说结果是过了。

## 我的程序

```c
#include <stdio.h>

int main()
{
    // 获取数据
    int size;
    scanf("%d", &size);
    int num[size];
    int max = 0, this = 0;
    // 记录首尾位置
    int start = 0, end = 0, temp = 0;
    // 记录负数和正数的个数
    int negFlag = 0;
    int posFlag = 0;
    // 在线处理，寻找最大子列和同时记录该子列和首尾位置
    for(int i = 0; i < size; i++)
    {
        scanf("%d", num + i);
        // 记录正数和负数的个数，等会有用
        if(num[i] < 0)negFlag++;
        else if(num[i] > 0)posFlag++;
        // 计算子列和
        this += num[i];
        if(this > max)
        {
            max = this;
            // 当最大子列和发生了变化，记录其末尾，并将之前缓存的首部放入start
            end = i;
            start = temp;
        }
        else if(this < 0)
        {
            this = 0;
            // 当在线处理发现了子列和为负数的情况，需要丢弃前面的子列和，此时使用temp记录此次更新，因为它可能成为最大子列和的首项
            temp = i + 1;
        }
    }
    if(negFlag == size)printf("%d %d %d", 0, num[0], num[size - 1]);	// 全是负数，输出最大值0和首尾项
    else if(posFlag > 0)printf("%d %d %d", max, num[start], num[end]);	// 如果有正数，则必然存在非零最大子列
    else if(posFlag == 0)printf("0 0 0");	// 如果没有正数，又不全是负数，则最大子列和是0，且子列内容也全是0，直接输出0
    return 0;
}
```

## 运行结果


![](https://i-blog.csdnimg.cn/blog_migrate/a149a3fd19ed118b5993fd92179a8e01.png)