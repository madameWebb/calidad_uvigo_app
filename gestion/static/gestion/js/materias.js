document.addEventListener('DOMContentLoaded', function() {
    const radios = document.querySelectorAll('input[name="campo"]');
    const selectOrden = document.getElementById('orden-campo');
    const tabla = document.querySelector('table tbody');
    
    if (!tabla) return;
    
    function obtenerTexto(fila, indice) {
        const celda = fila.cells[indice];
        return celda ? celda.textContent.trim() : '—';
    }
    
    function ordenarTabla() {
        const checked = document.querySelector('input[name="campo"]:checked');
        if (!checked) return;

        const campo = checked.value;
        const orden = selectOrden.value;

        if (orden === 'ninguno') return;

        const indice = campo === 'codigo' ? 0 : 1;
        const filas = Array.from(tabla.querySelectorAll('tr'));

        filas.sort((a, b) => {
            const textoA = obtenerTexto(a, indice);
            const textoB = obtenerTexto(b, indice);
            
            let resultado = textoA.localeCompare(textoB);
            
            if (orden === 'descendente') resultado *= -1;
            return resultado;
        });
        
        filas.forEach(fila => tabla.appendChild(fila));
    }
    
    radios.forEach(radio => radio.addEventListener('change', ordenarTabla));
    if (selectOrden) selectOrden.addEventListener('change', ordenarTabla);  
});