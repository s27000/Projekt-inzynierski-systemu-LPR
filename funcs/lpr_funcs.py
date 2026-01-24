import cv2
import numpy as np
import re 
import time 

from paddleocr import PaddleOCR
from ultralytics import YOLO

import funcs.img_funcs as imgfuncs

# FUNKCJA ZWRACAJĄCA MODELE
def get_models(detect_model_path):
    detect_model = YOLO(detect_model_path)

    print(f'[INFO] Ścieżka modelu wykrywania: {detect_model_path}')

    read_model = PaddleOCR(
        lang="en",
        use_angle_cls=True
    )

    return detect_model, read_model

# FUNKCJA WYKRYWANIA TABLIC REJESTRACYJNYCH NA ZDJĘCIU
def lpr_detect(img, detect_model):
    plate_crop_list = []
    results = detect_model(img, conf=0.3, verbose=False)
    for r in results:
        for predict_bounds in r.boxes:
            x1, y1, x2, y2 = predict_bounds.xyxy[0].cpu().numpy().astype(int)

            plate_crop = img[y1:y2, x1:x2].copy()
            plate_crop_list.append(plate_crop)

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return plate_crop_list

# FUNKCJA PRZETWARZAJĄCA ZDJĘCIE
def lpr_preprocess(img):
    preprocess_steps = []

    resized_img = imgfuncs.rescale_img_to_height(img,100)
    preprocess_steps.append(resized_img)

    gray_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
    preprocess_steps.append(gray_img)

    blurred_img = cv2.GaussianBlur(gray_img,(5,5),0)
    preprocess_steps.append(blurred_img)

    _, mask_th = cv2.threshold(blurred_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    preprocess_steps.append(mask_th)

    kernel_1 = np.ones((5, 5), np.uint8)

    mask_morph_close = cv2.morphologyEx(mask_th, cv2.MORPH_CLOSE, kernel_1, iterations=1)
    preprocess_steps.append(mask_morph_close)

    mask_dilate = cv2.dilate(mask_morph_close, kernel_1, iterations=1)
    preprocess_steps.append(mask_dilate)

    kernel_2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

    mask_morph_open = cv2.morphologyEx(mask_dilate, cv2.MORPH_OPEN, kernel_2, iterations=1)
    preprocess_steps.append(mask_morph_open)

    bitwise_and = cv2.bitwise_and(gray_img, gray_img, mask=mask_morph_open)
    preprocess_steps.append(bitwise_and)

    processed_img = cv2.cvtColor(bitwise_and, cv2.COLOR_GRAY2BGR)

    return processed_img, preprocess_steps

# FUNKCJA ODCZYTYWANIA TABLICY
def lpr_read(img, reader):
    ocr_out = reader.predict(img)

    raw_text = "".join(ocr_out[0]['rec_texts'])
    allowed_chars = re.compile(r"[^A-Z0-9]")

    plate_read = raw_text.upper()
    plate_read = allowed_chars.sub("", plate_read)

    return plate_read

# FUNKCJA WYKRYWAJĄCA I ODCZYTUJĄCA TABLICY REJESTRACYJNE Z ZDJĘCIA
def lpr_detect_and_read(img, detect_model, read_model):
    lpr_start = time.time()
    #ELEMENT WYKRYCIA TABLIC NA ZDJĘCIU
    plate_crop_list = lpr_detect(img, detect_model)
    plate_reading_list = []

    # Dla każdej wykrytej tablicy...
    for plate in plate_crop_list:
        # ELEMENT PRZETWORZENIA ZDJĘCIA
        preprocessed_plate, _ = lpr_preprocess(plate)
        # ELEMENT ODCZYTANIA TABLICY
        plate_read = lpr_read(preprocessed_plate, read_model)

        # ZAPISANIE PRZETWORZONEGO ZDJĘCIA ORAZ ODCZYTANEGO CIĄGU ZNAKÓW
        plate_reading_entry = {"plate_read": plate_read,"plate_img": preprocessed_plate}
        plate_reading_list.append(plate_reading_entry)
    
    lpr_end = time.time()
    lpr_total_time = float((f'{(lpr_end - lpr_start):.2f}'))
    
    return plate_reading_list, lpr_total_time
    
