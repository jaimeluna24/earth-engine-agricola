import asyncio
import os
from pathlib import Path

import ee
import folium
import leafmap.foliumap as leafmap
from playwright.async_api import async_playwright

from src.services.ee_service import EEService
from src.services.geojson_service import GeoJsonService
from src.services.indices_service import IndicesService
from src.services.sentinel_service import SentinelService


class MapService:


    @staticmethod
    def crear():

        EEService.inicializar()

        mapa = leafmap.Map()
        mapa.add_basemap("SATELLITE")

        return mapa


    @staticmethod
    def agregar_sentinel(
        mapa,
        fecha_inicio,
        fecha_fin,
        ruta_geojson
    ):

        geojson = GeoJsonService.cargar(
            ruta_geojson
        )


        imagen = SentinelService.obtener(
            fecha_inicio,
            fecha_fin,
            geojson
        )
        
        if imagen is None:
            
            return None


        vis_params = {
            "bands": [
                "B4",
                "B3",
                "B2"
            ],
            "min": 0,
            "max": 5000
        }


        map_id = imagen.getMapId(
            vis_params
        )


        mapa.add_tile_layer(
            map_id["tile_fetcher"].url_format,
            name="Sentinel RGB",
            attribution="Google Earth Engine"
        )


        return mapa
    
    @staticmethod 
    def agregar_ndvi( mapa, fecha_inicio, fecha_fin, ruta_geojson ): 
        geojson = GeoJsonService.cargar( ruta_geojson ) 
        imagen = SentinelService.obtener( fecha_inicio, fecha_fin, geojson ) 
        ndvi = IndicesService.ndvi( imagen ) 
        vis_params = { "min": 0, "max": 1, "palette": [ "#9E1114", "#FF9E3D", "#FFFF9E", "#77D66B", "#2B8326" ] } 
        map_id = ndvi.getMapId( vis_params ) 
        mapa.add_tile_layer( map_id["tile_fetcher"].url_format, name="NDVI", attribution="Google Earth Engine" ) 
        return mapa


    @staticmethod 
    def agregar_ndwi( mapa, fecha_inicio, fecha_fin, ruta_geojson ): 
        geojson = GeoJsonService.cargar( ruta_geojson ) 
        imagen = SentinelService.obtener( fecha_inicio, fecha_fin, geojson ) 
        ndwi = IndicesService.ndwi( imagen ) 
        vis_params = {
            "min": -1,
            "max": 1,
            "palette": [
                "#BA0800",  # Muy dañado
                "#6B3E2B",  # Dañado
                "#E76F51",  # Daño moderado
                "#D16B1B",  # Estrés
                "#DDF540",  # Amarillo
                "#ADE8A0",  # Transición
                "#258CE6",  # Vegetación moderada
                "#70D5F7",  # Vegetación saludable
                "#3D2675",  # Saludable
                "#D9448F"   # Muy saludable
            ]
        } 
        map_id = ndwi.getMapId( vis_params ) 
        mapa.add_tile_layer( map_id["tile_fetcher"].url_format, name="NDWI", attribution="Google Earth Engine" ) 
        return mapa

    @staticmethod
    def agregar_nre( mapa, fecha_inicio, fecha_fin, ruta_geojson ): 
        geojson = GeoJsonService.cargar( ruta_geojson ) 
        imagen = SentinelService.obtener( fecha_inicio, fecha_fin, geojson ) 
        nre = IndicesService.nre( imagen ) 
        vis_params = { "min": 0, "max": 1, "palette": [ "#9E1114", "#FF9E3D", "#FFFF9E", "#77D66B", "#2B8326" ] } 
        map_id = nre.getMapId( vis_params ) 
        mapa.add_tile_layer( map_id["tile_fetcher"].url_format, name="NRE", attribution="Google Earth Engine" ) 
        return mapa

    @staticmethod
    def agregar_lotes(
        mapa,
        ruta_geojson
    ):

        geojson = GeoJsonService.cargar(
            ruta_geojson
        )

        # Dibujar límites de los lotes
        mapa.add_geojson(
            geojson,
            layer_name="Lotes",
            info_mode=None,
            style={
                "color": "black",
                "weight": 2,
                "fillOpacity": 0
            }
        )

        # Agregar etiquetas de texto
        for feature in geojson["features"]:

            propiedades = feature.get(
                "properties",
                {}
            )

            lote = (
                propiedades.get("LOTE")
                or propiedades.get("name")
                or propiedades.get("LOTE_ID")
            )

            if not lote:
                continue

            geometria = ee.Geometry(
                feature["geometry"]
            )

            centroide = geometria.centroid()

            coordenadas = (
                centroide
                .coordinates()
                .getInfo()
            )

            lon = coordenadas[0]
            lat = coordenadas[1]

            folium.Marker(
                location=[
                    lat,
                    lon
                ],
                icon=folium.DivIcon(
                    html=f"""
                    <div style="
                        font-size: 12px;
                        font-weight: bold;
                        color: white;
                        text-align: center;
                        text-shadow:
                            -1px -1px 2px black,
                            1px -1px 2px black,
                            -1px  1px 2px black,
                            1px  1px 2px black;
                        white-space: nowrap;
                    ">
                        {lote}
                    </div>
                    """
                )
            ).add_to(mapa)

        return mapa
    
    @staticmethod
    def agregar_ndvi_raster(
        mapa,
        fecha_inicio,
        fecha_fin,
        ruta_geojson
    ):

        geojson = GeoJsonService.cargar(
            ruta_geojson
        )


        imagen = SentinelService.obtener(
            fecha_inicio,
            fecha_fin,
            geojson
        )

        # NDVI = (NIR - RED) / (NIR + RED)
        ndvi = imagen.normalizedDifference(
            [
                "B8",
                "B4"
            ]
        ).rename(
            "NDVI"
        )


        vis_params = {
            "min": 0,
            "max": 1,
            "palette": [
               "#9E1114", "#FF9E3D", "#FFFF9E", "#77D66B", "#2B8326"
            ]
        }


        map_id = ndvi.getMapId(
            vis_params
        )


        mapa.add_tile_layer(
            map_id["tile_fetcher"].url_format,
            name="NDVI Raster",
            attribution="Google Earth Engine"
        )


        return mapa
    
    @staticmethod
    def agregar_ndwi_raster(
        mapa,
        fecha_inicio,
        fecha_fin,
        ruta_geojson
    ):

        geojson = GeoJsonService.cargar(
            ruta_geojson
        )

        imagen = SentinelService.obtener(
            fecha_inicio,
            fecha_fin,
            geojson
        )

        # ============================================
        # NDWI
        # ============================================

        ndwi = (
            imagen
            .normalizedDifference(
                [
                    "B3",
                    "B8"
                ]
            )
            .rename("NDWI")
        )

        # ============================================
        # VISUALIZACIÓN
        # ============================================

        vis_params = {
            "min": -1,
            "max": 1,
            "palette": [
                "#8B0000",
                "#D33E35",
                "#E76F51",
                "#F4A261",
                "#E9C46A",
                "#C9D862",
                "#90C95A",
                "#5EAE4F",
                "#2E8B57",
                "#006400"
            ]
        }

        map_id = ndwi.getMapId(
            vis_params
        )

        mapa.add_tile_layer(
            map_id["tile_fetcher"].url_format,
            name="NDWI Raster",
            attribution="Google Earth Engine"
        )

        return mapa
    
    @staticmethod
    def agregar_ndwi_rangos(
        mapa,
        fecha_inicio,
        fecha_fin,
        ruta_geojson
    ):

        geojson = GeoJsonService.cargar(
            ruta_geojson
        )

        imagen = SentinelService.obtener(
            fecha_inicio,
            fecha_fin,
            geojson
        )
        
        if imagen is None:

            return None

        ndwi = IndicesService.ndwi(
            imagen
        )

        # =========================================
        # CLASIFICACIÓN NDWI
        # =========================================

        ndwi_clasificado = (
            ndwi
            .where(
                ndwi.gte(-0.15).And(
                    ndwi.lt(0.05)
                ),
                0
            )
            .where(
                ndwi.gte(0.05).And(
                    ndwi.lt(0.15)
                ),
                1
            )
            .where(
                ndwi.gte(0.15).And(
                    ndwi.lt(0.25)
                ),
                2
            )
            .where(
                ndwi.gte(0.25).And(
                    ndwi.lt(0.35)
                ),
                3
            )
            .where(
                ndwi.gte(0.35).And(
                    ndwi.lt(0.45)
                ),
                4
            )
            .where(
                ndwi.gte(0.45).And(
                    ndwi.lt(0.55)
                ),
                5
            )
            .where(
                ndwi.gte(0.55).And(
                    ndwi.lt(0.65)
                ),
                6
            )
            .where(
                ndwi.gte(0.65).And(
                    ndwi.lt(0.75)
                ),
                7
            )
            .where(
                ndwi.gte(0.75).And(
                    ndwi.lt(0.85)
                ),
                8
            )
            .where(
                ndwi.gte(0.85).And(
                    ndwi.lt(1)
                ),
                9
            )
        )

        # =========================================
        # COLORES
        # =========================================

        vis_params = {
            "min": 0,
            "max": 9,
            "palette": [
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
        }

        map_id = ndwi_clasificado.getMapId(
            vis_params
        )

        mapa.add_tile_layer(
            map_id["tile_fetcher"].url_format,
            name="NDWI por rangos",
            attribution="Google Earth Engine"
        )

        return mapa 
        
        
    @staticmethod
    def agregar_ndre_rangos(
        mapa,
        fecha_inicio,
        fecha_fin,
        ruta_geojson
    ):

        geojson = GeoJsonService.cargar(
            ruta_geojson
        )

        imagen = SentinelService.obtener(
            fecha_inicio,
            fecha_fin,
            geojson
        )
        
        if imagen is None:

            return None

        ndre = (
            IndicesService.ndre(
                imagen
            )
        )

        # =========================================
        # CLASIFICACIÓN NDRE
        # =========================================

        ndre_clasificado = (
            ndre
            .where(
                ndre.lt(0.20),
                0
            )
            .where(
                ndre.gte(0.20).And(
                    ndre.lt(0.40)
                ),
                1
            )
            .where(
                ndre.gte(0.40).And(
                    ndre.lt(0.60)
                ),
                2
            )
            .where(
                ndre.gte(0.60).And(
                    ndre.lt(0.80)
                ),
                3
            )
            .where(
                ndre.gte(0.80),
                4
            )
        )

        # =========================================
        # COLORES
        # =========================================

        vis_params = {
            "min": 0,
            "max": 4,
            "palette": [
                "#9E1114", "#FF9E3D", "#FFFF9E", "#77D66B", "#2B8326"
            ]
        }

        map_id = ndre_clasificado.getMapId(
            vis_params
        )

        mapa.add_tile_layer(
            map_id["tile_fetcher"].url_format,
            name="NDRE por rangos",
            attribution="Google Earth Engine"
        )

        return mapa
    
    
    @staticmethod
    def agregar_ndvi_rangos(
        mapa,
        fecha_inicio,
        fecha_fin,
        ruta_geojson
    ):

        geojson = GeoJsonService.cargar(
            ruta_geojson
        )


        imagen = SentinelService.obtener(
            fecha_inicio,
            fecha_fin,
            geojson
        )
        
        if imagen is None:

            return None


        # NDVI = (NIR - RED) / (NIR + RED)
        ndvi = imagen.normalizedDifference(
            [
                "B8",
                "B4"
            ]
        ).rename(
            "NDVI"
        )
                
        # =========================================
        # CLASIFICACIÓN NDVI
        # =========================================

        ndvi_clasificado = (
            ndvi
            .where(
                ndvi.lt(0.2),
                0
            )
            .where(
                ndvi.gte(0.20).And(
                    ndvi.lt(0.40)
                ),
                1
            )
            .where(
                ndvi.gte(0.40).And(
                    ndvi.lt(0.55)
                ),
                2
            )
            .where(
                ndvi.gte(0.55).And(
                    ndvi.lt(0.70)
                ),
                3
            )
            .where(
                ndvi.gte(0.70),
                4
            )
        )        


        vis_params = {
            "min": 0,
            "max": 4,
            "palette": [
               "#9E1114", "#FF9E3D", "#FFFF9E", "#77D66B", "#2B8326"
            ]
        }


        map_id = ndvi_clasificado.getMapId(
            vis_params
        )


        mapa.add_tile_layer(
            map_id["tile_fetcher"].url_format,
            name="NDVI Raster",
            attribution="Google Earth Engine"
        )


        return mapa
    
    @staticmethod
    def exportar_imagen(mapa, ruta):

        ruta = Path(ruta)

        ruta.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        ruta_html = ruta.with_suffix(".html")

        mapa.to_html(
            str(ruta_html)
        )

        async def capturar():

            async with async_playwright() as p:
                
                # Detectar la ruta del ejecutable de Chromium instalado por APT
                chromium_path = "/usr/bin/chromium" if os.path.exists("/usr/bin/chromium") else "/usr/bin/chromium-browser"

                browser = await p.chromium.launch(
                    executable_path=chromium_path if os.path.exists(chromium_path) else None,
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage",  # Evita crash por falta de memoria compartida (/dev/shm)
                        "--disable-gpu",
                        "--no-zygote",
                        "--single-process"  # Recomendado en contenedores con memoria limitada
                    ]
                )

                page = await browser.new_page(
                    viewport={
                        "width": 1600,
                        "height": 900
                    },
                    device_scale_factor=2
                )

                await page.goto(
                    ruta_html.resolve().as_uri(),
                    wait_until="domcontentloaded",
                    timeout=60000
                )

                # Esperar a que Leaflet se inicialice
                await page.wait_for_selector(
                    ".leaflet-container",
                    timeout=30000
                )

                # ====================================================
                # OCULTAR CONTROLES DE LEAFLET
                # ====================================================

                await page.evaluate("""
                    () => {

                        document.querySelectorAll(
                            '.leaflet-control-container'
                        ).forEach(
                            elemento => {
                                elemento.style.display = 'none';
                            }
                        );

                    }
                """)

                # ====================================================
                # ESPERAR A QUE CARGUEN LAS IMÁGENES
                # ====================================================

                await page.wait_for_timeout(10000)

                # ====================================================
                # CAPTURAR MAPA
                # ====================================================

                mapa_html = page.locator(
                    ".leaflet-container"
                )

                await mapa_html.screenshot(
                    path=str(ruta)
                )

                await browser.close()

        asyncio.run(
            capturar()
        )

        ruta_html.unlink(
            missing_ok=True
        )

        return str(ruta)