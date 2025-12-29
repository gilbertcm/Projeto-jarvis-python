import os
import speech_recognition as sr
import pyttsx3
from google import genai # Nova biblioteca oficial
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERRO: Chave não encontrada no .env")
    exit()

# Configuração do Cliente da Nova API
try:
    client = genai.Client(api_key=api_key)
    print("Conectado ao Sistema Gemini (Nova API).")
except Exception as e:
    print(f"Erro de conexão: {e}")
    exit()

# Configuração de Voz
engine = pyttsx3.init()
voices = engine.getProperty('voices')
# Tenta selecionar voz em PT-BR (índice 0 ou 1)
try:
    engine.setProperty('voice', voices[0].id) 
except:
    pass
engine.setProperty('rate', 190) # Velocidade da fala

def falar(texto):
    print(f"JARVIS: {texto}")
    engine.say(texto)
    engine.runAndWait()

def ouvir_microfone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # 1. Ajuste de ruído mais curto para ser mais ágil
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # --- CONFIGURAÇÃO ANTI-CORTES ---
        # pause_threshold: Tempo de silêncio necessário para ele achar que você acabou.
        # Aumentei para 2.0 segundos (antes era 0.8). Dá tempo de respirar.
        recognizer.pause_threshold = 2.0 
        
        # phrase_time_limit: Tirei o limite. Ele vai te ouvir até você ficar quieto por 2s.
        
        print("\n(Ouvindo...)")
        try:
            # timeout=None significa que ele vai esperar para sempre você começar a falar
            audio = recognizer.listen(source, timeout=None)
            print("(Processando...)")
            
            texto = recognizer.recognize_google(audio, language='pt-BR')
            print(f"VOCÊ: {texto}")
            return texto
        except sr.UnknownValueError:
            return None
        except Exception as e:
            # Ignora erros de timeout silenciosos
            return None

def main():
    falar("Módulo de comunicação atualizado. Estou ouvindo.")
    
    while True:
        comando = ouvir_microfone()
        
        if comando:
            if "desligar" in comando.lower() or "tchau" in comando.lower():
                falar("Sistemas offline.")
                break
            
            try:
                # NOVA SINTAXE DE GERAÇÃO (Google GenAI SDK)
                # Usando o modelo 1.5 Flash que é rápido e estável na nova lib
                response = client.models.generate_content(
                    model="gemini-1.5-flash", 
                    contents=comando,
                    config={
                        "system_instruction": "Você é o JARVIS. Responda em Português, de forma curta (máximo 2 frases), técnica e prestativa."
                    }
                )
                falar(response.text)
            except Exception as e:
                falar("Senhor, ocorreu um erro na matriz.")
                print(f"ERRO API: {e}")

if __name__ == "__main__":
    main()