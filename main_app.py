import sys
import os
import re
import configparser
import traceback

from PySide6.QtWidgets import *

from gui.load_app import LoadScreen
from gui.main_menu import MainMenu
from gui.img_reviewer import ImageReviewer

config = configparser.ConfigParser()
config.read('main_app.config')

# SCIEŻKI
DETECT_MODEL_PATH = config.get("MAIN_APP", "detect_model_path")
DEFAULT_READ_DIR_PATH = config.get("MAIN_APP", "default_read_dir_path")

# KLASA WIODĄCA GUI
class AppController:
    def __init__(self):
        self.current_window = None

    # Funkcja zmienają aktualne okno, zamykająca stare
    def change_window(self, window):
        if self.current_window:
            self.current_window.close()
        self.current_window = window
        self.current_window.show()
        self.center_window()

    # Funkcja wyśrodokowująca aktualne okno
    def center_window(self):
        if (self.current_window.isMaximized() or self.current_window.isFullScreen()):
            return
    
        screen = QApplication.primaryScreen()
        screen_geo = screen.availableGeometry()

        window_geo = self.current_window.frameGeometry()
        window_geo.moveCenter(screen_geo.center())

        self.current_window.move(window_geo.topLeft())

    # Funkcja przełaczenia na menu główne
    def switch_to_main_menu(self):
        print('[INFO] Przełączenie aplikacji na Menu Główne')
        self.change_window(MainMenu(self))
    
    # Funkcja przełaczenia na ekran ładowania
    def switch_to_load_screen(self):
        print('[INFO] Ładowanie aplikacji...')
        self.change_window(LoadScreen(self))

    # Funkcja przełączająca na opcję ładowania domyslnej ścieżki katalogu
    def switch_to_default_cat_option(self):
        print('[INFO] Zastosowanie domyślnej ścieżki katalogu')
        self.switch_to_cat_path_option(DEFAULT_READ_DIR_PATH)
    
    # Funkcja przełączaja na opcję ładowania wpisanej ścieżki katalogu
    def switch_to_cat_path_option(self, cat_path):
        print('[INFO] Przełączenie aplikacji na opcję ścieżki katalogu')
        try:
            self.verify_path(cat_path)

            if not os.path.isdir(cat_path):
                raise Exception("Podana ścieżka nie prowadzi do katalogu")
            
            file_list = os.listdir(cat_path)

            self.load_img_reviewer(DETECT_MODEL_PATH, cat_path, file_list, True)
            
        except Exception as err:
            self.error_messagebox(err)

    # Funkcja przełączaja na opcję ładowania wpisanej ścieżki zdjęcia
    def switch_to_img_path_option(self, image_path):
        print('[INFO] Przełączenie aplikacji na opcję ścieżki zdjęcia')
        try:
            self.verify_path(image_path)

            img_local, img_file_in_list = self.prep_review_for_single_image(image_path)
            
            self.load_img_reviewer(DETECT_MODEL_PATH, img_local, img_file_in_list, False)

        except Exception as err:
            self.error_messagebox(err)

    # Funkcja włączająca przełączająca na podgląd zdjęć 
    def load_img_reviewer(self, model_path, cat_path, file_list, add_nav_buttons):
        self.switch_to_load_screen()
        QApplication.processEvents()

        img_reviewer = ImageReviewer(self, model_path, cat_path, file_list, add_nav_buttons)
            
        self.change_window(img_reviewer)
        img_reviewer.load_pointed_image()

    # Funkcja weryfikująca ścieżkę
    def verify_path(self, path):
        if not path:
            raise Exception("Rubryka na ścieżkę jest pusta")
        if not os.path.exists(path):
            raise Exception("Ściezka nie istnieje")

    # Funkcja rozbijająca ścieżki zdjęcia na jedno elementową listę oraz lokalizację pliku
    def prep_review_for_single_image(self, img_path):
        img_path_parts = re.split(r"[\\/]", img_path)
        img_file = img_path_parts.pop()
        img_local = '\\'.join(img_path_parts)

        img_file_in_list = list()
        img_file_in_list.append(img_file)

        return img_local, img_file_in_list

    # Funkcja wyświetlająca błąd w aktualnym oknie
    def error_messagebox(self, exception):
        print(f"[ERROR] {type(exception).__name__}: {exception}")
        traceback.print_tb(exception.__traceback__)

        QMessageBox.critical(
            self.current_window,
            'error',
            f"BŁĄD: {type(exception).__name__}\n{exception}"
        )
## METDOA WIODĄCA
def main():
    app = QApplication(sys.argv)
    controller = AppController()

    controller.switch_to_main_menu()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()