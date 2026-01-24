import cv2
import os 
import sys
from pathlib import Path
import configparser

from tkinter import *

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import funcs.file_funcs as filefuncs
import funcs.img_funcs as imgfuncs
from funcs.img_browser import ImageBrowser

## ŚCIEŻKI
config = configparser.ConfigParser()
config.read('exploration/exploration.config')

LOAD_SET_PATH = config.get("DATA_MODIFIER", "load_set_path")
COPY_SET_PATH = config.get("DATA_MODIFIER", "copy_set_path")

Img_Browser = ImageBrowser(
    filefuncs.get_img_dir_path(LOAD_SET_PATH), 
    filefuncs.get_filtered_set_image_list(LOAD_SET_PATH, COPY_SET_PATH)
)

## WARTOŚCI STAŁE
MAIN_WINDOW_NAME = 'obraz'
ACCEPT_IMG_WIN_NAME = 'zapisz obraz'
ESC_KEY = 27

## Funkcja wpisująca element do listy odrzuconych
def append_set_blacklist(set_path, filtered_set, img_file_name):
    root_bl_path = filefuncs.get_root_blacklist_path(set_path)
    root_bl_dict = filefuncs.get_rootfile_as_dict(root_bl_path)

    if filtered_set not in root_bl_dict:
        root_bl_dict[filtered_set] = set()
    root_bl_dict[filtered_set].add(img_file_name)

    print(f'[INFO] Odrzucenie zdjecia {img_file_name} ze zbioru')

    filefuncs.override_root_file(root_bl_path, root_bl_dict)

## Funkcja przyjmująca element do listy przyjętych
# -> skopiowanie wszystkich niezbędnych elementów
# -> dopisanie elementu do pliku listy przyjętych
def copy_image_to_set_whitelist(set_path, filtered_set, img, img_file_name, saved_lp_list):
    print(f"[INFO] Zapisywanie {img_file_name} do zbioru, z obiektami:")

    for i in range(0, len(saved_lp_list)):
        print(f'->{saved_lp_list[i]}')

    root_wl_path = filefuncs.get_root_whitelist_path(set_path)
    root_wl_dict = filefuncs.get_rootfile_as_dict(root_wl_path)

    ## Dodawanie nowego elementu do zbioru
    # tworzenie ścieżek zapisu i plików
    copy_set_img_path = filefuncs.get_img_dir_path(set_path)
    copy_set_label_path = filefuncs.get_yolo_label_dir_path(set_path)
    copy_set_detail_path = filefuncs.get_details_dir_path(set_path)
    
    new_img_path = os.path.join(copy_set_img_path, img_file_name)
    
    img_txt_name = filefuncs.get_img_txt_name(img_file_name)
    new_yolo_label_path = os.path.join(copy_set_label_path, img_txt_name)
    new_detail_path = os.path.join(copy_set_detail_path, img_txt_name)

    cv2.imwrite(new_img_path, img)
    open(new_yolo_label_path, "a").close()
    open(new_detail_path, "a").close()

    # Zapisywanie elementu do zbioru danych
    with open(new_yolo_label_path, 'w') as new_yolo_file:
        with open(new_detail_path, 'w') as new_detail_file:
            for i in range(0, len(saved_lp_list)):
                yolo_label = " ".join(str(v) for v in saved_lp_list[i][1])
                if i == (len(saved_lp_list)-1):
                    new_detail_file.write(saved_lp_list[i][0])
                    new_yolo_file.write(yolo_label)
                else: 
                    new_detail_file.write(saved_lp_list[i][0] + '\n')
                    new_yolo_file.write(yolo_label + '\n')

    # Dodawanie nowego elementu do dict
    if filtered_set not in root_wl_dict:
        root_wl_dict[filtered_set] = set()
    root_wl_dict[filtered_set].add(img_file_name)

    # Zapisywanie nowego elementu do zbioru
    filefuncs.override_root_file(root_wl_path, root_wl_dict)

