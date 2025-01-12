import requests
import time
import json
import threading
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

url = "http://127.0.0.1:11434/api/generate"

data = {
    "model": "llama3.2:1b",
    "prompt": "Crie o roteiro de um pdf de 2 paginas sobre PYQT5",
    "max_tokens": 100
}

def save_TXT(string, filename, mode):
    with open(filename, mode, encoding="utf-8") as file:
        file.write(f'{string}\n')

def create_pdf(content, filename):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Adicionando estilos personalizados
    title_style = ParagraphStyle(name='TitleStyle', fontSize=24, textColor=colors.blue, spaceAfter=12)
    subtitle_style = ParagraphStyle(name='SubtitleStyle', fontSize=18, textColor=colors.orange, spaceAfter=10)
    body_style = ParagraphStyle(name='BodyStyle', fontSize=11, textColor=colors.black, spaceAfter=6)

    elements = []
    
    # Quebrando o conteúdo em linhas
    lines = content.split('\n')
    for line in lines:
        if line.strip():  # Ignorar linhas vazias
            if "Título" in line:  # Identifica título
                elements.append(Paragraph(line, title_style))
            elif "Subtítulo" in line:  # Identifica subtítulo
                elements.append(Paragraph(line, subtitle_style))
            else:  # Corpo do texto
                elements.append(Paragraph(line, body_style))
            elements.append(Spacer(1, 12))  # Espaço entre os elementos

    doc.build(elements)

def analyze_script(content):
    analysis_url = "http://127.0.0.1:11434/api/generate"  # URL para a API de análise
    analysis_data = {
        "model": "llama3.2:1b",
        "prompt": f"Analise o seguinte roteiro e identifique títulos, subtítulos e corpo do texto:\n\n{content}",
        "max_tokens": 300
    }
    response = requests.post(analysis_url, json=analysis_data)
    if response.status_code == 200:
        analysis_result = response.json()
        # Processa o resultado da análise conforme necessário
        print("Análise do roteiro:", analysis_result)
        return analysis_result
    else:
        print("Erro na análise:", response.status_code, response.text)
        return None

def streaming_response(url, data):
    response = requests.post(url, json=data, stream=True)
    if response.status_code == 200:
        response_text = ""
        try:
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    output = json.loads(line)
                    response_text += output["response"]
                    if output.get("done", False):
                        break
                    resposta_com_roteiro = output["response"]
                    save_TXT(resposta_com_roteiro, r"CoreApp\process\roteiro\roteiro.txt", "a")
                    time.sleep(0.04)

            print("\nResposta completa:", response_text)
            # Cria o PDF após receber a resposta completa
            create_pdf(response_text, r"CoreApp\process\roteiro\roteiro.pdf")

            # Inicia a thread para analisar o roteiro
            analysis_thread = threading.Thread(target=analyze_script, args=(response_text,))
            analysis_thread.start()

        except ValueError as e:
            print("Erro ao decodificar JSON:", e)
    else:
        print("Erro:", response.status_code, response.text)

streaming_response(url, data)
