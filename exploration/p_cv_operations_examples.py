import numpy as np
import cv2
import sys
import os
import configparser

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import funcs.img_funcs as imgfuncs
from funcs.img_browser import ImageBrowser

## SCIEŻKI
config = configparser.ConfigParser()
config.read('exploration/exploration.config')

IMG_PATH = config.get("CV_OP_EXAMPLES", "img_path")
Img_Browser = ImageBrowser(
    IMG_PATH, 
    os.listdir(IMG_PATH)
)

## WARTOŚCI STAŁE
MAX_IMG_SIZE = 750
WINDOW_NAME = 'obraz'
ESC_KEY = 27
is_window_reloaded = True

## PARAMETRY FUNKCJI WIZJI MASZYNOWYCH
class Param:
    def __init__(self, value, max_value):
        self.value = value
        self.max_value = max_value

## SŁOWNIK PARAMETRÓW
param_dict = {
    'hsv_low': Param(0,180),
    'hsv_high': Param(180,180),
    'sat_low': Param(0,255),
    'sat_high': Param(100,255),
    'val_low': Param(0,255),
    'val_high': Param(100,255),
    't_lower': Param(100,255),
    't_upper': Param(150,255),
    'aptr_size' : Param(0,2),
    'k_size': Param(0,45),
    'k_size_2': Param(0,45),
    'k_size_3' : Param(0,45),
    'block_size': Param(0,45),
    'c': Param(0,30),
    'epsilon': Param(0,100)
}

# Funkcja zwracająca funkcje zmieniającą parametry (wymagane jako parametr do suwaków TrackBar)
def update_param_dict(name):
    def cb(value):
        param_dict[name].value = value
 
    return cb

# Funkcja wytworzenia maski binarnej stosując progowanie globalne
def create_mask(img):
    hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    lower = np.array([param_dict['hsv_low'].value, param_dict['sat_low'].value, param_dict['val_low'].value])
    upper = np.array([param_dict['hsv_high'].value, param_dict['sat_high'].value, param_dict['val_high'].value])

    mask = cv2.inRange(hsv_frame, lower, upper)

    return mask

# Funkcja łącząca maskę binarnej z obrazem rzeczywistym, uzywając operacji bitowych 
def bitwise_and(img):
    mask = create_mask(img)
    bitwise_and_img = cv2.bitwise_and(img, img, mask=mask)

    return bitwise_and_img

# Funkcja przeprowadzająca operację zamykania morfologicznego
def morfology_close(img):
    mask = create_mask(img)

    k_size_rescaled = 2*param_dict['k_size'].value + 1

    kernel = np.ones((k_size_rescaled, k_size_rescaled), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)

    return mask

# Funkcja przeprowadzająca operację otwierania morfologicznego
def morfology_open(img):
    mask = create_mask(img)

    k_size_rescaled = 2*param_dict['k_size'].value + 1

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size_rescaled, k_size_rescaled))
    
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    return mask

# Funkcja przeprowadzająca rozmazanie Gaussa na obrazie 
def process_blur(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    k_size_rescaled = 2*param_dict['k_size'].value + 1
    blur = cv2.GaussianBlur(gray, (k_size_rescaled, k_size_rescaled), 0)

    return blur

# Funkcja stosująca algorytm Canny'ego na obrazie
def process_canny(img):
    appetureSize_rescaled = param_dict['aptr_size'].value * 2 + 3
    edge = cv2.Canny(img, param_dict['t_lower'].value, param_dict['t_upper'].value, apertureSize=appetureSize_rescaled)

    return edge

# Funkcja łącząca rozmywcie wraz z algorytmem Canny'ego
def process_blur_canny(img):
    blur = process_blur(img)
    edge = process_canny(blur)

    return edge

# Funkcja stosująca gaussowskie progowanie adaptacyjne na obrazie
def process_adaptiveThresholding(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    k_size_rescaled = 2*param_dict['k_size'].value + 1
    
    blur = cv2.GaussianBlur(gray,(k_size_rescaled,k_size_rescaled),0)

    block_size_rescaled = 2*param_dict['block_size'].value + 3
    th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY_INV, block_size_rescaled, param_dict['c'].value)
    
    k_size_rescaled_2 = 2*param_dict['k_size_2'].value + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k_size_rescaled_2,k_size_rescaled_2))
    morph_open = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)

    k_size_rescaled_3 = 2*param_dict['k_size_3'].value + 1
    kernel_2 = np.ones((k_size_rescaled_3, k_size_rescaled_3), np.int8)
    morph_close = cv2.morphologyEx(morph_open, cv2.MORPH_CLOSE, kernel_2, iterations=1)
    
    return morph_close

