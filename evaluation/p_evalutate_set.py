import os
import cv2
import sys
import time
import configparser
import json

from datetime import datetime
from ultralytics import YOLO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import funcs.file_funcs as filefuncs
import funcs.img_funcs as imgfuncs
import funcs.lpr_funcs as lpr

## SCIEŻKI
config = configparser.ConfigParser()
config.read('evaluation/evaluation.config')

DETECT_MODEL_PATH = config.get("EVALUATION", "detect_model_path")
TEST_SET_PATH = config.get("EVALUATION", "test_set_path")
RESULTS_LOG_PATH = config.get("EVALUATION", "results_log_path")
GENERATE_LOG = config.getboolean("EVALUATION", 'generate_log')
ENABLE_PREVIEW = config.getboolean("EVALUATION", 'enable_preview')
PREVIEW_ONLY_WRONG = config.getboolean("EVALUATION", 'preview_only_wrong')

def evaluate_img(read_list, true_read_list):
    read_set = set(read_list)
    true_read_set = set(true_read_list)

    if read_set == true_read_set:
        return 1
    else:
        return 0
    
def evaluate_plate(plate_string, true_read_list):
    true_read_set = set(true_read_list)
    if plate_string in true_read_set:
        return 1
    else:
        return 0

# FUNKCJA EWALUJĄCA ZBIÓR ZDJĘĆ
def evaluate_set(val_set_dir, detect_model_path):
    # Załadownie listy oraz modelu
    valid_img_file_list = filefuncs.get_set_image_list(val_set_dir)

    detect_model, read_model = lpr.get_models(detect_model_path)
    detect_model = YOLO(detect_model_path)

    print(f'[INFO] Ewaluacja programu na zbiorze \'{val_set_dir}\'')

    # Załadowanie wartości i licznikiów
    val_img_count = len(valid_img_file_list)
    correct_plate_count = 0
    total_det_plates_count = 0
    correct_img_count = 0
    update_threshold = 1 if int(val_img_count * 0.1) == 0 else int(val_img_count * 0.1)

    # Wyniki zdjęć
    img_results_list = []

    total_time_start = time.time()
    sum_lpr_time = 0

    # PĘTLA PRZECHODZĄCA PRZEZ KAŻDY ELEMENTY ZBIORU WALIDACYJNEGO
    for i in range(0, val_img_count):
        # Status informujący ile zbioru zostało sprawdzone
        if i % update_threshold == 0 and i != 0:
            elapsed_time_end = time.time()
            elapsed_time = elapsed_time_end - total_time_start
            elapsed_time_mm_ss = f'{int((elapsed_time)/60)}:{int((elapsed_time)%60):02d}'
            print(f'[STATUS] {round(i/val_img_count*100)}% zbioru sprawdzone | CZAS: {elapsed_time:.2f}s ({elapsed_time_mm_ss}|MM:SS)')

        # Przygotowanie zdjęcia i elementu walidacyjnego
        img_file_name = valid_img_file_list[i]
        img_dir_path = filefuncs.get_img_dir_path(val_set_dir)
        img_path = os.path.join(img_dir_path, img_file_name)
        img_true_read_list = filefuncs.get_file_details(val_set_dir, img_file_name)
        
        img = cv2.imread(img_path)

        plate_reading_list, lpr_total_time = lpr.lpr_detect_and_read(
            img, 
            detect_model=detect_model,
            read_model=read_model
        )
        
        sum_lpr_time += lpr_total_time

        readings_list = [x['plate_read'] for x in plate_reading_list]

        # Ewaluacja odczytanych tablic
        plate_evaluation_count = 0
        for plate in readings_list:
            plate_evaluation_count += evaluate_plate(plate, img_true_read_list)

        total_det_plates_count += len(plate_reading_list)
        correct_plate_count += plate_evaluation_count

        # Ewaluacja zdjęcia
        evaluation = evaluate_img(readings_list, img_true_read_list)
        correct_img_count += evaluation

        result_dict = {'image_file_name':img_file_name,
                       'image':img,
                       'plate_reading_list':plate_reading_list,
                       'true_read_list':img_true_read_list,
                       'time_elapsed':lpr_total_time,
                       'evaluation':evaluation}
        img_results_list.append(result_dict)

    # Zapisanie wyników
    total_time_end = time.time()
    total_time = total_time_end - total_time_start
    total_time_mm_ss = f'{int((total_time)/60)}:{int((total_time)%60):02d}'
    
    img_read_accuracy = correct_img_count/val_img_count
    plate_read_accuracy = correct_plate_count/total_det_plates_count
    avg_img_read_time = sum_lpr_time/val_img_count

    results_log = {
        'sciezka_modelu:':f'{detect_model_path}',
        'zbior_walidacyjny':f'{val_set_dir}',
        'dokladnosc_odczytu_zdjec':f'{img_read_accuracy:.3f}',
        'dokladnosc_odczytu_tablic':f'{plate_read_accuracy:.3f}',
        'sredni_czas_odczytu_zdjecia':f'{avg_img_read_time:.2f}s',
        'calkowity_czas_ewaluacji':f'{total_time:.2f}s'
    }

    print(
        f'-= WYNIKI EWALUACJI =-\n'
        f'-ewaluacja zdjęć: {correct_img_count} / {val_img_count} | {round(img_read_accuracy*100)}%\n'
        f'-ewaluacja tablic: {correct_plate_count} / {total_det_plates_count} | {round(plate_read_accuracy*100)}%\n'
        f'-całkowity czas ewaluacji: {total_time:.2f}s | {total_time_mm_ss} (MM:SS)\n'
        f'-średni czas ewaluacji zdjęcia: {avg_img_read_time:.2f}s'
    )
    
    return img_results_list, results_log

