#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 说明：
#    程序说明xxxxxxxxxxxxxxxxxxx
# History:
# Date          Author    Version       Modification
# --------------------------------------------------------------------------------------------------
# 2025/1/14    xiatn     V00.01.000    新建
# --------------------------------------------------------------------------------------------------
import os
from xtn_tools_pro.utils.file_utils import check_file_exists


class GoFun:
    def __init__(self, ini_file=""):
        if not ini_file:
            ini_current_dir = os.getcwd()
            ini_file = os.path.join(ini_current_dir, "st.ini")
            if not check_file_exists(ini_file):
                raise Exception("st.ini 配置文件不存在，请在当前文件夹中新建该配置文件")

            print(ini_file)
            print(f"The current working directory is: {ini_current_dir}")
