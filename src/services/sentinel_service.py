import ee


class SentinelService:

    @staticmethod
    def obtener(fecha_inicio, fecha_fin, geojson):

        features = []

        for feature in geojson["features"]:
            features.append(
                ee.Feature(
                    ee.Geometry(
                        feature["geometry"]
                    )
                )
            )


        finca = ee.FeatureCollection(
            features
        )


        geometria = finca.geometry()


        coleccion = (
            ee.ImageCollection(
                "COPERNICUS/S2_SR_HARMONIZED"
            )
            .filterBounds(
                geometria
            )
            .filterDate(
                fecha_inicio,
                fecha_fin
            )
            .filter(
                ee.Filter.lt(
                    "CLOUDY_PIXEL_PERCENTAGE",
                    60
                )
            )
        )
        
        if coleccion.size().getInfo() == 0:
            return None

        imagen = (
            coleccion
            .sort(
                "CLOUDY_PIXEL_PERCENTAGE"
            )
            .first()
            .clip(
                geometria
            )
        )


        return imagen
    
    @staticmethod
    def porcentaje_nubes(
        fecha_inicio,
        fecha_fin,
        geojson
    ):

        features = []

        for feature in geojson["features"]:

            features.append(
                ee.Feature(
                    ee.Geometry(
                        feature["geometry"]
                    )
                )
            )

        finca = ee.FeatureCollection(features)

        geometria = finca.geometry()

        coleccion = (
            ee.ImageCollection(
                "COPERNICUS/S2_CLOUD_PROBABILITY"
            )
            .filterBounds(geometria)
            .filterDate(
                fecha_inicio,
                fecha_fin
            )
            .sort("system:time_start")
        )

        if coleccion.size().getInfo() == 0:
            return 0

        imagen = coleccion.median()

        mascara_nubes = (
            imagen.select("probability")
            .gt(70)
        )

        estadisticas = (
            mascara_nubes
            .reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geometria,
                scale=10,
                maxPixels=1e13
            )
        )

        porcentaje = (
            estadisticas
            .get("probability")
            .getInfo()
        )

        return round(
            porcentaje * 100,
            2
        )