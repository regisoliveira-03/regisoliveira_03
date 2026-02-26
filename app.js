from flask import Flask, render_template, request, jsonify, send_file
import csv
from datetime import datetime
import io
import json

app = Flask(__name__)

# --- LÓGICA DE CÁLCULO (BACKEND) ---

# Tabela 1 do Anexo III: Fatores de Deposição (TDep) para 2 metros (sem defletor, em percentual).
Fatores_Deposito = {
    "MILHO": 17.0,
    "CEREAIS": 9.9,
    "BETERRABA": 0.03,
    "CANOLA": 0.11,
    "OUTRA": 17.0
}
Culturas = list(Fatores_Deposito.keys())

# Armazenamento em sessão (usando dicionário global - em produção usar session/banco de dados)
app_data = {
    "heubach_data": [],
    "qp_log": [],
    "last_refinement_data": {}
}

def calcular_dose_ha_fase1(dose_ia_100kg: float, taxa_semeadura: float) -> float:
    """
    Calcula a Dose de Poeira em g i.a./ha para a Fase 1 (Pior caso da Bula).
    Fórmula padrão (Anexo III): (Dose g i.a./100kg) * (Taxa de Semeadura kg/ha) / 100
    """
    if taxa_semeadura <= 0:
        return 0.0
    return (dose_ia_100kg * taxa_semeadura) / 100

def calcular_dose_ha_refinada(teor_ia_poeira_ou_heubach: float, taxa_semeadura_max: float) -> float:
    """
    Calcula a Dose de Poeira em g i.a./ha para o Refinamento (Pior caso).
    Fórmula: (Input g/100kg sementes) * (Taxa de Semeadura Máx kg/ha) / 100
    """
    if taxa_semeadura_max <= 0:
        return 0.0
    return (teor_ia_poeira_ou_heubach * taxa_semeadura_max) / 100

def calcular_qp(dose_ia_ha: float, dl50_contato: float, cultura: str, uso_defletor: bool = False):
    """
    Estima o Quociente de Perigo (QP) para a deriva da poeira.
    Fórmula: QP = (dose de poeira (em g de ia/ha) * TDep) / DL50
    """
    cultura_upper = cultura.strip().upper()
    
    t_dep_percentual = Fatores_Deposito.get(cultura_upper, Fatores_Deposito["OUTRA"])
    
    # Ajuste para uso de defletor (TDep / 10)
    if uso_defletor:
        t_dep_percentual /= 10
    
    # TDep como fator fracionário
    t_dep_fator = t_dep_percentual / 100

    # Cálculo do QP
    if dl50_contato <= 0:
        return None, "Erro: DL50 deve ser positiva.", t_dep_percentual
    
    qp = (dose_ia_ha * t_dep_fator) / dl50_contato

    # Avaliação de Risco
    gatilho = 50.0
    
    if qp < gatilho:
        risco = "ACEITÁVEL"
        cor = "green"
    else:
        risco = "POTENCIAL RISCO"
        cor = "red"
        
    return qp, risco, t_dep_percentual, cor

def formatar_numero(numero: float, casas: int = 4) -> str:
    """Formata número para exibição em português (troca ponto por vírgula)."""
    return f"{numero:,.{casas}f}".replace('.', '#').replace(',', '.').replace('#', ',')

def validar_float(valor_str: str) -> float:
    """Valida e converte string para float."""
    try:
        return float(valor_str.replace(',', '.'))
    except ValueError:
        raise ValueError("Entrada inválida. Por favor, insira um valor numérico.")

# --- ROTAS FLASK ---

@app.route('/')
def index():
    return render_template('index.html', culturas=Culturas)

