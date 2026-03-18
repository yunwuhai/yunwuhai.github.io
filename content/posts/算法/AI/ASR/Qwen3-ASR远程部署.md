---
date: 2026-03-18T16:46:38+08:00
draft: true
title: 'Qwen3-ASR远程部署'
categories:
 - 算法
tags:
 - ASR
 - AI
 - Qwen3-ASR
 - Qwen
author: ["云雾海"]
description: "记录了远程部署调用Qwen3-ASR模型的流程"
license: CC-BY-SA 4.0
---

# Qwen3-ASR部署

## 前言

### 模型介绍

Qwen3-ASR是阿里的千问团队开发的一个语音识别模型，包括两个版本Qwen3-ASR-1.7B 与 Qwen3-ASR-0.6B，以及一个创新的语音强制对齐模型 Qwen3-ForcedAligner-0.6B。

Qwen3-ASR最具特色的是其支持52个语种和方言的语种识别和语音识别，这在传统只能标准英语和普通话的语音识别模型中有较大突破。

### 部署目标

本人有一台装有4070TIS的Windows主机，同时有一台性能普通的笔记本。因为个人研究需求，需要将Qwen3-ASR模型部署到一台服务器上，刚好这个Windows主机就可以成为我的测试服务器，而笔记本作为客户端与服务器进行通信调用。

### 部署思路

基本的部署思路是，在Windows主机中通过WSL安装miniconda环境，然后部署Qwen3-ASR环境，通过tailscale将主机与笔记本连接，通过ssh在笔记本控制运行WSL，通过tailscale提供的局域网进行通信。本文主要详述Qwen3-ASR部署流程，关于远程部署部分只会简单提及，有需求可以根据提及的部分进行对应搜索。

## 准备工作

1. 一台高性能Windows主机，在本文中其显卡为4070TIS，系统为Windows11，后续我们称为服务器。
2. 另一台电脑，本文中为笔记本，系统为Windows11，后续我们称为客户端。
3. 服务器Windows系统中的tailscale和OpenSSH Server服务。因为我很早之前就已经为这个主机安装了ssh服务器，所以本文默认已经在Windows系统中有ssh服务，并且整个操作均在远端通过ssh访问，而因为服务器没有公网，所以内网穿透由tailscale提供。

## 部署流程

### WSL安装

经过尝试，直接在Windows上部署Qwen3-ASR模型的话，比较容易安装失败，尽管可以通过docker安装，但是在后续开发上仍然可能出现一些类似的踩坑，毕竟我们是为了进行软件开发，所以在WSL上进行安装是更好的选择。

