import os
import requests # Biblioteca para requisições HTTP diretas
import speech_recognition as sr
import pyttsx3
import json
from dotenv import load_dotenv

# --- CONFIGURAÇÃO ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("ERRO: Chave não encontrada no .env")
    exit()

# URL direta da API REST do Google (Bypassing SDK issues)
# Usando o modelo gemini-1.5-flash que é rápido e barato
URL_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# Configuração de Voz
engine = pyttsx3.init()
try:
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id) 
except:
    pass
engine.setProperty('rate', 190)

def falar(texto):
    print(f"JARVIS: {texto}")
    engine.say(texto)
    engine.runAndWait()

def enviar_para_gemini_http(texto_usuario):
    """
    Envia o texto via HTTP POST direto, sem usar a biblioteca do Google.
    Isso evita erros de versão de SDK.
    """
    headers = {"Content-Type": "application/json"}
    
    # Estrutura exata que a API REST espera
    payload = {
        "contents": [{
            "parts": [{"text": texto_usuario}]
        }],
        "systemInstruction": {
            "parts": [{"text": "Você é o JARVIS. Responda em Português, curto (max 2 frases), sarcástico e prestativo."}]
        }
    }

    try:
        response = requests.post(URL_API, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            dados = response.json()
            # Navega no JSON de resposta para pegar o texto
            try:
                texto_retorno = dados["candidates"][0]["content"]["parts"][0]["text"]
                return texto_retorno
            except KeyError:
                return "Senhor, recebi uma resposta vazia dos servidores."
        else:
            print(f"Erro HTTP: {response.status_code} - {response.text}")
            return "Desculpe, falha nos protocolos de comunicação."
            
    except Exception as e:
        print(f"Erro de conexão: {e}")
        return "Estou sem internet, senhor."

def ouvir_microfone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Calibragem inicial
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # --- AJUSTES FINOS ANTI-CORTE ---
        recognizer.pause_threshold = 2.0  # Espera 2s de silêncio para considerar FIM
        recognizer.energy_threshold = 300 # Sensibilidade (aumente se tiver muito ruído de fundo)
        recognizer.dynamic_energy_threshold = True # Ajusta sozinho conforme o barulho da sala
        
        print("\n(Ouvindo... Fale com calma)")
        try:
            # timeout=None: Espera indefinidamente você começar a falar
            audio = recognizer.listen(source, timeout=None)
            print("(Processando...)")
            
            texto = recognizer.recognize_google(audio, language='pt-BR')
            print(f"VOCÊ: {texto}")
            return texto
        except sr.UnknownValueError:
            return None
        except Exception as e:
            return None

def main():
    falar("Modo HTTP ativado. Conexão direta estabelecida. Estou pronto.")
    
    while True:
        comando = ouvir_microfone()
        
        if comando:
            if "desligar" in comando.lower() or "tchau" in comando.lower():
                falar("Desligando sistemas.")
                break
            
            # Chama a função HTTP manual
            resposta = enviar_para_gemini_http(comando)
            falar(resposta)

if __name__ == "__main__":
    main()