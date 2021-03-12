# -*- coding: utf-8 -*-
# @Time : 2021/3/9 23:03
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : main.py
# @notice ：

import sys

import cv2
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication

from clientWindow import Ui_MainWindow
from socketFrameThread import SocketFrameThread


class ClientMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.slot_init()

    def slot_init(self):
        self.connectButton.clicked.connect(self.connect_server)

    def connect_server(self):  # 连接服务器
        # frameThread = Thread(target=self.socket_frame_thread)
        # frameThread.setDaemon(True)
        # frameThread.start()

        ip = self.ipInput.text()
        port = int(self.portInput.text())
        self.frameThread = SocketFrameThread(ip, port)
        self.frameThread._signal.connect(self.show_camera)  # 连接信号
        self.frameThread.start()

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
