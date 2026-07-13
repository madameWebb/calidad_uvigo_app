document.addEventListener('DOMContentLoaded', function() {
    
    document.querySelectorAll('.btn-titulo').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            window.location.href = `/avaliacionspdis/${this.dataset.tituloId}/`;
        });
    });

});