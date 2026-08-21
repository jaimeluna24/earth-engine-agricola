import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.services.database_service import DatabaseService


# Utilizados para msotrar los detalles de cada color en el mapa
rangos = RANGOS_INDICES = {
    "NDVI": [
        ("Crítico", "< 0.20", "#9E1114"),
        ("Bajo", "0.20 – 0.40", "#FF9E3D"),
        ("Medio", "0.40 – 0.60", "#FFFF9E"),
        ("Bueno", "0.60 – 0.80", "#77D66B"),
        ("Excelente", "> 0.80", "#2B8326"),
    ],
    "NDWI": [
        ("Estrés Crítico", "< 0.05", "#7F0000"),
        ("Estrés Severo", "0.05 – 0.15", "#D73027"),
        ("Estrés Moderado", "0.15 – 0.25", "#F46D43"),
        ("Humedad Baja", "0.25 – 0.35", "#FAC234"),
        ("Humedad Optima", "0.35 – 0.45", "#E0FF6B"),
        ("Vegetación Hidratada", "0.45 – 0.55", "#66BD63"),
        ("Humedad Alta", "0.55 – 0.65", "#1A9850"),
        ("Agua Muy Alta", "0.65 – 0.75", "#6BAED6"),
        ("Saturación de Agua", "0.75 – 0.85", "#4292C6"),
        ("Agua Abierta", "0.85 – 1.00", "#D9448F"),
    ],
    "NDRE": [
        ("Crítico", "< 0.10", "#9E1114"),
        ("Bajo", "0.10 – 0.20", "#FF9E3D"),
        ("Medio", "0.20 – 0.30", "#FFFF9E"),
        ("Bueno", "0.30 – 0.40", "#77D66B"),
        ("Excelente", "> 0.40", "#2B8326"),
    ],
}


