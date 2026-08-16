import streamlit as st
import streamlit.components.v1 as components

from pathlib import Path
import base64


# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Inicio",
    page_icon="🌱",
    layout="wide"
)


# ============================================================
# QUITAR MÁRGENES DEL CONTENIDO DE STREAMLIT
# ============================================================

st.markdown(
    """
    <style>

    [data-testid="stMainBlockContainer"] {
        padding-left: 0 !important;
        padding-right: 0 !important;
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        max-width: 100% !important;
    }

    [data-testid="stAppViewContainer"] {
        padding: 0 !important;
    }

    [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# RUTA DE IMÁGENES
# ============================================================

ASSETS = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "assets"
    / "fondos"
)


# ============================================================
# CONVERTIR IMAGEN A BASE64
# ============================================================

def imagen_base64(ruta):

    with open(ruta, "rb") as archivo:

        return base64.b64encode(
            archivo.read()
        ).decode()


# ============================================================
# IMÁGENES DEL CARRUSEL
# ============================================================

archivos = [
    "fondo_1.png",
    "fondo_2.jpg",
    "fondo_3.jpg",
    "fondo_4.jpg",
    "fondo_5.jpg",
    "fondo_6.jpg",
    "fondo_7.jpg",
    "fondo_8.jpg",
    "fondo_9.jpg",
    "fondo_10.jpg",
]


# ============================================================
# CARGAR IMÁGENES
# ============================================================

imagenes = []


for archivo in archivos:

    ruta = ASSETS / archivo

    if not ruta.exists():
        continue

    extension = ruta.suffix.lower()

    if extension == ".png":

        tipo = "png"

    elif extension in [".jpg", ".jpeg"]:

        tipo = "jpeg"

    else:

        continue

    contenido = imagen_base64(ruta)

    imagenes.append(
        f"data:image/{tipo};base64,{contenido}"
    )


# ============================================================
# VERIFICAR IMÁGENES
# ============================================================

if not imagenes:

    st.error(
        "No se encontraron imágenes para el carrusel."
    )

    st.stop()


# ============================================================
# CONFIGURACIÓN
# ============================================================

duracion_imagen = 5


# ============================================================
# HTML INICIAL
# ============================================================

html = """
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

* {
    box-sizing: border-box;
}

html,
body {

    margin: 0;
    padding: 0;

    width: 100%;
    height: 100%;

    overflow: hidden;

}

.carrusel {

    position: relative;

    width: 100%;
    height: 100vh;

    overflow: hidden;

    margin: 0;
    padding: 0;

}

.carrusel img {

    position: absolute;

    top: 0;
    left: 0;

    width: 100%;
    height: 100%;

    object-fit: cover;

    opacity: 0;

    transition:
        opacity 1s ease-in-out;

}

.carrusel img.activa {

    opacity: 1;

}

.carrusel::after {

    content: "";

    position: absolute;

    top: 0;
    left: 0;

    width: 100%;
    height: 100%;

    background:
        rgba(0, 0, 0, 0.18);

    pointer-events: none;

}

</style>

</head>

<body>

<div class="carrusel">
"""


# ============================================================
# INSERTAR IMÁGENES
# ============================================================

for imagen in imagenes:

    html += f"""
        <img src="{imagen}">
    """


# ============================================================
# CERRAR DIV
# ============================================================

html += """
</div>

<script>

const imagenes = document.querySelectorAll(
    '.carrusel img'
);

let indice = 0;

if (imagenes.length > 0) {

    imagenes[indice].classList.add(
        'activa'
    );

}

setInterval(function() {

    imagenes[indice].classList.remove(
        'activa'
    );

    indice++;

    if (indice >= imagenes.length) {

        indice = 0;

    }

    imagenes[indice].classList.add(
        'activa'
    );

}, DURACION);

</script>

</body>

</html>
"""


# ============================================================
# REEMPLAZAR DURACIÓN
# ============================================================

html = html.replace(
    "DURACION",
    str(duracion_imagen * 1000)
)


# ============================================================
# MOSTRAR CARRUSEL
# ============================================================

components.html(
    html,
    height=650,
    scrolling=False
)