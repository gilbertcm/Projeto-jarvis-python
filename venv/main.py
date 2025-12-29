import os
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
from dotenv import load_dotenv

# --- CONFIGURAÇÃO INICIAL ---
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERRO: Chave de API não encontrada! Verifique o arquivo .env")
    exit()

genai.configure(api_key=api_key)

# Trocamos para um modelo que costuma ser mais estável na conexão
# Se der erro 404 novamente, troque "gemini-1.5-flash" por "gemini-pro"
MODELO_ESCOLHIDO = "gemini-pro" 

try:
    model = genai.GenerativeModel(
        model_name=MODELO_ESCOLHIDO,
        system_instruction="""
        Você é o J.A.R.V.I.S. Responda em Português do Brasil.
        Seja conciso (máximo 2 frases), técnico e levemente sarcástico.
        Não use markdown (*negrito*), fale como uma pessoa normal.
        """
    )
    # Teste rápido de conexão silencioso
    print("Conectando ao cérebro...")
except Exception as e:
    print(f"Erro ao configurar modelo: {e}")

chat = model.start_chat(history=[])

# Configuração de Voz
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id) 
engine.setProperty('rate', 190)

def falar(texto):
    print(f"JARVIS: {texto}")
    engine.say(texto)
    engine.runAndWait()

def ouvir_microfone():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        # Ajuste de sensibilidade (importante!)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # --- O SEGREDO PARA NÃO CORTAR ---
        recognizer.pause_threshold = 1.5  # Espera 1.5s de silêncio antes de finalizar
        recognizer.energy_threshold = 300 # Sensibilidade mínima para captar voz
        
        print("\n(Ouvindo...)")
        try:
            # Aumentei o timeout para você ter tempo de pensar
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=15)
            print("(Processando áudio...)")
            
            texto = recognizer.recognize_google(audio, language='pt-BR')
            print(f"VOCÊ: {texto}")
            return texto
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None # Não entendeu nada (silêncio ou ruído)
        except Exception as e:
            print(f"Erro mic: {e}")
            return None

def main():
    falar("Olá Gilbert, Sistemas rekalibrados. Microfone ajustado. Estou pronto.")
    
    while True:
        comando = ouvir_microfone()
        
        if comando:
            if "desligar" in comando.lower() or "encerrar" in comando.lower():
                falar("Encerrando protocolos.")
                break
            
            try:
                # Envia para o Gemini
                response = chat.send_message(comando)
                falar(response.text)
            except Exception as e:
                # Se der o erro 404 aqui, vai aparecer no terminal
                falar("Senhor, erro de conexão com o modelo de linguagem.")
                print(f"ERRO API DETALHADO: {e}")

if __name__ == "__main__":
    main()