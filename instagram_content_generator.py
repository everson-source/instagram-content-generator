#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Instagram Content Generator - VERSÃO FINAL COM WHATSAPP
Gera imagem, salva na nuvem, envia via WhatsApp
"""

import os
import json
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
import base64
from io import BytesIO
import requests
from google.oauth2.service_account import Credentials
import gspread

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

BRAND_COLORS = {
    "primary": (0, 0, 0),
    "accent": (255, 107, 53),
    "text": (255, 255, 255)
}

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
# GERAR IMAGEM
# ============================================================================

def gerar_imagem(tema, copy, papel, cta, numero_design=1):
    """Gera imagem 1080x1350"""
    width, height = 1080, 1350
    img = Image.new("RGB", (width, height), BRAND_COLORS["primary"])
    draw = ImageDraw.Draw(img)
    
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 56)
        font_copy = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
    except:
        font_title = ImageFont.load_default()
        font_copy = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    if numero_design % 3 == 1:
        y_pos = 100
        draw.rectangle([(0, 0), (width, 80)], fill=BRAND_COLORS["accent"])
        draw.text((40, 20), "PROF. EVERSON", font=font_small, fill=BRAND_COLORS["primary"])
        
        tema_wrapped = textwrap.fill(tema, width=20)
        draw.text((40, y_pos), tema_wrapped, font=font_title, fill=BRAND_COLORS["accent"])
        
        y_pos += 300
        copy_wrapped = textwrap.fill(copy, width=30)
        draw.text((40, y_pos), copy_wrapped, font=font_copy, fill=BRAND_COLORS["text"])
        
        draw.rectangle([(0, height-120), (width, height)], fill=BRAND_COLORS["accent"])
        draw.text((40, height-80), cta, font=font_small, fill=BRAND_COLORS["primary"])
        
    elif numero_design % 3 == 2:
        draw.rectangle([(0, 0), (int(width*0.25), height)], fill=BRAND_COLORS["accent"])
        draw.text((50, 150), papel, font=font_title, fill=BRAND_COLORS["primary"], anchor="lm")
        
        x_offset = int(width * 0.28)
        y_pos = 120
        
        tema_wrapped = textwrap.fill(tema, width=25)
        draw.text((x_offset, y_pos), tema_wrapped, font=font_title, fill=BRAND_COLORS["accent"])
        
        y_pos += 280
        copy_wrapped = textwrap.fill(copy, width=25)
        draw.text((x_offset, y_pos), copy_wrapped, font=font_copy, fill=BRAND_COLORS["text"])
        
        draw.text((x_offset, height-100), cta, font=font_small, fill=BRAND_COLORS["accent"])
    
    else:
        mid_height = int(height / 2)
        draw.rectangle([(0, mid_height), (width, height)], fill=BRAND_COLORS["accent"])
        
        y_pos = 80
        tema_wrapped = textwrap.fill(tema, width=22)
        draw.text((40, y_pos), tema_wrapped, font=font_title, fill=BRAND_COLORS["accent"])
        
        y_pos = mid_height + 60
        copy_wrapped = textwrap.fill(copy, width=26)
        draw.text((40, y_pos), copy_wrapped, font=font_copy, fill=BRAND_COLORS["primary"])
        
        draw.text((40, height-80), cta, font=font_small, fill=BRAND_COLORS["primary"])
    
    return img

# ============================================================================
# SALVAR IMAGEM NA NUVEM (IMGBB - GRÁTIS)
# ============================================================================

def salvar_imagem_nuvem(img):
    """Salva imagem no ImgBB (grátis) e retorna URL"""
    # Converte PIL Image para bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    img_bytes = buffer.getvalue()
    
    # Upload para ImgBB (API grátis)
    # Você pode gerar uma API key em https://imgbb.com/
    # Para teste, usamos upload anônimo
    
    try:
        files = {'image': ('image.png', img_bytes)}
        response = requests.post('https://api.imgbb.com/1/upload', 
                                files=files,
                                data={'key': '4d6207dfe4e2b4f1c8c8a73e8f7c5b3a'})  # API key demo (limitado)
        
        if response.status_code == 200:
            data = response.json()
            return data['data']['url']
        else:
            print("⚠️ Erro ao fazer upload. Usando URL temporária...")
            return None
    except Exception as e:
        print(f"⚠️ Erro no upload: {e}")
        return None

# ============================================================================
# ENVIAR VIA WHATSAPP (Z-API)
# ============================================================================

def enviar_whatsapp(tema, copy, cta, img_url, papel):
    """Envia a postagem + imagem via WhatsApp"""
    
    # Credenciais Z-API
    instance_id = "3F2CBD89B912E2E4430E02156C0FC2D1"
    token = "A0BB5D89712E451AB10EFE2F"
    
    # Seu número (adicionar 55 + DDD + número sem 0 inicial)
    # Exemplo: seu número: (16) 98203-3967 → 5516982033967
    seu_numero = "5516997506180"  # Substitua pelo seu número!
    
    # Formata a mensagem
    mensagem = f"""🎯 {papel}

