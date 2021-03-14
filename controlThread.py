# -*- coding: utf-8 -*-
# @Time : 2021/3/11 16:44
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : controlThread.py
# @notice ：

import json
import socket

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import *


# 继承QThread
class ControlThread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    frame_signal = pyqtSignal(np.ndarray)
    log_signal = pyqtSignal(str)
    connect_button_signal = pyqtSignal(bool)
    close_button_signal = pyqtSignal(bool)

    def __init__(self, user_name, password, ip, port):
        super().__init__()
        self.user_name = user_name
        self.password = password
        self.ip = ip
        self.port = port

        self.connect = socket.socket()  # 创建 socket 对象
        self.frameLen = 0

        self.isConnect = True

    def run(self):
        try:
            self.connect_button_signal.emit(False)
            self.close_button_signal.emit(True)
            self.connect.connect((self.ip, self.port))

            message = {'code': 200, 'userName': self.user_name, 'password': self.password}  # 登录
            self.connect.send(json.dumps(message).encode())

            jsonMessage = self.connect.recv(1024).decode()
            message = json.loads(jsonMessage)
            print(message)

            if message['code'] == 300:
                self.log_signal.emit('登录成功')

                jsonMessage = self.connect.recv(1024).decode()  # 帧数据大小
                message = json.loads(jsonMessage)
                print(message)

                if message['code'] == 500:
                    self.frameLen = message['data']
                    # time.sleep(0.1)
                    while self.isConnect:
                        frame = self.recv_frame()
                        # print(frame)
                        if type(frame) == np.ndarray:
                            self.frame_signal.emit(frame)

                    self.log_signal.emit('服务端断开了连接，可能所有的摄像头设备都已离线')

                elif message['code'] == 320:
                    self.log_signal.emit('无在线的摄像头设备，请上线摄像头后再登录')

            elif message['code'] == 301:
                self.log_signal.emit('用户名或密码错误')
            else:
                self.log_signal.emit(f'非预期的code {message["code"]}')

        except BaseException as e:
            self.log_signal.emit(f'连接错误: {e}')

        self.connect_button_signal.emit(True)
        self.close_button_signal.emit(False)

    def recv_frame(self):  # 根据数据长度接受一帧数据，返回 numpy.ndarray
        receivedSize = 0
        bytesMessage = b''

        while receivedSize < self.frameLen:
            res = self.connect.recv(8192)
            if len(res) == 0:  # 远端shutdown或close后，不断获取到空的结果
                self.isConnect = False
                print(len(res))
                break
            receivedSize += len(res)  # 每次收到的服务端的数据有可能小于8192，所以必须用len判断
            bytesMessage += res

        # print(receivedSize)
        if receivedSize == self.frameLen:
            return np.frombuffer(bytesMessage, dtype=np.uint8).reshape(480, 640, 3)
        return None

    def close(self):  # 结束
        self.isConnect = False
        # self.connect.shutdown(2)
        print('shutdown')
        self.connect.close()
