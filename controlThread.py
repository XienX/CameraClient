# -*- coding: utf-8 -*-
# @Time : 2021/3/11 16:44
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : controlThread.py
# @notice ：ControlThread类--连接控制线程

import json
import queue
import socket
import time
import traceback

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import *

from frameRecvThread import FrameRecvThread


# 继承QThread
class ControlThread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    frame_signal = pyqtSignal(Image.Image)
    log_signal = pyqtSignal(str)
    enabled_signal = pyqtSignal(bool)
    camera_list_signal = pyqtSignal(int)

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

            # 连接
            self.connect.connect((self.ip, self.port))

            # 登录
            message = {'code': 200, 'userName': self.user_name, 'password': self.password}  # 登录
            self.connect.send(json.dumps(message).encode())

            # 接收登录回复消息
            jsonMessage = self.connect.recv(64).decode()
            message = json.loads(jsonMessage)
            print(message)

            if message['code'] == 300:
                self.log_signal.emit('登录成功')

                # 接收摄像头列表消息
                jsonMessage = self.connect.recv(1024).decode()
                message = json.loads(jsonMessage)
                print(message)

                if message['code'] == 321:  # 摄像头列表
                    if message['num'] > 0:
                        self.camera_list_signal.emit(message['num'])

                        # 接收摄像头列表
                        # jsonMessage = self.connect.recv(1024).decode()
                        # message = json.loads(jsonMessage)
                        # print(str(message) + 'controlThread 72')

                        # message = {'code': 220, 'camera': 0}  # 请求视频流
                        # self.connect.send(json.dumps(message).encode())

                        # 接受视频流连接请求
                        jsonMessage = self.connect.recv(1024).decode()
                        message = json.loads(jsonMessage)
                        print(message)

                        # 创建视频接收线程
                        self.frameRecvThread = FrameRecvThread(self.ip, message['port'])
                        self.frameRecvThread.frame_signal.connect(self.show_frame)
                        self.frameRecvThread.start()

                        while self.isConnect:
                            operation = self.operationQueue.get()
                            print(operation)

                            if operation['code'] == 250:  # 断开连接
                                self.close()
                                break
                            elif operation['code'] == 220:  # 切换摄像头信号
                                self.connect.send(json.dumps(operation).encode())
                                jsonMessage = self.connect.recv(1024).decode()
                                message = json.loads(jsonMessage)
                                print(str(message) + 'controlThread 101')

                                if message['code'] == 321:  # 摄像头切换成功
                                    self.log_signal.emit('已切换摄像头画面')
                                    self.camera_list_signal.emit(message['num'])
                                else:
                                    self.log_signal.emit('此设备已掉线')
                                    print(str(message) + 'controlThread 93')
                                    break

                                # else:
                                #     self.connect.send(json.dumps(operation).encode())
                    else:
                        self.log_signal.emit('无在线的摄像头设备，请上线摄像头后再登录')

                else:
                    self.log_signal.emit(f'非预期的code {message["code"]}')

            elif message['code'] == 301:
                self.log_signal.emit('用户名或密码错误')
            else:
                self.log_signal.emit(f'非预期的code {message["code"]}')

        except BaseException as e:
            traceback.print_exc()

        self.log_signal.emit('连接已断开')
        time.sleep(0.1)
        self.enabled_signal.emit(True)

    # def queue_put(self):  # 放入操作指令
    #     pass

    def show_frame(self, frame):  # 显示视频帧
        self.frame_signal.emit(frame)

    def close(self):  # 结束
        if self.frameRecvThread is not None and self.frameRecvThread.isRunning():
            self.frameRecvThread.close()

        self.isConnect = False
        self.connect.close()

        print('shutdown')
