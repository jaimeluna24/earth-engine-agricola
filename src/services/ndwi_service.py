from src.services.estadisticas_indices_service import (
    EstadisticasIndicesService
)

from src.services.database_service import (
    DatabaseService
)


class NDWIService:

    @staticmethod
    def calcular_y_guardar(
        imagen,
        geojson,
        fecha_inicio,
        fecha_fin
    ):

        print("Calculando NDWI por lotes...")

        resultados = (
            EstadisticasIndicesService
            .ndwi_por_lote_rangos(
                imagen,
                geojson
            )
        )

        print(
            f"Resultados recibidos: "
            f"{len(resultados)}"
        )

        if not resultados:

            print(
                "NO HAY RESULTADOS PARA GUARDAR."
            )

            return []

        print(
            "Guardando resultados NDWI en MySQL..."
        )

        guardados = 0

        for i, datos in enumerate(resultados):

            if (
                datos["NDWI_mean"] is None
                or datos["NDWI_min"] is None
                or datos["NDWI_max"] is None
            ):
                continue
            
            edades = DatabaseService.obtener_fecha_lotes(datos['lote'], fecha_fin)

            DatabaseService.guardar_ndwi(
                datos["finca"],
                datos["lote"],
                fecha_inicio,
                fecha_fin,
                edades['fecha_cosecha_siembra'],
                edades['edad_meses'],
                edades['edad_dias'],
                datos
            )

            guardados += 1

            if i < 5:

                print(
                    f"{datos['finca']} "
                    f"{datos['lote']} "
                    f"→ NDWI "
                    f"{datos['NDWI_mean']:.4f}"
                )

        print(
            f"Se guardaron "
            f"{guardados} lotes NDWI."
        )

        return resultados