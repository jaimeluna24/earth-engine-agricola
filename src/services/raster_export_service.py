import ee

class RasterExportService:

    @staticmethod
    def exportar_geotiff(
        imagen: ee.Image,
        geometria,
        nombre,
        carpeta="EarthEngine"
    ):

        tarea = ee.batch.Export.image.toDrive(
        image=imagen,
        description=nombre,
        folder=carpeta,
        fileNamePrefix=nombre,
        region=geometria,
        scale=10,
        crs="EPSG:32616",
        maxPixels=1e13,
        fileFormat="GeoTIFF"
        )

        tarea.start()

        return tarea