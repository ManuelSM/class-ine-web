import numpy as np
import cv2


def preProcessTF(image, resize_size, float_mod:bool=False):
    image = image.resize((resize_size, resize_size))

    if not float_mod:
        np_image = np.array(image, dtype=np.uint8)
        return np.expand_dims(np_image, axis=0)

    np_image = np.array(image)

    if float_mod:
        norm_img_data = (np_image - np.min(np_image))/(np.max(np_image)-np.min(np_image))
        norm_img_data = np.array(norm_img_data, dtype=np.float32)
    else:
        norm_img_data = np.zeros(np_image.shape).astype('uint8')

    np_image = np.expand_dims(norm_img_data, axis=0)
    return np_image


def non_max_suppression(boxes, scores, iou_threshold):
    if boxes.size == 0 or scores.size == 0:
        return np.array([])
    
    # Ordena las detecciones por puntajes de confianza en orden descendente
    sorted_indices = np.argsort(scores)[::-1]

    # Lista para almacenar los índices seleccionados después de NMS
    selected_indices = []

    if len(sorted_indices)==1:
        selected_indices.append(sorted_indices[0])
    else:
        while sorted_indices.size > 1:  # Verifica que hay al menos dos elementos para comparar
            # Obtiene el índice con el puntaje más alto
            best_index = sorted_indices[0]
            selected_indices.append(best_index)

            # Calcula la superposición (IoU) con todas las demás detecciones
            iou = np.linalg.norm(boxes[best_index] - boxes[sorted_indices[1:]], axis=1)

            # Filtra las detecciones que tienen una superposición significativa con la mejor detección
            filtrado = sorted_indices[1:][iou < iou_threshold]
            if not isinstance(filtrado, np.ndarray):
                selected_indices.append(filtrado)

            # Actualiza los índices restantes para la siguiente iteración
            sorted_indices = sorted_indices[1:][iou >= iou_threshold]

    for i in reversed(range(0, len(selected_indices))):
        index = selected_indices[i]
        box = boxes[index]

        centerX = (box[0] + box[2]) // 2
        centerY = (box[1] + box[3]) // 2
        area = (box[2] - box[0]) * (box[3] - box[1])
            
        for ii in reversed(range(0, len(selected_indices))):
            if i==ii:
                continue

            index2 = selected_indices[ii]
            box2 = boxes[index2]
            box_inside_box2 = is_center_inside_box(centerX, centerY, box2[0], box2[1], box2[2], box2[3]) or has_corner_inside_box(box[0], box[1], box[2], box[3], box2[0], box2[1], box2[2], box2[3])
            if box_inside_box2:
                area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
                if area<area2:
                    selected_indices.pop(i)
                    break
    
    return selected_indices


def is_center_inside_box(center_x, center_y, box_left, box_top, box_right, box_bottom):
    return (box_left <= center_x <= box_right) and (box_top <= center_y <= box_bottom)
    

def has_corner_inside_box(box1_left, box1_top, box1_right, box1_bottom, box2_left, box2_top, box2_right, box2_bottom):
    left_top = (box2_left <= box1_left <= box2_right) and (box2_top <= box1_top <= box2_bottom)
    right_top = (box2_left <= box1_right <= box2_right) and (box2_top <= box1_top <= box2_bottom)
    left_bottom = (box2_left <= box1_left <= box2_right) and (box2_top <= box1_bottom <= box2_bottom)
    right_bottom = (box2_left <= box1_right <= box2_right) and (box2_top <= box1_bottom <= box2_bottom)

    return left_top or right_top or left_bottom or right_bottom


def detect_faces(image, convertToCV = False):
    if convertToCV:
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Carga el clasificador preentrenado de detección de rostros de OpenCV (Haar Cascade)
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Transforma la imagen a blanco y negro (escala de grises)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Realiza la detección de rostros
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    return faces