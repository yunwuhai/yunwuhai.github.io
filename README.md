# 云雾海的个人博客

## 简介

这个仓库用于存放本人平常的文章笔记，使用 [Hugo](https://gohugo.io/) 生成静态站点，主题为 [Stack](https://github.com/CaiJimmy/hugo-theme-stack)，通过 GitHub Pages 发布。

访问地址：<https://yunwuhai.github.io/>

文章笔记主要是个人在学习开发过程中进行的一些记录，不保证内容实现的准确性和一致性，请酌情参考。

## 技术栈

| 项目 | 说明 |
| --- | --- |
| 生成器 | Hugo **extended** `0.168.0`（Stack 主题要求 ≥ 0.157.0） |
| 主题 | [hugo-theme-stack](https://github.com/CaiJimmy/hugo-theme-stack) v4.0.3（git submodule） |
| 样式 | SCSS 由 **Dart Sass** 编译（站点覆盖了主题的 `head/style.html`），`assets/scss/custom.scss` 存放所有自定义样式 |
| 搜索 | Stack 内置的客户端搜索，索引由 `/search/index.json` 提供 |
| 部署 | GitHub Actions 构建 → GitHub Pages |

## 目录结构

```text
content/
  posts/                    # 全部文章（leaf bundle：每篇一个目录，内含 index.md + cover.jpg）
    嵌入式/                 # Arduino / C_CPP / USB / 硬件设计 / 工具链
    算法/                   # 题目 / 自制脚本语言
    网络安全/
    工具与环境/
    桌面端/
    杂谈/
  archive.md                # /archives/ 归档页
  search.md                 # /search/ 搜索页
  categories/_index.md      # /categories/ 分类总览
  tags/_index.md            # /tags/ 标签总览
layouts/                    # 站点级覆盖模板（不改主题源码）
  posts/overview.html       # 目录页 /posts/ 的三段式布局
  taxonomy.html             # 分类/标签总览的标签墙
  archives.html             # 归档页
  _partials/article-list/tile.html   # 分区卡片（补篇数与描述）
  _partials/head/style.html          # 用 Dart Sass 编译样式
  _partials/head/custom-font.html    # 置空，去掉 Google Fonts 请求
assets/
  scss/custom.scss          # 站点自定义样式
  icons/brand-bilibili.svg  # 主题没有的图标需要自己补
  avatar.png, favicon.png
i18n/zh-cn.toml             # 简体中文文案（站点语言键是 zh-cn，需自带一份）
scripts/covers/gen_cover.py # 封面图生成器（1200x630）
static/                     # 站点验证文件、旧 URL 跳转页
themes/hugo-theme-stack/    # 主题（git submodule）
```

## 本地开发

### 环境要求

- **Hugo extended** ≥ 0.157.0（工作流与文档统一使用 `0.168.0`）
- **Dart Sass** ≥ 1.92.1（需在 `PATH` 中，Hugo 会自动调用）
- Git

> 主题用 SCSS，非 extended 版 Hugo 会报 `you need the extended version to build SCSS/SASS`。

### 首次克隆

```bash
git clone --recurse-submodules git@github.com:yunwuhai/yunwuhai.github.io.git
```

已克隆但没拉子模块时：

```bash
git submodule update --init --recursive
```

### 本地预览

```bash
hugo server          # 默认 http://localhost:1313/
hugo server -D       # 连同草稿一起预览
```

若本地缓存目录不可写（Windows 上常见 `Access is denied`），先设置：

```powershell
$env:HUGO_CACHEDIR = 'C:/hugo_cache'
```

### 构建自检

```bash
hugo --gc --minify
```

## 写一篇新文章

```bash
hugo new content posts/嵌入式/C_CPP/文章标题/index.md
```

文章使用 leaf bundle 结构，正文与封面图放在同一目录：

```text
content/posts/嵌入式/C_CPP/文章标题/
  index.md
  cover.jpg     # 可选，front matter 里写 image: "cover.jpg"
```

front matter 示例：

```yaml
---
title: "文章标题"
date: 2026-01-01T12:00:00+08:00
draft: false
image: "cover.jpg"        # 与 index.md 同目录的 cover.jpg
categories:
  - C_CPP                 # 第一个必须与本篇文章所属分组一致（分组名会出现在分类页）
tags:
  - C
author: ["云雾海"]
description: 一句话摘要
license: CC-BY-SA 4.0
---
```

> `categories` 的第一项决定文章在分类页归到哪一组；现有各文章用的是「题目 / C_CPP / Arduino / USB / 硬件设计 / 工具链 / 自制脚本语言 / 工具与环境 / 网络安全 / 桌面端 / 杂谈」。改这一项等于改分类页结构，旧 term 的 URL 会失效，需要按下一节的办法补跳转。

批量重新生成封面图（需要 Python + Pillow，以及中文字体 `msyhbd.ttc`）：

```bash
python scripts/covers/gen_cover.py
```

## 发布方式

已使用 GitHub Actions + GitHub Pages 自动部署：

1. 提交并推送到 `master`
2. Actions 自动构建（Hugo 0.168.0 extended + Dart Sass）
3. 构建成功后发布到 GitHub Pages

因此本地**不需要**提交 `public/` 目录，本地构建只用于自检。

### 改分区 / 改 URL 时的注意事项

GitHub Pages 没有服务端重定向，一旦文章的目录名变了，旧链接就会 404。搬家时请：

1. 在文章 front matter 里加 `aliases`，写**旧 URL 的精确形式**（Hugo 生成的 permalink 里中文是小写百分号编码，aliases 要与之完全一致）；
2. 已被删除的分类 term，在 `static/categories/<旧名称>/index.html` 放一个静态跳转页。

现有全部旧 URL 都已保留，改动后建议用线上 `sitemap.xml` 的 URL 列表与本地 `public/` 做一次比对。

## 维护备忘

- **i18n**：站点语言键是 `zh-cn`，主题只提供 `zh.toml`，Hugo 不会自动回退，因此仓库自带一份 `i18n/zh-cn.toml`。改界面文案就改这里。
- **不要改主题源码**：`themes/hugo-theme-stack` 是 submodule，所有改动都通过站点级覆盖完成（`layouts/`、`assets/scss/custom.scss`、`assets/icons/`）。
- **正文图片全部本地化**：所有正文图片都放在各自文章的 leaf bundle 里（`content/posts/<分区>/<文章>/img/*.webp`），Markdown 里用相对路径 `img/xxx.webp` 引用。仓库里不再有外链图片，构建完全不依赖外网。
  - 图片格式统一 WebP（q82，长边 ≤1400px），动图按体积决定转 WebP 还是保留 GIF。
  - `layouts/_markup/render-image.html` 仍保留远程图兜底分支：万一以后又贴了外链，直接输出朴素 `<img referrerpolicy="no-referrer">`，不会触发 `resources.GetRemote` 拖慢构建。
  - 加图时把图片放进对应文章的 `img/` 目录即可；leaf bundle 里未被引用的文件也会被发布，所以别留废弃图片。
  - **单张图控制在 200 KB 以内**：WebP 已压缩过，Git 无法再压缩，仓库体积约等于图片字节总和。目前 294 张图共 11 MB，平均 38 KB/张。
  - 替换已有图片时注意 Git 无法去重：每换一次都是历史里的完整副本，别对同一张图反复微调重存。
- **封面图是纯装饰**：`scripts/covers/gen_cover.py` 只按分区配色生成渐变+纹理背景，**不画标题文字**（标题由主题在卡片和文章页渲染，重复会重影）。颜色表在脚本里的 `TOP_COLORS` / `SUB_COLORS`。
- **CI 用 `fetch-depth: 1`**：`hugo.toml` 里 `enableGitInfo = false`，构建不读 Git 历史，因此浅克隆即可。如果以后要按 commit 时间生成"最后更新"，需把 `.github/workflows/hugo.yaml` 的 `fetch-depth` 改回 `0` 并打开 `enableGitInfo`。
- **文件名不要带 `#`**：曾有一篇目录名含 `#`，导致 Hugo 生成的 srcset 在 `#` 处截断 URL、产生 18 处死链。现已改名并用 alias + 静态跳转页保住旧链接。

## 开源协议

博客所有笔记均为原创，采用 [Creative Commons Attribution-ShareAlike 4.0 International License][cc-by-sa] 协议进行授权，部分文章首发于 CSDN ，可以访问[我的主页](https://blog.csdn.net/qq_44884716)查看。

[![CC BY-SA 4.0][cc-by-sa-image]][cc-by-sa]

[cc-by-sa]: http://creativecommons.org/licenses/by-sa/4.0/
[cc-by-sa-image]: https://licensebuttons.net/l/by-sa/4.0/88x31.png
