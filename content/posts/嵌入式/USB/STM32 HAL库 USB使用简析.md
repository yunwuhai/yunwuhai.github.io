---
title: "STM32 HAL库 USB使用简析"
categories: 
- USB
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

### 选择芯片

我使用的CubeMX+VSCode+OpenOCD的开发环境，其它环境大部分操作同理。

选择芯片，如果还没有确定好要用什么芯片，也可以直接在CubeMX中进行芯片选型。我的芯片是STM32F103RCT6。

![选择芯片](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921152011749.png)

进入到配置界面后，按照如下顺序快速进行一些基础配置。

### 基础配置

#### 配置SWD

![配置SWD](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921152921971.png)

#### 配置时钟

![配置晶振](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921153029954.png)

#### 调整晶振频率 

注意这里只用调整晶振频率就可以了，因为打开USB后会自动配置其它部分

![调整晶振频率](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921153651439.png)

#### 打开USB

因为不同芯片的USB配置不同（部分可能支持High Speed、Low Speed模式），这里可能会有所差异，根据自己需要进行选择。

![打开USB](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921153900296.png)

#### 配置USB设备模式配置

根据自己的需要进行配置，我准备实现自定义USB设备，但是如果完全手写会很麻烦，而且我对USB开发尚不熟悉，目前先选择CDC模式，并在此基础生成的工程上进行修改。

因为后面要自己配置，所以下面的配置没必要修改，当然如果你想修改也可以根据自己的需要进行修改。

![配置USB设备模式配置](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921154613968.png)

#### 再次配置时钟

在前面打开USB的时候，就应该可以注意到Clock Configuration出现了一个红叉报错，重新进入时钟配置界面，可以发现一个提示可以自动配置始终的提示，点击Yes。

![再次配置时钟](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921154939786.png)

#### 完成项目配置

接下来完成项目设置即可，生成完成后点击close，然后前往项目文件夹，通过你的开发软件打开。

![配置项目](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921155115553.png)

![生成.c和.h文件](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921155147081.png)

![生成完成，点击Close](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921155249231.png)

![image-20250921155410341](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921155410341.png)

## 项目文件分析

### 项目整体结构分析

我使用VSCode打开了项目文件夹，现在观察项目在根路径上的结构。

![根路径](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921160010153.png)

#### 可以忽略的部分

项目中的这些部分不会影响到我们的编程，我们不会在笔记中详细探讨。

- .vscode：由vscode生成。
- build：编译文件所在位置。
- cmake：编译配置文件所在位置，该文件夹由STM32CubeMX生成，里面包含了由CubeMX生成的CMakeLists文件，不需要用户手动修改。
- .mxproject、STM32F103RCT6_USB_Test.ioc：cubemx的配置文件。
- CMakePresets.json：CMake的控制文件，不需要手动设置。
- startup_stm32f103xe.s、STM32F103XX_FLASH.ld：项目的引导和链接文件，前者是固定的没必要修改，后者是编译后自动生成的。

*CMakeLists.txt文件是仅当我们在cubeMX中选择cmake项目的时候会生成的，通过在里面增添自己写的c文件和库文件夹来完成编译，对于其它平台的项目可以忽略。*

#### Core

Core是核心逻辑文件夹，里面负责项目的核心逻辑，不关注接口实现，这里面的文件内容和USB基本不相关。

![image-20251111165930414](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251111165930414.png)

#### Drivers

Drivers是驱动文件夹，里面装有CMSIS库和HAL库，虽然涉及了USB底层内容，但和协议并不高度相关，我们仅在用到的时候讨论。

![image-20251111170123925](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251111170123925.png)

#### Middlewares

Middlewares是中间件文件夹，里面的内容是从STM32提供的官方USB库中直接拷贝过来的，通常我们不需要修改里面的内容，但是里面的文件我们需要详细研究。

![image-20251111170259247](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251111170259247.png)

- Core文件夹：包含了USB设备库状态机，它由USB2.0规范定义。
  - usbd_core(.c,.h)：此文件包含了处理所有USB通信和状态机的函数
  - usbd_ctlreq(.c,.h)：此文件的程序用于解析和处理USB控制管道上的请求。
  - usbd_ioreq(.c,.h)：此文件的程序用于执行USB控制管道上具体的数据收发。
  - usbd_def(.h)：通用的库定义。
  - 另外两个template是模板文件，它们已经通过CubeMX的修改，在USB_DEVICE文件夹里面生成了相应的文件。
- Class文件夹：包含了USB类实现相关的文件，因为我们在最开始选择的CDC设备，所以这里显示的就是CDC的类定义。CDC是虚拟通信端口处理程序。其中的template文件也是被生成在USB_DEVICE里面了。

#### USB_DEVICE

USB_DEVICE是USB设备配置文件夹，里面包含了关于USB的具体配置，通常来说我们需要在里面进行相关的设置，同时我们刚刚通过CubeMX配置的和USB相关的东西也基本都是生成在这里。

![image-20251111170443416](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251111170443416.png)

可以注意到，里面的`usbd_cdc_if(.c,.h)`、`usbd_desc(.c,.h)`、`usbd_conf(.c,.h)`都是通过前面的Middlewares里面的USB官方库生成的。

- App文件夹
  - usb_device(.c,.h)：USB的总体核心业务实现。
  - usbd_cdc_if(.c,.h)：CDC类接口实现。
  - usbd_desc(.c,.h)：设备描述符定义。
- Target文件夹
  - usbd_conf(.c,.h)：USB驱动配置。

### Core文件夹分析

#### main.c

##### USB系统初始化

让我们关注main文件，看向main函数。

![main函数中的USB](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921200402638.png)

在生成的`main`函数中出现了`MX_USB_DEVICE_Init`函数，字面意义上来看，这个对USB设备的初始化。

##### USB时钟初始化

另外我们可以直接在`main.c`文件中搜索`USB`，然后就可以看到：

![SystemClock中的USB](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921200740459.png)

这段内容出现在`void SystemClock_Config(void)`函数中，显然这里是对USB外设的时钟配置，这部分在CubeMX中已经配好了，我们无需要再关注了。

另外在`main.h`文件中没有关于USB的相关信息，我们不对其进行讨论。

#### stm32f1xx_it.c

##### PCD

通过在`stm32f1xx_it.c`文件中搜索USB，可以找到一个带USB的控制句柄。

![hpcd_USB_FS](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921202043366.png)

可以发现这个类型是`PCD_HandleTypeDef`的句柄，PCD的全称是`USB Physical Layer Circuit`，它负责STM32微控制器与USB物理接口的底层通信。通过类型名称可以跳转到`stm32f1xx_hal_pcd.h`的文件中，它对应了`stm32f1xx_hal_pcd.c`文件。对于USB协议栈而言，PCD是软件层面的最底层，它负责操作硬件的寄存器，USB协议栈上层所有的操作实际上都是通过调用PCD实现的。

我们通过这个变量跳转一下，可以发现这个变量被定义在`USB_DEVICE`的`usbd_conf.c`文件中，说明这个句柄和USB驱动配置相关，而且从名字上来看，它显然在USB协议栈和PCD之间的控制通信中发挥作用。

##### USB中断

继续往下查看，会发现`USB_LP_CAN1_RX0_IRQHandler`函数，从注释上来看，它负责管理USB低优先级中断或者CAN接收0中断，我们没有使用CAN总线，显然这里就是负责了USB低优先级中断：

![USB_LP_CAN1_RX0_IRQHandler](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921203416885.png)

