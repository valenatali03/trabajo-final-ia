import requests
import time
import json

def obtener_apps(api_key):

    url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
        
    todas_las_apps = []
    last_appid = 0

    if not api_key:
        print("Coloque una api_key valida")
        return

    print("Iniciando descarga")
    for _ in range(3):
        params = {
                    'key': api_key,
                    'max_results': 50000, # El máximo permitido por página
                    'last_appid': last_appid,
                    'include_games': 'true',
                    'include_dlc': 'false',
                    'include_software': 'false',
                    'include_hardware': 'false'
                }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'response' in data and 'apps' in data['response']:
                apps = data['response']['apps']

                apps_optimizado = [{'appid': app['appid'], 'name': app['name']} for app in apps]
                
                todas_las_apps.extend(apps_optimizado)

                last_appid = apps_optimizado[-1]['appid']

                print(f"Descargados {len(todas_las_apps)} ítems hasta ahora... (último ID: {last_appid})")

                time.sleep(1)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 403:
                raise ValueError("La API Key es incorrecta o ha sido revocada.")
            else:
                print(f"Error HTTP inesperado: {e}")
                break

        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break

    print(f"\n¡Terminado! Total de Apps encontradas: {len(todas_las_apps)}")
        
    with open('steam_apps_cache.json', 'w', encoding='utf-8') as f:
        json.dump(todas_las_apps, f, indent=4)
            
    print("Guardado en 'steam_apps_cache.json'")