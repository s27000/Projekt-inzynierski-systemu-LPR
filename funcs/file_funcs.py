import os 

## FUNKCJE ZWRACAJĄCE PODKATALOGI/PLIKI ŚCIEŻEK ZBIORU
def get_img_dir_path(set_path):
    return os.path.join(set_path, r'images')

def get_yolo_label_dir_path(set_path):
    return os.path.join(set_path, r'labels')

def get_details_dir_path(set_path):
    return os.path.join(set_path, r'details')

def get_root_whitelist_path(set_path):
    return os.path.join(set_path, r'root_whitelist.txt')

def get_root_blacklist_path(set_path):
    return os.path.join(set_path, r'root_blacklist.txt')

def get_yaml_path(set_path):
    return os.path.join(set_path, r'data.yaml')

## FUNKCJE ZWIĄZANE Z LISTOWANIEM KATALOGU ZDJĘĆ
def get_set_image_list(set_path):
    img_dir_path = get_img_dir_path(set_path)
    img_file_list = os.listdir(img_dir_path)

    return sorted(img_file_list)

def get_filtered_set_image_list(set_path, filtering_set_path):
    img_file_set = set(get_set_image_list(set_path))

    if os.path.exists(filtering_set_path):
        root_wl_path = get_root_whitelist_path(filtering_set_path)
        root_wl_dict = get_rootfile_as_dict(root_wl_path)
        if set_path in root_wl_dict:
            root_wl = root_wl_dict[set_path]
            img_file_set -= root_wl

        root_bl_path = get_root_blacklist_path(filtering_set_path)
        root_bl_dict = get_rootfile_as_dict(root_bl_path)
        if set_path in root_bl_dict:
            root_bl = root_bl_dict[set_path]
            img_file_set -= root_bl
    else:
        print(f'[WARNING] could not filter {set_path}, as {filtering_set_path} does not exist')

    img_file_list = sorted(img_file_set)

    return img_file_list

## FUNKCJE ZWIĄZANE Z PLIKAMI LISTOWYMI W ZBIORZE DOCELOWYM
def get_rootfile_as_dict(root_path):
    root_dict = {}
    with open(root_path, 'r') as root_wl:
        source_key = None
        for line in root_wl:
            line = line.rstrip()
            if not line:
                continue

            if not line.startswith('\t'):
                source_key = line
                root_dict[source_key] = set()

            elif line.startswith('\t') and source_key:
                line = line.strip()
                root_dict[source_key].add(line)

    return root_dict

def override_root_file(root_file_path, root_dict):
    with open(root_file_path, 'w') as root_file:
        for source_path, img_file_list in root_dict.items():
            root_file.write(f"{source_path}\n")
            for img_file in img_file_list:
                root_file.write(f"\t{img_file}\n")

## FUNKCJE ZWIĄZANE Z SZCZEGÓŁAMI PLIKÓW 
# Funkcja podmieniająca nazwę pliku z typu '.jpg' na '.txt'   
def get_img_txt_name(img_file_name):
    image_name_split = img_file_name.split(sep='.')
    image_name_split.pop()
    img_txt_name = '.'.join(image_name_split) + '.txt'

    return img_txt_name

# Funkcja zwraca listę obiektów yolo
def get_yolo_label_list(set_path, img_file_name):
    yolo_labels_path = get_yolo_label_dir_path(set_path)
    #Podmiana nazwy pliku z typu '.jpg' na '.txt'
    img_txt_name = get_img_txt_name(img_file_name)

    #Pełna ścieżka do pliku z obiektami YOLO
    yolo_label_file_path = os.path.join(yolo_labels_path, img_txt_name)

    yolo_label_list = []
    with open(yolo_label_file_path, 'r') as yolo_file:
        for line in yolo_file.read().splitlines():
            line_vals = line.split(sep=' ')
            cls, cx, cy, bw, bh = map(float, line_vals[0:5])
            cls = int(cls)
            yolo_label_list.append([cls, cx, cy, bw, bh])

    return yolo_label_list

# Funkcja zwracająca plik z listą zapisanych tablic rejestracyjnych.
def get_file_details(set_path, img_file_name):
    details_path = get_details_dir_path(set_path)
    img_txt_name = get_img_txt_name(img_file_name)

    details_file_path = os.path.join(details_path, img_txt_name)

    details_list = []
    with open(details_file_path, 'r') as details_file:
        for line in details_file.read().splitlines():
            details_list.append(line)
    
    return details_list

## FUNCKJA TWORZĄCA NOWY ZBIÓR DOCELOWY/ZAPISU
def create_new_dataset(copy_set_path, create_root_files):#, sv_img_path, sv_yolo_label_path, sv_detail_path, root_wl_path, root_bl_path):
    os.mkdir(copy_set_path)
    
    os.mkdir(
        get_img_dir_path(copy_set_path)
        #sv_img_path
    )
    os.mkdir(
        get_yolo_label_dir_path(copy_set_path)
        #sv_yolo_label_path
    )
    os.mkdir(
        get_details_dir_path(copy_set_path)
        #sv_detail_path
    )

    if create_root_files:
        root_bl_path = get_root_blacklist_path(copy_set_path)
        root_wl_path = get_root_whitelist_path(copy_set_path)

        open(root_wl_path, "a").close()
        open(root_bl_path, "a").close()
    '''
    if create_root_wl:
        open(root_wl_path, "a").close()
    if create_root_bl:
        open(root_bl_path, "a").close()
    '''

    print(f"[INFO] Stworzono nowy zbiór pod ścieżką: \'{copy_set_path}\'")