内部有一个`HAL_PCD_IRQHandler`的中断处理函数。尝试跳转会发现它有两个定义，并通过`USB`和`USB_OTG_FS`两个标志进行开关，因为我们没有使用OTG功能，所以现在只有`USB`这一个标志是定义了的。

![image-20250921203824932](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921203824932.png)

这个函数被定义在`stm32f1xx_hal_pcd.c`文件中：

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

稍微观察一下，不难发现，虽然这段代码很长，但是它们其实一直在做一件重复的事情：比对`wIstr`变量的值，如果比对成功则进入一段处理程序，处理完成后就直接return。其中`wIstr`是`USB_ReadInterrupts`函数的返回值：

![USB_ReadInterrupts](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20250921210024807.png)

我们查看这个函数的注释，不难发现，它的返回值代表了当前中断的状态码。

所以其实在这个函数中，每次if判断，都是在判断正在处理的这个中断是个什么中断，然后调用对应的回调函数去处理它，以下是可能出现的中断。

![image-20251112112021022](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251112112021022.png)

此外，我们可以注意到其中还有一些特殊的宏判断，它们的写法都是`#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)`，当这个宏定义被设置为`1U`的时候，就会执行由`hpcd`设定的回调函数，而非`HAL_PCD_xxCallback`这种HAL库函数。关于这个宏定义的设置，可以在`Core`文件夹下的`stm32f1xx_hal_conf.h`文件里看到，它可以在CubeMX的Project Manager界面的右边进行设置。

![image-20251112192237112](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251112192237112.png)

通常情况我们不需要打开这个功能，但是如果在一些情况下已经有固定代码不想重复造轮子，那么就可以打开该功能，并通过`HAL_PCD_RegisterCallback`对函数进行绑定，当然也可以通过`HAL_PCD_UnRegisterCallback`进行解绑，解绑之后`hpcd`里面的回调函数指针就又是指向`HAL_PCD_xxCallback`函数了。

##### PCD回调函数

对于`HAL_PCD_xxCallback`这类回调函数，我们可以对其进行自定义。

让我们随便跳转一个现有的回调函数，比如`HAL_PCD_ResetCallback`，然后我们就可以看到它的函数定义：

```c
__weak void HAL_PCD_ResetCallback(PCD_HandleTypeDef *hpcd)
{
  /* Prevent unused argument(s) compilation warning */
  UNUSED(hpcd);

  /* NOTE : This function should not be modified, when the callback is needed,
            the HAL_PCD_ResetCallback could be implemented in the user file
   */
}
```

我们注意到这个函数前面有一个`__weak`标记，表示这是一个弱函数，而如果我们再自行定义一个同样的普通函数，比如：

```c
void HAL_PCD_ResetCallback(PCD_HandleTypeDef *hpcd)
{
    // 加上你希望执行的代码
}
```

这样就可以完成定义的覆盖，在编译期间，原本的弱函数就会被放弃，而这段普通函数的代码才会被编译和最终执行。不过这里有非常多的回调函数，并且我们知道USB执行的过程非常复杂，如果我们从零开始挨个编写这些回调函数，那将会非常麻烦和复杂。

不过还记得我们在CubeMX中打开的USB_Device组件吗，并且当时设置了CDC模式还进行了一定的配置，会不会有可能这些回调函数其实已经被预生成了一遍了？

验证的方法很简单，我们只需要随便选择一个回调函数，然后使用VSCode的全局搜索功能搜索一下就知道了，比如我们还是选择`HAL_PCD_ResetCallback`这个函数：

![image-20251016212209880](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251016212209880.png)

可以发现它的定义出现在了两个c文件中，其中一个是我们刚才看过的弱函数，而另一个很显然是普通函数，其位于`usbd_conf.c`函数中，通过跳转可以观察其实现：

![image-20251112200522789](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251112200522789.png)

可以发现其中调用了三个函数，其中`Error_Handler`被定义在main.c文件中，`USBD_LL_SetSpeed`和`USBD_LL_Reset`两个函数则都被定义在Middlewares文件夹下USB库里的usbd_core.c文件中，我们无需修改。

### Middlewares文件夹分析

#### usbd_core(.c,.h)

两个文件定义和声明了大量函数，我们可以对其进行分类。

##### 设备管理函数 (设备核心层)

###### 设备生命周期管理

- **USBD_Init** - 初始化USB设备核心，配置描述符与ID
- **USBD_DeInit** - 释放USB设备资源，撤销初始化
- **USBD_Start** - 启动USB设备，使其可被主机识别
- **USBD_Stop** - 停止USB设备运行
- **USBD_RunTestMode** - 进入USB合规性测试模式，CDC生成模板中并没有提供具体实现

###### 设备类管理

- **USBD_RegisterClass** - 注册特定USB设备类(如HID、CDC、MSC)
- **USBD_SetClassConfig** - 为指定配置索引设置类特定参数
- **USBD_ClrClassConfig** - 清除指定配置索引的类特定参数

##### USB协议事件处理函数

###### 控制传输处理

- **USBD_LL_SetupStage** - 处理USB控制传输的Setup阶段
- **USBD_LL_DataOutStage** - 处理主机到设备的数据传输阶段
- **USBD_LL_DataInStage** - 处理设备到主机的数据传输阶段

###### USB总线事件

- **USBD_LL_Reset** - 处理总线复位事件
- **USBD_LL_SetSpeed** - 设置USB通信速度(全速/高速)
- **USBD_LL_Suspend** - 处理总线挂起事件
- **USBD_LL_Resume** - 处理从挂起状态恢复的事件
- **USBD_LL_SOF** - 处理帧起始(SOF)包事件
- **USBD_LL_IsoINIncomplete** - 处理等时IN端点不完整传输，CDC生成模板中并没有提供具体实现
- **USBD_LL_IsoOUTIncomplete** - 处理等时OUT端点不完整传输，CDC生成模板中并没有提供具体实现
- **USBD_LL_DevConnected** - 设备连接到主机时调用，CDC生成模板中并没有提供具体实现
- **USBD_LL_DevDisconnected** - 设备从主机断开时调用

---

上述函数均被定义于usbd_core.c文件中，而下面的函数虽然声明于usbd_core.h中，但被定义于usbd_conf.c中。这是因为usbd_core主要用于处理USB的核心逻辑，而usbd_conf则提供硬件交互。

---

#### usbd_conf.c（USBD_LL部分）

##### 底层硬件抽象层函数 (LL - Low Level)

###### 硬件控制

- **USBD_LL_Init** - 初始化USB外设硬件
- **USBD_LL_DeInit** - 释放USB外设硬件资源
- **USBD_LL_Start** - 启动底层USB硬件操作
- **USBD_LL_Stop** - 停止底层USB硬件操作
- **USBD_LL_Delay** - 提供精确延时，用于USB时序要求

###### 端点(Endpoint)管理

- **USBD_LL_OpenEP** - 配置并激活指定端点(地址、类型、最大包大小)
- **USBD_LL_CloseEP** - 关闭指定端点
- **USBD_LL_FlushEP** - 清空端点的FIFO缓冲区
- **USBD_LL_StallEP** - 将端点置于STALL状态(错误处理)
- **USBD_LL_ClearStallEP** - 清除端点的STALL状态
- **USBD_LL_IsStallEP** - 检查端点是否处于STALL状态
- **USBD_LL_SetUSBAddress** - 设置设备USB地址(枚举过程)

###### 数据传输

