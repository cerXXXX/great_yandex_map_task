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

        self.submit_button = QPushButton(self)
        self.submit_button.move(380, 0)
        self.submit_button.setText('Искать')

        self.set_scheme_view = QPushButton(self)
        self.set_scheme_view.move(380 + 100, 0)
        self.set_scheme_view.setText('Схема')

        self.set_scheme_view = QPushButton(self)
        self.set_scheme_view.move(380 + 100, 0)
        self.set_scheme_view.setText('Схема')

        self.set_map_view = QPushButton(self)
        self.set_map_view.move(380 + 100, 30)
        self.set_map_view.setText('Карта')

        self.set_hybrid_view = QPushButton(self)
        self.set_hybrid_view.move(380 + 100, 60)
        self.set_hybrid_view.setText('Гибрид')

        self.map_label = QLabel(self)
        self.map_label.resize(600, 500)
        self.map_label.move(0, 80)

        self.api_server = 'https://static-maps.yandex.ru/1.x/'
        self.map_zoom = 8
        self.delta = 0.1
        self.map_ll = [37.621598, 55.753460]
        self.map_l = 'map'
        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp and self.map_zoom <= 20:
            self.map_zoom += 1
        if event.key() == Qt.Key.Key_PageDown and self.map_zoom > 0:
            self.map_zoom -= 1
        self.refresh_map()

    def refresh_map(self):
        map_params = {
            'll': ','.join(map(str, self.map_ll)),
            'l': self.map_l,
            'z': self.map_zoom
        }
        response = requests.get(self.api_server, params=map_params)
        if response.status_code == 200:
            pix_map = QPixmap()
            pix_map.loadFromData(response.content)
            self.map_label.setPixmap(pix_map)
        else:
            print(response.status_code)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
