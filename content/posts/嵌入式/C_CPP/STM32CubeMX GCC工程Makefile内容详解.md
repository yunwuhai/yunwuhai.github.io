---
title: "STM32CubeMX GCC工程Makefile内容详解"
draft: false
categories:
- 嵌入式
tags:
- STM32CubeMX
- C
- C++
- Makefile
date: 2022-03-08T00:30:45+08:00
license: CC-BY-SA 4.0
description: 本文首发于CSDN，原文：https://blog.csdn.net/qq_44884716/article/details/123295638
---


# STM32CubeMX GCC工程Makefile内容详解

<!-- @import "[TOC]" {cmd="toc" depthFrom=1 depthTo=6 orderedList=false} -->

<!-- code_chunk_output -->

- [STM32CubeMX GCC工程Makefile内容详解](#stm32cubemx-gcc工程makefile内容详解)
  - [基础介绍](#基础介绍)
  - [注意](#注意)
  - [Makefile](#makefile)
    - [TARGET](#target)
    - [DEBUG](#debug)
    - [OPT](#opt)
    - [BUILD\_DIR](#build_dir)
    - [C\_SOURCES](#c_sources)
    - [ASM\_SOURCES](#asm_sources)
    - [PREFIX](#prefix)
    - [CC,AS,CP,SZ](#ccascpsz)
    - [HEX,BIN](#hexbin)
    - [CPU](#cpu)
    - [FPU](#fpu)
    - [FLOAT-ABI](#float-abi)
    - [MCU](#mcu)
    - [AD\_DEFS,C\_DEFS](#ad_defsc_defs)
    - [AS\_INCLUDES,C\_INCLUDES](#as_includesc_includes)
    - [ASFLAGS,CFLAGS](#asflagscflags)
    - [ifeq ($(DEBUG), 1)](#ifeq-debug-1)
    - [CFLAGS](#cflags)
    - [LDSCRIPTS](#ldscripts)
    - [LIBS,LIBDIR](#libslibdir)
    - [LDFLAGS](#ldflags)
    - [all](#all)
    - [OBJECTS](#objects)
    - [BUILD](#build)
    - [clean](#clean)
    - [flash](#flash)
    - [dependencies](#dependencies)
  - [结语](#结语)

<!-- /code_chunk_output -->



## 基础介绍

因为项目原因，需要对编译系统进行一些比较复杂的使用，但是我对于编译系统这一块并不是非常精通了解，所以需要进行一下学习。正巧，众所周知STM32推出过非常实用的工具——STM32CubeMX，这个工具可以对STM32进行一些基础配置并设置一些配置代码，基本可以靠图形界面完成对STM32的所有初始化配置，然后它就会生成一个基础工程，编程者在这个基础上进行设置即可。

当然，本文主要关注点是在编译系统，所以该工具的配置什么的就不详细说了，基本上就是简单随便配置一下时钟就可以了（事实上应该时钟都不需要配置），重点在于我们生成工程的时候需要选择生成Makefile工程，这样才可以使用我们的开源工具链进行配置。

之后我们可以得到如下的工程目录（当然，众所周知CubeMX的一些设置会影响到工程根目录的具体结构，不过这都不是重点）：

![](https://i-blog.csdnimg.cn/blog_migrate/6938647bafeaacf0a1a8963e69dd68a0.png)

其中build目录是编译后生成的，先不管，另外Core文件夹下的Test文件夹及其中内容是我进行测试的时候添加的，暂时也先不管。

我们先来看看其它的东西，首先是Core中的内容，这部分的内容基本上就完全是STM32CubeMX生成的，Inc中放h文件而Src中放c文件，里面的文件都是在CubeMX中配置过的东西，这些东西是每次CubeMX在修改后都会重新生成的东西（也有可能是你修改了哪一部分，就会重新生成哪一部分的文件，这个是CubeMX自己的机制，不重要）。

其次是Drivers中的内容，这些内容实际上都是从 CubeMX的安装目录里的sdk中复制过来的，如果我们在配置的时候没有选择要将这些东西复制过来，那么CubeMX也不会生成这个目录下的内容（或者不能说生成，而就是直接复制过来），但是取而代之的就是你使用的所有sdk的库函数，都是直接调用的安装目录里的东西，那么为了安全性着想，就不要在编程的时候修改他们了，否则你的库函数就被你的代码污染了，当然这样做的好处就是你的代码复用性会提高而且工程体积会稍微小点。

然后是下面的`.mxproject`文件，CubeMX的工程文件，不管。

接着就是我们等会最重要的Makefile，这个是Make工具的脚本文件，如果你不知道Make工具是啥，建议先了解一下再看本文会好一点。

之后是`MakeTest.ioc`文件，CubeMX的配置文件，不管。

然后是后缀为s的start文件，这个文件是芯片的项目启动文件，一般不需要管，里面放了中断向量表之类的东西。

最后是后缀为ld的链接脚本文件，这个是用于链接的，等会会说。

## 注意

本文的解析结构并没有按照makefile的解析顺序来，而是采用从上到下的顺序来解说的（当然会根据实际情况进行跳跃），主要原因在于我学习这个东西的目的主要是直接把这个Makefile当成一个模板，然后未来直接在这个模板上进行修改就可以了，而到目前为止我暂时还不打算自己从头来写个Makefile（毕竟能用就行，平时哪需要那么麻烦）。

考虑到篇幅，就不单独把全部makefile列出来了，需要时你直接用CubeMX生成一个工程然后看它Makefile即可，只要STM32公司那边没有对这个规则进行大改，那么下面这些内容应该都大差不差。

此外，本文中很多东西其实可以在[gcc的手册](https://gcc.gnu.org/onlinedocs/)中找到答案，如果感兴趣可以去看看。

## Makefile

### TARGET

```makefile
TARGET = MakeTest
```

设置目标文件名，实际上就是做了个变量，并且把Makefile这个作为参数传入。平时当成工程名即可，如果要换工程，就自己随便重新取个名字。

### DEBUG

```makefile
DEBUG = 1
```

是否进行调试编译，这里表示是，release版关闭调试时将1改成其它数即可，具体原因后面会讲到。

### OPT

```makefile
OPT = -Og
```

优化等级，这里使用Og的目的是因为开启了调试，所以优化时需要产生合理的优化而不和调试选项冲突。如果是release版本，可以使用`-Os`（提高速度并优化体积）或`-O3`（大幅提高速度但会增大体积）等命令，关于这部分的介绍可以参考[知乎回答](https://www.zhihu.com/question/27090458/answer/137944410)。

### BUILD\_DIR

```makefile
BUILD_DIR = build
```

编译目标地址，这也是前面提到为什么我会生成一个build文件夹，实际上就是这个变量进行的命名，如果你需要，可以把它修改成任何名字，然后编译出来的所有文件就都会放在这个你新命名的文件夹里面了。不过一般不建议修改，因为大家通用的都是build，不建议太特立独行。

### C_SOURCES

```makefile
C_SOURCES =  \
Core/Src/main.c \
Core/Src/gpio.c \
Core/Src/usart.c \
Core/Src/stm32f4xx_it.c \
Core/Src/stm32f4xx_hal_msp.c \
Core/Test/test.c\
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_tim.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_tim_ex.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_uart.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_rcc_ex.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash_ex.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_flash_ramfunc.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_gpio.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma_ex.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_dma.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_pwr_ex.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_cortex.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal.c \
Drivers/STM32F4xx_HAL_Driver/Src/stm32f4xx_hal_exti.c \
Core/Src/system_stm32f4xx.c  
```

其实从名字我们不难理解，这里放的就是所有用到的c文件。如果我们需要自己写个什么库自己写了什么新的c文件，而且最后会被编译到程序里面的话，就都需要自己在这里添加一行c文件地址。这些地址可以是相对路径，相对的就是makefile文件的地址，而如果不好相对路径，那么也可以设置为绝对路径，例如这里面所有Drivers的文件，如果我们没有配置为复制到工程里面，那么这些文件就会被写为绝对路径并导航到你的CubeMX的sdk存储地址里面。

此外，注意我添加了一行test.c的路径，这一行就是我自己写的文件，里面定义了一个全局变量，并被对应的test.h使用extern引用，然后在Src文件夹下面被main.c引用test.h后使用。这里我想说明的是，哪怕你用h文件做了个跳板（而不是直接extern过来）然后调用了test.c的东西，而且test.c中连个函数都没有，但是只要你使用了里面的东西，就必须要把文件地址填在上面的文件列表中。

不过说实话我个人感觉这样做非常麻烦，这里我有点想知道为什么不能直接添加一个文件夹然后遍历下面的所有c文件并添加呢？为此我还稍微查询了一下，找到了这个博客《[一点一点学写Makefile(6)-遍历当前目录源文件及其子目录下源文件](https://blog.csdn.net/qq849635649/article/details/52935079)》，感兴趣可以看看。

### ASM\_SOURCES

```makefile
ASM_SOURCES =  \
startup_stm32f411xe.s
```

所有汇编文件的地址，添加方法可以继续参考前面C文件的添加方法，也是绝对地址和相对地址添加即可。而这里的start文件，一般不需要用户自己写，这些厂商在开发好芯片后都至少会提供一个startup的c或s文件的，我们需要做的就只是把他添加进来即可（有的可能不是汇编s文件，如果是c文件，正常添加到前面C文件的路径下面即可，这种情况下汇编这里就不需要添加startup了，不过此外你自己写的其他汇编文件倒是仍然可以正常这样写进去）。

### PREFIX

```makefile
PREFIX = arm-none-eabi-
```

工具链起始名，说白了就是你使用的开源工具链（当然你有钱也可以买闭源的，不过没啥必要而且使用起来需要再自行研究一下），这里变量的内容是arm-none-eabi-，其实这个是一个gcc工具链的名字，这个工具链全程一般叫`arm-none-eabi-gcc`，arm表示架构平台，none表示无系统，eabi表示嵌入式应用二进制接口，gcc表示其遵守的GNU GCC的设计规范。这东西我记得之前在哪个很古老的博客上面看到的，但是当时忘了收藏，所以现在找不到了。总之，开发者将这个工具链除gcc部分命名后，里面的所有工具就全部使用这个前缀了，这个东西我们在后面会说。

如果你需要对linux的arm设备进行开发，那么你可能需要安装arm-linux-eabi-gcc（当然也可能是其他名字或顺序，这个是开发者自己决定的，因为里面还可以添加开发者名称，所以好像没有非常严格的规范），如果你需要对riscv架构的设备进行开发，那么可能需要使用riscv-none-gcc，总之，需要什么自己去芯片官网上先看看有没有推荐，然后下载并改这里的参数即可。

### CC,AS,CP,SZ

```makefile
ifdef GCC_PATH
CC = $(GCC_PATH)/$(PREFIX)gcc
AS = $(GCC_PATH)/$(PREFIX)gcc -x assembler-with-cpp
CP = $(GCC_PATH)/$(PREFIX)objcopy
SZ = $(GCC_PATH)/$(PREFIX)size
else
CC = $(PREFIX)gcc
AS = $(PREFIX)gcc -x assembler-with-cpp
CP = $(PREFIX)objcopy
SZ = $(PREFIX)size
endif
```

这里我们需要分别看两个东西，其中是ifdef部分，这东西是一个判断你有没有定义某个变量，看名字大概也可以猜到，这个就是我们gcc工具链的地址。这就涉及到一个问题，也就是环境变量，如果你将你的工具链的工具目录地址添加到环境变量中，那么我们就可以在命令行中直接通过工具的名称调用这个工具，否则我们就需要输入绝对路径来调用工具。

比如你的arm-none-eabi-gcc存储在D盘根目录下，那么你很可能需要在环境变量中添加`D:\arm-none-eabi-gcc\bin\`文件夹地址，此时我们就可以在命令行中直接使用`arm-none-eabi-gcc`来运行`D:\arm-none-eabi-gcc\bin\arm-none-eabi-gcc.exe`程序，否则，我们就需要输入完整的绝对路径来调用该程序。

而GCC_PATH就是用来帮助你添加这个绝对路径的，如果你没有添加环境变量，那么就可以在makefile前面定义GCC\_PATH并添加上地址，如`D:\arm-none-eabi-gcc\bin`，那么之后我们会运行ifdef中的程序（如果没定义就直接使用后面else的程序），makefile所有变量的本质其实就是字符替换，此时例如CC，就会被编译为`D:\arm-none-eabi-gcc\bin\arm-none-eabi-gcc.exe`，其余同理。当然，如果你不想在makefile中添加这个变量，也可以选择在输入`make`指令的时候添加`GCC_PATH=D:\arm-none-eabi-gcc\bin`。

`PREFIX`前面也已经说过了，不赘述。

然后我们关注到这四个工具，其中gcc出现了两次，分别在CC和AS中，CC中直接使用gcc，其实代表了其默认参数编译C语言，而AS从名字在可以猜是代表了汇编器，其使用了-x参数表示更换编译语言，只不过代表所更换的参数assembler-with-cpp，似乎不只是可以汇编，还可以处理C++？不过我把test.c改名成test.cpp后分别添加到汇编和C的Sources列表中似乎都不行，会编译错误，有点不是很懂，不过总之其可以编译汇编语言成为机器语言是肯定的。

之后是CP的objcopy，这是个复制文件内容的工具，具体介绍可以参考《[objcopy命令介绍 - Dake的信息摘录博客](https://my.oschina.net/dake/blog/196707)》。

SZ是一个记录生成程序内部各分段的大小的工具，这个在编译后查看编译出的文件大小进行项目优化的时候会比较有用，makefile中也用了这个工具，在编译到最后会输出这样的内容：

```shell
arm-none-eabi-size build/MakeTest.elf
   text    data     bss     dec     hex filename
   6524      24    1640    8188    1ffc build/MakeTest.elf
```

值得注意的是这个size工具只能对elf文件进行解析，而hex和bin文件中是不包含代码段数据段这些东西的。这里的大概意思是我的代码段有6524字节，数据段有24字节，bss段有1640字节，总共加起来有8188字节。关于这些段的介绍，参考可以参考这个博客《[堆栈、BSS段、代码段、数据段、RO、RW、ZI等概念区分](https://blog.csdn.net/zhy557/article/details/80832268)》。

### HEX,BIN

```makefile
HEX = $(CP) -O ihex
BIN = $(CP) -O binary -S
```

从名字我们就不难看出，这里其实指的就是生成十六进制文件和二进制文件，他们都是可以被烧录到stm32中的代码文件格式，而其中的参数也很好懂，分别就是生成十六进制和二进制所需的参数，没啥好解释的，直接用就行。

### CPU

```makefile
CPU = -mcpu=cortex-m4
```

选择cpu的架构，因为我使用的是stm32f4的芯片，故这里的架构是cortex-m4，如果是其它架构需要进行修改。

### FPU

```makefile
FPU = -mfpu=fpv4-sp-d16
```

选择fpu的架构，这里是因为F4系列有fpu，所以可以添加，如果没有就需要关闭，关闭后无法使用fpu对浮点数计算进行加速，相关概念可以参考《[【arm-gcc开发STM32】开启stm32f4的FPU](https://blog.csdn.net/weixin_42415539/article/details/110139722)》。

### FLOAT-ABI

```makefile
FLOAT-ABI = -mfloat-abi=hard
```

硬浮点或软浮点，如果有FPU就可以开启硬浮点，这里开启了，相关概念可以参考《[浮点 _ 运算处理方式(软硬-mfloat-abi=) _ 浮点协处理器类型 -mfpu=](http://blog.chinaunix.net/uid-27875-id-5785166.html)》。

### MCU

```makefile
MCU = $(CPU) -mthumb $(FPU) $(FLOAT-ABI)
```

此处代表了所有针对MCU硬件的配置，其它的我们已经说过，而这个`-mthumb`代表的是T32指令集，如果使用了另外一种指令集的架构就需要换这里的参数，具体参考《[【解读经典】ARM体系结构与编程（3）](http://blog.sina.com.cn/s/blog_675a80790102ylnk.html)》。

### AD\_DEFS,C\_DEFS

```makefile
AS_DEFS = 

C_DEFS =  \
-DUSE_HAL_DRIVER \
-DSTM32F411xE
```

分别是汇编和C的宏定义，这个项目中的汇编里面因为不需要，所以啥也没写，如果你不需要在汇编程序中增加什么外部的宏定义，就不需要这个。

而C文件宏定义，真正的宏需要去掉每个宏定义开头的-D，例如此处的-DUSE_HAL_DRIVER，实际上是宏定义了USE_HAL_DRIVER，这些宏定义会影响到c文件里面相关宏的内容，例如这个HAL，其实就代表了HAL库，那么C文件里面引用的东西就会选择HAL库而非LL库的内容。如果你想的话，也可以自己添加一些宏定义在c文件中作为开关，然后在这里添加东西表示打开。

### AS\_INCLUDES,C\_INCLUDES

```makefile
AS_INCLUDES = 

C_INCLUDES =  \
-ICore/Inc \
-IDrivers/STM32F4xx_HAL_Driver/Inc \
-IDrivers/STM32F4xx_HAL_Driver/Inc/Legacy \
-IDrivers/CMSIS/Device/ST/STM32F4xx/Include \
-IDrivers/CMSIS/Include
```

汇编和C的引用文件所在文件夹，其中因为汇编没有引用外部文件，所以什么也没有，如果有需要自己添加。

注意这里添加的是文件夹地址而不是具体的文件地址。

对于C来说，如果在自己的代码#include中使用了相对地址或绝对地址，则可以不添加，如果是只写了引用文件名或非本文件的文件名，则需要添加，以辅助编译器找到对应文件，编译器会主动从上述路径作为相对路径寻找include的文件。这里-I也全部是前缀。

例如我们需要在`Core\Src\main.c`中引用`Core\Test\test.h`，那么我们需要在main.c中写`#include "test.h"`并在`C_INCLUDES`中添加`-ICore/Test`，而如果我们不在`C_INCLUDES`中进行添加，那么main.c中就必须写相对或绝对地址，例如`#include "../Test/test.h"`，这样才能保证我们的编译器能够找准位置。

### ASFLAGS,CFLAGS

```makefile
ASFLAGS = $(MCU) $(AS_DEFS) $(AS_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections
CFLAGS = $(MCU) $(C_DEFS) $(C_INCLUDES) $(OPT) -Wall -fdata-sections -ffunction-sections
```

编译参数，分别针对汇编和C语言，他们各自前面四个变量参数已经讲过，不再赘述。

`-Wall`的功能主要是开启一些警告检测，如果我们的代码出现了不规范的地方，那么通过这个参数，编译器就会检查到这些地方并告知我们。关于这个参数的具体介绍可以参考《[gcc -Wall详解](http://blog.sina.com.cn/s/blog_553230d70101efqv.html)》。

`-fdata-sections`表示对程序中每个数据创建一个section，而`-ffunction-sections`则是针对函数创建section，GCC的链接操作是以section作为最小的处理单元，只要一个section中的某个符号被引用，该section就会被加到可执行程序中。关于这个部分具体可以参考《[gcc -ffunction-sections -fdata-sections -Wl,–gc-sections 参数详解](https://blog.csdn.net/pengfei240/article/details/55228228)》

### ifeq (\$(DEBUG), 1)

```makefile
ifeq ($(DEBUG), 1)
CFLAGS += -g -gdwarf-2
endif
```

语句很好理解，如果DEBUG=1，就执行，如果不是1，就不执行。很显然，这段话就是检测目前是否是调试模式，而注意这里CFLAGS前面其实已经出现过，而这里再次出现时使用的就不再是等号=了，而是+=符号，这个符号在makefile中表示在已有变量后面补上新的符号。

而补上的其实就是两个新的参数，我们应该不难猜测这两个参数就是针对的调试生成的。

`-g`表示的意思是生成调试信息，如果不生成的话我们在使用gdb调试的时候就很难做到代码定位，当然如果你不使用gdb，还可以使用`-gformat`然后加上你想要的格式。而`-gdwarf-2`的意思是生成DWARF version2 的格式的调试信息，常用于IRIXX6上的DBX调试器。GCC会使用DWARF version3的一些特性。关于这两个参数的使用，可以参考《[GCC 编译及编译选项](https://blog.csdn.net/luguifang2011/article/details/80642692)》。

### CFLAGS

```makefile
CFLAGS += -MMD -MP -MF"$(@:%.o=%.d)"
```

关于这个部分的内容又是针对CFLAGS，这里出现了三个新的参数，同时后面有一串makefile语法的宏。

这一串东西的主要功能是生成关联信息，关联信息会对链接产生影响，其中`-MMD`表示会把关联信息输出到.d文件中，`-MF`是指定用于存放关联信息的文件，`-MP`生成的依赖文件里面，依赖规则中的所有 .h 依赖项都会在该文件中生成一个伪目标，其不依赖任何其他依赖项。该伪规则将避免删除了对应的头文件而没有更新 “Makefile” 去匹配新的依赖关系而导致 make 出错的情况出现。

关于这三个参数以及相关信息的介绍可以参考《[GCC -M,-MM,-MMD,-MF,-MT](https://blog.csdn.net/linuxandroidwince/article/details/75221300)》和《[Linux Makefile 生成 *.d 依赖文件以及 gcc -M -MF -MP 等相关选项说明](https://blog.csdn.net/QQ1452008/article/details/50855810)》。

而后面那一堆宏，说实话我也不太看得懂，毕竟我对Makefile的语法研究不深，不过看样子意思大概是针对MF的，而且大概含义是把所有o文件的名字复制生成对应的d文件，然后配合前面的参数，把关联信息生成到这些d文件中，而且通过build中的确d文件和o文件基本可以对应上，也侧面应证了这个猜想。

### LDSCRIPTS

```makefile
LDSCRIPT = STM32F411CEUx_FLASH.ld
```

链接脚本，里面包括了链接时各程序的组织架构，以及包括堆栈地址大小等信息，这个东西是CubeMX生成的，所以里面其实很多东西你在CubeMX中都可以修改。这里的内容不只是修改芯片，只要修改了了中断向量、堆栈大小等信息，均需要修改此部分，它其实就代表了你的程序在芯片的ROM中是怎么存储的，感兴趣可以自行查看一下这个文件，我把我的这个文件复制上来给各位看一下（删除了一些无用的注释）：

```
/* Entry Point */
ENTRY(Reset_Handler)

/* Highest address of the user mode stack */
_estack = 0x20020000;    /* end of RAM */
/* Generate a link error if heap and stack don't fit into RAM */
_Min_Heap_Size = 0x200;      /* required amount of heap  */
_Min_Stack_Size = 0x400; /* required amount of stack */

/* Specify the memory areas */
MEMORY
{
RAM (xrw)      : ORIGIN = 0x20000000, LENGTH = 128K
FLASH (rx)      : ORIGIN = 0x8000000, LENGTH = 512K
}

/* Define output sections */
SECTIONS
{
  /* The startup code goes first into FLASH */
  .isr_vector :
  {
    . = ALIGN(4);
    KEEP(*(.isr_vector)) /* Startup code */
    . = ALIGN(4);
  } >FLASH

  /* The program code and other data goes into FLASH */
  .text :
  {
    . = ALIGN(4);
    *(.text)           /* .text sections (code) */
    *(.text*)          /* .text* sections (code) */
    *(.glue_7)         /* glue arm to thumb code */
    *(.glue_7t)        /* glue thumb to arm code */
    *(.eh_frame)

    KEEP (*(.init))
    KEEP (*(.fini))

    . = ALIGN(4);
    _etext = .;        /* define a global symbols at end of code */
  } >FLASH

  /* Constant data goes into FLASH */
  .rodata :
  {
    . = ALIGN(4);
    *(.rodata)         /* .rodata sections (constants, strings, etc.) */
    *(.rodata*)        /* .rodata* sections (constants, strings, etc.) */
    . = ALIGN(4);
  } >FLASH

  .ARM.extab   : { *(.ARM.extab* .gnu.linkonce.armextab.*) } >FLASH
  .ARM : {
    __exidx_start = .;
    *(.ARM.exidx*)
    __exidx_end = .;
  } >FLASH

  .preinit_array     :
  {
    PROVIDE_HIDDEN (__preinit_array_start = .);
    KEEP (*(.preinit_array*))
    PROVIDE_HIDDEN (__preinit_array_end = .);
  } >FLASH
  .init_array :
  {
    PROVIDE_HIDDEN (__init_array_start = .);
    KEEP (*(SORT(.init_array.*)))
    KEEP (*(.init_array*))
    PROVIDE_HIDDEN (__init_array_end = .);
  } >FLASH
  .fini_array :
  {
    PROVIDE_HIDDEN (__fini_array_start = .);
    KEEP (*(SORT(.fini_array.*)))
    KEEP (*(.fini_array*))
    PROVIDE_HIDDEN (__fini_array_end = .);
  } >FLASH

  /* used by the startup to initialize data */
  _sidata = LOADADDR(.data);

  /* Initialized data sections goes into RAM, load LMA copy after code */
  .data : 
  {
    . = ALIGN(4);
    _sdata = .;        /* create a global symbol at data start */
    *(.data)           /* .data sections */
    *(.data*)          /* .data* sections */

    . = ALIGN(4);
    _edata = .;        /* define a global symbol at data end */
  } >RAM AT> FLASH

  
  /* Uninitialized data section */
  . = ALIGN(4);
  .bss :
  {
    /* This is used by the startup in order to initialize the .bss secion */
    _sbss = .;         /* define a global symbol at bss start */
    __bss_start__ = _sbss;
    *(.bss)
    *(.bss*)
    *(COMMON)

    . = ALIGN(4);
    _ebss = .;         /* define a global symbol at bss end */
    __bss_end__ = _ebss;
  } >RAM

  /* User_heap_stack section, used to check that there is enough RAM left */
  ._user_heap_stack :
  {
    . = ALIGN(8);
    PROVIDE ( end = . );
    PROVIDE ( _end = . );
    . = . + _Min_Heap_Size;
    . = . + _Min_Stack_Size;
    . = ALIGN(8);
  } >RAM

  

  /* Remove information from the standard libraries */
  /DISCARD/ :
  {
    libc.a ( * )
    libm.a ( * )
    libgcc.a ( * )
  }

  .ARM.attributes 0 : { *(.ARM.attributes) }
}
```

我们简单看一下，最开始有个`ENTRY`指令，里面参数是`Reset_Handler`，显然它指向了一个所谓的复位句柄，那么这个句柄是在哪里呢？对，就是在我们前面说的startup汇编文件中，也就是说我们的入口程序实际上就是针对的这个句柄，然后后面通过这个句柄开始的程序进行逐渐执行，初始化硬件向量表这些，再然后才是开始运行我们的main程序，如果你需要写一些什么Bootloader之类的东西，其实也就是在这里看和改。

之后我们再继续查看后面的东西，可以发现我们还标注了RAM的大小、堆栈大小、地址等信息，这些信息都会最终被编译到我们的程序中，并且配合我们的烧录器或仿真器被烧录的芯片中的指定位置。

再之后就是每个区段section了，这些是对你的程序存储的划分，一般情况下我们是不需要对这些东西进行修改的，因为大部分芯片程序的运行存储理念都是差不多的，所以普通情况下我们需要修改的东西基本上就是前面的那些（当然，如果你换了其它芯片的架构，那可能还是要好好研究一下的）。

### LIBS,LIBDIR

```makefile
LIBS = -lc -lm -lnosys
LIBDIR =
```

LIBS里面的这几个东西，代表的链接库，其实就是C语言的标准库，比如说这个-lm就代表了链接了标准数学库，不过具体这几个库链接的都是哪几个，我就不是很清楚了，具体可能要参考GCC的手册，但是我感觉没啥必要，毕竟都是标准库，链接了就链接了呗。除非你需要自己添加引用一些其他的链接库或者你需要缩减代码体积的时候，到时候再去研究哪个有用哪个没用就是了。

而对于LIBDIR，很明显也是一个库地址的意思，如果你使用的是非标准库需要从外面引用的话，就需要在这里添加东西了，添加的方法和前面添加c和汇编库的方法类似。

### LDFLAGS

```makefile
LDFLAGS = $(MCU) -specs=nano.specs -T$(LDSCRIPT) $(LIBDIR) $(LIBS) -Wl,-Map=$(BUILD_DIR)/$(TARGET).map,--cref -Wl,--gc-sections
```

这个就是链接的参数。

`-specs=nano.specs`替换精简c库以缩小代码大小。

`-T`使用脚本文件xxx作为链接器脚本，此脚本替换ld的默认链接脚本（而非加进去），因此命令文件必须给出所有输出文件所需的东西，这里的链接脚本我们在前面已经说过了。

`-Wl`如果链接器不是直接被使用的，而是被编译器使用（如gcc），则所有的链接命令前面必须加上-Wl参数（或其他特殊编译器对应的参数）。

`-MAP`打印一个链接表到map文件中。

`--cref`输出一个交叉引用表。如果一个链接映射文件正在被生成，交叉参照表将会被输出到映射文件中。否则，将会被输出到标准输出。

`--gc-sections`允许对未使用的段使用垃圾收集。在不支持这个选项的目标上将被自动忽略。默认的行为可用’–no-gc-sections’恢复。

关于这部分的内容可以参考《[LD说明文档--2.LD命令行命令翻译](https://blog.csdn.net/yyww322/article/details/50827683)》

### all

```makefile
all: $(BUILD_DIR)/$(TARGET).elf $(BUILD_DIR)/$(TARGET).hex $(BUILD_DIR)/$(TARGET).bin
```

默认执行全部编译，生成elf、hex和bin文件，文件地址和文件名在前面已经说过了。

### OBJECTS

```makefile
OBJECTS = $(addprefix $(BUILD_DIR)/,$(notdir $(C_SOURCES:.c=.o)))
vpath %.c $(sort $(dir $(C_SOURCES)))
OBJECTS += $(addprefix $(BUILD_DIR)/,$(notdir $(ASM_SOURCES:.s=.o)))
vpath %.s $(sort $(dir $(ASM_SOURCES)))
```

这一大段都是makefile的语法，本质上代表了文件替换和名称命名等功能，一般而言我们修改芯片工程或其它什么时候，都不需要修改这个地方。该部分内容较多，另有博客对这一部分进行了比较详细的解释《[(GCC)STM32CubeMX生成的Makefile详解](https://blog.csdn.net/qwe5959798/article/details/112367495)》。

### BUILD

```makefile
$(BUILD_DIR)/%.o: %.c Makefile | $(BUILD_DIR) 
	$(CC) -c $(CFLAGS) -Wa,-a,-ad,-alms=$(BUILD_DIR)/$(notdir $(<:.c=.lst)) $< -o $@

$(BUILD_DIR)/%.o: %.s Makefile | $(BUILD_DIR)
	$(AS) -c $(CFLAGS) $< -o $@

$(BUILD_DIR)/$(TARGET).elf: $(OBJECTS) Makefile
	$(CC) $(OBJECTS) $(LDFLAGS) -o $@
	$(SZ) $@

$(BUILD_DIR)/%.hex: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(HEX) $< $@
	
$(BUILD_DIR)/%.bin: $(BUILD_DIR)/%.elf | $(BUILD_DIR)
	$(BIN) $< $@	
	
$(BUILD_DIR):
	mkdir $@
```

这一部分实际上前面那个博客也介绍得差不多了，但是他没有讲到里面的几个参数的功能。

其中-c和-o这两个gcc最基础的参数就不说了，重点是第一部分中出现的`-Wa,-a,-ad,-alms`几个参数是什么意思。说实话，我最开始也没找到，翻了gcc的手册但是只找到关于Wa的一点描述，而且还不咋看得懂。但是解铃还须系铃人，我们想要知道这几个意思其实最好的办法就是去问一下STM32，然后我就去STM32的官方论坛问了一下，对方给出了答复，说明这几个参数其实就是针对GCC的汇编器的，主要功能是生成一些信息还有引用一些库之类的，一般情况下我们对其可以不做更改。关于这里的问答，可以[跳转到论坛界面进行查看](https://community.st.com/s/feed/0D53W00001PXCcxSAH)。

### clean

```makefile
clean:
	rm -fR $(BUILD_DIR)
```

这个东西没啥好说的，就是清除编译出来的那一大堆文件，一般情况下写makefile都需要这个东西防止生成东西太多影响空间，使用方法就是`make clean`。

### flash

```makefile
flash:
	openocd -f interface/cmsis-dap.cfg -f target/stm32f4x.cfg -c "program $(BUILD_DIR)/$(TARGET).elf reset exit"
```

烧录程序，这个东西是我自己添加的，需要使用openocd并且配置环境变量，如果没有配置环境变量需要修改一下openocd命令的路径，而如果没有下载openocd的就无法使用这个功能了，这个功能不是必须的，如果需要可以直接使用stm32官方提供的烧录工具。

### dependencies

```makefile
-include $(wildcard $(BUILD_DIR)/*.d)
```

依赖引用，这里引用就是前面我们生成的关联文件，这些东西有什么用呢，其实目的就是为了生成我们的o文件。如果你看不懂这个东西什么意思，那么我们随便打开一个d文件其实你应该就懂了（如果你看过一点makefile基础）：

```makefile
build/gpio.o: Core/Src/gpio.c Core/Inc/gpio.h Core/Inc/main.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal.h \
 Core/Inc/stm32f4xx_hal_conf.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_rcc.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_def.h \
 Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f4xx.h \
 Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f411xe.h \
 Drivers/CMSIS/Include/core_cm4.h Drivers/CMSIS/Include/cmsis_version.h \
 Drivers/CMSIS/Include/cmsis_compiler.h Drivers/CMSIS/Include/cmsis_gcc.h \
 Drivers/CMSIS/Include/mpu_armv7.h \
 Drivers/CMSIS/Device/ST/STM32F4xx/Include/system_stm32f4xx.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/Legacy/stm32_hal_legacy.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_rcc_ex.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_gpio.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_gpio_ex.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_exti.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_dma.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_dma_ex.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_cortex.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_flash.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_flash_ex.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_flash_ramfunc.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_pwr.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_pwr_ex.h \
 Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_uart.h
Core/Inc/gpio.h:
Core/Inc/main.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal.h:
Core/Inc/stm32f4xx_hal_conf.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_rcc.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_def.h:
Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f4xx.h:
Drivers/CMSIS/Device/ST/STM32F4xx/Include/stm32f411xe.h:
Drivers/CMSIS/Include/core_cm4.h:
Drivers/CMSIS/Include/cmsis_version.h:
Drivers/CMSIS/Include/cmsis_compiler.h:
Drivers/CMSIS/Include/cmsis_gcc.h:
Drivers/CMSIS/Include/mpu_armv7.h:
Drivers/CMSIS/Device/ST/STM32F4xx/Include/system_stm32f4xx.h:
Drivers/STM32F4xx_HAL_Driver/Inc/Legacy/stm32_hal_legacy.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_rcc_ex.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_gpio.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_gpio_ex.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_exti.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_dma.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_dma_ex.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_cortex.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_flash.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_flash_ex.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_flash_ramfunc.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_pwr.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_pwr_ex.h:
Drivers/STM32F4xx_HAL_Driver/Inc/stm32f4xx_hal_uart.h:

```

这个是gpio.d，看着是不是很熟悉，感觉和前面那个《[(GCC)STM32CubeMX生成的Makefile详解](https://blog.csdn.net/qwe5959798/article/details/112367495)》说的把生成指令展开后C\_INCLUDES、C\_SOURCES生成的那一套很像？像就对了，这东西就是为了生成.d文件最顶部那个目标文件而存在的，而这里的gpio.d文件中所指的其实就是gpio.o，其余同理。

## 结语

好了，看到这你应该基本上理解了这个Makefile内部的功能和作用了，配合我找的这些资料以及官方文档，相信你可以学到更多。

本文的存在更多是类似一个学习笔记，而且本人本身才疏学浅，里面内容不免可能会存在一些矛盾错误或疏漏的地方，如果发现欢迎指出。