- **USBD_LL_Transmit** - 通过指定IN端点发送数据
- **USBD_LL_PrepareReceive** - 为指定OUT端点准备接收缓冲区
- **USBD_LL_GetRxDataSize** - 获取指定OUT端点接收到的数据大小
- **USBD_LL_Delay** - 延时函数

#### usbd_ctlreq(.c,.h)

- **USBD_StdDevReq** - 处理标准 USB 设备请求
- **USBD_StdItfReq** - 处理标准 USB 接口请求
- **USBD_StdEPReq** - 处理标准 USB 端点请求
- **USBD_CtlError** - 处理控制管道上的 USB 错误
- **USBD_ParseSetupRequest** - 将请求缓冲复制到设置结构体。
- **USBD_GetString** - 将ASCII字符串转换为Unicode

### USB_DEVICE文件夹分析

同样，让我们首先观察一下这个文件夹的整体结构：

![image-20251016221458373](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251016221458373.png)

很显然，文件夹由两个部分组成，其一是App，另一部分是Target。既然我们刚刚查询到USB中断里面的回调函数在Target文件夹中的`usbd_conf.c`文件中被重新定义了，那就让我们先关注Target这个文件夹吧。

#### usbd_conf.c

首先打开`usbd_conf.c`文件，从名字上易知该文件中应该是USB基础设置相关的内容。

##### 引用

首先我们观察一下它的引用文件，来确定它的依赖关系。

![image-20251017112425783](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251017112425783.png)

这五个`.h`文件来自两个部分，首先是以`stm32f1xx_`开头的两个文件，它们来自于Drivers文件夹中的STM32F1xx_HAL_Driver文件夹，是STM32HAL库的内容，我们无需修改它们。它们内部API的使用也不是我们这篇文章关注的内容。

然后是剩下三个以`usbd_`开头的文件，很显然，usbd的意思就是USB  Device，而这三个文件则位于`Middlewares\ST\STM32_USB_Device_Library`文件夹中，是STM32提供的USB设备驱动库，同样我们也不需要修改它们。而其中我们继续细分，可以发现`usbd_def.h`和`usbd_core.h`位于驱动文件夹的`Core`文件夹中，相当于USB Device的通用部分，而`usbd_cdc.h`则位于驱动文件夹的`Class\CDC`文件夹中，显然，这个头文件的内容是专门针对CDC这种设备类协议的。

另外我们可以注意到其中并没有引用`usbd_conf.h`文件，显然它对应的头文件只是为了给外部提供接口用的。

##### PCD句柄

首先，我们可以发现这里声明了一个PCD的控制句柄`hpcd_USB_FS`。

```c
PCD_HandleTypeDef hpcd_USB_FS;
```

PCD是Peripheral Control Driver的缩写，即外设控制驱动程序，而h代表Handle，即句柄。这个结构体包含USB设备控制器的各种信息，如设备实例、端点配置、传输状态等。通过这个句柄，USB设备库可以与底层硬件进行交互，执行如初始化、打开关闭端点、数据传输等操作。这个我们在`stm32f1xx_it.c`中已经发现过一次了。

##### 函数声明

继续往下翻，可以发现`usbd_conf.c`文件有几个函数声明：

```c
void Error_Handler(void);

static USBD_StatusTypeDef USBD_Get_USB_Status(HAL_StatusTypeDef hal_status);

#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)
static void PCDEx_SetConnectionState(PCD_HandleTypeDef *hpcd, uint8_t state);
#else
void HAL_PCDEx_SetConnectionState(PCD_HandleTypeDef *hpcd, uint8_t state);
#endif /* USE_HAL_PCD_REGISTER_CALLBACKS */
```

其中`Error_Handler`是用于处理错误情况的中断，这个中断在main.c中被定义的，内容可以自行修改。

![image-20251017225214523](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251017225214523.png)

而`USBD_Get_USB_Status`这个函数被定义在当前文件中，它的作用是根据HAL状态返回USB的状态，本质上就是一个状态码的映射转换。

至于`PCDEx_SetConnectionState`和`HAL_PCDEx_SetConnectionState`这两个函数，会因为宏定义的不同而存在名称上的差异，但是本质上是实现的同一个功能，即根据传入的连接状态`state`来配置USB设备的连接状态（连接或断开），并且不同状态可以执行不同的操作，可以根据需要进行修改：

![image-20251017225945109](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251017225945109.png)

##### HAL_PCD_xx系列函数

在我们看完这几个函数声明后，现在可以看看里面定义的函数了，当然我们不需要每个都仔细看，现在打开大纲，然后可以发现，在这个文件中有大量以`HAL_PCD_`开头的函数：

![image-20251018220238396](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251018220238396.png)

在这一部分的开头有一个注释：

![image-20251018220420358](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251018220420358.png)

这代表这一部分的数据是PCD传递数据给USB设备的。我们可以随便搜索一个函数，比如`HAL_PCD_MspInit`，可以发现它被`stm32f1_hal_pcd.c`这个HAL库文件广泛使用：

![image-20251018220632280](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251018220632280.png)

同时观察一下这个文件的大纲：

![image-20251018220923231](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251018220923231.png)

不难发现其中出现了很多刚才出现在`usbd_conf.c`中出现的`HAL_PCD_`开头的函数，如果你点过去看，可以发现它们全都带着`__weak`标志。

此外我们还可以发现，在`usbd_conf.c`中这些`HAL_PCD_`开头的函数，除了`HAL_PCD_MspInit`和`HAL_PCD_MspDeInit`之外，开头的函数末尾都有`Callback`代表回调函数。

我们可以随便选择一个回调函数看一下它的构成，这样可以帮助我们理解这里的其它回调函数，以SOF回调为例：

```c
/**
  * @brief  SOF callback.
  * @param  hpcd: PCD handle
  * @retval None
  */
#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)
static void PCD_SOFCallback(PCD_HandleTypeDef *hpcd)
#else
void HAL_PCD_SOFCallback(PCD_HandleTypeDef *hpcd)
#endif /* USE_HAL_PCD_REGISTER_CALLBACKS */
{
  USBD_LL_SOF((USBD_HandleTypeDef*)hpcd->pData);
}
```

不难发现，它也是和前面那个`HAL_PCDEx_SetConnectionState`一样用了宏定义来取了两个名，根据项目目前的设置，它实际上使用的是`HAL_PCD_SOFCallback`这个名字。而观察其内容，其实就是调用了`USB_LL_SOF`这个函数，通过跳转可以发现这个函数被定义在`usbd_core.c`中。

现在让我们来思考为什么要这样设计？回调函数在STM32的HAL库中通常出现在将逻辑与硬件解耦的情况下，比如中断。而此处的SOF也是如此，STM32有不同的芯片，有HAL库和LL库，但它们都可能需要检测SOF事件，故直接将它们共同定义成一个SOF回调函数，这样在HAL库中就可以直接使用这个逻辑而不在意和硬件的交互了。

而SOF事件是由USB协议制定的，针对一个USB库，必然也需要实现这样一个SOF的处理流程，只是不同库的底层结构会有所不同，比如拥有不同结构的句柄。在这里我们通过CubeMX使用了`STM32_USB_Device_Library`这个中间库，而其针对SOF事件的操作函数就是`USBD_LL_SOF`函数，所以我们只需要在回调函数中调用这个函数即可。

通过这样的设计，最终实现了逻辑与硬件解耦，协议与驱动解耦。

在理解了前面`HAL_PCD_xxCallback`这类函数后，我们已经初窥STM32的HAL库和USB库的关系了，并且大概理解到`usbd_conf.c`之所以在`Target`这么个文件夹里面，显然是作为一个沟通桥梁连接两个库的。

