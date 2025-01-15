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
import configparser
from xtn_tools_pro.utils.file_utils import check_file_exists


class GoFun:
    def __init__(self, ini_file=""):
        if not ini_file:
            ini_current_dir = os.getcwd()
            ini_file = os.path.join(ini_current_dir, "st.ini")
        if not check_file_exists(ini_file):
            raise Exception("st.ini 配置文件不存在，请在当前文件夹中新建该配置文件")

        # 读取配置信息
        config = configparser.ConfigParser()
        config.read(ini_file)
        server_host = config.get('server', 'host')
        server_port = config.get('server', 'port')
        server_task = config.get('server', 'task')
        server_auto = config.get('server', 'auto')

        print(server_host, server_port, server_task)
        if server_port:
            task_host = f"http://{server_host}:{server_port}"
        else:
            task_host = f"http://{server_host}"

        download_url = task_host + "/filter_server/phone/get"
        upload_url = task_host + "/filter_server/phone/update"

        print(server_auto)
        print(download_url)
        print(upload_url)