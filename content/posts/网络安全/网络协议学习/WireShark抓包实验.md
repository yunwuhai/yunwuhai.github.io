---
date: 2025-10-15T22:49:58+08:00
draft: false
title: 'WireShark抓包实验'
categories:
 - 网络协议学习
tags:
 - 网络协议
 - WireShark
 - ICMP
 - TCP
author: ["云雾海"]
description: "使用WireShark并进行网络协议分析"
license: CC-BY-SA 4.0
---

# WireShark抓包实验

## 目标

1. 掌握TCP/IP网络体系结构的网络接口层、网络层、传输层和应用层典型协议（Ethernet II、IP、TCP、ICMP、HTTP）的分析。
2. 分析常用即时通讯软件的通信过程。

## 实验内容

### 抓包PING

Ping命令是一种常用的网络诊断工具，用于测试两台计算机之间的连通性。本次实验中我们通过Ping命令访问百度的网址，并对整个过程进行抓包分析。

1. 我们打开WireShark然后进入抓包界面，并开始抓包。

2. 我们打开命令行，然后输入指令`ping www.baidu.com`。

   ![image-20251012211651131](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251012211651131.png)

### 分析DNS

1. DNS查询报文：因为我们不知道百度的IP地址，所以我们使用域名进行访问，而这个过程中，Ping会向DNS服务器寻求百度的IP地址，然后DNS服务器会返回它的IP地址。我们可以在WireShark中可以发现这两个包。

   ![image-20251012215157514](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251012215157514.png)

   首先让我们分析一下请求包，首先我们可以从统计表中得知数据是从`172.20.*.*`这个网址发出去的，这个就是我们的IP地址，根据网段不难得知这是一个私网网址。根据`Protocol`可以得知这是一个DNS包，而通过`Info`可以得知本次`DNS`查询是一次标准查询，通讯ID号是`0x1c2d`，而其中的`A`表示查询记录类型是IPv4地址（因为我这里的网络没有通IPv6，如果是IPv6，则应该为`AAAA`)，而后面跟的就是我们想要查询IP的网址`www.baidu.com`。让我们看看报文内容。

   首先让我们看看`Ethernet II`，即以太网帧（其中不重要的内容还有隐私内容已被我打码，下同）：

   ![image-20251012220735873](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251012220735873.png)

   我们可以在其中找到我们的以太网帧的帧头，这其中包含了目标MAC地址和源MAC地址，以及帧里面的数据包类型。在WireShark中，我们可以看到右边是实际发送的数据，左边是其解析的含义。

   接着我们观察IPv4报头，这是属于网络层的内容：

   ![image-20251013105029977](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251013105029977.png)

   其中重要的就是我们的源IP地址和目标IP地址，这里我的主机也就是源IP是`172.20.*.*`，目标IP是DNS服务器`61.139.2.69`。不过我们也可以关注一下其它部分，首先开头的`45`中`4`代表IPv4，`5`代表IP首部长度为`5x4=20`字节。*Differentiated Services Field（区分服务字段）*则是用于改善流量转发效果的，此处`DSCP=00(CS0)`让路由器默认处理该数据包，不改变其优先级，而`ECN=00(Not-ECT)`则代表不支持ECN显式拥塞通知功能。而后的`3b`代表IP数据包的总长度为59字节。而后`4c f8`代表其标识符ID。再后面的`0000`则依次代表`Flag(3bit)=0(可以分片但是没有分)`，`Fragment Offset(13bit)=0(片偏移量为0)`。而后`80`代表该报文生存时间为128跳。后面的`11`代表报文所用协议为`UDP`。然后又是个`0000`，代表首部校验和为0，用于校验IP头部的完整性。再然后就是源IP地址和目标IP地址了，前面已经说过。

   再往下则是UDP的报文内容。

   ![image-20251013113324896](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251013113324896.png)

   UDP报文的内容包括源端口号（2byte）、目的端口号（2byte）、UDP报文长度（2byte）、校验和（2byte）。

   然后后面就是我们的DNS报文了，这一部分根本目的是为了顺利获取到域名对应的IP地址：

   ![image-20251014194558517](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251014194558517.png)

   其事务ID（Transaction ID）为0x1c2d，代表该查询的唯一标识，这个查询报文对应的响应报文其事务ID也会是这个。Flags的值为0x0100，则代表了这是一个标准（Opcode=0)查询（Response=0）且授权应答位（Authoritative，在左侧未标注，但是可以观察到Opcode和Truncated中间有一个0，这一位只有在响应报文中有用）和截断位（Truncated）均未设置（=0），期望递归位已设置（Recursion desire=1，这个可以递归解析器，而不需要客户端自己去遍历根、TLD等服务器）、可递归位未设置（Recursion available，在Recursion desire和Z中间有一个0，这一位只有在响应报文中有用），保留位为0（Z=0），应答认证位（Answer authenticated，在Z和Non-authenticated data中间有一个0，表示服务器已经验证了DNSSEC签名，并确认数据是经过认证的，即来自权威源且未被篡改，这个只在响应报文中有用），禁用DNSSEC验证位（CD，即是否需要禁用前面的AD验证，0表示没有禁用，不过因为这里是查询报文，所以WireShark中显示的是Non-Authenticated data）。之后是连续4个2字节的计数字段分析，Questions=1代表报文中包含一个查询问题，后续三个都是在响应报文中才会出现的数据。至于Queries中的数据其实就是查询部分了，域名占用了13个字节（包括点号），不过我们仔细查看报文其实可以发现，这里的点号是用计数的方式来表示实现的，例如最开始的`03 77 77 77`其实代表了`www`，而`03`其实代表的接下来的一个标签（也就是`www`）长度为`3`，后续的`baidu`是`05`，`com` 是 `03`也是同理，而最后面还需要跟一个`00`作为结束符表示后面没有标签了。再后面的`00 01`代表希望查询的IP类型是`A`，即IPv4。最后的`00 01`则代表Class是Internet类，即互联网，这是最常用的类别。至此我们对于DNS查询报文的分析完成。

