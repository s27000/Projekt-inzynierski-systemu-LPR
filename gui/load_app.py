import os

from PySide6.QtWidgets import *
from PySide6.QtGui import *

class LoadScreen(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("loading screen")
        self.setFixedSize(300, 100)

        title = QLabel("Ładowanie interfejsu aplikacji")
        title.setStyleSheet("QWidget { border: 1px solid black; }")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setAlignment(Qt.AlignCenter)
        title.setFont(title_font)

        text = QLabel("Ładowanie...")
        text.setAlignment(Qt.AlignCenter)
        text_font = QFont()
        text_font.setPointSize(9)
        text.setFont(text_font)

        layout = QVBoxLayout(self)
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(text)
        layout.addStretch()