"""
ВНИМАНИЕ! Чтобы работали стрелки влево и вправо нужно кликнуть по карте!
"""


from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.Qt6 import *

import requests
import os
import sys


class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


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

        self.reset_button = QPushButton(self)
        self.reset_button.move(380, 60)
        self.reset_button.setText('Сброс')
        self.reset_button.clicked.connect(self.reset_marker)

        self.change_theme_button = QPushButton(self)
        self.change_theme_button.move(380, 30)
        self.change_theme_button.setText('Тема')
        self.change_theme_button.clicked.connect(self.change_theme)

        self.scheme_view = QPushButton(self)
        self.scheme_view.move(480, 0)
        self.scheme_view.setText('Схема')
        self.scheme_view.clicked.connect(self.set_scheme_view)

        self.map_view = QPushButton(self)
        self.map_view.move(480, 30)
        self.map_view.setText('Карта')
        self.map_view.clicked.connect(self.set_map_view)

        self.hybrid_view = QPushButton(self)
        self.hybrid_view.move(480, 60)
        self.hybrid_view.setText('Гибрид')
        self.hybrid_view.clicked.connect(self.set_hybrid_view)

        self.map_label = ClickableLabel(self)
        self.map_label.resize(600, 500)
        self.map_label.move(0, 100)
        self.map_label.clicked.connect(self.setFocus)

        self.submit_button.clicked.connect(self.search_location)
        self.input_data.returnPressed.connect(self.search_location)

        self.marker = None
        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.geocode_api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        self.theme = 'light'
        self.api_server = 'https://static-maps.yandex.ru/1.x/'
        self.map_zoom = 8
        self.delta = 0.1
        self.map_ll = [37.621598, 55.753460]
        self.map_l = 'map'
        self.setFocus()

        self.refresh_map()

    def search_location(self):
        query = self.input_data.text()
        if not query:
            return

        geocoder_url = 'https://geocode-maps.yandex.ru/1.x/'
        geocoder_params = {
            'apikey': self.geocode_api_key,
            'geocode': query,
            'format': 'json'
        }

        response = requests.get(geocoder_url, params=geocoder_params)
        if response.status_code == 200:
            try:
                results = response.json()
                pos_str = results['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                lon, lat = map(float, pos_str.split())
                self.map_ll = [lon, lat]
                self.marker = f"{lon},{lat},pm2rdm"
                self.refresh_map()
            except (IndexError, KeyError):
                print("Объект не найден")
        else:
            print(response.content)

    def reset_marker(self):
        self.marker = None
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
        if event.key() == Qt.Key.Key_PageUp:
            if self.map_zoom < 20:
                self.map_zoom += 1
        elif event.key() == Qt.Key.Key_PageDown:
            if self.map_zoom > 0:
                self.map_zoom -= 1
        elif event.key() == Qt.Key.Key_Left:
            self.map_ll[0] = max(-180, self.map_ll[0] - self.delta)
        elif event.key() == Qt.Key.Key_Right:
            self.map_ll[0] = min(180, self.map_ll[0] + self.delta)
        elif event.key() == Qt.Key.Key_Down:
            self.map_ll[1] = max(-85, self.map_ll[1] - self.delta)
        elif event.key() == Qt.Key.Key_Up:
            self.map_ll[1] = min(85, self.map_ll[1] + self.delta)

        self.refresh_map()

    def refresh_map(self):
        map_params = {
            'll': ','.join(map(str, self.map_ll)),
            'l': self.map_l,
            'z': self.map_zoom,
            'theme': self.theme,
            'apikey': self.api_key
        }
        if self.marker:
            map_params['pt'] = self.marker

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
