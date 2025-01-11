# ddddocr-basic

Basic version of [ddddocr](https://github.com/sml2h3/ddddocr) (OCR only).

---

DdddOcr，其由 [本作者](https://github.com/sml2h3) 与 [kerlomz](https://github.com/kerlomz) 共同合作完成，通过大批量生成随机数据后进行深度网络训练，本身并非针对任何一家验证码厂商而制作，本库使用效果完全靠玄学，可能可以识别，可能不能识别。

DdddOcr、最简依赖的理念，尽量减少用户的配置和使用成本，希望给每一位测试者带来舒适的体验

项目地址： [点我传送](https://github.com/sml2h3/ddddocr)

<!-- PROJECT LOGO -->
<br />

<p align="center">
  <a href="https://github.com/sml2h3/ddddocr/">
    <img src="https://cdn.wenanzhe.com/img/logo.png!/crop/700x500a400a500" alt="Logo">
  </a>
  <p align="center">
    一个容易使用的通用验证码识别python库
    <br />
    <a href="https://github.com/sml2h3/ddddocr/"><strong>探索本项目的文档 »</strong></a>
    <br />
    <br />
    ·
    <a href="https://github.com/sml2h3/ddddocr/issues">报告Bug</a>
    ·
    <a href="https://github.com/sml2h3/ddddocr/issues">提出新特性</a>
  </p>

</p>

### 上手指南

###### 环境支持

| 系统             | CPU | 备注                                                                             |
| ---------------- | --- | -------------------------------------------------------------------------------- |
| Windows 64 位    | √   | 部分版本 windows 需要安装<a href="https://www.ghxi.com/yxkhj.html">vc 运行库</a> |
| Windows 32 位    | ×   |                                                                                  |
| Linux 64 / ARM64 | √   |                                                                                  |
| Linux 32         | ×   |                                                                                  |
| Macos X64        | √   | M1/M2/M3...芯片参考<a href="https://github.com/sml2h3/ddddocr/issues/67">#67</a> |

###### **安装步骤**

**从 pypi 安装**

```sh
pip install ddddocr-basic
```

### 项目底层支持

本项目基于[dddd_trainer](https://github.com/sml2h3/dddd_trainer) 训练所得，训练底层框架位 pytorch，ddddocr 推理底层抵赖于[onnxruntime](https://pypi.org/project/onnxruntime/)，故本项目的最大兼容性与 python 版本支持主要取决于[onnxruntime](https://pypi.org/project/onnxruntime/)。

### 使用文档

##### 基础 ocr 识别能力

主要用于识别单行文字，即文字部分占据图片的主体部分，例如常见的英数验证码等，本项目可以对中文、英文（随机大小写 or 通过设置结果范围圈定大小写）、数字以及部分特殊字符。

```python
# example.py
import ddddocr

ocr = ddddocr.DdddOcr()

image = open("example.jpg", "rb").read()
result = ocr.classification(image)
print(result)
```

**注意**

之前发现很多人喜欢在每次 ocr 识别的时候都重新初始化 ddddocr，即每次都执行`ocr = ddddocr.DdddOcr()`，这是错误的，通常来说只需要初始化一次即可，因为每次初始化和初始化后的第一次识别速度都非常慢

**参考例图**

包括且不限于以下图片

<img src="https://cdn.wenanzhe.com/img/20210715211733855.png" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/78b7f57d-371d-4b65-afb2-d19608ae1892.png" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20211226142305.png" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20211226142325.png" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/2AMLyA_fd83e1f1800e829033417ae6dd0e0ae0.png" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/aabd_181ae81dd5526b8b89f987d1179266ce.jpg" alt="captcha" width="150">
<br />
<img src="https://cdn.wenanzhe.com/img/2bghz_b504e9f9de1ed7070102d21c6481e0cf.png" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/0000_z4ecc2p65rxc610x.jpg" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/2acd_0586b6b36858a4e8a9939db8a7ec07b7.jpg" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/2a8r_79074e311d573d31e1630978fe04b990.jpg" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/aftf_C2vHZlk8540y3qAmCM.bmp" alt="captcha" width="150">
<img src="https://cdn.wenanzhe.com/img/%E5%BE%AE%E4%BF%A1%E6%88%AA%E5%9B%BE_20211226144057.png" alt="captcha" width="150">