2. DNS响应报文：关于响应报文，前面的以太网帧头、IP报头、UDP协议包头都没有什么继续分析的必要了，因为本质上和查询报文没有区别，只是方向反过来而已。我们重点关注最后的DNS部分：

   ![image-20251014221115665](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251014221115665.png)

   首先事务ID和查询报文是一样的。其次，它的Flags中Response变为了1，代表是响应报文。Opcode为`0000`，则仍代表该查询是标准查询。授权应答位Authoritative=0，代表该服务器不是该域名的权威服务器。Truncated为`0`代表报文没有截断，完整返回。Recursion Desire为`1`代表客户端希望递归查询。Recursion Desire为`1`代表服务器支持递归查询，提供递归服务。Z是保留位为`0`。Answer Authenticated为`0`表示该答案部分没自由经过DNSSEC认证，Checking Disabled为`0`代表没有禁用DNSSEC认证。Questions为`1`表示查询部分包含1个问问题，Answer RRs为`3`表示有三个资源记录，剩下两个都是0代表没有授权服务器信息和没有附加信息，全是字面意思。Queries和查询报文一样。我们重点还是看Answers部分，这是这个响应报文的核心部分。我们从Answer RRs中可以知道，我们有三个答案记录，而第一个记录的Name是`www.baidu.com`，Type是`CNAME`，Class是`Internet`。我们应当注意的是，这里的Name在报文中显示的数据是`c0 0c`，这里其实是代表的一个类似于指针的设置，用于指示重复的域名以缩减报文传输量，`c`的二进制是`1100`，其中`11`其实代表的就是这是个指针，而后的`00`以及后面的12bit，共同组成了偏移量，这样它就指示到了从DNS报文的0字节开始，往后第12字节开始的那个域名，正是`wwww.baidu.com`，后面出现类似情况也是同理。然后我们注意这里的Type是`CNAME`，也就是说它其实是检测到一个别名了，而这个别名的值是`www.a.shifen.com`，这个是百度以前的一个广告系统的网址，看来百度是直接把它的`www.baidu.com`域名连接到这个域名上了，它还可以将其它域名的别名也设置成这个，这样未来如果需要迁移地址，只需要迁移这个域名的地址就可以了。然后我们可以查看下面这个域名，检测到两个IP，分别是`183.2.172.177`和`183.2.172.17`，看样子百度用了多IP轮询机制来实现负载均衡或者容灾备份。最终从我们的Ping命令效果来看，我们最终应该是选用了第一个，或者说当时第一个就可以联通，不需要使用第二个备用IP了。

### 分析ICMP

1. ICMP报文：在获取到DNS响应报文后，程序即获得了IP地址，此时即可以通过ICMP报文与服务器通信。PING命令会连续发送四条ICMP报文，并根据返回报文计算连通性性和通信时间，我们只需要分析其中一对即可。

   ![image-20251015162525481](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015162525481.png)

   ICMP报文由三部分组成：以太网帧头、IP报头和ICMP协议数据部分。其中前两者和DNS相比差不多，只是内容存在部分差异，我们就不重复详细分析了。重点针对ICMP协议数据部分进行讨论：

   ![image-20251015164123794](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015164123794.png)

   我们首先观察Type=`8`，其代表了这是一个回显请求，即`ping`的发送端。而Code=`0`则代表了无特殊错误码，正常请求。Checksum=`0x4d2c`是一个校验字段，用于验证报文完整性，已校验通过。Identifier(BE)=`1`表示发送大端格式的进程标识符，通常是进程的ID或者PID，此处为1。Identifier(LE)=`256`表示小端格式的进程标识符，对应了BE的值，本质上其实就是同一个值。Sequence Number(BE)=`47`表示大端格式的序列号，LE=`12032`表示小端格式的序列号，本质上就是同一个值。而后的Data部分有32个字节，根据ASCII码不难发现，其实发送的内容本质就是`abcdefghijklmnopqrstuvwabcdefghi`，其目的其实就是为了填充数据，没有实际含义。接下来让我们查看响应报文：

   ![image-20251015165452997](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015165452997.png)

   不难发现，其实内容也没有什么区别，只有Type变为了`0`，代表这是回显应答，即`ping`的响应端。校验和在值上发生了改变但是结果仍然正确没有问题。并且我们可以看到Response time=`35.251ms`，与我们在终端看到的`35ms`是对应的，这其实是抓包工具计算出的时间，并不在报文之中。

