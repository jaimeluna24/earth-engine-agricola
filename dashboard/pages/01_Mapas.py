import base64
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import streamlit as st

# ============================================================
# RUTA RAÍZ DEL PROYECTO
# ============================================================

ROOT_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
    .parent
)

if str(ROOT_DIR) not in sys.path:

    sys.path.append(
        str(ROOT_DIR)
    )

from dashboard.components.ndre_component import mostrar_ndre
from dashboard.components.ndvi_component import mostrar_ndvi
from dashboard.components.ndwi_component import mostrar_ndwi
from src.services.database_service import DatabaseService
from src.services.ee_service import EEService
from src.services.geojson_service import GeoJsonService
from src.services.map_service import MapService
from src.services.ndre_service import NDREService
from src.services.ndvi_service import NDVIService
from src.services.ndwi_service import NDWIService
from src.services.pdf_service import PDFService
from src.services.sentinel_service import SentinelService

# ============================================================
# CONFIGURACIÓN
# ============================================================
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")

st.set_page_config(
    page_title="Análisis de Cultivo",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed"
)


st.logo("src/assets/logo_achsa_dark.png")


# ============================================================
# LOGOS
# ============================================================

def cargar_logo(ruta):
    with open(ruta, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

ruta_logo_light = Path("src/assets/logo_achsa.jpg")
ruta_logo_dark = Path("src/assets/logo_achsa_dark.png")

logo_light = cargar_logo(ruta_logo_light)
logo_dark = cargar_logo(ruta_logo_dark)


# ============================================================
# ENCABEZADO
# ============================================================

col1, col2 = st.columns([8, 2])

with col1:
    st.markdown("""
        <h1 style='margin-bottom: 0px; padding-bottom: 0px;'>Análisis de Cultivo</h1>
        <p style='color: gray; margin-top: 2px; font-size: 0.85rem;'>Gerencia de Operaciones</p>
    """, unsafe_allow_html=True)

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

# ============================================================
# SESSION STATE
# ============================================================

if "datos_cargados" not in st.session_state:

    st.session_state.datos_cargados = False


if "mapas" not in st.session_state:

    st.session_state.mapas = None


if "datos_mapa" not in st.session_state:

    st.session_state.datos_mapa = None


if "pdf_prueba" not in st.session_state:

    st.session_state.pdf_prueba = None


if "pdf_filtros" not in st.session_state:

    st.session_state.pdf_filtros = None


# ============================================================
# RUTAS
# ============================================================

ruta_mapa = (
    "data/mapa_prueba.png"
)


ruta_geojson = (
    "data/geojson/"
    "fincas.geojson"
)


# ============================================================
# RANGOS
# ============================================================

RANGOS_INDICES = {

    "NDVI": [

        (
            "Crítico",
            "< 0.20",
            "#9E1114"
        ),

        (
            "Bajo",
            "0.20 – 0.40",
            "#FF9E3D"
        ),

        (
            "Medio",
            "0.40 – 0.60",
            "#FFFF9E"
        ),

        (
            "Bueno",
            "0.60 – 0.80",
            "#77D66B"
        ),

        (
            "Excelente",
            "> 0.80",
            "#2B8326"
        ),
    ],


    "NDWI": [

        (
            "Estrés Crítico",
            "< 0.05",
            "#7F0000"
        ),

        (
            "Estrés Severo",
            "0.05 – 0.15",
            "#D73027"
        ),

        (
            "Estrés Moderado",
            "0.15 – 0.25",
            "#F46D43"
        ),

        (
            "Humedad Baja",
            "0.25 – 0.35",
            "#FAC234"
        ),

        (
            "Humedad Optima",
            "0.35 – 0.45",
            "#E0FF6B"
        ),

        (
            "Vegetación Hidratada",
            "0.45 – 0.55",
            "#66BD63"
        ),

        (
            "Humedad Alta",
            "0.55 – 0.65",
            "#1A9850"
        ),

        (
            "Agua Muy Alta",
            "0.65 – 0.75",
            "#6BAED6"
        ),

        (
            "Saturación de Agua",
            "0.75 – 0.85",
            "#4292C6"
        ),

        (
            "Agua Abierta",
            "0.85 – 1.00",
            "#D9448F"
        ),
    ],


    "NDRE": [

        (
            "Crítico",
            "< 0.10",
            "#9E1114"
        ),

        (
            "Bajo",
            "0.10 – 0.20",
            "#FF9E3D"
        ),

        (
            "Medio",
            "0.20 – 0.30",
            "#FFFF9E"
        ),

        (
            "Bueno",
            "0.30 – 0.40",
            "#77D66B"
        ),

        (
            "Excelente",
            "> 0.40",
            "#2B8326"
        ),
    ]
}


# ============================================================
# PDF
# ============================================================

@st.fragment
def generar_pdf_fragmento(indice):

    datos = st.session_state.datos_mapa

    if datos is None:
        return

    filtros_actuales = (
        datos["finca"],
        indice,
        datos["fecha_fin"]
    )

    # ========================================================
    # DETECTAR CAMBIO DE FILTROS
    # ========================================================

    if (
        st.session_state.pdf_filtros
        != filtros_actuales
    ):

        st.session_state.pdf_prueba = None

        st.session_state.pdf_filtros = (
            filtros_actuales
        )

    # ========================================================
    # BOTÓN GENERAR
    # ========================================================

    if (
        not st.session_state.pdf_prueba
        and st.button(
            "Generar Documento",
            type="primary",
            key=f"generar_pdf_{indice}"
        )
    ):

        fecha_inicio = (
            datos["fecha_inicio_date"]
        )

        fecha_fin = (
            datos["fecha_fin_date"]
        )

        rangos = RANGOS_INDICES.get(
            indice,
            []
        )

        # ====================================================
        # OBTENER EL MAPA CORRESPONDIENTE
        # ====================================================

        mapa = (
            st.session_state
            .mapas[indice]
        )

        # ====================================================
        # RUTA DE IMAGEN
        # ====================================================

        ruta_mapa_indice = (
            Path("data")
            / f"mapa_{indice.lower()}.png"
        )

        # ====================================================
        # GENERAR CAPTURA DEL MAPA
        # ====================================================

        with st.spinner(
            f"Preparando mapa {indice}..."
        ):

            MapService.exportar_imagen(

                mapa,

                ruta_mapa_indice

            )

        # ====================================================
        # GENERAR PDF
        # ====================================================

        with st.spinner(
            f"Generando documento {indice}..."
        ):

            st.session_state.pdf_prueba = (

                PDFService.generar(

                    finca=datos["finca"],

                    indice=indice,

                    fecha_inicio=fecha_inicio,

                    fecha_fin=fecha_fin,

                    rangos=rangos,

                    ruta_mapa=str(
                        ruta_mapa_indice
                    )

                )
            )

        st.session_state.pdf_filtros = (
            filtros_actuales
        )

        st.rerun(
            scope="fragment"
        )

    # ========================================================
    # DESCARGAR
    # ========================================================

    if st.session_state.pdf_prueba:

        st.download_button(

            label="Descargar Documento",

            data=st.session_state.pdf_prueba,

            file_name=(
                f"mapa_{indice.lower()}.pdf"
            ),

            mime="application/pdf",

            type="primary",

            key=(
                f"descargar_pdf_{indice}"
            )
        )


# ============================================================
# FECHAS
# ============================================================

hoy = datetime.now(
    ZoneInfo(
        "America/Tegucigalpa"
    )
).date()


fecha_fin_default = hoy


fecha_inicio_default = (
    hoy - timedelta(days=7)
)


# ============================================================
# FILTROS
# ============================================================

col1, col2, col3, col4 = (
    st.columns(
        [3, 3, 1.5, 1.5]
    )
)


# ------------------------------------------------------------
# FINCA
# ------------------------------------------------------------

with col1:

    fincas = (
        GeoJsonService.obtener_fincas(
            ruta_geojson
        )
    )


    finca = st.selectbox(
        "Finca",
        fincas
    )


# ------------------------------------------------------------
# FECHA
# ------------------------------------------------------------

with col2:

    fecha_fin = st.date_input(

        "Fecha",

        value=fecha_fin_default

    )

# ------------------------------------------------------------
# PROCESAR
# ------------------------------------------------------------

with col3:

    st.markdown(
        "<p style='margin:0;'>Acción</p>",
        unsafe_allow_html=True
    )


    cargar = st.button(
        "Procesar Mapa",
        width="content"
    )


# ------------------------------------------------------------
# LOOKER
# ------------------------------------------------------------

with col4:

    st.markdown(
        "<p style='margin:0;'>Panel</p>",
        unsafe_allow_html=True
    )


    st.link_button(

        "Etapas Fenológicas",

        "https://datastudio.google.com/u/1/reporting/984ab6b1-fdf5-41a3-9bdb-133406f54efe/page/U8g5F",

        width="content"

    )


# ============================================================
# PROCESAR TODO
# ============================================================

if cargar:

    EEService.inicializar()
    fecha_inicio = (
        fecha_fin - timedelta(days=7)
    )


    if fecha_inicio > fecha_fin:

        st.error(
            "La fecha de inicio no puede "
            "ser mayor que la fecha final."
        )

        st.stop()


    fecha_inicio_str = (
        fecha_inicio.strftime(
            "%Y-%m-%d"
        )
    )


    fecha_fin_str = (
        fecha_fin.strftime(
            "%Y-%m-%d"
        )
    )


    # --------------------------------------------------------
    # GEOJSON DE LA FINCA
    # --------------------------------------------------------

    ruta_geojson_finca = (

        GeoJsonService.guardar_filtrado(

            ruta_geojson,

            finca,

            "data/geojson/"
            "temporales/"
            "finca_seleccionada.geojson"

        )
    )


    geojson = (
        GeoJsonService.cargar(
            ruta_geojson_finca
        )
    )


    # --------------------------------------------------------
    # PROCESAMIENTO
    # --------------------------------------------------------

    with st.spinner(
        "Cargando información..."
    ):

        # ====================================================
        # SENTINEL
        # ====================================================

        imagen = (
            SentinelService.obtener(

                fecha_inicio_str,

                fecha_fin_str,

                geojson

            )
        )


        if imagen is None:

            st.warning(

                "No se encontraron imágenes "
                "de Sentinel-2 para las fechas "
                "seleccionadas. Por favor, "
                "seleccione otra fecha."

            )

            st.stop()


        # ====================================================
        # COBERTURA NUBOSA
        # ====================================================

        porcentaje_nubes = (

            SentinelService.porcentaje_nubes(

                fecha_inicio_str,

                fecha_fin_str,

                geojson

            )
        )


        # ====================================================
        # CREAR LOS 3 MAPAS
        # ====================================================

        mapas = (

            MapService.crear_mapas(

                fecha_inicio_str,

                fecha_fin_str,

                ruta_geojson_finca

            )
        )


        # ====================================================
        # CALCULAR Y GUARDAR NDVI
        # ====================================================

        NDVIService.calcular_y_guardar(

            imagen,

            geojson,

            fecha_inicio_str,

            fecha_fin_str

        )


        # ====================================================
        # CALCULAR Y GUARDAR NDWI
        # ====================================================

        NDWIService.calcular_y_guardar(

            imagen,

            geojson,

            fecha_inicio_str,

            fecha_fin_str

        )


        # ====================================================
        # CALCULAR Y GUARDAR NDRE
        # ====================================================

        NDREService.calcular_y_guardar(

            imagen,

            geojson,

            fecha_inicio_str,

            fecha_fin_str

        )


        # ====================================================
        # GUARDAR EN SESSION STATE
        # ====================================================

        st.session_state.mapas = mapas


        st.session_state.datos_mapa = {

            "finca":
                finca,

            "fecha_inicio":
                fecha_inicio_str,

            "fecha_fin":
                fecha_fin_str,

            "fecha_inicio_date":
                fecha_inicio,

            "fecha_fin_date":
                fecha_fin,

            "ruta_geojson":
                ruta_geojson_finca,

            "porcentaje_nubes":
                porcentaje_nubes,
        }


        st.session_state.datos_cargados = True


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

if (
    st.session_state.datos_cargados
    and st.session_state.mapas
    and st.session_state.datos_mapa
):

    datos = (
        st.session_state.datos_mapa
    )


    # ========================================================
    # INFORMACIÓN DE NUBES
    # ========================================================

    porcentaje_nubes = (
        datos["porcentaje_nubes"]
    )


    fecha_estimada = (
        datos["fecha_fin_date"]
        - timedelta(days=7)
    )


    if porcentaje_nubes > 9:

        st.warning(

            f"La finca presenta "
            f"{porcentaje_nubes}% de cobertura "
            f"nubosa. Se recomienda buscar "
            f"con la fecha {fecha_estimada}."

        )

    else:

        st.info(

            f"La finca presenta "
            f"{porcentaje_nubes}% de cobertura nubosa."

        )


    # ========================================================
    # PESTAÑAS
    # ========================================================

    tab_ndvi, tab_ndwi, tab_ndre = (
        st.tabs(
            [
                "NDVI",
                "NDWI",
                "NDRE"
            ]
        )
    )


    # ========================================================
    # TAB NDVI
    # ========================================================

    with tab_ndvi:

        mostrar_ndvi(

            mapa=(
                st.session_state
                .mapas["NDVI"]
            ),

            finca=(
                datos["finca"]
            ),

            fecha_inicio=(
                datos["fecha_inicio"]
            ),

            fecha_fin=(
                datos["fecha_fin"]
            )

        )


        st.caption(
            "Generar Mapa en Documento PDF"
        )


        generar_pdf_fragmento("NDVI")


    # ========================================================
    # TAB NDWI
    # ========================================================

    with tab_ndwi:

        mostrar_ndwi(

            mapa=(
                st.session_state
                .mapas["NDWI"]
            ),

            finca=(
                datos["finca"]
            ),

            fecha_inicio=(
                datos["fecha_inicio"]
            ),

            fecha_fin=(
                datos["fecha_fin"]
            )

        )


        st.caption(
            "Generar Mapa en Documento PDF"
        )


        generar_pdf_fragmento("NDWI")


    # ========================================================
    # TAB NDRE
    # ========================================================

    with tab_ndre:
        
        st.caption(
            "Generar Mapa en Documento PDF"
        )
        mostrar_ndre(

            mapa=(
                st.session_state
                .mapas["NDRE"]
            ),

            finca=(
                datos["finca"]
            ),

            fecha_inicio=(
                datos["fecha_inicio"]
            ),

            fecha_fin=(
                datos["fecha_fin"]
            )

        )

        generar_pdf_fragmento("NDRE")


# ============================================================
# PIE DE PÁGINA
# ============================================================

st.markdown(
    """
    <div style="
        margin-top: 40px;
        padding-top: 12px;
        text-align: left;
        font-size: 13px;
        color: #777;
    ">
        Datos satelitales procesados mediante
        Google Earth Engine utilizando
        imágenes Sentinel-2.
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
        © 2026 Desarrollado por
        Gerencia de Operaciones - ACHSA.
    </div>
    """,
    unsafe_allow_html=True
)