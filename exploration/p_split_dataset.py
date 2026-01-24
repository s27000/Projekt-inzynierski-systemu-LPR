import os 
import sys
import shutil
import configparser

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import funcs.file_funcs as filefuncs

## SCIEŻKI
config = configparser.ConfigParser()
config.read('exploration/exploration.config')

LOAD_SET_PATH = config.get("SPLIT_DATASET", "load_set_path")
SPLIT_SET_DIR_PATH = config.get("SPLIT_DATASET", "split_set_dir_path")

## Funkcja rozdzielająca zbiór na podzbiór treningowy, testowy, validacyjny
# -> elementy są dzielone w stosunku 7/1/2 (train/test/valid)
# -> funkcja dzieli zbiór sekwencyjnie co 10 elementów 
# -> parametry n_dig, odpowiadają za co który element w sekwencji należy do danego zbioru 
# (np. co test_dig element należy do zbioru testowego)
def balance_split_set(img_list, test_dig, val_dig_1, val_dig_2):
    train_img_file_list = []
    test_img_file_list = []
    valid_img_file_list = []

    for i in range(0, len(img_list)):
        if i % 10 == test_dig:
            test_img_file_list.append(img_list[i])
        elif i % 10 == val_dig_1 or i % 10 == val_dig_2:
            valid_img_file_list.append(img_list[i])
        else:
            train_img_file_list.append(img_list[i])

    return train_img_file_list, test_img_file_list, valid_img_file_list

## FUNKCJA TWORZĄCA PLIK .YAML DLA ZBIORU
def create_yaml_file(set_dir):
    content = (
        "train: ../train/images\n"
        "val: ../valid/images\n"
        "test: ../test/images\n\n"
        "nc: 1\n"
        "names: ['License_Plate']"
    )

    yaml_path = filefuncs.get_yaml_path(set_dir)
    with open(yaml_path, "w", encoding="utf-8") as yaml_file:
        yaml_file.write(content)

## FUNKCJA TWORZĄCA NOWY WYDZIELONY 
def split_ds(test_dig, val_dig_1, val_dig_2):
    #Zbieranie nazwy elementów (zdjęć) zbioru macierzystego
    #-> dzielenie go na podzbioru train_list, test_list, valid_list 
    train_list, test_list, valid_list = balance_split_set(
        filefuncs.get_set_image_list(LOAD_SET_PATH), 
        test_dig, 
        val_dig_1, 
        val_dig_2
    )

    load_set_img_path = filefuncs.get_img_dir_path(LOAD_SET_PATH)
    load_set_label_path = filefuncs.get_yolo_label_dir_path(LOAD_SET_PATH)
    load_set_detail_path = filefuncs.get_details_dir_path(LOAD_SET_PATH)

    subset_map = {
        'train':train_list,
        'test':test_list,
        'valid':valid_list
    }

    # Tworzenie nowego katalogu zbioru wydzielonego
    split_set_count = len(os.listdir(SPLIT_SET_DIR_PATH))
    new_split_set_name = f'dataset_{(split_set_count+1):02d}'
    new_split_set_dir_path = os.path.join(SPLIT_SET_DIR_PATH, new_split_set_name)
    os.mkdir(new_split_set_dir_path)

    # Kopowianie elementów podzbiorów do podkatalogów zbioru wydzielonego  
    for subset in subset_map.keys():
        subset_path = os.path.join(new_split_set_dir_path, subset)

        split_set_img_path = filefuncs.get_img_dir_path(subset_path)#os.path.join(subset_path, r'images')
        split_set_yolo_path = filefuncs.get_yolo_label_dir_path(subset_path)#os.path.join(subset_path, r'labels')
        split_set_details_path = filefuncs.get_details_dir_path(subset_path)#os.path.join(subset_path, r'details')
        
        filefuncs.create_new_dataset(
            subset_path, 
            create_root_files=False
        )
        
        img_name_file_list = subset_map[subset]

        for img_name in img_name_file_list:
            img_txt_name = filefuncs.get_img_txt_name(img_name)
            
            shutil.copy(os.path.join(load_set_img_path, img_name), os.path.join(split_set_img_path, img_name))
            shutil.copy(os.path.join(load_set_label_path, img_txt_name), os.path.join(split_set_yolo_path, img_txt_name))
            shutil.copy(os.path.join(load_set_detail_path, img_txt_name), os.path.join(split_set_details_path, img_txt_name))

    # TWORZENIE NIEZBĘDNEGO PLIKU .yaml
    create_yaml_file(new_split_set_dir_path)

    print(
        f'--==== NOWY WYDZIELONY ZBIÓR ====--\n'
        f'Zbiór macierzysty: {LOAD_SET_PATH}\n'
        f'->elementy treningowe: {len(train_list)}\n'
        f'->elementy testowe: {len(test_list)}\n'
        f'->elementy walidacyjne: {len(valid_list)}\n'
        f'Nazwa nowego podzbioru: {new_split_set_name}\n'
        f'--===============================--'
    )

# FUNKCJA WIODĄCA
def main():
    split_ds(2,3,7)
    split_ds(5,2,9)
    split_ds(1,0,8)
    split_ds(3,1,5)
    split_ds(7,4,6)
    
if __name__ == '__main__':
    main()