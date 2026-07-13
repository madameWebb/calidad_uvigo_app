document.addEventListener('DOMContentLoaded', function() {
    const selectSigma = document.getElementById('orden-sigma');
    const selectDenominacion = document.getElementById('orden-denominacion');
    const selectTipo = document.getElementById('orden-tipo');
    const container = document.querySelector('.indicadores-container');
    
    if (!container) return;
    
    function obtenerTexto(tarjeta, selector) {
        const elemento = tarjeta.querySelector(selector);
        return elemento ? elemento.textContent.trim() : '—';
    }
    
    function ordenarTarjetas() {
        const tarjetas = Array.from(container.querySelectorAll('.card-indicador'));
        
        // Array de campos a ordenar: [selector, valor select, prioritario?]
        const campos = [
            { selector: '.card-content-inicial h3', select: selectSigma, nombre: 'sigma' },
            { selector: '.card-content-inicial .denominacion', select: selectDenominacion, nombre: 'denominacion' },
            { selector: '.card-content-inicial .tipo', select: selectTipo, nombre: 'tipo' }
        ];
        
        tarjetas.sort((a, b) => {
            // Recorrer los campos en orden de prioridad
            for (let campo of campos) {
                const orden = campo.select ? campo.select.value : 'ninguno';
                
                if (orden === 'ninguno') continue;
                
                const textoA = obtenerTexto(a, campo.selector);
                const textoB = obtenerTexto(b, campo.selector);
                
                let resultado = textoA.localeCompare(textoB);
                
                if (orden === 'descendente') resultado *= -1;
                if (resultado !== 0) return resultado;
            }
            
            return 0;
        });
        
        // Volver a añadir las tarjetas ordenadas
        tarjetas.forEach(tarjeta => container.appendChild(tarjeta));
    }
    
    // Añadir event listeners a todos los selectores
    [selectSigma, selectDenominacion, selectTipo].forEach(select => {
        if (select) select.addEventListener('change', ordenarTarjetas);
    });
});