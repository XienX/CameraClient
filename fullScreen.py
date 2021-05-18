# -*- coding: utf-8 -*-
# @Time : 2021/5/18 17:08
# @Author : XieXin
# @Email : 1324548879@qq.com
# @File : fullScreen.py
# @notice ：全屏视频画面页面


from PyQt5.QtWidgets import QMainWindow
from fullScreenDialog import Ui_Dialog


class fullScreenUI(QMainWindow, Ui_Dialog):
    def __init__(self, ):
        super().__init__()
        self.setupUi(self)

    def showImage(self):  # 显示图片
        pass
