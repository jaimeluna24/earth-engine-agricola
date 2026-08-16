import json

from pathlib import Path


class GeoJsonService:

    # =========================================================
    # CARGAR GEOJSON
    # =========================================================

    @staticmethod
    def cargar(ruta):

        with open(
            ruta,
            "r",
            encoding="utf-8"
        ) as archivo:

            return json.load(archivo)


    # =========================================================
    # OBTENER FINCAS
    # =========================================================

    @staticmethod
    def obtener_fincas(ruta):

        geojson = GeoJsonService.cargar(
            ruta
        )

        fincas = set()

        for feature in geojson.get(
            "features",
            []
        ):

            propiedades = feature.get(
                "properties",
                {}
            )

            finca = propiedades.get(
                "FINCA"
            )

            if finca:

                fincas.add(
                    finca
                )

        return sorted(
            fincas
        )


    # =========================================================
    # FILTRAR GEOJSON POR FINCA
    # =========================================================

    @staticmethod
    def filtrar_por_finca(
        ruta,
        finca
    ):

        geojson = GeoJsonService.cargar(
            ruta
        )

        features = []

        for feature in geojson.get(
            "features",
            []
        ):

            propiedades = feature.get(
                "properties",
                {}
            )

            if propiedades.get(
                "FINCA"
            ) == finca:

                features.append(
                    feature
                )

        return {
            "type": "FeatureCollection",
            "features": features
        }


    # =========================================================
    # GUARDAR GEOJSON FILTRADO
    # =========================================================

    @staticmethod
    def guardar_filtrado(
        ruta,
        finca,
        ruta_salida
    ):

        geojson = GeoJsonService.filtrar_por_finca(
            ruta,
            finca
        )

        ruta_salida = Path(
            ruta_salida
        )

        ruta_salida.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            ruta_salida,
            "w",
            encoding="utf-8"
        ) as archivo:

            json.dump(
                geojson,
                archivo,
                ensure_ascii=False
            )

        return str(
            ruta_salida
        )