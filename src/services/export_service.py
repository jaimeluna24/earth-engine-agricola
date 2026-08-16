import csv
import os

class ExportService:

    @staticmethod
    def features_a_csv(
        resultado,
        ruta_salida
    ):

        data = resultado.getInfo()

        features = data["features"]

        if not features:
            raise Exception(
                "No hay resultados para exportar"
            )

        # Obtener todas las columnas existentes
        columnas = set()

        for feature in features:
            columnas.update(
                feature["properties"].keys()
            )

        columnas = list(columnas)

        os.makedirs(
            os.path.dirname(ruta_salida),
            exist_ok=True
        )

        with open(
            ruta_salida,
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as archivo:

            escritor = csv.DictWriter(
                archivo,
                fieldnames=columnas,
                extrasaction="ignore"
            )

            escritor.writeheader()

            for feature in features:

                escritor.writerow(
                    feature["properties"]
                )