{tema}

{copy}

👉 {cta}

Link na bio — lista de espera"""
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Envia a imagem (se conseguiu fazer upload)
        if img_url:
            payload_img = {
                "phone": seu_numero,
                "image": img_url,
                "caption": mensagem
            }
            requests.post(
                f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-image",
                json=payload_img,
                headers=headers
            )
            print(f"✅ Imagem + mensagem enviada para WhatsApp")
        else:
            # Se não conseguiu, envia só a mensagem
            payload_msg = {
                "phone": seu_numero,
                "message": mensagem
            }
            requests.post(
                f"https://api.z-api.io/instances/{instance_id}/token/{token}/send-message",
                json=payload_msg,
                headers=headers
            )
            print(f"✅ Mensagem enviada para WhatsApp")
            
    except Exception as e:
        print(f"⚠️ Erro ao enviar WhatsApp: {e}")

# ============================================================================
# GOOGLE SHEETS
# ============================================================================

def get_google_credentials():
    secrets_json = os.getenv("GOOGLE_CREDENTIALS")
    if not secrets_json:
        raise ValueError("Variável GOOGLE_CREDENTIALS não configurada")
    
    creds_dict = json.loads(secrets_json)
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return credentials

def atualizar_google_sheets(conteudo, sheet_id, credentials):
    gc = gspread.authorize(credentials)
    worksheet = gc.open_by_key(sheet_id).sheet1
    
    nova_linha = [
        conteudo["data"],
        conteudo["dia_semana"],
        conteudo["horario"],
        conteudo["papel"],
        conteudo["tema"],
        conteudo["copy"],
        conteudo["cta"],
        "Aguardando publicação"
    ]
    
    worksheet.append_row(nova_linha)

# ============================================================================
# LÓGICA PRINCIPAL
# ============================================================================

def gerar_conteudo():
    hoje = datetime.now()
    day_of_week = hoje.weekday()
    
    papel_info = GRADE_SEMANAL.get(day_of_week, {"papel": "Amigo", "objetivo": "Retenção"})
    papel = papel_info["papel"]
    
    tema = random.choice(TEMAS)
    copy_template = random.choice(COPY_TEMPLATES.get(papel, COPY_TEMPLATES["Amigo"]))
    copy = copy_template.format(tema=tema.lower())
    cta = random.choice(CTA_TEMPLATES)
    
    return {
        "papel": papel,
        "tema": tema,
        "copy": copy,
        "cta": cta,
        "horario": datetime.now().strftime("%H:%M"),
        "data": hoje.strftime("%d/%m/%Y"),
        "dia_semana": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"][day_of_week]
    }

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("🚀 Gerando conteúdo Instagram...")
    
    try:
        credentials = get_google_credentials()
        conteudo = gerar_conteudo()
        
        print(f"✅ Papel: {conteudo['papel']}")
        print(f"✅ Tema: {conteudo['tema']}")
        
        # Gera imagem
        numero_design = random.randint(1, 3)
        img = gerar_imagem(
            conteudo["tema"],
            conteudo["copy"],
            conteudo["papel"],
            conteudo["cta"],
            numero_design
        )
        print(f"✅ Imagem gerada (design {numero_design})")
        
        # Salva na nuvem
        img_url = salvar_imagem_nuvem(img)
        
        # Envia via WhatsApp
        enviar_whatsapp(
            conteudo["tema"],
            conteudo["copy"],
            conteudo["cta"],
            img_url,
            conteudo["papel"]
        )
        
        # Atualiza Google Sheets
        sheet_id = "16wDqZRZ0X3MYkO8UYWAdHoZSJG8zzvyOMjC1CS_OQXE"
        atualizar_google_sheets(conteudo, sheet_id, credentials)
        print(f"✅ Google Sheets atualizado")
        
        print("\n📱 Conteúdo + imagem enviados para WhatsApp!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise

if __name__ == "__main__":
    main()
