#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="xtn-fun-task-pro",  # 模块名称
    version="1.0.0.0.1",  # 版本
    author="xtn",  # 作者
    author_email="xtnkking@hotmail.com",  # 作者邮箱
    description="xtn",  # 模块简介
    long_description=long_description,  # 模块详细介绍
    long_description_content_type="text/markdown",  # 模块详细介绍格式
    packages=setuptools.find_packages(),  # 自动找到项目中导入的模块
    # 模块相关的元数据(更多描述信息)
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    # 依赖模块
    install_requires=[
        "requests",
    ],
    python_requires='>=3',
)
