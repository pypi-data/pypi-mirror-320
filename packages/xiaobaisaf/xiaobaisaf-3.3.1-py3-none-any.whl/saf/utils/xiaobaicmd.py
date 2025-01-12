#! /usr/bin/env python
"""
@Author: xiaobaiTser
@Time  : 2022/8/24 2:26
@File  : xiaobaicmd.py
"""
try:
    import click
except ImportError:
    raise ImportError("请先安装click模块：pip install click")
import os.path
from shutil import copytree
from saf.utils.FlushDNSUtils import flushDNS
from saf.utils.MonitorAndroidPackageGUI import gui
from saf.utils.MonitorAndroidPackageCLI import cli
from saf.utils.MonitorAndroidDeviceGUI import MonitorDevice
from saf.utils.MonitorAndroidPackagePower import power
from saf.utils.MonitorCP import cpmain

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

@click.command()
@click.option(
    "--template",
    "-t",
    type=click.Choice(["web", "api", "app"]),
    nargs=1,
    help="创建自动化项目模板",
)
@click.option("--dirname", "-d", default=".", type=str, nargs=1, help="创建自动化项目模板存放的目录")
@click.option(
    "--domains",
    type=str,
    nargs=1,
    help='用户提供多域名使用","分割自动获取DNS解析结果并写入HOSTS文件，\n例如：--domains github.com,raw.githubusercontent.com',
)
@click.option(
    "--monitor",
    "-m",
    type=click.Choice(["gui", "cli", "power", "memory", "cp"]),
    nargs=1,
    help="监控自动识别APP页面点击/滑动的Xpath表达式与坐标信息或者监控设备电量与APP内存使用率，监听粘贴板转为requests代码",
)
@click.option("--device", "-e", type=int, nargs=1, help="监控设备的界面图像，从1开始计算设备序号，暂无其他功能")
def main(template, dirname, domains, monitor, device):
    if template:
        if "web" == template.lower():
            copytree(
                os.path.join(CUR_DIR, '..', 'templates', "WEB_Project"),
                os.path.join(os.path.abspath(dirname), "WEB_Project"),
            )
        elif "api" == template.lower():
            copytree(
                os.path.join(CUR_DIR, '..' ,'templates', "API_Project"),
                os.path.join(os.path.abspath(dirname), "API_Project"),
            )
        elif "app" == template.lower():
            copytree(
                os.path.join(CUR_DIR, '..', 'example', "app"),
                os.path.join(os.path.abspath(dirname), "app"),
            )
        else:
            raise ValueError("您输入的数据有误，有效范围：web 或 api 或 app")
    elif monitor == "gui":
        gui()
    elif monitor == "cli":
        cli()
    elif monitor == "power":
        power()
    elif monitor == "memory":
        power()
    elif monitor == "cp":
        cpmain()
    elif device:
        MonitorDevice(device - 1)
    elif domains:
        flushDNS(domains)
