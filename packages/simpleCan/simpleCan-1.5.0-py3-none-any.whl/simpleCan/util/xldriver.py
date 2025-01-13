# -*- coding: UTF-8 -*-
'''
@File    :   xldriver.py
@Time    :   2025/01/06 15:30:00
@Author  :   Jiajie Liu
@Version :   1.0
@Contact :   ljj26god@163.com
@Desc    :   This file reads dll file from vector official website and utilize necessary functions for sending CAN messages.
'''

import ctypes, time
import logging
from simpleCan.util import dataStructure as ds
import os

util_path = os.path.dirname(os.path.abspath(__file__))
simpleCan_path = os.path.dirname(util_path)
dll_file_path = os.path.join(simpleCan_path, 'dll_file')
dll_path = os.path.join(dll_file_path,'vxlapi64.dll')
_xlapi_dll = ctypes.windll.LoadLibrary(dll_path)
libc = ctypes.CDLL("msvcrt.dll")

# initialize functions
xlOpenDriver = _xlapi_dll.xlOpenDriver

xlGetApplConfig = _xlapi_dll.xlGetApplConfig

xlGetChannelMask = _xlapi_dll.xlGetChannelMask

xlOpenPort = _xlapi_dll.xlOpenPort
xlActivateChannel = _xlapi_dll.xlActivateChannel

xlCanTransmit = _xlapi_dll.xlCanTransmit
xlCanTransmit.argtypes = [
    ds.XLportHandle,
    ds.XLaccessMark,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ds.XLevent),
]
xlCanTransmit.restype = ds.XLstatus

xlReceive = _xlapi_dll.xlReceive
xlReceive.argtypes = [
    ds.XLportHandle,
    ctypes.POINTER(ctypes.c_uint),
    ctypes.POINTER(ds.XLevent),
]

xlCanReceive = _xlapi_dll.xlCanReceive
xlCanReceive.argtypes = [
    ds.XLportHandle,
    ctypes.POINTER(ds.XLcanRxEvent),
]


xlGetErrorString = _xlapi_dll.xlGetErrorString

libc.memset.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
libc.memset.restype = ctypes.c_void_p

######################################################################################

appName = ctypes.create_string_buffer(b'CANalyzer')
pAppName = ctypes.pointer(appName)
appChannel = ctypes.c_uint()
HwType = ctypes.c_uint()
pHwType = ctypes.pointer(HwType)
HwIndex = ctypes.c_uint()
pHwIndex = ctypes.pointer(HwIndex)
HwChannel = ctypes.c_uint()
pHwChannel = ctypes.pointer(HwChannel)
busTypex = ctypes.c_uint()

portHandle = ds.XLportHandle()
pPortHandle = ctypes.pointer(portHandle)


userName = ds.userName
channelMask = ctypes.c_uint()
permissionMask = ctypes.c_uint64()
pPermissionMask = ctypes.pointer(permissionMask)
rx_queue_size = ds.rx_queue_size
xlInterfaceVersion = ds.xlInterfaceVersion
busType = ds.busType

XLeventTag_transmit = ds.XLeventTag_transmit
flags = ds.flags
activate_channel_flag = ds.activate_channel_flag
dlc = ds.dlc
def sendMessage(messageID, data):
    canID = ds.XL_CAN_EXT_MSG_ID | messageID
    myXLevent = (ds.XLevent * 10)()
    message_count = ctypes.c_uint(len(data))
    try:
        libc.memset(myXLevent, 0, ctypes.sizeof(myXLevent))
        for i in range(10):
            myXLevent[i].tag = XLeventTag_transmit
            myXLevent[i].tagData.msg.id = canID
            myXLevent[i].tagData.msg.flags = flags
            myXLevent[i].tagData.msg.data[0] = data[0]
            myXLevent[i].tagData.msg.data[1] = data[1]
            myXLevent[i].tagData.msg.data[2] = data[2]
            myXLevent[i].tagData.msg.data[3] = data[3]
            myXLevent[i].tagData.msg.data[4] = data[4]
            myXLevent[i].tagData.msg.data[5] = data[5]
            myXLevent[i].tagData.msg.data[6] = data[6]
            myXLevent[i].tagData.msg.data[7] = data[7]
            myXLevent[i].tagData.msg.dlc = dlc
        result = xlCanTransmit(portHandle, channelMask, message_count, myXLevent)
        if result == 0:
            logging.info('send message ' + str(hex(messageID)) + ' result ' + str(result))
        else:
            logging.error('send message ' + str(hex(messageID)) + ' result ' + str(result))
    except Exception as e:
        logging.error(f"Error: {e}")

def recvMessage(duration = 3):
    xLevent = ds.XLevent()
    pxLevent = ctypes.pointer(xLevent)
    eventCount = ctypes.c_uint(1)
    peventCount = ctypes.pointer(eventCount)
    xlReceive(portHandle, peventCount, pxLevent)
    print("receiving messages through CAN")
    print(xLevent.tag)

def setup():
    xlstatus = xlOpenDriver()
    logging.info('open driver result is ' + str(xlstatus))

    xlstatus = xlGetApplConfig(pAppName, appChannel, pHwType, pHwIndex, pHwChannel, busTypex)
    logging.info('get appl config result is ' + str(xlstatus))

    global channelMask
    channelMask = xlGetChannelMask(HwType, HwIndex, HwChannel)
    logging.info('channel mask is ' + str(channelMask))

    xlstatus = xlOpenPort(pPortHandle,
                          userName,
                          channelMask,
                          ctypes.pointer(permissionMask),
                          rx_queue_size,
                          xlInterfaceVersion,
                          busType)
    logging.info('open port result is ' + str(xlstatus))
    xlstatus = xlActivateChannel(portHandle,
                                 channelMask,
                                 busType,
                                 activate_channel_flag)
    logging.info('Activate channel result is ' + str(xlstatus))