##### USBD_LL_xx系列函数

那么接下来我们看到下面一堆`USBD_LL_`开头的函数，就会很好理解了。

![image-20251019185743424](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019185743424.png)

显然，它们是原属于被声明在`STM32_USB_Device_Library`这个库里的函数，但是我们知道`LL`的全称其实就是`Low Layer`，而这些操作也显然和硬件密切相关，它们的具体实现需要涉及硬件操作，所以就在`usbd_conf.c`文件里面完成。

以`USBD_LL_Init`为例，我们观察一下它的具体实现：

```c
/**
  * @brief  Initializes the low level portion of the device driver.
  * @param  pdev: Device handle
  * @retval USBD status
  */
USBD_StatusTypeDef USBD_LL_Init(USBD_HandleTypeDef *pdev)
{
  /* Init USB Ip. */
  /* Link the driver to the stack. */
  hpcd_USB_FS.pData = pdev;
  pdev->pData = &hpcd_USB_FS;

  hpcd_USB_FS.Instance = USB;
  hpcd_USB_FS.Init.dev_endpoints = 8;
  hpcd_USB_FS.Init.speed = PCD_SPEED_FULL;
  hpcd_USB_FS.Init.low_power_enable = DISABLE;
  hpcd_USB_FS.Init.lpm_enable = DISABLE;
  hpcd_USB_FS.Init.battery_charging_enable = DISABLE;
  if (HAL_PCD_Init(&hpcd_USB_FS) != HAL_OK)
  {
    Error_Handler( );
  }

#if (USE_HAL_PCD_REGISTER_CALLBACKS == 1U)
  /* Register USB PCD CallBacks */
  HAL_PCD_RegisterCallback(&hpcd_USB_FS, HAL_PCD_SOF_CB_ID, PCD_SOFCallback);
  HAL_PCD_RegisterCallback(&hpcd_USB_FS, HAL_PCD_SETUPSTAGE_CB_ID, PCD_SetupStageCallback);
  HAL_PCD_RegisterCallback(&hpcd_USB_FS, HAL_PCD_RESET_CB_ID, PCD_ResetCallback);
  HAL_PCD_RegisterCallback(&hpcd_USB_FS, HAL_PCD_SUSPEND_CB_ID, PCD_SuspendCallback);
  HAL_PCD_RegisterCallback(&hpcd_USB_FS, HAL_PCD_RESUME_CB_ID, PCD_ResumeCallback);
  HAL_PCD_RegisterCallback(&hpcd_USB_FS, HAL_PCD_CONNECT_CB_ID, PCD_ConnectCallback);
  HAL_PCD_RegisterCallback(&hpcd_USB_FS, HAL_PCD_DISCONNECT_CB_ID, PCD_DisconnectCallback);

  HAL_PCD_RegisterDataOutStageCallback(&hpcd_USB_FS, PCD_DataOutStageCallback);
  HAL_PCD_RegisterDataInStageCallback(&hpcd_USB_FS, PCD_DataInStageCallback);
  HAL_PCD_RegisterIsoOutIncpltCallback(&hpcd_USB_FS, PCD_ISOOUTIncompleteCallback);
  HAL_PCD_RegisterIsoInIncpltCallback(&hpcd_USB_FS, PCD_ISOINIncompleteCallback);
#endif /* USE_HAL_PCD_REGISTER_CALLBACKS */
  /* USER CODE BEGIN EndPoint_Configuration */
  HAL_PCDEx_PMAConfig((PCD_HandleTypeDef*)pdev->pData , 0x00 , PCD_SNG_BUF, 0x18);
  HAL_PCDEx_PMAConfig((PCD_HandleTypeDef*)pdev->pData , 0x80 , PCD_SNG_BUF, 0x58);
  /* USER CODE END EndPoint_Configuration */
  /* USER CODE BEGIN EndPoint_Configuration_CDC */
  HAL_PCDEx_PMAConfig((PCD_HandleTypeDef*)pdev->pData , 0x81 , PCD_SNG_BUF, 0xC0);
  HAL_PCDEx_PMAConfig((PCD_HandleTypeDef*)pdev->pData , 0x01 , PCD_SNG_BUF, 0x110);
  HAL_PCDEx_PMAConfig((PCD_HandleTypeDef*)pdev->pData , 0x82 , PCD_SNG_BUF, 0x100);
  /* USER CODE END EndPoint_Configuration_CDC */
  return USBD_OK;
}
```

显然，它里面使用了大量HAL库，这代表这个功能的实现和HAL库，或者说当前平台息息相关。

然后我们可以搜索一下这个库的名称，看它在哪些地方被使用了？

![image-20251019190207174](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019190207174.png)

可以发现它在`usbd_core.c`文件中被使用了，被用于实现一个叫`USBD_Init`的函数，也就是USB的初始化。显然，USB初始化需要底层硬件的参与，不同平台的USB初始化的过程不可能一样，但是通过这样一个硬件层函数的移植，我们的`STM32_USB_Device_Library`就不需要理会其它平台的具体实现了，`USBD_Init`其它地方可以专心实现USB初始化的算法逻辑，而和硬件相关的部分交给`USBD_LL_Init`就可以了。

![image-20251019190311041](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019190311041.png)

这和我们的猜测完全一致。

显然，`usbd_conf.c`里面这些函数我们通常不需要修改，因为它们本身就是硬件到逻辑的实现，而这个逻辑是固定的，CubeMX生成的内容就已经足够。

#### usbd_conf.h

现在让我们将视线转移到`usbd_conf.h`中。

##### 引用

首先观察它的引用部分：

![image-20251019210107148](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019210107148.png)

前三个是C语言的标准库，main.h中初始状态只有一个`Error_Handler`函数的声明，文件中其实没有用到，可能是为了某种安全冗余，如果介意编译过程中一点非常小的损耗，可以删除这一行。剩余两个引用都是HAL库的内容。

##### USB基础配置

然后往下翻，可以发现一段非常重要的配置：

```c
/*---------- -----------*/
#define USBD_MAX_NUM_INTERFACES     1
/*---------- -----------*/
#define USBD_MAX_NUM_CONFIGURATION     1
/*---------- -----------*/
#define USBD_MAX_STR_DESC_SIZ     512
/*---------- -----------*/
#define USBD_DEBUG_LEVEL     0
/*---------- -----------*/
#define USBD_SELF_POWERED     1
/*---------- -----------*/
#define MAX_STATIC_ALLOC_SIZE     512

/****************************************/
/* #define for FS and HS identification */
#define DEVICE_FS 		0
```

这一部分定义了USB设备的一些配置参数：

1. `USBD_MAX_NUM_INTERFACES`：USB设备可以支持的最大接口数，如果希望设备是复合设备，就需要修改这个值。
2. `USBD_MAX_NUM_CONFIGURATION `：USB设备可以支持的最大配置数，在绝大多数情况下不需要修改。
3. `USBD_MAX_STR_DESC_SIZ`：USB字符串描述符的最大大小，代表了包括产品名、厂商名、序列号等一系列描述符的最大长度，但512字节已经足够大，通常不需要增大，如果内存紧张可以改小。不过正常情况不用管。
4. `USBD_DEBUG_LEVEL`：USB设备驱动的调试日志级别，数字越大信息越多，最大为3，可以在调试的时候设置为3。
5. `USBD_SELF_POWERED`：USB设备的电源模式，1表示自供电（设备有自己的电源），0表示总线供电（靠USB的5V供电）。
6. `MAX_STATIC_ALLOC_SIZE`：静态内存分配的最大大小，根据传输的数据包大小进行调整。
7. `DEVICE_FS`：USB全速模式，这里设置为0是因为它是一个id，当为0时代表全速模式(Full Speed)。