### 分析HTTP

1. HTTP报文：现在让我们分析一下方法百度的三次握手包。因为只是初次尝试，我们选择访问`HTTP`的百度。通过在命令行中运行`nslookup baidu.com`这个代码获取百度网页的ip地址。

   ![image-20251015172626691](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015172626691.png)

   应答中出现了两个地址，我们选择访问第一个试试，在此之前记得打开Wireshark：

   ![image-20251015172741106](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015172741106.png)

   看来没问题，然后我们在Wireshark中添加过滤来找到这个访问，输入`ip.host == 39.156.70.37`然后回车即可：

   ![image-20251015173409903](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015173409903.png)

   然后我们就可以查看显示结果了：

   ![image-20251015185910439](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015185910439.png)

   可以发现，不知道为何，我们这里出现了两个三次握手，不过下面有一个HTTP报文，可以通过它来分析哪一个才是我们需要的。其中关于以太网帧和IP数据包的部分仍然可以忽略，让我们观察TCP部分：

   ![image-20251015190542901](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015190542901.png)

   TCP部分可以注意到其Source Port是59049，Destination Port是80，说明我们只需要找到上方同样通信Port是59049和80的报文就可以了，刚好有三个，可以组成三次握手。其它的都是一些传输信息，我们不需要太关注。HTTP报文中在TCP后面还有一个HTTP部分，这一部分其实就是该网页的一些基础信息，不同网页内容也不一样，这里我们也同样不关注。

### 分析三次握手

1. 三次握手报文：在三次握手中，我们主要需要关注的还是TCP部分。

   这是第一次握手的内容：

   ![image-20251015205007760](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015205007760.png)

   我们可以注意到其Flags的SYN标志被置为1了，这是而ACK仍为0，所以这显然是第一次握手的内容。而Sequence Number初始为0，因为这是当前客户端的第一个报文。Acknowledgment Number被设置为0，因为这是第一次握手。Options中则设置了包括分块等一系列设置，这会在前两次握手中出现。

   现在我们观察第二次握手的报文：

   ![image-20251015205638328](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015205638328.png)

   这一次我们可以看到Flags中的ACK被置为1了，而Syn也仍然为1，可以判断这是第二次握手。Sequence Number也仍然为0，因为这是服务器的第一个报文。而Acknowledgment Number则为1，因为已经接收到一次报文了。Options仍然有一些反馈设置。

   我们观察第三次握手报文：

   ![image-20251015205959870](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015205959870.png)

   在这一次中，Flags中只有ACK被置为1，同时Sequence Number变成了1，Acknowledgment Number也变成了1，符合我们的发送接收情况。同时我们可以注意这一次没有Options了。

   至此，我们的三次握手分析完毕。

### 分析微信

1. 接下来我们简单分析一下微信的数据传输，首先我们需要确定微信通信的IP地址，这个过程非常简单，我们只需要打开资源管理器并选中网络部分，接着给文件传输助手发送一个比较大的文件，然后观察资源管理器中的变化就可以了。

   ![image-20251015215753890](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015215753890.png)
   
   显然，我们获知了微信的IP地址，现在让我们在筛选器中填入`ip.addr == 219.153.153.110`就好了，接着我们会发现一大堆GQUIC报文：
   
   ![image-20251015221134577](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015221134577.png)
   
   关于QUIC的介绍可以参考《[QUIC协议详解](https://zhuanlan.zhihu.com/p/405387352)》，而gQUIC则是谷歌的版本，与其相对的是IETF版本的iQUIC。
   
   ![image-20251015220956982](https://raw.githubusercontent.com/yunwuhai/blog-img/master/img/image-20251015220956982.png)
   
   我们通过前面的介绍还有名字不难发现微信使用的QUIC协议本质上其实就是一种UDP的传输层协议，在协议中通过QUIC将实际需要发送的UDP数据加密打包发送。

## 总结

通过本次实验，我们完成了包括针对PING、三次握手、微信传输三个大流程中使用到的各个报文的抓包和协议解析，基本掌握了WireShark的操作方法和筛选技巧，以及针对具体应用（如微信）如何通过资源管理器进行限位，以快速找到通信IP地址实现抓包。







