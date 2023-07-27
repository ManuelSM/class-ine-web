import os 
from jinja2 import Environment, FileSystemLoader, select_autoescape

class Writer:


    def __init__(self, path, width, height, depth=3, database='unknown', segmented=0):
        
        environment = Environment(
            loader=FileSystemLoader('voc_template'),
            keep_trailing_newline=True,
            autoescape=select_autoescape(['html', 'xml']),
            )

        self.annotation_template = environment.get_template('annotation_ine_coor.xml')

        abspath = os.path.abspath(path)

        self.filename = os.path.basename(abspath).split('.')[0]

        self.template_parameters = {
            'path': abspath,
            'filename': os.path.basename(abspath),
            'folder': os.path.basename(os.path.dirname(abspath)),
            'width': width,
            'height': height,
            'depth': depth,
            'database': database,
            'segmented': segmented,
            'objects': []
        }


    def addObject(self, name, xmin, ymin, xmax, ymax, pose='Unspecified', truncated=0, difficult=0):
        self.template_parameters['objects'].append({
            'name': name,
            'xmin': xmin,
            'ymin': ymin,
            'xmax': xmax,
            'ymax': ymax,
            'pose': pose,
            'truncated': truncated,
            'difficult': difficult,
        })


    def addObjectINE(self, name, width, height, credential, orientation, version, quality, left, top, right, bottom):
        self.template_parameters['objects'].append({
            'credential': credential,
            'orientation': orientation,
            'version': version,
            'quality': quality,
            'left': left,
            'top': top,
            'right': right,
            'bottom': bottom
        })


    def save(self, annotation_path, same_name = False):

        if same_name: 
            with open(f"{annotation_path}/{self.filename}.xml", 'w') as file:
                content = self.annotation_template.render(**self.template_parameters)
                file.write(content)
        else:
            with open(annotation_path, 'w') as file:
                content = self.annotation_template.render(**self.template_parameters)
                file.write(content)
