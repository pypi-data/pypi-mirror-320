#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: lidongdong
# Mail: 927052521@qq.com
# Created Time: 2022.10.21  19.50
############################################

from setuptools import setup, find_packages

setup(
    name = "MultiAgentKit",
    version = "1.3.2",
    keywords = {"pip", "license","licensetool", "tool", "gm"},
    description = "修复DF查询为空的情况！",
    long_description = "具体功能，请自行挖掘。",
    license = "MIT Licence",

    url = "https://github.com/not_define/please_wait",
    author = "lidongdong",
    author_email = "927052521@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ['numpy','PyYAML']
)
