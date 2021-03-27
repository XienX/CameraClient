# -*- coding: utf-8 -*-
# @Time : 2021/3/24 14:54
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : frameRecvThread.py
# @notice ：
import json
import socket
import traceback

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import *


class FrameRecvThread(QtCore.QThread):
    frame_signal = pyqtSignal(np.ndarray)

    def __init__(self, ip, port):
        super().__init__()

        self.ip = ip
        self.port = port

        self.connect = socket.socket()
        self.isConnect = True

        self.frameLen = 921600  # 默认640*480

    def run(self):
        try:
            self.connect.connect((self.ip, self.port))

            while self.isConnect:
                frame = self.recv_frame()
                if frame is not None:
                    self.frame_signal.emit(frame)

        except BaseException as e:
            traceback.print_exc()

        print('FrameRecvThread close')

    def recv_frame(self):  # 根据数据长度接受一帧数据，返回 numpy.ndarray
        receivedSize = 0
        bytesMessage = b''

        while receivedSize < self.frameLen:
            res = self.connect.recv(8192)
            if not res:  # 远端shutdown或close后，不断获取到空的结果
                self.isConnect = False
                # print(len(res))
                break
            receivedSize += len(res)  # 每次收到的服务端的数据有可能小于8192，所以必须用len判断
            bytesMessage += res

        # print(receivedSize)
        try:
            if receivedSize == self.frameLen:
                return np.frombuffer(bytesMessage, dtype=np.uint8).reshape(480, 640, 3)
        except BaseException as e:
            print(traceback.print_exc())
        return None

    def close(self):  # 关闭此线程
        self.isConnect = False
        self.connect.close()
        print('FrameRecvThread.close(self)')
