from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import requests
import sys


class ClickableLabel(QLabel):
    clicked = pyqtSignal(QPoint)

    def mousePressEvent(self, event):
        self.clicked.emit(event.pos())
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)
        self.init_ui()
        self.init_map_params()

    def init_ui(self):
        self.input_data = QLineEdit(self)
        self.input_data.resize(380, 30)
        self.input_data.move(0, 0)

        self.submit_button = QPushButton('Искать', self)
        self.submit_button.move(380, 0)
        self.submit_button.clicked.connect(self.search_location)

        self.reset_button = QPushButton('Сброс', self)
        self.reset_button.move(380, 60)
        self.reset_button.clicked.connect(self.reset_marker)

        self.change_theme_button = QPushButton('Тема', self)
        self.change_theme_button.move(380, 30)
        self.change_theme_button.clicked.connect(self.change_theme)

        self.scheme_view = QPushButton('Схема', self)
        self.scheme_view.move(480, 0)
        self.scheme_view.clicked.connect(self.set_scheme_view)

        self.map_view = QPushButton('Карта', self)
        self.map_view.move(480, 30)
        self.map_view.clicked.connect(self.set_map_view)

        self.hybrid_view = QPushButton('Гибрид', self)
        self.hybrid_view.move(480, 60)
        self.hybrid_view.clicked.connect(self.set_hybrid_view)

        self.map_label = ClickableLabel(self)
        self.map_label.resize(600, 450)
        self.map_label.move(0, 100)
        self.map_label.clicked.connect(self.handle_map_click)

        self.address_label = QLabel(self)
        self.address_label.resize(380, 30)
        self.address_label.move(0, 570)

        self.include_postcode_checkbox = QCheckBox('Включить почтовый индекс', self)
        self.include_postcode_checkbox.move(380, 90)
        self.include_postcode_checkbox.stateChanged.connect(self.update_address)

        self.input_data.returnPressed.connect(self.search_location)

    def init_map_params(self):
        self.marker = None
        self.address = None
        self.api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        self.geocode_api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        self.theme = 'light'
        self.api_server = 'https://static-maps.yandex.ru/1.x/'
        self.geocode_api_server = 'https://geocode-maps.yandex.ru/1.x/'
        self.map_zoom = 10
        self.map_center = [37.617644, 55.755819]
        self.map_l = 'map'
        self.refresh_map()

    def handle_map_click(self, pos):
        try:
            map_width = self.map_label.width()
            map_height = self.map_label.height()

            delta_lon = 360 / (2 ** self.map_zoom)
            delta_lat = 180 / (2 ** self.map_zoom)

            dx = (pos.x() - map_width / 2) * delta_lon / map_width
            dy = (map_height / 2 - pos.y()) * delta_lat / map_height

            lon = self.map_center[0] + dx
            lat = self.map_center[1] + dy

            self.process_geocoding(lon, lat)

        except Exception as e:
            self.address_label.setText(f"Ошибка: {str(e)}")

    def process_geocoding(self, lon, lat):
        geocoder_params = {
            'apikey': self.geocode_api_key,
            'geocode': f"{lon:.6f},{lat:.6f}",
            'format': 'json'
        }
        try:
            response = requests.get(self.geocode_api_server, params=geocoder_params, timeout=5)
            if response.status_code != 200:
                self.address_label.setText("Ошибка соединения")
                return
            results = response.json()
            features = results.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])

            if not features:
                self.address_label.setText("Адрес не найден")
                self.marker = None
                self.refresh_map()
                return

            feature = features[0].get('GeoObject', {})
            pos_str = feature.get('Point', {}).get('pos', '')

            if not pos_str:
                raise Exception()

            marker_lon, marker_lat = map(float, pos_str.split())
            self.marker = f"{marker_lon:.6f},{marker_lat:.6f},pm2rdm"
            self.address = feature.get('name', 'Неизвестный адрес')
            self.update_address(results)
            self.refresh_map()

        except Exception as e:
            print(e)

    def search_location(self):
        query = self.input_data.text().strip()
        if not query:
            return
        geocoder_params = {
            'apikey': self.geocode_api_key,
            'geocode': query,
            'format': 'json'
        }
        try:
            response = requests.get(self.geocode_api_server, params=geocoder_params, timeout=5)
            if response.status_code != 200:
                self.address_label.setText("Ошибка поиска")
                return
            results = response.json()
            features = results.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [])

            if not features:
                self.address_label.setText("Объект не найден")
                return

            feature = features[0].get('GeoObject', {})
            pos_str = feature.get('Point', {}).get('pos', '')

            if not pos_str:
                raise ValueError()

            lon, lat = map(float, pos_str.split())
            self.map_center = [lon, lat]
            self.marker = f"{lon:.6f},{lat:.6f},pm2rdm"
            self.address = feature.get('name', 'Неизвестный адрес')
            self.update_address(results)
            self.refresh_map()

        except requests.RequestException:
            self.address_label.setText("Ошибка сети")
        except (KeyError, IndexError, ValueError):
            self.address_label.setText("Ошибка данных")
        except Exception:
            self.address_label.setText("Системная ошибка")

    def update_address(self, results=None):
        try:
            text = "Адрес: " + (self.address or "не определен")
            if results and self.include_postcode_checkbox.isChecked():
                address_data = results.get('response', {}).get('GeoObjectCollection', {}).get('featureMember', [{}])[
                    0].get('GeoObject', {}).get('metaDataProperty', {}).get('GeocoderMetaData', {}).get('Address', {})
                postcode = address_data.get('postal_code', '')
                if postcode:
                    text += f", {postcode}"
            self.address_label.setText(text)
        except Exception:
            self.address_label.setText("Ошибка формата данных")

    def reset_marker(self):
        self.marker = None
        self.address = None
        self.address_label.setText("Адрес: ")
        self.refresh_map()

    def change_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.refresh_map()

    def set_map_view(self):
        self.map_l = 'map'
        self.refresh_map()

    def set_scheme_view(self):
        self.map_l = 'skl'
        self.refresh_map()

    def set_hybrid_view(self):
        self.map_l = 'sat,skl'
        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_PageUp:
            self.map_zoom = min(20, self.map_zoom + 1)
        elif event.key() == Qt.Key.Key_PageDown:
            self.map_zoom = max(1, self.map_zoom - 1)
        elif event.key() == Qt.Key.Key_Left:
            self.map_center[0] -= 0.5 * (360 / (2 ** self.map_zoom))
        elif event.key() == Qt.Key.Key_Right:
            self.map_center[0] += 0.5 * (360 / (2 ** self.map_zoom))
        elif event.key() == Qt.Key.Key_Down:
            self.map_center[1] -= 0.5 * (180 / (2 ** self.map_zoom))
        elif event.key() == Qt.Key.Key_Up:
            self.map_center[1] += 0.5 * (180 / (2 ** self.map_zoom))
        self.map_center[0] = max(-180, min(180, self.map_center[0]))
        self.map_center[1] = max(-85, min(85, self.map_center[1]))
        self.refresh_map()

    def refresh_map(self):
        map_params = {
            'll': f"{self.map_center[0]:.6f},{self.map_center[1]:.6f}",
            'l': self.map_l,
            'z': self.map_zoom,
            'theme': self.theme,
            'size': '600,450',
            'apikey': self.api_key
        }
        if self.marker:
            map_params['pt'] = self.marker
        response = requests.get(self.api_server, params=map_params)
        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            self.map_label.setPixmap(pixmap)
        else:
            print(f"Ошибка: {response.status_code}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
