# -*- coding: utf-8 -*-
"""
案例1：QQ 表情包图片下载（教材 3.4 节，代码重构可复用版）

实现思路：
    1）请求表情包列表页，用正则从 HTML 中提取 <img> 的 src 图片地址；
    2）把不完整的图片地址补全为完整 URL；
    3）逐张发送 GET 请求，得到图片的二进制数据（r.content）；
    4）用二进制写文件的方式把图片保存到本地指定目录，文件名取自 URL 末尾。

重构要点：通用逻辑放到 spider_utils.py，本文件只保留业务相关的
“请求信息定义 + 下载 + 保存 + 流程控制”，函数之间互不依赖，可单独复用。
"""

import re
from pathlib import Path

import requests

from spider_utils import ensure_dir, save_binary

# ==================== (1) 定义请求信息 ====================
BASE_URL = "http://www.bspider.top"           # 站点域名，用于补全图片 URL
LIST_URL = BASE_URL + "/yh31/"                # 表情包列表页地址
HEADERS = {                                   # 请求头：设置用户代理，应对简单反爬
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 10                                  # 超时时间（秒）
SAVE_DIR = Path(__file__).parent / "output" / "images"   # 图片保存目录
MAX_COUNT = 12                                # 本次最多下载的图片数量


def get_image_urls(list_url, headers, timeout=TIMEOUT):
    """请求列表页，解析出页面上所有表情包图片的完整 URL（去重后保持原顺序）。"""
    resp = requests.get(list_url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding        # 按页面真实编码解码，避免中文乱码

    # 图片标签形如：<img src="/static/yh31/images/2021....gif" alt="..." width="160">
    src_list = re.findall(r'<img[^>]+src="([^"]+)"', resp.text)
    urls = []
    for src in src_list:
        if src.startswith("/static/"):            # 只保留表情包图片，过滤图标等资源
            urls.append(BASE_URL + src)           # 相对地址补全为完整地址
    return list(dict.fromkeys(urls))              # 去重（dict 保持插入顺序）


# ==================== (2) 发送请求并获得响应 ====================
def get_image(url, headers, timeout=TIMEOUT):
    """下载单张图片：发送请求 -> 判断状态码 -> 返回二进制数据；失败返回 None。"""
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()                  # 非 200 抛出异常，由 except 捕获
        return resp.content                      # content 是图片的二进制数据
    except Exception as err:                     # 网络异常、超时、404 等统一处理
        print(f"下载失败：{url} -> {err}")
        return None


# ==================== (3) 将响应图片存储到本地 ====================
def save_image(path, content):
    """把图片二进制数据写入磁盘，path 为文件完整路径。"""
    with open(path, "wb") as f:                  # wb：二进制写入，不能用文本模式
        f.write(content)


def main():
    """主函数：负责流程控制，把“取地址 -> 下载 -> 保存”串起来。"""
    ensure_dir(SAVE_DIR)                         # 目录不存在时先创建
    image_urls = get_image_urls(LIST_URL, HEADERS)[:MAX_COUNT]
    print(f"列表页共解析到图片 {len(image_urls)} 张，开始下载……")

    success = 0
    for url in image_urls:
        content = get_image(url, HEADERS)        # (2) 发送请求并获得响应
        if content is None:                      # 单张失败不影响整体流程
            continue
        file_name = url.split("/")[-1]           # 从 URL 中取原始文件名和扩展名
        save_image(SAVE_DIR / file_name, content)   # (3) 存储到本地
        success += 1
        print(f"[{success}] 已保存 {file_name}（{len(content)} 字节）")

    print(f"下载完成：成功 {success} 张，保存目录 -> {SAVE_DIR}")


if __name__ == "__main__":
    main()
