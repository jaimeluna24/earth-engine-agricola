from config.settings import PROJECT_ID

from services.earth_engine_service import EarthEngineService
from services.geojson_service import GeoJsonService
from services.sentinel_service import SentinelService
from services.indices_service import IndicesService
from services.estadisticas_service import EstadisticasService
from services.export_service import ExportService
from services.raster_export_service import RasterExportService


# Inicializar Earth Engine
EarthEngineService(PROJECT_ID)


# Cargar lotes desde GeoJSON
feature_collection = GeoJsonService.cargar(
    "data/geojson/finca_rancho_alegre.geojson"
)


# Obtener imagen Sentinel
imagen = SentinelService.mejor_imagen(
    feature_collection,
    "2025-01-01",
    "2025-12-31"
)


# Recortar la imagen a la finca
imagen_finca = imagen.clip(
    feature_collection.geometry()
)


# Calcular NDVI
ndvi = IndicesService.ndvi(
    imagen_finca
)


# Estadísticas por lote
resultado = EstadisticasService.calcular_por_lotes(
    ndvi,
    feature_collection
)


# Exportar CSV
ExportService.features_a_csv(
    resultado,
    "output/ndvi_lotes.csv"
)


print("CSV generado correctamente")


# Exportar NDVI como GeoTIFF
RasterExportService.exportar_geotiff(
    ndvi,
    feature_collection.geometry(),
    "NDVI_RANCHO_ALEGRE"
)


print("Tarea TIFF enviada a Earth Engine")