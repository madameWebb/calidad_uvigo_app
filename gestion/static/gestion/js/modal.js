document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modal-orixe');
    const selectOrixe = document.getElementById('select-orixe');
    const btnAceptar = document.getElementById('btn-aceptar');
    const btnCancelar = document.getElementById('btn-cancelar');
    let centroActual = null;

    // Abrir modal al hacer click en centro
    document.querySelectorAll('.btn-centro').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            centroActual = this.dataset.centroId;
            selectOrixe.value = '';
            modal.classList.add('visible');
        });
    });

    // Cerrar modal
    btnCancelar.addEventListener('click', function() {
        modal.classList.remove('visible');
    });

    // Aceptar y navegar
    btnAceptar.addEventListener('click', function() {
        const orixe = selectOrixe.value;
        if (!orixe) {
            alert('Por favor selecciona un año');
            return;
        }
        // Convertir 23/24 a 23-24 para la URL
        const oreixeUrl = orixe.replace('/', '-');
        window.location.href = `/seguimentos-centros/${centroActual}/${oreixeUrl}/`;
    });

    // Cerrar modal al hacer click fuera
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            modal.classList.remove('visible');
        }
    });
});