#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Instagram Content Generator para Prof. Everson
Gera imagens + copy automático baseado na grade semanal
Integração: Google Sheets + Google Drive
"""

import os
import json
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import requests
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
import gspread

# ============================================================================
# CONFIGURAÇÃO - Cores e Identidade
# ============================================================================

COLORS = {
    "black": "#000000",
    "orange": "#FF6B35",
    "white": "#FFFFFF",
    "dark_gray": "#1a1a1a"
}

BRAND_COLORS = {
    "primary": (0, 0, 0),  # Preto RGB
    "accent": (255, 107, 53),  # Laranja RGB
    "text": (255, 255, 255)  # Branco
}

# ============================================================================
# GRADE SEMANAL E BANCO DE CONTEÚDO
# ============================================================================

GRADE_SEMANAL = {
    0: {"papel": "Líder", "objetivo": "Quebra de crença · Alcance"},
    1: {"papel": "Professor", "objetivo": "Autoridade técnica · Salvamento"},
    2: {"papel": "Mentor", "objetivo": "Resultado de aluno · Conversão HT"},
    3: {"papel": "Criador", "objetivo": "Diferenciação do método · Qualificação HT"},
    4: {"papel": "Amigo", "objetivo": "Bastidor/humanização · Retenção"},
}

TEMAS = [
    "Trava na prova? Não é culpa sua.",
    "Os 3 erros que 90% comete em matemática",
    "Por que estudar sozinho não funciona",
    "A diferença entre quem passa e quem reprova",
    "Como a banca te engana nas questões",
    "Seu filho quer te ver vencer",
    "Método FAST: o que ninguém te contou",
    "Reprovar por causa da matemática dói",
    "Organização bate talento. Sempre.",
    "Aquele colega que ninguém achava capaz?",
    "Seu bloqueio em matemática tem solução",
    "80% de acertos em 30 dias é possível",
    "O problema nunca foi você. Foi o método.",
    "Matemática não é talento, é organização",
    "Concurso não passa sozinho",
]

COPY_TEMPLATES = {
    "Líder": [
        "O problema nunca foi você. Foi o {tema}.",
        "Você reprova porque ninguém ensinou como estudar.",
        "{tema} — e aí, não é verdade?",
        "Se você pudesse voltar no tempo...",
    ],
    "Professor": [
        "Deixa eu te mostrar como isso funciona.",
        "Entender é mais fácil que decorar.",
        "A maioria estuda errado. Você não precisa ser assim.",
        "Isso que você faz está travando sua progressão.",
    ],
    "Mentor": [
        "Um aluno meu saiu de 30% para 80% em 30 dias.",
        "Seu resultado é meu resultado.",
        "Mentoria Matemática Acelerada — lista de espera aberta.",
        "Conheça a história de quem virou o jogo.",
    ],
    "Criador": [
        "Metodologia FAST: Fundamentos, Aceleração, Suporte, Treino.",
        "Não é macete. É organização.",
        "Enquanto você tenta decorar, outras pessoas entendem.",
        "Isso é o que diferencia meu método.",
    ],
    "Amigo": [
        "Por trás de cada live tem preparação.",
        "Aqui é um espaço de gente que quer vencer.",
        "Meus alunos são minhas Águias.",
        "Vamos juntos nessa?",
    ]
}

CTA_TEMPLATES = [
    "Comenta MENTORIA",
    "Link na bio — lista de espera",
    "Manda NOMEAÇÃO no direct",
    "Salva esse vídeo",
    "Se inscreve no canal",
]

# ============================================================================
# AUTENTICAÇÃO GOOGLE
# ============================================================================

def get_google_credentials():
    """Lê credenciais do arquivo secrets.json (GitHub Secrets)"""
    secrets_json = os.getenv("GOOGLE_CREDENTIALS")
    if not secrets_json:
        raise ValueError("Variável GOOGLE_CREDENTIALS não configurada")
    
    creds_dict = json.loads(secrets_json)
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return credentials

# ============================================================================
# GERAÇÃO DE IMAGEM
# ============================================================================

def gerar_imagem(tema, copy, papel, cta, numero_design=1):
    """
    Gera imagem 1080x1350 com design variado
    Cores: Preto + Laranja
    """
    width, height = 1080, 1350
    img = Image.new("RGB", (width, height), BRAND_COLORS["primary"])
    draw = ImageDraw.Draw(img)
    
    # Fonte (sistema fallback)
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        font_copy = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_title = ImageFont.load_default()
        font_copy = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Layout varia conforme numero_design
    if numero_design % 3 == 1:
        # Design 1: Título grande + cópia abaixo
        y_pos = 100
        
        # Header com laranja
        draw.rectangle([(0, 0), (width, 80)], fill=BRAND_COLORS["accent"])
        draw.text((40, 20), "PROF. EVERSON", font=font_small, fill=BRAND_COLORS["primary"])
        
        # Tema em laranja grande
        tema_wrapped = textwrap.fill(tema, width=20)
        draw.text((40, y_pos), tema_wrapped, font=font_title, fill=BRAND_COLORS["accent"])
        
        y_pos += 300
        
        # Cópia em branco
        copy_wrapped = textwrap.fill(copy, width=30)
        draw.text((40, y_pos), copy_wrapped, font=font_copy, fill=BRAND_COLORS["text"])
        
        # CTA em laranja na base
        draw.rectangle([(0, height-120), (width, height)], fill=BRAND_COLORS["accent"])
        draw.text((40, height-80), cta, font=font_small, fill=BRAND_COLORS["primary"])
        
    elif numero_design % 3 == 2:
        # Design 2: Laranja na esquerda, conteúdo à direita
        draw.rectangle([(0, 0), (int(width*0.25), height)], fill=BRAND_COLORS["accent"])
        
        # Papel do dia rotacionado
        draw.text((50, 150), papel, font=font_title, fill=BRAND_COLORS["primary"], anchor="lm")
        
        # Tema e copy lado direito
        x_offset = int(width * 0.28)
        y_pos = 120
        
        tema_wrapped = textwrap.fill(tema, width=25)
        draw.text((x_offset, y_pos), tema_wrapped, font=font_title, fill=BRAND_COLORS["accent"])
        
        y_pos += 280
        
        copy_wrapped = textwrap.fill(copy, width=25)
        draw.text((x_offset, y_pos), copy_wrapped, font=font_copy, fill=BRAND_COLORS["text"])
        
        # CTA na base
        draw.text((x_offset, height-100), cta, font=font_small, fill=BRAND_COLORS["accent"])
    
    else:
        # Design 3: Split vertical (preto/laranja)
        mid_height = int(height / 2)
        draw.rectangle([(0, mid_height), (width, height)], fill=BRAND_COLORS["accent"])
        
        # Parte superior
        y_pos = 80
        tema_wrapped = textwrap.fill(tema, width=22)
        draw.text((40, y_pos), tema_wrapped, font=font_title, fill=BRAND_COLORS["accent"])
        
        # Parte inferior (laranja)
        y_pos = mid_height + 60
        copy_wrapped = textwrap.fill(copy, width=26)
        draw.text((40, y_pos), copy_wrapped, font=font_copy, fill=BRAND_COLORS["primary"])
        
        # CTA
        draw.text((40, height-80), cta, font=font_small, fill=BRAND_COLORS["primary"])
    
    return img

# ============================================================================
# LÓGICA DE CONTEÚDO
# ============================================================================

def gerar_conteudo():
    """Gera tema, copy e CTA para o dia"""
    hoje = datetime.now()
    day_of_week = hoje.weekday()  # 0=seg, 1=ter, 2=qua, 3=qui, 4=sex
    
    # Papel do dia
    papel_info = GRADE_SEMANAL.get(day_of_week, {"papel": "Amigo", "objetivo": "Retenção"})
    papel = papel_info["papel"]
    
    # Escolhe tema aleatório
    tema = random.choice(TEMAS)
    
    # Escolhe copy baseado no papel
    copy_template = random.choice(COPY_TEMPLATES.get(papel, COPY_TEMPLATES["Amigo"]))
    copy = copy_template.format(tema=tema.lower())
    
    # CTA aleatório
    cta = random.choice(CTA_TEMPLATES)
    
    return {
        "papel": papel,
        "tema": tema,
        "copy": copy,
        "cta": cta,
        "data": hoje.strftime("%Y-%m-%d"),
        "dia_semana": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"][day_of_week]
    }

# ============================================================================
# INTEGRAÇÃO GOOGLE SHEETS E DRIVE
# ============================================================================

def salvar_em_google_drive(img, nome_arquivo, folder_id, credentials):
    """Salva imagem em Google Drive e retorna link público"""
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    import tempfile
    
    # Salva imagem temporária
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        img.save(tmp.name)
        tmp_path = tmp.name
    
    try:
        drive_service = build("drive", "v3", credentials=credentials)
        
        file_metadata = {
            "name": nome_arquivo,
            "parents": [folder_id]
        }
        
        media = MediaFileUpload(tmp_path, mimetype="image/png")
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields="id, webViewLink"
        ).execute()
        
        file_id = file.get("id")
        
        # Torna público (opcional)
        drive_service.permissions().create(
            fileId=file_id,
            body={"role": "reader", "type": "anyone"}
        ).execute()
        
        return file.get("webViewLink")
    
    finally:
        os.remove(tmp_path)

def atualizar_google_sheets(conteudo, link_imagem, sheet_id, credentials):
    """Atualiza Google Sheets com novo conteúdo"""
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(sheet_id).sheet1
    
    # Adiciona linha com dados
    nova_linha = [
        conteudo["data"],
        conteudo["dia_semana"],
        conteudo["papel"],
        conteudo["tema"],
        conteudo["copy"],
        conteudo["cta"],
        link_imagem,
        "Agendado"
    ]
    
    worksheet.append_row(nova_linha)

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("🚀 Gerando conteúdo Instagram...")
    
    try:
        # Autenticação
        credentials = get_google_credentials()
        
        # Gera conteúdo
        conteudo = gerar_conteudo()
        print(f"✅ Papel: {conteudo['papel']}")
        print(f"✅ Tema: {conteudo['tema']}")
        
        # Gera imagem (varia design aleatoriamente)
        numero_design = random.randint(1, 3)
        img = gerar_imagem(
            conteudo["tema"],
            conteudo["copy"],
            conteudo["papel"],
            conteudo["cta"],
            numero_design
        )
        
        # Salva em Google Drive
        nome_arquivo = f"instagram_{conteudo['data']}_design{numero_design}.png"
        sheet_id = "16wDqZRZ0X3MYkO8UYWAdHoZSJG8zzvyOMjC1CS_OQXE"
        folder_id = "1XKmMptImYnHiLy3GSTUK6CIMWEOt71Yz"
        
        link = salvar_em_google_drive(img, nome_arquivo, folder_id, credentials)
        print(f"✅ Imagem salva: {link}")
        
        # Atualiza Google Sheets
        atualizar_google_sheets(conteudo, link, sheet_id, credentials)
        print(f"✅ Google Sheets atualizado")
        
        print("\n📱 Conteúdo pronto para N8N publicar!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise

if __name__ == "__main__":
    main()
