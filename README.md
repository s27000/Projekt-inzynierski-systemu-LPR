# Projekt-inzynierski-systemu-LPR
__Autor__: Adam Bartkiewicz

__Nr Albumu:__ s27000

__Uczelnia:__ Polsko-Japońska Akademia Technik Komputerowych

__Tytuł pracy inżynierskiej:__ "Rozpoznawanie tablic rejestracyjnych pojazdów za pomocą sztucznej inteligencji"

Wydział Informatyki, Katedra Systemów Inteligentnych i Data Science

## Wstęp do projektu

## Opis elementów projektu
### Przygotowanie środowiska
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
### Moduły
Programy stosowane w badaniach lub wykorzystujące funkcje systemu LPR, zostały podzielone na moduły. Każdy z modułów ma swój wyznaczony katalog.

__exploration__: przygotowanie rozwiązania oraz działania na zbiorze danych
- __exploration.config__: plik ustawień dla wszystkich programów w module
- __p_split_dataset.py__: program generujący 5 zbiorów badawczych. Aby program zadziałał prawidłowo, należy przygotować
katalog zawierający podkatalog 'images' (z zdjęciami), 'labels' (z obiektami yolo) oraz 'details (dodatkowe szczegóły obiektów yolo). Program tworzy 5 wymieszanych zbiorów badawczych, z 3 podzbiorami: train, valid i test. Wymieszanie elementów zbiorów badawczych opiera się na sekwencyjnym podziale elementów pierwotnego zbioru. Ścieżka do zbioru z którego program ma wytworzyć zbiory badawcze należy ustawić w exploration.config. W tym samym miejscu należy zdefinować ścieżkę katalog, w którym zbiory mają zostać wygenerowane.

## Struktura projektu
```
.
├── data
│   ├── prepared
│   │   └── rbf_cleaned_merged
|   ├── raw
│   │   └── CLP_roboflow
│   
├── exploration
│   ├── exploration.config
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
