# -*- coding: utf-8 -*-
# @Time : 2021/3/9 23:03
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : main.py
# @notice ：

import socket
import sys
import json
import numpy as np

import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication

from clientWindow import Ui_MainWindow


class ClientMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.slot_init()

    def slot_init(self):
        self.connectButton.clicked.connect(self.connect_server)

    def connect_server(self):  # 连接服务器
        self.connect = socket.socket()  # 创建 socket 对象
        ip = self.ipInput.text()
        port = int(self.portInput.text())
        self.connect.connect((ip, port))

        message = {'code': 200}  # 登录
        self.connect.send(json.dumps(message).encode())

        message = self.connect.recv(1024).decode()
        LoginCode = json.loads(message)['code']
        print(LoginCode)

        bytesMessage = self.connect.recv(1024)
        message = json.loads(bytesMessage.decode())

        if message['code'] == 500:  # 数据长度通知
            try:
                frame = self.recv_frame(message['data'])
                self.show_camera(frame)
            except BaseException as e:
                print(e)

    def recv_frame(self, size):  # 根据数据长度接受一帧数据，返回 numpy.ndarray
        receivedSize = 0
        bytesMessage = b''
        print(size)

        while receivedSize < size:
            res = self.connect.recv(8192)
            receivedSize += len(res)
            bytesMessage += res

        # message = json.loads(bytesMessage.decode())
        # if message['code'] == 350:
        #     # return np.asarray(message['data'], dtype='uint8')
        #     return np.frombuffer(message['data'], dtype=np.uint8)
        # else:
        #     return -1
        return np.frombuffer(bytesMessage, dtype=np.uint8).reshape(480, 640, 3)

    def show_camera(self, frame):  # 显示一帧
        # print(frame)
        show = cv2.resize(frame, (400, 300))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.cameraLabel.setPixmap(QPixmap.fromImage(showImage))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = ClientMainWindow()
    ui.show()
    sys.exit(app.exec_())