## FUNKCJE ZWIĄZANE Z GUI PRZYJMOWANIA ZDJĘCIA
def get_gui_funcs(yolo_label_list, yolo_label_list_pointer, saved_lp_list, window, count_label, entry):
    # Wyjście z GUI
    def func_quit():
        window.destroy()  

    # Narysowanie granic obiektu YOLO
    def draw_yolo_pointer_rect():
        nonlocal yolo_label_list_pointer, yolo_label_list, count_label
        img = Img_Browser.get_pointed_image()

        imgfuncs.draw_yolo_rect(img, yolo_label_list[yolo_label_list_pointer], (255,0,0))
        count_label.config(text=f'({yolo_label_list_pointer+1} z {len(yolo_label_list)})')

        cv2.imshow(ACCEPT_IMG_WIN_NAME, imgfuncs.resize_image(img, 700))
    
    # Przejście do kolejnego obiektu YOLO w liście
    def increment_yolo_list():
        nonlocal yolo_label_list_pointer, yolo_label_list, entry
        
        #Czyszczenie pola tekstowego
        entry.delete(0, END)
        
        if yolo_label_list_pointer >= len(yolo_label_list) - 1:    
            copy_image_to_set_whitelist(
                COPY_SET_PATH,
                filtered_set=LOAD_SET_PATH,
                img=Img_Browser.get_pointed_image(),
                img_file_name=Img_Browser.get_pointed_image_name(),
                saved_lp_list=saved_lp_list
            )
            func_quit()
        else:
            yolo_label_list_pointer += 1
            draw_yolo_pointer_rect()

    # Wpisanie obiektu YOLO do listy przyjętych
    def append_lp_list():
        nonlocal yolo_label_list_pointer, yolo_label_list, saved_lp_list, entry

        lp_string = entry.get().replace(" ", "")

        new_lp_list_entry = (lp_string, yolo_label_list[yolo_label_list_pointer])
        saved_lp_list.append(new_lp_list_entry)
        print(f'[INFO] Zapisano nową tablice rejestracyjną: {new_lp_list_entry}')

        increment_yolo_list()

    return func_quit, draw_yolo_pointer_rect, increment_yolo_list, append_lp_list

## FUNKCJA GENERUJĄCA GUI AKCEPTOWANIA ZDJĘCIA
def get_img_accept_gui(yolo_label_list, yolo_label_list_pointer, saved_lp_list):
    # Okno
    window = Tk()
    window.title('zapis tablic')
    window.geometry(f'400x150+{int(window.winfo_screenwidth()/2)-200}+{int(window.winfo_screenheight()/2)-75}')
    window.resizable(False,False)

    # Napisy
    Label(window, text='Wprowadź ciąg tablicy rejestracyjnej', font=('Arial', 12)).pack(side=TOP)
    count_label = Label(window, font=('Arial', 9))
    count_label.pack(side=TOP)

    # Pole tekstowe
    entry = Entry()
    entry.config(font=('Arial', 25))
    entry.pack()

    # Przestrzeń na przyciski
    button_frame = Frame(window)
    button_frame.pack(side="bottom", pady=10)

    # Przycisk 'zatwierdz'
    zatwierdz = Button(button_frame, text="zatwierdź")
    zatwierdz.pack(side="left", padx=15)

    # Przycisk 'odrzuc' (Warunkowo, dla zdjęć które mają więcej niż jedna tablica)
    odrzuc = Button(button_frame, text="odrzuc_tablicę")
    odrzuc.pack(side="left", padx=15)

    # Przycisk 'Anuluj Wszystko'
    an_wszytsko = Button(button_frame, text="anuluj wszystko")
    an_wszytsko.pack(side="left", padx=15)

    # FUNKCJE NIEZBĘDNE DLA DZIAŁANIA GUIZKÓW
    func_quit, func_draw_yolo_pointer_rect, func_increment_yolo_list, func_append_lp_list = get_gui_funcs(
        yolo_label_list, yolo_label_list_pointer, saved_lp_list, 
        window, count_label, entry)

    # Przypisanie funkcji do przycisków
    zatwierdz.config(command=func_append_lp_list)
    odrzuc.config(command=func_increment_yolo_list)
    an_wszytsko.config(command=func_quit)

    return window, odrzuc, func_draw_yolo_pointer_rect

## FUNKCJA ROZPOCZYNAJĄCA GUI WGLĄDU NA PRZYJĘCIE ZDJĘCIA
def whitelist_img_in_copy_set():
    yolo_label_list = filefuncs.get_yolo_label_list(
        LOAD_SET_PATH,
        Img_Browser.get_pointed_image_name()
    )
    
    yolo_label_list_pointer = 0
    saved_lp_list = []

    window, odrzuc, func_draw_yolo_pointer_rect = get_img_accept_gui(yolo_label_list, yolo_label_list_pointer, saved_lp_list)

    # Wyłączenie guzika odrzuc, jeśli jest tylko jeden element w liście
    if len(yolo_label_list) < 2:
        odrzuc.config(state=DISABLED)

    # OBOWIĄZKOWE użycie funkcji draw_yolo_pointer_rect, aby narysować pierwszy obiektu YOLO
    func_draw_yolo_pointer_rect()

    # Włączenie GUI
    window.mainloop()
    cv2.destroyWindow(ACCEPT_IMG_WIN_NAME)

