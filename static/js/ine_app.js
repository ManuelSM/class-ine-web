(function () {

    "use strict";
   
    // Grupo de botones de opciones
    const labelGroupArrayCred = document.getElementById('label-group-credential').querySelectorAll('button');
    const labelGroupArrayOri  = document.getElementById('label-group-orientation').querySelectorAll('button');
    const labelGroupArrayVer  = document.getElementById('label-group-version').querySelectorAll('button');
    const labelGroupArrayQua  = document.getElementById('label-group-quality').querySelectorAll('button');

    // Botones para guardar datos
    const btnSaveData = document.getElementById('label-save-data');
    const btnSaveConfirm = document.getElementById('label-save-confirm');

    // Imagen de credencial
    const imageINE = document.getElementById('image-target');
    const buttonNoCredential = document.getElementById('label_no_credential');

    let scaleX;
    let scaleY;

    const labelObject = {
        name: '',
        width: 0,
        height: 0,
        credential: '', 
        orientation: '',
        version: '',
        quality: '',
        left: '',
        top: '',
        right: '',
        bottom: '',
    }

    console.log("Hola HuBOX :)");


    window.addEventListener('DOMContentLoaded', function() {
        
    
        // Tomamos datos de la imagen original 
        getIneData().then(data => {

            const hasCred = setLabelCredential(data);

            if (hasCred) {

                setOrientation(data);
                setQuality(data)
            
                // Valores originales de Rect de la imagen original
                const originalCoord = data.bounding_box;
                const arrayCoord = getJcropCoords(originalCoord);
                const rect = Jcrop.Rect.create(arrayCoord[0], arrayCoord[1], arrayCoord[2], arrayCoord[3]);
                
                // Crear el nuevo widget 
                const options = {};
                stage.newWidget(rect, options);


                paintValues(arrayCoord);
                // Agregar los valores de rect al objeto 
                setCoordObject(arrayCoord);
            }

        }).catch (error => {
            console.log(error);
        });

        
        const stage  = Jcrop.attach('image-target');
        
        stage.listen('crop.change', function (widget, e) {

           const pos = widget.pos;
           const arrayCoor = [pos.x, pos.y, pos.w, pos.h];
           const arrayObject = [pos.y, pos.x, pos.x + pos.w, pos.y + pos.h];

           paintValues(arrayCoor);
           setCoordObject(arrayObject);
           
        });
        
        selectOption(labelGroupArrayCred);
        selectOption(labelGroupArrayOri);   
        selectOption(labelGroupArrayVer);   
        selectOption(labelGroupArrayQua);

        labelObject.name = imageINE.src.split('/').pop();
        
        btnSaveData.addEventListener('click', () => {
            
            // Checar si labelObject esta completo 
            const nullOnObject = checkNullObject(labelObject)

            if (labelObject.credential === "none") {

                showAlertDisableConfirm(false);
                setObjectNoCredential();

            } else if (nullOnObject) {

                showAlertDisableConfirm(true);

            } else {

                showAlertDisableConfirm(false);

            }

            console.log(labelObject);

        });


        btnSaveConfirm.addEventListener('click', () => {
            saveData()
        });


        buttonNoCredential.addEventListener('click', () => {
            deactivateOptions()
        });


    });


    function setQuality(data){
        const ids = data.data.ids[0]
        const quality = ids?.quality
        
        if (quality < 10) {
            labelGroupArrayQua[1].classList.add('active');
            labelObject.quality = 'Mala'
            return
        }

        labelGroupArrayQua[0].classList.add('active');
        labelObject.quality = 'Buena'

        return

    }


    function setLabelCredential(data){
 
        let hasCred;
        const ids = data.data.ids[0]
        const label = ids?.label
 
        if (label == "back_id") {

            labelGroupArrayCred[1].classList.add('active');
            labelObject.credential = "reverso";

            hasCred = true;

        } else if (label == "front_id") {
            
            labelGroupArrayCred[0].classList.add('active');
            labelObject.credential = "anverso";

            hasCred = true;
        } else if(label === undefined) {
            
            buttonNoCredential.classList.add('active');
            labelObject.credential = "none";
            deactivateOptions();

            hasCred = false;

        }

        return hasCred
    }


    function setOrientation(data) {

        const ids = data.data.ids[0]

        const orientation = ids.orientation

        switch (orientation) {
            case 0:
                labelGroupArrayOri[0].classList.add('active');
                labelObject.orientation = '0';
                break;
            case 1:
                labelGroupArrayOri[1].classList.add('active');
                labelObject.orientation = '1';
                break;
            case 2:
                labelGroupArrayOri[2].classList.add('active');
                labelObject.orientation = '2';
                break;
            case 3:
                labelGroupArrayOri[3].classList.add('active')
                labelObject.orientation = '3';
                break;
            default:
                console.log("Default");
                break;
        }

        return ids.orientation

    }

    function setCoordObject(array) {

        // TODO: Ver si es el valor original o el renderizado

        // left value times width
        labelObject.left = array[0] / scaleX

        // top value times scale height
        labelObject.top = array[1] / scaleY

        // right value times scale width 
        labelObject.right = array[2] / scaleX

        // bottom value times scale height
        labelObject.bottom = array[3] / scaleY
    }


    function paintValues(array) {

        const valuesDiv = document.getElementById('valores_imagen');
        const pValues = valuesDiv.lastChild;

        pValues.textContent = array
        
    }


    function getJcropCoords(arrayINE) {

        // Obtener medidas de imagen originales
        const originalWidth = imageINE.naturalWidth
        const originalHeight = imageINE.naturalHeight

        // Obtener medidas de imagen renderizada
        const renderWidth = imageINE.width
        const renderHeight = imageINE.height

        scaleX = renderWidth / originalWidth
        scaleY = renderHeight / originalHeight

        if (arrayINE.length == 4) {

            const [left, top, right, bottom] = arrayINE

            const leftNew = left * scaleX
            const topNew = top * scaleY
            const rightNew = right * scaleX
            const bottomNew = bottom * scaleY

            const widthNew = rightNew - leftNew
            const heightNew = bottomNew - topNew

            const arrayCoord = [Math.floor(leftNew), Math.floor(topNew), Math.floor(widthNew), Math.floor(heightNew)]


            // console.log(`renderWidth => ${renderWidth} :: renderHeight => ${renderHeight}`);
            // console.log(`left: ${left}, right: ${right}, top: ${top}, bottom: ${bottom}`);
            // console.log(`scaleX: ${scaleX}, scaleY: ${scaleY}`);
            // console.log(`leftN: ${leftNew}, topNew: ${topNew}, rightNew: ${rightNew}, bottomNew: ${bottomNew}`);
            // console.log(`widthNew: ${widthNew}, heightNew: ${heightNew}`);
            // console.log(`arrayCoord => ${arrayCoord}`);

            return arrayCoord

        }

        return []        

    }


    function setObjectNoCredential() {

        labelObject.orientation = "";
        labelObject.quality = "";
        labelObject.version = "";

    }


    function deactivateOptions() {

        if (buttonNoCredential.classList.contains('active')){

            labelGroupArrayOri.forEach(element => {
                element.classList.add('disabled')
                element.classList.remove('active')
            });
            labelGroupArrayQua.forEach(element => {
                element.classList.add('disabled')
                element.classList.remove('active')
            });
            labelGroupArrayVer.forEach(element => {
                element.classList.add('disabled')
                element.classList.remove('active')
            });

            setObjectNoCredential()

            btnSaveConfirm.classList.remove('disabled');

        } else {

            labelGroupArrayOri.forEach(element => {
                element.classList.remove('disabled')
            });
            labelGroupArrayQua.forEach(element => {
                element.classList.remove('disabled')
            });
            labelGroupArrayVer.forEach(element => {
                element.classList.remove('disabled')
            });
            
        }


    }


    function showAlertDisableConfirm(disable) {

        const modalMsg = document.getElementById('exampleModal').querySelector('.modal-body');

        if (disable) {
            btnSaveConfirm.classList.add('disabled');
            modalMsg.textContent = "Complete las opciones para guardar";
        } else {
            btnSaveConfirm.classList.remove('disabled');
            modalMsg.textContent = "Una vez guardado ya no podrá cambiar las etiquetas";
        }

    }


    function saveData() {
        const imageWidth = imageINE.naturalWidth
        const imageHeight = imageINE.naturalHeight

        labelObject.height = imageHeight
        labelObject.width = imageWidth

        let jsData = JSON.stringify(labelObject);

       

        fetch('/process',
        {
            method: 'POST',
            credentials: 'include',
            body: jsData,
            cache: 'no-cache',
            headers: new Headers({
                'content-type': 'application/json'
            }),
        })
        .then(window.location = '/');
        
    }


    function checkNullObject(inputObject) {
        let isNull = Object.values(inputObject).some(value => {
            if (value === null || value === ""){
                return true;
            }
            return false;
        });

        return isNull
    }


    function selectOption(labelGroupArray) {        

        labelGroupArray.forEach(element => {
            element.addEventListener('click', () => {
                labelGroupArray.forEach(btn => btn.classList.remove('active'));
                element.classList.add('active');

                getLabel(element)

                console.log(labelObject);

                deactivateOptions()

            });


        });
        
    }


    function getLabelClass(element){
        const labelId = element.id 
        const labelClass = labelId.split('-').pop()
        return labelClass
    }


    function getLabel(selectedLabel) {

        const label = selectedLabel.querySelector('h6').textContent;
        const labelParent = selectedLabel.parentElement
        const labelClass = getLabelClass(labelParent)

        if(labelClass == "credential")  {
            let text = label.split(' ').pop()

            if (text == 'credencial') {
                text = "none"
            }

            labelObject.credential = text

        } else if (labelClass == "orientation") {

            const text = label.split('.')[0]
            
            labelObject.orientation = text

        } else if (labelClass == "version"){
            const text = label.split(' ')[1]

            labelObject.version = text

        } else {
            
            labelObject.quality = label

        }


    }


    async function getIneData() {

        var imagen = document.getElementById('image-target');

        var srcParam = encodeURIComponent(imagen.src);
        var url = `/obtener_datos?src=${srcParam}`;


        return fetch(url)
        .then(response => response.json())
        .then(data => {

            console.log(data.datos);

            // return data.datos.bounding_box;

            return data.datos;

        })
        .catch(error => console.error('Error:', error));


    }

    
})();