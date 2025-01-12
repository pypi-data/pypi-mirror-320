#! /usr/bin/env python
'''
Auther      : xiaobaiTser
Email       : 807447312@qq.com
createTime  : 2024/12/2 14:25
fileName    : Message.py
'''
from requests import post
from jsonpath import jsonpath
from ..common.LOG import Logger
from ..config.message_config import *

class MessageManager(MSG_Config):
    logger = Logger()
    def __init__(self):
        self.client = post

    def sendMsg(self, msg: str = ''):
        """
        发送消息函数
        :param msg:             WebHook发送的信息
        :return:
        """
        if not msg:
            self.logger.error("msg信息不能为空，必填内容！")
            raise ValueError("msg信息不能为空，必填内容！")
        else:
            self.msg_format['text']['content'] = msg + '\n@所有人 '
            try:
                response = self.client(
                    url=self.webhook,
                    headers={"Content-Type": "application/json"},
                    json=self.msg_format,
                )

                if self.assert_jsonpath and self.assert_value:
                    try:
                        assert self.assert_value == jsonpath(self.assert_jsonpath, response.json())
                        self.logger.info(f'{self.app_name}发送消息已成功')
                    except AssertionError as e:
                        self.logger.error(f'{self.app_name}的消息发送失败：{e}')
            except Exception as e:
                self.logger.error(f'{self.app_name}的消息发送失败：{e}')

class DingDingService(DingDing_Config, MessageManager):
    def sendRobot(self, msg):
        self.sendMsg(msg)

class FeiShuService(FeiShu_Config, MessageManager):
    def sendRobot(self, msg):
        self.sendMsg(msg)

class WeiXinService(WeiXin_Config, MessageManager):
    def sendRobot(self, msg):
        self.sendMsg(msg)