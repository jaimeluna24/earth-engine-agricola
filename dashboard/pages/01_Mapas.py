import base64
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.services.database_service import DatabaseService
from src.services.geojson_service import GeoJsonService
from src.services.map_service import MapService
from src.services.ndre_service import NDREService
from src.services.ndvi_service import NDVIService
from src.services.ndwi_service import NDWIService
from src.services.pdf_service import PDFService
from src.services.sentinel_service import SentinelService


def cargar_logo(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

ruta_logo_light = Path("src/assets/logo_achsa.jpg")
ruta_logo_dark = Path("src/assets/logo_achsa_dark.png")

logo_light = cargar_logo(ruta_logo_light)
logo_dark = cargar_logo(ruta_logo_dark)

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.set_page_config(
    page_title="Análisis de Cultivo",
    page_icon="",
    layout="wide"
)

st.logo("src/assets/logo_achsa_dark.png")

col1, col2 = st.columns([8, 2])

with col1:
    st.title("Análisis de Cultivo")

with col2:
    st.markdown(
        f"""
        <div style="
            display: flex;
            justify-content: flex-end;
            align-items: center;
            height: 100%;
        ">
            <img 
                src="data:image/png;base64,{logo_dark}"
                style="
                    height: 55px;
                    width: auto;
                    object-fit: contain;
                "
            />
        </div>
        """,
        unsafe_allow_html=True
    )

if "datos_cargados" not in st.session_state:
    st.session_state.datos_cargados = False

if "pdf_prueba" not in st.session_state:
    st.session_state.pdf_prueba = None
    
if "pdf_filtros" not in st.session_state:
    st.session_state.pdf_filtros = None

ruta_mapa = "data/mapa_prueba.png"

ruta_geojson = (
        "data/geojson/"
        "fincas.geojson"
    )

@st.fragment
def generar_pdf_fragmento():

    filtros_actuales = (
        finca,
        indice,
        fecha_fin
    )

    # Comprobació de filtros

    if (
        st.session_state.pdf_filtros
        != filtros_actuales
    ):

        st.session_state.pdf_prueba = None

        st.session_state.pdf_filtros = (
            filtros_actuales
        )

    # Generación del pdf para descargar
    
    if not st.session_state.pdf_prueba and st.button("Generar Documento", type="primary"):

            fecha_inicio = (
                fecha_fin
                - timedelta(days=7)
            )

            rangos = RANGOS_INDICES.get(
                indice,
                []
            )

            st.session_state.pdf_prueba = (
                PDFService.generar(
                    finca=finca,
                    indice=indice,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    rangos=rangos,
                    ruta_mapa=ruta_mapa
                )
            )

            st.session_state.pdf_filtros = (
                filtros_actuales
            )

            st.rerun(scope="fragment")

    # Descarga de pdf

    if st.session_state.pdf_prueba:

        st.download_button(
            label="Descargar Documento",
            data=st.session_state.pdf_prueba,
            file_name="mapa_prueba.pdf",
            mime="application/pdf",
            type="primary"
        )


# Obtiene la fecha actual usando la zona horaria local
hoy = datetime.now(ZoneInfo("America/Tegucigalpa")).date()

fecha_fin_default = hoy

fecha_inicio_default = hoy - timedelta(days=7)

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

# área de filtros 
col1, col2, col3, col4, col5 = st.columns([2,2,2,1,1])

with col1:
    fincas = GeoJsonService.obtener_fincas(
        ruta_geojson
    )

    finca = st.selectbox(
        "Finca",
        fincas
    )

with col2:
    fecha_fin = st.date_input(
        "Fecha",
        value=fecha_fin_default
    )

with col3:
    indice = st.selectbox(
        "Índice",
        [
            "NDVI",
            "NDWI",
            "NDRE"
        ]
    )

# Boton de procesar mapa
with col4:
    st.markdown(
        "<p style='margin:0;'>Cargar</p>",
        unsafe_allow_html=True
    )
    cargar = st.button(
        "Procesar Mapa",
        width='content',
)
    
# Redirección a Looker
with col5:
    st.markdown(
        "<p style='margin:0;'>Panel</p>",
        unsafe_allow_html=True
    )

    st.link_button(
        "Ir a Looker",
        "https://datastudio.google.com/u/1/reporting/984ab6b1-fdf5-41a3-9bdb-133406f54efe/page/U8g5F",
        width="content"
    )

# Validaciones de fecha
if cargar:
    st.session_state.datos_cargados = True
    
    fecha_inicio = fecha_fin - timedelta(days=7)
    
    if fecha_inicio > fecha_fin:

        st.error(
            "La fecha de inicio no puede ser mayor "
            "que la fecha final."
        )
        st.stop()

    # FECHAS PARA EARTH ENGINE / MYSQL
    fecha_inicio_str = fecha_inicio.strftime(
        "%Y-%m-%d"
    )

    fecha_fin_str = fecha_fin.strftime(
        "%Y-%m-%d"
    )
    
    fecha_estimada = fecha_fin - timedelta(days=7)

    # Geojson temporal creado para mostrar la finca seleccionada de maestro
    ruta_geojson_finca = GeoJsonService.guardar_filtrado(
        ruta_geojson,
        finca,
        "data/geojson/temporales/finca_seleccionada.geojson"
    )
    
    # Apartado de la generación del mapa
    with st.spinner(
        "Cargando mapa..."
    ):
        
        mapa = MapService.crear()
        
        mapa = MapService.agregar_sentinel(
            mapa,
            fecha_inicio_str,
            fecha_fin_str,
            ruta_geojson_finca
        )

        # Bloque que muestra según el tipo de mapa escogido
        if indice == "NDVI":

            mapa = MapService.agregar_ndvi_rangos(
                mapa,
                fecha_inicio_str,
                fecha_fin_str,
                ruta_geojson_finca
            )

        elif indice == "NDWI":
            
            mapa = MapService.agregar_ndwi_rangos(
                mapa,
                fecha_inicio_str,
                fecha_fin_str,
                ruta_geojson_finca
            )

        elif indice == "NDRE":

            mapa = MapService.agregar_ndre_rangos(
                mapa,
                fecha_inicio_str,
                fecha_fin_str,
                ruta_geojson_finca
            )
        
        if mapa is None:
            st.warning(
                "No se encontraron imágenes de Sentinel-2 para las fechas seleccionadas. Por favor, seleccione otra fecha."
            )
            st.stop()

        # Carga los poligonos para seccionar los lotes en el mapa
        mapa = MapService.agregar_lotes(
            mapa,
            ruta_geojson_finca
        )

        MapService.exportar_imagen(
            mapa,
            ruta_mapa
        )
        
    # Calculos para los datos NDVI, NDWI y NDRE y almacenarlos en la DB
    if indice == "NDVI":

        with st.spinner(
            "Calculando NDVI por lotes..."
        ):

            geojson = GeoJsonService.cargar(
                ruta_geojson_finca
            )
            
            porcentaje_nubes = (
                SentinelService.porcentaje_nubes(
                    fecha_inicio_str,
                    fecha_fin_str,
                    geojson
                )
            )

            if porcentaje_nubes > 1 and porcentaje_nubes < 10:

                st.warning(
                    f"La finca presenta "
                    f"{porcentaje_nubes}% de cobertura nubosa. "
                    f"Se recomienda buscar con la fecha {fecha_estimada}"
                )
                
            if porcentaje_nubes < 10:
            
                st.warning(
                    f"La finca presenta "
                    f"{porcentaje_nubes}% de cobertura nubosa. "
                )

            imagen = SentinelService.obtener(
                fecha_inicio_str,
                fecha_fin_str,
                geojson
            )


            resultados = NDVIService.calcular_y_guardar(
                imagen,
                geojson,
                fecha_inicio_str,
                fecha_fin_str
            )
            
    elif indice == "NDWI":

        with st.spinner(
            "Calculando NDWI por lotes..."
        ):

            geojson = GeoJsonService.cargar(
                ruta_geojson_finca
            )
            
            porcentaje_nubes = (
                SentinelService.porcentaje_nubes(
                    fecha_inicio_str,
                    fecha_fin_str,
                    geojson
                )
            )

            if porcentaje_nubes > 10:
            
                st.warning(
                    f"La finca presenta "
                    f"{porcentaje_nubes}% de cobertura nubosa. "
                    f"Se recomienda buscar con la fecha {fecha_estimada}"
                )
                            
            if porcentaje_nubes > 1 and porcentaje_nubes < 10:
                        
                st.warning(
                    f"La finca presenta "
                    f"{porcentaje_nubes}% de cobertura nubosa. "
            )
                
            imagen = SentinelService.obtener(
                fecha_inicio_str,
                fecha_fin_str,
                geojson
            )

            resultados = NDWIService.calcular_y_guardar(
                imagen,
                geojson,
                fecha_inicio_str,
                fecha_fin_str
            )
            
    elif indice == "NDRE":

        with st.spinner(
            "Calculando NDRE por lotes..."
        ):

            geojson = GeoJsonService.cargar(
                ruta_geojson_finca
            )

            porcentaje_nubes = (
                SentinelService.porcentaje_nubes(
                    fecha_inicio_str,
                    fecha_fin_str,
                    geojson
                )
            )

            if porcentaje_nubes > 10:
 
                 st.warning(
                     f"La finca presenta "
                     f"{porcentaje_nubes}% de cobertura nubosa. "
                     f"Se recomienda buscar con la fecha {fecha_estimada}"
                 )
                 
            if porcentaje_nubes > 1 and porcentaje_nubes < 10:
             
                 st.warning(
                     f"La finca presenta "
                     f"{porcentaje_nubes}% de cobertura nubosa. "
                 )           
                

            imagen = SentinelService.obtener(
                fecha_inicio_str,
                fecha_fin_str,
                geojson
            )

            resultados = NDREService.calcular_y_guardar(
                imagen,
                geojson,
                fecha_inicio_str,
                fecha_fin_str
            )
            
    # Apartado donde se carga el mapa y sus leyendas
    st.subheader(
        "Mapa"
    )

    col1, col2 = st.columns([3,1])
    
    with col1:

        mapa.to_streamlit(
            height=700
        )
        
    with col2:
        st.subheader(
                "Rangos del índice"
            )
        
        if indice == "NDVI":
            st.caption("Vegetación (Vigor y Biomasa)")
            
            # Leyendas del mapa y sus rangos
            leyenda_ndvi = {
                "#9E1114": "0.00 - 0.20 | Suelo desnudo / Cultivo seco",
                "#FF9E3D": "0.20 - 0.40 | Vegetación muy escasa o brotes",
                "#FFFF9E": "0.40 - 0.55 | Crecimiento moderado / Desarrollo",
                "#77D66B": "0.55 - 0.70 | Vegetación saludable / Buen desarrollo",
                "#2B8326": "0.70 - 1.00 | Dosel completo / Máximo vigor"
            }
            
            for color, texto in leyenda_ndvi.items():
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <div style="background-color: {color}; width: 24px; height: 24px; border-radius: 4px; margin-right: 12px; border: 1px solid #555;"></div>
                        <span style="font-size: 14px; font-weight: 500;">{texto}</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
            if st.session_state.datos_cargados:
                st.caption("Generar Mapa en Documento PDF")
                generar_pdf_fragmento()

        elif indice == "NDWI":
            st.caption("Humedad Agrícola (Contenido de agua en hojas)")
            
            leyenda_ndwi = {
                "#7F0000": "-1.00 a 0.05 | Estrés hídrico crítico",
                "#D73027": "0.05 a 0.15 | Estrés hídrico severo",
                "#F46D43": "0.15 a 0.25 | Estrés hídrico moderado",
                "#FAC234": "0.25 a  0.35 | Humedad ligeramente baja",
                "#E0FF6B": "0.35 a  0.45 | Humedad óptima de transición",
                "#66BD63": "0.45 a  0.55 | Vegetación bien hidratada",
                "#1A9850": "0.55 a  0.65 | Humedad alta / Excelente riego",
                "#6BAED6": "0.65 a  0.75 | Contenido de agua muy alto",
                "#4292C6": "0.75 a  0.85 | Saturación de agua / Charco",
                "#D9448F": "0.85 a  1.00 | Agua abierta detectada"
            }
            
            for color, texto in leyenda_ndwi.items():
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center; margin-bottom: 6px;">
                        <div style="background-color: {color}; width: 24px; height: 20px; border-radius: 3px; margin-right: 12px; border: 1px solid #555;"></div>
                        <span style="font-size: 13px; font-weight: 500;">{texto}</span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
            
            if st.session_state.datos_cargados:
                st.caption("Generar Mapa en Documento PDF")
                generar_pdf_fragmento()
                
        elif indice == "NDRE":
            st.caption("Borde Rojo (Contenido de Clorofila / Nitrógeno)")
            
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

            if st.session_state.datos_cargados:
                st.caption("Generar Mapa en Documento PDF")
                generar_pdf_fragmento()

    # Apartado estadistico de los mapas segun el mapa seleccionado
    if indice == "NDVI":

        st.subheader(
            "Datos de NDVI por Finca"
        )

        datos = DatabaseService.obtener_ndvi(
            finca,
            fecha_inicio_str,
            fecha_fin_str
        )
        
        historico = DatabaseService.obtener_historico_ndvi(finca)
        historico["Fecha"] = pd.to_datetime(
            historico["Fecha"]
        )
                    
        historico["Mes"] = historico["Fecha"].dt.to_period("M")
        
        historico["Prom_Ponderado"] = (
            historico["Prom"] * historico["Area"]
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
        
        mensual["Mes"] = mensual["Mes"].dt.strftime("%Y-%m")
                
        if datos.empty:

            st.info(
                "No existen datos de NDVI para "
                "la finca y fechas seleccionadas."
            )

        else:
            area_total = datos["Area"].sum()
            area_ha = area_total / 10000
            promedio = (
                (datos["Area"] * datos["Prom"]).sum()
                / area_total
            )

            minimo = datos["Min"].min()
            maximo = datos["Max"].max()
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Cards estadisticas
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
            
            # Calculos de conversión del área
            area_critica = (
                datos["Area"] * datos["Crítico"] / 100
            ).sum() / 10000

            area_baja = (
                datos["Area"] * datos["Bajo"] / 100
            ).sum() / 10000

            area_media = (
                datos["Area"] * datos["Medio"] / 100
            ).sum() / 10000

            area_buena = (
                datos["Area"] * datos["Bueno"] / 100
            ).sum() / 10000

            area_excelente = (
                datos["Area"] * datos["Excelente"] / 100
            ).sum() / 10000

            area_total = (
                area_critica
                + area_baja
                + area_media
                + area_buena
                + area_excelente
            )

            estados = [
                "Crítico",
                "Bajo",
                "Medio",
                "Bueno",
                "Excelente"
            ]

            areas = [
                area_critica,
                area_baja,
                area_media,
                area_buena,
                area_excelente
            ]

            porcentajes = [
                (area / area_ha) * 100
                for area in areas
            ]

            textos = [
                f"{area:,.2f} ha · {porcentaje:.1f}%"
                for area, porcentaje in zip(areas, porcentajes)
            ]
            
            # área de grafico
            fig = go.Figure(
                go.Bar(
                    x=areas,
                    y=estados,
                    orientation="h",
                    text=textos,
                    textposition="outside",
                    marker_color=[
                        "#9E1114",  # Crítico
                        "#FF9E3D",  # Bajo
                        "#FFFF9E",  # Medio
                        "#77D66B",  # Bueno
                        "#2B8326"   # Excelente
                    ]
                )
            )

            fig.update_layout(
                title="Distribución del área por estado",
                xaxis_title="Área (ha)",
                yaxis_title="",
                height=400,
                showlegend=False,
                margin={
                    "l": 20,
                    "r": 20,
                    "t": 60,
                    "b": 40,
                },
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )
            
            st.subheader("Rangos del índice")
            
            rangos = RANGOS_INDICES.get(indice, [])

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

            # Tabla de datos generados
            st.subheader("Estadísticas")
            
            st.dataframe(
                datos,
                width='stretch',
                hide_index=True
            )
            
            # Grafico de lineas
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
                title="Evolución mensual del NDVI",
                xaxis_title="Mes",
                yaxis_title="NDVI",
                height=450,
                hovermode="x unified"
            )
            
            st.plotly_chart(
                fig,
                width="stretch"
            )

            
    elif indice == "NDWI":

        st.subheader(
            "Datos de NDWI por Finca"
        )

        datos = DatabaseService.obtener_ndwi(
            finca,
            fecha_inicio_str,
            fecha_fin_str
        )
        
        historico = DatabaseService.obtener_historico_ndwi(finca)
        historico["Fecha"] = pd.to_datetime(
            historico["Fecha"]
        )
                    
        historico["Mes"] = historico["Fecha"].dt.to_period("M")
        
        historico["Prom_Ponderado"] = (
            historico["Prom"] * historico["Area"]
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
        
        mensual["Mes"] = mensual["Mes"].dt.strftime("%Y-%m")        

        if datos.empty:

            st.info(
                "No existen datos de NDWI para "
                "la finca y fechas seleccionadas."
            )
        else:
            area_total = datos["Area"].sum()
            area_ha = area_total / 10000
            promedio = (
                (datos["Area"] * datos["Prom"]).sum()
                / area_total
            )

            minimo = datos["Min"].min()
            maximo = datos["Max"].max()
            
            col1, col2, col3, col4 = st.columns(4)
            # Cards estadisticas NDWI
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
            # Calculos de área NDWI
            estres_critico = (
                datos["Area"] * datos["Estrés Crítico"] / 100
            ).sum() / 10000

            estres_severo = (
                datos["Area"] * datos["Estrés Severo"] / 100
            ).sum() / 10000

            estres_moderado = (
                datos["Area"] * datos["Estrés Moderado"] / 100
            ).sum() / 10000

            humedad_optima = (
                datos["Area"] * datos["Humedad Optima"] / 100
            ).sum() / 10000

            vegetacion_hidratada = (
                datos["Area"] * datos["Vegetación Hidratada"] / 100
            ).sum() / 10000
            
            humedad_alta = (
                datos["Area"] * datos["Humedad Alta"] / 100
            ).sum() / 10000
            
            agua_alta = (
                datos["Area"] * datos["Agua Muy Alta"] / 100
            ).sum() / 10000
            
            saturacion_agua = (
                datos["Area"] * datos["Saturación de Agua"] / 100
            ).sum() / 10000
            
            agua_abierta = (
                datos["Area"] * datos["Agua Abierta"] / 100
            ).sum() / 10000

            area_total = (
                estres_critico
                + estres_severo
                + estres_moderado
                + humedad_optima
                + vegetacion_hidratada
                + humedad_alta
                + agua_alta
                + saturacion_agua
                + agua_abierta
            )

            estados = [
                "Estrés Crítico",
                "Estrés Severo",
                "Estrés Moderado",
                "Humedad Optima",
                "Vegetación Hidratada",
                "Humedad Alta",
                "Agua Muy Alta",
                "Saturación de Agua",
                "Agua Abierta"
            ]

            areas = [
                estres_critico,
                estres_severo,
                estres_moderado,
                humedad_optima,
                vegetacion_hidratada,
                humedad_alta,
                agua_alta,
                saturacion_agua,
                agua_abierta
            ]

            porcentajes = [
                (area / area_ha) * 100
                for area in areas
            ]

            textos = [
                f"{area:,.2f} ha · {porcentaje:.1f}%"
                for area, porcentaje in zip(areas, porcentajes)
            ]

            # Grafico de barras
            fig = go.Figure(
                go.Bar(
                    x=areas,
                    y=estados,
                    orientation="h",
                    text=textos,
                    textposition="outside",
                    marker_color=[
                        "#7F0000",
                        "#D73027",
                        "#F46D43",
                        "#FAC234",
                        "#E0FF6B",
                        "#66BD63",
                        "#1A9850",
                        "#6BAED6",
                        "#4292C6",
                        "#D9448F"
                    ]
                )
            )

            fig.update_layout(
                title="Distribución del área por estado",
                xaxis_title="Área (ha)",
                yaxis_title="",
                height=400,
                showlegend=False,
                margin={
                    "l": 20,
                    "r": 20,
                    "t": 60,
                    "b": 40,
                },
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )
            
            st.subheader("Rangos del índice")
            
            rangos = RANGOS_INDICES.get(indice, [])

            cols = st.columns(10)

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
                            <div>{rango}</div>
                            <div>{estado}</div>      
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
            st.subheader("Estadísticas")
            
            # Tabla de datos 
            st.dataframe(
                datos,
                width='content',
                hide_index=True
            )
            
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
                title="Evolución mensual del NDWI",
                xaxis_title="Mes",
                yaxis_title="NDWI",
                height=450,
                hovermode="x unified"
            )
            
            st.plotly_chart(
                fig,
                width="stretch"
            )

           
            
    elif indice == "NDRE":
    
        st.subheader(
            "Datos de NDRE por lote"
        )
    
        datos = DatabaseService.obtener_ndre(
            finca,
            fecha_inicio_str,
            fecha_fin_str
         )
    
        historico = DatabaseService.obtener_historico_ndre(finca)
        historico["Fecha"] = pd.to_datetime(
            historico["Fecha"]
        )
                        
        historico["Mes"] = historico["Fecha"].dt.to_period("M")
            
        historico["Prom_Ponderado"] = (
            historico["Prom"] * historico["Area"]
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
            
        mensual["Mes"] = mensual["Mes"].dt.strftime("%Y-%m")

        if datos.empty:

            st.info(
                "No existen datos de NDRE para "
                "la finca y fechas seleccionadas."
            )
    
        else:

            area_total = datos["Area"].sum()
            area_ha = area_total / 10000
            promedio = (
                (datos["Area"] * datos["Prom"]).sum()
                / area_total
            )

            minimo = datos["Min"].min()
            maximo = datos["Max"].max()
            
            col1, col2, col3, col4 = st.columns(4)
            # Cards estadisticas NDRE 
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
            
            # Calculos de area
            area_critica = (
                datos["Area"] * datos["Crítico"] / 100
            ).sum() / 10000

            area_baja = (
                datos["Area"] * datos["Bajo"] / 100
            ).sum() / 10000

            area_media = (
                datos["Area"] * datos["Medio"] / 100
            ).sum() / 10000

            area_buena = (
                datos["Area"] * datos["Bueno"] / 100
            ).sum() / 10000

            area_excelente = (
                datos["Area"] * datos["Excelente"] / 100
            ).sum() / 10000

            area_total = (
                area_critica
                + area_baja
                + area_media
                + area_buena
                + area_excelente
            )

            estados = [
                "Crítico",
                "Bajo",
                "Medio",
                "Bueno",
                "Excelente"
            ]

            areas = [
                area_critica,
                area_baja,
                area_media,
                area_buena,
                area_excelente
            ]

            porcentajes = [
                (area / area_ha) * 100
                for area in areas
            ]

            textos = [
                f"{area:,.2f} ha · {porcentaje:.1f}%"
                for area, porcentaje in zip(areas, porcentajes)
            ]
            
            # Grafico de barras
            fig = go.Figure(
                go.Bar(
                    x=areas,
                    y=estados,
                    orientation="h",
                    text=textos,
                    textposition="outside",
                    marker_color=[
                        "#9E1114",  # Crítico
                        "#FF9E3D",  # Bajo
                        "#FFFF9E",  # Medio
                        "#77D66B",  # Bueno
                        "#2B8326"   # Excelente
                    ]
                )
            )

            fig.update_layout(
                title="Distribución del área por estado",
                xaxis_title="Área (ha)",
                yaxis_title="",
                height=400,
                showlegend=False,
                margin={
                    "l": 20,
                    "r": 20,
                    "t": 60,
                    "b": 40,
                },
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )
            
            st.subheader("Rangos del índice")
            
            rangos = RANGOS_INDICES.get(indice, [])

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
                    
            st.subheader("Estadísticas")
            # Tabla de datos
            st.dataframe(
                datos,
                width='stretch',
                hide_index=True
            )
            
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

# Pie de pagina
st.markdown(
    """
    <div style="
        margin-top: 40px;
        padding-top: 12px;
        text-align: left;
        font-size: 13px;
        color: #777;
    ">
        Datos satelitales procesados mediante Google Earth Engine
        utilizando imágenes Sentinel-2.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        text-align: center;
        padding-top: 12px;
        margin-top: 40px;
        font-size: 14px;
        color: gray;
        border-top: 1px solid #dcdcdc;
    ">
        Sistema de Gestión y Monitoreo de Cultivos
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style="
        text-align: center;
        font-size: 14px;
        color: gray;
    ">
        © 2026 Desarrollado por Gerencia de Operaciones - ACHSA.
    </div>
    """,
    unsafe_allow_html=True
)
