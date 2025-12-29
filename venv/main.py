import speech_recognition as sr
import pyttsx3

# --- CONFIGURAÇÃO INICIAL ---
# Inicializa o motor de voz (Text-to-Speech)
engine = pyttsx3.init()

# Configurações de voz (opcional: ajusta velocidade e volume)
voices = engine.getProperty('voices')
# Tenta pegar uma voz em português (geralmente index 0 ou 1 no Windows)
engine.setProperty('voice', voices[0].id) 
engine.setProperty('rate', 190) # Velocidade da fala

def falar(texto):
    """Função para o assistente falar"""
    print(f"JARVIS: {texto}")
    engine.say(texto)
    engine.runAndWait()

def ouvir_microfone():
    """Ouve o microfone e retorna o texto"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        # Ajusta o ruído ambiente (importante para não travar)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("\nOuvindo...")
        
        try:
            # Escuta o áudio
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            print("Processando...")
            
            # Converte para texto (usando Google Speech Recognition - requer internet básica)
            texto = recognizer.recognize_google(audio, language='pt-BR')
            print(f"VOCÊ: {texto}")
            return texto.lower()
            
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            # Não entendeu o áudio
            return None
        except sr.RequestError:
            falar("Erro de conexão com o serviço de reconhecimento.")
            return None

# --- LOOP PRINCIPAL ---
def main():
    falar("Sistemas online. O que deseja, senhor?")
    
    while True:
        comando = ouvir_microfone()
        
        if comando:
            # Lógica simples (hardcoded) só para testar a Fase 1
            if "encerrar" in comando or "sair" in comando:
                falar("Desligando sistemas. Até logo.")
                break
            
            elif "quem é você" in comando:
                falar("Eu sou o Jarvis, seu assistente virtual.")
                
            else:
                falar(f"Você disse: {comando}. Ainda não tenho cérebro para responder isso.")

if __name__ == "__main__":
    main()