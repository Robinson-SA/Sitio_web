let selectedId = null;

document.addEventListener('DOMContentLoaded', function () {
    const btnModificar = document.getElementById('btnModificar');
    const btnEliminar = document.getElementById('btnEliminar');
    const btnFiniquitar = document.getElementById('btnFiniquitar');
    const btnRenovar = document.getElementById('btnRenovar');

    document.querySelectorAll('.fila-empleado').forEach(fila => {
        fila.addEventListener('click', function () {
            document.querySelectorAll('.fila-empleado').forEach(f => f.classList.remove('fila-seleccionada'));
            this.classList.add('fila-seleccionada');
            selectedId = this.dataset.id;

            btnModificar.disabled = false;
            btnEliminar.disabled = false;
            btnFiniquitar.disabled = false;
            btnRenovar.disabled = false;

            btnModificar.dataset.url = this.dataset.urlModificar;
            btnEliminar.dataset.url = this.dataset.urlEliminar;
            btnFiniquitar.dataset.url = this.dataset.urlFiniquitar;
            btnRenovar.dataset.url = this.dataset.urlRenovar;
        });
    });

    [btnModificar, btnEliminar, btnFiniquitar, btnRenovar].forEach(btn => {
        btn.addEventListener('click', function () {
            if (selectedId && this.dataset.url) window.location.href = this.dataset.url;
        });
    });

    document.querySelectorAll('.fila-empleado .celda-foto').forEach(celda => {
        celda.addEventListener('click', e => e.stopPropagation());
    });
});
