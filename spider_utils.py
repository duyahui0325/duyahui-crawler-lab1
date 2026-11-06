# -*- coding: utf-8 -*-
"""
spider_utils.py —— 通用网络请求工具函数（可复用）

设计思路：把与具体业务无关的“发送请求 / 取文本 / 取二进制 / 写文件 / 建目录”
抽象成通用函数，案例1、案例2 只负责业务（URL、参数、保存位置），
实现“调用代码与通用函数分离”，提高代码的复用性和健壮性。
"""

from pathlib import Path

import requests

# 默认超时时间（秒），避免网络异常时程序无限等待
DEFAULT_TIMEOUT = 10


def default_headers() -> dict:
    """构造默认请求头：伪装成浏览器，降低被网站反爬拦截的概率。"""
    return {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }


def get_response(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    """发送 GET 请求，返回响应对象；状态码不是 200 时抛出异常。"""
    resp = requests.get(
        url,
        params=params,
        headers=headers or default_headers(),
        timeout=timeout,
    )
    # 状态码不是 200 时抛出 HTTPError，避免后续把错误页面当成数据使用
    resp.raise_for_status()
    return resp


def get_text(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT) -> str:
    """发送 GET 请求并以文本形式返回。

    r.text 默认按响应头中的编码解码，中文网站经常出现乱码，
    因此这里用 apparent_encoding（chardet 推测出的真实编码）重新解码。
    """
    resp = get_response(url, params=params, headers=headers, timeout=timeout)
    resp.encoding = resp.apparent_encoding
    return resp.text


def get_binary(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT) -> bytes:
    """发送 GET 请求并以二进制形式返回（下载图片、音频等非文本资源时使用）。"""
    resp = get_response(url, params=params, headers=headers, timeout=timeout)
    return resp.content


def check_status(resp) -> bool:
    """返回响应是否成功（状态码 200），用于调用方做健壮性判断。"""
    return resp.status_code == requests.codes.ok


def ensure_dir(dir_path) -> Path:
    """创建目录（已存在也不会报错），返回 Path 对象。"""
    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_binary(path, content) -> Path:
    """把二进制数据写入文件（图片、压缩包等），返回文件路径。"""
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "wb") as f:          # wb：二进制写入方式
        f.write(content)
    return path


def save_text(path, text, encoding="utf-8") -> Path:
    """把文本写入文件，默认使用 utf-8 编码（保存网页源码时使用）。"""
    path = Path(path)
    ensure_dir(path.parent)
    with open(path, "w", encoding=encoding) as f:
        f.write(text)
    return path
