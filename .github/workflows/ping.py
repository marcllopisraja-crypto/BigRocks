import requests
import sys

url = "https://bigrocks.streamlit.app/"

try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        print(f"La web {url} està activa.")
    else:
        print(f"La web ha respost amb el codi: {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"Error connectant a {url}: {e}")
    sys.exit(1)
