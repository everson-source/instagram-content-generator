#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Instagram Content Generator para Prof. Everson - VERSÃO FINAL
Gera conteúdo e salva na Google Sheets
N8N gera a imagem na hora de publicar
"""

import os
import json
from datetime import datetime
import random
from google.oauth2.service_account import Credentials
import gspread

# ============================================================================
# CONFIGURAÇÃO
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
    """Lê credenciais do GitHub Secrets"""
    secrets_json = os.getenv("GOOGLE_CREDENTIALS")
    if not secrets_json:
        raise ValueError("Variável GOOGLE_CREDENTIALS não configurada")
    
    creds_dict = json.loads(secrets_json)
    credentials = Credentials.from_service_account_info(
        creds_dict,
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return credentials

# ============================================================================
# LÓGICA DE CONTEÚDO
# ============================================================================

def gerar_conteudo():
    """Gera tema, copy e CTA para o dia"""
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
# INTEGRAÇÃO GOOGLE SHEETS
# ============================================================================

def atualizar_google_sheets(conteudo, sheet_id, credentials):
    """Atualiza Google Sheets com conteúdo do dia"""
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
# MAIN
# ============================================================================

def main():
    print("🚀 Gerando conteúdo Instagram...")
    
    try:
        credentials = get_google_credentials()
        conteudo = gerar_conteudo()
        
        print(f"✅ Papel: {conteudo['papel']}")
        print(f"✅ Tema: {conteudo['tema']}")
        print(f"✅ Copy: {conteudo['copy'][:50]}...")
        print(f"✅ CTA: {conteudo['cta']}")
        
        sheet_id = "16wDqZRZ0X3MYkO8UYWAdHoZSJG8zzvyOMjC1CS_OQXE"
        atualizar_google_sheets(conteudo, sheet_id, credentials)
        
        print(f"✅ Google Sheets atualizado")
        print("\n📱 Conteúdo pronto! N8N vai publicar automaticamente.")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        raise

if __name__ == "__main__":
    main()
