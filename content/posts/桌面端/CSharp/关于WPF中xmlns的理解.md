---
date: 2026-01-14T22:04:53+08:00
draft: false
title: '关于WPF中xmlns的理解'
categories:
 - CSharp
tags:
 - C#
 - WPF
 - XAML
author: ["云雾海"]
description: "关于WPF的XAML文件中xmlns的理解笔记"
license: CC-BY-SA 4.0
---

# 关于WPF中xmlns的理解

## 命名空间映射

以一个通过Visual Studio直接创建的简单WPF项目为例，我们查看其`MainWindow.xaml`文件，这是一个纯粹的窗口：

```xaml
<Window x:Class="Test.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        xmlns:local="clr-namespace:Test"
        mc:Ignorable="d"
        Title="MainWindow" Height="450" Width="800">
    <Grid>
            
    </Grid>
</Window>

```

其中这一部分很难理解：

```xaml
x:Class="Test.MainWindow"
xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
xmlns:local="clr-namespace:Test"
mc:Ignorable="d"
```

微软官方文档说，这个部分的内容其实叫XAML命名空间映射。

## 命名空间重命名

我们知道，在C#中就存在命名空间，也就是我们的namespace。

而XAML则是微软基于XML开发的一种声明性语言，WPF是XAML最出名的使用者，而关于XAML的解析则由`.NET`框架实现，它常被用于定义构造用户界面（UI）。

显然这是两种不同的语言，但显然两者需要进行交互，那么XAML就需要一种功能来调用命名空间，而这就是xmlns（XML/XAML namespace）的功能。

我们知道，对于C#中，调用其它命名空间的一种方式就是使用`using`语句，比如：

```c#
using System.Collections.Generic;
List<string> list = new List<string>();
```

而`xmlns`也是类似这样的功能，我们可以通过类似于以下的方式创建一个我们自定义于命名空间叫`Test`下的一个`TestButton`控件：

```xaml
xmlns:ts="clr-namespace:Test"
<ts:TestButton />
```

当然，如果更加准确一点形容，它在C#中应该更加类似于以下这种形式：

```c#
using ts = Test;
ts.TestButton = new ts.TestButton();
```

也就是说，`xmlns:（name）`这种格式有点类似于引用命名空间并重命名或重映射，这里就是把`Test`这个命名空间重映射为`ts`了。

但是和C#中非常大的不同是，C#可以不重映射，比如直接通过以下形式实现：

```c#
Test.TestButton = new Test.TestButton;
```

但是XAML中要引用命名空间则必须先使用`xmlns`语句将其重映射一遍。

另外XAML中调用命名空间时使用的`clr-namespace:`是一个固定关键词，在这个关键词后面可以通过类似C#的方式来写命名空间，而且它不只能引用到`namespace`这一级，继续往下到类也是可以的。

```xaml
xmlns:tb="clr-namespace:Test.TestButton"
```

这一点用C#的思想去理解就可以了。

而事实上，我们的`xmlns:local`就是这个功能，它提供的服务就是将项目的命名空间引用起来了，而这个`local`可以改成任意其他名称，不过通常我们不用改。

## 默认命名空间

现在我们大概理解了`xmlns`的作用，那么让我们重新回顾语句，会发现其中有一个没加`:`的语句，即：

```xaml
xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
```

这个语句其实代表了一个默认命名空间，而它后面跟的不是`clr-namespace:`而是一个网址。

事实上这个网址并不是一个网页，而是统一资源标识符（URI），使用这种格式而非命名空间名字，最大的原因是为了保证全局唯一性，因为`microsoft.com`这个网址是微软拥有的，所以这个URI只有微软能用，这个URI的信息主要如下：

```markdown
http://schemas.microsoft.com/winfx/2006/xaml/presentation
                |           |        |      |      |
                公司        规范     年份  技术   具体组件
```

其中`schemas`代表模式或规范，而`WinFx/2006`就是WPF的代号和规范的年份，`xaml`代表用于XAML技术，`presentation`代表WPF的Presentation层。

简单理解，这一个自动生成的`xmlns`代表的就是`WPF`的整个库，而它没有`:`则是因为它将作为默认空间使用，在XAML中任何没有加前缀的控件，都会优先在这个命名空间里面寻找，比如：

```xaml
<Button Content="Button" HorizontalAlignment="Center" VerticalAlignment="Center"/>
```

