import ee

class EstadisticasService:

    @staticmethod
    def calcular(
        imagen: ee.Image,
        geometria,
        reducer=None,
        scale=10
    ):

        if reducer is None:
            reducer = ee.Reducer.mean()

        resultado = imagen.reduceRegion(
            reducer=reducer,
            geometry=geometria,
            scale=scale,
            maxPixels=1e13
        )

        return resultado.getInfo()

    @staticmethod
    def calcular_por_lotes(
        imagen: ee.Image,
        feature_collection,
        reducer=None,
        scale=10
    ):

        if reducer is None:
            reducer = ee.Reducer.mean()

        return imagen.reduceRegions(
            collection=feature_collection,
            reducer=reducer,
            scale=scale
        )