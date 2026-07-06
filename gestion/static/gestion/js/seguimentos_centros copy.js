document.addEventListener('DOMContentLoaded', function() {
    const selectCodigo = document.getElementById('orden-codigo-c');
    const selectDenominacion = document.getElementById('orden-centro-uvigo');
    const table = document.querySelector('table tbody');
    
    if (!table) return;

    function obtenerTexto(fila, selector) {
        const elemento = fila.querySelector(selector);
        return elemento ? elemento.textContent.trim() : '—';
    }
    
    function ordenarTabla() {
        const filas = Array.from(table.querySelectorAll('tr'));
        const campos = [
            { selector: '.table-content .codigo-seguimento', select: selectCodigo, nombre: 'codigo' },
            { selector: '.table-content .nome-centro', select: selectDenominacion, nombre: 'denominacion' },
        ];
        
        
        filas.sort((a, b) => {
            let resultado = 0;
            
            for (let campo of campos) {
                const orden = campo.select ? campo.select.value : 'ninguno';
                
                if (orden === 'ninguno') continue;
                
                const textoA = obtenerTexto(a, campo.selector);
                const textoB = obtenerTexto(b, campo.selector);
                
                resultado = textoA.localeCompare(textoB);
                
                if (orden === 'descendente') resultado *= -1;
                if (resultado !== 0) return resultado;
            }
            
            return 0;
        });
        
        // Volver a añadir las filas ordenadas
        filas.forEach(fila => table.appendChild(fila));
    }
    
    selectCodigo.addEventListener('change', ordenarTabla);
    selectDenominacion.addEventListener('change', ordenarTabla);
});