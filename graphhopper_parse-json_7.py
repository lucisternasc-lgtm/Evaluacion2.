import requests
import urllib.parse

route_url = "https://graphhopper.com/api/1/route?"
geocode_url = "https://graphhopper.com/api/1/geocode?"
key = "0a2376c8-1b18-47e2-a4fb-b58d889e7943"

transportes = {"1": "car", "2": "bike", "3": "foot"}
nombres = {"car": "auto", "bike": "bicicleta", "foot": "a pie"}


def geocoding(ubicacion, key):
    url = geocode_url + urllib.parse.urlencode(
        {"q": ubicacion, "limit": "1", "locale": "es", "key": key}
    )
    try:
        replydata = requests.get(url, timeout=30)
        json_data = replydata.json()
    except requests.exceptions.RequestException as error:
        print("Error de conexión:", error)
        return None, None, None, ubicacion
    json_status = replydata.status_code
    print("Estado HTTP:", json_status)
    if json_status == 200 and json_data.get("hits"):
        hit = json_data["hits"][0]
        lat = hit["point"]["lat"]
        lng = hit["point"]["lng"]
        print("Ubicación encontrada:", hit.get("name", ubicacion))
        print(f"Latitud: {lat:.2f}")
        print(f"Longitud: {lng:.2f}")
        return json_status, lat, lng, hit.get("name", ubicacion)
    print("No se encontraron resultados:", json_data.get("message", "sin resultados"))
    return json_status, None, None, ubicacion


while True:
    loc1 = input("Ubicación de origen (ingrese s o salir para salir): ").strip()
    if loc1.lower() in ("s", "salir"):
        print("Saliendo del programa. ¡Hasta luego!")
        break
    if not loc1:
        print("Debe ingresar una ubicación.\n")
        continue
    orig = geocoding(loc1, key)
    if orig[1] is None:
        print("No se pudo ubicar el origen. Intente de nuevo.\n")
        continue

    loc2 = input("Destino (ingrese s o salir para salir): ").strip()
    if loc2.lower() in ("s", "salir"):
        print("Saliendo del programa. ¡Hasta luego!")
        break
    if not loc2:
        print("Debe ingresar un destino.\n")
        continue
    dest = geocoding(loc2, key)
    if dest[1] is None:
        print("No se pudo ubicar el destino. Intente de nuevo.\n")
        continue

    print("\nMedio de transporte:")
    print("1. auto")
    print("2. bicicleta")
    print("3. a pie")
    opcion = input("Ingrese 1, 2 o 3 (s o salir para salir): ").strip().lower()
    if opcion in ("s", "salir"):
        print("Saliendo del programa. ¡Hasta luego!")
        break
    vehiculo = transportes.get(opcion, "car")

    url = route_url + urllib.parse.urlencode(
        [
            ("point", f"{orig[1]},{orig[2]}"),
            ("point", f"{dest[1]},{dest[2]}"),
            ("vehicle", vehiculo),
            ("locale", "es"),
            ("instructions", "true"),
            ("key", key),
        ]
    )
    respuesta = requests.get(url, timeout=30)
    datos = respuesta.json()
    print("\nEstado HTTP de la ruta:", respuesta.status_code)
    print("URL de la API de rutas:\n" + url)

    if respuesta.status_code == 200 and "paths" in datos:
        ruta = datos["paths"][0]
        km = ruta["distance"] / 1000
        minutos = ruta["time"] / 1000 / 60
        print("=" * 50)
        print(f"Ruta desde {orig[3]} hasta {dest[3]} en {nombres[vehiculo]}")
        print(f"Distancia total: {km:.2f} km")
        print(f"Duración estimada: {minutos:.2f} minutos")
        print("=" * 50)
        print("Narrativa del viaje:")
        for indicacion in ruta["instructions"]:
            print(f"- {indicacion['text']} ({indicacion['distance']:.2f} metros)")
    else:
        print("No se pudo calcular la ruta:", datos.get("message", "error desconocido"))
    print("=" * 50 + "\n")
