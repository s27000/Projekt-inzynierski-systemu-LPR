import cv2
import os 

### Klasa prostej przeglądarki zdjęć
# -> przechowuje listę i ścieżkę listy nazwy zdjęc do poglądu (image_dir_path i image_file_list)
# -> wskaźnik wskazuje na element listy na który przeglądarka ma wskazywać (image_file_pointer)
# -> wskaźnik można przesuwać (zmniejszać/zwiększać wartośc) aby przeglądać poprzednie lub następne zdjęcie
class ImageBrowser:
    def __init__(self, image_dir_path, image_file_list):
        self.image_dir_path = image_dir_path
        self.image_file_list = image_file_list
        self.image_file_pointer = 0

    ## FUNKCJE ZWIĄZANE Z WSKAŹNIKIEM LISTY
    # Funkcja zmiany wartości (jeżeli wskaźnik nie wychodzi poza zakres listy)
    # -> zwraca wartość logiczną, jeżeli udało się zaktualizować wartość
    def update_file_pointer(self, val):
        if self.image_file_pointer + val >= len(self.image_file_list) or self.image_file_pointer + val < 0:
            return False
        else:
            self.image_file_pointer += val
            return True

    def increment_file_pointer(self):
        return self.update_file_pointer(1)

    def decrement_file_pointer(self):
        return self.update_file_pointer(-1)
    
    def get_file_pointer(self):
        return self.image_file_pointer

    ## FUNKCJE ZWIĄZANE Z LISTĄ ZDJĘĆ
    # Funkcja związana z aktualizacją zdjęć
    # -> wskaźnik jest aktualizowany do aby nie wychodzić poza zakres nowej listy
    def set_image_file_list(self, image_file_list):
        self.image_file_list = image_file_list
        
        if self.image_file_pointer >= len(image_file_list) and self.image_file_pointer != 0:
            self.update_file_pointer(len(image_file_list)-1)

    def get_image_file_list(self):
        return self.image_file_list

    ## FUNKCJE ZWIĄZANE Z ZWRACANIEM WSKAZYWANEGO ZDJĘCIA
    def get_pointed_image_name(self):
        return self.image_file_list[self.image_file_pointer]

    def get_pointed_image(self):
        image_path = os.path.join(self.image_dir_path, self.get_pointed_image_name())
        image = cv2.imread(image_path)
        
        return image