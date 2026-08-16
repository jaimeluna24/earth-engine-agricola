import ee

# Inicializar Earth Engine
ee.Initialize(project="mapas-achsa")

# Coordenadas de ejemplo (cámbialas luego por una finca)
punto = ee.Geometry.Point([-87.19, 13.30])

# Buscar imágenes Sentinel-2
coleccion = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(punto)
    .filterDate("2025-01-01", "2025-12-31")
    .sort("CLOUDY_PIXEL_PERCENTAGE")
)

print("Cantidad de imágenes encontradas:")
print(coleccion.size().getInfo())