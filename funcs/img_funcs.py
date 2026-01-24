import cv2

from bbox_utils import BoundingBox

# Funkcja rysująca obiekt yolo
def draw_yolo_rect(img, yolo_label, color):
    H, W = img.shape[:2]
    cx, cy, bw, bh = yolo_label[1:5]
    
    box_bounderies = BoundingBox.from_yolo((cx, cy), bw, bh, (H, W)).to_xyxy()

    xy1 = box_bounderies[0]
    xy2 = box_bounderies[1]

    cv2.rectangle(img, xy1, xy2, color, 2)

# Funkcja zmiany rozmiaru obrazu
def resize_image(img, max_img_size):
    h, w = img.shape[:2]
    scale = max_img_size / max(h, w)

    new_w = int(w * scale)
    new_h = int(h * scale)

    resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    return resized_img

def rescale_img_to_height(img, target_height):
    h, w = img.shape[:2]
    scale = target_height / h

    new_w = int(w*scale)

    resized_img = cv2.resize(img, (new_w, target_height), interpolation=cv2.INTER_AREA)

    return resized_img

def rescale_img_to_height_cap_width(img, target_height, width_cap):
    h, w = img.shape[:2]
    scale = target_height / h

    new_w = int(w*scale)
    if new_w > width_cap:
        new_w = width_cap

    resized_img = cv2.resize(img, (new_w, target_height), interpolation=cv2.INTER_AREA)

    return resized_img