# Funkcja stosująca globalne progowanie Otsu
def process_otsu(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return mask

# Funkcja wprowadzająca suwaki do okna z wybranej listy parametrów
def reload_window(param_list):
    global is_window_reloaded
    if is_window_reloaded:
        cv2.destroyWindow(WINDOW_NAME)
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, 700, 700)
        for param in param_list:
            cv2.createTrackbar(param, 
                               WINDOW_NAME, 
                               param_dict[param].value, 
                               param_dict[param].max_value, 
                               update_param_dict(param))
        is_window_reloaded = False

# Wyświetlenie opcji
def print_help():
    print(
        f'-----===== Możliwe opcje =====-----\n'
        f'\'h\' - wyświetl możliwe opcje\n'
        f'\'ESC\' - wyjście z aplikacji\n'
        f'\'a\' / \'d\' - przemieszczenie się po liście plików\n'
        f'\'1\' - zdjęcie bez modyfikacji\n'
        f'\'2\' - progowanie globalne liczbą stałą\n'
        f'\'3\' - operacja morfologicznego zamykania\n'
        f'\'4\' - operacja morfologicznego otwierania\n'
        f'\'5\' - połączenie maski z zdjęciem operacją bitową\n'
        f'\'6\' - rozmycie Gaussa\n'
        f'\'7\' - algorytm Canny\'ego\n'
        f'\'8\' - rozmycie Gaussa + algorytm Canny\'ego\n'
        f'\'9\' - progowanie adaptacyjne gaussowskie\n'
        f'\'0\' - progowanie Otsu'
    )

# METODA WIODĄCA
def main():
    global is_window_reloaded

    # Załadowanie domyślnego zdjęcia
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    image = Img_Browser.get_pointed_image()
    displayed_image = image.copy()
    selected_function = 1

    print_help()

    # PĘTLA APLIKACJI
    while True:

        # Wyświetlanie zdjęcia
        match selected_function:
            case 1:
                displayed_image = image.copy()
                reload_window([])
            case 2:
                displayed_image = create_mask(image)
                reload_window(['hsv_low', 'hsv_high', 'sat_low', 'sat_high', 'val_low', 'val_high'])
            case 3:
                displayed_image = morfology_close(image)
                reload_window(['hsv_low', 'hsv_high', 'sat_low', 'sat_high', 'val_low', 'val_high', 'k_size'])
            case 4:
                displayed_image = morfology_open(image)
                reload_window(['hsv_low', 'hsv_high', 'sat_low', 'sat_high', 'val_low', 'val_high', 'k_size'])
            case 5:
                displayed_image = bitwise_and(image)
                reload_window(['hsv_low', 'hsv_high', 'sat_low', 'sat_high', 'val_low', 'val_high'])
            case 6:
                displayed_image = process_blur(image)
                reload_window(['k_size'])
            case 7:
                displayed_image = process_canny(image)
                reload_window(['t_lower','t_upper','aptr_size'])
            case 8:
                displayed_image = process_blur_canny(image)
                reload_window(['k_size', 't_lower','t_upper', 'aptr_size'])
            case 9:
                displayed_image = process_adaptiveThresholding(image)
                reload_window(['k_size', 'block_size', 'c', 'k_size_2', 'k_size_3'])
            case 0:
                displayed_image = process_otsu(image)
                reload_window([])

        cv2.imshow(WINDOW_NAME, imgfuncs.resize_image(displayed_image, 600))

        # FUNKCJE KLAWISZY
        key = cv2.pollKey()

        # Wyświetlenie pomocy
        if key == ord('h'):
            print_help()

        # Wyjście z aplikacji
        if key == ESC_KEY:
            cv2.destroyAllWindows()
            break
        
        # Przewijanie zdjęć
        if key == ord('d'):
            Img_Browser.increment_file_pointer()
            image = Img_Browser.get_pointed_image()
        if key == ord('a'):
            Img_Browser.decrement_file_pointer()
            image = Img_Browser.get_pointed_image()

        # Wybieranie rodzaj wyświetlanego zdjęcia (klawiwsze 0 - 9)
        if ord('0') <= key <= ord('9'):
            key_value = key - ord('0')
            selected_function = key_value  
            is_window_reloaded = True  
            
if __name__ == "__main__":
    main()