def mostrar_ndre(
    mapa,
    finca,
    fecha_inicio,
    fecha_fin
):

    # =====================================================
    # MAPA
    # =====================================================

    st.subheader("Mapa NDRE")

    col_mapa, col_leyenda = st.columns([3, 1])

    with col_mapa:

        mapa.to_streamlit(
            height=700
        )

    with col_leyenda:

        st.subheader(
            "Rangos del índice"
        )

        st.caption(
            "Borde Rojo "
            "(Contenido de Clorofila / Nitrógeno)"
        )

        leyenda_ndre = {
            "#9E1114": "< 0.20 | Deficiencia severa / Zona crítica",
            "#FF9E3D": "0.20 - 0.40 | Clorofila baja / Posible clorosis",
            "#FFFF9E": "0.40 - 0.60 | Nivel de nitrógeno moderado",
            "#77D66B": "0.60 - 0.80 | Cultivo saludable y verde",
            "#2B8326": "> 0.80 | Nutrición excelente / Alta densidad"
        }
            
        for color, texto in leyenda_ndre.items():
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <div style="background-color: {color}; width: 24px; height: 24px; border-radius: 4px; margin-right: 12px; border: 1px solid #555;"></div>
                    <span style="font-size: 14px; font-weight: 500;">{texto}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )

    # =====================================================
    # DATOS
    # =====================================================

    st.divider()

    st.subheader(
        "Datos de NDRE por Finca"
    )

    datos = DatabaseService.obtener_ndre(
        finca,
        fecha_inicio,
        fecha_fin
    )

    if datos.empty:

        st.info(
            "No existen datos de NDRE para "
            "la finca y fechas seleccionadas."
        )

        return

    # =====================================================
    # HISTÓRICO
    # =====================================================

    historico = DatabaseService.obtener_historico_ndre(
        finca
    )

    historico["Fecha"] = pd.to_datetime(
        historico["Fecha"]
    )

    historico["Mes"] = (
        historico["Fecha"]
        .dt.to_period("M")
    )

    historico["Prom_Ponderado"] = (
        historico["Prom"]
        * historico["Area"]
    )

    mensual = historico.groupby("Mes").agg(
        Min=("Min", "min"),
        Max=("Max", "max"),
        Area=("Area", "sum"),
        Prom_Ponderado=("Prom_Ponderado", "sum")
    ).reset_index()

    mensual["Prom"] = (
        mensual["Prom_Ponderado"]
        / mensual["Area"]
    )

    mensual["Mes"] = (
        mensual["Mes"]
        .dt.strftime("%Y-%m")
    )

    # =====================================================
    # MÉTRICAS
    # =====================================================

    area_total = datos["Area"].sum()

    area_ha = (
        area_total / 10000
    )

    promedio = (
        (
            datos["Area"]
            * datos["Prom"]
        ).sum()
        / area_total
    )

    minimo = datos["Min"].min()

    maximo = datos["Max"].max()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.markdown(
            f"""
            <div style="
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                background-color: #2B8326;
            ">
                <div style="font-size: 1.1em;">Área total</div>
                <div style="font-size: 1.6em; font-weight: semibold;">{area_ha:,.2f} ha</div>      
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        st.markdown(
            f"""
            <div style="
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                background-color: #FFFF9E ;
                color: #000000;
            ">
                <div style="font-size: 1.1em;">Promedio</div>
                <div style="font-size: 1.6em; font-weight: semibold;">{promedio:.2f}</div>      
            </div>
            """,
            unsafe_allow_html=True
        )     

    with col3:

        st.markdown(
            f"""
            <div style="
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
                 text-align: center;
                background-color: #9E1114 ;
            ">
                <div style="font-size: 1.1em;">Mínimo</div>
                <div style="font-size: 1.6em; font-weight: semibold;">{minimo:.2f}</div>      
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:

        st.markdown(
            f"""
            <div style="
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 12px;
                text-align: center;
                background-color: #77D66B ;
            ">
                <div style="font-size: 1.1em;">Máximo</div>
                <div style="font-size: 1.6em; font-weight: semibold;">{maximo:.2f}</div>      
            </div>
             """,
             unsafe_allow_html=True
        )

    # =====================================================
    # ÁREAS
    # =====================================================

    estados = [
        "Crítico",
        "Bajo",
        "Medio",
        "Bueno",
        "Excelente"
    ]

    columnas = [
        "Crítico",
        "Bajo",
        "Medio",
        "Bueno",
        "Excelente"
    ]

    areas = []

    for columna in columnas:

        area = (
            datos["Area"]
            * datos[columna]
            / 100
        ).sum() / 10000

        areas.append(area)

    porcentajes = [
        (area / area_ha) * 100
        for area in areas
    ]

    textos = [
        f"{area:,.2f} ha · {porcentaje:.1f}%"
        for area, porcentaje
        in zip(areas, porcentajes)
    ]

    fig = go.Figure(
        go.Bar(
            x=areas,
            y=estados,
            orientation="h",
            text=textos,
            textposition="outside",
            marker_color=[
                "#9E1114",
                "#FF9E3D",
                "#FFFF9E",
                "#77D66B",
                "#2B8326"
            ]
        )
    )

    fig.update_layout(
        title="Distribución del área por estado",
        xaxis_title="Área (ha)",
        yaxis_title="",
        height=400,
        showlegend=False
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # =====================================================
    # RANGOS
    # =====================================================

    st.subheader(
        "Rangos del índice"
    )

    rangos = RANGOS_INDICES.get("NDRE", [])

    cols = st.columns(5)

    for col, (estado, rango, color) in zip(cols, rangos):

        with col:

            st.markdown(
                f"""
                <div style="
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 12px;
                    text-align: center;
                ">
                <div style="
                    width: 14px;
                    height: 14px;
                    background-color: {color};
                    border-radius: 50%;
                    margin: 0 auto 8px auto;
                ">
                </div>
                <div>
                    <strong>{rango}</strong>
                </div>
                <div>
                    {estado}
                </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================================
    # TABLA
    # =====================================================

    st.subheader(
        "Estadísticas"
    )

    st.dataframe(
        datos,
        width="stretch",
        hide_index=True
    )

    # =====================================================
    # HISTÓRICO
    # =====================================================

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=mensual["Mes"],
            y=mensual["Min"],
            mode="lines+markers",
            name="Mínimo"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=mensual["Mes"],
            y=mensual["Prom"],
            mode="lines+markers",
            name="Promedio"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=mensual["Mes"],
            y=mensual["Max"],
            mode="lines+markers",
            name="Máximo"
        )
    )

    fig.update_layout(
        title="Evolución mensual del NDRE",
        xaxis_title="Mes",
        yaxis_title="NDRE",
        height=450,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )