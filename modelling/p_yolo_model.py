import configparser
import sys
import torch

from ultralytics import YOLO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ŚCIEZKI
config = configparser.ConfigParser()
config.read('modelling/modelling.config')

DATA_CONFIG_PATH = config.get("YOLO_MODEL", "data_config_path")
NAME = config.get("YOLO_MODEL", "name")
# PARAMETRY MODELU YOLO
EPOCHS = int(config.get("YOLO_MODEL", "epochs"))
IMAGE_SIZE = int(config.get("YOLO_MODEL", "image_size"))
BATCH = int(config.get("YOLO_MODEL", "batch"))
WORKERS = int(config.get("YOLO_MODEL", "workers"))
PATIENCE = int(config.get("YOLO_MODEL", "patience"))

if torch.cuda.is_available():
    DEVICE = int(config.get("YOLO_MODEL", "device"))
else:
    DEVICE = 'cpu'

def train_yolo_model(data, name):
    model = YOLO("yolov8s.pt")

    model.train(
        data=data,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH,
        device=DEVICE,
        workers=WORKERS,
        patience=PATIENCE,
        cos_lr=True,
        amp=True,
        name=name
    )

def main():
    train_yolo_model(DATA_CONFIG_PATH, NAME)

if  __name__ == "__main__":
    main()
