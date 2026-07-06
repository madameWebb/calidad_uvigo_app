document.addEventListener('DOMContentLoaded', function() {
    const radios = document.querySelectorAll('input[name="campo"]');
    const selectOrden = document.getElementById('orden-campo');
    const table = document.querySelector('table tbody');
    
    if (!table) return;
    
    function obtenerTexto(fila, selector) {
        const elemento = fila.querySelector(selector);
        return elemento ? elemento.textContent.trim() : '—';
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
    
    radios.forEach(radio => radio.addEventListener('change', ordenarTabla));
    selectOrden.addEventListener('change', ordenarTabla);
});