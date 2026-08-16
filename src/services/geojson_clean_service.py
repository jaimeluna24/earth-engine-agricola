import json
from shapely.geometry import shape, mapping

class GeoJsonCleanService:

    @staticmethod
    def limpiar(ruta_entrada):

        with open(
            ruta_entrada,
            encoding="utf-8"
        ) as archivo:

            geojson = json.load(archivo)


        nuevo_geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for feature in geojson["features"]:

            geometria = shape(
                feature["geometry"]
            )

            nueva_feature = {
                "type": "Feature",
                "properties": {
                    "LOTE_ID": feature["properties"].get("LOTE_ID"),
                    "FINCA": feature["properties"].get("FINCA"),
                    "VARIEDAD": feature["properties"].get("VARIEDAD"),
                    "CICLO": feature["properties"].get("CICLO"),
                    "AREA": feature["properties"].get("Area Calc")
                },
                "geometry": json.loads(
                    json.dumps(
                        mapping(geometria)
                    )
                )
            }

            nuevo_geojson["features"].append(
                nueva_feature
            )

        return nuevo_geojson