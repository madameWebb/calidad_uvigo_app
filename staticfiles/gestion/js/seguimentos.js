document.addEventListener('DOMContentLoaded', function() {
    const selectCampus = document.getElementById('filtro-campus');
    const selectCentro = document.getElementById('filtro-centro');
    const radios = document.querySelectorAll('input[name="campo"]');
    const localizacion = document.querySelectorAll('input[name="localizacion"]');
    const selectOrden = document.getElementById('orden-campo');
    const table = document.querySelector('table tbody');
    const tipoRadios = document.querySelectorAll('input[name="tipo-indicador"]');

    if (!table && tipoRadios.length === 0) return;
    
    function obtenerTexto(fila, selector) {
        const elemento = fila.querySelector(selector);
        return elemento ? elemento.textContent.trim() : '—';
    }
    
    function filtrarCampus(){
        const campus = this.value;
        table.querySelectorAll('tr').forEach(fila => {
            if (!campus || fila.dataset.campus === campus) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    }

    function filtrarCentro(){
        const centro = this.value;
        table.querySelectorAll('tr').forEach(fila => {
            if (!centro || fila.dataset.centro === centro) {
                fila.style.display = '';
            } else {
                fila.style.display = 'none';
            }
        });
    }

    function ordenarTabla() {
        const campo = document.querySelector('input[name="campo"]:checked').value;
        const orden = selectOrden.value;
        
        if (orden === 'ninguno') return;
        
        const selector = campo === 'codigo' ? '.codigo-seguimento' : '.nome-centro';
        const filas = Array.from(table.querySelectorAll('tr'));
        
        filas.sort((a, b) => {
            const textoA = obtenerTexto(a, selector);
            const textoB = obtenerTexto(b, selector);
            
            let resultado = textoA.localeCompare(textoB);
            
            if (orden === 'descendente') resultado *= -1;
            return resultado;
        });
        
        filas.forEach(fila => table.appendChild(fila));
    }
    function agrupar() {
        const checked = document.querySelector('input[name="localizacion"]:checked');
        if (!checked) return;

        const elegir = checked.value;
        console.log('Agrupar:', elegir);  // DEBUG
        const filtroCampus = document.getElementById('filtro-campus-container');
        const filtroCentro = document.getElementById('filtro-centro-container');
        console.log('filtroCampus:', filtroCampus);  // DEBUG
        console.log('filtroCentro:', filtroCentro);  // DEBUG
        if (elegir === 'campus') {
            filtroCampus.style.display = '';
            filtroCentro.style.display = 'none';
        } else if (elegir === 'centro') {
            filtroCampus.style.display = 'none';
            filtroCentro.style.display = '';
        } 
    }
    function filtrarTipo() {
        const tipo = document.querySelector('input[name="tipo-indicador"]:checked').value;
        document.querySelectorAll('.card-indicador').forEach(card => {
            if (tipo === 'todos' || card.dataset.tipo === tipo) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }

    tipoRadios.forEach(radio => radio.addEventListener('change', filtrarTipo));    
    radios.forEach(radio => radio.addEventListener('change', ordenarTabla));
    localizacion.forEach(radio => radio.addEventListener('change', agrupar));
    selectOrden.addEventListener('change', ordenarTabla);
    
    if (selectCampus) selectCampus.addEventListener('change', filtrarCampus);
    if (selectCentro) selectCentro.addEventListener('change', filtrarCentro);
    
    agrupar();
});