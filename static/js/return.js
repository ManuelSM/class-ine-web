(function () {

    const btnSi = $('.boton-si a');
    const btnNo = $('.boton-no a');

    $(document).ready(function () {

        const getUrl = window.location.href;
        const botonNo = document.querySelector('.boton-no a');

        if (getUrl.includes('Correcta')) {
            btnSi.text("Cancelar");
            btnNo.text("Incorrecta"); // Cambiar a Etiquetar
        }

        if (getUrl.includes("Incorrecta")) {
            btnSi.text("Correcta");
            btnNo.text("Cancelar");
        }

        const nombreImgArr = getUrl.split('/');
        const nombreImg = nombreImgArr[nombreImgArr.length - 1].split('.')[0];

        botonNo.href = `${window.location.origin}/label/${nombreImg}`;

        btnSi.click(function () {

            $.ajax({
                url: '',
                type: 'get',
                contentType: 'application/json',
                data: {
                    button_text: $(this).text(),
                    img: $('.imagen').attr('src'),
                },
                done: function () {
                    sessionStorage.clear();
                }
            });

        });

        
    });
})();