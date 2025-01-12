# WEB自动化项目


# 目录结构
```text
--------API_Project
| 
|----api_project
|   |
|   |
|   |----pageObjects（页面对象封装）
|   |   |
|   |   |----__init__.py
|   |
|   |----testcases（测试用例脚本）
|   |   |
|   |   |----test_*.py
|   |   |----test_*.py
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

# 使用说明
## 1、导出Web模板
`xiaobaicmd -t web -d D:/`

## 2、进入模板目录
`cd Web_Project`

## 3、初始化环境
`init_env.bat 或者 init_env.sh 或者 python init_env.py`

## 4、运行POM工具（将网页自动生成PO模型代码）
`pomGenerator.bat`
或者
`xiaobaipom --help`

## 5、修改配置文件（具体位置如下）
```cmd
  Email(邮箱服务配置)
  WEB_Project>>web_project>>config>>email_config.py
  
  BUG(BUG单配置，支持禅道与JIRA)
  WEB_Project>>web_project>>config>>bug_config.py
  
  message(消息配置，支持飞书机器人、钉钉机器人、企业微信机器人)
  WEB_Project>>web_project>>config>>message_config.py
```

## 6、修改测试用例（可选）
路径：WEB_Project>>web_project>>testcases>>*
```python
import pytest
import allure
from web_project.pageObjects.PAGE1 import page1_class   # 导入页面类，此行代码需要修改

@allure.feature("功能名称")
class TestCase:
    
    ...  # 省略其他代码
    
    @allure.story("用例名称")
    def test_case(self, driver):
        # 实例化页面
        p1 = page1_class(driver)
        # 打开p1页面
        driver.get(p1.page_url)
        # 操作p1页面的元素
        p1.send_username("admin")
        p1.send_password("123456")
        p1.click_login()
        # 断言
        assert driver.title == "xxxxx"
```

## 7、执行用例
`run_testcases.bat 或者 run_testcases.sh 或者 python run_testcases.py`
