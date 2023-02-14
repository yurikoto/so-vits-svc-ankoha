import json
import platform
import subprocess

from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import os
import threading
import inference_main

class BaseThread(threading.Thread):
    def __init__(self, callback=None, callback_args=None, *args, **kwargs):
        target = kwargs.pop('target')
        super(BaseThread, self).__init__(target=self.target_with_callback, *args, **kwargs)
        self.callback = callback
        self.method = target
        self.callback_args = callback_args

    def target_with_callback(self):
        self.method()
        if self.callback is not None:
            self.callback(*self.callback_args)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setFixedWidth(1015)
        self.setFixedHeight(466)
        # self.setWindowIcon(QIcon('favicon.ico'))
        self.isInitiating = True
        dir = os.getcwd()
        loadUi(dir + "/xml/MainWindow.ui", self)

        modelDirList = os.listdir(dir + "/model")
        hubertDirList = os.listdir(dir + "/hubert")
        if "model.pth" not in modelDirList or "config.json" not in modelDirList or "hubert-soft-0d54a1f4.pt" not in hubertDirList:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("模型文件缺失")
            msg.setText("请下载补充模型文件包并解压覆盖到本软件目录中")
            msg.buttonClicked.connect(lambda i: exit(1))
            msg.exec_()

        self.soundInput = ""
        self.soundOutput = ""
        self.wavFormat = "wav"

        with open(dir + '/model/config.json', 'r') as f:
            config = json.load(f)

        for spk in config['spk'].keys():
            self.comboBoxSound.addItem(spk)

        # formats = ["wav", "aiff", "flac", "ogg"]
        # for format in formats:
        #     self.comboBoxWavFormat.addItem(format)

        self.pushButtonSoundInput.clicked.connect(self.getSoundInput)
        self.pushButtonSoundOutput.clicked.connect(self.getSoundOutput)
        self.pushButtonStartInference.clicked.connect(self.startInference)

        self.isInitiating = False

        # self.statusBar().showMessage("就绪。")

    def getSoundInput(self):
        file_filter = 'WAV File (*.wav);'
        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='请选择输入音频',
            directory=os.getcwd(),
            filter=file_filter,
            initialFilter='WAV File (*.wav)'
        )
        if response[0]:
            self.lineEditInputPath.setText(response[0])
            self.soundInput = response[0]

    def getSoundOutput(self):
        file_filter = 'WAV File (*.wav);; AIFF File (*.aiff);; OGG File (*.ogg);; FLAC File(*.flac);'
        response = QFileDialog.getSaveFileName(
            parent=self,
            caption='请指定保存位置',
            directory= os.getcwd() + '/results/result.wav',
            filter=file_filter,
            initialFilter='WAV File (*.wav)'
        )
        if response[0]:
            self.lineEditOutputPath.setText(response[0])
            self.soundOutput = response[0]
            self.wavFormat = response[0].split(".")[-1]

    def startInference(self):
        self.transInt = self.spinBoxTransInt.value()
        self.speaker = self.comboBoxSound.currentText()
        self.sliceDb = self.spinBoxSliceDb.value()

        if not self.soundInput or not self.soundOutput:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("未指定输入或输出文件")
            msg.setText("请指定输入和输出文件")
            msg.exec_()
            return

        print(self.soundInput, self.transInt, self.speaker, self.sliceDb, self.soundOutput, self.wavFormat)

        self.pushButtonStartInference.setEnabled(False)

        def callback():
            self.pushButtonStartInference.setEnabled(True),
            if platform.system() == 'Darwin':  # macOS
                subprocess.call(('open', self.soundOutput))
            elif platform.system() == 'Windows':  # Windows
                os.startfile(self.soundOutput)
            else:  # linux variants
                subprocess.call(('xdg-open', self.soundOutput))

        thread = BaseThread(
            name='inference',
            target=lambda: inference_main.Infer(self, self.soundInput, self.transInt, self.speaker, self.sliceDb, self.wavFormat, self.soundOutput),
            callback=callback,
            # callback=self.btnTrainModel.setEnabled,
            callback_args=(),
            # callback_args=tuple([True])
        )
        thread.setDaemon(True)
        thread.start()

        #inference_main.Infer(self, self.soundInput, self.transInt, self.speaker, self.sliceDb, self.wavFormat, self.soundOutput)