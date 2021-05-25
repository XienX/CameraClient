# -*- coding: utf-8 -*-
# @Time : 2021/3/24 14:54
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : frameRecvThread.py
# @notice ：FrameRecvThread类--帧接受线程

import socket
import time
import traceback
from io import BytesIO

from PIL import Image
from PyQt5 import QtCore
from PyQt5.QtCore import *


class FrameRecvThread(QtCore.QThread):
    frame_signal = pyqtSignal(Image.Image)

    def __init__(self, ip, port):
        super().__init__()

        self.ip = ip
        self.port = port

        self.connect = socket.socket()
        self.isConnect = True

    def run(self):
        try:
            self.connect.connect((self.ip, self.port))

            while self.isConnect:
                frame = self.recv_frame()
                # print(type(frame))  # <class 'PIL.JpegImagePlugin.JpegImageFile'>
                if frame is not None:
                    self.frame_signal.emit(frame)
                time.sleep(0.02)

        except BaseException as e:
            # traceback.print_exc()
            print(e)

        # print('FrameRecvThread close')

    def recv_frame(self):  # 根据数据长度接受一帧数据，返回 numpy.ndarray
        try:
            receivedSize = 0
            bytesMessage = b''

            # frameLenBytesMessage = self.connect.recv(1024).decode()
            # message = json.loads(frameLenBytesMessage)
            # time.sleep(0.01)

            frameLen = int.from_bytes(self.connect.recv(4), byteorder='big')
            # print(f'frameLen {frameLen}')
            if frameLen == 0:
                self.isConnect = False
                return None

            # if message['code'] == 500:
            #     frameLen = message['frameLen']

            # while receivedSize < frameLen:
            #     res = self.connect.recv(8192)
            #     if not res:  # 远端shutdown或close后，不断获取到空的结果
            #         self.isConnect = False
            #         break
            #     receivedSize += len(res)  # 每次收到的服务端的数据有可能小于8192，所以必须用len判断
            #     bytesMessage += res

            while receivedSize < frameLen:  # 循环接收数据
                res = self.connect.recv(frameLen - receivedSize)
                if not res:  # 远端shutdown或close后，不断获取到空的结果
                    self.isConnect = False
                    break
                receivedSize += len(res)
                bytesMessage += res

            # bytesMessage += self.connect.recv(frameLen - len(bytesMessage))
            # print(len(bytesMessage))

            if receivedSize == frameLen:
                return Image.open(BytesIO(bytesMessage))
        except BaseException:
            # traceback.print_exc()
            print(e)

        return None

    def close(self):  # 关闭此线程
        self.isConnect = False
        self.connect.close()
        # print('FrameRecvThread.close(self)')
