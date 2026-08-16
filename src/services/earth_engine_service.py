import ee


class EarthEngineService:

    def __init__(self, project_id):

        ee.Initialize(project=project_id)

    @staticmethod
    def verificar():

        return ee.String(
            "Earth Engine conectado"
        ).getInfo()