from src.services.database_service import DatabaseService
from src.services.estadisticas_indices_service import EstadisticasIndicesService


class NDVIService:

    @staticmethod
    def calcular_y_guardar(
        imagen,
        geojson,
        fecha_inicio,
        fecha_fin
    ):

        print("Calculando NDVI por lotes...")

        resultados = (
            EstadisticasIndicesService
            .ndvi_por_lote_rangos(
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
            "Guardando resultados en MySQL..."
        )

        guardados = 0

        for i, datos in enumerate(resultados):

            if (
                datos["NDVI_mean"] is None
                or datos["NDVI_min"] is None
                or datos["NDVI_max"] is None
            ):
                continue
            
            edades = DatabaseService.obtener_fecha_lotes(datos['lote'], fecha_fin)
            
            DatabaseService.guardar_ndvi(
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

            # Solo mostrar 5
            if i < 5:

                print(
                    f"{datos['finca']} "
                    f"{datos['lote']} "
                    f"→ NDVI "
                    f"{datos['NDVI_mean']:.4f}"
                )

        print(
            f"Se guardaron "
            f"{guardados} lotes."
        )

        return resultados