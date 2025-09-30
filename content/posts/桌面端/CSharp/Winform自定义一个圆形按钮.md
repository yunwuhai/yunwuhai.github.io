---
title: "Winform自定义一个圆形按钮"
draft: false
categories:
- 桌面端
tags:
- C#
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/115057585
date: 2021-03-21T22:45:35+08:00
---


*因为我是电子专业的，学校没教过C#，学下来也基本上都是野路子东看西看基于需求地乱学，故而对C#的理解并不是很深。然而个人项目需要自定义一个控件来实现动态连线功能，不得不从入门直接跳到高级应用进行学习，这里做一个记录以对后面有类似需要的朋友一个参考。目前只是实现了一个简单的变色按钮功能，但是需要使用的大部分技术都用上了，如果需要实现其它更复杂功能的话就把本文当个抛砖引玉吧。*

*本文参考了《[C#] （原创）一步一步教你自定义控件——01，TrackBar》,但是在其基础上增加了设置控件区域的功能。另外因为那篇文章被很多人盗用，原文已经不可考，所以不贴地址给他们引流了，如果有需要可以直接百度这个名字即可。*

## 新建工程

新建一个项目，选择Windows窗体控件库(.NET Framwork)，然后选择地址、命名。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/739585ea15f492b0d84f5b50c03bf306.png#pic_center)


正常情况下工程里应该有一个UserControl1.cs文件，不要它，直接删除，然后新建一个没有模板的类。

将此类的访问属性改为public并且继承自Control，如果Control下出现波浪线报错的话是因为没有引用其命名空间，可以按住`Alt + Enter`后选中第一个命名空间再按一次Enter进行修改，VS将自动添加上`using System.Windows.Forms;`。

## 添加属性

然后我们根据需求进行添加属性，因为这个功能只是需要实现一个圆形开关，那么我们需要知道的属性就有开关打开时的颜色，开关关闭时的颜色，圆形开关的直径，开关的状态四个属性。颜色使用Color类进行定义，直径使用int或者float进行定义，开关状态用布尔进行定义，并且给他们赋值上初始值。

```csharp
private Color openColor = Color.FromArgb(128, 255, 128);	// 开启默认浅绿色
private Color closeColor = Color.FromArgb(255, 128, 128);	// 关闭默认浅红色
private int diameter = 20;	// 直径默认20，且为整数类型
private bool isOpen = false;	// 默认关闭
```

然后为他们添加上各自的访问器：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/fd57a6439e9358d15ad2c206b752bba2.png#pic_center)


![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/543f0ac40433a38bd90034f48897f3fe.png#pic_center)


![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/d0751f17324da7995052ef8543f8f0b0.png#pic_center)


![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/6e40163512af66c91631e13ad14c48a1.png#pic_center)


我们可以注意到，他们各自的get访问器其实没啥特别的，但是set访问器中除了基本的赋值以外，每个访问器中都有`Invalidate();`这么一句，它的工作目的是重新绘制一遍控件。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/4a719da808aecb7b0ce4feedbf6ef341.png#pic_center)


一般来说，如果你调整的这个属性将会影响到当前控件的外观，那么就有必要加上这么一句，它的功能类似于将原本的控件从你的屏幕上删除，然后根据新的定义创建一个新的控件。

然后我们再观察直径的访问器中使用了`Size = new Size(diameter, diameter);`这么一句话，它的目的是什么呢？其实从语义上就可以推测知道，是重新赋值了大小属性，其中宽度和长度变成了直径的。但是理论上其实不加这句也没有问题，因为我们后面会使用一个指定边界函数实现相同功能，但是如果不加上的话我们在使用Winform的设计模式的时候就容易出现bug，调整大小的时候，如果调大就会出现内容消失的情况，需要手动去调整一下才能重新刷新出来。我理解的原因是设计模式其实开启了一个模拟窗口，但是这里我们修改属性值的时候只有一些基础属性会被显示出来而不会触发具体的方法函数。故而我们不能运行后面那个指定边界函数进行样式的刷新，导致出现视觉bug。

然后另一个需要注意的是，我们在IsOpen中使用了一个TestSwitch的事件，如果我们的开关状态发生了改变，那么就会触发这个事件。后来如果我们需要，可以为这个事件增加功能，一旦IsOpen被赋值，就可以执行相应的功能。

不过我们如果需要使用这个功能的话，就还需要添加上委托和事件的定义，一般情况下我们在命名空间内写委托，然后在类里定义事件。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/54bdcf19c95fe0409915e213ac2d364a.png#pic_center)


![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/e38aaa0fc11b41260f72bc0d54176302.png#pic_center)


但是，我们知道如果想使用VS的设计器的话可以利用属性栏修改控件的属性，所以我们自定义的控件自然也想要相同的功能。此时需要输入`[Category("属性分类"), Description("功能描述")]`即可添加这些功能。其中属性分类的目的是为了方便我们找到我们自定义的这些功能，而功能描述则是方便使用的时知道该如何填入所需的属性。如果这里出现了报错，同样是因为没有引用所需的命名空间，只需要像前面一样按住`Alt + Enter`然后进行修正即可。

以下是我定义的所有的属性以及他们的描述。

```csharp
		private Color openColor = Color.FromArgb(128, 255, 128);
        [Category("DemoUI"), Description("开启时的颜色")]
        public Color OpenColor
        {
            get { return openColor; }
            set
            {
                openColor = value;
                Invalidate();
            }
        }

        private Color closeColor = Color.FromArgb(255, 128, 128);
        [Category("DemoUI"), Description("关闭时的颜色")]
        public Color CloseColor
        {
            get { return closeColor; }
            set
            {
                closeColor = value;
                Invalidate();
            }
        }

        private int diameter = 20;
        [Category("DemoUI"), Description("圆直径")]
        public int Diameter
        {
            get { return diameter; }
            set
            {
                diameter = value;
                Size = new Size(diameter, diameter);
                Invalidate();
            }
        }

        private bool isOpen = false;
        [Category("DemoUI"), Description("开关状态")]
        public bool IsOpen
        {
            get { return isOpen; }
            set
            {
                isOpen = value;
                Invalidate();
                TestSwitch?.Invoke(this, new TestEventArgs(isOpen));
            }
        }
```

## 添加方法

完成了上述工作后，我们还需要为这个控件添加一些方法，然后他就可以成为真正的控件了。

首先，我们需要重写SetBoundsCore方法，这个方法可以定义控件的边界工作，根据微软给的定义，通过这个方法可以控制控件的Left、Top、Width、Height和BoundSpecified值，其中Left和Top控制着控件的位置，而Width和Height控制着控件边界的大小，而最后一个参数是枚举，不过功能没搞懂是做啥的，但是实际应用中不管也没事，因为我们一般都是重写Width和Height就好了。

```csharp
protected override void SetBoundsCore(int x, int y, int width, int height, BoundsSpecified specified)
{
	base.SetBoundsCore(x, y, Diameter, Diameter, specified);
}
```

通过这个重写，我们可以让边界大小始终等于圆的直径，其中base的意思是在重写是基于原本的方法进行重写。

然后我们还需要设置一个可以改变开关值的方法，因为我希望得到的效果是在点击控件时不会改变，而在放开时：如果在控件内放开鼠标可以改变值，而如果在控件外放开鼠标则保持原本只不变。这种情况下我们只需要重写OnMouseUp控件就好了，我重写的内容如下，内容一看就懂，就不多写注释了：

```
protected override void OnMouseUp(MouseEventArgs e)
{
	base.OnMouseUp(e);
 	if (Region.IsVisible(e.Location))
 	{
 		if (IsOpen)
		{
			IsOpen = false;
 		}
 		else
 		{
 			IsOpen = true;
 		}
 	}
}
```

然后我们再重写OnPaint方法，这个方法在我们每次调用Invalidate()的时候都会用到（就是前面每次我们调用set访问器的时候都会使用的那个函数），它的功能就是把控件在屏幕上画一遍（只是画一遍，并没有Invalidate中的清除原控件的功能）。

这里我们使用GDI+来画控件，当然事实上你也可以调用图片然后来实现，他们的原理相似。

首先我们需要让GDI+的分辨率提高（其实这个控件太简单了可能用不着，但是如果未来在画一些复杂的控件的时候可能需要）：

```csharp
e.Graphics.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.HighQuality;
```

然后我们现在需要把圆画出来，因为在后面要切割，所以这里其实怎么画都没问题，不过为了严谨我们还是正规点画个圆就行。

```csharp
if(isOpen == true)
{
	e.Graphics.FillEllipse(new SolidBrush(OpenColor),0, 0, Diameter, Diameter);
}
else
{
	e.Graphics.FillEllipse(new SolidBrush(CloseColor), 0, 0, Diameter, Diameter);
}
```

这两句话的意思是使用开启颜色或关闭颜色画个直径为我们设定直径的圆。

然后最重要的一步来了，虽然我们当前画出来了一个圆，它的样子和我们所需要的样式相同了，但是其本质上还是一个矩形，只是矩形上面画了一个圆而已，而在点击的时候其实点在这个矩形的空白部分我们仍然等同于点到了这个控件。

这时候，我们需要用Region把这个圆的区域抠出来，具体做法就是新建一个`System.Drawing.Drawing2D.GraphicsPath`的对象，然后用它在正确位置抠出一个和我们画出的圆一样大小的圆，这样就刚好吧我们需要的圆抠出来了。

```csharp
System.Drawing.Drawing2D.GraphicsPath path = new System.Drawing.Drawing2D.GraphicsPath();
path.AddEllipse(0, 0, Diameter, Diameter);
Region = new Region(path);
```

现在，我们就真正有了一个圆形的开关了。

## 添加事件

之前我们在属性中使用的事件，可以自己新增事件库进行管理，新建类，然后将其设为public并继承自EventArgs，接着新建事件并设计这个事件的参数和执行的操作。

```csharp
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DemoControls
{
    public class TestEventArgs : EventArgs
    {
        public TestEventArgs(object value)
        {
            Value = value;
        }

        public object Value { get; set; }
    }
}
```

同时我们还可以把这个事件设为默认事件，在开头部分我们定义这个控件类的默认事件为我们前面注册的TestSwitch。

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/20b434b3f3024c7e349b2480e5496d4f.png#pic_center)


## 使用这个控件

那么该如何使用这个控件呢？你可以新建一个工程（一般情况下建议新建工程来使用控件，而控件库单独用一个工程来管理，你未来所有的控件都可以放在控件库里），如果在本解决方案中的话，只需要在解决方案管理器中右键点击你的控件库工程名，选择生成，然后你就可以当前解决方案的任意工程中使用你控件库里的所有控件了。

而如果你需要在外部使用你的控件库，可以在生成后，进入到你的工程文件夹，Debug或者Release文件夹里的dll文件。如果你需要在某一个工程中使用这个控件的话，就在新工程里点击工具-选择工具箱项，点击浏览，然后添加刚才那个dll文件即可。

现在我们在当前解决方案试试看吧：

生成文件、新建工程、然后开始使用设计页面，可以发现设计页面最开头添加了我们的控件库：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/533f3dc5f5f6af437880e1b5a233b25e.png#pic_center)


然后我们拖出来两个，设置一下他们的大小和颜色：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/ee732094f8a4b7749553b2667701621e.png#pic_center)


同时双击第一个控件增添事件功能：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/6cced7a1cc2475ecca74f99e70f751fa.png#pic_center)


最后启动：

![在这里插入图片描述](https://i-blog.csdnimg.cn/blog_migrate/f03246cf7249a979453708845785e066.gif#pic_center)


成功。

[完整的工程下载地址](https://github.com/yunwuhai/TestControlsLib)