document.addEventListener('DOMContentLoaded', function() {
    const selectCodigo = document.getElementById('orden-codigo-i');
    const selectNome = document.getElementById('orden-nome-indicador');
    const selectProcedemento = document.getElementById('orden-procedemento');
    const container = document.querySelector('.indicadores-container');

    function obtenerTexto(tarjeta, selector) {
        const elemento = tarjeta.querySelector(selector);
        return elemento ? elemento.textContent.trim() : '—';
    }

    function ordenarTarjetas() {
        const tarjetas = Array.from(container.querySelectorAll('.card-indicador'));
        
        // Array de campos a ordenar: [selector, valor select, prioritario?]
        const campos = [
            { selector: '.card-content-inicial h3', select: selectCodigo, nombre: 'código' },
            { selector: '.card-content-inicial .denominacion', select: selectNome, nombre: 'denominacion' },
            { selector: '.card-content-inicial .procedemento', select: selectProcedemento, nombre: 'procedemento' }
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
    [selectCodigo, selectNome, selectProcedemento].forEach(select => {
        if (select) select.addEventListener('change', ordenarTarjetas);
    });

    document.querySelectorAll('.btn-expand').forEach(btn => {
        btn.addEventListener('click', function() {
            const card = this.closest('.card-indicador');
            const body = card.querySelector('.card-body');
            
            body.classList.toggle('visible');
            const isVisible = body.classList.contains('visible');
            this.textContent = isVisible ? '▲' : '▼';
        });
    });
});