# -*- coding: UTF-8 -*-
'''
@File    :   simpleCan.py
@Time    :   2025/01/06 15:30:00
@Author  :   Jiajie Liu
@Version :   1.0
@Contact :   ljj26god@163.com
@Desc    :   This file is the main class of simpleCan package. It provides all the necessary interfaces for users to use.
'''
import logging
from typing import Optional
from simpleCan.util import xldriver
from simpleCan.util.task  import SendMessageTask, RecvMessageTask
from simpleCan.util.messageList import MessageList

# logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s', level=logging.CRITICAL)

class SimpleCan:

    def __init__(self):
        # create a list to store all messages sending to DDU
        self.tasklist = []
        self.messageList = MessageList()
        xldriver.setup()


    # from messagelist, read all the messages and convert them into tasks.
    # then append to taskList
    def env_setup(self,duration = 360):
        self.messageList.clearMessageList()
        self.messageList.load_default_messageList()
        messageList = self.messageList.get_messageList()
        self.clearTaskList()
        for i in range(len(messageList)):
            self.tasklist.append(SendMessageTask(message_id=messageList[i].id,
                                                 data=messageList[i].data,
                                                 period=messageList[i].period,
                                                 duration=duration))
    def env_run(self):
        for task in self.tasklist:
            task.task_run()

    # this function simply creates a task that sends message through Can channel
    # each task contains four attributes:
    # message_id -- id of the message you want to send
    # data  -- data of the message you want to send. Example: [0,0,0,0,0,0,0,0]
    # period -- frequency of the message you want to send. Unit in seconds.
    # duration -- If you need explanation for this, then your intelligence level is not suitable for using this package.

    # Create a task, which contains the message to be sent, and append to task list
    def sendMessage(self, message_id, data, period, duration = 30):
        task = SendMessageTask(message_id=message_id,
                               data = data,
                               period = period,
                               duration = duration)
        self.tasklist.append(task)
        task.task_run()

    def recvMessage(self, duration:Optional[int]):
        task = RecvMessageTask(duration)
        task.task_run()

    def modifyMessage(self, message_id, data):
        try:
            for task in self.tasklist:
                if task.get_messageID() == message_id:
                    task.task_modifyData(newData = data)
        except Exception as e:
            logging.error(e)

    def stopMessage(self, message_id):
        try:
            for task in self.tasklist:
                if task.get_messageID() == message_id:
                    task.task_stop()
        except Exception as e:
            logging.error(e)

    def clearTaskList(self):
        self.tasklist = []
    def endAllTasks(self):
        for task in self.tasklist:
            task.task_stop()

    def __del__(self):
        self.endAllTasks()






