#! /usr/bin/env python
'''
@Author: xiaobaiTser
@Time  : 2022/8/24 3:24
@File  : setup.py
'''

from setuptools import setup, find_packages
from saf.__version__ import __version__

f = open('README.md', 'r', encoding='utf-8')

setup(
    # 指定项目名称，我们在后期打包时，这就是打包的包名称，当然打包时的名称可能还会包含下面的版本号哟~
    name='xiaobaisaf',
    # 指定版本号
    version=__version__,
    # 这是对当前项目的一个描述
    description="simple_automation_framework(简称：SAF)" +\
                "使用最简单的模式就可以实现需要功能和测试效果，也是xiaobaiauto2的简化版" +\
                "SAF继承了selenium、requests/httpx、appium、loguru、xiaobaiauto2、飞书机器人、钉钉机器人、企业微信机器人（暂时不支持）、禅道提单API",
    long_description=f.read(),
    long_description_content_type="text/markdown",
    # 作者是谁，
    author='xiaobaiTser',
    # 作者的邮箱
    author_email='807447312@qq.com',
    # 写上项目的地址。
    url='https://gitee.com/xiaobaiOTS/simlpe_automation_framework',
    # 指定包名，即你需要打包的包名称，要实际在你本地存在哟，它会将指定包名下的所有"*.py"文件进行打包哟，但不会递归去拷贝所有的子包内容。
    # 综上所述，我们如果想要把一个包的所有"*.py"文件进行打包，应该在packages列表写下所有包的层级关系哟~这样就开源将指定包路径的所有".py"文件进行打包!
    keywords="saf automation xiaobai xiaobaiauto2 test framework",
    packages=find_packages(),
    include_package_data=True,
    # 指定Python的版本
    python_requires='>3.8',
    extras_require={
        'dev': [
            'pytest',
            'pytest-html',
            'pytest-xdist',
            'pytest-ordering',
            'pytest-assume',
            'allure-pytest',
            'allure-python-commons',
            'allure2-adaptor',
            'pytest-rerunfailures',
            'pytest-xdist',
        ],
        'doc': [
            'sphinx',
            'sphinx_rtd_theme',
            'recommonmark',
            'sphinx_markdown_tables',
            'sphinxcontrib-napoleon',
        ],
        'xiaobaiauto2': [
            'xiaobaiauto2',
        ],
        'web': [
            'pytest',
            'pytest-html',
            'pytest-xdist',
            'pytest-ordering',
            'pytest-assume',
            'allure-pytest',
            'allure-python-commons',
            'allure2-adaptor',
            'pytest-rerunfailures',
            'pytest-xdist',
            'xiaobaiauto2',
            'pypinyin',
            'bs4',
            'lxml',
        ],
        'app': [
            'pytest',
            'pytest-html',
            'pytest-xdist',
            'pytest-ordering',
            'pytest-assume',
            'allure-pytest',
            'allure-python-commons',
            'allure2-adaptor',
            'pytest-rerunfailures',
            'pytest-xdist',
            'adbutils',
            'xiaobaiauto2',
        ],
        'api': [
            'pytest',
            'pytest-html',
            'pytest-xdist',
            'pytest-ordering',
            'pytest-assume',
            'allure-pytest',
            'allure-python-commons',
            'allure2-adaptor',
            'pytest-rerunfailures',
            'pytest-xdist',
            'xiaobaiauto2',
            'prance',
        ],
        'all': [
            'pytest',
            'pytest-html',
            'pytest-xdist',
            'pytest-ordering',
            'pytest-assume',
            'allure-pytest',
            'allure-python-commons',
            'allure2-adaptor',
            'pytest-rerunfailures',
            'pytest-xdist',
            'adbutils',
            'loguru',
            'matplotlib',
            'msvc-runtime',
            'psutil',
            'pillow',
            'xiaobaiauto2',
            'pypinyin',
            'jmespath',
            'bs4',
            'lxml',
            'prance',
            'click',
            'python-opencv',
            'JIRA',
        ],
    },
    # install_requires=[
    #     'adbutils',
    #     'loguru',
    #     'bs4',
    #     'lxml',
    #     'matplotlib',
    #     'msvc-runtime',
    #     'psutil',
    #     'pillow',
    #     'pypinyin',
    #     'xiaobaiauto2',
    # ],
    entry_points={
        'console_scripts': [
            'xiaobaicmd = saf.utils.xiaobaicmd:main',
            'xiaobaimanager = saf.utils.SoftwareManager:main',
            'xiaobaifinder = saf.utils.finder:main',
            'xiaobaidevice = saf.utils.DeviceGUI:main',
            'xiaobaidevice2 = saf.utils.DeviceGUI2:main',
            'xiaobaipom = saf.utils.POMGenerator:main',
        ]
    },
    data_files=[
        ('favicon', ['saf/data/favicon.ico']),
        ('androidMonitor', ['saf/utils/androidMonitor-v1.1.exe']),
    ],
    # package_data={ 'saf': ['templates/*'] }
)

'''
#python setup.py sdist bdist_wheel
#python -m twine upload dist/*
'''