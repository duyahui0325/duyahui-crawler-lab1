# 实验一 静态网页爬取（QQ 表情包下载 + 手机归属地查询）

《大数据采集与处理》实验一配套代码，对应教材第 3 章 **3.4 案例 1** 与 **3.5 案例 2**。

两个案例均按要求编写为**代码重构可复用版**：把“发请求、取数据、存文件”等通用逻辑
抽到 `spider_utils.py`，业务脚本只保留参数定义与主流程，调用代码与通用函数分离。

## 目录结构

```
.
├── spider_utils.py        # 通用函数：发送请求、取文本/二进制、建目录、写文件
├── case1_qq_emoji.py      # 案例1：解析列表页 → 下载多张表情包 → 保存到 output/images
├── case2_phone_query.py   # 案例2：GET 查询手机归属地 → 保存到 output/手机归属地_<手机号>.html
├── requirements.txt       # 依赖（requests）
├── output/
│   ├── images/            # 案例1 下载的表情包（已提交 12 张）
│   └── *.html             # 案例2 保存的查询页源码（运行后生成，不提交）
└── README.md
```

## 环境

- Python 3.12
- requests 2.34.2（`python -m pip install -r requirements.txt`）
- 其余为 Python 标准库：`re`、`pathlib`、`urllib.parse`

## 运行

```bash
python case1_qq_emoji.py     # 下载 12 张表情包到 output/images/
python case2_phone_query.py  # 查询手机归属地并保存为本地 html
```

案例 2 中的手机号在 `case2_phone_query.py` 顶部的 `PARAMS` 字典里，改成自己的号码即可。

## 实现要点

**案例 1（QQ 表情包图片下载）**

1. 请求列表页 `http://www.bspider.top/yh31/`，用正则从 HTML 中取出 `<img src="...">`；
2. 页面里是 `/static/...` 相对地址，程序自动用站点域名补全为完整 URL，并过滤站点图标等无关资源；
3. `get_image()` 逐张发送 GET 请求，`resp.raise_for_status()` 判断状态码，`resp.content` 取二进制；
4. `save_image()` 以 `wb` 模式写入磁盘，文件名取自 URL 末尾；
5. `main()` 负责流程控制，单张失败（`try…except`）不影响整体。

**案例 2（手机号码归属地查询）**

1. ip138 查询接口是典型 GET 请求，参数为 `mobile`、`action`，用字典交给 `requests` 的 `params` 自动拼接；
2. 设置 `User-Agent` 请求头，`resp.raise_for_status()` 处理异常状态码；
3. `resp.encoding = resp.apparent_encoding` 解决中文乱码；
4. 响应源码保存为本地 html；由于页面 CSS 使用 `//cache.ip138.com/...` 这种省略协议的地址，
   保存时插入 `<base href="https://www.ip138.com/">`，本地打开才能正常显示样式（内容不做修改）。

## 运行结果示例

案例 1：从列表页解析出 12 张表情包并全部下载成功，见 `output/images/`。

案例 2：控制台输出形如

```
响应源码已保存：...\output\手机归属地_xxxxxxxxxxx.html
==================================
手机号码归属地查询结果
==================================
您查询的手机号码段：xxxxxxxxxxx
卡号归属地：江苏 淮安
运营商：中国移动
区号：0517
邮编：223000
==================================
```

## 说明

- 教材中给出的镜像地址 `http://www.bspider.top/ip138/` 已不能返回真实查询结果（只返回查询表单页），
  因此案例 2 直接请求 `https://www.ip138.com/mobile.asp`。
- 站点结构和反爬策略可能变化；若请求失败，先检查目标页面是否仍可访问、是否需要更新正则或请求头。
