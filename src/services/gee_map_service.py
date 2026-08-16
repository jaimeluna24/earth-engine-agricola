import geemap.foliumap as geemap
import ee

class GeeMapService:

    _initialized = False

    @staticmethod
    def _inicializar_ee():
        if not GeeMapService._initialized:
            try:
                ee.Initialize(project="TU_PROJECT_ID")
            except Exception:
                ee.Authenticate()
                ee.Initialize(project="TU_PROJECT_ID")
            GeeMapService._initialized = True

    @staticmethod
    def crear_mapa():
        GeeMapService._inicializar_ee()

        mapa = geemap.Map(
            center=[13.24, -87.34],
            zoom=14
        )

        return mapa