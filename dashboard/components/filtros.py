import streamlit as st


@staticmethod
def obtener_fincas(geojson) -> list[str]:
    fincas = {
        feature["properties"]["FINCA"]
        for feature in geojson["features"]
        if feature["properties"].get("FINCA")
    }
    return sorted(fincas)