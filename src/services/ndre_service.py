from src.services.estadisticas_indices_service import (
    EstadisticasIndicesService
)

from src.services.database_service import (
    DatabaseService
)


class NDREService:

    @staticmethod
    def calcular_y_guardar(
        imagen,
        geojson,
        fecha_inicio,
        fecha_fin
    ):

        print("Calculando NDRE por lotes...")

        resultados = (
            EstadisticasIndicesService
            .ndre_por_lote_rangos(
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
            "Guardando resultados NDRE en MySQL..."
        )

        guardados = 0

        for i, datos in enumerate(resultados):

            if (
                datos["NDRE_mean"] is None
                or datos["NDRE_min"] is None
                or datos["NDRE_max"] is None
            ):
                print(
                    f"NDRE inválido -> "
                    f"{datos['finca']} {datos['lote']} | "
                    f"min={datos['NDRE_min']} | "
                    f"mean={datos['NDRE_mean']} | "
                    f"max={datos['NDRE_max']}"
                )
                continue
            edades = DatabaseService.obtener_fecha_lotes(datos['lote'], fecha_fin)
            etapa = DatabaseService.obtener_etapa_fenologica(edades['edad_dias'])

            DatabaseService.guardar_ndre(
                datos["finca"],
                datos["lote"],
                fecha_inicio,
                fecha_fin,
                edades['fecha_cosecha_siembra'],
                edades['edad_meses'],
                edades['edad_dias'],
                etapa['etapa_id'],
                datos
            )

            guardados += 1

            if i < 5:

                print(
                    f"{datos['finca']} "
                    f"{datos['lote']} "
                    f"→ NDRE "
                    f"{datos['NDRE_mean']:.4f}"
                )

        print(
            f"Se guardaron "
            f"{guardados} lotes NDRE."
        )

        return resultados