关于WSL的安装，可以参考[官方文档](https://learn.microsoft.com/zh-cn/windows/wsl/install)进行，我直接默认安装的Ubuntu系统。

### tailscale安装

安装完WSL后，我们需要在WSL中安装tailscale，这样我们就可以在远端直接用ssh访问WSL的文件系统了，尽管我们也可以先访问Windows，然后在一个Powershell终端里面通过`wsl`命令访问WSL，但是这种做法无法打开WSL的文件系统，所以直接用tailscale在内部穿透是比较好的方法。关于tailscale的安装，可以参考[官方文档](https://tailscale.com/docs/install/windows/wsl2)。

### ssh服务器

在tailscale安装完成后，就已经获得了一个新的内网IP，此时我们可以通过ssh连接WSL了，不过在此之前需要为WSL安装ssh服务器，安装命令如下：

```bash
sudo apt update
sudo apt install openssh-server
```

由于 WSL2 的一些限制（如默认不支持密码登录或端口冲突），我们需要微调一下配置文件：`sudo nano /etc/ssh/sshd_config`
取消以下内容的注释并根据需要进行修改：

```
Port 2222（建议将端口改为 2222，因为 Windows 自身可能已经占用了 22 端口）。
PasswordAuthentication yes（如果你想用密码登录，请确保这里是 yes）。
ListenAddress 0.0.0.0（允许从任何 IP 访问）。
```

最后保存并退出，按`Ctrl+O`保存，`Enter`确认，`Ctrl+X`退出。

然后重启服务：`sudo service ssh restart`。

通过`tailscale ip`指令可以获取IP地址，然后通过ssh连接WSL。

为了方便，我们可以在vscode中安装[Remote Development](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)来辅助远程开发。

### Miniconda安装

我们当然不希望只在WSL中安装一个Qwen3-ASR模型后就不玩其它模型了，所以Python环境管理工具是很重要的，因为我们在WSL中且不需要什么界面环境，所以安装miniconda即可，参考[官方文档](https://www.anaconda.com/docs/getting-started/miniconda/install/linux-install)进行安装。

安装完成后，我们创建一个conda环境：`conda create -n qwen-asr-env python=3.10 -y`。实际上官方推荐的使用`python=3.12`，但是因为我个人的需求，部分依赖库没有后续更新，所以我选择了`3.10`版本。

之后启动这个环境`conda activate qwen-asr-env`。

### Qwen3-ASR安装

其实到这一步后，部署就已经很简单了：

```bash
pip install -U qwen-asr[vllm]
MAX_JOBS=4 pip install -U flash-attn --no-build-isolation
```

两步就可以完成，但是事实上，在安装Flash Attention的时候很容易失败，我之前是在Windows中安装，就反复失败，但是在WSL中就成功了。另外如果觉得下载很慢，可以修改镜像，只需要通过`export PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple`修改镜像源即可，当然也可以在`install`命令里面直接添加镜像。

### Qwen3-ASR远程调用

在完成部署后，我们就可以在客户端进行远程调用了，因为我们已经通过tailscale分配了IP，现在只需要指定端口即可。下面我写了两个Python脚本，分别运行在客户端和服务器上，实现了包含VAD功能的类流式语音识别，代码没有精修，大概能运行的程度。

#### 服务器端

```python
import socket
import struct
import numpy as np
from qwen_asr import Qwen3ASRModel
import torch.distributed as dist

# 配置参数
ASR_MODEL_PATH = "Qwen/Qwen3-ASR-1.7B"
HOST = "100.xx.xx.xx"          # 换成自己的Tailscale IP
PORT = 8823               # 端口号
SAMPLE_RATE = 16000          # 采样率
BYTES_PER_SAMPLE = 4      # float32 = 4 bytes

def recv_exact(sock, n):
    """接收精确长度的字节数据，直到收满或连接断开"""
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def main():
    print("正在初始化 vLLM 模型...")
    asr = Qwen3ASRModel.LLM(
        model=ASR_MODEL_PATH,
        gpu_memory_utilization=0.6,
        max_model_len=16384,
        max_new_tokens=4096,          # 可根据需要调整
    )
    print("模型加载完成，启动 TCP 服务器...")

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((HOST, PORT))
    server_sock.listen(5)
    print(f"服务器监听 {HOST}:{PORT}，等待客户端连接...")

    try:
        while True:
            client_sock, client_addr = server_sock.accept()
            print(f"客户端 {client_addr} 已连接")

            try:
                while True:
                    len_data = recv_exact(client_sock, 4)
                    if len_data is None:
                        print("客户端断开连接")
                        break
                    data_len = struct.unpack('!I', len_data)[0]
                    if data_len == 0:
                        break
                    audio_data = recv_exact(client_sock, data_len)
                    if audio_data is None:
                        print("客户端断开连接")
                        break

                    audio_seg = np.frombuffer(audio_data, dtype=np.float32).copy()

                    state = asr.init_streaming_state(
                        unfixed_chunk_num=2,
                        unfixed_token_num=5,
                        chunk_size_sec=2.0,
                    )

                    asr.streaming_transcribe(audio_seg, state)

                    asr.finish_streaming_transcribe(state)

                    print(f"[{client_addr}] {state.text}")

            except Exception as e:
                print(f"处理客户端 {client_addr} 时出错: {e}")
            finally:
                client_sock.close()
                print(f"客户端 {client_addr} 连接关闭")

    except KeyboardInterrupt:
        print("服务器关闭")
    finally:
        server_sock.close()
        if hasattr(asr, 'close'):
            asr.close()
        if dist.is_initialized():
            dist.destroy_process_group()

if __name__ == "__main__":
    main()
```

#### 客户端

```python
import socket
import struct
import pyaudio
import numpy as np
import torch
from silero_vad import VADIterator, get_speech_timestamps  # 导入新库

SERVER_IP = '100.xx.xx.xx'  # 服务器的Tailscale IP
SERVER_PORT = 8823
SAMPLE_RATE = 16000
CHUNK_SIZE = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1

print("正在加载 Silero VAD 模型...")
from silero_vad import load_silero_vad
model = load_silero_vad()
vad_iterator = VADIterator(model, sampling_rate=SAMPLE_RATE)
print("VAD 模型加载完成。")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((SERVER_IP, SERVER_PORT))
print(f"已连接到服务器 {SERVER_IP}:{SERVER_PORT}")

p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE)

def send_audio(int16_bytes):
    """将 int16 音频转换为 float32 并发送给服务器"""
    # int16 -> float32 (归一化到 [-1, 1])
    audio_float32 = np.frombuffer(int16_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    data = audio_float32.tobytes()
    # 发送长度前缀 + 音频数据
    sock.sendall(struct.pack('!I', len(data)))
    sock.sendall(data)
    print(f"[客户端] 已发送一句话，长度: {len(int16_bytes)} 字节")

print("开始监听麦克风...（按 Ctrl+C 退出）")
try:
    speech_buffer = []  # 用于缓存当前这句话的音频帧
    while True:
        audio_frame = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        # 转换为 numpy 数组 (int16)
        audio_int16 = np.frombuffer(audio_frame, dtype=np.int16)
        # 转换为 float32 torch tensor (Silero 要求的格式)
        audio_tensor = audio_int16.astype(np.float32) / 32768.0
        audio_tensor = torch.from_numpy(audio_tensor)

        speech_dict = vad_iterator(audio_tensor, return_seconds=False)

        if speech_dict:
            # 如果检测到语音开始 ('start' key)
            if 'start' in speech_dict:
                print("检测到语音开始")

            # 如果检测到语音结束 ('end' key)
            if 'end' in speech_dict:
                print("检测到语音结束")
                # 将缓存的所有音频帧拼接并发送
                if speech_buffer:
                    full_sentence = b''.join(speech_buffer)
                    send_audio(full_sentence)
                    speech_buffer = []  # 清空缓存，准备下一句
                else:
                    print("警告：检测到语音结束，但缓存为空")

        speech_buffer.append(audio_frame)

except KeyboardInterrupt:
    print("\n用户中断")

    # 处理最后可能残留的音频（如果程序在说话中间被中断）
    if speech_buffer:
        print("处理最后残留的音频...")
        if len(speech_buffer) * CHUNK_SIZE / SAMPLE_RATE > 0.5:
            full_sentence = b''.join(speech_buffer)
            send_audio(full_sentence)

finally:
    print("正在清理资源...")
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
    print("客户端已关闭。")
```

通过上述步骤，我们成功地在 Tailscale 网络中部署了一个基于 Silero VAD 的 Qwen3-ASR 服务，并实现了客户端与服务器之间的音频传输和语音识别功能。客户端通过麦克风捕获音频，并发送给服务器进行语音识别，服务器将识别结果返回给客户端，通过ssh可以看到结果。

## 总结

以上就是关于Qwen3-ASR远程部署的过程，整体流程比较粗狂，不过可以作为一个参考，毕竟安装环境只要安装上就行了。享受这个新AI吧。