import os
import requests
import speech_recognition as sr
import pyttsx3
import json
import winsound # Somente para Windows
from dotenv import load_dotenv

# --- CONFIGURAÇÃO ---
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# MUDANÇA: Voltando para o 1.5-Flash que apareceu na sua lista.
# Ele é mais estável e não tem o limite agressivo de "30s de espera" do 2.0
URL_API = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# Configuração de Voz
engine = pyttsx3.init()
engine.setProperty('rate', 190)

def tocar_bip():
    # Toca um som de frequência 1000Hz por 200ms
    # Isso serve para você saber quando PODE falar
    winsound.Beep(1000, 200)

def falar(texto):
    print(f"JARVIS: {texto}")
    engine.say(texto)
    engine.runAndWait()

def enviar_para_gemini(texto_usuario):
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "contents": [{"parts": [{"text": texto_usuario}]}],
        "systemInstruction": {
            "parts": [{"text": "Você é o JARVIS. Responda em Português. Seja curto, direto e prestativo."}]
        }
    }

    try:
        response = requests.post(URL_API, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        elif response.status_code == 429:
            return "Estou sobrecarregado, senhor. Tente novamente em alguns segundos."
        else:
            print(f"Erro Google ({response.status_code}): {response.text}")
            return "Erro nos protocolos de comunicação."
    except Exception as e:
        return "Sem conexão."

def ouvir_microfone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nCalibrando ruído... (fique em silêncio)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        # --- AJUSTE EXTREMO ANTI-CORTE ---
        recognizer.pause_threshold = 2.5  # Espera 2.5s de silêncio para parar
        recognizer.phrase_threshold = 0.3 # Mínimo de tempo falando para considerar válido
        
        print(">> PODE FALAR AGORA <<")
        tocar_bip() # O sinal sonoro!
        
        try:
            # timeout=None: Espera para sempre você começar
            audio = recognizer.listen(source, timeout=None)
            print("(Pensando...)")
            texto = recognizer.recognize_google(audio, language='pt-BR')
            print(f"VOCÊ: {texto}")
            return texto
        except sr.UnknownValueError:
            return None
        except Exception:
            return None

def main():
    falar("Sistemas 1.5 online. Aguarde o bip para falar.")
    
    while True:
        comando = ouvir_microfone()
        
        if comando:
            if "desligar" in comando.lower():
                falar("Até logo.")
                break
            
            resposta = enviar_para_gemini(comando)
            falar(resposta)

if __name__ == "__main__":
    main()