和我们前面的`TestButton`的调用方法不同，前面并没有加任何`name:`，所以这种`Button`就会直接在`xmlns`指向的默认命名空间中寻找。

否则，我们在前面加一个`ts:`：

```xaml
<ts:Button Content="Button" HorizontalAlignment="Center" VerticalAlignment="Center"/>
```

只是加了一个`ts:`，现在就必须在一个`xmlns:ts`的命名空间里面寻找了，如果前面没有引用这个空间，或者空间里面没有`Button`这个类，那么就会报错。

## 特殊的x

我们发现在我们开始举例的XAML代码里面，最开始有一个`x:Class`，而后面才出现了`xmlns:x=http://schemas.microsoft.com/winfx/2006/xaml`。

并且通过我们刚才对URI的理解，我们发现这个`x`的URI和刚刚的`xmlns`的很相似，只是它的URI少了`/presentation`，这代表它似乎是直接对XAML本身的规范。

事实上在XAML中`x`也确实是一个比较特殊的命名空间，它提供的不是某些控件，而是XAML本身的一些语言特性或特殊操作。

而`x:Class`就是这个命名空间中一个比较重要的操作，它提供了XAML和C#后台代码的连接，比如在XAML中我们看到：
```xaml
x:Class="Test.MainWindow"
```

这其实对应了C#后台代码的：

```c#
namespace Test
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }
    }
}
```

可以发现，它们的命名空间和类名完美对应上了，在编译时，两个板块才能够连接在一起。

显然`x`在工作中并不是调用某个C#的类或方法，而是作为一种特殊工具来操作XAML本身。

而`x`的常用功能很多，比如我们在XAML中通过语句添加了一个Button控件，就像我们刚才那样：

```xaml
<Button Content="Button" HorizontalAlignment="Center" VerticalAlignment="Center"/>
```

我们或许可以在VS的布局界面看到这个按钮，但是我们该如何在C#中调用这个按钮呢，其实要做的就是添加`x:Name`，比如：
```xaml
<Button x:Name="button" Content="Button" HorizontalAlignment="Center" VerticalAlignment="Center"/>
```

现在，我们就可以在C#后台代码中通过变量名`button`直接访问控制这个控件了，操作变得非常简单。

关于`x`，常用的指令有：

- `x:Class` - 连接XAML和C#后台代码
- `x:Name` - 给控件起名字，用于后台访问
- `x:Key` - 给资源（样式、模板等）起标识符
- `x:Type` - 表示一个类型
- `x:Static` - 引用静态成员

另外`x`这个名字是可以改的，因为它只是一个约定俗成的名字，其本身仍然遵守XAML的语法规则。但是通常不建议修改，因为一些库里面习惯了这个约定俗成的名字，改了很可能会出现一些意想不到的错误，而且也会降低代码可读性。

## 用于设计的d

我们还可以看到一个自动生成的命名空间：

```xaml
xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
```

d=Design，代表设计时。

它和`x`类似，不直接提供控件但是提供一些特殊服务，而这里的服务则是一些供Visual Studio设计器或者Blend中显示，而运行时会消失的特殊属性，比如：

```xaml
<Window
    xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
    d:DesignHeight="450"
    d:DesignWidth="800">
```

这是在设计器里面提供了一个预览尺寸，方便在设计界面的时候看到效果，但是实际运行时窗口的大小则和这两个属性无关。

不过我们大多数设计其实不需要关注`d`提供的这些服务，所以如果你不需要，不管它就行了。不过你如果担心它会污染你的代码，出现一些意想不到的错误，其实可以放心，因为下面一个命名空间的功能解决了这个问题。

## 标记兼容性的mc

继续往下看，我们可以发现两个语句：

```xaml
xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
mc:Ignorable="d"
```

这里面都出现了`mc`命名空间，mc=Markup Compatibility，即标记兼容性。

这个命名空间通常与`d:`配合使用，它会告诉编译器，有些标记只是设计时使用的，运行的时候可以忽略，即`mc:Ignorable="d"`。

如果没有这个声明，编译器在看到`d:DesignHeight`时可能会产生困惑，这个属性是什么，自己似乎并未见过（因为这个功能只在设计器或Blend中被调用实现了）。

此外，利用mc的一些特性，可以将某些实验功能或未来版本的功能标记为可忽略，这样旧版本的编译器就不会报错。

同样，大部分时候我们不需要关注这个标记的用法，需要用的时候再自行查询即可。