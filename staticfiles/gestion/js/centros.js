document.addEventListener('DOMContentLoaded', function() {
    const selectCampus = document.getElementById('orden-campus');
    const selectCodigo = document.getElementById('orden-codigo');
    const selectDenominacion = document.getElementById('orden-denominacion');
    const table = document.querySelector('table tbody');
    
    if (!selectCampus || !selectDenominacion || !table) return;
    
    function ordenarTabla() {
        const ordenCampus = selectCampus.value;
        const ordenCodigo = selectCodigo.value;
        const ordenDenom = selectDenominacion.value;
        
        const filas = Array.from(table.querySelectorAll('tr'));
        
        filas.sort((a, b) => {
            let resultado = 0;
            
            // Ordenar por Campus primero
            if (ordenCampus !== 'ninguno') {
                const campusA = a.cells[0].textContent.trim();
                const campusB = b.cells[0].textContent.trim();
                resultado = campusA.localeCompare(campusB);
                if (ordenCampus === 'descendente') resultado *= -1;
                if (resultado !== 0) return resultado;
            }
            
            if (ordenCodigo !== 'ninguno') {
                const codigoA = a.cells[1].textContent.trim();
                const codigoB = b.cells[1].textContent.trim();
                resultado = codigoA.localeCompare(codigoB);
                if (ordenCodigo === 'descendente') resultado *= -1;
                if (resultado !== 0) return resultado;
            }

            // Luego por Denominación
            if (ordenDenom !== 'ninguno') {
                const denomA = a.cells[2].textContent.trim();
                const denomB = b.cells[2].textContent.trim();
                resultado = denomA.localeCompare(denomB);
                if (ordenDenom === 'descendente') resultado *= -1;
            }
            
            return resultado;
        });
        
        // Volver a añadir las filas ordenadas
        filas.forEach(fila => table.appendChild(fila));
    }
    
    selectCampus.addEventListener('change', ordenarTabla);
    selectCodigo.addEventListener('change', ordenarTabla);
    selectDenominacion.addEventListener('change', ordenarTabla);
});