##### USB内存分配函数

紧接着，使用宏定义重命名了一些内存分配函数：

```c
/** Alias for memory allocation. */
#define USBD_malloc         (uint32_t *)USBD_static_malloc

/** Alias for memory release. */
#define USBD_free           USBD_static_free

/** Alias for memory set. */
#define USBD_memset         /* Not used */

/** Alias for memory copy. */
#define USBD_memcpy         /* Not used */

/** Alias for delay. */
#define USBD_Delay          HAL_Delay
```

同时还在下面声明了两个静态内存分配和释放函数，这两个函数在`usbd_conf.c`中进行了实现。

再往下，有一段关于USB调试模式输出内容的宏定义，根据`USBD_DEBUG_LEVEL`而有所区别：

```c
/* DEBUG macros */

#if (USBD_DEBUG_LEVEL > 0)
#define USBD_UsrLog(...)    printf(__VA_ARGS__);\
                            printf("\n");
#else
#define USBD_UsrLog(...)
#endif

#if (USBD_DEBUG_LEVEL > 1)

#define USBD_ErrLog(...)    printf("ERROR: ") ;\
                            printf(__VA_ARGS__);\
                            printf("\n");
#else
#define USBD_ErrLog(...)
#endif

#if (USBD_DEBUG_LEVEL > 2)
#define USBD_DbgLog(...)    printf("DEBUG : ") ;\
                            printf(__VA_ARGS__);\
                            printf("\n");
#else
#define USBD_DbgLog(...)
#endif
```

这部分同样不需要修改，只需要知道其在`USBD_DEBUG_LEVEL`的值改变后会有所差异就行。

至此，关于`usbd_conf`两个文件的解析就完成了，我们可以发现最重要的其实就是`usbd_conf.h`中关于`USBD_MAX_NUM_INTERFACES`的修改，其它部分通常情况下基本不用修改。

#### usbd_desc.h

通过名字我们可以知道，这两个文件是用于管理USB描述符的，这是USB操作的关键部分。

我们从`usbd_desc.c`的引用部分可以发现它引用了`usbd_core.h`，还有刚刚我们分析的`usbd_conf.h`，以及它自己对应的`usbd_desc.h`。

![image-20251019214505007](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019214505007.png)

为此我们最好还是先从`usbd_desc.h`开始看起。

##### 引用

在`usbd_desc.h`的引用中，它只引用了一个`usbd_def.h`，跳过去看一下会发现这个文件其实就是一大堆USB操作码的宏定义常量，看来是为了方便后面的书写和理解。

![image-20251019214707558](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019214707558.png)

##### UID

然后往下，我们就可以看到一串宏定义，它们标定了设备唯一标识符（UID）的三个地址常量以及这个标识符的存储字符长度，前三个宏定义和硬件相关，不应该修改，最后一个宏定义可以修改但不建议。

![image-20251019214915572](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019214915572.png)

STM32微控制器内置了一个96位的唯一标识符（UID），这个UID对于每一个STM32芯片都是独一无二的。这个UID通常由芯片的制造参数组合而成，包括晶圆上的X和Y坐标、批次号和晶圆号。UID可以用于区分不同芯片或用于安全应用中的密钥。在USB中通常可以作为主机识别不同设备的ID。

##### USB描述符结构体

再然后，下面就是一个向外引出的结构体：

![image-20251019215612488](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251019215612488.png)

这个结构体定义在`usbd_desc.c`中，而结构体类型定义在`usbd_de.h`，我们可以跳转到这个结构体的类型定义中观察：

```c
typedef struct
{
  uint8_t  *(*GetDeviceDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
  uint8_t  *(*GetLangIDStrDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
  uint8_t  *(*GetManufacturerStrDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
  uint8_t  *(*GetProductStrDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
  uint8_t  *(*GetSerialStrDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
  uint8_t  *(*GetConfigurationStrDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
  uint8_t  *(*GetInterfaceStrDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
#if (USBD_LPM_ENABLED == 1U)
  uint8_t  *(*GetBOSDescriptor)(USBD_SpeedTypeDef speed, uint16_t *length);
#endif
} USBD_DescriptorsTypeDef;
```

可以发现这是由一系列函数指针组成的结构体，并且从名字上来看，它们都是描述符，事实上它们相当于访问描述符的一个接口函数。

#### usbd_desc.c

既然如此，那么让我们来看看`usbd_desc.c`文件吧。

##### USB设备描述符核心配置

首先我们可以看到一堆宏定义：

```c
#define USBD_VID 1155
#define USBD_LANGID_STRING 1033
#define USBD_MANUFACTURER_STRING "STMicroelectronics"
#define USBD_PID_FS 22336
#define USBD_PRODUCT_STRING_FS "STM32 Virtual ComPort"
#define USBD_CONFIGURATION_STRING_FS "CDC Config"
#define USBD_INTERFACE_STRING_FS "CDC Interface"
```

这是我们设备描述符的核心部分，相当于我们USB设备的身份证。

让我们分别看看这些设置：

1. `USBD_VID`：厂商ID，16位数字，1155（0x0483)是STMicroelectronics的官方VID，如果只是学习或者个人使用可以不改，如果需要发布产品、避免驱动冲突，则必须修改。通常可以购买VID（但是很贵，只有大公司适合），或者使用开源项目提供的VID（如pid.codes提供的`0x1209`）。当然如果你是混沌派，那么你可以随便设置你想要设置的VID，不过为防止冲突，最好去USB-IF查询一下这个VID是不是已经被人占用了。
2. `USBD_LANGID_STRING`：语言ID，表示字符串描述符使用的语言。通常不变，1033代表英语。
3. `USBD_MANUFACTURER_STRING`：厂商字符串，这个通常需要修改成你的公司名、团队名或个人名。
4. `USBD_PID_FS`：产品ID，16位数字，22336是ST的Virtual ComPort示例PID。在你所属的VID中选择一个空着的或者合适的PID，如果你选择了pid.codes项目，那么你可以向他们申请PID，不过通常这需要你的项目是有意义且开源的。
5. `USBD_PRODUCT_STRING_FS`：产品字符串，改为设备的真实名称，这会显示在设备管理器中。
6. `USBD_CONFIGURATION_STRING_FS`：配置字符串，也就是配置名称，根据你的需求进行修改，不过一般情况只有一个配置，所以改成啥都无所谓。
7. `USBD_INTERFACE_STRING_FS`：接口字符串，同样也是可改可不改，但如果是复合设备有多个接口，就需要为每个接口设置一个接口字符串（你可以将其命名为`USBD_INTERFACE_STRING_FS_A`、`USBD_INTERFACE_STRING_FS_B`，或任意你认为适合区分的名字）。

总之，大部分情况，我们关注的主要还是VID、PID、厂商字符串、设备字符串这四个部分，而配置字符串和接口字符串可改可不改，语言ID通常不改。

##### 序列号管理函数

接着我们往下看，可以发现两个函数声明：

![image-20251020230056715](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251020230056715.png)

它们的`static`关键字说明了它们是工作在这个文件中的，我们可以跳转到它们的定义中：

