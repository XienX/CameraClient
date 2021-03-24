# -*- coding: utf-8 -*-
# @Time : 2021/3/11 16:44
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : controlThread.py
# @notice ：

import json
import queue
import socket
import time
import traceback

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import *

from frameRecvThread import FrameRecvThread


# 继承QThread
class ControlThread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    frame_signal = pyqtSignal(np.ndarray)
    log_signal = pyqtSignal(str)
    enabled_signal = pyqtSignal(bool)

    def __init__(self, user_name, password, ip, port):
        super().__init__()
        self.user_name = user_name
        self.password = password
        self.ip = ip
        self.port = port

        self.connect = socket.socket()  # 创建 socket 对象
        # self.frameLen = 0
        self.isConnect = True

        self.frameRecvThread = None

        self.operationQueue = queue.Queue(5)

    def run(self):
        try:
            self.enabled_signal.emit(False)

            self.connect.connect((self.ip, self.port))

            message = {'code': 200, 'userName': self.user_name, 'password': self.password}  # 登录
            self.connect.send(json.dumps(message).encode())

            jsonMessage = self.connect.recv(1024).decode()
            message = json.loads(jsonMessage)
            print(message)

            if message['code'] == 300:
                self.log_signal.emit('登录成功')

                jsonMessage = self.connect.recv(1024).decode()
                message = json.loads(jsonMessage)
                print(message)

                if message['code'] == 321:
                    self.frameRecvThread = FrameRecvThread(self.ip, message['port'])
                    self.frameRecvThread.frame_signal.connect(self.show_frame)
                    self.frameRecvThread.start()

                    while 1:
                        operation = self.operationQueue.get()
                        self.logger.debug(operation)

                        self.connect.send(operation)

                elif message['code'] == 331:
                    self.log_signal.emit('无在线的摄像头设备，请上线摄像头后再登录')

                # jsonMessage = self.connect.recv(1024).decode()  # 帧数据大小
                # message = json.loads(jsonMessage)
                # print(message)
                #
                # if message['code'] == 500:
                #     self.frameLen = message['data']
                #     # time.sleep(0.1)
                #     while self.isConnect:
                #         frame = self.recv_frame()
                #         # print(frame)
                #         if type(frame) == np.ndarray:
                #             self.frame_signal.emit(frame)

                    # self.log_signal.emit('服务端断开了连接，可能所有的摄像头设备都已离线')

                # elif message['code'] == 331:
                    # self.log_signal.emit('无在线的摄像头设备，请上线摄像头后再登录')

            elif message['code'] == 301:
                self.log_signal.emit('用户名或密码错误')
            else:
                self.log_signal.emit(f'非预期的code {message["code"]}')

        except BaseException as e:
            traceback.print_exc()
            self.log_signal.emit('连接已断开')

        time.sleep(0.1)

        self.enabled_signal.emit(True)

    def queue_put(self):  # 放入操作指令
        pass

    def show_frame(self, frame):  # 显示视频帧
        self.frame_signal.emit(frame)


    def close(self):  # 结束

        if self.frameSendThread is not None and self.frameSendThread.isAlive:
            self.frameSendThread.close()

        self.isConnect = False
        # self.connect.shutdown(2)
        print('shutdown')
        self.connect.close()
