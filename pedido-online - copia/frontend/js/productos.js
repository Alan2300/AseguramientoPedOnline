const apiURL = 'http://127.0.0.1:5000/api/products';

document.addEventListener('DOMContentLoaded', () => {
    cargarProductos();
    document.getElementById('formAgregarProducto').addEventListener('submit', guardarProducto);
    document.getElementById('buscador').addEventListener('input', buscarProducto);
});

function cargarProductos() {
    fetch(`${apiURL}/list`)
        .then(response => response.json())
        .then(data => mostrarProductos(data))
        .catch(error => console.error('Error al cargar productos:', error));
}

function mostrarProductos(productos) {
    const tabla = document.getElementById('tablaProductos');
    tabla.innerHTML = '';

    productos.forEach(prod => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
            <td><img src="http://127.0.0.1:5000${prod.imagen}" alt="${prod.nombre}" width="60"></td>
            <td>${prod.nombre}</td>
            <td>${prod.descripcion}</td>
            <td>Q ${prod.precio_unitario}</td>
            <td>${prod.cantidad_actual || 0}</td>
            <td>
                <button class="editar" onclick="mostrarFormularioEditar(${prod.id_producto}, '${prod.nombre}', '${prod.descripcion}', ${prod.precio_unitario}, ${prod.cantidad_actual || 0})">Editar</button>
                <button class="eliminar" onclick="eliminarProducto(${prod.id_producto})">Eliminar</button>
            </td>
        `;
        tabla.appendChild(fila);
    });
}

function guardarProducto(e) {
    e.preventDefault();
    const form = document.getElementById('formAgregarProducto');
    const formData = new FormData(form);
    const id = form.dataset.idProducto;
    const url = id ? `${apiURL}/update/${id}` : `${apiURL}/add`;

    fetch(url, {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            alert(data.mensaje);
            form.reset();
            form.style.display = 'none';
            form.removeAttribute('data-id-producto');
            cargarProductos();
        })
        .catch(error => {
            console.error('Error al guardar producto:', error);
            alert('Error al guardar producto.');
        });
}

function eliminarProducto(id) {
    if (!confirm('¿Seguro que deseas eliminar este producto?')) return;

    fetch(`${apiURL}/delete/${id}`, {
        method: 'DELETE'
    })
        .then(response => response.json())
        .then(data => {
            alert(data.mensaje);
            cargarProductos();
        })
        .catch(error => {
            console.error('Error al eliminar producto:', error);
            alert('Error al eliminar producto.');
        });
}

function mostrarFormularioEditar(id, nombre, descripcion, precio, cantidad) {
    const form = document.getElementById('formAgregarProducto');
    form.style.display = 'block';
    form.dataset.idProducto = id;
    form.nombre.value = nombre;
    form.descripcion.value = descripcion;
    form.precio_unitario.value = precio;
    form.cantidad.value = cantidad;
}

function mostrarFormularioAgregar() {
    const form = document.getElementById('formAgregarProducto');
    form.reset();
    form.style.display = 'block';
    form.removeAttribute('data-id-producto');
}

function buscarProducto() {
    const filtro = document.getElementById('buscador').value.toLowerCase();
    const filas = document.querySelectorAll('#tablaProductos tr');

    filas.forEach(fila => {
        const nombre = fila.children[1].textContent.toLowerCase();
        fila.style.display = nombre.includes(filtro) ? '' : 'none';
    });
}
