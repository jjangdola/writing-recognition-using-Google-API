import sys
import cv2
import io

from google.cloud import vision_v1p3beta1 as vision
from PyQt5.QtWidgets import *
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QSize, QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import *


form_class = uic.loadUiType("./dpi_ui_5.ui")[0]


class MyWindow(QtWidgets.QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()

        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, 1280)
        self.camera.set(4, 720)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.cameraBtn.clicked.connect(self.captureImage)
        self.ocrBtn.clicked.connect(self.performOCR)
        self.onoffBtn.clicked.connect(self.onClicked)
        self.returnBtn.clicked.connect(self.returnToCamera)

        self.image_path = ""

        self.ocrBtn.setEnabled(False)  # OCR 버튼 비활성화

    def initUI(self):
        self.setWindowTitle("Dpi")
        # pushbutton
        self.fileBtn.clicked.connect(self.fileopen)
        self.onoffBtn.setText('OFF')

    def returnToCamera(self):
        self.imgLabel.clear()
        self.image_path = ""
        self.startCamera()


    def fileopen(self):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, ' Open File','',
                                                         'Image file(*.png *jpg)')
        if filename[0]:
            # QPixmap 객체
            pixmap = QPixmap(filename[0])
            slmage = pixmap.scaled(QSize(550,500), Qt.KeepAspectRatio)
            self.imgLabel.setPixmap(slmage)  # 이미지 세팅
            self.image_path = filename[0]

        else:
            QMessageBox.about(self, 'Warning', '파일을 선택하지 않았습니다.')

    def onClicked(self):
        if self.onoffBtn.text() == 'OFF':
            self.startCamera()
            self.onoffBtn.setText('ON')
        else:
            self.stopCamera()
            self.onoffBtn.setText('OFF')  
            self.imgLabel.clear()
   
    def stopCamera(self):
     self.timer.stop()
     self.camera.release()
     if self.image_path:
        self.imgLabel.clear()
     self.image_path = ""


    def startCamera(self):
        self.camera = cv2.VideoCapture(0)
        self.camera.set(3, 640)  # 너비
        self.camera.set(4, 480)  # 높이
        self.timer.start(33)  # 30fps (1000ms / 30)

    def updateFrame(self):
        if self.image_path:
            # 촬영한 사진이 있는 경우
            pixmap = QPixmap(self.image_path)
            slmage = pixmap.scaled(QSize(1280, 720), Qt.KeepAspectRatio)
            self.imgLabel.setPixmap(slmage)
        else:
            # 웹캠 화면을 표시
            ret, frame = self.camera.read()
            if ret: 
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, c = frame.shape
                qImg = QImage(frame.data, w, h, w * c, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qImg)
                slmage = pixmap.scaled(QSize(1280, 720), Qt.KeepAspectRatio)
                self.imgLabel.setPixmap(slmage)

    def closeEvent(self, event):
        self.camera.release()

    def captureImage(self):
     if self.onoffBtn.text() == 'OFF':
        QMessageBox.about(self, 'Warning', '카메라가 꺼져있습니다.')
     else:
        ret, frame = self.camera.read()
        if ret:
            cv2.imwrite("captured_image.jpg", frame)
            self.image_path = "captured_image.jpg"
            # 화면에 이미지 표시
            pixmap = QPixmap(self.image_path)
            slmage = pixmap.scaled(QSize(1280, 720), Qt.KeepAspectRatio)
            self.imgLabel.setPixmap(slmage)
            self.ocrBtn.setEnabled(True)  # OCR 버튼 활성화

    def performOCR(self):
        if self.image_path:
            # 이미지를 바이너리로 인코딩
            image = cv2.imread(self.image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            _, content = cv2.imencode('.jpg', image)
            content = content.tobytes()

            # Vision API에 이미지 바이너리 전송
            client = vision.ImageAnnotatorClient()
            image = vision.Image(content=content)

            # OCR 수행
            response = client.text_detection(image=image)
            texts = response.text_annotations

            # 결과 출력
            if texts:
                result = texts[0].description
                self.textBrowser.setText(result)
            else:
                self.textBrowser.setText("OCR 결과를 찾을 수 없습니다.")
        else:
            self.textBrowser.setText("이미지를 선택해주세요.")

        # OCR 완료 후 버튼 상태 변경
        self.ocrBtn.setEnabled(False)  # OCR 버튼 비활성화
        self.cameraBtn.setEnabled(True)  # 카메라 버튼 활성화

    def cameraBtnClicked(self):
        self.captureImage()
    

    def ocrBtnClicked(self):
        self.performOCR()
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
