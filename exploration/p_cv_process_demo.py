import cv2
import sys
import configparser

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import funcs.lpr_funcs as lpr
import funcs.img_funcs as imgfuncs

#SCIEŻKA
config = configparser.ConfigParser()
config.read('exploration/exploration.config')

IMG_PATH = config.get("CV_PROCESS_DEMO", "img_path")

def main():
    img = cv2.imread(IMG_PATH)
    _, preprocess_steps = lpr.lpr_preprocess(img)

    print('[INFO] Wcisnij ESC aby zakończyć program')
    run_app = True
    while run_app:
        for i in range(0, len(preprocess_steps)):
            cv2.imshow(f'krok_{i}', imgfuncs.resize_image(preprocess_steps[i],300))

        key = cv2.pollKey()

        if key == 27:
            cv2.destroyAllWindows()
            run_app = False

if __name__ == "__main__":
    main()