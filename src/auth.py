import ee

try:
    ee.Authenticate()
    ee.Initialize(project="mapas-achsa")

    print("✅ Conexión con Google Earth Engine exitosa")

except Exception as e:
    print("❌ Error")
    print(e)