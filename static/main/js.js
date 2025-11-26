function confirmarEliminacion(formId, nombre) {  // ← Cambia 'url' por 'formId'
    Swal.fire({
        title: '¿Estás seguro?',
        text: `Vas a eliminar al conductor "${nombre}". Esta acción no se puede deshacer.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
            document.getElementById(formId).submit();  // ← Esto está correcto
        }
    });
}

function confirmarEliminacionSweetAlert(pk, nombre) {
    Swal.fire({
        title: '¿Estás seguro?',
        html: `Vas a eliminar al supervisor: <strong>"${nombre}"</strong>`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar',
        reverseButtons: true,
        backdrop: true,
        allowOutsideClick: false
    }).then((result) => {
        if (result.isConfirmed) {
            // Crear formulario dinámico para enviar la solicitud POST
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = `/supervisores/eliminar/${pk}/`;
            
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrfmiddlewaretoken';
                csrfInput.value = csrfToken.value;
                form.appendChild(csrfInput);
            }
            
            document.body.appendChild(form);
            form.submit();
        }
    });
}


d