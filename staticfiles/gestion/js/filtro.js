document.addEventListener('DOMContentLoaded', function() {
    const inputFiltro = document.getElementById('filtro-input');
    
    if (!inputFiltro) return;
    
    inputFiltro.addEventListener('keyup', function() {
        const texto = this.value.toLowerCase();
        const items = document.querySelectorAll('[data-filtrable]');
        let visibles = 0;
        
        items.forEach(item => {
            const textoItem = item.textContent.toLowerCase();
            const coincide = textoItem.includes(texto);
            
            item.style.display = coincide ? '' : 'none';
            if (coincide) visibles++;
        });
        
        // Mostrar/ocultar mensaje de no resultados
        const noResultados = document.getElementById('no-resultados');
        if (noResultados) {
            noResultados.style.display = visibles === 0 ? 'block' : 'none';
        }
    });
});