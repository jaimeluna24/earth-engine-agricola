import ee


class EEService:

    @staticmethod
    def inicializar():

        if not ee.data.is_initialized():

            ee.Initialize(
                project="mapas-achsa"
            )