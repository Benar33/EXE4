from PySide6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os


def load_stylesheet(app):
    qss_path = os.path.join(os.path.dirname(__file__), 'modern.qss')
    with open(qss_path, 'r', encoding='utf-8') as qss_file:
        app.setStyleSheet(qss_file.read())


class AboutWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('About Me')
        self.setFixedSize(420, 560)
        self.setObjectName('aboutWindow')

        self.my_name = QLabel('BEN ARBIB', self)
        self.my_name.setObjectName('aboutName')
        self.my_name.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.my_picture = QLabel(self)
        self.my_picture.setObjectName('aboutPicture')
        self.my_picture.setFixedSize(300, 300)
        self.my_picture.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_path = os.path.join(os.path.dirname(__file__), 'me.jpg')
        image = QPixmap(image_path).scaled(
            296, 296,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.my_picture.setPixmap(image)

        self.my_email = QLabel('Email: ben.david.arbib@s.afeka.ac.il', self)
        self.my_email.setObjectName('aboutEmail')
        self.my_email.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.my_link = QLabel('<a href="https://github.com/Benar33">GitHub</a>', self)
        self.my_link.setObjectName('aboutLink')
        self.my_link.setOpenExternalLinks(True)
        self.my_link.setAlignment(Qt.AlignmentFlag.AlignCenter)

        root = QVBoxLayout(self)
        root.setContentsMargins(36, 28, 36, 28)
        root.setSpacing(14)
        root.addWidget(self.my_name)

        picture_row = QHBoxLayout()
        picture_row.addStretch()
        picture_row.addWidget(self.my_picture)
        picture_row.addStretch()
        root.addLayout(picture_row)
        root.addWidget(self.my_email)
        root.addWidget(self.my_link)


if __name__ == '__main__':
    app = QApplication()
    load_stylesheet(app)
    window = AboutWindow()
    window.show()
    app.exec()