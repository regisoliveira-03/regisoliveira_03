import requests
import urllib3

# Desativa avisos de segurança sobre o certificado SSL da Caixa
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def obter_ultimo_resultado(modalidade):
    url = f"https://servicebus2.caixa.gov.br/portalloterias/api/{modalidade}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        # verify=False evita erros de certificado comuns no servidor da Caixa
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return f"Erro ao acessar {modalidade}: {e}"

# Lista das principais loterias para consultar
loterias = ["megasena", "lotofacil", "quina", "lotomania", "maismilionaria"]

print("--- ÚLTIMOS RESULTADOS CAIXA ---")

for loteria in loterias:
    dados = obter_ultimo_resultado(loteria)
    
    if isinstance(dados, dict):
        num_concurso = dados.get('numero')
        data = dados.get('dataApuracao')
        dezenas = ", ".join(dados.get('listaDezenas', []))
        valor_acumulado = dados.get('valorEstimadoProximoConcurso', 0)
        
        print(f"\n>> {loteria.upper()}")
        print(f"Concurso: {num_concurso} ({data})")
        print(f"Dezenas:  {dezenas}")
        print(f"Próximo prêmio estimado: R$ {valor_acumulado:,.2f}")
    else:
        print(f"\n[!] {dados}")

print("\n--------------------------------")