```c
/**
 * @brief  Create the serial number string descriptor
 * @param  None
 * @retval None
 */
static void Get_SerialNum(void) {
  uint32_t deviceserial0;
  uint32_t deviceserial1;
  uint32_t deviceserial2;

  deviceserial0 = *(uint32_t *)DEVICE_ID1;
  deviceserial1 = *(uint32_t *)DEVICE_ID2;
  deviceserial2 = *(uint32_t *)DEVICE_ID3;

  deviceserial0 += deviceserial2;

  if (deviceserial0 != 0) {
    IntToUnicode(deviceserial0, &USBD_StringSerial[2], 8);
    IntToUnicode(deviceserial1, &USBD_StringSerial[18], 4);
  }
}

/**
 * @brief  Convert Hex 32Bits value into char
 * @param  value: value to convert
 * @param  pbuf: pointer to the buffer
 * @param  len: buffer length
 * @retval None
 */
static void IntToUnicode(uint32_t value, uint8_t *pbuf, uint8_t len) {
  uint8_t idx = 0;

  for (idx = 0; idx < len; idx++) {
    if (((value >> 28)) < 0xA) {
      pbuf[2 * idx] = (value >> 28) + '0';
    } else {
      pbuf[2 * idx] = (value >> 28) + 'A' - 10;
    }

    value = value << 4;

    pbuf[2 * idx + 1] = 0;
  }
}
```

读代码就可以理解，`Get_SerialNum`的功能是通过读取UID，然后将他们计算成为一个序列号供USB主机识别用。而`IntToUnicode`可以将证书转换为Unicode码并存在缓冲区中。两个都是用于管理序列号，确保每个USB设备都具有唯一的序列号字符串描述符，有助于设备的唯一标识和管理。

##### 描述符函数和结构体

接着往下，可以发现一堆返回值是`uint8_t*`的函数，他们的结构统一为`uin8_t *USBD_FS_xxDescriptor`，显然它们可以用于获取描述符的数据指针。

![image-20251021092621585](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021092621585.png)

而后，这些函数被统一收纳在一个结构体`FS_Desc`中：

![image-20251021092721702](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021092721702.png)

我们在前面已经讲过这个结构体类型的组成，可知后续如果需要获得某个描述符的数据，只需要通过这个结构体进行访问就可以了。

##### 设备描述符

继续往下，我们终于发现了非常重要的USB标准描述符部分，让我们尝试分析一下这部分：

```c
#if defined(__ICCARM__) /* IAR Compiler */
#pragma data_alignment = 4
#endif /* defined ( __ICCARM__ ) */
/** USB standard device descriptor. */
__ALIGN_BEGIN uint8_t USBD_FS_DeviceDesc[USB_LEN_DEV_DESC] __ALIGN_END = {
    0x12,                 /*bLength */
    USB_DESC_TYPE_DEVICE, /*bDescriptorType*/
    0x00,                 /*bcdUSB */
    0x02,
    0x02,                /*bDeviceClass*/
    0x02,                /*bDeviceSubClass*/
    0x00,                /*bDeviceProtocol*/
    USB_MAX_EP0_SIZE,    /*bMaxPacketSize*/
    LOBYTE(USBD_VID),    /*idVendor*/
    HIBYTE(USBD_VID),    /*idVendor*/
    LOBYTE(USBD_PID_FS), /*idProduct*/
    HIBYTE(USBD_PID_FS), /*idProduct*/
    0x00,                /*bcdDevice rel. 2.00*/
    0x02,
    USBD_IDX_MFC_STR,          /*Index of manufacturer  string*/
    USBD_IDX_PRODUCT_STR,      /*Index of product string*/
    USBD_IDX_SERIAL_STR,       /*Index of serial number string*/
    USBD_MAX_NUM_CONFIGURATION /*bNumConfigurations*/
};
```

首先我们关注最上面的宏定义：

```c
#if defined(__ICCARM__) /* IAR Compiler */
#pragma data_alignment = 4
#endif /* defined ( __ICCARM__ ) */
```

从注释可以理解，这个宏定义的触发条件是当使用IAR编译器的时候会使用`#pragma data_alignment = 4`，不过我们使用的GCC工具链，所以这个宏定义并没有开放。

紧接着下面是一个数组，根据注释可知，这个数组就是我们的USB标准设备描述符了。让我们先关注一下它的写法：

```c
__ALIGN_BEGIN uint8_t USBD_FS_DeviceDesc[USB_LEN_DEV_DESC] __ALIGN_END 
```

可以发现，这里使用了`__ALIGN_BEGIN`和`__ALIGN_END`两个宏定义，让我们跳转过去看看：

![image-20251021102339894](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021102339894.png)

这个宏定义可以保证数组在内存中按照4字节对齐，这是一种为了保证内存安全和数据完整性的标准写法，我们不需要修改它。

而定义的这个数组是一个8位无符号整数类型的数组，`USB_LEN_DEV_DESC`是这个描述符的长度，其值为`0x12`即18。

然后我们可以观察描述符内部结构了。

1. `bLength`：设备描述符固定长度为 18 字节（0x12）。改了会导致主机解析错误。
2. `bDescriptorType`：`USB_DESC_TYPE_DEVICE`代表这个描述符是设备描述符。我们同样不应该修改。
3. `bcdUSB`：接下来两个值共同组成了USB版本号，`0x00, 0x02`代表的其实是`0x0200`，即USB2.0。同样我们不需要修改。
4. `bDeviceClass`：设备大类。`0x02`代表CDC通信设备，如果希望定义为HID则设置为`0x03`，复合设备为`0x00`，自定义设备为`0xFF`。关于具体设置可以自行在网上查阅。
5. `bDeviceSubClass`：设备子类。依赖于USB设备大类的子类，在这里的`0x02`是依赖于大类的`0x02`（CDC）， 表示 ACM（虚拟串口）。关于具体设置可以自行在网上查阅。
6. `bDeviceProtocol`：设备协议。依赖于大类和子类，在这里的`0x00`在CDC ACM设备中表示没有特定协议。关于具体设置可以自行在网上查阅。
7. `bMaxPacketSize`：控制端点 0 的最大包大小。`USB_MAX_EP0_SIZE`是最大值，没必要修改。
8. `idVendor`：VID，其中的`USBD_VID`需要修改，这个我们在前面已经讲过。
9. `idProduct`：PID，其中的`USBD_PID_FS`需要修改，这个我们在前面已经讲过。
10. `bcdDevice`：设备版本号。`0x00, 0x02`代表`0x0200`，即版本`v2.00`。可以根据自己的实际更新情况进行修改。
11. `iManufacturer`：厂商字符串索引，这个值通常指向1，使用它的宏定义就可以了，不需要修改。
12. `iProduct`：产品字符串索引，这个值通常指向2，使用它的宏定义就可以了，不需要修改。
13. `iSerialNumber`：序列号字符串索引，这个值通常指向3，使用它的宏定义就可以了，不需要修改。
14. `bNumConfigurations`：配置数量，使用的前面我们设置的`USBD_MAX_NUM_CONFIGURATION`，通常值都是1，不需要修改。

可见，这里面主要需要修改的就是设备大类、子类和协议，而其它部分要么如PID、VID已经在前面修改完了，要么就是通常不需要修改的。

##### 语言描述符

在设备描述符之后，就是语言描述符，这个描述符告诉主机该设备支持哪些语言的字符串描述符：