# FUNKCJA ZWRACAJĄCA INFORMACJE O KLASYFIKACJI ELEMENTÓW ZBIORU, WZGLĘDEM ZBIORU FILTRUJĄCEGO
def print_load_set_details(load_set_path, copy_set_path):
    set_total_count = len(filefuncs.get_set_image_list(load_set_path))
    set_remain_count = len(Img_Browser.get_image_file_list())
    set_whitelisted_count = 0
    set_blacklisted_count = 0

    root_wl_path = filefuncs.get_root_whitelist_path(copy_set_path)
    root_wl_dict = filefuncs.get_rootfile_as_dict(root_wl_path)

    if load_set_path in root_wl_dict.keys():
        set_whitelisted_count = len(root_wl_dict[load_set_path])

    root_bl_path = filefuncs.get_root_blacklist_path(copy_set_path)
    root_bl_dict = filefuncs.get_rootfile_as_dict(root_bl_path)

    if load_set_path in root_bl_dict.keys():
        set_blacklisted_count = len(root_bl_dict[load_set_path])   

    print("--======= MODYFIKOWANIE ZBIORU =======--\n"
          f"Ścieżka kopii modyfikowanego zbioru: {copy_set_path}\n"
          f"DANE MODYFIKOWANEGO ZBIORU:\n"
          f"->ścieżka: {load_set_path}\n" 
          f"->całkowity rozmiar: {set_total_count}\n"
          f"->elementy niezaklasyfikowane: {set_remain_count}\n"
          f"->elementy przyjęte: {set_whitelisted_count}\n"
          f"->elementy odrzucone: {set_blacklisted_count}\n"
          "--====================================--")

## FUNKCJA SPRAWDZAJĄCA CZY ELEMENT NIE JEST JUŻ ZAPISANY W ZBIORZE DOCELOWYM
def check_if_already_copied(copy_set_path, img_file_name):
    root_wl_path = filefuncs.get_root_whitelist_path(copy_set_path)
    root_wl_dict = filefuncs.get_rootfile_as_dict(root_wl_path)
    for source_path_key, file_set in root_wl_dict.items():
        if img_file_name in file_set:
            print(f'[WARNING] zapisany plik (w whitelist) o podobnej nazwie w :\n źródło:{source_path_key}, nazwa:{img_file_name}')
        
    root_bl_path = filefuncs.get_root_blacklist_path(copy_set_path)
    root_bl_dict = filefuncs.get_rootfile_as_dict(root_bl_path)
    for source_path_key, file_set in root_bl_dict.items():
        if img_file_name in file_set:
            print(f'[WARNING] odrzucony plik (w blacklist) o podobnej nazwie w:\n->źródło:{source_path_key}, nazwa:{img_file_name}')

# Wyświetlenie opcji
def print_help():
    print(
        f'-----===== Możliwe opcje =====-----\n'
        f'\'h\' - wyświetl możliwe opcje\n'
        f'\'ESC\' - wyjście z aplikacji\n'
        f'\'a\' / \'d\' - przemieszczenie się po liście plików\n'
        f'\'k\' - przekopiuj element do docelowego zbioru\n'
        f'\'b\' - odrzuć element z przeglądu'
    )

## METODA WIDODĄCA
def main():
    if not os.path.exists(COPY_SET_PATH):
        filefuncs.create_new_dataset(
            COPY_SET_PATH, 
            create_root_files=True
        )

    print_load_set_details(LOAD_SET_PATH, COPY_SET_PATH)
    print_help()

    run_app = True
    image = []

    def quit_app():
        nonlocal run_app
        cv2.destroyAllWindows()
        run_app = False

    def upload_img_preview():
        nonlocal image
        if len(Img_Browser.get_image_file_list())==0:
            print('[INFO] Zbiór jest pusty lub wszystkie elementy zostały zaklasyfikowane w zbiorze docelowym')
            quit_app()
            return
        
        img_file_name = Img_Browser.get_pointed_image_name()
        yolo_label_list = filefuncs.get_yolo_label_list(
            LOAD_SET_PATH,
            filefuncs.get_img_txt_name(img_file_name) 
        )

        image = Img_Browser.get_pointed_image()
        for yolo_label in yolo_label_list:
            imgfuncs.draw_yolo_rect(image, yolo_label, (0,255,0))
        
        check_if_already_copied(COPY_SET_PATH, img_file_name)
        
    upload_img_preview()
    # PĘTLA APLIKACJI
    while run_app:
        cv2.imshow(MAIN_WINDOW_NAME, imgfuncs.resize_image(image, 700))

        ## FUNKCJE KLAWISZY
        key = cv2.pollKey()

        # Wyświetlenie pomocy
        if key == ord('h'):
            print_help()

        # Wyjście z aplikacji
        if key == ESC_KEY:
            quit_app()
            
        # Przewijanie zdjęć
        if key == ord('d'):
            Img_Browser.increment_file_pointer()
            upload_img_preview()
        if key == ord('a'):
            Img_Browser.decrement_file_pointer()
            upload_img_preview()
            
        # Zapisanie/Odrzucenie zdjęcia
        if key == ord('k') or key == ord('b'):
            cv2.destroyWindow(MAIN_WINDOW_NAME)
            if key == ord('k'):
                whitelist_img_in_copy_set()
            if key == ord('b'):
                append_set_blacklist(
                    COPY_SET_PATH, 
                    LOAD_SET_PATH, 
                    Img_Browser.get_pointed_image_name()
                )

            Img_Browser.set_image_file_list(
                filefuncs.get_filtered_set_image_list(LOAD_SET_PATH, COPY_SET_PATH)
            )
            upload_img_preview()
            
if __name__ == "__main__":
    main()