# -*- coding: UTF-8 -*-
'''
@File    :   task.py
@Time    :   2025/01/06 15:30:00
@Author  :   Jiajie Liu
@Version :   1.0
@Contact :   ljj26god@163.com
@Desc    :   This file contains Task class that utilize thread for handling period and duration for messages.
'''

import threading
import time
from simpleCan.util import xldriver


# Whenever an instance of Task() is initialized, id, data, period and duration should be passed to it.
# A thread is created for each Task() instance
class SendMessageTask:
    def __init__(self, message_id = None, data = None, period = 0, duration = 0):
        self.message_id = message_id
        self.data = data
        self.period = period
        self.duration = duration
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self.thread = threading.Thread(target=self.sendMessage_task)

    def get_messageID(self):
        return self.message_id

    def get_messageData(self):
        return self.data

    def sendMessage_task(self): # append sendData task with parameter period and duration
        end_time = time.time() + self.duration
        while time.time() < end_time:
            xldriver.sendMessage(messageID=self.message_id, data=self.data)
            time.sleep(self.period)
            if self._stop_event.is_set():
                break
    def task_run(self):
        self.thread.start()

    def task_modifyData(self, newdata):
        with self._lock:
            self.data = newdata

    def task_stop(self):
        self._stop_event.set()
        self.thread.join()

class RecvMessageTask:
    def __init__(self, duration = 10):
        self.duration = duration
        self.thread = threading.Thread(target=self.recvMessage_task)

    def recvMessage_task(self): # append sendData task with parameter period and duration
        xldriver.recvMessage(self.duration)

    def task_run(self):
        self.thread.start()

    def task_stop(self):
        self.thread.join()






