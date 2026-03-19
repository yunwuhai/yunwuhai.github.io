---
date: 2026-03-19T11:56:51+08:00
draft: false
title: 'Mihomo远程部署'
categories:
 - 解决方案
tags:
 - Mihomo
 - Clash
 - WSL
author: ["云雾海"]
description: "在WSL中部署Mihomo"
license: CC-BY-SA 4.0
---

# Mihomo远程部署

## 前言

因为在WSL中需要下载一些东西，而因为电脑又在远程，无法使用GUI，且如果直接调用Windows中的Mihomo，会导致ssh无法正常连接，故在此直接在WSL中部署Mihomo。

## 工作环境

1. WSL2环境
2. Tailscale
3. SSH

## 步骤

### 下载Mihomo

此部分不要直接完全复制，请根据最新版本[替换链接](https://github.com/MetaCubeX/mihomo/releases)
```bash
# 创建目录
mkdir ~/mihomo && cd ~/mihomo

# 下载链接，根据最新链接进行替换，注意应选择mihomo-linux-amd64-vx.xx.x.gz
wget https://github.com/MetaCubeX/mihomo/releases/download/v1.18.9/mihomo-linux-amd64-v1.18.9.gz

# 解压并重命名
gunzip mihomo-linux-amd64-v1.18.9.gz
mv mihomo-linux-amd64-v1.18.9 mihomo
chmod +x mihomo
```

### 配置核心文件

#### 下载地理文件

这个文件一般Mihomo在初次运行时会自动下载，但是经常失败，所以直接手动下载
```bash
wget -O Country.mmdb https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/geoip.metadb
```

#### 配置设置文件

你应该会有一个订阅链接，通过这个订阅链接可以下载一个config.yaml文件，使用以下语句进行下载：
```bash
curl -L -o config.yaml "https://api.v1.mk/sub?target=clash&url=你的订阅链接"
```

#### 初步测试

```bash
./mihomo -d .
```

如果一切正常，应该会看到`Start initial configuration successful`之类的内容，并且在shell中它展开了一个服务。

### 常驻后台
#### 移动文件

将Mihomo文件移动到`/usr/local/bin`中，这样就可以直接使用`mihomo`命令了。

```bash
sudo mv mihomo /usr/local/bin/
sudo mkdir -p /etc/mihomo
sudo cp Country.mmdb /etc/mihomo/
sudo cp config.yaml /etc/mihomo/
```

#### 使用systemd守护进程

创建服务文件`sudo nano /etc/systemd/system/mihomo.service`

然后写下以下内容：

```TOML
[Unit]
Description=mihomo Daemon
After=network.target

[Service]
Type=simple
Restart=always
ExecStart=/usr/local/bin/mihomo -d /etc/mihomo

[Install]
WantedBy=multi-user.target
```

再`Ctrl+O`、`Enter`、`Ctrl+X`保存文件。

#### 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable mihomo
sudo systemctl start mihomo
```

### 配置启动命令

在`~/.bashrc`中添加以下内容：

```bash
# 代理开关快捷键
alias proxy="export https_proxy='http://127.0.0.1:7890'; export http_proxy='http://127.0.0.1:7890'; echo 'Proxy ON'"
alias unproxy="unset https_proxy; unset http_proxy; echo 'Proxy OFF'"
```

然后`source ~/.bashrc`使其生效。

之后输入`proxy`命令，即可使用代理。输入`unproxy`命令，即可取消代理。

### 界面化配置

我们有时候需要修改连接线路，如果直接在config里面修改很麻烦，通过yacd可以很方便地解决这一问题。

#### 安装yacd

```bash
cd /etc/mihomo
sudo git clone -b gh-pages https://github.com/haishanh/yacd.git dashboard
```

#### 修改`config.yaml`

在`config.yaml`中添加以下内容：

```yaml
external-controller: 0.0.0.0:9090  # 允许外部连接控制端口
external-ui: dashboard             # 刚才下载的文件夹名称
secret: "你的密码"                  # 设置一个密码，防止别人乱动
```

然后重启mihomo：`sudo systemctl restart mihomo`。

#### 访问yacd

在浏览器中输入`http://tailscale的IP地址:9090/ui`，即可访问yacd。

至此，Mihomo的远程部署就完成了。