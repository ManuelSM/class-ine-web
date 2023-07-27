
const labelGroup = document.getElementById('label-group')
const labelGroupArray = labelGroup.querySelectorAll('button');

const labelTable = document.getElementById('label-table');
const btnAddLabel = document.getElementById('label-add');
const btnSaveData = document.getElementById('label-saveData');
const btnSaveTable = document.getElementById('label-save-table');


const imageLabel = document.getElementById('target');
const formHiddenInputs = document.getElementById('hidden-form').querySelectorAll('.label-coor');
const formHiddenLabelName = document.querySelector('.label-name');

let count = 1;

// Función para tomar el nombre de la etiqueta seleccionada por el usuario.
function getLabel(selectedLabel) {
    const label = selectedLabel.querySelector('small').textContent;
    formHiddenLabelName.value = label.split(':')[1].trim();

}

// Función para calcular las coordenadas del área seleccionada de la imagen original.
function getCoord(coor) {

    const scale = imageLabel.clientWidth / imageLabel.naturalWidth;
    const [XminCnt, YminCnt, width, height] = coor;

    const Ymin = Math.round(YminCnt / scale);
    const Xmin = Math.round(XminCnt / scale);
    const Ymax = Math.round( (YminCnt + height) / scale);
    const Xmax = Math.round( (XminCnt + width) / scale);

    const coorArray = [Xmin, Ymin, Xmax, Ymax]

    formHiddenInputs.forEach((element, index) => {
        element.value = coorArray[index];
    });

}

// Función para tomar de la segunda hasta la penúltima celda de la tabla y guardar los datos en un arreglo de arreglos.
function getTableData(tablaId){
    return [...document.querySelector(tablaId).rows].map(renglones => [...renglones.cells].slice(1,6).map(celda => celda.textContent));

}

// Función para enviar datos de tabla vía POST a Flask.
function saveTableData() {
    
    const objImg = {
        name: imageLabel.src.split('/').pop(),
        width: imageLabel.naturalWidth,
        height: imageLabel.naturalHeight,
        labels: getTableData("#label-table-body"),
    }

    let js_data = JSON.stringify(objImg);

    fetch(`${window.origin}/label/${imageLabel.src.split('/').pop().split('.')[0]}`, {
        method: 'POST',
        credentials: 'include',
        body: js_data,
        cache: 'no-cache',
        headers: new Headers({
            'content-type': 'application/json'
        }),
    })
    .then(sessionStorage.clear())
    .then(window.location = '/'); //window.location = '/'

}

// Función para insertar datos de etiqueta y coordenadas en la tabla.
function insertDataLabel() {
    
    let row = labelTable.querySelector('tbody').insertRow(-1);

    let num    = row.insertCell(0);
    let name   = row.insertCell(1);
    let xmin   = row.insertCell(2);
    let ymin   = row.insertCell(3);
    let xmax   = row.insertCell(4);
    let ymax   = row.insertCell(5);
    let delRow = row.insertCell(6);

    const arrayYXMinMax = [xmin, ymin, xmax, ymax];

    num.innerHTML = count;
    count++;

    name.innerHTML = formHiddenLabelName.value;

    formHiddenInputs.forEach((element, index) => {
        arrayYXMinMax[index].innerHTML = element.value;
    });

    const btnDel = document.createElement('button');

    btnDel.innerHTML = `<i class="bi bi-trash"></i>`;
    btnDel.classList.add('btn', 'btn-warning', 'btn-sm', 'label-del');
    btnDel.setAttribute('onclick', 'RemoveRow(this)');

    delRow.appendChild(btnDel);

}

// Función para remover la fila de la tabla.
function RemoveRow(fila){
    let td = fila.parentNode.parentNode;
    td.parentNode.removeChild(td);
}

window.addEventListener('DOMContentLoaded', function () {

    // Se indica que la imagen sera "target" para la librería Jcrop.
    const stage = Jcrop.attach('target');

    stage.listen('crop.change', function (widget, e) {
        const pos = widget.pos;
        const arrayCoor = [pos.x, pos.y, pos.w, pos.h];

        getCoord(arrayCoor);
    });


    // Se identifica que etiqueta fue seleccionada por el usuario.
    labelGroupArray.forEach(element => {
        element.addEventListener('click', () => {
            labelGroupArray.forEach(btn => btn.classList.remove('active'));
            element.classList.add('active');

            getLabel(element);

        });
    });

    // Click en botón para añadir etiquetas, se muestra una alerta si no se ha elegido área o etiqueta.
    btnAddLabel.addEventListener('click', function () {

        const alertaDiv = document.createElement('div');
        const opcionDiv = document.querySelector('.label-options');
        
        alertaDiv.classList.add('alert', 'alert-warning', 'my-3');
        alertaDiv.setAttribute('role', 'alert');
        alertaDiv.textContent = "Escoge un label o elige área en la imagen.";
        
        const alerta = document.querySelector('.alert');
        if (!!formHiddenLabelName.value && !!formHiddenInputs[0].value) {
            insertDataLabel();
        } else {
            if(!alerta){
                opcionDiv.appendChild(alertaDiv);
            }
            setTimeout(() => {
                opcionDiv.removeChild(alertaDiv);
            }, 4000);
        }
    });

    // Click en botón para abrir ventana modal, si no hay datos en la tabla se desactiva el botón de guardar cambios.
    btnSaveTable.addEventListener('click', function(){
    
        const tablaLabel = document.getElementById('label-table');
        const tablaBody = tablaLabel.querySelector('tbody');
        const contenidoBody = tablaBody.innerHTML;

        const modalMsg = document.getElementById('exampleModal').querySelector('.modal-body');

        if(!contenidoBody.includes('td')){
            btnSaveData.classList.add('disabled');
            modalMsg.textContent = "Agregue etiquetas para poder guardar";
        } else {
            btnSaveData.classList.remove('disabled');
            modalMsg.textContent = "Una vez guardado ya no podrá cambiar las etiquetas";
        }

    });

    // Click en botón para Guardar Cambios y enviar datos de etiquetas y datos de imagen.
    btnSaveData.addEventListener('click', function() {
        saveTableData();
    });

});