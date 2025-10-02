---
title: "STM32 HAL库 USB使用简析"
categories: 
- 嵌入式/USB
tags: 
- USB
license: CC-BY-SA 4.0
date: 2025-09-21T15:07:00+08:00
author: 云雾海
contact: yunwuhai@outlook.com
draft: true
---


# STM32 HAL库 USB使用简析

> [!NOTE]
>
> 这是我在学习USB的实践笔记，理论部分可以参考《[USB基础概念](https://yunwuhai.github.io/posts/%E5%B5%8C%E5%85%A5%E5%BC%8F/usb/usb%E5%9F%BA%E7%A1%80%E6%A6%82%E5%BF%B5/)》。水平有限，如有发现错误遗漏，欢迎指出。

## CubeMX配置

我使用的CubeMX+VSCode+OpenOCD的开发环境，其它环境大部分操作同理。

选择芯片，如果还没有确定好要用什么芯片，也可以直接在CubeMX中进行芯片选型。我的芯片是STM32F103RCT6。

![选择芯片](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921152011749.png)

进入到配置界面后，按照如下顺序快速进行一些基础配置：

**配置SWD**

![配置SWD](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921152921971.png)

**配置时钟**

![配置晶振](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921153029954.png)

**调整晶振频率** 

注意这里只用调整晶振频率就可以了，因为打开USB后会自动配置其它部分

![调整晶振频率](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921153651439.png)

**打开USB**

因为不同芯片的USB配置不同（部分可能支持High Speed、Low Speed模式），这里可能会有所差异，根据自己需要进行选择。

![打开USB](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921153900296.png)

**配置USB设备模式配置**

根据自己的需要进行配置，我准备实现自定义USB设备，但是如果完全手写会很麻烦，而且我对USB开发尚不熟悉，目前先选择CDC模式，并在此基础生成的工程上进行修改。

因为后面要自己配置，所以下面的配置没必要修改，当然如果你想修改也可以根据自己的需要进行修改。

![配置USB设备模式配置](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921154613968.png)

**再次配置时钟**

在前面打开USB的时候，就应该可以注意到Clock Configuration出现了一个红叉报错，重新进入时钟配置界面，可以发现一个提示可以自动配置始终的提示，点击Yes。

![再次配置时钟](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921154939786.png)

**完成项目配置**

接下来完成项目设置即可，生成完成后点击close，然后前往项目文件夹，通过你的开发软件打开。

![配置项目](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921155115553.png)

![生成.c和.h文件](./assets/image-20250921155147081.png)

![生成完成，点击Close](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921155249231.png)

![image-20250921155410341](./assets/image-20250921155410341.png)

## 项目文件

### 根路径文件和文件夹

我使用VSCode打开了项目文件夹，现在观察项目在根路径上的结构。

![根路径](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921160010153.png)

**可以忽略的部分：**项目中的这些部分不会影响到我们的编程，我们不会在笔记中详细探讨。

- .vscode：由vscode生成。
- build：编译文件所在位置。
- cmake：编译配置文件所在位置，该文件夹由STM32CubeMX生成，里面包含了由CubeMX生成的CMakeLists文件，不需要用户手动修改。
- .mxproject、STM32F103RCT6_USB_Test.ioc：cubemx的配置文件。
- CMakePresets.json：CMake的控制文件，不需要手动设置。
- startup_stm32f103xe.s、STM32F103XX_FLASH.ld：项目的引导和链接文件，前者是固定的没必要修改，后者是编译后自动生成的。

*CMakeLists.txt文件是仅当我们在cubeMX中选择cmake项目的时候会生成的，通过在里面增添自己写的c文件和库文件夹来完成编译，对于其它平台的项目可以忽略。*

### Core

#### main.c

现在我们先关注Core文件夹，这个文件夹中有我们的核心逻辑。

![Core文件夹](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921195604226.png)

因为我们只需要关注USB的开发，所以里面绝大多数文件也可以忽略，现在让我们首先关注main.c文件。

![头文件](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921200134212.png)

可以注意到，这里引用了一个`usb_device.h`的文件，显然，这里面会有关于USB部分的关键内容，不过先让我们继续往下看。

![main函数中的USB](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921200402638.png)

在生成的`main`函数中出现了`MX_USB_DEVICE_Init`文件，很显然，关于USB初始化的核心逻辑就在这里面了。

尽管`main.c`部分关于USB的东西应该就这些东西了，但是我们还是看看还有没有其它地方有关于USB的配置。直接在`main.c`文件中搜索`USB`，然后就可以看到：

![SystemClock中的USB](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921200740459.png)

这段内容出现在`void SystemClock_Config(void)`函数中，显然这里是对USB外设的时钟配置，这部分在CubeMX中已经配好了，我们无需要再关注了。

另外我们也可以检查以下`main.h`文件，可以发现里面也没有其它关于USB的内容了。

通过上述部分我们可以知道，在CubeMX生成的文件中，关于USB做了两件事，其一是配置了USB的时钟，其二就是进行了USB设备的初始化。关于时钟配置的部分我们已经看完了，后面我们只需要关注USB的初始化即可。

#### stm32f1xx_it.c和stm32f1xx_it.h

不过我们知道，嵌入式设备除了基本的顺序逻辑外，还存在中断的概念，这里面可能也存在关于USB的相关中断，让我们点开`stm32f1xx_it.c`查看一下。通过搜索USB，可以很快发现一个从外部导入的变量。

![hpcd_USB_FS](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921202043366.png)

我们通过这个变量跳转一下，可以发现这个变量被定义在`USB_DEVICE`这个文件夹下面的文件中。

![hpcd_USB_FS的定义位置](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921202247216.png)

其实我们在`main.c`文件中也进行一下跳转，会发现`usb_device.h`还有`MX_USB_DEVICE_Init`的内容也都在这个文件夹下面。

不过我们先不着急探究它们是做什么的，现在继续往下查看，会发现一个关于USB的中断函数：

![USB_LP_CAN1_RX0_IRQHandler](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921203416885.png)

根据注释可以发现，这个函数是用来处理USB低优先级中断和CAN接收中断的，其中有一个`HAL_PCD_IRQHandler`的中断处理函数。尝试跳转会发现它有两个定义，并通过`USB`和`USB_OTG_FS`两个标志进行开关，因为我们没有使用OTG功能，所以现在只有`USB`这一个标志是定义了的。

![image-20250921203824932](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921203824932.png)

这个函数被定义在Drivers文件夹的STM32F1xx_HAL_Driver文件夹中，让我们点进去看一看这个函数是做什么的？

```c
void HAL_PCD_IRQHandler(PCD_HandleTypeDef *hpcd)
{
  uint32_t wIstr = USB_ReadInterrupts(hpcd->Instance);
  uint16_t store_ep[8];
  uint8_t i;

  if ((wIstr & USB_ISTR_CTR) == USB_ISTR_CTR)
  {
    /* servicing of the endpoint correct transfer interrupt */
    /* clear of the CTR flag into the sub */
    (void)PCD_EP_ISR_Handler(hpcd);

    return;
  }

  if ((wIstr & USB_ISTR_RESET) == USB_ISTR_RESET)
  {
    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_RESET);

#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)
    hpcd->ResetCallback(hpcd);
#else
    HAL_PCD_ResetCallback(hpcd);
#endif /* USE_HAL_PCD_REGISTER_CALLBACKS */

    (void)HAL_PCD_SetAddress(hpcd, 0U);

    return;
  }

  if ((wIstr & USB_ISTR_PMAOVR) == USB_ISTR_PMAOVR)
  {
    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_PMAOVR);

    return;
  }

  if ((wIstr & USB_ISTR_ERR) == USB_ISTR_ERR)
  {
    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_ERR);

    return;
  }

  if ((wIstr & USB_ISTR_WKUP) == USB_ISTR_WKUP)
  {
    hpcd->Instance->CNTR &= (uint16_t) ~(USB_CNTR_LP_MODE);
    hpcd->Instance->CNTR &= (uint16_t) ~(USB_CNTR_FSUSP);

#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)
    hpcd->ResumeCallback(hpcd);
#else
    HAL_PCD_ResumeCallback(hpcd);
#endif /* USE_HAL_PCD_REGISTER_CALLBACKS */

    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_WKUP);

    return;
  }

  if ((wIstr & USB_ISTR_SUSP) == USB_ISTR_SUSP)
  {
    /* WA: To Clear Wakeup flag if raised with suspend signal */

    /* Store Endpoint registers */
    for (i = 0U; i < 8U; i++)
    {
      store_ep[i] = PCD_GET_ENDPOINT(hpcd->Instance, i);
    }

    /* FORCE RESET */
    hpcd->Instance->CNTR |= (uint16_t)(USB_CNTR_FRES);

    /* CLEAR RESET */
    hpcd->Instance->CNTR &= (uint16_t)(~USB_CNTR_FRES);

    /* wait for reset flag in ISTR */
    while ((hpcd->Instance->ISTR & USB_ISTR_RESET) == 0U)
    {
    }

    /* Clear Reset Flag */
    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_RESET);

    /* Restore Registre */
    for (i = 0U; i < 8U; i++)
    {
      PCD_SET_ENDPOINT(hpcd->Instance, i, store_ep[i]);
    }

    /* Force low-power mode in the macrocell */
    hpcd->Instance->CNTR |= (uint16_t)USB_CNTR_FSUSP;

    /* clear of the ISTR bit must be done after setting of CNTR_FSUSP */
    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_SUSP);

    hpcd->Instance->CNTR |= (uint16_t)USB_CNTR_LP_MODE;

#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)
    hpcd->SuspendCallback(hpcd);
#else
    HAL_PCD_SuspendCallback(hpcd);
#endif /* USE_HAL_PCD_REGISTER_CALLBACKS */

    return;
  }

  if ((wIstr & USB_ISTR_SOF) == USB_ISTR_SOF)
  {
    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_SOF);

#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)
    hpcd->SOFCallback(hpcd);
#else
    HAL_PCD_SOFCallback(hpcd);
#endif /* USE_HAL_PCD_REGISTER_CALLBACKS */

    return;
  }

  if ((wIstr & USB_ISTR_ESOF) == USB_ISTR_ESOF)
  {
    /* clear ESOF flag in ISTR */
    __HAL_PCD_CLEAR_FLAG(hpcd, USB_ISTR_ESOF);

    return;
  }
}
```

稍微观察一下，不难发现，虽然这段代码很长，但是它们其实一直在做一件重复的事情：比对`wIstr`变量的值，如果比对成功则进入一段处理程序，处理完成后就直接return。

其中`wIstr`是`USB_ReadInterrupts`函数的返回值，而我们查看这个函数的注释，不难发现，它的返回值代表了当前中断的状态码。

![USB_ReadInterrupts](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921210024807.png)

所以其实在这个函数中，每次if判断，都是在判断正在处理的这个中断是个什么中断，然后调用对应的回调函数去处理它。

此外，我们可以注意到其中还有一些特殊的宏判断，它们的写法都是`#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)`，当这个宏定义被设置为`1U`的时候，就会执行由`hpcd`设定的回调函数。

当然我们也不需要
