import os

from PySide6.QtWidgets import *
from PySide6.QtGui import *

class MainMenu(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller

        self.setWindowTitle("main app")
        self.setMinimumWidth(520)

        # Tytuł
        title = QLabel("Aplikacja systemu odczytywania tablic rejestracyjnych pojazdów, wspomaganym AI")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)

        # Opis
        label_desc = QLabel(
            "Program przestawia działanie zaimplementowanego systemu automatycznego odczytu tablic rejestracyjnych. "
            "System korzysta z modelu YOLO, którego ścieżkę można ustawić w pliku \'main_app.config\'. Program korzysta "
            "z funkcji znajdujących się w bibliotece \'funcs.lpr_funcs\', w której znajduję się cała istotna implementacja systemu LPR. "
            "Implementacja obejmuje m.in. wykorzystanie sieci konwolucyjnej typu Yolo, algorytmów wizji maszynowej oraz algorytmu OCR). " 
            "Zalecany jest jej przegląd, aby uzyskać więcej informacji na temat wykorzystanych funkcji, użytych "
            "zależności i innych istotnych szczegółów w realizacji systemu"
        )
        label_desc.setWordWrap(True)
        label_desc.setStyleSheet("QWidget { border: 1px solid black; border-radius: 5px;}")
        
        # Czcionka nagłówków
        markdown_font = QFont()
        markdown_font.setBold(True)

        # Opcja #1 - przegląd domyslnego katalogu
        group_default_cat_option = QGroupBox("Opcja #1: Przegląd domyślnego katalogu ze zdjęciami")

        # Nagłówek i przycisk Opcji #1
        label_default_opt_input = QLabel("Użyj ścieżkę domyślną, zapisaną w pliku \'main_app.config\'")
        label_default_opt_input.setFont(markdown_font)
        self.img_default_opt_button = QPushButton('Rozpocznij')
        self.img_default_opt_button.clicked.connect(self.default_option_start)

        default_cat_start_layout = QVBoxLayout()
        default_cat_start_button_layout = QHBoxLayout()

        default_cat_start_button_layout.addWidget(self.img_default_opt_button)
        default_cat_start_button_layout.addStretch()

        default_cat_start_layout.addWidget(label_default_opt_input)
        default_cat_start_layout.addLayout(default_cat_start_button_layout)

        group_default_cat_option.setLayout(default_cat_start_layout)

        # Opcja #2 - przegląd katalogu zdjęć
        group_cat_option = QGroupBox("Opcja #2: Przegląd katalogu z zdjęciami")

        # Nagłówek, Pole tekstowe i przycisk Opcji #2
        label_cat_input = QLabel("Podaj ścieżkę do katalogu ze zdjęciami")
        label_cat_input.setFont(markdown_font)
        self.cat_path_input = QLineEdit()
        self.cat_input_button = QPushButton('Rozpocznij')
        self.cat_input_button.clicked.connect(self.cat_option_start)

        cat_input_layout = QVBoxLayout()
        cat_input_layout_editbox_n_button = QHBoxLayout()

        cat_input_layout_editbox_n_button.addWidget(self.cat_path_input)
        cat_input_layout_editbox_n_button.addWidget(self.cat_input_button)

        cat_input_layout.addWidget(label_cat_input)
        cat_input_layout.addLayout(cat_input_layout_editbox_n_button)

        group_cat_option.setLayout(cat_input_layout)

        # Opcja #3 - przegląd jednego zdjęcia
        group_img_option = QGroupBox("Opcja #3: Przegląd jednego zdjęcia")

        # Nagłówek, Pole tekstowe i przycisk Opcji #3
        label_img_input = QLabel("Podaj ścieżkę do zdjęcia")
        label_img_input.setFont(markdown_font)
        self.img_path_input = QLineEdit()
        self.img_input_button = QPushButton('Rozpocznij')
        self.img_input_button.clicked.connect(self.image_option_start)

        img_input_layout = QVBoxLayout()
        img_input_layout_editbox_n_button = QHBoxLayout()

        img_input_layout_editbox_n_button.addWidget(self.img_path_input)
        img_input_layout_editbox_n_button.addWidget(self.img_input_button)

        img_input_layout.addWidget(label_img_input)
        img_input_layout.addLayout(img_input_layout_editbox_n_button)

        group_img_option.setLayout(img_input_layout)

        # Przycisk wyjścia z aplikacji
        self.exit_button = QPushButton('Wyjdź')
        self.exit_button.clicked.connect(self.close)

        # Wyśrodkowoanie przyisku wyjścia
        exit_button_layout = QHBoxLayout()
        exit_button_layout.addStretch()
        exit_button_layout.addWidget(self.exit_button)
        exit_button_layout.addStretch()

        # Wstawianie wszystkich elementów do okna
        window_layout = QVBoxLayout()

        window_layout.addWidget(title)
        window_layout.addSpacing(10)
        window_layout.addWidget(label_desc)
        window_layout.addSpacing(25)

        window_layout.addWidget(group_default_cat_option)
        window_layout.addWidget(group_cat_option)
        window_layout.addWidget(group_img_option)

        window_layout.addSpacing(15)

        window_layout.addStretch()
        window_layout.addLayout(exit_button_layout)

        self.setLayout(window_layout)

    # Funkcja wybierająca opcję domyslnego katalogu
    def default_option_start(self):
        self.controller.switch_to_default_cat_option()

    # Funkcja wybierająca opcję ścieżki katalogu
    def cat_option_start(self):
        cat_path = self.cat_path_input.text().strip()
        self.controller.switch_to_cat_path_option(cat_path)
    
    # Funkcja wybierająca opcję ścieżki zdjęcia
    def image_option_start(self):
        img_path = self.img_path_input.text().strip()
        self.controller.switch_to_img_path_option(img_path)
    