from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.Qt6 import *

import requests
import os
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)

        self.input_data = QLineEdit(self)
        self.input_data.resize(380, 30)
        self.input_data.move(0, 0)
        # self.input_data.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.submit_button = QPushButton(self)
        self.submit_button.move(380, 0)
        self.submit_button.setText('Искать')
        # self.submit_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.change_theme_button = QPushButton(self)
        self.change_theme_button.move(380, 30)
        self.change_theme_button.setText('Тема')
        self.change_theme_button.clicked.connect(self.change_theme)

        self.scheme_view = QPushButton(self)
        self.scheme_view.move(380 + 100, 0)
        self.scheme_view.setText('Схема')
        self.scheme_view.clicked.connect(self.set_scheme_view)
        # self.set_scheme_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.map_view = QPushButton(self)
        self.map_view.move(380 + 100, 30)
        self.map_view.setText('Карта')
        self.map_view.clicked.connect(self.set_map_view)
        # self.set_map_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hybrid_view = QPushButton(self)
        self.hybrid_view.move(380 + 100, 60)
        self.hybrid_view.setText('Гибрид')
        self.hybrid_view.clicked.connect(self.set_hybrid_view)
        # self.set_hybrid_view.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.map_label = QLabel(self)
        self.map_label.resize(600, 500)
        self.map_label.move(0, 80)
        # self.map_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.theme = 'light'
        self.api_server = 'https://static-maps.yandex.ru/1.x/'
        self.map_zoom = 8
        self.delta = 0.1
        self.map_ll = [37.621598, 55.753460]
        self.map_l = 'map'
        self.refresh_map()

    def change_theme(self):
        if self.theme == 'light':
            self.theme = 'dark'
        else:
            self.theme = 'light'
        self.refresh_map()

    def set_map_view(self):
        self.map_l = 'map'
        self.refresh_map()

    def set_scheme_view(self):
        self.map_l = 'drive'
        self.refresh_map()

    def set_hybrid_view(self):
        self.map_l = 'admin'
        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp and self.map_zoom <= 20:
            self.map_zoom += 1
        if event.key() == Qt.Key.Key_PageDown and self.map_zoom > 0:
            self.map_zoom -= 1
        print(1)
        if event.key() == Qt.Key.Key_Left:
            self.map_ll[0] -= self.delta
        if event.key() == Qt.Key.Key_Right:
            self.map_ll[0] += self.delta
        if event.key() == Qt.Key.Key_Down:
            self.map_ll[1] -= self.delta
        if event.key() == Qt.Key.Key_Up:
            self.map_ll[1] += self.delta

        self.refresh_map()

    def refresh_map(self):
        map_params = {
            'll': ','.join(map(str, self.map_ll)),
            'l': self.map_l,
            'z': self.map_zoom,
            'theme': self.theme,
            'apikey': self.api_key
        }
        response = requests.get(self.api_server, params=map_params)
        if response.status_code == 200:
            pix_map = QPixmap()
            pix_map.loadFromData(response.content)
            self.map_label.setPixmap(pix_map)
        else:
            print(response.status_code, response.content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
