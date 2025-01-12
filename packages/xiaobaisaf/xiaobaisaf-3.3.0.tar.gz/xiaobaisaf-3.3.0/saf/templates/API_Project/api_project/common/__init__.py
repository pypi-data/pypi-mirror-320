#! /usr/bin/env python
'''
Auther      : xiaobaiTser
Email       : 807447312@qq.com
createTime  : 2024/11/18 23:27
fileName    : __init__.py.py
'''

import os
import platform
import subprocess
import shutil
from .. import (
    DATA_DIR_PATH,
    REPORT_DIR_PATH,
    ALLURE_REPORT_DIR_PATH,
    PROJECT_CLEAN
)
from .ENV import ENV
from ..config.host_config import HOST
from..config.allure_config import Allure
from .LOG import Logger

logger = Logger()

def _clean(path:str = None):
    '''
    清空文件及或者删除指定的文件
    :param path: 文件夹或者文件
    :return:
    '''
    path = os.path.abspath(path)
    if os.path.isdir(path):
        try:
            shutil.rmtree(path)
            logger.info(f'[{path}]\t文件夹已经清空完毕~')
        except Exception as e:
            logger.error(str(e))
        if not os.path.exists(path):
            os.mkdir(path)
            logger.info(f'[{path}]\t文件夹已经创建完毕~')
    elif os.path.isfile(path):
        try:
            os.remove(path)
            logger.info(f'[{path}]\t文件已经删除完毕~')
        except Exception as e:
            logger.error(str(e))

def clean():
    ''' 清除上次执行的数据 '''

    if PROJECT_CLEAN.data_status:
        _clean(DATA_DIR_PATH)
    if PROJECT_CLEAN.report_status:
        _clean(REPORT_DIR_PATH)
    if PROJECT_CLEAN.allure_report_status:
        _clean(ALLURE_REPORT_DIR_PATH)

def kill_process(port:int = 0):
    if port == 0:
        return
    system = platform.system()
    if system == "Windows":
        try:
            result = subprocess.run(
                ['netstat', '-ano', '|', 'findstr', f':{port}'],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                pids = set()
                for line in lines:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[4]
                        pids.add(pid)
                for pid in pids:
                    subprocess.run(['taskkill', '/F', '/PID', pid], check=True)
                logger.info(f"已尝试在Windows系统中正常关闭占用端口 {port} 的进程")
            else:
                logger.error(f"在Windows系统中查找占用端口 {port} 的进程时出错: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"在Windows系统中终止占用端口 {port} 的进程时出错: {e}")
    elif system == "Linux" or system == "Darwin":  # Darwin是macOS系统对应的标识
        try:
            result = subprocess.run(
                ['lsof', '-t', '-i:{}'.format(port)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    subprocess.run(['kill', '-15', pid], check=True)
                logger.info(f"已尝试在 {system} 系统中正常关闭占用端口 {port} 的进程")
            else:
                logger.error(f"在 {system} 系统中查找占用端口 {port} 的进程时出错: {result.stderr}")
        except subprocess.CalledProcessError as e:
            logger.error(f"在 {system} 系统中终止占用端口 {port} 的进程时出错: {e}")
    else:
        logger.warning(f"不支持的操作系统: {system}")

def init():
    ''' 初始化 '''
    clean()
    ENV.load()
    ENV.set_env('HOST', HOST.CURRENT_HOST)
    kill_process(Allure.PORT)
    logger.info('初始化完毕~')
