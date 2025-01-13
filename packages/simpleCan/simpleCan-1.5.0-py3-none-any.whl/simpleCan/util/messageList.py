# -*- coding: UTF-8 -*-
'''
@File    :   messageList.py
@Time    :   2025/01/06 15:30:00
@Author  :   Jiajie Liu
@Version :   1.0
@Contact :   ljj26god@163.com
@Desc    :   This file contains reads a excel file to set up CAN message environment. It also creates a list of tasks to manage all the tasks.
'''

from simpleCan.util import dataStructure as ds

class MessageList:

    def __init__(self):
        self.messageList = []
    def load_default_messageList(self):
        defaultMessageList = DefaultMessageList()
        for i in range(len(defaultMessageList.messageList)):
            self.messageList.append(defaultMessageList.messageList[i])

    def clearMessageList(self):
        self.messageList = []
    def get_messageList(self):
        return self.messageList

    def printMessageList(self):
        for i in range(len(self.messageList)):
            print(self.messageList[i].id)
            print(self.messageList[i].data)
            print(self.messageList[i].period)

class DefaultMessageList():
    def __init__(self):
        self.messageList = []
        self.messageList.append(ds.CanMessage(id=0X18FEAE30, data=[0X0,0XCB,0X5E,0X5B,0X0,0X0,0X0,0X0], period=1))
        self.messageList.append(ds.CanMessage(id=0X10FF8E11, data=[0x0,0x0,0x0,0x28,0x0,0x0,0xC0,0xf], period=0.1))
        self.messageList.append(ds.CanMessage(id=0X10ff8f11, data=[0x0,0x0,0x80,0x0,0xC0,0x0,0x0,0x0], period=0.1))
        self.messageList.append(ds.CanMessage(id=0X18ff6a47, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18ffb11e, data=[0x0,0x0,0x0,0x0,0x10,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18feca30, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18FECA00, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18FECA2F, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18feca27, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18FECA03, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18FECA33, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18F0010B, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=1))
        self.messageList.append(ds.CanMessage(id=0X18F0010B, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=0.1))
        self.messageList.append(ds.CanMessage(id=0X19FF4150, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=0.02))
        self.messageList.append(ds.CanMessage(id=0XCFF6F5A, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], period=0.02))










