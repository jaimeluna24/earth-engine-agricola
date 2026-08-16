from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


class PDFService:
    
    NOMBRES_INDICES = {
        "NDVI": "Índice de Vegetación",
        "NDWI": "Índice de Estrés Hídrico",
        "NDRE": "Índice Salud Vegetal",
    }
    
    @staticmethod
    def generar(
        finca,
        indice,
        fecha_inicio,
        fecha_fin,
        rangos,
        ruta_mapa=None
    ):
        
        nombre_indice = PDFService.NOMBRES_INDICES.get(
            indice,
            indice
        )

        titulo = f'{indice} "{nombre_indice}"'

        subtitulo = (
            f"FINCA {finca}"
        )
        
        fecha_inicio_pdf = fecha_inicio.strftime(
            "%d/%m/%Y"
        )

        fecha_fin_pdf = fecha_fin.strftime(
            "%d/%m/%Y"
        )

        periodo = (
            f"{fecha_inicio_pdf} - {fecha_fin_pdf}"
        )

        buffer = BytesIO()

        pdf = canvas.Canvas(
            buffer,
            pagesize=landscape(A4)
        )

        pdf.setTitle("Formato de mapa")

        # DIMENSIONES

        ancho, alto = landscape(A4)

        margen = 25

        # BORDE GENERAL

        pdf.setStrokeColor(colors.black)
        pdf.setLineWidth(1)

        pdf.rect(
            margen,
            margen,
            ancho - (margen * 2),
            alto - (margen * 2)
        )

        # ENCABEZADO

        alto_encabezado = 75

        y_encabezado = (
            alto
            - margen
            - alto_encabezado
        )

        pdf.line(
            margen,
            y_encabezado,
            ancho - margen,
            y_encabezado
        )

        # COLUMNAS DEL ENCABEZADO

        ancho_logo = 170
        ancho_cartografia = 180
        ancho_fecha = 180

        x_logo = ancho - margen - ancho_logo

        x_cartografia = x_logo - ancho_cartografia

        x_fecha = x_cartografia - ancho_fecha

        # Separadores verticales

        pdf.line(
            x_fecha,
            y_encabezado,
            x_fecha,
            alto - margen
        )

        pdf.line(
            x_cartografia,
            y_encabezado,
            x_cartografia,
            alto - margen
        )

        pdf.line(
            x_logo,
            y_encabezado,
            x_logo,
            alto - margen
        )

        # COLUMNA 1 — TÍTULO

        x_titulo = margen + 12

        y1 = alto - margen - 25
        y2 = alto - margen - 45

        pdf.setFont(
            "Helvetica-Bold",
            15
        )

        pdf.drawString(
            x_titulo,
            y1,
            titulo
        )

        pdf.setFont(
            "Helvetica",
            11
        )

        pdf.drawString(
            x_titulo,
            y2,
            subtitulo
        )

        # COLUMNA 2 — FECHA / GERENCIA

        x_info = x_fecha + 10

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.drawString(
            x_info,
            y1,
            "Fecha: "
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawString(
            x_info + 35,
            y1,
            periodo
        )

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.drawString(
            x_info,
            y2,
            "Gerencia de Operaciones"
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawString(
            x_info,
            y2 - 15,
            "Mapas de Análisis de Cultivo"
        )
        
        # COLUMNA 3 — INFORMACIÓN CARTOGRÁFICA

        x_carto = x_cartografia + 10

        pdf.setFont(
            "Helvetica-Bold",
            10
        )

        pdf.drawString(
            x_carto,
            y1,
            "Información Cartográfica"
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawString(
            x_carto,
            y2,
            "Sentinel-2 / G. Earth Engine"
        )

        pdf.drawString(
            x_carto,
            y2 - 13,
            "Sis. de coordenadas: WGS 84"
        )

        # COLUMNA 4 — LOGO

        ruta_logo = "src/assets/logo_achsa.jpg"

        # Área disponible para el logo

        padding_logo = 10

        area_logo_x = x_logo + padding_logo
        area_logo_y = y_encabezado + padding_logo

        area_logo_ancho = (
            ancho_logo - (padding_logo * 2)
        )

        area_logo_alto = (
            alto_encabezado - (padding_logo * 2)
        )

        # Obtener dimensiones reales de la imagen

        imagen_logo = ImageReader(
            ruta_logo
        )

        logo_ancho, logo_alto = (
            imagen_logo.getSize()
        )

        # Calcular escala manteniendo proporción

        escala = min(
            area_logo_ancho / logo_ancho,
            area_logo_alto / logo_alto
        )

        logo_ancho_final = (
            logo_ancho * escala
        )

        logo_alto_final = (
            logo_alto * escala
        )

        # Centrar dentro del contenedor

        x_logo_final = (
            area_logo_x
            + (area_logo_ancho - logo_ancho_final) / 2
        )

        y_logo_final = (
            area_logo_y
            + (area_logo_alto - logo_alto_final) / 2
        )
        
        # Dibujar logo

        pdf.drawImage(
            imagen_logo,
            x_logo_final,
            y_logo_final,
            width=logo_ancho_final,
            height=logo_alto_final,
            preserveAspectRatio=True,
            mask="auto"
        )

        # ÁREA CENTRAL DEL MAPA

        alto_pie = 25

        y_mapa = margen + alto_pie

        alto_mapa = (
            y_encabezado
            - y_mapa
        )
        
        # MAPA

        if ruta_mapa:

            imagen_mapa = ImageReader(
                ruta_mapa
            )

            pdf.drawImage(
                imagen_mapa,
                margen,
                y_mapa,
                width=ancho - (margen * 2),
                height=alto_mapa,
                preserveAspectRatio=True,
                anchor="c"
            )
            
        # BORDE DEL MAPA

        pdf.setStrokeColor(
            colors.black
        )

        pdf.setFillColor(
            colors.transparent
        )

        pdf.rect(
            margen,
            y_mapa,
            ancho - (margen * 2),
            alto_mapa,
            fill=0,
            stroke=1
        )
        
        # RANGOS

        cantidad_rangos = len(rangos)

        alto_rangos = 35 + (cantidad_rangos * 18)
        ancho_rangos = 100

        margen_rangos = 10

        x_rangos = (
            ancho
            - margen
            - ancho_rangos
            - margen_rangos
        )

        y_rangos = (
            y_mapa
            + alto_mapa
            - alto_rangos
            - margen_rangos
        )        

        # CONTENEDOR

        pdf.setFillColor(colors.white)

        pdf.setStrokeColor(colors.black)

        pdf.roundRect(
            x_rangos,
            y_rangos,
            ancho_rangos,
            alto_rangos,
            6,
            fill=1,
            stroke=1
        )

        # TÍTULO

        pdf.setFillColor(colors.black)

        pdf.setFont(
            "Helvetica-Bold",
            9
        )

        pdf.drawString(
            x_rangos + 10,
            y_rangos + alto_rangos - 18,
            "RANGOS"
        )

        # RANGOS

        x_rango = x_rangos + 10

        y_rango = (
            y_rangos
            + alto_rangos
            - 38
        )

        for _, rango, color_hex in rangos:

            # Cuadro de color
            pdf.setFillColor(
                colors.HexColor(color_hex)
            )

            pdf.rect(
                x_rango,
                y_rango,
                12,
                12,
                fill=1,
                stroke=1
            )

            # Rango numérico
            texto = rango

            x_texto = x_rango + 20
            y_texto = y_rango + 2

            # Contorno blanco
            pdf.setFont(
                "Helvetica-Bold",
                8
            )

            pdf.setFillColor(
                colors.white
            )

            desplazamiento = 0.5

            for dx, dy in [
                (-desplazamiento, 0),
                (desplazamiento, 0),
                (0, -desplazamiento),
                (0, desplazamiento),
                (-desplazamiento, -desplazamiento),
                (-desplazamiento, desplazamiento),
                (desplazamiento, -desplazamiento),
                (desplazamiento, desplazamiento),
            ]:

                pdf.drawString(
                    x_texto + dx,
                    y_texto + dy,
                    texto
                )

            # Texto principal
            pdf.setFillColor(
                colors.black
            )

            pdf.drawString(
                x_texto,
                y_texto,
                texto
            )

            y_rango -= 18
        
        # FLECHA NORTE SOBRE EL MAPA

        x_norte = margen + 35

        y_norte = (
            y_mapa
            + alto_mapa
            - 55
        )

        pdf.setFillColor(
            colors.black
        )

        pdf.setFont(
            "Helvetica-Bold",
            12
        )

        pdf.drawCentredString(
            x_norte,
            y_norte + 25,
            "N"
        )

        pdf.setLineWidth(1.5)

        pdf.line(
            x_norte,
            y_norte,
            x_norte,
            y_norte + 20
        )

        pdf.line(
            x_norte,
            y_norte + 20,
            x_norte - 5,
            y_norte + 12
        )

        pdf.line(
            x_norte,
            y_norte + 20,
            x_norte + 5,
            y_norte + 12
        )

        # ESCALA SOBRE EL MAPA

        x_escala = margen + 30

        y_escala = y_mapa + 25

        pdf.setLineWidth(2)

        pdf.line(
            x_escala,
            y_escala,
            x_escala + 100,
            y_escala
        )

        pdf.setLineWidth(1)

        pdf.line(
            x_escala,
            y_escala - 4,
            x_escala,
            y_escala + 4
        )

        pdf.line(
            x_escala + 100,
            y_escala - 4,
            x_escala + 100,
            y_escala + 4
        )

        pdf.setFont(
            "Helvetica",
            8
        )

        pdf.drawCentredString(
            x_escala + 50,
            y_escala + 7,
            "500 m"
        )

        # PIE DE PÁGINA

        pdf.setFont(
            "Helvetica",
            8
        )

        pdf.drawString(
            margen + 10,
            margen + 5,
            "Sistema de Gestión y Monitoreo de Cultivos"
        )

        pdf.drawRightString(
            ancho - margen - 10,
            margen + 5,
            "Mapa generado en SGMC"
        )

        # FINALIZAR

        pdf.save()

        buffer.seek(0)

        return buffer.getvalue()