from flask import Flask, request, render_template, redirect, url_for, jsonify
from voc_writer import Writer
import os, shutil
from random import shuffle
from PIL import Image, ImageOps
from math import ceil
from time import time

from ine_detector_utilities.INE_Detector import INE_Detector

app = Flask(__name__)

ine_detector = INE_Detector()

RESIZE_WIDTH = 220
TIME_LIMIT = 5

PATH_DATASET    = './static/assets/dataset/original_dataset'
PATH_PROCCESSED = './static/assets/dataset/processed_dataset'

PATH_MODEL_CREDENTIAL  = './static/assets/dataset/model_credential'
PATH_MODEL_ORIENTATION = './static/assets/dataset/model_orientation'
PATH_MODEL_VERSION     = './static/assets/dataset/model_version'
PATH_MODEL_QUALITY     = './static/assets/dataset/model_quality'

PATH_MODEL_TEMP = './static/assets/dataset/temp_files'


@app.route("/obtener_datos", methods=['GET'])
def get_data_ine():

    image_src = request.args.get('src')
    real_path = PATH_MODEL_TEMP + '/' + image_src.split('/')[-1].split('.')[0] + '.jpg'
    image = Image.open(real_path)

    response = ine_detector.detect_id(image)
    bounding_box = ine_detector.bounding_box

    data = {
        "bounding_box": [int(bounding_box.left), int(bounding_box.top), int(bounding_box.right), int(bounding_box.bottom)],
        "data": response
    }

    return jsonify(datos = data)
    

@app.route("/", methods=['GET'])
def index():
    
    # Escoger imagen del directorio del dataset
    image_name = get_image()

    if image_name != "no_images":

        image_path = PATH_DATASET + '/' + image_name

        jpg_image_path = png_to_jpg(image_path, PATH_MODEL_TEMP, image_name)

    if request.method == 'GET':

        if image_name == "no_images":
            remove_unprocess_temp_files()
            return render_template("noimgs.html")

        count = len(os.listdir(PATH_PROCCESSED))
        total_count = len(os.listdir(PATH_DATASET)) + len(os.listdir(PATH_PROCCESSED))

        return render_template("index.html", img=image_name, count=count, total_count=total_count)
    

@app.route('/process', methods=['POST', 'GET'])
def process_image():

    if request.method == 'GET':
        return show_cat()

    if request.method == 'POST':

        is_credential = True

        print('Desde POST process')

        img_data = request.get_json()

        image_name = img_data['name']

        image_path = PATH_DATASET + '/' + image_name

        xml = Writer(path = image_path, width=img_data['width'], height=img_data['height'])

        xml.addObjectINE(img_data['name'],
                         img_data['width'],
                         img_data['height'],
                         img_data['credential'],
                         img_data['orientation'],
                         img_data['version'],
                         img_data['quality'],
                         img_data['left'],
                         img_data['top'],
                         img_data['right'],
                         img_data['bottom'])
        
        try:
            xml.save('static/assets/xml_files', same_name=True)
        except ValueError:
            pass

        image_post_name = img_data['name'].split('.')[0] + '.jpg'

        abs_path_image = PATH_MODEL_TEMP + '/' + image_post_name

        # resize a la imagen 
        image_jpg = Image.open(abs_path_image)
        resize_image_jpg = resize_image_width(RESIZE_WIDTH, image_jpg)

        # tomar path de la imagen resize jpg para guardar en directorios
        resized_image_name = f'res_{image_post_name}'
        resized_image_path = PATH_MODEL_TEMP + '/' + resized_image_name

        resize_image_jpg.save(resized_image_path)

        credential = img_data['credential']

        if credential == 'reverso':
            image_path_save = PATH_MODEL_CREDENTIAL + '/reverso/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass
        elif credential == 'anverso':
            image_path_save = PATH_MODEL_CREDENTIAL + '/anverso/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass
        else:
            is_credential = False
            image_path_save = PATH_MODEL_CREDENTIAL + '/no/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass

        orientation = img_data['orientation']

        if is_credential:

            print("true en is credencial")

            if orientation == '0':
                
                image_path_save = PATH_MODEL_ORIENTATION + '/0/' + resized_image_name
                try:
                    shutil.copy(resized_image_path, image_path_save)
                except FileNotFoundError:
                    pass
            elif orientation == '1':
                
                image_path_save = PATH_MODEL_ORIENTATION + '/1/' + resized_image_name
                try:
                    shutil.copy(resized_image_path, image_path_save)
                except FileNotFoundError:
                    pass
            elif orientation == '2':
                
                image_path_save = PATH_MODEL_ORIENTATION + '/2/' + resized_image_name
                try:
                    shutil.copy(resized_image_path, image_path_save)
                except FileNotFoundError:
                    pass
            else:
                
                image_path_save = PATH_MODEL_ORIENTATION + '/3/' + resized_image_name
                try:
                    shutil.copy(resized_image_path, image_path_save)
                except FileNotFoundError:
                    pass

        version = img_data['version']

        if version == 'GH' and credential == 'anverso':
            image_path_save = PATH_MODEL_VERSION + '/GH/anverso/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass
        elif version == 'GH' and credential == 'reverso':
            image_path_save = PATH_MODEL_VERSION + '/GH/reverso/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass
        elif version == 'DEF' and credential == 'anverso':
            image_path_save = PATH_MODEL_VERSION + '/DEF/anverso/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass
        elif version == 'DEF' and credential == 'reverso':
            image_path_save = PATH_MODEL_VERSION + '/DEF/reverso/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass
        else: 
            image_path_save = PATH_MODEL_VERSION + '/null/' + resized_image_name
            try:
                shutil.copy(resized_image_path, image_path_save)
            except FileNotFoundError:
                pass 

        quality = img_data['quality']

        if is_credential:

            if quality == 'Buena':
                image_path_save = PATH_MODEL_QUALITY + '/buena/' + resized_image_name
                try:
                    shutil.copy(resized_image_path, image_path_save)
                except FileNotFoundError:
                    pass
            else:
                image_path_save = PATH_MODEL_QUALITY + '/mala/' + resized_image_name
                try:
                    shutil.copy(resized_image_path, image_path_save)
                except FileNotFoundError:
                    pass


        # Borrar imagen de archivos temporales
        if os.path.exists(abs_path_image):
            os.remove(abs_path_image)
            print(f'File removed {abs_path_image}')
        else:
            print(f"File not found {abs_path_image}")


        if os.path.exists(resized_image_path):
            os.remove(resized_image_path)
            print(f"File removed {resized_image_path}")
        else:
            print(f"File not found {resized_image_path}")

        move_png_image_process(image_path, image_name)

        # checamos que archivos no fueron usados y quitamos de temp_files
        remove_unprocess_temp_files()

        return "<h2>Desde post</h2>"
    

