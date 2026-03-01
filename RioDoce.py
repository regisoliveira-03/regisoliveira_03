import requests

url = "https://monitoramentoriodoce.org/download-dos-dados/"

try:
    response = requests.head(url)
    # Tenta obter o cabeçalho 'Last-Modified'
    last_modified = response.headers.get('Last-Modified')
    
    if last_modified:
        print(f"Data de modificação informada pelo servidor: {last_modified}")
    else:
        print("O servidor não fornece uma data 'Last-Modified' direta.")
except Exception as e:
    print(f"Erro ao acessar: {e}")
