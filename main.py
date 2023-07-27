from flask import Flask, redirect, render_template, request, url_for
import os, shutil
from random import shuffle
from voc_writer import Writer

app = Flask(__name__)

imgs_in_use = []
count = 0

@app.route("/")
def index():

    global count

    img_list = os.listdir("static/assets/imgs")

    text = request.args.get('button_text')
    path_image = request.args.get('img')

    if text == "No":
        image_name = path_image.split('/')[-1]
    
        try:
            shutil.move('static/assets/imgs/{}'.format(image_name), 'static/assets/wrong_imgs/{}'.format(image_name))
            imgs_in_use.remove(image_name)
        except FileNotFoundError:
            redirect( url_for('index') )
    
    if text == "Si":
        image_name = path_image.split('/')[-1]
        
        try:
            shutil.move('static/assets/imgs/{}'.format(image_name), 'static/assets/correct_imgs/{}'.format(image_name))
            imgs_in_use.remove(image_name)
        except FileNotFoundError:
            redirect( url_for('index') )
        
    if len(img_list) > 0:
    
        shuffle(img_list)
        img = img_list.pop()
        
        if img in imgs_in_use:
            count += 1

            if count >= 15:
                count = 0
                return render_template("noimgs.html")

            return redirect( url_for('index') )

        if len(imgs_in_use) >= 30:
            imgs_in_use.clear()
        
        imgs_in_use.append(img)

        count = 0

        return render_template("index.html", img=img)
    else:
        return render_template("noimgs.html")


@app.route('/lastimg/<type>/<name>')
def last_img(type, name):
    
    path2img = ''
    text = request.args.get('button_text')
    path_image = request.args.get('img')

    if text == "Correcta":
        image_name = path_image.split('/')[-1]

        try:
            shutil.move('static/assets/wrong_imgs/{}'.format(image_name), 'static/assets/correct_imgs/{}'.format(image_name))
        except FileNotFoundError:
            redirect( url_for('index') )

    if text == "Incorrecta":
        image_name = path_image.split('/')[-1]

        redirect( url_for('label_img', name=image_name) )
    

    if type == "Correcta":
        path2img = '/assets/correct_imgs/{}'.format(name)
    elif type == "Incorrecta":
        path2img = '/assets/wrong_imgs/{}'.format(name)
    return render_template('last_img.html', type=type, name=path2img)


@app.route('/label/<name>', methods=['GET', 'POST'])
def label_img(name):

    if request.method == 'POST':
        img_data = request.get_json()

        xml = Writer(path=img_data['name'], width=img_data['width'], height=img_data['height'])
        
        for label in img_data['labels']:
            xml.addObject(label[0], label[1], label[2], label[3], label[4])

        xml.save('static/assets/xml_files', same_name=True)

        try:
            shutil.move('static/assets/correct_imgs/{}'.format(img_data['name']), 'static/assets/wrong_imgs/{}'.format(img_data['name']))
        except:
           pass

        return redirect( url_for('index'))

    if request.method == 'GET':

        real_name = f"{name}.jpg"
        
        return render_template("label_img.html", img=real_name)

    
    img_list = os.listdir('static/assets/img_wo_label')

    if len(img_list) > 0:
        shuffle(img_list)
        img = img_list.pop()
        
    return render_template('label_img.html', img=img)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)