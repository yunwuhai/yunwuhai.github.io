---
date: 2020-12-25T21:10:10+08:00
draft: true
title: '如何在Vim中使用系统剪贴板'
categories:
- category1
tags:
- vim
- Linux
author: ["云雾海"]
description: "本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/111707347"
license: CC-BY-SA 4.0
---



作为一名砖业的CV攻城狮候补，在使用vim时因为vim的剪贴板是一块单独的内存，不能很方便地CV我们在网上找到的优秀代码，这实在让我感到非常头疼，故而在网上搜了一下如何让vim能够使用系统剪贴板，在这里记录一下。

首先在终端里执行`vim --version | grep clipboard`指令，这句话的意思大概是在vim的配置中搜索clipboard（剪贴板），然后我们可以看到一个配置名全称就是clipboard，它前面的符号有两种情况，如果是+号则说明可以在vim中使用系统剪贴板，只是需要一点特殊的指令。而如果是-号则说明暂时不能在vim中使用系统剪贴板，在这种情况下我们需要下载插件。根据我在网上看到的各种帖子，有两种方法，一是`sudo apt-get install vim-gnome`另一个是`sudo apt-get install vim-gtk`，我先是使用了第一种安装vim-gnome，但是不知道为什么无法安装，显示的已被引用。

我搜了很多帖子并且尝试了很多方法，但是这个vim-gnome始终无法安装上去，所以这个方法就被我pass了，不过我没有直接使用vim-gtk这种方法，而是直接用.vimrc文件来配置了一下，先是通过vim处理.vimrc配置文件：`vim ~/.vimrc`，然后在.vimrc文件中输入一行`set clipboard=unnamedplus`这句话的意思是让vim的剪贴板与外部剪贴板连接。然后我就直接可以在vim中使用y、p、d、x指令与系统剪贴板连通了。感觉这句话的意思有可能是让系统剪贴板和vim剪贴板的地址直接相等，这样在这段内存中Linux系统与vim就可以直接公用了。

然后因为各种原因，我重装了一个新的Linux，这一次我使用了上面说的第二种方法，安装了vim-gtk，然后在安装了这个插件后，使用`vim --version | grep clipboard`就可以看见clipboard的配置前面的符号变成了+号，这个时候如果进入vim，就可以使用`“+y`这类语句调用系统剪贴板了。详细可见[知乎回答](https://www.zhihu.com/question/47691414/answer/374044474)。