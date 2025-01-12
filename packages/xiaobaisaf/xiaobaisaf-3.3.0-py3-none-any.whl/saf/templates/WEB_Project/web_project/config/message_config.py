#! /usr/bin/env python
'''
Auther      : xiaobaiTser
Email       : 807447312@qq.com
createTime  : 2024/12/2 14:30
fileName    : message_config.py
'''
from typing import Union, Any

class MSG_Config(object):
    app_name            : str = ''
    _token_             : str = ''
    webhook             : str = ''
    # msg                 : str = ''
    msg_format          : dict = {}
    assert_jsonpath     : str = ''
    assert_value        : Union[Any] = None

class FeiShu_Config(MSG_Config):
    app_name            :str = '飞书'
    _token_             :str = ''
    webhook_help_document :str = 'https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN'
    webhook             :str = 'https://open.feishu.cn/open-apis/bot/v2/hook/' + _token_
    # msg                 :str = 'Hello,FeiShu!'
    msg_format          :dict= {"msg_type": "text", "content": {"text": '@所有人'}}
    assert_jsonpath     :str = "code"
    assert_value        :int = 0

class DingDing_Config(MSG_Config):
    app_name            :str = '钉钉'
    _token_             :str = ''
    webhook_help_document :str = 'https://open.dingtalk.com/document/group/custom-robot-access'
    webhook             :str = 'https://oapi.dingtalk.com/robot/send?access_token=' + _token_
    # msg                 :str = 'Hello,DingDing!'
    msg_format          :dict= {"msgtype": "text", "text": {"content": '@所有人'}}
    assert_jsonpath     :str = 'errcode'
    assert_value        :int = 0

class WeiXin_Config(MSG_Config):
    app_name            :str = "企业微信"
    _token_             :str = ''
    webhook_help_document :str = 'https://developer.work.weixin.qq.com/document/path/91770'
    webhook             :str = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=' + _token_
    # msg                 :str = 'Hello WeiXin!'
    msg_format          :dict= {"msgtype": "text", "text": {"content": '@所有人'}}
    assert_jsonpath     :str = 'errcode'
    assert_value        :int = 0
