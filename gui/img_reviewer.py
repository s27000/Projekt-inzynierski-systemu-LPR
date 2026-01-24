import sys

from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import QTimer

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import funcs.img_funcs as imgfuncs
import funcs.lpr_funcs as lpr
from funcs.img_browser import ImageBrowser

class ImageReviewer(QWidget):
    def __init__(self, controller, detect_model_path, img_local_path, img_file_list, add_nav_buttons):
        super().__init__()
        #Przypisanie pól obiektów
        self.controller = controller
        self.img_browser = ImageBrowser(img_local_path, img_file_list)
        self.detect_model, self.read_model = lpr.get_models(detect_model_path)
        self.add_nav_buttons = add_nav_buttons
        print(f'[INFO] Ścieżka ładowania pliku/ów: {img_local_path}')
        # Nazwa okna
        self.setWindowTitle("image review")

        # Czcionki - Tytułu oraz nagłówka
        heading_font = QFont()
        heading_font.setPointSize(16)
        heading_font.setBold(True)

        self.subheading_font = QFont()
        self.subheading_font.setPointSize(12)
        self.subheading_font.setBold(True)

        # Panel przetworzonych tablic - lewy panel
        self.plate_panel = QWidget()
        self.plate_panel_layout = QVBoxLayout(self.plate_panel)

        # Panel zdjęcia - środkowy panel
        image_panel = QWidget()
        image_panel.setStyleSheet("QWidget { border: 1px solid black; }")
        image_panel_layout = QVBoxLayout(image_panel)
        heading = QLabel('Przegląd wyników implementacji')
        heading.setFont(heading_font)
        heading.setAlignment(Qt.AlignCenter)
        self.image_display = QLabel()
        self.image_display.setAlignment(Qt.AlignCenter)
        self.image_display.setMinimumSize(600, 600)
        image_panel_layout.addWidget(heading)
        image_panel_layout.addStretch()
        image_panel_layout.addWidget(self.image_display)
        image_panel_layout.addStretch()

        # Panel zawierający nawigację, szczegóły pliku oraz wyniki programu - prawy panel
        nav_panel = QWidget()
        nav_panel.setObjectName('nav_panel')
        nav_panel.setStyleSheet("#nav_panel { border: 1px solid black; }")
        nav_panel_layout = QVBoxLayout(nav_panel)

        # Panel nawigacji - prawy górny
        nav_group_box = QGroupBox('Nawigacja')
        nav_group_box.setAlignment(Qt.AlignCenter)
        nav_group_box_layout = QVBoxLayout(nav_group_box)
        self.exit_button = QPushButton('Powrót do Menu')
        self.exit_button.clicked.connect(self.return_to_menu)

        # Dodawanie guzików nawigacji, jezeli opcja add_nav_buttons jest TRUE
        if self.add_nav_buttons:
            self.previous_img_button = QPushButton('Poprzednie zdjęcie')
            self.previous_img_button.clicked.connect(self.load_prev_image)

            self.next_img_button = QPushButton('Następne zdjęcie')
            self.next_img_button.clicked.connect(self.load_next_image)

            nav_buttons_layout = QHBoxLayout()

            nav_buttons_layout.addWidget(self.previous_img_button)
            nav_buttons_layout.addSpacing(10)
            nav_buttons_layout.addWidget(self.next_img_button)
            nav_group_box_layout.addLayout(nav_buttons_layout)

        nav_group_box_layout.addWidget(self.exit_button)

        # Panel szczegółowy - prawy środkowo
        info_panel = QWidget()
        info_panel.setStyleSheet("QWidget { border: 1px solid black; }")
        info_panel_layout = QVBoxLayout(info_panel)
        img_info_heading = QLabel('Szczegóły pliku')
        img_info_heading.setFont(self.subheading_font)
        img_info_heading.setAlignment(Qt.AlignCenter)
        self.img_info = QLabel()
        self.img_info.setWordWrap(True)
        
        # Panel wyników - prawy dolny
        results_info_heading = QLabel('Wynik programu')
        results_info_heading.setFont(self.subheading_font)
        results_info_heading.setAlignment(Qt.AlignCenter)
        self.results_info = QLabel()

        info_panel_layout.addWidget(img_info_heading)
        info_panel_layout.addWidget(self.img_info)
        info_panel_layout.addSpacing(50)
        info_panel_layout.addWidget(results_info_heading)
        info_panel_layout.addWidget(self.results_info)
        info_panel_layout.addStretch()
        
        nav_panel_layout.addWidget(nav_group_box)
        nav_panel_layout.addWidget(info_panel)
        nav_panel.setFixedWidth(325)

        # Wstawianie paneli do interfejsu
        self.window_layout = QHBoxLayout(self)
        self.window_layout.addWidget(self.plate_panel)
        self.window_layout.addStretch()
        self.window_layout.addWidget(image_panel)
        self.window_layout.addStretch()
        self.window_layout.addWidget(nav_panel)

        self.load_empty_plate_panel('')

        self.adjustSize()

    # Funkcja powrotu do MENU
    def return_to_menu(self):
        self.controller.switch_to_main_menu()

    # Funkcja convertująca obraz cv2 na mapę piksli QPixMap (istotne w wyświetlaniu zdjęcia w GUI)
    def convert_cv2_to_qpixmap(self, img, target_height, max_width):
        img = imgfuncs.rescale_img_to_height_cap_width(img, target_height, max_width)

        qimg = QImage(
            img.data, 
            img.shape[1], 
            img.shape[0], 
            img.strides[0], 
            QImage.Format_BGR888
        )

        pixmap = QPixmap.fromImage(qimg.copy())

        return pixmap
    
    # Funkcja zmieniająca text w Panelu szczegółów pliku
    def load_img_info_text(self, text):
        self.img_info.setText(text)

    # Funkcja zmieniająca text w Panelu wyników programu
    def load_results_info_text(self, text):
        self.results_info.setText(text)
    
    # Funkcja opróżniająca panel tablic, wstawiająca w jego miejsce komunikat (np. Ładowanie...)
    def load_empty_plate_panel(self, label_message):
        old_plate_panel = self.plate_panel

        # Tworzenie nowego panelu
        self.plate_panel = QWidget()
        self.plate_panel.setObjectName('plate_panel')
        self.plate_panel.setStyleSheet("#plate_panel { border: 1px solid black; }")
        self.plate_panel_layout = QVBoxLayout(self.plate_panel)

        plate_panel_subheading = QLabel('Przetworzone tablice')
        plate_panel_subheading.setObjectName('plate_panel_subheading')
        plate_panel_subheading.setStyleSheet("#plate_panel_subheading { border: 1px solid black; }")
        plate_panel_subheading.setFont(self.subheading_font)
        plate_panel_subheading.setAlignment(Qt.AlignCenter)

        plate_panel_text = QLabel(label_message)
        plate_panel_text.setAlignment(Qt.AlignCenter)

        self.plate_panel_layout.addWidget(plate_panel_subheading)
        self.plate_panel_layout.addStretch()
        self.plate_panel_layout.addWidget(plate_panel_text)
        self.plate_panel_layout.addStretch()
        self.plate_panel.setFixedWidth(325)

        # Zastępywanie starego panelu nowym i usunięcie starego
        self.window_layout.replaceWidget(old_plate_panel, self.plate_panel)
        
        old_plate_panel.hide()
        self.plate_panel.repaint()
        old_plate_panel.deleteLater()

    # Funkcja ładująca listę przetworzonych tablic do panelu
    def load_read_plates(self, plate_reading_list):
        old_plate_panel = self.plate_panel

        # Tworzenie nowego panelu
        self.plate_panel = QWidget()
        self.plate_panel_layout = QVBoxLayout(self.plate_panel)
        plate_panel_subheading = QLabel('Przetworzone tablice')
        plate_panel_subheading.setFont(self.subheading_font)
        plate_panel_subheading.setAlignment(Qt.AlignCenter)
        self.plate_panel_layout.addWidget(plate_panel_subheading)
        
        # Dodawanie tablic z listy
        for i in range(0, len(plate_reading_list)):
            plate_read_details = plate_reading_list[i]
            plate_img = plate_read_details['plate_img']
            plate_qpixmap = self.convert_cv2_to_qpixmap(plate_img, 85, 275)

            plate_display_heading = QLabel(f"Tablica #{(i+1)}")
            plate_display = QLabel()
            plate_display.setAlignment(Qt.AlignCenter)
            plate_display.setPixmap(plate_qpixmap)
            plate_caption = QLabel(f"Odczyt: ['{plate_read_details['plate_read']}']")
            plate_caption.setWordWrap(True)

            plate_group_box = QGroupBox()
            plate_group_box_layout = QVBoxLayout()
            plate_group_box_layout.addWidget(plate_display_heading)
            plate_group_box_layout.addWidget(plate_display)
            plate_group_box_layout.addWidget(plate_caption)
            plate_group_box.setLayout(plate_group_box_layout)
        
            self.plate_panel_layout.addWidget(plate_group_box)

        # Dodawanie szczegółów do nowego panelu
        self.plate_panel_layout.addStretch()
        self.plate_panel.setFixedWidth(325)
        self.plate_panel.setStyleSheet("QWidget { border: 1px solid black; }")

        # Zastępywanie starego panelu z nowym
        self.window_layout.replaceWidget(old_plate_panel, self.plate_panel)
        old_plate_panel.deleteLater()
        self.plate_panel.repaint()

    # Funkcja ładująca zdjęcie, wskzazywane przez przeglądarkę zdjęć ImageBrowser
    def load_pointed_image(self):
        shortened_file_name = ''
        file_index = ''
        try:
            # Załadowanie pliku
            file_name = self.img_browser.get_pointed_image_name()

            if self.add_nav_buttons:
                self.update_nav_button()

            print(f'[INFO] Załadowanie {file_name}')
            shortened_file_name = file_name if len(file_name) <= 40 else f"{file_name[:31]}[...]{file_name[-4:]}"
            file_index = f'Plik: [ {(self.img_browser.get_file_pointer()+1)} / {len(self.img_browser.get_image_file_list())} ]\n' if self.add_nav_buttons else '' 

            img = self.img_browser.get_pointed_image()

            # Jeżeli plik nie jest zdjęciem, zwrócić błąd
            if img is None:
                raise TypeError('Nie udało się załadować zdjęcia')

            # Informację zdjęcia oraz rozpoczęcie ładowania
            self.load_img_info_text(
                f'{file_index}'
                f'Nazwa: {shortened_file_name}\n'
                f'Wymiary: {img.shape[1]} x {img.shape[0]}\n'
                f'Pamięć (RAM): {(img.nbytes / (1024 * 1024)):.2f} MB'
            )

            self.image_display.setPixmap(QPixmap())
            self.image_display.setText("Ładowanie...")
            self.image_display.setStyleSheet("QLabel { border: 2px solid black; }")

            self.load_empty_plate_panel('Ładowanie...')
            self.load_results_info_text('Ładowanie...')

            QTimer.singleShot(0, self.controller.center_window)
            QApplication.processEvents()

            # Zastosowanie Funkcji LPR na zdjęciu
            plate_reading_list, lpr_total_time = lpr.lpr_detect_and_read(img, self.detect_model, self.read_model)
            img_pixmap = self.convert_cv2_to_qpixmap(img, 600, 800)

            # Załadowanie wyników
            self.image_display.setText("")
            self.image_display.setPixmap(img_pixmap)
            self.image_display.setStyleSheet("")
            self.image_display.setMinimumSize(img_pixmap.size())

            if len(plate_reading_list) > 0:
                self.load_read_plates(plate_reading_list)
                self.load_results_info_text(
                    f'Czas odczytu: {lpr_total_time:.2f}s\n'
                    f'Liczba znalezionych tablic: {len(plate_reading_list)}\n'
                    f'Odczyty:\n'
                    f'{"\n".join(f"- ['{p}']" for p in [x['plate_read'] for x in plate_reading_list])}'
                )
            else:
                self.load_empty_plate_panel('Brak tablic')
                self.load_results_info_text(
                    f'Czas odczytu: {lpr_total_time}\n'
                    f'Nie znaleziono żadnej tablicy'
                )

        except Exception as err:
            # Obsługa błędu
            self.load_img_info_text(
                f'{file_index}'
                f'Nazwa: {shortened_file_name}\n'
                f'Plik nie udało się załadować'
            )
            self.image_display.setText("Błąd ładowania")
            self.load_empty_plate_panel('Wystąpił Błąd')
            self.load_results_info_text('')
            self.controller.error_messagebox(err)
        
        if not (self.isMaximized() or self.isFullScreen()):
            self.adjustSize()  
            QTimer.singleShot(0, self.controller.center_window)

    # Załadowanie następnego zdjęcia w liście ImageBrowser
    def load_next_image(self):
        self.img_browser.increment_file_pointer()

        if self.img_browser.get_file_pointer() == (len(self.img_browser.get_image_file_list()) - 1):
            self.next_img_button.setEnabled(False)
        self.previous_img_button.setEnabled(True)

        self.load_pointed_image()
    
    # Załadowanie poprzedniego zdjęcia w liście ImageBrowser
    def load_prev_image(self):
        self.img_browser.decrement_file_pointer()
        
        if self.img_browser.get_file_pointer() == 0:
            self.previous_img_button.setEnabled(False)
        self.next_img_button.setEnabled(True)

        self.load_pointed_image()
    
    # Zablokowanie guzików nawigacji, jeżeli osiągają granicę liste (początek lub koniec)
    def update_nav_button(self):
        if self.img_browser.get_file_pointer() == 0:
            self.previous_img_button.setEnabled(False)
        else:
            self.previous_img_button.setEnabled(True)

        if self.img_browser.get_file_pointer() == (len(self.img_browser.get_image_file_list()) - 1):
            self.next_img_button.setEnabled(False)
        else:
            self.next_img_button.setEnabled(True)
