# 接口自动化项目


# 目录结构
```text
--------API_Project
| 
|----api_project
|   |
|   |
|   |----apis（接口封装）
|   |   |
|   |   |----Client.py
|   |
|   |----testcases（测试用例脚本）
|   |   |
|   |   |----test_*.py
|   |   |----test_*.py
|   |
|   |----case_data_files（测试用例数据）
|   |   |
|   |   |----*_CASE_DATA.csv
|   |
|   |----common（公共方法）
|   |   |
|   |   |----ENV.py
|   |   |----Email.py
|   |   |----CSV.py
|   |   |----BUG.py
|   |   |----Data.py
|   |   |----LOG.py
|   |   |----Message.py
|   |   |----Network.py
|   |
|   |----config（配置数据）
|   |   |
|   |   |----case_config.py（测试用例配置文件）
|   |   |----allure_config.py（allure配置文件）
|   |   |----bug_config.py（BUG单配置文件）
|   |   |----email_config.py（邮件配置文件）
|   |   |----host_config.py（主机域名配置文件）
|   |   |----log_config.py（日志配置文件）
|   |   |----message_config.py（消息配置文件）
|   |
|   |----bin 
|   |   |
|   |   |----allure
|   |       |----bin
|   |           |----allure.bat (allure可执行文件)
|   |           |----allure (allure可执行文件)
|   |
|   |----log（日志文件）
|   |   |
|   |   |----*.log
|   |
|   |----report（pytest测试报告）
|   |   |
|   |   |----（默认为空，执行前清空文件等内容）
|   |
|   |----allure_report（allure测试报告）
|   |   |
|   |   |----index.html
|   |   |----*
|   |
|
|----convert_ui.bat                     # curl转项目的脚本
|----convert_ui.sh                      # curl转项目的脚本
|----convert_ui.py                      # curl转项目的脚本
|----init_env.bat                       # 初始化环境脚本
|----init_env.sh                        # 初始化环境脚本
|----run_testcases.bat                  # 执行用例脚本
|----run_testcases.sh                   # 执行用例脚本
|----run_testcases.py                   # 执行用例脚本
```
----
# 环境准备
- 1、Python>=3.9.*
  - 1.1、安装xiaobaisaf库`pip install -U xiaobaisaf`
  - 1.2、需要使用xiaobaiauto2Api命令时安装xiaobaiauto2库`pip install xiaobaisaf[xiaobaiauto2]`  
- 2、JDK>=8 `xiaobaiauto2Api -i jdk -v 17 -d D:\\` （可选，若已安装JDK请忽略）
- 3、Allure（模板自带）
-----

# 使用步骤

## 1、导出模板
`xiaobaicmd -t api -d D:/`

## 2、进入模板目录
`cd API_Project`

## 3、初始化环境
`init_env.bat 或者 init_env.sh 或者 python init_env.py`

## 4、运行转换工具
`convert_ui.bat 或者 convert_ui.sh 或者 python convert_ui.py`

## 5、修改配置文件（具体位置如下）
```cmd
  Email(邮箱服务配置)
  API_Project>>api_project>>config>>email_config.py
  
  BUG(BUG单配置，支持禅道与JIRA)
  API_Project>>api_project>>config>>bug_config.py
  
  message(消息配置，支持飞书机器人、钉钉机器人、企业微信机器人)
  API_Project>>api_project>>config>>message_config.py
```

## 6、新增测试数据（可选）
路径：API_Project>>api_project>>case_data_files>>*

| url | method | headers |                     data                     |
| :---: | :---: | :---: |:--------------------------------------------:|
| /api/v1/login | POST | {'content-type':'application/json'} | {"username":"xiaobai", "password":"123456"}  |
| /api/v1/login | POST | {'content-type':'application/json'} | {"username":"xiaobai", "password":"1234567"} |
| /api/v1/login | POST | {'content-type':'application/json'} | {"username":"xiaobai", "password":""} |

## 7、修改测试用例（可选）
路径：API_Project>>api_project>>testcases>>*
```python
import requests
import pytest
import allure
from ..apis.Client import *
from ..common.CSV import Reader
from ..config.case_config import UPDATE_CASE_DATA_PATH

@allure.story("接口名称")
@pytest.mark.parametrize('url, method, headers, data', Reader(UPDATE_CASE_DATA_PATH, True))
def test_update(url, method, headers, data):
    """
    接口名称：UPDATE
    接口域名：http://test.xiaobai.com
    接口测试数据：{'url': '/api/v1/login', 'method': 'POST', 'headers': {'Content-Type': 'application/json'}, 'data': '{"username":"xiaobai", "password":"123456"}'}
    """
    allure.step('接口名称-请求')
    response = APIClient.session(url=url, method=method, headers=eval(headers), data=data)
    
    allure.step('接口名称-断言')
    assert response.status_code == 200    
    # json_assert(response, expression='jsonpath表达式', value=预期值)  # 依据接口文档修改
    
    # allure.step('接口名称-提取器')
    # json_extractor(response, env_name='变量名', expression='jsonpath表达式', index=0, default=默认值)
    # 调用格式：os.environ.get('变量名')
```
或者
```python
import os
import pytest
import allure
from ..apis.Client import *
from ..common.CSV import Reader
from ..config.case_config import 接口名称_CASE_DATA_PATH

@allure.story('接口名称')
# @at_json_extractor(env_name='存储的变量名', expression='jsonpath表达式', index=0, default='缺省值')
# @at_json_assert(expression='jsonpath表达式', index=0, value='预期值')
@at_http_status_code_assert(code=200)
@pytest.mark.parametrize(','.join(Reader(接口名称_CASE_DATA_PATH, False)[0]), Reader(接口名称_CASE_DATA_PATH, True))
def test_接口名称(method, uri, headers, data):
    \'\'\'
        接口名称：
        接口域名：
        接口测试数据：
    \'\'\'
    allure.step('接口名称-请求')
    response = APIClient.session(method=method, url=uri, headers=eval(headers), data=data)

    return response
```

## 8、执行用例
`run_testcases.bat 或者 run_testcases.sh 或者 python run_testcases.py`