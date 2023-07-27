(function () {

    "use strict";

    const btnReturn = document.querySelector('.div-btn-regresar a');
    const btnIncorrecta = document.getElementById('btn-no');
    
    function allStorage() {

        var values = [],
            keys = Object.keys(sessionStorage),
            i = keys.length;

        while (i--) {
            values.push(sessionStorage.getItem(keys[i]));
        }

        return values;
    }


    $(document).ready(function () {

        const lastImg = $('.imagen').attr('src');
        const arrayName = lastImg.split('/');
        const nameImg = arrayName[arrayName.length - 1];

        if (!allStorage().length) {
            btnReturn.classList.add('disabled');
        } else {
            btnReturn.classList.remove('disabled');

            const url = allStorage()[0];
            const urlType = url.split('|')[0];
            const urlName = url.split('|')[1];

            const currentLoc = window.location;

            btnReturn.href = `${currentLoc}lastimg/${urlType}/${urlName}`;

        }

        const name = nameImg.split('.')[0];

        btnIncorrecta.href = `${window.location}label/${name}`;

        $('.boton-si a').click(function () {

            $.ajax({
                url: '',
                type: 'get',
                contentType: 'application/json',
                data: {
                    button_text: $(this).text(),
                    img: $('.imagen').attr('src'),
                },

            });

            sessionStorage.clear();
            sessionStorage.setItem(lastImg, `Correcta|${nameImg}`);

        });


        $('.boton-no a').click(function () {

            $.ajax({
                url: '',
                type: 'get',
                contentType: 'application/json',
                data: {
                    button_text: $(this).text(),
                    img: $('.imagen').attr('src'),
                }

            });
            sessionStorage.clear();
            sessionStorage.setItem(lastImg, `Incorrecta|${nameImg}`);

        });

        $(document).keyup(function (event) {

            // Tecla direccional izquierda
            if (event.which === 37) {

                const btnNo = $('.boton-no a');

                btnNo.trigger('click');
                btnNo.addClass('press-key-no');

                sessionStorage.clear()
                sessionStorage.setItem(lastImg, `Incorrecta|${nameImg}`);

                setTimeout(() => {
                    btnNo.removeClass('press-key-no');
                    location.reload();
                }, 500);
            }

            // Tecla direccional derecha
            if (event.which === 39) {

                const btnSi = $('.boton-si a');

                btnSi.trigger('click');
                btnSi.addClass('press-key-yes');

                sessionStorage.clear();
                sessionStorage.setItem(lastImg, `Correcta|${nameImg}`);

                setTimeout(() => {
                    btnSi.removeClass('press-key-yes');
                    location.reload();
                }, 500);

            }
        });


    });
})();