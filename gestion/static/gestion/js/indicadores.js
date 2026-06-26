document.addEventListener('DOMContentLoaded', function() {
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