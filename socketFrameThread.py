import json
import socket

import numpy
import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import *


# 继承QThread
class SocketFrameThread(QtCore.QThread):
    #  通过类成员对象定义信号对象
    _signal = pyqtSignal(numpy.ndarray)

    def __init__(self, ip, port):
        super().__init__()
        self.ip = ip
        self.port = port

        self.connect = socket.socket()  # 创建 socket 对象
        self.frameLen = 0

    def __del__(self):
        self.wait()

    def run(self):
        self.connect.connect((self.ip, self.port))

        message = {'code': 200}  # 登录
        self.connect.send(json.dumps(message).encode())

        message = self.connect.recv(1024).decode()
        LoginCode = json.loads(message)['code']
        print(LoginCode)

        bytesMessage = self.connect.recv(1024)
        message = json.loads(bytesMessage.decode())

        if message['code'] == 500:  # 数据长度通知
            try:
                self.frameLen = message['data']
                # time.sleep(0.1)
                while 1:
                    frame = self.recv_frame()
                    # print(frame)
                    if type(frame) == numpy.ndarray:
                        self._signal.emit(frame)  # 注意这里与_signal = pyqtSignal(str)中的类型相同
            except BaseException as e:
                print(e)

    def recv_frame(self):  # 根据数据长度接受一帧数据，返回 numpy.ndarray
        receivedSize = 0
        bytesMessage = b''

        while receivedSize < self.frameLen:
            res = self.connect.recv(8192)
            receivedSize += len(res)
            bytesMessage += res

        # message = json.loads(bytesMessage.decode())
        # if message['code'] == 350:
        #     # return np.asarray(message['data'], dtype='uint8')
        #     return np.frombuffer(message['data'], dtype=np.uint8)
        # else:
        #     return -1

        # print(receivedSize)
        if receivedSize == self.frameLen:
            return np.frombuffer(bytesMessage, dtype=np.uint8).reshape(480, 640, 3)
        return None
