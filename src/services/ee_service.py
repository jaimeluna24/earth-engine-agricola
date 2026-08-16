# import ee


# class EEService:

#     @staticmethod
#     def inicializar():

#         if not ee.data.is_initialized():

#             ee.Initialize(
#                 project="mapas-achsa"
#             )

import os
import ee
import streamlit as st
from google.oauth2.service_account import Credentials

class EEService:
    @staticmethod
    def inicializar():
        try:
            # 1. Intentar inicializar si ya está autenticado
            ee.Initialize()
        except Exception:
            # 2. Si falla (como en Streamlit Cloud), autenticar con los Secrets
            if "gcp_service_account" in st.secrets:
                creds_dict = dict(st.secrets["gcp_service_account"])
                
                # Google requiere que los saltos de línea en la clave privada sean reales
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                
                credentials = Credentials.from_service_account_info(
                    creds_dict,
                    scopes=['https://www.googleapis.com/auth/earthengine']
                )
                
                # Inicializar Earth Engine especificando las credenciales y el proyecto
                ee.Initialize(
                    credentials=credentials,
                    project=creds_dict.get("project_id")
                )
            else:
                # 3. Fallback para desarrollo local
                ee.Authenticate()
                ee.Initialize()