```c
__ALIGN_BEGIN uint8_t USBD_LangIDDesc[USB_LEN_LANGID_STR_DESC] __ALIGN_END = {
    USB_LEN_LANGID_STR_DESC, USB_DESC_TYPE_STRING, LOBYTE(USBD_LANGID_STRING),
    HIBYTE(USBD_LANGID_STRING)};
```

其写法与设备描述符类似，不过内容有一定改变：

1. `bLength`：描述符长度，对于单语言支持，固定为4，如果需要增加语言，每增加一个语言，这个值应该加2。并且修改后还需要在字符串描述符函数中设计对应的变化。
2. `bDescriptorType`：`USB_DESC_TYPE_STRING`代表这个描述符是字符串描述符。我们不应该修改。
3. `wLANGID[0]`：语言ID的低字节和高字节，此处取用了`USBD_LANGID_STRING`的值`1033`，即英文\-美国。如果还需要支持更多语言，则应该在修改描述符长度后，在后面继续模仿这个写法增加新语言ID的低字节和高字节，例如需要支持简体中文，则应该定义一个常量如`USBD_LANGID_STRING_CN`，并让它的值等于简体中文的语言ID，即`2052`。通常情况下，英文是必须支持的，其它语言是可选添加的。

##### 字符串描述符

继续往下，可以发现一个字符串描述符数组，这个数组并没有被初始化：

```c
__ALIGN_BEGIN uint8_t USBD_StrDesc[USBD_MAX_STR_DESC_SIZ] __ALIGN_END;
```

它将用于临时存储USB字符串描述符，通过`USBD_MAX_STR_DESC_SIZ`可以避免描述符超出内存限制。

##### 序列号描述符

然后是一个序列号描述符，用于记录USB的序列号：

```c
__ALIGN_BEGIN uint8_t USBD_StringSerial[USB_SIZ_STRING_SERIAL] __ALIGN_END = {
    USB_SIZ_STRING_SERIAL,
    USB_DESC_TYPE_STRING,
};
```

1. `bLength`：描述符长度，序列号描述符的长度为26。
2. `bDescriptorType`：`USB_DESC_TYPE_STRING`代表这个描述符是序列号描述符。我们不应该修改。

可以发现这个描述符长度为26，但是只用了2个字节，这是因为剩下的字节需要在运行时生成并填充。

##### 描述符函数

描述符函数可以用于访问描述符，通过这样的设计可以实现数据的隔离，降低代码耦合度。

我们可以任意选择一个描述符函数来观察，例如用于获取设备描述符的`USBD_FS_DeviceDescriptor`：

```c
/**
 * @brief  Return the device descriptor
 * @param  speed : Current device speed
 * @param  length : Pointer to data length variable
 * @retval Pointer to descriptor buffer
 */
uint8_t *USBD_FS_DeviceDescriptor(USBD_SpeedTypeDef speed, uint16_t *length) {
  UNUSED(speed);
  *length = sizeof(USBD_FS_DeviceDesc);
  return USBD_FS_DeviceDesc;
}
```

可以发现它没有处理speed，即设备速度，代码中使用了`UNUSED(speed)`，这会翻译成`(void)speed`，被编译器识别为故意没有使用这个变量，以防止编译器警告。看样子速度这个对它没有用处。

然后它将描述符长度返回到了`length`中，因为这是个指针，所以数据会被带出去。

最后，它返回了`USBD_FS_DeviceDesc`，也就是前面定义的设备描述符数组的指针，此时也就实现了获取描述符的功能。

其它的描述符函数也是类似的效果，内容上可能有细微变化但整体逻辑不变，就不一一赘述了。

#### usbd_cdc_if.h

我们继续分析`usbd_cdc_if.h`这个文件，很显然，这个文件就和USB类直接相关了，因为我们在CubeMX中将该设备设置成了CDC设备，所以CubeMX还生成了专门针对CDC配置和处理的程序，而`cdc_if`就代表CDC接口。如果不需要使用CDC，则这个文件和它的`.c`文件可以废弃。或者自定义设备也可以在此基础上修改，或者复合设备可以在保留的基础上新建其它类型文件，然后共同使用。不过我们目前只是分析这个文件当前的作用。

##### 引用

`usbd_cdc.h`的引用内容很少，只有一个：

![image-20251021131855494](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021131855494.png)

这个文件同样是位于`Middlewares`中的，不过它位于最底层的`Class\CDC`路径，定义了一些和CDC相关的数据结构。

##### 缓存区大小

接着，文件定义了收发数据的缓存区大小的值。

![image-20251021133757077](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021133757077.png)

##### CDC接口函数结构体

和`usbd_desc`中的`USBD_DescriptorsTypeDef`类似，`usbd_cdc_if.h`也有一个存储函数接口的结构体：

![image-20251021133349840](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021133349840.png)

我们跳转到结构体类型定义中：

```c
typedef struct _USBD_CDC_Itf
{
  int8_t (* Init)(void);
  int8_t (* DeInit)(void);
  int8_t (* Control)(uint8_t cmd, uint8_t *pbuf, uint16_t length);
  int8_t (* Receive)(uint8_t *Buf, uint32_t *Len);

} USBD_CDC_ItfTypeDef;
```

不难发现它们的功能就是提供四个函数的接口，分别代表初始化、取消初始化、控制、接收，这四个函数最终定义在`usbd_cdc_if.c`中，我们等会分析。

##### 发送函数

最后，在这个文件中还声明了一个CDC的发送函数：

![image-20251021133612341](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021133612341.png)

显然是可以通过这个函数，给主机发送数据。

#### usbd_cdc_if.c

现在让我们看看CDC部分具体是怎么实现的。

##### 引用

对于`usbd_cdc_if.c`文件，它的引用内容很少，就是对它对应头文件的引用：

![image-20251021133935049](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021133935049.png)

##### 缓存区

紧接着定义了两个数组作为收发缓存区，它们的值都是1024字节。

![image-20251021134034976](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021134034976.png)

##### USB设备句柄

在`usbd_cdc_if.c` 中，还额外引入了一个USB设备句柄：

![image-20251021182537772](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021182537772.png)

这个句柄是在`usb_device.c`中定义的，等会我们会分析它。

不过从类型定义中我们可以大致知晓其功能：

```c
typedef struct _USBD_HandleTypeDef
{
  uint8_t                 id;
  uint32_t                dev_config;
  uint32_t                dev_default_config;
  uint32_t                dev_config_status;
  USBD_SpeedTypeDef       dev_speed;
  USBD_EndpointTypeDef    ep_in[16];
  USBD_EndpointTypeDef    ep_out[16];
  uint32_t                ep0_state;
  uint32_t                ep0_data_len;
  uint8_t                 dev_state;
  uint8_t                 dev_old_state;
  uint8_t                 dev_address;
  uint8_t                 dev_connection_status;
  uint8_t                 dev_test_mode;
  uint32_t                dev_remote_wakeup;

  USBD_SetupReqTypedef    request;
  USBD_DescriptorsTypeDef *pDesc;
  USBD_ClassTypeDef       *pClass;
  void                    *pClassData;
  void                    *pUserData;
  void                    *pData;
} USBD_HandleTypeDef;
```

通过名称不难知道，这个结构体其实就是用于管理USB整体状态的，包括配置、端点、端点0、描述符等等。

不过它现在不重要，我们等会在`usb_device.c`中详细分析。

##### CDC接口函数和结构体

紧接着就是刚才我们提到到CDC接口函数的声明还有将它们引出去的结构体：

![image-20251021183312312](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251021183312312.png)

##### CDC初始化函数

它们的定义也紧跟在下面，让我们逐一观察：

