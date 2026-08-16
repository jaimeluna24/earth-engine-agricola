import ee


class IndicesService:

    @staticmethod
    def ndvi(imagen):

        return (
            imagen
            .normalizedDifference(
                ["B8", "B4"]
            )
            .rename("NDVI")
        )

    @staticmethod
    def ndwi(imagen):

        return (
            imagen
            .normalizedDifference(
                ["B8", "B11"]
            )
            .rename("NDWI")
        )

    @staticmethod
    def nre(imagen):

        return (
            imagen.expression(
                "(nir-rededge)/(nir+rededge)",
                {
                    "nir": imagen.select("B8A"),
                    "rededge": imagen.select("B5")
                }
            )
            .rename("NRE")
        )
        
    @staticmethod
    def ndre(imagen):

        return (
            imagen
            .normalizedDifference([
                "B8A",
                "B5"
            ])
            .rename("NDRE")
        )