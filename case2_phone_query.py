# -*- coding: utf-8 -*-
"""
案例2：手机号码归属地查询（教材 3.5 节，代码重构可复用版）

实现思路：
    1）ip138 的查询页是典型 GET 请求，参数为 mobile（手机号）和 action；
    2）用字典存放查询参数，交给 requests 的 params 参数自动拼接成
       key=value&key=value 的形式（等价于 urlencode）；
    3）发送请求拿到响应文本，重新设置编码解决中文乱码；
    4）把响应源码保存为本地 html 文件，使用浏览器打开即可看到查询结果。

重构要点：通用请求/写文件函数在 spider_utils.py 中，本文件只保留业务代码。
"""

import re
from pathlib import Path

import requests

from spider_utils import ensure_dir, get_text, save_text

# ==================== (1) 定义请求信息 ====================
QUERY_URL = "https://www.ip138.com/mobile.asp"      # 查询接口地址
PARAMS = {                                          # 查询参数（GET 请求的参数）
    "mobile": "19741881290",                        # 要查询的手机号
    "action": "mobile",
}
HEADERS = {                                         # 请求头：设置用户代理
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}
TIMEOUT = 10
SAVE_DIR = Path(__file__).parent / "output"          # 结果保存目录
HTML_NAME = f"手机归属地_{PARAMS['mobile']}.html"     # 以手机号命名，便于区分


# ==================== (2) 发送请求并获得响应 ====================
def get_html(url, params, headers, timeout=TIMEOUT):
    """发送 GET 请求，返回响应网页的文本内容（已处理编码问题）。"""
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()                      # 状态码非 200 时抛异常
        resp.encoding = resp.apparent_encoding       # 解决中文乱码
        return resp.text                             # 返回网页文本
    except Exception as err:
        print(f"请求失败：{err}")
        return None


# ==================== (3) 将响应存储到本地 html ====================
def save_html(path, html):
    """把网页源码保存为本地 html 文件。"""
    # 原始页面样式表用的是 “//cache.ip138.com/...” 这种省略协议的地址，
    # 本地打开会解析失败导致页面没样式，故插入 <base> 指定基准地址（内容不动）
    html = html.replace("<head>", '<head>\n<base href="https://www.ip138.com/">', 1)
    return save_text(path, html, encoding="utf-8")


def parse_result(html):
    """从返回的源码中提取关键字段，便于在控制台直接查看查询结果。"""
    # 结果表格中手机号后面紧跟“测吉凶”链接，先删除，避免混入电话号码
    html = re.sub(r'<a class="link".*?</a>', "", html, flags=re.S)
    rows = re.findall(r"<tr>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>", html, re.S)

    keywords = ("您查询的手机号码段", "卡号归属地", "运营商", "卡类型", "区号", "邮编")
    info = {}
    for key, value in rows:
        # 去掉标签和多余空白，"运 营 商" 这类带空格的字段名统一成 "运营商"
        key = re.sub(r"<[^>]+>", "", key)
        key = re.sub(r"\s+", "", key)
        if key not in keywords:
            continue
        value = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", value)).strip()
        if value:                                  # 页面确实返回了该字段才记录
            info[key] = value
    return info


def main():
    """主函数：负责流程控制（取数据 -> 保存 -> 打印结果）。"""
    ensure_dir(SAVE_DIR)
    html = get_html(QUERY_URL, PARAMS, HEADERS)      # (2) 发送请求并获得响应
    if html is None:
        print("查询失败，程序结束。")
        return

    save_html(SAVE_DIR / HTML_NAME, html)            # (3) 保存到本地 html
    print(f"响应源码已保存：{SAVE_DIR / HTML_NAME}")
    print(f"源码长度：{len(html)} 字符")

    result = parse_result(html)
    print("=" * 34)
    print("手机号码归属地查询结果")
    print("=" * 34)
    for key, value in result.items():
        print(f"{key}：{value}")
    print("=" * 34)


if __name__ == "__main__":
    main()
