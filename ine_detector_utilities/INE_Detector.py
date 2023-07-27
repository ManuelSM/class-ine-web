from PIL import ImageChops
import tensorflow as tf
import numpy as np
from pyzbar import pyzbar 
from urllib.parse import urlparse
import cv2

from ine_detector_utilities.image_utils import preProcessTF, non_max_suppression, detect_faces
from ine_detector_utilities.Rect import Rect
from ine_detector_utilities.INE_Detection import INE_Detection

class INE_Detector:

    MODEL_PATH = './ine_detector_utilities/model/ids.tflite'

    def __init__(self, min_size_pct:float = 0.7, min_quality:float = 10.0, min_color_distance:float = 20.0, allow_copy:bool = False) -> None:

        self.min_size_pct = min_size_pct 
        self.min_quality = min_quality
        self.min_color_distance = min_color_distance
        self.allow_copy = allow_copy

        self.bounding_box = None

        # Carga el modelo TFLite
        self.interpreter = tf.lite.Interpreter(model_path=self.MODEL_PATH)
        self.interpreter.allocate_tensors()

        # Obtiene los detalles del modelo
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        #print("Input", input_details)
        #print("Output", output_details)

        self.labels = ["front_id", "back_id", "passport"]


    def detect_id(self, image):
        self.image = image
        input_data = preProcessTF(self.image, 320)

        # Asigna los datos de entrada al intérprete
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)

        # Ejecuta la inferencia
        self.interpreter.invoke()

        output_index1 = 600 #scores
        output_index2 = 598 #bounding_boxes
        output_index3 = 601 #???
        output_index4 = 599 #Classes

        scores = self.interpreter.get_tensor(output_index1)[0]
        boxes = self.interpreter.get_tensor(output_index2)[0]
        #output_data3 = self.interpreter.get_tensor(output_index3)[0]
        classes = self.interpreter.get_tensor(output_index4)[0]

        confidence_threshold = 0.1
        
        valid_scores = [scores[i] for i in range(len(scores)) if scores[i] > confidence_threshold]
        valid_boxes = [boxes[i] for i in range(len(scores)) if scores[i] > confidence_threshold]
        valid_classes = [classes[i] for i in range(len(scores)) if scores[i] > confidence_threshold]

        #Escala los bounding Boxes
        for i in range(len(valid_boxes)):
            ymin, xmin, ymax, xmax = valid_boxes[i]
            width, height = self.image.size
            x_min = int(xmin * width)
            x_max = int(xmax * width)
            y_min = int(ymin * height)
            y_max = int(ymax * height)

            if x_min<0:
                x_min = 1
            
            if y_min<0:
                y_min = 1
            
            if x_max>width:
                x_max = width-2
            
            if y_max>height:
                y_max = height-2

            valid_boxes[i] = (x_min, y_min, x_max, y_max)

        #Normaliza los arreglos
        valid_scores = np.array(valid_scores)
        valid_boxes = np.array(valid_boxes)
        valid_classes = np.array(valid_classes)

        #Filtra los objetos con más de una detección duplicada
        selected_indices = non_max_suppression(valid_boxes, valid_scores, confidence_threshold)

        valid_scores = valid_scores[selected_indices]
        valid_boxes = valid_boxes[selected_indices]
        valid_classes = valid_classes[selected_indices]

        #Genera la lista de Detecciones final
        detections = []
        for i in range(len(valid_scores)):
            box = valid_boxes[i]
            rect_boxes = Rect(box[0], box[1], box[2], box[3])

            score = valid_scores[i]
            boundingBox = rect_boxes
            class_id = int(valid_classes[i])
            label = self.labels[class_id]

            detection = INE_Detection(boundingBox, score, class_id, label)
            ok = False
            orientation = -1
            value = None

            self.bounding_box = boundingBox

            if class_id == 0:
                status, orientation, value = self.get_front_orientation(detection)
                detection.setOrientation(orientation)
                
                if status==0:
                    ok = True
                    detection.setQuality(value)
            else:
                if class_id == 1:
                    status, orientation, value = self.get_back_orientation(detection)
                    detection.setOrientation(orientation)
                    
                    if status==0:
                        ok = True
                        detection.setQuality(value)
                else:
                    status = 1 #ID not found on image
                    
            #print("Orientation =", orientation, ",", ok)
            if ok:
                detections.append(detection)

        return self.get_json_response(status, self.get_description_by_status(status, value), detections)
        return status, self.get_description_by_status(status, value), detections


    def get_json_response(self, status:int, description:str, detections:list) -> dict:
        
        dectection_list = [{
            "label": detection.label,
            "orientation": detection.orientation,
            "quality": detection.quality
        } for detection in detections]
        
        return {
            "status": status,
            "description": description,
            "ids": dectection_list
        }


    def get_front_orientation(self, ineDetection):
        boundingBox = ineDetection.boundingBox

        status, ok, value = self.check_id_info(ineDetection)
        if not ok:
            return status, None, value
        

        idWidth = boundingBox.width()
        idHeight = boundingBox.height()

        horizontal = idWidth>idHeight

        left = boundingBox.left
        top = boundingBox.top
        right = boundingBox.right
        bottom = boundingBox.bottom

        if horizontal:
            right = left + (idWidth/2)
        else:
            bottom = top + (idHeight/2)

        halfID = self.image.crop((left, top, right, bottom))
        
        frontOk = False
        face = None
        orientation = None
        rotated = halfID
        for ori in range(4):
            if ori!=0:
                rotated = rotated.rotate(90, expand=True)

            faces = detect_faces(rotated, True)
            if len(faces)>0:
                orientation = ori
                frontOk = True
                face = faces[0]
                break

        if frontOk:
            status = 0
        else:
            status = 3 #Orientation could not be found 
        return status, orientation, value #, face
    

    def get_back_orientation(self, ineDetection):
        boundingBox = ineDetection.boundingBox

        status, ok, value = self.check_id_info(ineDetection)
        if not ok:
            return status, None, value
        

        idWidth = boundingBox.width()
        idHeight = boundingBox.height()

        oriLeft = boundingBox.left
        oriTop = boundingBox.top
        oriRight = boundingBox.right
        oriBottom = boundingBox.bottom

        horizontal = idWidth>idHeight

        backOk = False
        orientation = None
        
        if horizontal:
            left = oriLeft + (idWidth/2)
            right = oriRight
            top = oriTop
            bottom = oriBottom
        else:
            top = oriTop + (idHeight/2)
            right = oriRight
            left = oriLeft
            bottom = oriBottom

        halfID = self.image.crop((left, top, right, bottom))

        qrs = self.detect_URL_QRs(halfID)
        if len(qrs)>0:
            if self.contains_INE_URL(qrs):
                backOk = True
                if horizontal:
                    orientation = 0
                else:
                    orientation = 1

        if backOk==False:
            if horizontal:
                left = oriLeft
                right = oriLeft + (idWidth/2)
                top = oriTop
                bottom = oriBottom
            else:
                top = oriTop
                right = oriRight
                left = oriLeft
                bottom = oriTop + (idHeight/2)

            halfID = self.image.crop((left, top, right, bottom))
                
            qrs = self.detectURLQRs(halfID)
            if len(qrs)>0:
                if self.contains_INE_URL(qrs):
                    backOk = True
                    if horizontal:
                        orientation = 2
                    else:
                        orientation = 3

        if backOk:
            status = 0
        else:
            status = 3 #Orientation could not be found 

        return status, orientation, value
        

    def check_id_info(self, ineDetection):
        boundingBox = ineDetection.boundingBox

        idCropped = self.image.crop((boundingBox.left, boundingBox.top, boundingBox.right, boundingBox.bottom))

        # ID Quality
        imgCV = cv2.cvtColor(np.array(idCropped), cv2.COLOR_RGB2BGR)
        laplacian = cv2.Laplacian(imgCV,cv2.CV_64F)
        gnorm = np.sqrt(laplacian**2)
        sharpness = np.average(gnorm)

        if sharpness < self.min_quality: #minQuality
            status = 4 #Too low Quality value
            return status, False, sharpness
        
        # ID Size on image
        bBArea = boundingBox.getArea()
        width, height = self.image.size
        imgArea = width*height
        areaPct = (imgArea/bBArea)

        if areaPct < self.min_size_pct: #minSizePct
            status = 2 #The detected ID is too small on the image
            return status, False, areaPct
        
        # ID color distance
        if not self.allow_copy:
            if not (self.image.mode not in ("L", "RGB")) and self.image.mode == "RGB":
                rgb = idCropped.split()

                colorDistance = ImageChops.difference(rgb[0],rgb[1]).getextrema()[1]
                if colorDistance < self.min_color_distance:
                    status = 5
                    return status, False, colorDistance
                
                colorDistance = ImageChops.difference(rgb[0],rgb[2]).getextrema()[1]
                if colorDistance < self.min_color_distance:
                    status = 5
                    return status, False, colorDistance
            else:
                status = 5
                colorDistance = 0
                return status, False, colorDistance

        return 0, True, sharpness
    

    def get_description_by_status(self, status, value):
        if status==0:
            return "OK"
        if status==1:
            return "Could not detect an ID on the image"
        if status==2:
            return "The detected ID is too small on the image (" + str(value) + ")"
        if status==3:
            return "Orientation could not be detected"
        if status==4:
            return "Too low Quality value (" + str(value) + ")"
        if status==5:
            return "Possible photocopy detected (" + str(value) + ")"


    def detect_URL_QRs(self, image):
        urls = []
        try:
            qrs = pyzbar.decode(image)
            for qr in qrs:
                qrData = qr.data
                try:
                    url = urlparse(qrData.decode())
                    
                    urls.append(url.geturl())
                except (KeyError, IndexError):
                    continue
        finally:
            return urls
        

    def is_INE_URL(self, url):
        length = len(url)
        return (12 <= length <= 149)


    def contains_INE_URL(self, urls):
        for url in urls:
            if self.is_INE_URL(url):
                return True
        return False
    

    def get_boundings_id(self):
        return self.bounding_box

