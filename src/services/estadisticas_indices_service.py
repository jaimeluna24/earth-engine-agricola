import ee


class EstadisticasIndicesService:

    # ============================================================
    # AGRUPAR POLÍGONOS DEL MISMO LOTE
    # ============================================================

    @staticmethod
    def _agrupar_por_lote(resultados, indice, rangos):
        """
        Une varios polígonos que pertenecen al mismo lote.

        Ejemplo:

            RAL042 -> polígono 1
            RAL042 -> polígono 2

        Se convierten en:

            RAL042 -> un solo registro
        """

        agrupados = {}

        for datos in resultados:

            clave = (
                datos["finca"],
                datos["lote"]
            )

            if clave not in agrupados:

                agrupados[clave] = {
                    "finca": datos["finca"],
                    "lote": datos["lote"],

                    f"{indice}_min": datos[
                        f"{indice}_min"
                    ],

                    f"{indice}_max": datos[
                        f"{indice}_max"
                    ],

                    "area_total": datos[
                        "area_total"
                    ],

                    # Para calcular promedio ponderado
                    "_suma_ponderada": (
                        (
                            datos[f"{indice}_mean"]
                            or 0
                        )
                        * datos["area_total"]
                    ),

                    "_area_mean": datos[
                        "area_total"
                    ]
                }

                # Áreas de cada rango
                for rango in rangos:

                    agrupados[clave][
                        f"area_{rango}"
                    ] = datos.get(
                        f"area_{rango}",
                        0
                    )

            else:

                actual = agrupados[clave]

                # ------------------------------------------------
                # MÍNIMO
                # ------------------------------------------------

                valor_min = datos[
                    f"{indice}_min"
                ]

                if valor_min is not None:

                    if (
                        actual[f"{indice}_min"]
                        is None
                        or valor_min
                        < actual[f"{indice}_min"]
                    ):

                        actual[
                            f"{indice}_min"
                        ] = valor_min

                # ------------------------------------------------
                # MÁXIMO
                # ------------------------------------------------

                valor_max = datos[
                    f"{indice}_max"
                ]

                if valor_max is not None:

                    if (
                        actual[f"{indice}_max"]
                        is None
                        or valor_max
                        > actual[f"{indice}_max"]
                    ):

                        actual[
                            f"{indice}_max"
                        ] = valor_max

                # ------------------------------------------------
                # ÁREA TOTAL
                # ------------------------------------------------

                area = datos.get(
                    "area_total",
                    0
                ) or 0

                actual["area_total"] += area

                # ------------------------------------------------
                # PROMEDIO PONDERADO
                # ------------------------------------------------

                mean = datos.get(
                    f"{indice}_mean"
                )

                if mean is not None:

                    actual[
                        "_suma_ponderada"
                    ] += mean * area

                    actual[
                        "_area_mean"
                    ] += area

                # ------------------------------------------------
                # ÁREAS POR RANGO
                # ------------------------------------------------

                for rango in rangos:

                    actual[
                        f"area_{rango}"
                    ] += datos.get(
                        f"area_{rango}",
                        0
                    ) or 0

        # ========================================================
        # CONSTRUIR RESULTADOS FINALES
        # ========================================================

        resultados_finales = []

        for datos in agrupados.values():

            area_total = datos[
                "area_total"
            ]

            # ----------------------------------------------------
            # PROMEDIO PONDERADO
            # ----------------------------------------------------

            if datos["_area_mean"] > 0:

                mean = (
                    datos["_suma_ponderada"]
                    / datos["_area_mean"]
                )

            else:

                mean = None

            # ----------------------------------------------------
            # RESULTADO
            # ----------------------------------------------------

            resultado = {

                "finca": datos["finca"],

                "lote": datos["lote"],

                f"{indice}_min": datos[
                    f"{indice}_min"
                ],

                f"{indice}_mean": mean,

                f"{indice}_max": datos[
                    f"{indice}_max"
                ],

                "area_total": area_total
            }

            # ----------------------------------------------------
            # PORCENTAJES
            # ----------------------------------------------------

            for rango in rangos:

                area_rango = datos[
                    f"area_{rango}"
                ]

                if area_total > 0:

                    porcentaje = (
                        area_rango
                        / area_total
                    ) * 100

                else:

                    porcentaje = 0

                resultado[
                    f"porcentaje_{rango}"
                ] = porcentaje

            resultados_finales.append(
                resultado
            )

        return resultados_finales


    # ============================================================
    # NDVI
    # ============================================================

    @staticmethod
    def ndvi_por_lote_rangos(
        imagen,
        geojson
    ):

        ndvi = (
            imagen
            .normalizedDifference(
                ["B8", "B4"]
            )
            .rename("NDVI")
        )

        pixel_area = ee.Image.pixelArea()

        # ========================================================
        # ÁREAS
        # ========================================================

        area_total = (
            pixel_area
            .updateMask(ndvi.mask())
            .rename("area_total")
        )

        area_critico = (
            pixel_area
            .updateMask(
                ndvi.lt(0.18)
            )
            .rename("area_critico")
        )

        area_bajo = (
            pixel_area
            .updateMask(
                ndvi.gte(0.18)
                .And(ndvi.lt(0.35))
            )
            .rename("area_bajo")
        )

        area_medio = (
            pixel_area
            .updateMask(
                ndvi.gte(0.35)
                .And(ndvi.lt(0.53))
            )
            .rename("area_medio")
        )

        area_bueno = (
            pixel_area
            .updateMask(
                ndvi.gte(0.53)
                .And(ndvi.lt(0.70))
            )
            .rename("area_bueno")
        )

        area_excelente = (
            pixel_area
            .updateMask(
                ndvi.gte(0.70)
            )
            .rename("area_excelente")
        )

        imagen_estadisticas = (
            ndvi
            .addBands(area_total)
            .addBands(area_critico)
            .addBands(area_bajo)
            .addBands(area_medio)
            .addBands(area_bueno)
            .addBands(area_excelente)
        )

        # ========================================================
        # LOTES
        # ========================================================

        features = []

        for feature in geojson["features"]:

            geometria = ee.Geometry(
                feature["geometry"]
            )

            propiedades = feature.get(
                "properties",
                {}
            )

            finca = propiedades.get(
                "FINCA",
                "SIN FINCA"
            )

            lote = (
                propiedades.get("LOTE")
                or propiedades.get("name")
                or propiedades.get("LOTE_ID")
                or "SIN LOTE"
            )

            features.append(
                ee.Feature(
                    geometria,
                    {
                        "finca": finca,
                        "lote": lote
                    }
                )
            )

        lotes = ee.FeatureCollection(
            features
        )

        # ========================================================
        # REDUCER
        # ========================================================

        reducer = (
            ee.Reducer.mean()
            .combine(
                ee.Reducer.minMax(),
                sharedInputs=True
            )
            .combine(
                ee.Reducer.sum(),
                sharedInputs=True
            )
        )

        resultados_fc = (
            imagen_estadisticas
            .reduceRegions(
                collection=lotes,
                reducer=reducer,
                scale=10
            )
        )

        resultados = resultados_fc.getInfo()

        resultados_temporales = []

        # ========================================================
        # RESULTADOS INDIVIDUALES
        # ========================================================

        for feature in resultados["features"]:

            propiedades = feature[
                "properties"
            ]

            area_total = (
                propiedades.get(
                    "area_total_sum"
                ) or 0
            )

            resultados_temporales.append({

                "finca": propiedades.get(
                    "finca",
                    "SIN FINCA"
                ),

                "lote": propiedades.get(
                    "lote",
                    "SIN LOTE"
                ),

                "NDVI_min": propiedades.get(
                    "NDVI_min"
                ),

                "NDVI_mean": propiedades.get(
                    "NDVI_mean"
                ),

                "NDVI_max": propiedades.get(
                    "NDVI_max"
                ),

                "area_total": area_total,

                "area_critico": (
                    propiedades.get(
                        "area_critico_sum"
                    ) or 0
                ),

                "area_bajo": (
                    propiedades.get(
                        "area_bajo_sum"
                    ) or 0
                ),

                "area_medio": (
                    propiedades.get(
                        "area_medio_sum"
                    ) or 0
                ),

                "area_bueno": (
                    propiedades.get(
                        "area_bueno_sum"
                    ) or 0
                ),

                "area_excelente": (
                    propiedades.get(
                        "area_excelente_sum"
                    ) or 0
                )
            })

        # ========================================================
        # CAMBIO IMPORTANTE
        # AQUÍ SE UNEN LOS POLÍGONOS DEL MISMO LOTE
        # ========================================================

        return EstadisticasIndicesService._agrupar_por_lote(

            resultados_temporales,

            "NDVI",

            [
                "critico",
                "bajo",
                "medio",
                "bueno",
                "excelente"
            ]
        )


    # ============================================================
    # NDWI
    # ============================================================

    @staticmethod
    def ndwi_por_lote_rangos(
        imagen,
        geojson
    ):

        ndwi = (
            imagen
            .normalizedDifference(
                ["B8", "B11"]
            )
            .rename("NDWI")
        )

        pixel_area = ee.Image.pixelArea()

        # ========================================================
        # RANGOS
        # ========================================================

        rangos = {

            "muy_danado": ndwi.lt(0.05),

            "danado": (
                ndwi.gte(0.05)
                .And(ndwi.lt(0.15))
            ),

            "dano_moderado": (
                ndwi.gte(0.15)
                .And(ndwi.lt(0.25))
            ),

            "estres": (
                ndwi.gte(0.25)
                .And(ndwi.lt(0.35))
            ),

            "amarillo": (
                ndwi.gte(0.35)
                .And(ndwi.lt(0.45))
            ),

            "transicion": (
                ndwi.gte(0.45)
                .And(ndwi.lt(0.55))
            ),

            "vegetacion_moderada": (
                ndwi.gte(0.55)
                .And(ndwi.lt(0.65))
            ),

            "vegetacion_saludable": (
                ndwi.gte(0.65)
                .And(ndwi.lt(0.75))
            ),

            "saludable": (
                ndwi.gte(0.75)
                .And(ndwi.lt(0.85))
            ),

            "muy_saludable": ndwi.gte(0.85)
        }

        # ========================================================
        # BANDAS DE ÁREA
        # ========================================================

        imagen_estadisticas = (
            ndwi
            .addBands(
                pixel_area
                .updateMask(ndwi.mask())
                .rename("area_total")
            )
        )

        for nombre, mascara in rangos.items():

            banda = (
                pixel_area
                .updateMask(mascara)
                .rename(
                    f"area_{nombre}"
                )
            )

            imagen_estadisticas = (
                imagen_estadisticas
                .addBands(banda)
            )

        # ========================================================
        # LOTES
        # ========================================================

        features = []

        for feature in geojson["features"]:

            geometria = ee.Geometry(
                feature["geometry"]
            )

            propiedades = feature.get(
                "properties",
                {}
            )

            finca = propiedades.get(
                "FINCA",
                "SIN FINCA"
            )

            lote = (
                propiedades.get("LOTE")
                or propiedades.get("name")
                or propiedades.get("LOTE_ID")
                or "SIN LOTE"
            )

            features.append(
                ee.Feature(
                    geometria,
                    {
                        "finca": finca,
                        "lote": lote
                    }
                )
            )

        lotes = ee.FeatureCollection(
            features
        )

        # ========================================================
        # REDUCER
        # ========================================================

        reducer = (
            ee.Reducer.mean()
            .combine(
                ee.Reducer.minMax(),
                sharedInputs=True
            )
            .combine(
                ee.Reducer.sum(),
                sharedInputs=True
            )
        )

        resultados_fc = (
            imagen_estadisticas
            .reduceRegions(
                collection=lotes,
                reducer=reducer,
                scale=10
            )
        )

        resultados = resultados_fc.getInfo()

        resultados_temporales = []

        # ========================================================
        # RESULTADOS INDIVIDUALES
        # ========================================================

        for feature in resultados["features"]:

            propiedades = feature[
                "properties"
            ]

            resultados_temporales.append({

                "finca": propiedades.get(
                    "finca",
                    "SIN FINCA"
                ),

                "lote": propiedades.get(
                    "lote",
                    "SIN LOTE"
                ),

                "NDWI_min": propiedades.get(
                    "NDWI_min"
                ),

                "NDWI_mean": propiedades.get(
                    "NDWI_mean"
                ),

                "NDWI_max": propiedades.get(
                    "NDWI_max"
                ),

                "area_total": (
                    propiedades.get(
                        "area_total_sum"
                    ) or 0
                )
            })

            # ----------------------------------------------------
            # AGREGAR ÁREAS
            # ----------------------------------------------------

            for nombre in rangos:

                resultados_temporales[-1][
                    f"area_{nombre}"
                ] = (
                    propiedades.get(
                        f"area_{nombre}_sum"
                    ) or 0
                )

        # ========================================================
        # CAMBIO IMPORTANTE
        # AQUÍ SE UNEN LOS POLÍGONOS DEL MISMO LOTE
        # ========================================================

        return EstadisticasIndicesService._agrupar_por_lote(

            resultados_temporales,

            "NDWI",

            list(rangos.keys())
        )


    # ============================================================
    # NDRE
    # ============================================================

    @staticmethod
    def ndre_por_lote_rangos(
        imagen,
        geojson
    ):

        ndre = (
            imagen
            .normalizedDifference(
                [
                    "B8A",
                    "B5"
                ]
            )
            .rename("NDRE")
        )

        pixel_area = ee.Image.pixelArea()

        # ========================================================
        # ÁREAS
        # ========================================================

        area_total = (
            pixel_area
            .updateMask(ndre.mask())
            .rename("area_total")
        )

        area_critico = (
            pixel_area
            .updateMask(
                ndre.lt(0.20)
            )
            .rename("area_critico")
        )

        area_bajo = (
            pixel_area
            .updateMask(
                ndre.gte(0.20)
                .And(ndre.lt(0.40))
            )
            .rename("area_bajo")
        )

        area_medio = (
            pixel_area
            .updateMask(
                ndre.gte(0.40)
                .And(ndre.lt(0.60))
            )
            .rename("area_medio")
        )

        area_bueno = (
            pixel_area
            .updateMask(
                ndre.gte(0.60)
                .And(ndre.lt(0.80))
            )
            .rename("area_bueno")
        )

        area_excelente = (
            pixel_area
            .updateMask(
                ndre.gte(0.80)
            )
            .rename("area_excelente")
        )

        imagen_estadisticas = (
            ndre
            .addBands(area_total)
            .addBands(area_critico)
            .addBands(area_bajo)
            .addBands(area_medio)
            .addBands(area_bueno)
            .addBands(area_excelente)
        )

        # ========================================================
        # LOTES
        # ========================================================

        features = []

        for feature in geojson["features"]:

            geometria = ee.Geometry(
                feature["geometry"]
            )

            propiedades = feature.get(
                "properties",
                {}
            )

            finca = propiedades.get(
                "FINCA",
                "SIN FINCA"
            )

            lote = (
                propiedades.get("LOTE")
                or propiedades.get("name")
                or propiedades.get("LOTE_ID")
                or "SIN LOTE"
            )

            features.append(
                ee.Feature(
                    geometria,
                    {
                        "finca": finca,
                        "lote": lote
                    }
                )
            )

        lotes = ee.FeatureCollection(
            features
        )

        # ========================================================
        # ESTADÍSTICAS NDRE
        # ========================================================

        resultados_fc = (
            ndre
            .reduceRegions(
                collection=lotes,
                reducer=(
                    ee.Reducer.mean()
                    .combine(
                        reducer2=ee.Reducer.minMax(),
                        sharedInputs=True
                    )
                ),
                scale=20
            )
        )

        # ========================================================
        # ÁREAS
        # ========================================================

        resultados_area = (
            imagen_estadisticas
            .select([
                "area_total",
                "area_critico",
                "area_bajo",
                "area_medio",
                "area_bueno",
                "area_excelente"
            ])
            .reduceRegions(
                collection=lotes,
                reducer=ee.Reducer.sum(),
                scale=20
            )
        )

        resultados = resultados_fc.getInfo()

        resultados_areas = (
            resultados_area.getInfo()
        )

        resultados_temporales = []

        # ========================================================
        # RESULTADOS INDIVIDUALES
        # ========================================================

        for feature, feature_area in zip(
            resultados["features"],
            resultados_areas["features"]
        ):

            propiedades = feature[
                "properties"
            ]

            propiedades_area = (
                feature_area["properties"]
            )

            resultados_temporales.append({

                "finca": propiedades.get(
                    "finca",
                    "SIN FINCA"
                ),

                "lote": propiedades.get(
                    "lote",
                    "SIN LOTE"
                ),

                "NDRE_min": propiedades.get(
                    "min"
                ),

                "NDRE_mean": propiedades.get(
                    "mean"
                ),

                "NDRE_max": propiedades.get(
                    "max"
                ),

                "area_total": (
                    propiedades_area.get(
                        "area_total"
                    ) or 0
                ),

                "area_critico": (
                    propiedades_area.get(
                        "area_critico"
                    ) or 0
                ),

                "area_bajo": (
                    propiedades_area.get(
                        "area_bajo"
                    ) or 0
                ),

                "area_medio": (
                    propiedades_area.get(
                        "area_medio"
                    ) or 0
                ),

                "area_bueno": (
                    propiedades_area.get(
                        "area_bueno"
                    ) or 0
                ),

                "area_excelente": (
                    propiedades_area.get(
                        "area_excelente"
                    ) or 0
                )
            })

        # ========================================================
        # CAMBIO IMPORTANTE
        # AQUÍ SE UNEN LOS POLÍGONOS DEL MISMO LOTE
        # ========================================================

        return EstadisticasIndicesService._agrupar_por_lote(
            resultados_temporales,
            "NDRE",
            [
                "critico",
                "bajo",
                "medio",
                "bueno",
                "excelente"
            ]
        )