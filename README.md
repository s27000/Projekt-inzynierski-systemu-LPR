# Projekt-inzynierski-systemu-LPR
__Autor__: Adam Bartkiewicz

__Nr Albumu:__ s27000

__Uczelnia:__ Polsko-Japońska Akademia Technik Komputerowych

__Tytuł pracy inżynierskiej:__ "Rozpoznawanie tablic rejestracyjnych pojazdów za pomocą sztucznej inteligencji"

Wydział Informatyki, Katedra Systemów Inteligentnych i Data Science

## Streszczenie projektu
Repozytorium przechowuje obszar roboczy części praktycznej pracy dyplomowej. Celem części praktycznej pracy było zrealizowaniem systemy LPR, w oparciu o algorytmy sztucznej intelgencji. Repozytorium Zawiera popronowaną implementację systemu LPR, wykorzystująca przygotowane algorytmy oraz modele znajdujących się w innych bibliotekach. Zawiera programy które były wykorzystywane do utworzenia tego systemu oraz takie które sprawdzały jego działanie oraz skuteczność. Zawiera również zbiór danych pobrany z źródła, oraz jego iteracje które zostały przygotowane na potrzebę realizacji celu badawczego. Opis kluczowych elementów repozytorium znajduje się poniżej, pod nagłówkiem struktury projektu.

## Źródło zbioru danych:
Roboflow Universe

__License Plate Recognition Computer Vision Model__

https://universe.roboflow.com/roboflow-universe-projects/license-plate-recognition-rxg4e

_Zbiór został pobrany i znajduje się w katalogu CLP_roboflow_

## Przygotowanie środowiska
Aby uruchomić projekt, należy przygotować środowisko wirtualne języka python w wersji 3.13.5

Więcej szczegółów na ten temat: https://docs.python.org/3/library/venv.html

Listy pakietów wymaganych do działania projektu:
- _requirements-cpu.txt_ - Dla środowiska, w którym modelowanie YOLO jest oparte na procesorze
- _requirements-gpu-first.txt_ - Pierwsza część środowiska, w którym modelowanie YOLO jest oparte na karcie graficznej
- _requirements-gpu-second.txt_ - Druga część środowiska, w którym modelowanie YOLO jest oparte na karcie graficznej

__UWAGA!__ środowisko GPU jest dostowane pod konkretną architekturę komputera. Może nie działać dla wszystkich urządzeń.
```
# Tworzenie wirtualnego środowiska (CPU)
py -3.13 -m venv .venv-cpu
.venv-gpu/Scripts/activate
pip install -r requirements-cpu.txt

# Tworzenie wirtualnego środowiska (GPU)
py -3.13 -m venv .venv-gpu
.venv-gpu/Scripts/activate
pip install -r requirements-gpu-first.txt
pip install -r requirements-gpu-second.txt

## Ważne! W przypadku środowiska GPU kolejność stosowania plików requirements jest istotna, i nie wolno jej zmieniać.
```

## Struktury projektu
```
.
├── data                    # KATALOG ZBIORÓW
│   ├── prepared                # PODKATALOG ZBIORÓW PRZECZYSZCZONYCH/PRZYGOTOWANYCH
│   │   └── rbf_cleaned_merged        # Przeczyszczony wariant zbioru danych pobranego z źródła
│   │ 
|   ├── raw                     # PODKATALOG ZBIORÓW NIEZMIENONYCH
│   │   └── CLP_roboflow              # Zbiór pobrany z repozytorium Roboflow
│   │
|   ├── split                   # PODKATALOG ZBIORÓW BADAWCZYCH
│   │
|   └── test                    # PODKATALOG ZBIORÓW TESTOWYCH
│       ├── test_1                    # Zbiór testowy
│       ├── test_1_1                  # Podzbiór zbioru testowego 1
│       └── test_2                    # Zbiór testowy 2
|
├── exploration                 # MODUŁ PRZEGLĄDANIA ROZWIĄZAŃ I MODFYKOWANIA ZBIORU DANYCH
│   ├── exploration.config            # Plik ustawień programów katalogu 'exploration'
│   ├── p_cv_operations_examples.py   
│   ├── p_cv_process_demo.py
│   ├── p_cv_dataset_modifier.py      
│   └── p_split_dataset.py            # Program generujący podzbiory badawcze
│
├── main_app.config
├── main_app.py
│
├── requirements-cpu.txt              # Lista pakietów dla środowiska CPU
├── requirements-gpu-first.txt        # Pierwsza część listy pakietów dla środowiska CPU
├── requirements-gpu-second.txt       # Druga część listy pakietów dla środowiska CPU
│
├── yolo11n.pt
├── yolo8n.pt
└── yolo8s.pt
```
