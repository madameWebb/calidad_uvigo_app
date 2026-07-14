document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('modal-orixe');
    const selectOrixe = document.getElementById('select-orixe');
    const btnAceptar = document.getElementById('btn-aceptar');
    const btnCancelar = document.getElementById('btn-cancelar');
    const selectCentro = document.getElementById('filtro-centro');
    const tbody = document.querySelector('table tbody');
    let materiaActual = null;

    // Filtro por centro
    if (selectCentro) {
        selectCentro.addEventListener('change', function() {
            const centro = this.value;
            tbody.querySelectorAll('tr').forEach(fila => {
                if (!centro || fila.dataset.centro === centro) {
                    fila.style.display = '';
                } else {
                    fila.style.display = 'none';
                }
            });
        });
    }

    // Modal
    document.querySelectorAll('.btn-materia').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            materiaActual = this.dataset.materiaId;
            selectOrixe.value = '';
            modal.classList.add('visible');
        });
    });

    btnCancelar.addEventListener('click', function() {
        modal.classList.remove('visible');
    });

    btnAceptar.addEventListener('click', function() {
        const orixe = selectOrixe.value;
        if (!orixe) {
            alert('Por favor selecciona un ano');
            return;
        }
        window.location.href = `/seguimentos-materias/${materiaActual}/${orixe}/`;
    });

    modal.addEventListener('click', function(e) {
        if (e.target === modal) modal.classList.remove('visible');
    });
});