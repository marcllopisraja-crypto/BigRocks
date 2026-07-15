import requests
import sys

url = "LA_TEVA_URL_AQUÍ" # La web que vols comprovar

try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        print(f"La web {url} està activa.")
    else:
        print(f"La web ha respost amb el codi: {response.status_code}")
        sys.exit(1) # Això farà que l'acció falli i t'avisin
except Exception as e:
    print(f"Error connectant a {url}: {e}")
    sys.exit(1)