# FUNKCJA TWORZĄCA PLIK Z WYNIKAMI
def create_results_log(results_log_path, results_log_content):
    now = datetime.now()
    time_stamp = now.strftime("%Y%m%d_%H%M%S%f")[:-3]
    log_file_name = f'results_log_{time_stamp}.json'

    results_log_file_path = os.path.join(results_log_path, log_file_name)

    with open(results_log_file_path, 'w') as results_file:
        json.dump(results_log_content, results_file, indent=4)
        print(f'[INFO] Zapisano wyniki do \'{results_log_file_path}\'')

def main():
    #_, results_log = evaluate_set(TEST_SET_PATH, DETECT_MODEL_PATH)
    _, results_log = evaluate_set(TEST_SET_PATH, DETECT_MODEL_PATH)

    if GENERATE_LOG:
        create_results_log(RESULTS_LOG_PATH, results_log)

    _, results_log = evaluate_set(r'data/split/dataset_03/test', r'runs/detect/yolo_dataset_03/weights/best.pt')

    if GENERATE_LOG:
        create_results_log(RESULTS_LOG_PATH, results_log)

    _, results_log = evaluate_set(r'data/split/dataset_04/test', r'runs/detect/yolo_dataset_04/weights/best.pt')

    if GENERATE_LOG:
        create_results_log(RESULTS_LOG_PATH, results_log)

    _, results_log = evaluate_set(r'data/split/dataset_05/test', r'runs/detect/yolo_dataset_05/weights/best.pt')

    if GENERATE_LOG:
        create_results_log(RESULTS_LOG_PATH, results_log)
    

# Wyświetlenie opcji
def print_help():
    print(
        f'-----===== Możliwe opcje =====-----\n'
        f'\'h\' - wyświetl możliwe opcje\n'
        f'\'ESC\' - wyjście z aplikacji\n'
        f'\'a\' / \'d\' - przemieszczenie się po liście plików'
    )

def main_w_preview():
    img_results_list, results_log = evaluate_set(TEST_SET_PATH, DETECT_MODEL_PATH)

    if GENERATE_LOG:
        create_results_log(RESULTS_LOG_PATH, results_log)

    if PREVIEW_ONLY_WRONG:
        for i in range(len(img_results_list) - 1, -1, -1):
            if img_results_list[i]['evaluation'] == 1:
                img_results_list.pop(i)
    
    if len(img_results_list) == 0:
        print(f'[WARNING] Lista wyników jest pusta')
        return

    results_list_pointer = 0
    image = None

    def load_image():
        nonlocal image
        cv2.destroyAllWindows()

        results_dict = img_results_list[results_list_pointer]
        image = results_dict['image']
        plate_reading_list = results_dict['plate_reading_list']

        for i in range(0, len(plate_reading_list)):
            plate_img = plate_reading_list[i]['plate_img']
            plate_img = imgfuncs.resize_image(plate_img, 300)

            cv2.putText(
                plate_img, plate_reading_list[i]['plate_read'] or "?",
                (5, 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.3, (0, 0, 0), 2, cv2.LINE_AA
            )
            cv2.putText(
                plate_img, plate_reading_list[i]['plate_read'] or "?",
                (5, 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.3, (0, 255, 0), 1, cv2.LINE_AA
            )

            cv2.imshow(f'plate_{i}', plate_img)#imgfuncs.rescale_img_to_height(plate_reading_list[i],150))
            
        evalution_char = '✅' if results_dict['evaluation'] == 1 else '❌'
        print(
            f'[INFO] Podgląd zdjęcia: {results_dict['image_file_name']} {evalution_char}\n'
            f'\t> odczytane wartości: {[x['plate_read'] for x in plate_reading_list]}\n'
            f'\t> prawdziwe wartości: {results_dict['true_read_list']}'
        )
        cv2.imshow("obraz", imgfuncs.resize_image(image, 600))

    def update_pointer(val):
        nonlocal results_list_pointer
        if not (results_list_pointer + val >= len(img_results_list)) and not (results_list_pointer + val < 0):
            results_list_pointer += val

    load_image()

    while True:
        key = cv2.waitKey()

        if key == 27:
            cv2.destroyAllWindows()
            break

        # Wyświetlenie pomocy
        if key == ord('h'):
            print_help()

        if key == ord('d'):
            update_pointer(1)
            load_image()

        if key == ord('a'):
            update_pointer(-1)
            load_image()

if __name__ == "__main__":
    if ENABLE_PREVIEW:
        main_w_preview()
    else:
        main()
