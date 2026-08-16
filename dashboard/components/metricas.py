import streamlit as st


def mostrar(
    promedio,
    area,
    fecha,
    nubes
):

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "NDVI promedio",
        promedio
    )

    c2.metric(
        "Área",
        area
    )

    c3.metric(
        "Fecha imagen",
        fecha
    )

    c4.metric(
        "Nubosidad",
        nubes
    )