@app.route('/api/calcular-fase1', methods=['POST'])
def calcular_fase1_api():
    """Calcula dose FASE 1 e retorna resultado."""
    try:
        data = request.json
        dose_bula = validar_float(data['dose_bula'])
        taxa_semeadura = validar_float(data['taxa_semeadura'])
        
        if dose_bula < 0 or taxa_semeadura <= 0:
            return jsonify({'error': 'Dose da Bula e Taxa de Semeadura devem ser valores positivos.'}), 400
        
        dose_ha = calcular_dose_ha_fase1(dose_bula, taxa_semeadura)
        
        # Zera dados de refinamento
        app_data['last_refinement_data'] = {}
        
        return jsonify({
            'dose_ha': formatar_numero(dose_ha),
            'dose_ha_raw': dose_ha,
            'fonte': 'FASE 1 (Dose Bula)'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro: {e}'}), 500

@app.route('/api/logar-ensaio', methods=['POST'])
def logar_ensaio_api():
    """Loga um novo ensaio Heubach."""
    try:
        data = request.json
        
        teor_ia_str = data.get('teor_ia', '').strip()
        valor_heubach_str = data.get('valor_heubach', '').strip()
        
        densidade = validar_float(data['densidade'])
        
        # Converte opcionais para float ou None
        teor_ia = validar_float(teor_ia_str) if teor_ia_str else None
        valor_heubach = validar_float(valor_heubach_str) if valor_heubach_str else None

        if densidade <= 0:
            return jsonify({'error': 'Densidade de Semeadura deve ser um valor positivo.'}), 400
        
        # Validação: Pelo menos um valor (i.a. ou Heubach) deve estar presente
        if teor_ia is None and valor_heubach is None:
            return jsonify({'error': 'Pelo menos um valor (Teor i.a. na Poeira ou Valor Heubach) deve ser inserido.'}), 400
        
        teor_ia_final = teor_ia if teor_ia is not None else 0.0

        ensaio = {
            "Amostra": data.get('amostra', 'N/A'),
            "Teor_ia_poeira": teor_ia_final, 
            "Densidade_semeadura": densidade,
            "Valor_heubach": valor_heubach
        }
        app_data['heubach_data'].append(ensaio)
        
        return jsonify({
            'message': f'Ensaio logado com sucesso. Total de ensaios: {len(app_data["heubach_data"])}',
            'total_ensaios': len(app_data['heubach_data'])
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro: {e}'}), 500

@app.route('/api/pior-caso-labels', methods=['GET'])
def pior_caso_labels_api():
    """Retorna os valores de pior caso logados."""
    if not app_data['heubach_data']:
        return jsonify({
            'max_ia': '---',
            'max_heubach': '---',
            'max_densidade': '---'
        })
    
    max_ia = max((d['Teor_ia_poeira'] for d in app_data['heubach_data']), default=0.0)
    max_heubach = max((d['Valor_heubach'] for d in app_data['heubach_data'] if d['Valor_heubach'] is not None), default=0.0)
    max_densidade = max((d['Densidade_semeadura'] for d in app_data['heubach_data']), default=0.0)
    
    return jsonify({
        'max_ia': formatar_numero(max_ia, 4),
        'max_heubach': formatar_numero(max_heubach, 4),
        'max_densidade': formatar_numero(max_densidade, 4)
    })

@app.route('/api/calcular-pior-caso-ia', methods=['POST'])
def calcular_pior_caso_ia_api():
    """Calcula dose usando pior caso I.A. na Poeira."""
    try:
        if not app_data['heubach_data']:
            return jsonify({'error': 'Nenhum ensaio Heubach logado.'}), 400
        
        max_ia = max((d['Teor_ia_poeira'] for d in app_data['heubach_data']), default=0.0)
        max_densidade = max((d['Densidade_semeadura'] for d in app_data['heubach_data']), default=0.0)
        
        if max_ia <= 0:
            return jsonify({'error': 'Não há dados de Teor i.a. na Poeira (> 0) logados.'}), 400
        
        ensaio_pior = next((d for d in app_data['heubach_data'] if d['Teor_ia_poeira'] == max_ia), app_data['heubach_data'][0])
        
        dose_ha = calcular_dose_ha_refinada(max_ia, max_densidade)
        
        app_data['last_refinement_data'] = {
            "Amostra": ensaio_pior.get("Amostra", "PIOR CASO (Combinação I.A.)"),
            "Teor_ia_poeira": formatar_numero(max_ia, 4),
            "Densidade_semeadura": formatar_numero(max_densidade, 4),
            "Valor_heubach": formatar_numero(ensaio_pior["Valor_heubach"], 4) if ensaio_pior["Valor_heubach"] else "N/A"
        }
        
        return jsonify({
            'dose_ha': formatar_numero(dose_ha),
            'dose_ha_raw': dose_ha,
            'fonte': 'REFINAMENTO (Max I.A. Poeira)'
        })
    except Exception as e:
        return jsonify({'error': f'Erro: {e}'}), 500

@app.route('/api/calcular-pior-caso-heubach', methods=['POST'])
def calcular_pior_caso_heubach_api():
    """Calcula dose usando pior caso Heubach."""
    try:
        if not app_data['heubach_data']:
            return jsonify({'error': 'Nenhum ensaio Heubach logado.'}), 400
        
        max_heubach = max((d['Valor_heubach'] for d in app_data['heubach_data'] if d['Valor_heubach'] is not None), default=0.0)
        max_densidade = max((d['Densidade_semeadura'] for d in app_data['heubach_data']), default=0.0)
        
        if max_heubach <= 0:
            return jsonify({'error': 'Não há dados de Valor Heubach (> 0) logados.'}), 400
        
        ensaio_pior = next((d for d in app_data['heubach_data'] if d['Valor_heubach'] == max_heubach), app_data['heubach_data'][0])
        
        dose_ha = calcular_dose_ha_refinada(max_heubach, max_densidade)
        
        app_data['last_refinement_data'] = {
            "Amostra": ensaio_pior.get("Amostra", "PIOR CASO (Combinação Heubach)"),
            "Teor_ia_poeira": "N/A (Usando Heubach)",
            "Densidade_semeadura": formatar_numero(max_densidade, 4),
            "Valor_heubach": formatar_numero(max_heubach, 4)
        }
        
        return jsonify({
            'dose_ha': formatar_numero(dose_ha),
            'dose_ha_raw': dose_ha,
            'fonte': 'REFINAMENTO (Max Heubach)'
        })
    except Exception as e:
        return jsonify({'error': f'Erro: {e}'}), 500

@app.route('/api/calcular-qp', methods=['POST'])
def calcular_qp_api():
    """Calcula QP e adiciona ao log."""
    try:
        data = request.json
        
        dose_ia_ha = validar_float(data['dose_ia_ha'])
        dl50_contato = validar_float(data['dl50'])
        cultura = data['cultura']
        uso_defletor = data.get('defletor', False)
        fonte_dose = data['fonte']
        
        if dose_ia_ha <= 0 or dl50_contato <= 0:
            return jsonify({'error': 'A Dose de Poeira e a DL50 devem ser valores positivos.'}), 400
        
        qp_resultado, risco_resultado, t_dep_usado, cor = calcular_qp(
            dose_ia_ha, 
            dl50_contato, 
            cultura, 
            uso_defletor
        )
        
        qp_str = formatar_numero(qp_resultado, 2)
        
        # Prepara dados de refinamento para log
        if "REFINAMENTO" in fonte_dose:
            ref_data = app_data['last_refinement_data']
        else:
            ref_data = {
                "Amostra": "Fase 1 (Bula)",
                "Teor_ia_poeira": "N/A",
                "Densidade_semeadura": "N/A",
                "Valor_heubach": "N/A"
            }
        
        # Log entry
        log_entry = {
            "Cultura": cultura,
            "TDep": formatar_numero(t_dep_usado, 2),
            "DL50": formatar_numero(dl50_contato, 4),
            "Dose_ia_ha": formatar_numero(dose_ia_ha, 4),
            "QP": qp_str,
            "Risco": risco_resultado,
            "Fonte": fonte_dose + (" (c/ Defletor)" if uso_defletor else " (s/ Defletor)"),
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "Amostra": ref_data.get("Amostra", "N/A"),
            "Teor_ia_poeira": ref_data.get("Teor_ia_poeira", "N/A"),
            "Densidade_semeadura": ref_data.get("Densidade_semeadura", "N/A"),
            "Valor_heubach": ref_data.get("Valor_heubach", "N/A")
        }
        
        app_data['qp_log'].append(log_entry)
        
        return jsonify({
            'qp': qp_str,
            'risco': risco_resultado,
            'cor': cor,
            't_dep': formatar_numero(t_dep_usado, 2),
            'message': f'QP de {qp_str} registrado na Tabela Consolidada.'
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Erro: {e}'}), 500

@app.route('/api/obter-log', methods=['GET'])
def obter_log_api():
    """Retorna o log consolidado de QP."""
    return jsonify(app_data['qp_log'])

@app.route('/api/limpar-log-heubach', methods=['POST'])
def limpar_log_heubach_api():
    """Limpa o log de ensaios Heubach."""
    app_data['heubach_data'] = []
    app_data['last_refinement_data'] = {}
    return jsonify({'message': 'Log de ensaios Heubach limpo.'})

@app.route('/api/limpar-qp-log', methods=['POST'])
def limpar_qp_log_api():
    """Limpa o log consolidado de QP."""
    app_data['qp_log'] = []
    return jsonify({'message': 'Log consolidado QP limpo.'})

@app.route('/api/exportar-csv', methods=['GET'])
def exportar_csv_api():
    """Exporta log consolidado como CSV."""
    if not app_data['qp_log']:
        return jsonify({'error': 'Não há dados para exportar.'}), 400
    
    output = io.StringIO()
    fieldnames = list(app_data['qp_log'][0].keys())
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
    writer.writerow({k: k.replace('_', ' ').title() for k in fieldnames})
    writer.writerows(app_data['qp_log'])
    
    # Prepara para download
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'qp_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