def remove_unprocess_temp_files() -> bool:

    is_success = False

    image_temp_list = os.listdir(PATH_MODEL_TEMP)

    for temp_image in image_temp_list:

        image_abs_path = PATH_MODEL_TEMP + '/' + temp_image

        if get_creation_file_time(image_abs_path):
            if os.path.exists(image_abs_path):
                os.remove(image_abs_path)
                is_success = True
            else:
                print("File does not exist")
        
    return is_success


def get_creation_file_time(file:str) -> bool:
    time_limit_seconds = TIME_LIMIT * 60
    time_now = time()

    ctime = os.path.getctime(file)

    if time_now - ctime > time_limit_seconds:
        return True
    
    return False


def move_png_image_process(png_image_path, image_name)-> None:
    
    source = png_image_path
    destination = PATH_PROCCESSED + '/' + image_name

    shutil.move(source, destination)


def get_image() -> str:

    """
    Get image name with extension from original database
    """

    # terminacion png
    image_original_list = os.listdir(PATH_DATASET)
    
    # terminacion jpg
    image_temp_list = os.listdir(PATH_MODEL_TEMP)

    image_original_list = [element.split('.')[0] for element in image_original_list]
    image_temp_list = [element.split('.')[0] for element in image_temp_list]

    image_list = get_real_image_list(image_original_list, image_temp_list)

    if len(image_list) > 0:
        shuffle(image_list)
        return image_list.pop() + '.png'
    
    return "no_images"


def png_to_jpg(image_path: str, save_path: str, image_name: str)-> str:
    """
    Convertir imagen png a jpg, conservando orientacion
    """
    
    complete_image_path = save_path + '/' + image_name.split('.')[0] + '.jpg'

    image_png = Image.open(image_path)
    image_png = ImageOps.exif_transpose(image_png)

    image_rgb = image_png.convert('RGB')
    image_rgb.save(complete_image_path)

    return complete_image_path


def resize_image_width(new_width, image:Image)-> Image:
    
    image_width, image_height = image.size
    new_height = ceil((image_height / image_width) * new_width)
    img_resize = image.resize((new_width, new_height))

    return img_resize


def get_real_image_list(original_list:list, temp_list:list):
    my_list = [elem for elem in original_list if elem not in temp_list]
    return my_list


def show_cat():
    cat = """<pre>
                 /\_____/\ 
                /  o   o  \ 
               ( ==  ^  == ) 
                )         ( 
               (           ) 
              ( (  )   (  ) ) 
             (__(__)___(__)__)</pre>"""

    return cat


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)