```c
/**
  * @brief  Initializes the CDC media low layer over the FS USB IP
  * @retval USBD_OK if all operations are OK else USBD_FAIL
  */
static int8_t CDC_Init_FS(void)
{
  /* USER CODE BEGIN 3 */
  /* Set Application Buffers */
  USBD_CDC_SetTxBuffer(&hUsbDeviceFS, UserTxBufferFS, 0);
  USBD_CDC_SetRxBuffer(&hUsbDeviceFS, UserRxBufferFS);
  return (USBD_OK);
  /* USER CODE END 3 */
}
```

从函数名可以知道这个函数是用于初始化CDC的，其主要执行的功能就是将USB设备句柄里关于收发的缓存区进行了设置。

但是这个设置的过程又是怎样的呢？让我们继续分析：

```c
/**
  * @brief  USBD_CDC_SetTxBuffer
  * @param  pdev: device instance
  * @param  pbuff: Tx Buffer
  * @retval status
  */
uint8_t  USBD_CDC_SetTxBuffer(USBD_HandleTypeDef   *pdev,
                              uint8_t  *pbuff,
                              uint16_t length)
{
  USBD_CDC_HandleTypeDef   *hcdc = (USBD_CDC_HandleTypeDef *) pdev->pClassData;

  hcdc->TxBuffer = pbuff;
  hcdc->TxLength = length;

  return USBD_OK;
}


/**
  * @brief  USBD_CDC_SetRxBuffer
  * @param  pdev: device instance
  * @param  pbuff: Rx Buffer
  * @retval status
  */
uint8_t  USBD_CDC_SetRxBuffer(USBD_HandleTypeDef   *pdev,
                              uint8_t  *pbuff)
{
  USBD_CDC_HandleTypeDef   *hcdc = (USBD_CDC_HandleTypeDef *) pdev->pClassData;

  hcdc->RxBuffer = pbuff;

  return USBD_OK;
}
```

以上是这两个设置函数的实现，以`USBD_CDC_SetTxBuffer`为例，它首先是将USB设备句柄结构体的`pClassData`项取出来赋值给`hcdc`。前面给出的USB设备句柄结构体类型定义中我们可以知道，`pClassData`是一个`void*`指针，而现在这个指针实际指向的内容似乎是一个`USBD_CDC_HandleTypeDef`结构体。

虽然我们暂时还不知道什么时候它指向的这么一个结构体，不过让我们先看看这个结构体的内容长什么样：

```c
typedef struct
{
  uint32_t data[CDC_DATA_HS_MAX_PACKET_SIZE / 4U];      /* Force 32bits alignment */
  uint8_t  CmdOpCode;
  uint8_t  CmdLength;
  uint8_t  *RxBuffer;
  uint8_t  *TxBuffer;
  uint32_t RxLength;
  uint32_t TxLength;

  __IO uint32_t TxState;
  __IO uint32_t RxState;
}
USBD_CDC_HandleTypeDef;
```

结构体很简单，我们可以注意到在`USBD_CDC_SetTxBuffer`中其实并没有用到全部内容，只用到了`TxBuffer`和`TxLength`，从名字上可以知道这两个值分别代表发送缓存区和缓存区的长度。并且我们知道在`CDC_Init_FS`中，这个`length`值等于0，显然不符合`UserTxBufferFS`的实际长度，故我们可以推测这个`TxLength`代表的可能是当前缓存区的实际长度。

同理，`USBD_CDC_SetRxBuffer`的写法也是类似，只是没有设置`RxLength`，这可能是因为初始化过程什么也没收到，所以没必要设置。

##### CDC去初始化函数

接下来是去初始化函数，这个里面什么也没做，可以根据实际需求自行修改：

```c
/**
  * @brief  DeInitializes the CDC media low layer
  * @retval USBD_OK if all operations are OK else USBD_FAIL
  */
static int8_t CDC_DeInit_FS(void)
{
  /* USER CODE BEGIN 4 */
  return (USBD_OK);
  /* USER CODE END 4 */
}
```

##### CDC控制函数

接下来是CDC的控制函数：

```c
/**
  * @brief  Manage the CDC class requests
  * @param  cmd: Command code
  * @param  pbuf: Buffer containing command data (request parameters)
  * @param  length: Number of data to be sent (in bytes)
  * @retval Result of the operation: USBD_OK if all operations are OK else USBD_FAIL
  */
static int8_t CDC_Control_FS(uint8_t cmd, uint8_t* pbuf, uint16_t length)
{
  /* USER CODE BEGIN 5 */
  switch(cmd)
  {
    case CDC_SEND_ENCAPSULATED_COMMAND:

    break;

    case CDC_GET_ENCAPSULATED_RESPONSE:

    break;

    case CDC_SET_COMM_FEATURE:

    break;

    case CDC_GET_COMM_FEATURE:

    break;

    case CDC_CLEAR_COMM_FEATURE:

    break;

  /*******************************************************************************/
  /* Line Coding Structure                                                       */
  /*-----------------------------------------------------------------------------*/
  /* Offset | Field       | Size | Value  | Description                          */
  /* 0      | dwDTERate   |   4  | Number |Data terminal rate, in bits per second*/
  /* 4      | bCharFormat |   1  | Number | Stop bits                            */
  /*                                        0 - 1 Stop bit                       */
  /*                                        1 - 1.5 Stop bits                    */
  /*                                        2 - 2 Stop bits                      */
  /* 5      | bParityType |  1   | Number | Parity                               */
  /*                                        0 - None                             */
  /*                                        1 - Odd                              */
  /*                                        2 - Even                             */
  /*                                        3 - Mark                             */
  /*                                        4 - Space                            */
  /* 6      | bDataBits  |   1   | Number Data bits (5, 6, 7, 8 or 16).          */
  /*******************************************************************************/
    case CDC_SET_LINE_CODING:

    break;

    case CDC_GET_LINE_CODING:

    break;

    case CDC_SET_CONTROL_LINE_STATE:

    break;

    case CDC_SEND_BREAK:

    break;

  default:
    break;
  }

  return (USBD_OK);
  /* USER CODE END 5 */
}
```

我们可以发现虽然这里用`switch`分了很多情况，但是`CDC_Control_FS`实际上仍然是一个没有任何实现的函数，需要用户自行修改。

针对虚拟串口，我们可以在`CDC_SET_LINE_CODING`中设置波特率、停止位、校验位、数据位的值，具体设置方法它的注释已经给出来了。我们可以这样定义一个结构体：

```c
typedef struct {
    uint32_t bitrate;
    uint8_t  format;
    uint8_t  paritytype;
    uint8_t  datatype;
} USBD_CDC_LineCodingTypeDef;

USBD_CDC_LineCodingTypeDef LineCoding = {
    115200, /* Default bitrate */
    0x00,   /* 1 stop bit */
    0x00,   /* No parity */
    0x08    /* 8 data bits */
};
```

然后通过`pbuf`将数据传出：

```c
LineCoding.bitrate = *(uint32_t*)(pbuf + 0);  // 波特率
LineCoding.format = *(pbuf + 4);              // 停止位
LineCoding.paritytype = *(pbuf + 5);          // 校验位
LineCoding.datatype = *(pbuf + 6);            // 数据位
```

而对于`CDC_GET_LINE_CODING`就是相反的过程即可。

## 其它参考资料

[STM32Cube USB 设备库参考手册](https://www.st.com/resource/zh/user_manual/dm00108129-stm32cube-usb-device-library-stmicroelectronics.pdf)
