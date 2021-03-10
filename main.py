# -*- coding: utf-8 -*-
# @Time : 2021/3/9 23:03
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : main.py
# @notice ：

import socket
import json

import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow

from clientWindow import Ui_MainWindow


class ControllerWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.connect = socket.socket()  # 创建 socket 对象

        self.slot_init()

    def slot_init(self):
        self.connectButton.clicked.connect(self.connect_server)
        self.timer_camera.timeout.connect(self.show_camera)

    def connect_server(self):  # 连接服务器
        self.connect = socket.socket()  # 创建 socket 对象
        ip = self.ipInput.text()
        port = int(self.portInput.text())
        self.connect.connect((ip, port))

        message = {'code': 200}  # len = 13
        self.connect.send(json.dumps(message).encode())

        message = self.connect.recv(1024).decode()
        LoginCode = json.loads(message)['code']
        print(LoginCode)

        self.send_frame()

    def recv_frame(self):  # 接收一帧数据
        pass


    def show_camera(self):  # 显示一帧
        flag, frame = self.camera.cap.read()  # 640*480
        show = cv2.resize(frame, (400, 300))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.cameraLabel.setPixmap(QPixmap.fromImage(showImage))

if __name__ == '__main__':
    pass
