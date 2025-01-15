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
    def __init__(self, ini_dict):
        # 读取配置信息
        host = ini_dict.get('host', '')
        port = ini_dict.get('port', 0)
        task = ini_dict.get('task', '')
        auto = ini_dict.get('auto', '')
        is_processes = ini_dict.get('is_processes', False)
        processes_num = ini_dict.get('processes_num', 0)
        is_thread = ini_dict.get('is_thread', False)
        thread_num = ini_dict.get('thread_num', 0)

        self.__ini_info = {
            "host": host,
            "port": port,
            "task": task,
            "auto": auto,
            "is_processes": is_processes,
            "processes_num": processes_num,
            "is_thread": is_thread,
            "thread_num": thread_num,
        }

        for server_k, server_v in self.__ini_info.items():
            if not server_v and server_k not in ["port", "is_processes", "processes_num", "is_thread", "thread_num"]:
                raise Exception(f"ini_dict 配置 {server_k} 不存在")

        if port:
            task_host = f"http://{host}:{port}"
        else:
            task_host = f"http://{host}"

        download_url = task_host + "/filter_server/phone/get"
        upload_url = task_host + "/filter_server/phone/update"

        self.__ini_info["download_url"] = download_url
        self.__ini_info["upload_url"] = upload_url

        print(self.__ini_info)
